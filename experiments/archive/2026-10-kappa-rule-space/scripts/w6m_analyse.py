# /// script
# dependencies = ["polars", "numpy", "scipy"]
# ///
"""W6 matched-area reanalysis (M1-M3 in README, 'W6 matched-area reanalysis', registered before this script existed).
Reads dumps/w6_probe.csv (seeds 401..406) and results/w6_pairs.csv; no new simulation.
usage (repo root): uv run experiments/archive/2026-10-kappa-rule-space/scripts/w6m_analyse.py"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import numpy as np, polars as pl
from kcommon import *

NULL_RAW = 0.036  # W6 P6.2 raw 3-vs-3 replicate null of |d ln kappa| (results/w6_stats.txt), fixed in the registration
raw = pl.read_csv(EXP / "dumps" / "w6_probe.csv")
r = per_rule(raw).with_columns(seed=pl.col("rule").str.split("@").list.last().cast(int), base=pl.col("rule").str.split("@").list.first())
r = r.join(raw.filter(pl.col("k") == 22).select("rule", lnA22=pl.col("area").log()), on="rule", how="left")
core = r.filter(pl.col("alpha_w").is_between(0.25, 0.42) & (pl.col("kappa") > 0)).with_columns(lk=pl.col("kappa").log())
R = {}
for (rule,), g in core.group_by("base"):
    if g.height >= 4:
        R[rule] = dict(lk=dict(zip(g["seed"], g["lk"])), A=dict(zip(g["seed"], g["lnA22"])))
sat = pl.read_csv(EXP / "results" / "w6_pairs_scored.csv")  # carries stationarity-free pair list as scored in W6

rows = []
for b, j, m in pl.read_csv(EXP / "results" / "w6_pairs.csv").iter_rows():
    if b not in R or m not in R: continue
    sh = sorted(set(R[b]["lk"]) & set(R[m]["lk"]))
    mb = lambda k, x: np.mean(list(R[x][k].values()))
    d = mb("lk", m) - mb("lk", b); dA = mb("A", m) - mb("A", b)
    # SE of dA from shared-seed differences (patch is shared, so paired differences are the honest noise)
    pa = np.array([R[m]["A"][s] - R[b]["A"][s] for s in sh]) if len(sh) >= 3 else np.array([np.nan, np.nan])
    seA = pa.std(ddof=1) / np.sqrt(len(pa)) if len(sh) >= 3 else np.nan
    rows.append(dict(base=b, pos=j, mutant=m, early=int(j <= 3), d=d, dA=dA, seA=seA))
P = pl.DataFrame(rows)
assert P.height == sat.height, (P.height, sat.height)  # same 277 usable pairs as W6
assert np.allclose(np.sort(P["d"].to_numpy()), np.sort(sat["d"].to_numpy()))
out = [header("uv run scripts/w6m_analyse.py"), f"usable pairs {P.height} (early {P['early'].sum()}), bases {P['base'].n_unique()}"]
bases = sorted(P["base"].unique().to_list())
byb = {b: P.filter(pl.col("base") == b) for b in bases}
brng = np.random.default_rng(20261014 + 31)
BOOT = [brng.integers(0, len(bases), len(bases)) for _ in range(2000)]  # one set of resamples, shared by all tests

def frame(idx):
    return pl.concat([byb[bases[i]] for i in idx])

def ratio_med(P_, cal):
    s = P_.filter(pl.col("dA").abs() < cal)
    e = s.filter(pl.col("early") == 1)["d"].abs().to_numpy(); l = s.filter(pl.col("early") == 0)["d"].abs().to_numpy()
    return (np.median(e) / np.median(l)) if len(e) and len(l) else np.nan

def ols(P_, feat="early"):
    x = P_["early"].to_numpy().astype(float) if feat == "early" else np.log(P_["pos"].to_numpy().astype(float))
    X = np.column_stack([np.ones(P_.height), P_["dA"].to_numpy(), x]); y = P_["d"].to_numpy()
    return np.linalg.lstsq(X, y, rcond=None)[0]

def resid_ratio(P_):
    b0, b1, g = ols(P_); res = np.abs(P_["d"].to_numpy() - b0 - b1 * P_["dA"].to_numpy() - g * P_["early"].to_numpy())
    e = P_["early"].to_numpy() == 1
    return np.median(res[e]) / np.median(res[~e])

def ci(f, P0, restrict=None):
    v = []
    for idx in BOOT:
        Q = frame(idx)
        if restrict is not None: Q = restrict(Q)
        try: v.append(f(Q))
        except Exception: pass
    v = np.array(v); v = v[np.isfinite(v)]
    return np.percentile(v, [2.5, 97.5]), len(v)

for cal in (0.15, 0.10, 0.25):
    s = P.filter(pl.col("dA").abs() < cal); ne = int(s["early"].sum()); nl = s.height - ne
    est = ratio_med(P, cal); (lo, hi), nb = ci(lambda Q: ratio_med(Q, cal), P)
    tag = "PRIMARY M1" if cal == 0.15 else "sensitivity"
    out.append(f"{tag}: caliper |dA|<{cal}: early n={ne}, late n={nl}; median |d| early {np.median(s.filter(pl.col('early')==1)['d'].abs()):.3f} vs late {np.median(s.filter(pl.col('early')==0)['d'].abs()):.3f}; ratio {est:.2f} [{lo:.2f}, {hi:.2f}] ({nb} usable draws)"
               + (f"  -> M1 {'HELD' if est >= 1.3 and lo > 1 else 'FAILED'}" if cal == 0.15 else ""))
    if ne < 20: out.append(f"   UNDERPOWERED flag: fewer than 20 early pairs ({ne})")
    if cal == 0.15:
        late_med = float(np.median(s.filter(pl.col('early') == 0)['d'].abs())); out.append(f"M3: late median |d| at caliper {late_med:.3f} = {late_med / NULL_RAW:.2f} x raw null {NULL_RAW} (bar 1.5) -> M3 {'HELD' if late_med >= 1.5 * NULL_RAW else 'FAILED'}")

b0, b1, g = ols(P); (glo, ghi), _ = ci(lambda Q: ols(Q)[2], P)
out.append(f"M2: d = {b0:+.3f} + {b1:.3f} dA + {g:+.3f} early; gamma 95% CI [{glo:+.3f}, {ghi:+.3f}] -> M2 {'HELD (gamma != 0)' if glo > 0 or ghi < 0 else 'FAILED (CI includes 0)'}")
(b1lo, b1hi), _ = ci(lambda Q: ols(Q)[1], P); out.append(f"   beta(dA) {b1:.3f} [{b1lo:.3f}, {b1hi:.3f}]")
_, bl, gl = ols(P, "logpos"); (lo, hi), _ = ci(lambda Q: ols(Q, "logpos")[2], P)
out.append(f"   log(pos) variant: slope on ln pos {gl:+.3f} [{lo:+.3f}, {hi:+.3f}], beta(dA) {bl:.3f}")
rr = resid_ratio(P); (lo, hi), _ = ci(resid_ratio, P); out.append(f"   residual contrast median|r| early/late {rr:.2f} [{lo:.2f}, {hi:.2f}]")

# errors-in-variables bound: reliability of dA, lam = 1 - mean(seA^2)/var(dA); beta/lam is an upper bound on the corrected slope
seA2 = np.nanmean(P["seA"].to_numpy() ** 2); lam = 1 - seA2 / P["dA"].to_numpy().var(ddof=1)
out.append(f"sensitivity: reliability of dA (shared-seed paired SE) lam = {lam:.3f}; attenuation-corrected beta <= {b1 / lam:.3f}")
b0c, b1c = b0, b1 / lam
# gamma with beta fixed at the corrected value (largest plausible area absorption): early minus late mean residual
resid = P["d"].to_numpy() - b1c * P["dA"].to_numpy(); e = P["early"].to_numpy() == 1
out.append(f"   gamma if beta were {b1c:.3f}: {resid[e].mean() - resid[~e].mean():+.3f} (mean residual early minus late, descriptive)")

# stationarity restriction: stationary mutant, as in w6_checks (uses |g_k| < 0.05 of the mutant's W6 runs)
g_k = core.group_by("base").agg(g=pl.col("g_k").median()).with_columns(st=pl.col("g").abs() < 0.05)
st = set(g_k.filter(pl.col("st"))["base"].to_list())
Ps = P.filter(pl.col("mutant").is_in(list(st)))
bs = sorted(Ps["base"].unique().to_list())
out.append(f"stationary-mutant restriction (|median g_k|<0.05 in W6 runs): {Ps.height} pairs (early {int(Ps['early'].sum())})")
sub = lambda Q: Q.filter(pl.col("mutant").is_in(list(st)))
e15 = ratio_med(Ps, 0.15); (lo, hi), _ = ci(lambda Q: ratio_med(Q, 0.15), P, restrict=sub); out.append(f"   M1 ratio at 0.15: {e15:.2f} [{lo:.2f}, {hi:.2f}]")
gs = ols(Ps)[2]; (lo, hi), _ = ci(lambda Q: ols(Q)[2], P, restrict=sub); out.append(f"   M2 gamma: {gs:+.3f} [{lo:+.3f}, {hi:+.3f}]")
(EXP / "results" / "w6m_stats.txt").write_text("\n".join(out) + "\n"); print("\n".join(out))
