# /// script
# dependencies = ["polars", "numpy"]
# ///
"""A7: is RRLLLLLLR@seed non-self-averaging? Input experiments/archive/2026-10-a7-rrllllllr-self-averaging/results/a7_probe.csv (200 seeds 25..224, probe to 2^30) plus, as a
separate row, the 24 item-4 seeds. Decision rule is in notes/frontier-2026-10-13-results.md (written before the run).
usage: uv run experiments/archive/2026-10-a7-rrllllllr-self-averaging/scripts/a7_stats.py"""
import polars as pl, numpy as np
rng = np.random.default_rng(20261013)
def table(path):
    d = pl.read_csv(path).filter(~pl.col("escaped"))
    d = d.with_columns(seed=pl.col("rule").str.split("@").list.get(1).cast(pl.Int64))
    return d
def cvs(d, ks):
    out = {}
    piv = {k: d.filter(pl.col("k") == k).sort("seed")["area"].to_numpy() / 2.0 ** (2 * k / 3) for k in ks}
    for k, x in piv.items():
        boots = [ (lambda s: s.std(ddof=1) / s.mean())(rng.choice(x, len(x))) for _ in range(2000)]
        out[k] = (x.std(ddof=1) / x.mean(), float(np.std(boots)), x)
    return out
for label, path in [("200 new seeds", "experiments/archive/2026-10-a7-rrllllllr-self-averaging/results/a7_probe.csv"), ("item-4 seeds 1..24", "experiments/archive/2026-10-item4-exponent-rotor-calibrated/results/item4_probe.csv")]:
    d = table(path)
    if label.startswith("item"): d = d.filter(pl.col("rule").str.starts_with("RRLLLLLLR@"))
    ks = list(range(24, 31)) if label.startswith("200") else list(range(24, 31))
    ks = [k for k in ks if d.filter(pl.col("k") == k).height > 0]
    r = cvs(d, ks)
    print(f"\n{label}: seeds {d['seed'].n_unique()}, escaped runs dropped")
    for k in ks: print(f"  k={k}: n={len(r[k][2])} CV={r[k][0]:.3f} +- {r[k][1]:.3f}  mean x={r[k][2].mean():.3f}")
    kk = np.array(ks); cv = np.array([r[k][0] for k in ks])
    rho = np.corrcoef(np.argsort(np.argsort(kk)), np.argsort(np.argsort(cv)))[0, 1]
    print(f"  Spearman(CV,k) = {rho:.2f}; argmax k = {ks[int(cv.argmax())]}")
    if 30 in r and 26 in r:
        diff = r[30][0] - r[26][0]; se = np.hypot(r[30][1], r[26][1])
        print(f"  CV(30)-CV(26) = {diff:.3f}  ({diff/se:.1f} SE)")
    if ks[-1] in r:
        x = np.log(r[ks[-1]][2]); h = 1.06 * x.std(ddof=1) * len(x) ** -0.2
        g = np.linspace(x.min() - 3 * h, x.max() + 3 * h, 400)
        dens = np.exp(-0.5 * ((g[:, None] - x[None]) / h) ** 2).sum(1)
        mx = [i for i in range(1, 399) if dens[i] > dens[i - 1] and dens[i] > dens[i + 1]]
        print(f"  KDE modes of log x_{ks[-1]}: {len(mx)} at x = {np.round(np.exp(g[mx]), 3).tolist()}; quantiles 5/25/50/75/95% of x: {np.round(np.quantile(r[ks[-1]][2], [.05,.25,.5,.75,.95]), 3).tolist()}")
