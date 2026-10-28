# /// script
# dependencies = ["polars", "numpy", "scipy"]
# ///
"""H1 (research-frontier-2026-10-13-pm.md): is the rule-specific part of the area exponent carried by drift of the filling fraction eta = A/(W_x W_y)?
usage: uv run experiments/archive/2026-10-h1-lacunarity-decomposition/scripts/h1_lacunarity.py > experiments/archive/2026-10-h1-lacunarity-decomposition/results/h1_lacunarity.txt   (input experiments/archive/2026-10-b2-between-rule-variance/results/b2_probe.csv, window k = 20..26, as b2_anova.py)"""
import sys
import numpy as np, polars as pl
from scipy import stats
sys.path.insert(0, "experiments/_lib")
import analyse_probe as ap
ap.KLO, ap.KHI = 20, 26
raw = pl.read_csv("experiments/archive/2026-10-b2-between-rule-variance/results/b2_probe.csv").filter(~pl.col("escaped"))
runs = ap.per_rule(pl.read_csv("experiments/archive/2026-10-b2-between-rule-variance/results/b2_probe.csv"))
# exact x/y exponents (the identity a = ax + ay + g_eta is exact only with the two box sides)
ex = []
for (rule,), g in raw.group_by("rule"):
    g = g.filter((pl.col("k") >= 20) & (pl.col("k") <= 26)).sort("k")
    if g.height < 7: continue
    t = g["t"].to_numpy().astype(float)
    ex.append(dict(rule=rule, ax=ap.slope(t, g["width"].to_numpy()), ay=ap.slope(t, g["height"].to_numpy())))
runs = runs.join(pl.DataFrame(ex), on="rule").with_columns(
    base=pl.col("rule").str.split("@").list.first(), geta=pl.col("g_fill"),
    d=pl.col("a") - 2 * pl.col("alpha_w"), a_hat=pl.col("a") - pl.col("ax") - pl.col("ay"))
print(f"runs {runs.height} (not escaped, full window); rules {runs['base'].n_unique()}")
print("identity check, corr(a-ax-ay, g_fill) =", round(float(np.corrcoef(runs['a_hat'], runs['geta'])[0, 1]), 4), " max abs diff", round(float((runs['a_hat'] - runs['geta']).abs().max()), 4))
def icc(col, df):
    groups = [g[col].to_numpy() for _, g in df.group_by("base") if g.height >= 6]
    sw = np.sqrt(np.mean([g.var(ddof=1) for g in groups])); means = np.array([g.mean() for g in groups]); m = np.mean([len(g) for g in groups])
    sb2 = max(means.var(ddof=1) - sw ** 2 / m, 0.0)
    return len(groups), sw, np.sqrt(sb2), sb2 / (sb2 + sw ** 2)
for label, df in (("all runs", runs), ("core band 0.25<alpha_w<0.42", runs.filter(pl.col("alpha_w").is_between(0.25, 0.42)))):
    print(f"\n== {label}: {df.height} runs")
    r = stats.linregress(df["geta"].to_numpy(), df["d"].to_numpy())
    print(f"R^2(g_eta -> a-2alpha_w) = {r.rvalue**2:.3f}, slope {r.slope:.3f}")
    for c in ("a", "alpha_w", "geta", "d"):
        n, sw, sb, i = icc(c, df); print(f"ICC {c:8s} rules {n}  sd_within {sw:.4f}  sd_between {sb:.4f}  ICC {i:.3f}")
    m = df.group_by("base").agg(pl.col("geta").mean(), pl.col("a").mean(), pl.col("alpha_w").mean(), pl.col("fill").mean())
    print(f"mean g_eta {m['geta'].mean():+.4f}  (rule-mean sd {m['geta'].std():.4f}); frac rules g_eta>0: {(m['geta']>0).mean():.2f}")
    print(f"rule means: corr(fill, g_eta) = {np.corrcoef(m['fill'], m['geta'])[0,1]:+.3f}; corr(a, g_eta) = {np.corrcoef(m['a'], m['geta'])[0,1]:+.3f}; corr(alpha_w, g_eta) = {np.corrcoef(m['alpha_w'], m['geta'])[0,1]:+.3f}")
    hi = m.filter(pl.col("a") > 2/3 + 0.01); lo = m.filter(pl.col("a") < 2/3 - 0.01)
    print(f"rules a>2/3+.01: n={hi.height} mean g_eta {hi['geta'].mean():+.4f}; a<2/3-.01: n={lo.height} mean g_eta {lo['geta'].mean():+.4f}")
