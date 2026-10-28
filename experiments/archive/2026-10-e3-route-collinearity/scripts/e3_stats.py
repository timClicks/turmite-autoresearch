# /// script
# dependencies = ["polars", "numpy", "scipy"]
# ///
"""E3: homeward-leg counts (ret.u32) vs knockout loss, controlling for occupancy, distance and dose. Decision rule: notes/frontier-2026-10-13-results.md.
usage: uv run experiments/archive/2026-10-e3-route-collinearity/scripts/e3_stats.py"""
import numpy as np, polars as pl
from scipy.stats import spearmanr, rankdata
S, C = 4096, 2048
def partial(y, x, controls):
    def res(v):
        A = np.column_stack([np.ones(len(v))] + [rankdata(c) for c in controls]); r = rankdata(v)
        return r - A @ np.linalg.lstsq(A, r, rcond=None)[0]
    return float(np.corrcoef(res(y), res(x))[0, 1])
for rule in ("RRRRRLLLLLL", "RLLLLRRRRLR"):
    t = pl.read_csv(f"experiments/archive/2026-10-knockout-maps/knock/{rule}/tiles.csv")
    ret = np.fromfile(f"experiments/archive/2026-10-knockout-maps/knock/{rule}/e3/ret.u32", dtype="<u4").reshape(S, S).astype(float)
    r = np.array([ret[C + int(y):C + int(y) + 5, C + int(x):C + int(x) + 5].mean() for x, y in zip(t["x"], t["y"])])
    loss, occ, route, dist, dose = (t[c].to_numpy() for c in ("loss", "occ", "route", "dist", "dose"))
    ctrl = [np.log1p(occ), dist, dose]
    rng = np.random.default_rng(20261013); n = len(loss)
    boot = [partial(loss[i], r[i], [c[i] for c in ctrl]) for i in (rng.integers(0, n, n) for _ in range(1000))]
    print(f"{rule}: {n} tiles; share of excursion steps that are on homeward legs: {ret.sum() / max(route.sum() if False else np.fromfile(f'experiments/archive/2026-10-knockout-maps/knock/{rule}/route.u32', dtype='<u4').sum(), 1):.2f}")
    print(f"  Spearman(ret, occ) = {spearmanr(r, occ)[0]:.2f}; Spearman(ret, route) = {spearmanr(r, route)[0]:.2f}; Spearman(loss, ret) = {spearmanr(loss, r)[0]:.3f}")
    print(f"  partial Spearman(loss, ret | log1p occ, dist, dose) = {partial(loss, r, ctrl):.3f}  95% CI [{np.quantile(boot, .025):.3f}, {np.quantile(boot, .975):.3f}]  (route, for comparison: {partial(loss, route, ctrl):.3f})")
