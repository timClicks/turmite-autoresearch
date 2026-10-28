# /// script
# dependencies = []
# ///
"""E3b job lists: strat2 jobs, 60 draws x class {0,1} x route quartile {0..3}, 25 cells each. Writes experiments/archive/2026-10-knockout-maps/knock/RULE/e3b.jobs."""
for rule in ("RRRRRLLLLLL", "RLLLLRRRRLR"):
    open(f"experiments/archive/2026-10-knockout-maps/knock/{rule}/e3b.jobs", "w").write("\n".join(f"strat2,{c},{q},5,5,{s}" for c in (0, 1) for q in range(4) for s in range(1, 61)) + "\n")
