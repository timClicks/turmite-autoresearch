"""Knockout map: shuffle one 5x5 patch of the real territory at a time.

Pre-registered in notes/knockout-map-hypotheses.md. Needs experiments/archive/2026-10-knockout-maps/dumps/RULE.grid and
the knock example (examples/knock.rs). Run inside WSL:

  KNOCK=$HOME/turmite-target/release/examples/knock python3 -I experiments/archive/2026-10-knockout-maps/scripts/knockout.py coarse RULE
  ... refine RULE   (sliding windows around hot tiles; reads experiments/archive/2026-10-knockout-maps/knock/RULE/hot.csv)

Stages write to experiments/archive/2026-10-knockout-maps/knock/RULE/ (gitignored). The ant is deterministic, so "seeds"
are different permutations of the patch.
"""
import csv
import os
import subprocess
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2 if lib else 3]
S = 4096
C = S // 2
STEPS = 1 << 26
KNOCK = os.environ.get("KNOCK", str(ROOT / "target/release/examples/knock"))
SEEDS = (1, 2, 3)
NSWAP = 100


def grid(rule):
    return np.fromfile(ROOT / "experiments/archive/2026-10-knockout-maps/dumps" / f"{rule}.grid", dtype=np.uint8).reshape(S, S)


def run_jobs(rule, jobs, name):
    d = ROOT / "experiments/archive/2026-10-knockout-maps/knock" / rule
    d.mkdir(parents=True, exist_ok=True)
    jf, out = d / f"{name}.jobs", d / f"{name}.csv"
    jf.write_text("\n".join(",".join(map(str, j)) for j in jobs) + "\n")
    subprocess.run([KNOCK, str(ROOT / "experiments/archive/2026-10-knockout-maps/dumps" / f"{rule}.grid"), rule, str(STEPS), "jobs", str(jf), str(out)], check=True)
    return np.genfromtxt(out, delimiter=",", names=True, dtype=None, encoding=None)


def base(rule):
    d = ROOT / "experiments/archive/2026-10-knockout-maps/knock" / rule
    d.mkdir(parents=True, exist_ok=True)
    res = subprocess.run([KNOCK, str(ROOT / "experiments/archive/2026-10-knockout-maps/dumps" / f"{rule}.grid"), rule, str(STEPS), "base", str(d)],
                         capture_output=True, text=True, check=True).stdout.splitlines()
    return dict(zip(res[0].split(","), map(float, res[1].split(","))))


def tiles(rule, stride=5):
    g = grid(rule)
    ys, xs = np.nonzero(g != 255)
    x0, y0 = xs.min() - C, ys.min() - C
    x1, y1 = xs.max() - C, ys.max() - C
    vis, blank = [], []
    for y in range(y0, y1 + 1, stride):
        for x in range(x0, x1 + 1, stride):
            n = int((g[C + y:C + y + stride, C + x:C + x + stride] != 255).sum())
            (vis if n >= 5 else blank if n == 0 else []).append((x, y))
    return vis, blank


def coarse(rule):
    b = base(rule)
    vis, blank = tiles(rule)
    rng = np.random.default_rng(7)
    blank = [blank[i] for i in rng.choice(len(blank), size=min(20, len(blank)), replace=False)]
    jobs = [("patch", x, y, 5, 5, s) for (x, y) in vis for s in SEEDS]
    jobs += [("patch", x, y, 5, 5, 1) for (x, y) in blank]
    jobs += [("swap", 0, 0, 5, 5, s) for s in range(1, NSWAP + 1)]
    print(f"{rule}: baseline {b}; {len(vis)} tiles, {len(blank)} blank tiles, {NSWAP} swaps, {len(jobs)} runs", flush=True)
    run_jobs(rule, jobs, "coarse")
    (ROOT / "experiments/archive/2026-10-knockout-maps/knock" / rule / "base.csv").write_text(",".join(b) + "\n" + ",".join(map(str, b.values())) + "\n")


def refine(rule):
    """Stride-1 5x5 windows around hot tiles (+-3), then 3x3 windows around the best 5x5 ones."""
    d = ROOT / "experiments/archive/2026-10-knockout-maps/knock" / rule
    hot = np.genfromtxt(d / "hot.csv", delimiter=",", names=True)
    org = sorted({(int(h["x"]) + dx, int(h["y"]) + dy) for h in hot for dx in range(-3, 4) for dy in range(-3, 4)})
    jobs = [("patch", x, y, 5, 5, s) for (x, y) in org for s in SEEDS]
    print(f"{rule}: {len(org)} 5x5 windows, {len(jobs)} runs", flush=True)
    r5 = run_jobs(rule, jobs, "refine5")
    B = float(np.genfromtxt(d / "base.csv", delimiter=",", names=True)["near_home"])
    loss = {}
    for r in r5:
        loss.setdefault((int(r["x"]), int(r["y"])), []).append(B - float(r["near_home"]))
    top = sorted(loss, key=lambda k: -np.mean(loss[k]))[:5]
    org3 = sorted({(x + dx, y + dy) for (x, y) in top for dx in range(-1, 6) for dy in range(-1, 6)})
    jobs3 = [("patch", x, y, 3, 3, s) for (x, y) in org3 for s in SEEDS]
    jobs3 += [("swap", 0, 0, 3, 3, s) for s in range(1, 101)]
    print(f"{rule}: {len(org3)} 3x3 windows around {top}, {len(jobs3)} runs", flush=True)
    run_jobs(rule, jobs3, "refine3")


if __name__ == "__main__":
    {"coarse": coarse, "refine": refine}[sys.argv[1]](sys.argv[2])
