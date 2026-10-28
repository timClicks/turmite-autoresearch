# /// script
# dependencies = ["polars", "numpy"]
# ///
"""Item 14 follow-up: recolour all cells of colour K (to a random other colour) vs recolour the same number of random cells; and spatial core shuffles.
Input experiments/archive/2026-10-recolour/results/recolour.csv (tetherlab dose, age 2^24, 12 seeds)."""
import numpy as np, polars as pl
raw = open("experiments/archive/2026-10-recolour/results/recolour.csv").read().splitlines(); hdr = raw[0].split(",")
d = pl.DataFrame([l.split(",") for l in raw if not l.startswith("rule,") and l], schema=hdr, orient="row").with_columns(spread=pl.col("spread").cast(pl.Float64))
cnt = {}
for l in open("experiments/archive/2026-10-colourstats/results/describe_colours.csv"):
    p = l.strip().split(",")
    if p[0] != "rule": cnt[(p[0], int(p[1]))] = int(p[2])
m = lambda rule, mode: d.filter((pl.col("rule") == rule) & (pl.col("mode") == mode))["spread"].to_numpy()
for rule in ["RRRRRLLLLLL", "RLLLLRRRRLR"]:
    print(f"\n{rule}: real {m(rule,'real').mean():.1f} shuffle {m(rule,'shuffle').mean():.1f}")
    print(" colour (cells) | recolour class | recolour same number of random cells | ratio")
    for k in range(11):
        a, c = m(rule, f"recolour:{k}"), m(rule, f"recolourctrl:{k}")
        print(f"   {k:2d} ({cnt[(rule,k)]:4d})   | {a.mean():5.1f}+-{a.std(ddof=1):3.1f}   | {c.mean():5.1f}+-{c.std(ddof=1):3.1f}   | {a.mean()/c.mean():.2f}")
    print(" spatial core shuffles (cells within R of home):", {R: round(float(m(rule, f'core:{R}').mean()), 1) for R in (10, 20, 30, 40)})
