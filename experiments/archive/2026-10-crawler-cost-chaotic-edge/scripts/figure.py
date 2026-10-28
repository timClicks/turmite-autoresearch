"""Figure: (a) boundary reads per birth 1/c against the lead m, with the chaotic lead law, the crawler line m + 5/4, census Pi
blobs, their composition-matched controls and the kept fresh Pi rules of Stage 2; (b) median relative flip effect e by relative
position q = p - m for leads 1-3 (P2), with each lead's registered window q in [1, m+1] marked. Reads committed results only.

usage: uv run --frozen experiments/archive/2026-10-crawler-cost-chaotic-edge/scripts/figure.py   -> results/fig_crawler_ceiling.png
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import polars as pl

RES = Path(__file__).resolve().parents[1] / "results"
INK, MUTED, GRID, SURFACE = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"
SERIES = ["#2a78d6", "#eb6834", "#1baf7a"]
MARKERS = ["o", "s", "^"]

p1 = pl.read_csv(RES / "p1p3_rules.csv")
s2 = pl.read_csv(RES / "stage2_rules.csv").filter(pl.col("status") == "kept")
eff = pl.read_csv(RES / "p2_effects.csv").filter(pl.col("kept"))

plt.rcParams.update({"font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": MUTED,
                     "ytick.color": MUTED, "axes.spines.top": False, "axes.spines.right": False})
fig, (a, b) = plt.subplots(1, 2, figsize=(10, 4.2), facecolor=SURFACE)
for ax in (a, b):
    ax.set_facecolor(SURFACE)
    ax.grid(color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)

m = np.linspace(1.5, 9.5, 50)
a.plot(m, m + 1.25, color=INK, linewidth=2, label="crawler line m + 5/4 (exact)")
a.plot(m, 1.363 + 0.696 * m, color=MUTED, linewidth=2, linestyle="--", label="chaotic lead law 1.36 + 0.70 m")
rng = np.random.default_rng(0)  # horizontal jitter only, for visibility
groups = [(p1.filter(pl.col("role") == "pi"), "inv_c_census", "census blobs with crawler table (n = 40)"),
          (p1.filter(pl.col("role").str.starts_with("ctrl")), "inv_c_census", "composition-matched controls (73 draws)"),
          (s2, "inv_c", "fresh crawler-table rules, n 13-18 (89 kept)")]
for (g, col, lab), c, mk, dx in zip(groups, SERIES, MARKERS, (-0.18, 0.0, 0.18)):
    x = g["m"].to_numpy() + dx + rng.uniform(-0.05, 0.05, g.height)
    a.scatter(x, g[col].to_numpy(), s=22, color=c, marker=mk, edgecolor=SURFACE, linewidth=0.8, label=lab, zorder=3)
a.set_xlabel("lead m (opening same-letter run)")
a.set_ylabel("boundary reads per birth, 1/c")
a.set_title("(a) The crawler line as a ceiling", loc="left", color=INK, fontsize=10)
a.legend(frameon=False, fontsize=7.5, loc="upper left")

for mm, c, mk in zip((1, 2, 3), SERIES, MARKERS):
    g = eff.filter(pl.col("m") == mm).group_by("q").agg(pl.col("e").median()).sort("q").filter(pl.col("q") <= 9)
    b.plot(g["q"], g["e"], color=c, marker=mk, markersize=6, linewidth=2, label=f"lead m = {mm} (window q = 1..{mm + 1})")
    y0 = -0.012 - 0.012 * (mm - 1)
    b.plot([1, mm + 1], [y0, y0], color=c, linewidth=4, solid_capstyle="round")
    b.text(mm + 1.25, y0, f"window, m = {mm}", color=MUTED, fontsize=7, va="center")
b.set_xlabel("relative position of the flipped letter, q = p - m")
b.set_ylabel("median relative change in 1/c")
b.set_title("(b) Near letters matter; the window does not move with m", loc="left", color=INK, fontsize=10)
b.axhline(0, color=MUTED, linewidth=0.8)
b.legend(frameon=False, fontsize=7.5, loc="upper right")
fig.tight_layout()
fig.savefig(RES / "fig_crawler_ceiling.png", dpi=160, facecolor=SURFACE)
