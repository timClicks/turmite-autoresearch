# /// script
# dependencies = ["polars", "numpy"]
# ///
"""Item 10 complement: recolouring only the rare-colour cells inside the knockout hot tiles vs the same number of other cells in the same tiles."""
import numpy as np, polars as pl
raw = open("experiments/archive/2026-10-hot-tiles/results/hot_recolour.csv").read().splitlines(); hdr = raw[0].split(",")
d = pl.DataFrame([l.split(",") for l in raw if not l.startswith("rule,") and l], schema=hdr, orient="row").with_columns(spread=pl.col("spread").cast(pl.Float64), near=pl.col("near").cast(pl.Float64))
for rule in ["RRRRRLLLLLL", "RLLLLRRRRLR"]:
    g = d.filter(pl.col("rule") == rule)
    def m(tag): 
        v = g.filter(pl.col("mode").str.ends_with(tag))["spread"].to_numpy(); return v
    real = g.filter(pl.col("mode") == "real")["spread"].mean()
    rare, allc = m(f"{rule}_rare.txt"), m(f"{rule}_all.txt")
    ctrl = [m(f"{rule}_ctrl{k}.txt").mean() for k in range(1, 7)]
    nrare = {"RRRRRLLLLLL": 47, "RLLLLRRRRLR": 62}[rule]
    print(f"{rule}: intact {real:.2f}")
    print(f"  recolour the {nrare} rare-colour cells inside the hot tiles: spread {rare.mean():.2f} +- {rare.std(ddof=1):.2f}  (12 recolourings)")
    print(f"  recolour {nrare} other cells from the same hot tiles (6 different draws, 12 recolourings each): {np.round(ctrl, 2).tolist()}  mean {np.mean(ctrl):.2f}")
    print(f"  recolour ALL visited cells in the hot tiles: {allc.mean():.2f} +- {allc.std(ddof=1):.2f}")
    print(f"  rare effect = {rare.mean() - real:+.2f}, control effect = {np.mean(ctrl) - real:+.2f}, whole tiles {allc.mean() - real:+.2f}")
