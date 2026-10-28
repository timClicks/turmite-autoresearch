# /// script
# dependencies = ["polars", "numpy"]
# ///
"""E1 follow-up: why does the rotated-field coarse map show only 2 hot tiles (original: 11) although the rotated hot tiles have the same mean loss?
Lists the top tiles of experiments/archive/2026-10-e1-one-sided-hot-region/knock_e1/RRRRRLLLLLL_rot90 against the null thresholds and the tile-grid origin mod 5 of both maps. usage: uv run experiments/archive/2026-10-e1-one-sided-hot-region/scripts/e1_rot_alignment.py"""
import numpy as np, polars as pl
b = pl.read_csv("experiments/archive/2026-10-e1-one-sided-hot-region/knock_e1/RRRRRLLLLLL_rot90/base.csv"); B = float(b["near_home"][0])
c = pl.read_csv("experiments/archive/2026-10-e1-one-sided-hot-region/knock_e1/RRRRRLLLLLL_rot90/coarse.csv").filter(pl.col("ok") == 1).with_columns(loss=B - pl.col("near_home"))
null = c.filter(pl.col("kind") == "swap")["loss"].to_numpy(); p95 = np.quantile(null, .95); p95m3 = np.quantile(np.random.default_rng(0).choice(null, size=(20000, 3)).mean(axis=1), .95)
t = c.filter((pl.col("kind") == "patch") & (pl.col("nvis") > 0)).group_by("x", "y").agg(loss=pl.col("loss").mean(), nex=(pl.col("loss") > p95).sum()).sort("loss", descending=True)
print("rotated map: single-swap p95", round(float(p95), 4), " mean-of-3 p95", round(float(p95m3), 4)); print(t.head(14))
print("tile origin (x mod 5, y mod 5): rotated map", sorted({(int(x) % 5, int(y) % 5) for x, y in zip(t['x'], t['y'])}))
o = pl.read_csv("experiments/archive/2026-10-knockout-maps/knock/RRRRRLLLLLL/coarse.csv"); print("original map", sorted({(int(x) % 5, int(y) % 5) for x, y in zip(o['x'], o['y'])}))
hot = [(-(int(float(y)) + 4), int(float(x))) for x, y in ((r.split(',')[0], r.split(',')[1]) for r in open("experiments/archive/2026-10-knockout-maps/knock/RRRRRLLLLLL/hot.csv").read().splitlines()[1:])]
print("rotated positions of the 11 original hot tiles (x mod 5, y mod 5):", sorted({(x % 5, y % 5) for x, y in hot}))
