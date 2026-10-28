# /// script
# dependencies = []
# ///
"""A6 mechanism: job list for knock `strat` jobs. Per rule: 60 draws x class {0,1} x occupancy quartile {0..3}, 25 cells each. Writes experiments/archive/2026-10-knockout-maps/knock/RULE/a6.jobs."""
for rule in ("RRRRRLLLLLL", "RLLLLRRRRLR"):
    open(f"experiments/archive/2026-10-knockout-maps/knock/{rule}/a6.jobs", "w").write("\n".join(f"strat,{c},{q},5,5,{s}" for c in (0, 1) for q in range(4) for s in range(1, 61)) + "\n")
