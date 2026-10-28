# /// script
# dependencies = []
# ///
"""E6 job lists: hot tiles of the 2^24 map (experiments/archive/2026-10-knockout-maps/knock/RULE/hot.csv) x fresh permutation seeds 11,12,13, plus 100 swaps (seeds 101..200). Writes experiments/archive/2026-10-knockout-maps/knock/RULE/e6.jobs."""
import csv
for rule in ("RRRRRLLLLLL", "RLLLLRRRRLR"):
    hot = [(int(float(r["x"])), int(float(r["y"]))) for r in csv.DictReader(open(f"experiments/archive/2026-10-knockout-maps/knock/{rule}/hot.csv"))]
    jobs = [f"patch,{x},{y},5,5,{s}" for x, y in hot for s in (11, 12, 13)] + [f"swap,0,0,5,5,{s}" for s in range(101, 201)]
    open(f"experiments/archive/2026-10-knockout-maps/knock/{rule}/e6.jobs", "w").write("\n".join(jobs) + "\n"); print(rule, len(hot), "hot tiles,", len(jobs), "jobs")
