# /// script
# dependencies = ["polars", "numpy", "scipy"]
# ///
"""Cross-check for items 9/10/14 (read-only on experiments/archive/2026-10-knockout-maps/knock/ and experiments/archive/2026-10-knockout-maps/dumps/): are the knockout map's hot tiles rich in the rare
colours that item 14 found to be critical?  Uses experiments/archive/2026-10-knockout-maps/knock/RULE/tiles.csv (5x5 tiles: x,y top-left relative to home, loss, nvis, hot)
and experiments/archive/2026-10-knockout-maps/dumps/RULE.grid (the field the knockout agent used; 255 = never visited)."""
import numpy as np, polars as pl
from scipy import stats
S = 4096; C = S // 2
for rule, n in [("RRRRRLLLLLL", 11), ("RLLLLRRRRLR", 11)]:
    g = np.fromfile(f"experiments/archive/2026-10-knockout-maps/dumps/{rule}.grid", dtype=np.uint8).reshape(S, S)
    vis = g != 255
    cnt = np.bincount(g[vis], minlength=n)[:n]
    order = np.argsort(cnt)
    rare = [int(k) for k in order[:3]]  # the three rarest colours
    print(f"\n{rule}: colour counts {cnt.tolist()} -> rare colours {rare} ({cnt[rare].sum() / cnt.sum():.1%} of cells)")
    t = pl.read_csv(f"experiments/archive/2026-10-knockout-maps/knock/{rule}/tiles.csv").filter(pl.col("nvis") > 0)
    rare_n, rare_frac = [], []
    for x, y, nv in zip(t["x"], t["y"], t["nvis"]):
        sub = g[C + y:C + y + 5, C + x:C + x + 5]
        r = np.isin(sub, rare).sum(); rare_n.append(int(r)); rare_frac.append(r / max(nv, 1))
    t = t.with_columns(rare_n=pl.Series(rare_n), rare_frac=pl.Series(rare_frac))
    loss = t["loss"].to_numpy()
    print(f"  tiles with visited cells: {t.height}; hot tiles: {int(t['hot'].sum())}")
    print("  Spearman(loss, rare cells in tile) = %.3f ; Spearman(loss, rare fraction) = %.3f ; Spearman(loss, nvis) = %.3f" % (
        stats.spearmanr(loss, t["rare_n"])[0], stats.spearmanr(loss, t["rare_frac"])[0], stats.spearmanr(loss, t["nvis"])[0]))
    hot = t.filter(pl.col("hot") == 1)
    print("  rare cells per tile: hot mean %.2f vs all-tile mean %.2f; rare fraction hot %.3f vs all %.3f" % (
        hot["rare_n"].mean(), t["rare_n"].mean(), hot["rare_frac"].mean(), t["rare_frac"].mean()))
    # permutation test for hot-tile enrichment
    rng = np.random.default_rng(20261013)
    obs = hot["rare_n"].mean(); k = hot.height
    perm = np.array([rng.choice(t["rare_n"].to_numpy(), k, replace=False).mean() for _ in range(5000)])
    print("  permutation p(hot tiles have >= this many rare cells) = %.4f" % ((perm >= obs).mean()))
    # partial: regress loss rank on nvis and distance, then correlate residual with rare count
    from scipy.stats import rankdata
    X = np.c_[np.ones(t.height), rankdata(t["nvis"]), rankdata(t["dist"]), rankdata(t["occ"])]
    def resid(v):
        v = rankdata(v); b, *_ = np.linalg.lstsq(X, v, rcond=None); return v - X @ b
    print("  partial Spearman(loss, rare cells | nvis, dist, occupancy) = %.3f" % stats.pearsonr(resid(loss), resid(t["rare_n"].to_numpy()))[0])
