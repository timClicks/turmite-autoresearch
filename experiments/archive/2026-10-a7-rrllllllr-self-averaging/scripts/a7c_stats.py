# /// script
# dependencies = ["polars", "numpy"]
# ///
"""A7c: RRLLLLLLR to 2^32, 64 new seeds. Rule: notes/frontier-2026-10-13-results.md."""
import numpy as np, polars as pl
rng = np.random.default_rng(20261013)
d = pl.read_csv("experiments/archive/2026-10-a7-rrllllllr-self-averaging/results/a7c_probe.csv").filter(~pl.col("escaped")).with_columns(seed=pl.col("rule").str.split("@").list.get(1).cast(pl.Int64))
print("usable seeds:", d["seed"].n_unique(), "of 64")
cv = {}
for k in range(26, 33):
    x = d.filter(pl.col("k") == k).sort("seed")["area"].to_numpy() / 2.0 ** (2 * k / 3)
    if len(x) < 20: continue
    bs = [(lambda s: s.std(ddof=1) / s.mean())(rng.choice(x, len(x))) for _ in range(2000)]
    cv[k] = (x.std(ddof=1) / x.mean(), float(np.std(bs)), len(x), x.mean()); print(f"k={k}: n={len(x)} CV={cv[k][0]:.3f} +- {cv[k][1]:.3f} mean x={x.mean():.3f} median x={np.median(x):.3f}")
ks = sorted(cv)
if 32 in cv and 30 in cv:
    diff = cv[32][0] - cv[30][0]; se = np.hypot(cv[32][1], cv[30][1]); mx = max(cv[k][0] for k in ks if k <= 31); kmx = max((k for k in ks if k <= 31), key=lambda k: cv[k][0])
    sp = np.corrcoef(np.argsort(np.argsort([k for k in ks if k >= 28])), np.argsort(np.argsort([cv[k][0] for k in ks if k >= 28])))[0, 1]
    print(f"CV(32)-CV(30) = {diff:+.3f} ({diff/se:+.1f} SE); max CV at k<=31: {mx:.3f} (k={kmx}); CV(32)-max = {cv[32][0]-mx:+.3f}; Spearman(CV,k) over k>=28: {sp:.2f}")
    print("verdict:", "non-self-averaging (still rising)" if diff > 2 * se and sp >= 0.8 else "peaked/converging" if cv[32][0] < mx - 2 * np.hypot(cv[32][1], cv[kmx][1]) else "undecided")
