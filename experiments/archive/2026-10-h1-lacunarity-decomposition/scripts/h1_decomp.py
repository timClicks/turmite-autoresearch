# /// script
# dependencies = ["polars", "numpy", "scipy"]
# ///
import sys
import numpy as np, polars as pl
from scipy import stats
sys.path.insert(0, "experiments/_lib")
import analyse_probe as ap
ap.KLO, ap.KHI = 20, 26

raw = pl.read_csv("experiments/archive/2026-10-b2-between-rule-variance/results/b2_probe.csv").filter(~pl.col("escaped"))
runs = ap.per_rule(pl.read_csv("experiments/archive/2026-10-b2-between-rule-variance/results/b2_probe.csv"))

ex = []
for (rule,), g in raw.group_by("rule"):
    g = g.filter((pl.col("k") >= 20) & (pl.col("k") <= 26)).sort("k")
    if g.height < 7: continue
    t = g["t"].to_numpy().astype(float)
    sx = ap.slope(t, g["width"].to_numpy())
    sy = ap.slope(t, g["height"].to_numpy())
    s_long = max(sx, sy)
    s_short = min(sx, sy)
    ex.append(dict(rule=rule, ax=sx, ay=sy, a_long=s_long, a_short=s_short, a_sum=sx+sy))

runs = runs.join(pl.DataFrame(ex), on="rule").with_columns(
    base=pl.col("rule").str.split("@").list.first(),
    geta=pl.col("g_fill"),
)

def icc(col, df):
    groups = [g[col].to_numpy() for _, g in df.group_by("base") if g.height >= 6]
    sw = np.sqrt(np.mean([g.var(ddof=1) for g in groups]))
    means = np.array([g.mean() for g in groups])
    m = np.mean([len(g) for g in groups])
    sb2 = max(means.var(ddof=1) - sw ** 2 / m, 0.0)
    return len(groups), sw, np.sqrt(sb2), sb2 / (sb2 + sw ** 2)

for label, df in (("all runs", runs), ("core band 0.25<alpha_w<0.42", runs.filter(pl.col("alpha_w").is_between(0.25, 0.42)))):
    print(f"\n==================== {label}: {df.height} runs ====================")
    for c in ("a", "alpha_w", "a_long", "a_short", "a_sum", "geta"):
        n, sw, sb, i = icc(c, df)
        print(f"ICC {c:10s}: rules={n:2d}  sd_within={sw:.4f}  sd_between={sb:.4f}  ICC={i:.3f}")
    
    # Variance and covariance decomposition of a = a_long + a_short + geta (or ax + ay + geta)
    print("\nVariance and Covariance decomposition of a = ax + ay + geta:")
    cov_mat = np.cov([df["ax"], df["ay"], df["geta"]], ddof=1)
    print("Covariance matrix (ax, ay, geta):")
    print(cov_mat)
    var_a = df["a"].to_numpy().var(ddof=1)
    sum_cov = np.sum(cov_mat)
    print(f"Var(a) = {var_a:.6f}, Sum(Cov(ax,ay,geta)) = {sum_cov:.6f}")
    
    print("\nVariance and Covariance decomposition of a = a_long + a_short + geta:")
    cov_mat2 = np.cov([df["a_long"].to_numpy(), df["a_short"].to_numpy(), df["geta"].to_numpy()], ddof=1)
    print("Covariance matrix (a_long, a_short, geta):")
    print(cov_mat2)
    sum_cov2 = np.sum(cov_mat2)
    print(f"Var(a) = {var_a:.6f}, Sum(Cov(a_long, a_short, geta)) = {sum_cov2:.6f}")
    
    # Between-rule vs within-rule covariance decomposition
    print("\nBetween-rule means covariance (a_long, a_short, geta):")
    m = df.group_by("base").agg(pl.col("a_long").mean(), pl.col("a_short").mean(), pl.col("geta").mean(), pl.col("a").mean())
    cov_between = np.cov([m["a_long"].to_numpy(), m["a_short"].to_numpy(), m["geta"].to_numpy()], ddof=1)
    print(cov_between)
    var_between_a = m["a"].to_numpy().var(ddof=1)
    print(f"Var_between(a) = {var_between_a:.6f}, Sum(Cov_between) = {np.sum(cov_between):.6f}")
    print(f"Shares of Var_between(a):")
    print(f"  Var(a_long): {cov_between[0,0] / np.sum(cov_between) * 100:.1f}%")
    print(f"  Var(a_short): {cov_between[1,1] / np.sum(cov_between) * 100:.1f}%")
    print(f"  Var(geta): {cov_between[2,2] / np.sum(cov_between) * 100:.1f}%")
    print(f"  2*Cov(a_long, a_short): {2*cov_between[0,1] / np.sum(cov_between) * 100:.1f}%")
    print(f"  2*Cov(a_long, geta): {2*cov_between[0,2] / np.sum(cov_between) * 100:.1f}%")
    print(f"  2*Cov(a_short, geta): {2*cov_between[1,2] / np.sum(cov_between) * 100:.1f}%")
