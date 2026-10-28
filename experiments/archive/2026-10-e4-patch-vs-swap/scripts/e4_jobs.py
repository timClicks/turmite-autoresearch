# /// script
# dependencies = []
# ///
"""E4 job lists. Per rule: (a) the stored coarse jobs (5x5 patch x3 permutations, blanks, 100 swaps of 25 cells) verbatim,
(b) swaps of 50, 100, 200, 400 cells (5x10, 10x10, 10x20, 20x20), seeds 1..100, (c) 10x10 patches at the corner of
every seed-1 5x5 patch job, seeds 1..2. Writes experiments/archive/2026-10-knockout-maps/knock/RULE/e4.jobs. usage: uv run experiments/archive/2026-10-e4-patch-vs-swap/scripts/e4_jobs.py"""
for rule in ("RRRRRLLLLLL", "RLLLLRRRRLR"):
    base = [l.strip() for l in open(f"experiments/archive/2026-10-knockout-maps/knock/{rule}/coarse.jobs") if l.strip()]
    jobs = list(base)
    for w, h in ((5, 10), (10, 10), (10, 20), (20, 20)):
        jobs += [f"swap,0,0,{w},{h},{s}" for s in range(1, 101)]
    for l in base:
        k, x, y, w, h, s = l.split(",")
        if k == "patch" and s == "1" and w == "5":
            jobs += [f"patch,{x},{y},10,10,{t}" for t in (1, 2)]
    open(f"experiments/archive/2026-10-knockout-maps/knock/{rule}/e4.jobs", "w").write("\n".join(jobs) + "\n")
    print(rule, len(jobs), "jobs")
