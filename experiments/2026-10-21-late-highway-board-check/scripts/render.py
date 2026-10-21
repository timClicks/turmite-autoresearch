"""Render board fillers next to genuine highways, on two board sizes.

    uv run experiments/2026-10-21-late-highway-board-check/scripts/render.py [--ray]

Rows: the filler RLRRRRL (k = 1 of the R^k L R R... series) on 1024 and 2048 boards, then the genuine highway
RRRLLLRRRR (census onset 4,146,461, almost the filler's onset on 1024) on the same two boards. A filler's escape time
grows with the board area and its footprint is the whole board; a genuine highway escapes from a central blob along
one arm, starting at the same step on both boards. `--ray` adds RLLLRLRRR on the census 32768 board (5.7e9 steps, a few
minutes, 1 GB): the "highway" that is a ray inside its own territory (README part 1).

Snapshots come from examples/late_highway_board_check_render.rs (deterministic, no seeds); intermediate .bin files go
to scratch/render/, the figure to results/fillers_vs_highways.png.
"""
import os
import subprocess
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import polars as pl
from matplotlib.colors import ListedColormap

ROOT = Path(__file__).resolve().parents[3]
EXP = Path(__file__).resolve().parents[1]
SCRATCH = EXP / "scratch" / "render"
OUT = EXP / "results" / "fillers_vs_highways.png"
# Cargo builds into CARGO_TARGET_DIR when it is set (relative paths resolve against the build's working directory, ROOT).
TARGET = ROOT / os.environ.get("CARGO_TARGET_DIR", "target")
BIN = TARGET / "release/examples/late_highway_board_check_render"
FINAL = 10**12  # "run until the ant leaves the board"

# (label, rule, board, snapshot steps); the last snapshot is the escape.
CASES = [
    ("Board filler RLRRRRL, 1024 board", "RLRRRRL", 1024, [1_000_000, 2_500_000, 4_000_000, FINAL]),
    ("Same filler, 2048 board", "RLRRRRL", 2048, [1_000_000, 4_141_534, 12_000_000, FINAL]),
    ("Genuine highway RRRLLLRRRR, 1024 board", "RRRLLLRRRR", 1024, [1_000_000, 2_500_000, 4_146_461, FINAL]),
    ("Same highway, 2048 board", "RRRLLLRRRR", 2048, [1_000_000, 2_500_000, 4_146_461, FINAL]),
]
if "--ray" in sys.argv:
    CASES.append(("Ray artefact RLLLRLRRR, 32768 board", "RLLLRLRRR", 32768, [1_000_000_000, 4_000_000_000, 5_723_529_364, FINAL]))

PAPER = "#f4f1ea"


def snapshots(rule: str, board: int, steps: list[int]) -> list[tuple[dict, np.ndarray]]:
    stem = SCRATCH / f"{rule}_{board}"
    csv = Path(f"{stem}.csv")
    if not csv.exists():
        subprocess.run([str(BIN), rule, str(board), str(stem), *map(str, steps)], check=True)
    rows = pl.read_csv(csv).to_dicts()
    w = min(board, 1024)
    return [(r, np.fromfile(f"{stem}_{r['t']}.bin", dtype=np.uint8).reshape(w, w)) for r in rows]


def colourmap(n: int) -> ListedColormap:
    # 0 = never visited; colours 0..n-1 shifted by one, drawn from a perceptual map.
    return ListedColormap([PAPER, *plt.get_cmap("viridis")(np.linspace(0.05, 0.95, n))])


def main() -> None:
    SCRATCH.mkdir(parents=True, exist_ok=True)
    subprocess.run(["cargo", "build", "--release", "--example", "late_highway_board_check_render"], cwd=ROOT, check=True)
    ncol = max(len(c[3]) for c in CASES)
    fig, axes = plt.subplots(len(CASES), ncol, figsize=(3.0 * ncol, 3.25 * len(CASES)), squeeze=False)
    fig.patch.set_facecolor("white")
    for row, (label, rule, board, steps) in zip(axes, CASES):
        snaps = snapshots(rule, board, steps)
        cmap = colourmap(len(rule))
        for k, ax in enumerate(row):
            ax.set_xticks([])
            ax.set_yticks([])
            if k >= len(snaps):
                ax.axis("off")
                continue
            r, img = snaps[k]
            ax.imshow(img, cmap=cmap, vmin=0, vmax=len(rule), interpolation="nearest")
            for s in ax.spines.values():
                s.set_color("#333333")
                s.set_linewidth(1.2)
            w = img.shape[0]
            scale = w / board
            # After an escape the ant stands one cell outside the board: clamp the marker to the edge.
            px = np.clip((r["x"] + board // 2) * scale, 0, w - 1)
            py = np.clip((r["y"] + board // 2) * scale, 0, w - 1)
            ax.plot(px, py, marker="o", ms=5, mfc="#d1495b", mec="white", mew=0.8, clip_on=False)
            ax.set_xlim(-0.5, w - 0.5)
            ax.set_ylim(w - 0.5, -0.5)
            frac = r["visited"] / board**2
            state = "left the board" if r["left_board"] else f"t = {r['t']:.3g}"
            ax.set_title(f"{state}\nvisited {frac:.1%} of board" + (f", t = {r['t']:.4g}" if r["left_board"] else ""), fontsize=8.5)
            if k == 0:
                ax.set_ylabel(label, fontsize=9, labelpad=8)
    fig.suptitle(
        "Board fillers vs genuine highways: a filler escapes only after covering the board (escape time grows with board area);\n"
        "a genuine highway starts at the same step on every board and leaves a central blob along one arm (escaping later on\n"
        "a bigger board only by the arm's extra length).  Red dot: the ant.",
        fontsize=10,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig(OUT, dpi=110)
    print(f"wrote {OUT.relative_to(ROOT)}")
    for _, rule, board, _ in CASES:
        last = pl.read_csv(SCRATCH / f"{rule}_{board}.csv").tail(1).to_dicts()[0]
        print(f"{rule:>11} on {board:>5}: last snapshot t = {last['t']}, left board {last['left_board']}, visited {last['visited'] / board**2:.1%}")


if __name__ == "__main__":
    main()
