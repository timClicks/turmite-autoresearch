"""Pattern-matched fields: does a hard tethered rule form a home?

For each rule and level, make a field with the same colour counts as the
rule's final territory (experiments/archive/2026-10-knockout-maps/dumps/RULE.grid, 2^24 steps) and drop a fresh ant at
home for 2^26 steps, exactly as the published shuffle test did.

Levels
  shuffle, radial, pairs, b2, b3   via examples/synth (see notes/pattern-fields-hypotheses.md)
  keep_rand_F   a random fraction F of visited cells keep their original colour,
                the rest are shuffled among themselves
  keep_disc_R   cells within R of the territory centre keep their colour, the
                rest are shuffled among themselves
  keep_out_R    the reverse: cells beyond R keep their colour, the core is shuffled
  blank_R       a shuffled field with every cell within R of the centre set to 0
                (fresh ground), to test whether a hard rule nucleates on blank

Outcomes, over the last quarter of the run: own (share of time within 10 cells
of the previous block's mean; >= 0.25 counts as tethered, as published) and
spread (RMS distance from the block's mean position, in cells).

With REUSE=1 in the environment, existing grids in synth/ are re-measured
rather than regenerated (their synthesis columns are left empty).

usage: python3 -I experiments/archive/2026-10-patterns-fields/scripts/patterns.py OUT.csv
"""
import csv
import os
import subprocess
import sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[4]
SYN = ROOT / "experiments/archive/2026-10-patterns-fields/synth"
S = 4096
STEPS = 1 << 26
SWEEPS = {"pairs": 1000, "b2": 5000, "b3": 3000}
HARD = ["RRRRRLLLLLL", "RLLLLRRRRLR"]
EASY = ["RRRLLRLLR", "RLLRRRRRLRLR", "RRRLLLLRRRLL"]
SEEDS = (1, 2, 3)


def centre(rule):
    p = np.fromfile(ROOT / "experiments/archive/2026-10-knockout-maps/dumps" / f"{rule}.traj", dtype="<i2").reshape(-1, 2).astype(float)
    return p.mean(axis=0)


