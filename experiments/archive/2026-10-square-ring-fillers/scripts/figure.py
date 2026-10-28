"""Figure for the square-ring fillers: (a) visit counts of RLRRRL (k = 1) after 2e5 steps from a blank board; (b) the north
edge of RRLRRRR (k = 2) after 1e6 steps with each cell's visit count printed; (c) exit-step shortfall below 2(k+1) G^2:
the committed quadratics (lines) against every observed exit (points; 1024-4096 from the late-highway board check, 8192-32768
from results/p4_board_*.csv). Deterministic (no seeds).

usage: uv run --frozen experiments/archive/2026-10-square-ring-fillers/scripts/figure.py   -> results/fig_square_ring.png
"""
import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import BoundaryNorm, ListedColormap

EXP = Path(__file__).resolve().parents[1]
ROOT = Path(__file__).resolve().parents[4]
BC = ROOT / "experiments/archive/2026-10-late-highway-board-check/results"
INK, MUTED, SURFACE = "#0b0b0b", "#52514e", "#fcfcfb"
SERIES = ["#2a78d6", "#eb6834", "#1baf7a"]


def simulate(rule, steps, size):
    n = len(rule)
    turn = [1 if t == "R" else 3 for t in rule]
    vis = [[0] * size for _ in range(size)]
    x = y = size // 2
    h = 0
    dx, dy = (0, 1, 0, -1), (-1, 0, 1, 0)
    for _ in range(steps):
        row = vis[y]
        v = row[x]
        h = (h + turn[v % n]) & 3
        row[x] = v + 1
        x += dx[h]
        y += dy[h]
    return np.array(vis), x, y


def panel_a(ax):
    vis, _, _ = simulate("RLRRRL", 200000, 400)
    ys, xs = np.nonzero(vis)
    sub = vis[ys.min() - 2: ys.max() + 3, xs.min() - 2: xs.max() + 3]
    blues = ["#fcfcfb", "#dbe8f7", "#b7d1ef", "#86b2e6", "#2a78d6", "#eb6834", "#0b0b0b"]
    cmap = ListedColormap(blues)
    norm = BoundaryNorm([-0.5, 0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 1e9], cmap.N)
    ax.imshow(sub, cmap=cmap, norm=norm, interpolation="nearest")
    ax.set_title("(a) RLRRRL (k = 1) after 2·10⁵ steps", fontsize=10, color=INK, loc="left")
    ax.set_xticks([])
    ax.set_yticks([])
    handles = [plt.Rectangle((0, 0), 1, 1, color=c, ec=MUTED, lw=0.4) for c in blues[1:]]
    ax.legend(handles, ["1", "2", "3", "4 = 2k+2", "5 (corner)", "≥ 6 (seed)"], title="visits per cell", fontsize=7,
              title_fontsize=7, loc="upper center", bbox_to_anchor=(0.5, -0.02), ncol=3, frameon=False)


def panel_b(ax):
    vis, _, _ = simulate("RRLRRRR", 1000000, 900)
    ys, xs = np.nonzero(vis)
    top = ys.min()
    cx = (xs.min() + xs.max()) // 2
    sub = vis[top - 1: top + 5, cx - 10: cx + 11]
    k = 2
    pal = {0: "#fcfcfb", k: "#dbe8f7", k + 1: "#b7d1ef", 2 * k + 1: "#86b2e6", 2 * k + 2: "#2a78d6"}
    img = np.ones(sub.shape + (3,))
    for (i, j), v in np.ndenumerate(sub):
        c = pal.get(int(v), "#eb6834")
        img[i, j] = [int(c[s: s + 2], 16) / 255 for s in (1, 3, 5)]
        ax.text(j, i, "" if v == 0 else str(v), ha="center", va="center", fontsize=7,
                color="#fcfcfb" if v == 2 * k + 2 else INK)
    ax.imshow(img, interpolation="nearest")
    ax.set_xticks(np.arange(-0.5, sub.shape[1], 1), minor=True)
    ax.set_yticks(np.arange(-0.5, sub.shape[0], 1), minor=True)
    ax.grid(which="minor", color="#ffffff", lw=1)
    ax.tick_params(which="both", length=0)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title("(b) RRLRRRR (k = 2), north edge after 10⁶ steps:\nrows k-pairs / (k+1, 2k+1)-pairs / 2k+2", fontsize=9,
                 color=INK, loc="left")


def panel_c(ax):
    pred = {r["rule"]: r for r in csv.DictReader((EXP / "results/p4_predictions.txt").read_text().splitlines()[1:])}
    obs = {}
    for g in (1024, 2048, 4096):
        for r in csv.DictReader(open(BC / f"board_{g}.csv")):
            obs.setdefault(r["rule"], {})[g] = int(r["steps"])
    for g in (8192, 16384, 32768):
        for r in csv.DictReader(open(EXP / f"results/p4_board_{g}.csv")):
            obs.setdefault(r["rule"], {})[g] = int(r["steps"])
    G = np.logspace(np.log2(800), np.log2(40000), 200, base=2)
    marks = ["o", "s", "^"]
    for i, (rule, p) in enumerate(pred.items()):
        a, b, c = (float(eval(p[v])) for v in ("alpha", "beta", "gamma"))
        ax.plot(G, 1 - (a * G * G + b * G + c) / (a * G * G), color=SERIES[i], lw=2, ls=["-", "--", ":"][i],
                label=f"{rule} (k = {i + 1}): {int(a)}G² − {-int(b)}G + {int(c)}")
        gs = sorted(obs[rule])
        e = np.array([obs[rule][g] for g in gs], dtype=float)
        gg = np.array(gs, dtype=float)
        ax.plot(gg, 1 - e / (a * gg * gg), marks[i], ms=8 - i, mfc=SERIES[i], mec=SURFACE, mew=1.5, ls="none")
    ax.legend(fontsize=7, frameon=False, loc="upper right")
    ax.set_xscale("log", base=2)
    ax.set_yscale("log")
    ax.set_xlabel("board side G", fontsize=8, color=MUTED)
    ax.set_ylabel("shortfall 1 − E / (2(k+1)G²)", fontsize=8, color=MUTED)
    ax.set_title("(c) exit step E(G): fit on 1024-4096 (lines),\nevery observed exit (points), 12/12 later exits exact", fontsize=9,
                 color=INK, loc="left")
    ax.tick_params(labelsize=7, colors=MUTED)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.grid(True, which="major", color="#e6e5e1", lw=0.6)


def main():
    fig = plt.figure(figsize=(13, 4.6), facecolor=SURFACE)
    gs = fig.add_gridspec(1, 3, width_ratios=[1.0, 1.25, 1.25], wspace=0.25)
    panel_a(fig.add_subplot(gs[0]))
    panel_b(fig.add_subplot(gs[1]))
    panel_c(fig.add_subplot(gs[2]))
    out = EXP / "results/fig_square_ring.png"
    fig.savefig(out, dpi=130, bbox_inches="tight", facecolor=SURFACE)
    print("wrote", out)


main()
