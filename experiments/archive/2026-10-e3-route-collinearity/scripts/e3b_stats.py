# /// script
# dependencies = ["polars", "numpy"]
# ///
"""E3b: loss for homeward-dominant vs outward-dominant excursion cells at equal route-count quartile. Decision rules: notes/frontier-2026-10-13-results.md. usage: uv run experiments/archive/2026-10-a6-corruption-mechanism/scripts/a6_stats.py"""
import numpy as np, polars as pl
for rule in ("RRRRRLLLLLL", "RLLLLRRRRLR"):
    B = float(pl.read_csv(f"experiments/archive/2026-10-knockout-maps/knock/{rule}/base.csv")["near_home"][0])
    d = pl.read_csv(f"experiments/archive/2026-10-knockout-maps/knock/{rule}/e3b.csv").filter(pl.col("ok") == 1).with_columns(loss=B - pl.col("near_home"), cls=pl.col("x"), q=pl.col("y"))
    print(f"\n{rule}: base near_home {B:.4f}; runs {d.height}")
    stats = {}
    for c in (0, 1):
        row = []
        for q in range(4):
            v = d.filter((pl.col("cls") == c) & (pl.col("q") == q))["loss"].to_numpy()
            stats[(c, q)] = (v.mean(), v.std(ddof=1) / np.sqrt(len(v)), len(v)); row.append(f"q{q}: {v.mean():+.4f}+-{v.std(ddof=1)/np.sqrt(len(v)):.4f} (n={len(v)})")
        print(("homeward " if c else "outward  ") + "  ".join(row))
    for c in (0, 1):
        a, b = stats[(c, 3)], stats[(c, 0)]; z = (a[0] - b[0]) / np.hypot(a[1], b[1])
        print(f"  {'homeward' if c else 'outward'}: q3 - q0 = {a[0]-b[0]:+.4f} ({z:+.1f} SE) -> {'(more visited hurts less)' if z < -2 else 'more visited hurts more' if z > 2 else 'flat/mixed'}")
    nsig = 0
    for q in range(4):
        a, b = stats[(1, q)], stats[(0, q)]; z = (a[0] - b[0]) / np.hypot(a[1], b[1]); nsig += abs(z) > 2
        print(f"  q{q}: homeward - outward = {a[0]-b[0]:+.4f} ({z:+.1f} SE)")
    print(f"  quartiles with |homeward - outward| > 2 SE: {nsig} of 4 -> leg direction matters at equal occupancy: {nsig >= 3}")
