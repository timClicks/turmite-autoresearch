"""Illustrative figures for main.typ (accessible overview). Run from repo root:
    uv run research-outputs/scholarly-articles/cube-root-growth/gallery.py            # -> research-outputs/scholarly-articles/cube-root-growth/fig/gallery.pdf, research-outputs/scholarly-articles/cube-root-growth/fig/growth_curves.pdf
Grids are made first with examples/snapshot.rs (deterministic, blank 8192^2 board):
    GAL=~/gal; mkdir -p $GAL; B=target/release/examples/snapshot
    $B RL 17000 $GAL/RL.bin
    for r in RLL RLR RRLL RLLR RRLRLLRLRRLR RRLRLRLLLLLL; do $B $r 33554432 $GAL/$r.bin; done   # 2^25 steps
GAL env var overrides the grid directory (default ~/gal). Colours and conventions: research-outputs/scholarly-articles/cube-root-growth/style.py."""
import os, sys
from pathlib import Path
import numpy as np
import polars as pl
from scipy.ndimage import binary_fill_holes
import matplotlib.pyplot as plt

R = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(R / "research-outputs" / "scholarly-articles" / "cube-root-growth"))
import style as st  # noqa: E402

st.apply()
GAL = Path(os.environ.get("GAL", Path.home() / "gal"))
OUT = R / "research-outputs" / "scholarly-articles" / "cube-root-growth" / "fig"


def load(rule):
    g = np.fromfile(GAL / f"{rule}.bin", dtype=np.uint8).reshape(8192, 8192)
    vis = binary_fill_holes(g > 0)  # colour 0 inside the territory was visited too (wrapped round)
    ys, xs = np.nonzero(vis)
    pad = 6
    y0, y1, x0, x1 = ys.min() - pad, ys.max() + pad, xs.min() - pad, xs.max() + pad
    return g[y0:y1 + 1, x0:x1 + 1], vis[y0:y1 + 1, x0:x1 + 1]


def rgb(g, vis, n, target=700):
    """Colour image; blocks of f x f cells are averaged in RGB so large grids stay readable."""
    img = st.cells_img(g, vis, n)
    f = max(1, max(g.shape) // target)
    h, w = img.shape[0] // f * f, img.shape[1] // f * f
    return img[:h, :w].reshape(h // f, f, w // f, f, 3).mean(axis=(1, 3)), f


def panel(ax, rule, title, g, vis, caption):
    im, f = rgb(g, vis, len(rule))
    ax.imshow(im, interpolation="nearest"); st.clean(ax)
    ax.set_title(title, fontsize=8, family="monospace", pad=2)
    st.note(ax, caption + (f"; 1 px = {f}×{f} cells" if f > 1 else ""))


# --- Fig A: gallery -------------------------------------------------------
fig, axs = plt.subplots(2, 4, figsize=(st.W, 3.7))
axs = axs.ravel()
g, vis = load("RL")
panel(axs[0], "RL", "RL (Langton's ant)", g, vis, "17 000 steps: highway")
items = [("RLL", "grows as a blob"), ("RLR", "blob, ragged edge"), ("RRLL", "blob with a notch"),
         ("RLLR", "square frame, faster growth"), ("RRLRLLRLRRLR", "12 colours, blob"), ("RRLRLRLLLLLL", "log growth: stays near home")]
for ax, (r, caption) in zip(axs[1:7], items):
    g, vis = load(r)
    panel(ax, r, st.short(r), g, vis, caption)
# zoom on the texture of RLR (centre 160 x 160 cells)
g, vis = load("RLR"); cy, cx = np.array(g.shape) // 2
z = slice(cy - 80, cy + 80), slice(cx - 80, cx + 80)
panel(axs[7], "RLR", "RLR, zoomed", g[z], vis[z], "centre, 160×160 cells: no pattern")
fig.subplots_adjust(left=0.01, right=0.99, top=0.94, bottom=0.07, wspace=0.05, hspace=0.25)
st.save(fig, OUT / "gallery.pdf"); plt.close(fig)

# --- Fig B: growth curves -------------------------------------------------
pa = pl.read_csv(R / "experiments/archive/2026-10-probe-growth-census/results/probe_all.csv")
rot = pl.read_csv(R / "experiments/archive/2026-10-calib-instrument-calibration/results/calib_rotor.csv").filter(pl.col("rule") == "rotor:0").sort("t")
rw = pl.read_csv(R / "experiments/archive/2026-10-calib-instrument-calibration/results/calib_rw.csv").filter(pl.col("rule") == "rw:0").sort("t")
fig, ax = plt.subplots(1, 2, figsize=(st.W, 2.7))
for a, key, slope, lab in [(ax[0], "width", 1 / 3, "width of the territory (cells)"), (ax[1], "area", 2 / 3, "cells visited")]:
    for r, c in st.RULE_COLOUR.items():
        d = pa.filter(pl.col("rule") == r).sort("t")
        a.plot(d["t"], d[key], color=c, label=st.short(r))
    a.plot(rot["t"], rot[key], color=st.ROTOR, label="rotor")
    a.plot(rw["t"], rw[key], color=st.RANDOM, label="random walk")
    ref = pa.filter(pl.col("rule") == "RLR").sort("t")
    t0 = 2.0 ** 14; y0 = 0.45 * float(np.interp(t0, ref["t"], ref[key]))
    tt = np.array([2.0 ** 11, 2.0 ** 27]); st.guide_line(a, tt, y0 * (tt / t0) ** slope)
    a.text(2.0 ** 24.6, y0 * (2.0 ** 24.6 / t0) ** slope * 0.4, f"slope {'2/3' if key == 'area' else '1/3'}", color=st.GUIDE["color"], fontsize=7, ha="right")
    a.set_xscale("log", base=2); a.set_yscale("log"); a.set_xlabel("steps $t$"); a.set_ylabel(lab)
for a in ax:
    st.end_labels(a, a.lines[:6], fontsize=6, gap=.075)
fig.tight_layout(); st.save(fig, OUT / "growth_curves.pdf"); plt.close(fig)
print("ok")

