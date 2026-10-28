# /// script
# dependencies = ["polars", "numpy", "scipy"]
# ///
"""W7: at which octave k does the rule-level rank order of kappa(k) match kappa(26)? Uses windows k=9..26 in b2/item21/patched.
usage (repo root): uv run experiments/archive/2026-10-kappa-rule-space/scripts/w7_emergence.py"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import numpy as np, polars as pl
from scipy.stats import spearmanr, rankdata
from kcommon import *

MINB = 200  # boundary steps per run-window below which kappa(k) is count noise
runs = pool_runs(["b2_probe.csv", "item21_probe.csv", "patched.csv"])
pool = rule_means(runs)  # >=6 core-band runs, pool-192
keep_runs = set(runs.filter(pl.col("base").is_in(pool["base"]))["rule"].to_list())
gk = dict(zip(pool["base"], pool["g_k"]))
frames = []
kmin = {}
for f in ("b2_probe.csv", "item21_probe.csv", "patched.csv"):
    raw = pl.read_csv(legacy(f)).filter(~pl.col("escaped") & pl.col("rule").is_in(list(keep_runs)))
    kmin[f] = int(raw["k"].min())
    frames.append(raw)
w = pl.concat(frames).with_columns(base=pl.col("rule").str.split("@").list.first(), steps=pl.col("t") // 2).with_columns(
    kappa=(pl.col("boundary_steps") / pl.col("steps")) / (pl.col("perimeter") / pl.col("area")), lnA=pl.col("area").log())
w = w.filter((pl.col("boundary_steps") >= MINB) & (pl.col("kappa") > 0))
out = [f"pool-192 rules; runs kept (core band, from the pool): {len(keep_runs)}; min k per file: {kmin}; windows need >= {MINB} boundary steps",
       f"stationary = |median g_k| < 0.05: {(np.abs(pool['g_k'].to_numpy()) < 0.05).sum()} of {pool.height}"]

per = w.group_by(["base", "k"]).agg(lnk=pl.col("kappa").log().mean(), lnA=pl.col("lnA").mean(), n=pl.len())
piv = per.pivot(on="k", index="base", values="lnk")
pivA = per.pivot(on="k", index="base", values="lnA")
ref = piv.select("base", ref=pl.col("26")).drop_nulls()
bases = ref["base"].to_list(); yref = ref["ref"].to_numpy()
stat = np.array([abs(gk[b]) < 0.05 for b in bases])


def partial_spearman(x, y, z):
    rx, ry, rz = rankdata(x), rankdata(y), rankdata(z)
    A = np.c_[np.ones(len(rz)), rz]
    ex = rx - A @ np.linalg.lstsq(A, rx, rcond=None)[0]; ey = ry - A @ np.linalg.lstsq(A, ry, rcond=None)[0]
    return np.corrcoef(ex, ey)[0, 1]


rows = []
out.append("\n k | rules | Spearman(ln k(k), ln k(26)) all | stationary | non-stat | partial (given ln A(k)) all | ICC ln k(k) over runs")
runs_k = w.with_columns(lk=pl.col("kappa").log())
for k in range(9, 26):
    col = str(k)
    if col not in piv.columns:
        continue
    x = piv.join(ref, on="base").select("base", col, "ref").drop_nulls()
    if x.height < 30:
        continue
    bs = x["base"].to_list(); xv = x[col].to_numpy(); yv = x["ref"].to_numpy(); st = np.array([abs(gk[b]) < 0.05 for b in bs])
    rho = spearmanr(xv, yv)[0]; rs = spearmanr(xv[st], yv[st])[0]; rn = spearmanr(xv[~st], yv[~st])[0] if (~st).sum() > 8 else float("nan")
    Ak = pivA.join(x.select("base"), on="base")
    Ak = Ak.sort("base"); x2 = x.sort("base"); zA = Ak[col].to_numpy()
    pr = partial_spearman(x2[col].to_numpy(), x2["ref"].to_numpy(), zA)
    gl = [g["lk"].to_numpy() for _, g in runs_k.filter(pl.col("k") == k).group_by("base")]
    icc = icc_groups(gl)[0] if len([g for g in gl if len(g) >= 6]) > 20 else float("nan")
    rows.append((k, x.height, rho, rs, rn, pr, icc))
    out.append(f"{k:2d} | {x.height:5d} | {rho:+.3f} | {rs:+.3f} | {rn:+.3f} | {pr:+.3f} | {icc:.3f}")

def first_stable(idx, thr):
    ks = [r[0] for r in rows]; vs = [r[idx] for r in rows]
    for i, k in enumerate(ks):
        if all((not np.isnan(v)) and v >= thr for v in vs[i:]):
            return k
    return None

out.append("\nPre-registered verdicts (README W7):")
r12 = [r for r in rows if r[0] == 12]; ge16 = [r for r in rows if r[0] >= 16]
out.append(f"P7.1 Spearman >= 0.6 at k=12: {r12[0][2] if r12 else float('nan'):+.3f}; >= 0.8 for every k >= 16: min {min(r[2] for r in ge16):+.3f} -> "
           + ("HELD" if r12 and r12[0][2] >= 0.6 and min(r[2] for r in ge16) >= 0.8 else "FAILED"))
ks_all, ks_stat, ks_ns = first_stable(2, 0.8), first_stable(3, 0.8), first_stable(4, 0.8)
out.append(f"first k from which rank correlation stays >= 0.8: all {ks_all}, stationary {ks_stat}, non-stationary {ks_ns}")
out.append(f"P7.2 non-stationary crossing later by >= 4 octaves AND >= k=20: " + (f"{ks_ns} vs {ks_stat} -> {'HELD' if (ks_ns is not None and ks_stat is not None and ks_ns - ks_stat >= 4 and ks_ns >= 20) else 'FAILED'}" if ks_stat is not None else "not evaluable (stationary never reaches 0.8)"))
txt = header("uv run experiments/archive/2026-10-kappa-rule-space/scripts/w7_emergence.py") + "\n".join(out) + "\n"
(EXP / "results" / "w7_emergence.txt").write_text(txt); print(txt)
