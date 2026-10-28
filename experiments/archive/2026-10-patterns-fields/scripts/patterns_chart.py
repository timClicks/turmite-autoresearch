"""Chart: how tightly a hard tethered ant is held, against how much of its
original field is back in place. Writes notes/pattern-fields.png."""
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[4]
rows = json.loads((ROOT / "experiments/archive/2026-10-patterns-fields/results/patterns_summary.json").read_text())
BLUE, ORANGE, AQUA, GREY, INK, MUTED = "#2a78d6", "#eb6834", "#1baf7a", "#8a8980", "#1f1e1c", "#6b6a63"
plt.rcParams.update({"font.size": 10, "axes.edgecolor": "#d6d5ce", "axes.labelcolor": INK, "xtick.color": MUTED,
                     "ytick.color": MUTED, "font.family": "DejaVu Sans"})
OFFS = {("RRRRRLLLLLL", "radial"): (-10, 22), ("RRRRRLLLLLL", "pairs"): (30, -6), ("RRRRRLLLLLL", "b2"): (18, -26),
        ("RLLLLRRRRLR", "radial"): (-44, 2), ("RLLLLRRRRLR", "pairs"): (-36, -16), ("RLLLLRRRRLR", "b2"): (-6, -26)}
fig, axes = plt.subplots(1, 2, figsize=(11, 4.6), sharey=True)
for ax, rule in zip(axes, ["RRRRRLLLLLL", "RLLLLRRRRLR"]):
    d = {r["level"]: r for r in rows if r["rule"] == rule}
    keep = ["shuffle"] + [f"keep_rand_{f}" for f in ("0.25", "0.5", "0.75", "0.9", "0.97", "0.99")] + ["real"]
    ax.plot([d[k]["same"] for k in keep], [d[k]["spread"] for k in keep], "-o", color=BLUE, lw=2, ms=6,
            label="random cells kept in place, rest shuffled", zorder=3)
    for k in ("keep_disc_20", "keep_disc_30", "keep_disc_40", "keep_out_10", "keep_out_20", "keep_out_30"):
        ax.plot(d[k]["same"], d[k]["spread"], "s", color=ORANGE, ms=7, mec="white", mew=1.5, zorder=4,
                label="central disc or outer rim kept" if k == "keep_disc_20" else None)
        lab = ("r≤" if "disc" in k else "r>") + k.split("_")[-1]
        ax.annotate(lab, (d[k]["same"], d[k]["spread"]), xytext=(-30, -14) if k == "keep_out_20" else (6, 4), textcoords="offset points", fontsize=8, color=MUTED)
    for k, lab in (("pairs", "pairs"), ("b2", "2×2"), ("b3", "3×3"), ("radial", "radial")):
        ax.plot(d[k]["same"], d[k]["spread"], "D", color=AQUA if k != "radial" else GREY, ms=7, mec="white", mew=1.5,
                zorder=5, label="pattern-matched field" if k == "pairs" else ("radial shuffle" if k == "radial" else None))
        off = OFFS.get((rule, k), (6, -11))
        ax.annotate(lab, (d[k]["same"], d[k]["spread"]), xytext=off, textcoords="offset points", fontsize=8.5, color=INK,
                    arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.6) if abs(off[1]) > 12 else None)
    ax.annotate("real field", (1, d["real"]["spread"]), xytext=(-52, -14), textcoords="offset points", fontsize=8.5, color=INK)
    ax.annotate("shuffled", (d["shuffle"]["same"], d["shuffle"]["spread"]), xytext=(6, 6), textcoords="offset points", fontsize=8.5, color=INK)
    ax.set_title(rule, family="monospace", fontsize=11, color=INK, loc="left")
    ax.set_xlabel("share of territory cells with their original colour, in place")
    ax.set_xlim(0, 1.05)
    ax.grid(color="#ecebe6", lw=0.8)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
axes[0].set_ylabel("ant's spread, cells (RMS distance from its mean)")
axes[0].set_ylim(10, 50)
h, l = axes[0].get_legend_handles_labels()
fig.legend(h, l, loc="lower center", ncol=4, frameon=False, fontsize=9)
fig.suptitle("A hard tethered ant is held by its exact field, not by local pattern statistics", x=0.06, ha="left",
             fontsize=12, color=INK)
fig.tight_layout(rect=(0, 0.08, 1, 0.95))
fig.savefig(ROOT / "notes/pattern-fields.png", dpi=160, facecolor="white")
