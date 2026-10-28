# /// script
# dependencies = ["polars", "numpy"]
# ///
"""Baseline for item 24: the square-lattice ants' area exponent in the SAME window (k=16..24, area at t=2^k)
as the hex screen, using probe_all.csv (t is the window end; k is log2 t)."""
import numpy as np, polars as pl
p = pl.read_csv("experiments/archive/2026-10-probe-growth-census/results/probe_all.csv").filter(~pl.col("escaped") & (pl.col("k") >= 16) & (pl.col("k") <= 24))
s = pl.read_csv("experiments/archive/2026-10-probe-growth-census/results/probe_summary.csv").filter((pl.col("cls") == "blob") & (pl.col("alpha_w") > 0.3) & (pl.col("alpha_w") < 0.37))
core = set(s["rule"].to_list())
a = []
for (r,), g in p.group_by("rule"):
    if r in core and g.height == 9:
        g = g.sort("k"); a.append(np.polyfit(g["k"].to_numpy() * np.log(2), np.log(g["area"].to_numpy()), 1)[0])
a = np.array(a); print("square ants core rules:", len(a), "area exponent k16-24 quantiles 10/25/50/75/90:", np.round(np.quantile(a, [.1, .25, .5, .75, .9]), 3))
