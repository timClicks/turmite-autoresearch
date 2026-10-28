# /// script
# dependencies = ["numpy"]
# ///
"""E1: knockout coarse map on an arbitrary grid file (same protocol as knockout.py coarse: every 5x5 tile with >= 5 visited cells,
3 permutations; 20 blank tiles; 100 swaps of 25 cells; 2^26 steps). usage: uv run experiments/archive/2026-10-e1-one-sided-hot-region/scripts/e1_map.py TAG GRIDFILE RULE
Outputs experiments/archive/2026-10-e1-one-sided-hot-region/knock_e1/TAG/{base.csv,coarse.jobs,coarse.csv}. Needs the knock example built in ~/turmite-target-frontier4 (or KNOCK env)."""
import os, subprocess, sys
from pathlib import Path
import numpy as np
S, C = 4096, 2048
tag, gridfile, rule = sys.argv[1:4]
KNOCK = os.environ.get("KNOCK", os.path.expanduser("~/turmite-target-frontier4/release/examples/knock"))
out = Path("experiments/archive/2026-10-e1-one-sided-hot-region/knock_e1") / tag; out.mkdir(parents=True, exist_ok=True)
g = np.fromfile(gridfile, dtype=np.uint8).reshape(S, S)
ys, xs = np.nonzero(g != 255)
x0, y0, x1, y1 = xs.min() - C, ys.min() - C, xs.max() - C, ys.max() - C
vis, blank = [], []
for y in range(y0, y1 + 1, 5):
    for x in range(x0, x1 + 1, 5):
        n = int((g[C + y:C + y + 5, C + x:C + x + 5] != 255).sum())
        (vis if n >= 5 else blank if n == 0 else []).append((x, y))
rng = np.random.default_rng(7)
blank = [blank[i] for i in rng.choice(len(blank), size=min(20, len(blank)), replace=False)]
jobs = [("patch", x, y, 5, 5, s) for (x, y) in vis for s in (1, 2, 3)] + [("patch", x, y, 5, 5, 1) for (x, y) in blank] + [("swap", 0, 0, 5, 5, s) for s in range(1, 101)]
(out / "coarse.jobs").write_text("\n".join(",".join(map(str, j)) for j in jobs) + "\n")
b = subprocess.run([KNOCK, gridfile, rule, str(1 << 26), "base", str(out)], capture_output=True, text=True, check=True).stdout.splitlines()
(out / "base.csv").write_text(b[0] + "\n" + b[1] + "\n")
print(tag, "tiles", len(vis), "jobs", len(jobs), "base", b[1], flush=True)
subprocess.run([KNOCK, gridfile, rule, str(1 << 26), "jobs", str(out / "coarse.jobs"), str(out / "coarse.csv")], check=True)
(out / "done").write_text("ok")
