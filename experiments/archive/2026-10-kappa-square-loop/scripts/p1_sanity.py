# /// script
# dependencies = []
# ///
"""P1 (README): on a blank board a rule with lead run k (R^k then L, or mirror) repeats a 2x2 loop for
exactly k laps (4k steps) from the first step. Pure-Python re-derivation, independent of src/.
Writes results/p1_sanity.txt. usage (repo root): uv run experiments/archive/2026-10-kappa-square-loop/scripts/p1_sanity.py"""
from pathlib import Path
import itertools, random

EXP = Path(__file__).resolve().parents[1]
DIRS = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # N, E, S, W; R = +1 (clockwise)


def run(rule, steps):
    grid, pos, h, path = {}, (0, 0), 0, []
    for _ in range(steps):
        c = grid.get(pos, 0)
        h = (h + (1 if rule[c] == "R" else -1)) % 4
        grid[pos] = (c + 1) % len(rule)
        pos = (pos[0] + DIRS[h][0], pos[1] + DIRS[h][1])
        path.append(pos)
    return path


def loop_laps(rule):
    """Number of whole 4-step laps from t=0 for which pos[t]==pos[t-4] holds without break."""
    p = [(0, 0)] + run(rule, 4 * 8 + 8)
    t = 4
    while t < len(p) and p[t] == p[t - 4]:
        t += 1
    return (t - 4) // 4 + 1  # first lap needs no repeat; each further lap is 4 repeating steps


rng = random.Random(20261016)
rows, ok = [], True
for k in range(1, 7):
    for flip in (False, True):
        for _ in range(20):
            tail = "".join(rng.choice("LR") for _ in range(8))
            lead, brk = ("R", "L") if not flip else ("L", "R")
            rule = lead * k + brk + tail
            laps = loop_laps(rule)
            good = laps == k
            ok &= good
            rows.append((rule, k, laps, good))
bad = [r for r in rows if not r[3]]
out = [f"P1: {len(rows)} rules (k=1..6, both chiralities, random 8-letter tails, seed 20261016); laps == k in {len(rows) - len(bad)}/{len(rows)}"]
out += [f"  MISMATCH {r[0]} k={r[1]} laps={r[2]}" for r in bad[:20]]
(EXP / "results/p1_sanity.txt").write_text("\n".join(out) + "\n")
print("\n".join(out))
