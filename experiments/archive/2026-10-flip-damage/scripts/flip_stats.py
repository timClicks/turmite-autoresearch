# /// script
# dependencies = ["polars", "numpy"]
# ///
"""Item 11: single/multi-cell flips on the running state (hard rules, age 2^24, 3.4e7 steps continuation, 16 perturbations per setting)."""
import numpy as np, polars as pl
cols = ["nflip", "rule", "pert", "flip_dist", "first_contact", "dmg_1e4", "dmg_1e5", "dmg_1e6", "spread_pert", "spread_base", "ok"]
d = pl.read_csv("experiments/archive/2026-10-flip-damage/results/flip_all.csv", has_header=False, new_columns=cols, null_values=["none"], infer_schema_length=500)
area = {"RRRRRLLLLLL": 7264, "RLLLLRRRRLR": 11144}
for rule in area:
    print(f"\n{rule} (area {area[rule]}):  base spread {d.filter(pl.col('rule')==rule)['spread_base'].mean():.1f}")
    print(" nflip | perturbed runs | lost tether (spread>=25) | spread_pert median [min,max] | contact: none / median steps | damage (cells) median at lag 1e4 / 1e5 / 1e6 | share >=30% area at 1e6")
    for nf in (1, 10, 100, 700):
        g = d.filter((pl.col("rule") == rule) & (pl.col("nflip") == nf))
        sp = g["spread_pert"].to_numpy(); lost = (sp >= 25).sum()
        fc = g["first_contact"]
        dm = [g[c].drop_nulls().drop_nans().to_numpy() for c in ("dmg_1e4", "dmg_1e5", "dmg_1e6")]
        big = (dm[2] >= 0.3 * area[rule]).mean() if len(dm[2]) else float("nan")
        print(f"  {nf:4d} | {g.height:3d} | {lost:2d}/{g.height} | {np.median(sp):5.1f} [{sp.min():.1f},{sp.max():.1f}] | {fc.is_null().sum()} / {fc.drop_nulls().median() if fc.drop_nulls().len() else float('nan'):.0f} | " +
              " / ".join(f"{np.median(x):.0f}(n={len(x)})" if len(x) else "-" for x in dm) + f" | {big:.2f}")