def keep_field(rule, kind, param, seed, out):
    g = np.fromfile(ROOT / "experiments/archive/2026-10-knockout-maps/dumps" / f"{rule}.grid", dtype=np.uint8).reshape(S, S)
    vis = g != 255
    rng = np.random.default_rng(seed * 1000 + 17)
    if kind == "rand":
        keep = vis & (rng.random(g.shape) < param)
    else:
        cx, cy = centre(rule)
        yy, xx = np.mgrid[0:S, 0:S]
        r = np.hypot(xx - S // 2 - cx, yy - S // 2 - cy)
        keep = vis & ((r <= param) if kind == "disc" else (r > param))
    free = vis & ~keep
    f = g.copy()
    f[free] = rng.permutation(g[free])
    f.tofile(out)
    same = float((f[vis] == g[vis]).mean())
    return {"windows": 0, "distinct": 0, "cost0": 0, "cost": 0, "same_place": same}


def blank_field(rule, radius, seed, out):
    g = np.fromfile(ROOT / "experiments/archive/2026-10-knockout-maps/dumps" / f"{rule}.grid", dtype=np.uint8).reshape(S, S)
    vis = g != 255
    rng = np.random.default_rng(seed * 1000 + 29)
    f = g.copy()
    f[vis] = rng.permutation(g[vis])
    cx, cy = centre(rule)
    yy, xx = np.mgrid[0:S, 0:S]
    f[vis & (np.hypot(xx - S // 2 - cx, yy - S // 2 - cy) <= radius)] = 0
    f.tofile(out)
    return {"windows": 0, "distinct": 0, "cost0": 0, "cost": 0, "same_place": float((f[vis] == g[vis]).mean())}


EMPTY = {"windows": None, "distinct": None, "cost0": None, "cost": None, "same_place": None}


def make(rule, level, seed):
    out = SYN / f"{rule}_{level}_{seed}.grid"
    if level == "real":
        return ROOT / "experiments/archive/2026-10-knockout-maps/dumps" / f"{rule}.grid", {**EMPTY, "same_place": 1.0}
    if os.environ.get("REUSE") == "1" and out.exists():
        return out, dict(EMPTY)
    if level.startswith("blank_"):
        return out, blank_field(rule, float(level.split("_")[1]), seed, out)
    if level.startswith("keep_"):
        _, kind, param = level.split("_")
        return out, keep_field(rule, kind, float(param), seed, out)
    cmd = [str(ROOT / "target/release/examples/synth"), str(ROOT / "experiments/archive/2026-10-knockout-maps/dumps" / f"{rule}.grid"), str(len(rule)),
           level, str(seed), str(SWEEPS.get(level, 0)), str(out)]
    if level == "radial":
        cx, cy = centre(rule)
        cmd += [f"{cx:.2f}", f"{cy:.2f}"]
    line = subprocess.run(cmd, capture_output=True, text=True, check=True, env={"SYNTH_T0": "1.5"}).stdout.strip()
    _, _, w, d, c0, c, same = line.split(",")
    return out, {"windows": int(w), "distinct": int(d), "cost0": int(c0), "cost": int(c), "same_place": float(same)}


def transplant(rule, grid, seed):
    res = subprocess.run([str(ROOT / "target/release/examples/transplant"), str(grid), rule, "real", "0", "0",
                          str(STEPS), str(seed)], capture_output=True, text=True)
    if "left the board" in res.stderr:
        return {"own": None, "spread": None, "home": None, "first_own": None, "mx": None, "my": None, "t_tether": None}
    rows = list(csv.DictReader(res.stdout.splitlines()))
    last = rows[-16:]
    own = np.mean([float(r["near_prev"]) for r in last])
    # first block from which the ant stays tethered (own >= 0.25) to the end
    t_tether = None
    for k in range(len(rows)):
        if all(float(r["near_prev"]) >= 0.25 for r in rows[k:]):
            t_tether = int(rows[k]["t"])
            break
    spread = np.mean([float(r["spread"]) for r in last])
    return {"own": round(float(own), 3), "spread": round(float(spread), 2), "home": round(float(np.mean([float(r["near_home"]) for r in last])), 3),
            "first_own": round(float(np.mean([float(r["near_prev"]) for r in rows[:4]])), 3),
            "mx": round(float(np.mean([float(r["mean_x"]) for r in last])), 1),
            "my": round(float(np.mean([float(r["mean_y"]) for r in last])), 1), "t_tether": t_tether}


def job(args):
    rule, level, seed = args
    grid, info = make(rule, level, seed)
    tp = transplant(rule, grid, 1)
    row = {"rule": rule, "hard": rule in HARD, "level": level, "seed": seed, **info, **tp}
    print(row, flush=True)
    return row


if __name__ == "__main__":
    SYN.mkdir(exist_ok=True)
    levels = sys.argv[2].split(",") if len(sys.argv) > 2 else [
        "shuffle", "radial", "pairs", "b2", "b3",
        "keep_rand_0.25", "keep_rand_0.5", "keep_rand_0.75", "keep_disc_5", "keep_disc_10", "keep_disc_20"]
    rules = sys.argv[3].split(",") if len(sys.argv) > 3 else HARD + EASY
    jobs = [(r, lv, s) for lv in levels for r in rules for s in SEEDS]
    # longest first so the two workers finish together
    jobs.sort(key=lambda j: -SWEEPS.get(j[1], 0) * (3 if j[1] == "b3" else 1))
    with Pool(2) as pool:
        rows = pool.map(job, jobs, chunksize=1)
    out = Path(sys.argv[1])
    write_header = not out.exists()
    with out.open("a", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        if write_header:
            w.writeheader()
        w.writerows(rows)
