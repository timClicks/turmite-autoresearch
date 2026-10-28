# /// script
# dependencies = ["polars", "numpy"]
# ///
"""Item 14: class knockouts (colour classes, parity classes) vs matched random controls.
Input experiments/archive/2026-10-knockout-maps/results/classko.csv from tetherlab dose (age 2^24, trial 2^23, 12 seeds)."""
import numpy as np, polars as pl
raw = open("experiments/archive/2026-10-knockout-maps/results/classko.csv").read().splitlines(); hdr = raw[0].split(",")
d = pl.DataFrame([l.split(",") for l in raw if not l.startswith("rule,") and l], schema=hdr, orient="row").with_columns(spread=pl.col("spread").cast(pl.Float64), near=pl.col("near").cast(pl.Float64))
m = lambda rule, mode: d.filter((pl.col("rule") == rule) & (pl.col("mode") == mode))["spread"].to_numpy()
for rule, ctrl_par in [("RRRRRLLLLLL", "ctrl:3600"), ("RLLLLRRRRLR", "ctrl:5600")]:
    print(f"\n{rule}: real {m(rule,'real').mean():.1f}  shuffle {m(rule,'shuffle').mean():.1f}")
    print(" colour k | class spread  | matched control | ratio class/control   (mean+-sd of 12 runs)")
    ratios = []
    for k in range(11):
        a, c = m(rule, f"class:{k}"), m(rule, f"ctrlclass:{k}")
        if len(a) == 0: continue
        ratios.append(a.mean() / c.mean())
        print(f"   {k:2d}     | {a.mean():5.1f}+-{a.std(ddof=1):3.1f}  | {c.mean():5.1f}+-{c.std(ddof=1):3.1f}   | {a.mean()/c.mean():.2f}")
    print(f" class/control ratio: min {min(ratios):.2f} max {max(ratios):.2f}; classes outside [0.8, 1.2]:", [k for k, r in enumerate(ratios) if not (0.8 <= r <= 1.2)])
    p0, p1, c = m(rule, "parity:0"), m(rule, "parity:1"), m(rule, ctrl_par)
    print(f" parity 0: {p0.mean():.1f}  parity 1: {p1.mean():.1f}  control (same number of random cells): {c.mean():.1f}")
