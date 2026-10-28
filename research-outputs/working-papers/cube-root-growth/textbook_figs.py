"""Explanatory ("textbook") figures for main.typ. Run from repo root: uv run research-outputs/working-papers/cube-root-growth/textbook_figs.py
Outputs research-outputs/working-papers/cube-root-growth/fig/{mechanics,timeline,edge,timelapse,census,rotor}.pdf. Deterministic (rotor arrows from numpy seed 1).
Time-lapse grids come from examples/snapshot.rs (blank 8192^2 board):
    for k in 14 17 20 23; do $B RLL $((1<<k)) $GAL/RLL_k$k.bin; done      # B, GAL as in gallery.py
Colours and conventions: research-outputs/working-papers/cube-root-growth/style.py. Everything else is simulated here with a small reference ant (same rules as src/reference.rs; pure Python, <= 2^22 steps)."""
import os
from pathlib import Path
import numpy as np
import polars as pl
from scipy.ndimage import binary_fill_holes
import sys
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Rectangle

R = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(R / "research-outputs" / "working-papers" / "cube-root-growth"))
import style as st  # noqa: E402

st.apply()
GAL = Path(os.environ.get("GAL", Path.home() / "gal"))
OUT = R / "research-outputs" / "working-papers" / "cube-root-growth" / "fig"
DIRS = [(0, -1), (1, 0), (0, 1), (-1, 0)]  # N E S W, y down (as src/lib.rs)


def run_ant(rule, steps, S=1024, snaps=()):
    """Reference ant on an S x S board. Returns colours, visited and {t: (colours, visited)} at the snapshot times."""
    n = len(rule); turn = [1 if c == "R" else 3 for c in rule]
    col = bytearray(S * S); vis = bytearray(S * S)
    x = y = S // 2; h = 0; vis[y * S + x] = 1; out = {}
    snaps = set(snaps)
    for t in range(1, steps + 1):
        i = y * S + x; c = col[i]
        h = (h + turn[c]) & 3; col[i] = (c + 1) % n
        dx, dy = DIRS[h]; x += dx; y += dy; vis[y * S + x] = 1
        if t in snaps:
            out[t] = (np.frombuffer(bytes(col), np.uint8).reshape(S, S).copy(), np.frombuffer(bytes(vis), np.uint8).reshape(S, S).astype(bool))
    return np.frombuffer(bytes(col), np.uint8).reshape(S, S), np.frombuffer(bytes(vis), np.uint8).reshape(S, S).astype(bool), out


img_of = st.cells_img
clean = st.clean


# ---- 1. mechanics: how the rule moves the ant ------------------------------
def draw_frames(axs, rule, S=7):
    n = len(rule); turn = [1 if c == "R" else 3 for c in rule]
    col = np.zeros((S, S), int); x = y = S // 2; h = 0
    for k, ax in enumerate(axs):
        ax.set_xlim(-.5, S - .5); ax.set_ylim(S - .5, -.5); ax.set_aspect("equal"); clean(ax)
        for yy in range(S):
            for xx in range(S):
                ax.add_patch(Rectangle((xx - .5, yy - .5), 1, 1, fc=st.CELL[col[yy, xx]], ec="white", lw=.8))
        dx, dy = DIRS[h]; px, py = -dy, dx
        tri = [(x + .38 * dx, y + .38 * dy), (x - .3 * dx + .28 * px, y - .3 * dy + .28 * py), (x - .3 * dx - .28 * px, y - .3 * dy - .28 * py)]
        ax.add_patch(Polygon(tri, fc=st.INK, ec="none"))
        c = col[y, x]
        ax.set_title(f"step {k}", fontsize=7, pad=2)
        ax.set_xlabel(f"on colour {c}: turn {rule[c]},\ncell becomes {(c + 1) % n}" if k < len(axs) - 1 else "…", fontsize=6.5, labelpad=2)
        h = (h + turn[c]) & 3; col[y, x] = (c + 1) % n; dx, dy = DIRS[h]; x += dx; y += dy


fig, axs = plt.subplots(2, 6, figsize=(st.W, 3.1))
draw_frames(axs[0], "RL"); draw_frames(axs[1], "RLL")
fig.text(0.008, 0.73, "RL", family="monospace", fontsize=8, rotation=90, va="center")
fig.text(0.008, 0.28, "RLL", family="monospace", fontsize=8, rotation=90, va="center")
fig.subplots_adjust(left=0.04, right=0.995, top=0.93, bottom=0.12, wspace=0.08, hspace=0.6)
st.save(fig, OUT / "mechanics.pdf"); plt.close(fig)

# ---- 2. timeline of Langton's ant -----------------------------------------
ts = [500, 3000, 8000, 10500, 12500, 17000]
col, vis, sn = run_ant("RL", 17000, snaps=ts)
ys, xs = np.nonzero(vis); y0, y1, x0, x1 = ys.min() - 4, ys.max() + 4, xs.min() - 4, xs.max() + 4
fig, axs = plt.subplots(1, 6, figsize=(st.W, 1.45))
for ax, t in zip(axs, ts):
    c, v = sn[t]
    ax.imshow(img_of(c[y0:y1 + 1, x0:x1 + 1], v[y0:y1 + 1, x0:x1 + 1], 2), interpolation="nearest"); clean(ax)
    ax.set_title(f"$t$ = {t:,}".replace(",", " "), fontsize=7, pad=2)
