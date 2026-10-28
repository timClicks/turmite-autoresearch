# /// script
# dependencies = ["polars", "numpy"]
# ///
"""D2: 3D ants to 2^32. Input experiments/archive/2026-10-d2-three-dimensions/results/d2c_cube.csv (spec,k,area=volume,extent; k=-1 marks leaving the box). Design/decision: notes/frontier-2026-10-13-results.md.
usage: uv run experiments/archive/2026-10-d2-three-dimensions/scripts/d2_stats.py"""
import numpy as np, polars as pl
d = pl.read_csv("experiments/archive/2026-10-d2-three-dimensions/results/d2c_cube.csv")
esc = d.filter(pl.col("k") == -1)["spec"].to_list(); d = d.filter(pl.col("k") > 0)
rows = []
for (spec,), g in d.group_by("spec"):
    g = g.sort("k"); w = g.filter(pl.col("k").is_between(30, 34))
    if w.height < 5 or spec in esc: continue
    k = w["k"].to_numpy().astype(float)
    rows.append((spec, np.polyfit(k, np.log2(w["area"].to_numpy().astype(float)), 1)[0], np.polyfit(k, np.log2(w["extent"].to_numpy().astype(float)), 1)[0]))
print(f"specs {d['spec'].n_unique()}; left the 1024^3 box before 2^32: {len(set(esc))}; usable (k=30..34 complete): {len(rows)}")
if rows:
    v = np.array([r[1] for r in rows]); e = np.array([r[2] for r in rows])
    print(f"volume exponent k=30..34: median {np.median(v):.3f}, IQR {np.quantile(v,.25):.3f}-{np.quantile(v,.75):.3f}, range {v.min():.3f}-{v.max():.3f}")
    print(f"extent exponent k=30..34: median {np.median(e):.3f}, IQR {np.quantile(e,.25):.3f}-{np.quantile(e,.75):.3f}, range {e.min():.3f}-{e.max():.3f}")
    for lo, hi in ((26, 30), (28, 32)):
        vv = []
        for (spec,), g in d.group_by("spec"):
            w = g.filter(pl.col("k").is_between(lo, hi))
            if spec in esc or w.height < hi - lo + 1: continue
            vv.append(np.polyfit(w["k"].to_numpy().astype(float), np.log2(w["area"].to_numpy().astype(float)), 1)[0])
        print(f"volume exponent k={lo}..{hi}: median {np.median(vv):.3f} over {len(vv)} rules")
    print("fraction with volume exponent > 0.775:", float(np.mean(v > 0.775)), "; extent outside [0.225,0.26]:", float(np.mean((e < 0.225) | (e > 0.26))))
