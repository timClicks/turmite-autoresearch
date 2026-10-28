# /// script
# dependencies = ["polars", "numpy"]
# ///
"""ratio = kappa / kappa_unif(a, beta) per walker, per seed, with own (a, beta) from the same run.

Same estimators as 2026-10-kappa-uniform-baseline/scripts/analyse.py: log-log fits of area vs t
and perimeter vs area over the window set; kappa = mean over those windows of
(boundary_steps / (t/2)) / (perimeter/area). Here t is the probe CSV's t column, which is the
window END (window (t/2, t], k = log2 t); the baseline experiment's own CSV labels windows by
their start, so its t_end was 2^(k+1).
"""
from pathlib import Path
import numpy as np, polars as pl

root = Path(__file__).resolve().parents[1]
ANT = dict(q05=0.443, q25=0.664, med=0.814, q75=0.957, q95=1.332)  # results/census_spread.txt, baseline expt

def kunif(a, b):
    p = a * (1 - b); return 2 * (1 - 0.5 ** (1 - p)) / (1 - p)

def kunif_local(t, A, P):
    """Descriptive: per-window kappa_unif from local exponents of adjacent window ends (needs rows k-1, k)."""
    la, lp, lt = np.log(A), np.log(P), np.log(t)
    a = np.diff(la) / np.diff(lt); b = np.diff(lp) / np.diff(la)
    return np.array([kunif(x, y) for x, y in zip(a, b)])

def walker(d, lo, hi):
    out = []
    for run in sorted(d["rule"].unique()):
        g = d.filter(pl.col("rule") == run).sort("k")
        esc = int(g["escaped"].sum())
        w = g.filter((pl.col("k") >= lo) & (pl.col("k") <= hi))
        if w.height < hi - lo + 1: out.append(dict(run=run, esc=esc, ok=False)); continue
        t = w["t"].to_numpy().astype(float); A = w["area"].to_numpy().astype(float); P = w["perimeter"].to_numpy().astype(float)
        kap = (w["boundary_steps"].to_numpy() / (t / 2)) / (P / A)
        a = np.polyfit(np.log(t), np.log(A), 1)[0]; b = np.polyfit(np.log(A), np.log(P), 1)[0]
        # local reference: window k uses area/perimeter at ends of windows k-1 and k
        g2 = g.filter((pl.col("k") >= lo - 1) & (pl.col("k") <= hi))
        ku_loc = kunif_local(g2["t"].to_numpy().astype(float), g2["area"].to_numpy().astype(float), g2["perimeter"].to_numpy().astype(float)).mean()
        out.append(dict(run=run, esc=esc, ok=True, a=a, beta=b, kappa=kap.mean(), ku=kunif(a, b), ku_loc=ku_loc,
                        ratio=kap.mean() / kunif(a, b), ratio_loc=kap.mean() / ku_loc))
    return out

def report(name, rows, lines):
    ok = [r for r in rows if r["ok"]]
    n_esc = sum(1 for r in rows if r["esc"] > 0)
    f = lambda k: np.array([r[k] for r in ok])
    def ms(k): x = f(k); return f"{x.mean():.3f} (sd {x.std(ddof=1):.3f})"
    lines.append(f"{name:26s} n={len(ok)}/{len(rows)} esc_runs={n_esc} a={ms('a')} beta={ms('beta')} kappa={ms('kappa')} "
                 f"kunif={ms('ku')} ratio={ms('ratio')}  [local-ref ratio={ms('ratio_loc')}]")
    r = f("ratio"); m, s = r.mean(), r.std(ddof=1)
    where = "above ant IQR" if m > ANT["q75"] else ("in ant IQR" if m >= ANT["q25"] else "below ant IQR")
    where += ", inside ant 5-95" if ANT["q05"] <= m <= ANT["q95"] else ", OUTSIDE ant 5-95"
    z = (m - ANT["q75"]) / s if s > 0 else float("inf")
    lines.append(f"{'':26s} -> {where}; (mean - ant q75)/seed-sd = {z:.1f}; ant median 0.814")

lines = [f"ant (census_spread.txt): {ANT}"]
mem = pl.read_csv(root / "results/probe_mem.csv")
for pre, nm in [("rw:", "rw"), ("pw:0.25:", "pw:0.25"), ("pw:0.5:", "pw:0.5"), ("pw:0.75:", "pw:0.75")]:
    d = mem.filter(pl.col("rule").str.starts_with(pre))
    report(f"{nm} k=12..22", walker(d, 12, 22), lines)
rot = pl.read_csv(root / "results/probe_rotor.csv")
report("rotor k=12..22", walker(rot, 12, 22), lines)
report("rotor k=20..26", walker(rot, 20, 26), lines)
lines.append("mean-field anchor (baseline expt, not rerun): kappa 1.118 / kunif 1.107 = 1.010 (seed sd 0.009)")
(root / "results/analysis.txt").write_text("\n".join(lines) + "\n"); print("\n".join(lines))