fig.subplots_adjust(left=0.005, right=0.995, top=0.88, bottom=0.01, wspace=0.04)
st.save(fig, OUT / "timeline.pdf"); plt.close(fig)

# ---- 3. the edge: visited cells with an unvisited neighbour ----------------
col, vis, _ = run_ant("RLL", 2 ** 16)
nb = np.zeros_like(vis)
for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
    nb |= ~np.roll(np.roll(vis, dy, 0), dx, 1)
edge = vis & nb
ys, xs = np.nonzero(vis); y0, y1, x0, x1 = ys.min() - 3, ys.max() + 3, xs.min() - 3, xs.max() + 3
A, P = int(vis.sum()), int(edge.sum())
rgbim = np.where(vis[..., None], np.array([.80, .80, .80]), 1.0); rgbim[edge] = (0, 0, 0)  # territory grey, edge black
fig, ax = plt.subplots(1, 2, figsize=(st.W, 3.0), gridspec_kw={"width_ratios": [1.15, 1]})
ax[0].imshow(rgbim[y0:y1 + 1, x0:x1 + 1], interpolation="nearest")
ax[0].set_title(f"$t = 2^{{16}}$: area $A$ = {A:,} cells; edge $P$ = {P:,} cells".replace(",", " "), fontsize=7.5)
# zoom on an edge stretch: the right-most edge cell in the middle rows
mid = (ys.min() + ys.max()) // 2
row = np.nonzero(edge[mid])[0]; cx, cy = int(row.max()) - 12, mid
zy, zx = slice(cy - 14, cy + 14), slice(cx - 14, cx + 14)
ax[0].add_patch(Rectangle((cx - 14 - x0 - .5, cy - 14 - y0 - .5), 28, 28, fill=False, ec="k", lw=.8))
zi = img_of(col[zy, zx], vis[zy, zx], 3); m = edge[zy, zx]
ax[1].imshow(zi, interpolation="nearest"); ax[1].set_title("zoom (box at left): edge cells outlined in black", fontsize=7.5)
for yy, xx in zip(*np.nonzero(m)):
    ax[1].add_patch(Rectangle((xx - .5, yy - .5), 1, 1, fill=False, ec=st.EDGE, lw=1.4))
for a in ax:
    clean(a)
fig.tight_layout(); st.save(fig, OUT / "edge.pdf"); plt.close(fig)
print("edge: A, P =", A, P)

