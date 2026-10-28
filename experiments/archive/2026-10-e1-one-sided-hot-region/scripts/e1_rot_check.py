# /// script
# dependencies = ["numpy", "polars"]
# ///
"""E1 covariance check: the 11 hot 5x5 tiles of RRRRRLLLLLL (top-left (x,y)) become, in the field rotated 90 degrees clockwise ((x,y)->(-y,x)), the 5x5 tiles with top-left (-(y+4), x).
Run them there (START_H=1, fresh permutation seeds 11,12,13, same as e6) and compare the mean loss per tile with the original-field value (experiments/archive/2026-10-knockout-maps/knock/RULE/e6_k24.csv).
usage: uv run experiments/archive/2026-10-e1-one-sided-hot-region/scripts/e1_rot_check.py"""
import csv, os, subprocess, numpy as np, polars as pl
R = "RRRRRLLLLLL"
hot = [(int(float(r["x"])), int(float(r["y"]))) for r in csv.DictReader(open(f"experiments/archive/2026-10-knockout-maps/knock/{R}/hot.csv"))]
jobs = [f"patch,{-(y + 4)},{x},5,5,{s}" for x, y in hot for s in (11, 12, 13)] + [f"swap,0,0,5,5,{s}" for s in range(101, 201)]
os.makedirs("experiments/archive/2026-10-e1-one-sided-hot-region/knock_e1/rotcheck", exist_ok=True); open("experiments/archive/2026-10-e1-one-sided-hot-region/knock_e1/rotcheck/jobs.txt", "w").write("\n".join(jobs) + "\n")
K = os.path.expanduser("~/turmite-target-frontier4/release/examples/knock")
env = dict(os.environ, START_H="1")
subprocess.run([K, f"experiments/archive/2026-10-e1-one-sided-hot-region/dumps_e1/{R}_rot90.grid", R, str(1 << 26), "jobs", "experiments/archive/2026-10-e1-one-sided-hot-region/knock_e1/rotcheck/jobs.txt", "experiments/archive/2026-10-e1-one-sided-hot-region/knock_e1/rotcheck/rot.csv"], check=True, env=env)
B = 0.4737
rot = pl.read_csv("experiments/archive/2026-10-e1-one-sided-hot-region/knock_e1/rotcheck/rot.csv").filter(pl.col("ok") == 1).with_columns(loss=B - pl.col("near_home"))
org = pl.read_csv(f"experiments/archive/2026-10-knockout-maps/knock/{R}/e6_k24.csv").filter(pl.col("ok") == 1).with_columns(loss=B - pl.col("near_home"))
a = [org.filter((pl.col("kind") == "patch") & (pl.col("x") == x) & (pl.col("y") == y))["loss"].mean() for x, y in hot]
b = [rot.filter((pl.col("kind") == "patch") & (pl.col("x") == -(y + 4)) & (pl.col("y") == x))["loss"].mean() for x, y in hot]
print("tile (x,y): original mean loss vs rotated-field mean loss (3 fresh permutations each)")
for (x, y), u, v in zip(hot, a, b): print(f"  ({x:3d},{y:3d}): {u:+.4f} vs {v:+.4f}")
sw_o = org.filter(pl.col("kind") == "swap")["loss"].to_numpy(); sw_r = rot.filter(pl.col("kind") == "swap")["loss"].to_numpy()
print(f"mean over the 11 tiles: original {np.mean(a):.4f}, rotated {np.mean(b):.4f}; Spearman across tiles {np.corrcoef(np.argsort(np.argsort(a)), np.argsort(np.argsort(b)))[0,1]:.2f}")
print(f"swap null 95th percentile: original {np.quantile(sw_o, .95):.4f}, rotated {np.quantile(sw_r, .95):.4f}")
