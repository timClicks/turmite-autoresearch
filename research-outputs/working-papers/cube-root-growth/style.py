"""Shared visual language for every figure in main.typ. Import, call apply(), use the names below.

Colours carry a fixed meaning across the paper:
  ANT / blob rules   blue          ROTOR walker   red         RANDOM walk (control)  grey
  LOG-growing rules  teal          builders       brown       HIGHWAY builders       purple
  EDGE cells         black outline (never a fill: cells keep their own colour underneath)
  theory / guides    grey dashed   (slope guides, the cone, y = x)
Cell states (colour 0 .. n-1 of a rule) use CELL, a separate qualitative set with no red, so a red mark always
means "rotor" and black always means "edge / ant". Colour 0 is light grey when visited; never-visited ground is white.
Conventions: rule names in monospace; full-width figures 6.5 in wide; 8 pt text, 6.5 pt for notes/legends; no top/right
spines; legends unframed; log axes in base 2 for t, base 10 for sizes."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from cycler import cycler

W = 6.5            # full text width, inches
W_HALF = 3.2

ANT = "#3b4cc0"
ROTOR = "#d1495b"
RANDOM = "#8a8a8a"
LOG = "#1fa187"
BUILDER = "#8c6d31"
HIGHWAY = "#7a3b8f"
EDGE = "#111111"
GUIDE = dict(color="#96968e", ls=(0, (3, 3)), lw=.65)
INK = "#222222"

# Cell-state palette (index = colour). 0 is the visited-blank grey.
CELL = ["#e3e3e3", "#1fa187", "#e8a33d", "#7a3b8f", "#5fb3d9", "#8c6d31", "#b8d85a", "#444444", "#e377c2", "#3b4cc0", "#17becf", "#bcbd22"]

# Several ant rules in one plot: a blue-violet family (the rotor is red, log growth teal).
RULES = ["#3b4cc0", "#5fb3d9", "#7a3b8f", "#8c6d31", "#444444", "#9aa5ea"]
RULE_COLOUR = {"RLL": RULES[0], "RLR": RULES[1], "RRLL": RULES[2], "RRLRLRLLLLLL": LOG}


def apply():
    plt.rcParams.update({
        "font.family": "DejaVu Sans", "mathtext.fontset": "dejavuserif",
        "pdf.fonttype": 42, "ps.fonttype": 42,
        "font.size": 8, "axes.titlesize": 8, "axes.labelsize": 8, "legend.fontsize": 6.5, "legend.frameon": False,
        "xtick.labelsize": 7, "ytick.labelsize": 7, "axes.spines.top": False, "axes.spines.right": False,
        "axes.labelcolor": INK, "text.color": INK, "xtick.color": INK, "ytick.color": INK,
        "axes.prop_cycle": cycler(color=RULES), "lines.linewidth": 1.0, "figure.dpi": 150, "savefig.dpi": 300,
        "axes.edgecolor": "#aaa9a2", "axes.linewidth": .45,
        "axes.titlelocation": "left", "axes.titleweight": "normal",
        "axes.labelpad": 5, "axes.grid": False,
        "xtick.direction": "out", "ytick.direction": "out",
        "xtick.major.size": 2.5, "ytick.major.size": 2.5,
        "xtick.major.width": .45, "ytick.major.width": .45,
        "xtick.minor.visible": False, "ytick.minor.visible": False,
        "legend.labelcolor": "linecolor", "legend.handlelength": 1.3,
        "legend.borderaxespad": .3, "savefig.facecolor": "white",
    })


def end_labels(ax, lines, fontsize=6.5, gap=.075):
    """Label actual endpoints; leaders preserve identity when labels must move.

    Space labels in axes coordinates so log scales get the same treatment.
    Call after setting limits and scales, before tight_layout.
    """
    ax.figure.canvas.draw()
    items = []
    for line in lines:
        x, y = np.asarray(line.get_xdata()), np.asarray(line.get_ydata())
        valid = np.isfinite(x) & np.isfinite(y)
        if not valid.any():
            continue
        last = np.flatnonzero(valid)[-1]
        endpoint = (x[last], y[last])
        height = ax.transAxes.inverted().transform(ax.transData.transform(endpoint))[1]
        items.append((height, line, endpoint))
    items.sort(key=lambda item: item[0])
    heights = []
    for height, _, _ in items:
        heights.append(max(.04, height, heights[-1] + gap if heights else .04))
    if heights and heights[-1] > .96:
        heights = [h - (heights[-1] - .96) for h in heights]
    for height, (_, line, endpoint) in zip(heights, items):
        ax.annotate(line.get_label(), xy=endpoint, xycoords="data",
                    xytext=(1.03, height), textcoords="axes fraction",
                    color=line.get_color(), fontsize=fontsize, va="center",
                    annotation_clip=False,
                    arrowprops=dict(arrowstyle="-", color=line.get_color(), lw=.4,
                                    shrinkA=2, shrinkB=2))


def save(fig, path):
    """Keep vector output and a matching inspection image; omit volatile dates."""
    from pathlib import Path
    path = Path(path)
    for ax in fig.axes:
        ax.minorticks_off()
    fig.savefig(path, bbox_inches="tight", pad_inches=.05,
                metadata={"CreationDate": None, "ModDate": None})
    fig.savefig(path.with_suffix(".png"), dpi=160, bbox_inches="tight", pad_inches=.05)


def short(rule, keep=6):
    """Rule name for titles: long rules are abbreviated with an ellipsis."""
    return rule if len(rule) <= keep + 3 else rule[:keep] + "…" + rule[-3:]


def rule_title(ax, rule, extra="", pad=2):
    ax.set_title(short(rule) + extra, fontsize=8, family="monospace", pad=pad)


def cell_rgb(n):
    """(n, 3) float array: the colour of each cell state, 0 = visited blank."""
    return np.array([[int(CELL[c % len(CELL)][i:i + 2], 16) for i in (1, 3, 5)] for c in range(n)], float) / 255


def cells_img(col, vis, n):
    """RGB image of a colour field; never-visited cells are white."""
    return np.where(vis[..., None], cell_rgb(n)[col % n], 1.0)


def clean(ax):
    """Image panel: no ticks, no frame."""
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(False)


def note(ax, text, y=-0.03):
    ax.text(0.5, y, text, transform=ax.transAxes, ha="center", va="top", fontsize=6.5)


def guide_line(ax, x, y, **kw):
    ax.plot(x, y, **{**GUIDE, **kw})