# ---- 4. time-lapse of one blob (same rule, ever longer) --------------------
fig, axs = plt.subplots(1, 4, figsize=(st.W, 1.9))
for ax, k in zip(axs, (14, 17, 20, 23)):
    g = np.fromfile(GAL / f"RLL_k{k}.bin", dtype=np.uint8).reshape(8192, 8192)
    v = binary_fill_holes(g > 0); ys, xs = np.nonzero(v); pad = 3
    sl = (slice(ys.min() - pad, ys.max() + pad + 1), slice(xs.min() - pad, xs.max() + pad + 1))
    gg, vv = g[sl], v[sl]
    hgt, w = gg.shape
    f = max(1, max(hgt, w) // 380); hh, ww = hgt // f * f, w // f * f
    im = img_of(gg, vv, 3)[:hh, :ww].reshape(hh // f, f, ww // f, f, 3).mean(axis=(1, 3))
    ax.imshow(im, interpolation="nearest"); clean(ax)
    ax.set_title(f"$t = 2^{{{k}}}$", fontsize=8, pad=2)
    ax.set_xlabel(f"width {w - 2 * pad:,} cells".replace(",", " "), fontsize=7, labelpad=2)
fig.subplots_adjust(left=0.005, right=0.995, top=0.88, bottom=0.12, wspace=0.04)
st.save(fig, OUT / "timelapse.pdf"); plt.close(fig)

# ---- 5. census overview ----------------------------------------------------
sw = pl.read_csv(R / "experiments/archive/2026-10-census-sweeps/results/sweep_v2.csv", infer_schema_length=0).select("rule", pl.col("n").cast(int), "stop")
ce = pl.read_csv(R / "experiments/archive/2026-10-census-sweeps/results/census.csv").select("rule", "cls")
d = sw.join(ce, on="rule", how="left").with_columns(
    pl.when(pl.col("cls").is_not_null()).then(pl.col("cls")).when(pl.col("stop") == "escaped").then(pl.lit("highway")).otherwise(pl.lit("other")).alias("k"))
order = [("highway", st.HIGHWAY, "builds a highway"), ("builder", st.BUILDER, "fills a frame slowly"), ("log", st.LOG, "grows only logarithmically"), ("blob", st.ANT, "grows as a blob")]
fig, ax = plt.subplots(figsize=(st.W * .8, 2.4))
ns = list(range(3, 13)); bottom = np.zeros(len(ns))
for key, c, lab in order:
    frac = np.array([d.filter(pl.col("n") == n).select((pl.col("k") == key).mean()).item() for n in ns])
    ax.bar(ns, frac, bottom=bottom, color=c, label=lab, width=.8); bottom += frac
print("census 'other':", d.filter(pl.col("k") == "other").height, " n=2 rules:", d.filter(pl.col("n") == 2).height)
ax.set_xticks(ns); ax.set_xlabel("rule length $n$"); ax.set_ylabel("fraction of rules"); ax.set_ylim(0, 1)
ax.legend(ncol=2, loc="upper center", bbox_to_anchor=(.5, 1.28))
fig.tight_layout(); st.save(fig, OUT / "census.pdf"); plt.close(fig)

# ---- 6. rotor walker next to an ant, and the occupation cone ---------------
T = 2 ** 22; S = 2048


def run_rotor(steps, seed=1):
    arrows = bytearray(np.random.default_rng(seed).integers(0, 4, S * S, dtype=np.uint8).tobytes())
    cnt = [0] * (S * S); x = y = S // 2
    for _ in range(steps):
        i = y * S + x; a = (arrows[i] + 1) & 3; arrows[i] = a; cnt[i] += 1
        dx, dy = DIRS[a]; x += dx; y += dy
    return np.array(cnt, np.int32).reshape(S, S)


def run_ant_counts(rule, steps):
    n = len(rule); turn = [1 if c == "R" else 3 for c in rule]
    col = bytearray(S * S); cnt = [0] * (S * S); x = y = S // 2; h = 0
    for _ in range(steps):
        i = y * S + x; c = col[i]; h = (h + turn[c]) & 3; col[i] = (c + 1) % n; cnt[i] += 1
        dx, dy = DIRS[h]; x += dx; y += dy
    return np.array(cnt, np.int32).reshape(S, S)


def profile(cnt, steps):
    v = binary_fill_holes(cnt > 0); Aa = v.sum(); yy, xx = np.nonzero(v); cy, cx = yy.mean(), xx.mean()
    Y, X = np.indices(cnt.shape); r = np.hypot(Y - cy, X - cx) / np.sqrt(Aa / np.pi)
    b = np.linspace(0, 1.3, 27); idx = np.digitize(r.ravel(), b) - 1; ok = (idx >= 0) & (idx < 26)
    num = np.bincount(idx[ok], cnt.ravel()[ok], 26); den = np.bincount(idx[ok], minlength=26)
    return (b[:-1] + b[1:]) / 2, num / np.maximum(den, 1) / (steps / Aa)


cr = run_rotor(T); ca = run_ant_counts("RLL", T)
fig, ax = plt.subplots(1, 3, figsize=(st.W, 2.3), gridspec_kw={"width_ratios": [1, 1, 1.2]})
for a, cnt, ttl in [(ax[0], cr, "rotor walker"), (ax[1], ca, "ant RLL")]:
    v = binary_fill_holes(cnt > 0); ys, xs = np.nonzero(v)
    sl = (slice(ys.min(), ys.max() + 1), slice(xs.min(), xs.max() + 1))
    a.imshow(np.where(v[sl], np.log1p(cnt[sl].astype(float)), np.nan), cmap="viridis", interpolation="nearest"); clean(a)
    a.set_title(ttl + ", $t=2^{22}$", fontsize=7.5)
for cnt, lab, c in [(cr, "rotor", st.ROTOR), (ca, "ant RLL", st.ANT)]:
    r, p = profile(cnt, T); ax[2].plot(r, p, "o-", ms=2.5, lw=.9, color=c, label=lab)
rr = np.linspace(0, 1, 50); st.guide_line(ax[2], rr, 3 * (1 - rr), label="cone $3(1-r/R)$")
ax[2].set_xlabel("distance from centre / territory radius"); ax[2].set_ylabel("visits per cell, units of $t/A$"); ax[2].legend()
fig.tight_layout(); st.save(fig, OUT / "rotor.pdf"); plt.close(fig)

# Title-page comparison: the same occupation instrument, time and colour scale.
# Keep the field visible; the measured edge difference belongs in the caption.
from matplotlib.colors import Normalize
fig, axes = plt.subplots(1, 2, figsize=(st.W, 2.15))
fields = []
for cnt in (ca, cr):
    visited = binary_fill_holes(cnt > 0)
    ys, xs = np.nonzero(visited)
    sl = (slice(ys.min(), ys.max() + 1), slice(xs.min(), xs.max() + 1))
    field = cnt[sl].astype(float) / (T / visited.sum())
    fields.append(np.ma.array(field, mask=~visited[sl]))
norm = Normalize(0, 4, clip=True)
for ax, field, label in zip(axes, fields, ("ANT / RLL", "ROTOR WALKER")):
    ax.imshow(field, cmap="Greys", norm=norm, interpolation="nearest")
    clean(ax)
    ax.set_title(label, fontsize=7, color=st.INK, pad=5, loc="center")
fig.subplots_adjust(left=.04, right=.96, bottom=.02, top=.88, wspace=.12)
st.save(fig, OUT / "hero.pdf")
plt.close(fig)
print("ok")

