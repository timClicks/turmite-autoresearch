# /// script
# dependencies = ["polars", "numpy"]
# ///
"""H3 + H1 follow-up (notes/research-frontier-2026-10-13-pm.md). Input experiments/archive/2026-10-b2-between-rule-variance/results/b2_probe.csv, window k=20..26 as b2_anova.py.
H3: does dividing A(t)/t^(2/3) by c*kappa cut the between-rule variance of log K by > 75%? Also free fit log K ~ b log(c kappa).
H1b: ICC and covariance of (alpha_x, alpha_y, g_eta) inside a = ax+ay+g_eta.  usage: uv run experiments/archive/2026-10-h3-scaling-collapse/scripts/h3_collapse.py > experiments/archive/2026-10-h3-scaling-collapse/results/h3_collapse.txt"""
import sys
import numpy as np, polars as pl
sys.path.insert(0, "experiments/_lib")
import analyse_probe as ap
ap.KLO, ap.KHI = 20, 26
raw = pl.read_csv("experiments/archive/2026-10-b2-between-rule-variance/results/b2_probe.csv").filter(~pl.col("escaped"))
runs = ap.per_rule(pl.read_csv("experiments/archive/2026-10-b2-between-rule-variance/results/b2_probe.csv"))
ex = []
for (rule,), g in raw.group_by("rule"):
    g = g.filter((pl.col("k") >= 20) & (pl.col("k") <= 26)).sort("k")
    if g.height < 7: continue
    t = g["t"].to_numpy().astype(float); r26 = g.filter(pl.col("k") == 26)
    ex.append(dict(rule=rule, ax=ap.slope(t, g["width"].to_numpy()), ay=ap.slope(t, g["height"].to_numpy()), A26=float(r26["area"][0]), t26=float(r26["t"][0])))
r = runs.join(pl.DataFrame(ex), on="rule").with_columns(base=pl.col("rule").str.split("@").list.first(), geta=pl.col("g_fill"))
r = r.filter(pl.col("alpha_w").is_between(0.25, 0.42)).with_columns(
    steps=pl.col("t26") / 2).with_columns(logK=(pl.col("A26") / pl.col("steps") ** (2 / 3)).log(), logck=(pl.col("c") * pl.col("kappa")).log())
print(f"core-band runs {r.height}, rules {r['base'].n_unique()}")
def icc(col):
    gs = [g[col].to_numpy() for _, g in r.group_by("base") if g.height >= 6]
    sw2 = np.mean([g.var(ddof=1) for g in gs]); means = np.array([g.mean() for g in gs]); m = np.mean([len(g) for g in gs])
    sb2 = max(means.var(ddof=1) - sw2 / m, 0.0); return len(gs), np.sqrt(sw2), np.sqrt(sb2), sb2 / (sb2 + sw2)
m = r.group_by("base").agg(pl.col(["logK", "logck", "ax", "ay", "geta", "a", "alpha_w"]).mean())
K, X = m["logK"].to_numpy(), m["logck"].to_numpy()
print(f"\nH3 (rule means of last-window values; c, kappa from k=26 window): var(log K) = {K.var(ddof=1):.4f}")
print(f"  var(log K - log(c kappa)) = {(K-X).var(ddof=1):.4f}  -> reduction {(1-(K-X).var(ddof=1)/K.var(ddof=1))*100:.1f}%")
b, a0 = np.polyfit(X, K, 1); res = K - (a0 + b * X)
print(f"  free fit log K = {a0:.3f} + {b:.3f} log(c kappa); R^2 = {1-res.var(ddof=1)/K.var(ddof=1):.3f}; corr = {np.corrcoef(K,X)[0,1]:+.3f}")
for name, f in (("c only", np.log(m['logck'].exp()*0+1)),):
    pass
print("\nH1b: ICC of exponents")
for c in ("ax", "ay", "geta", "a"):
    n, sw, sb, i = icc(c); print(f"  {c:5s} rules {n} sd_within {sw:.4f} sd_between {sb:.4f} ICC {i:.3f}")
C = np.cov(np.vstack([m['ax'], m['ay'], m['geta']])); print("rule-mean covariance (ax, ay, geta):"); print(np.round(C, 6))
tot = C.sum(); print(f"var(a rule means) = {m['a'].var(ddof=1):.6f}; contributions Cov(term, a): ax {C[0].sum():.6f}  ay {C[1].sum():.6f}  geta {C[2].sum():.6f}  (sum {tot:.6f})")
