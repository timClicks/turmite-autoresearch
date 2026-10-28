# /// script
# dependencies = ["polars", "numpy"]
# ///
"""Item 10 complement: cell lists inside the knockout agent's hot 5x5 tiles (read-only use of experiments/archive/2026-10-knockout-maps/knock/RULE/hot.csv, experiments/archive/2026-10-knockout-maps/dumps/RULE.grid).
Writes experiments/archive/2026-10-hot-tiles/results/hot_lists/RULE_{rare,ctrlK,all}.txt as 'x,y' (relative to home). 'rare' = rare-colour cells in the hot tiles; 'ctrlK' = the same
number of other (non-rare) visited cells drawn from the same hot tiles (K = 1..6, numpy seed 20261013); 'all' = every visited cell in the hot tiles."""
import numpy as np, polars as pl
from pathlib import Path
S = 4096; C = S // 2
Path("experiments/archive/2026-10-hot-tiles/results/hot_lists").mkdir(exist_ok=True)
rng = np.random.default_rng(20261013)
for rule, rare in [("RRRRRLLLLLL", [6, 8, 10]), ("RLLLLRRRRLR", [0, 6, 8])]:
    g = np.fromfile(f"experiments/archive/2026-10-knockout-maps/dumps/{rule}.grid", dtype=np.uint8).reshape(S, S)
    hot = pl.read_csv(f"experiments/archive/2026-10-knockout-maps/knock/{rule}/hot.csv")
    cells = []
    for x, y in zip(hot["x"], hot["y"]):
        for dy in range(5):
            for dx in range(5):
                v = g[C + y + dy, C + x + dx]
                if v != 255: cells.append((x + dx, y + dy, int(v)))
    r = [(x, y) for x, y, v in cells if v in rare]; o = [(x, y) for x, y, v in cells if v not in rare]
    w = lambda name, L: Path(f"experiments/archive/2026-10-hot-tiles/results/hot_lists/{rule}_{name}.txt").write_text("\n".join(f"{x},{y}" for x, y in L) + "\n")
    w("rare", r); w("all", [(x, y) for x, y, _ in cells])
    for k in range(1, 7):
        idx = rng.choice(len(o), len(r), replace=False); w(f"ctrl{k}", [o[i] for i in idx])
    print(rule, "hot tiles", hot.height, "visited cells in them", len(cells), "rare cells", len(r), "other cells", len(o))
