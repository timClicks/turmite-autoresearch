# /// script
# dependencies = ["numpy", "scipy"]
# ///
"""Crystal score on crystal_s0 dumps (registered in NOTEBOOK 'deviation'). usage: crystal_score.py RULE...
G = (modal visit count, modal colour). Non-ground visited cells; diagonal runs (8-connected along (1,1) or (1,-1))
and axial runs (4-connected along rows/cols) of length >= MINRUN. score = diag fraction / axial fraction."""
import sys
from pathlib import Path
import numpy as np

MINRUN = 20
root = Path(__file__).resolve().parents[1]

def run_cover(mask, step):
    """fraction-cover mask of cells that belong to a run >= MINRUN along `step` (dy,dx)."""
    H, W = mask.shape
    dy, dx = step
    cover = np.zeros_like(mask)
    # walk each line: start cells are those whose predecessor is out of bounds
    for sy in range(H):
        for sx in range(W):
            pass
    return cover

def cover_fast(mask, step):
    # label run lengths by dynamic programming along the direction (vectorised over the orthogonal axis)
    H, W = mask.shape
    dy, dx = step
    fwd = np.zeros(mask.shape, np.int32)
    ys = range(H) if dy >= 0 else range(H - 1, -1, -1)
    if dy == 0:  # horizontal: iterate over columns
        for x in range(W):
            prev = fwd[:, x - 1] if x > 0 else 0
            fwd[:, x] = np.where(mask[:, x], prev + 1, 0)
        bwd = np.zeros(mask.shape, np.int32)
        for x in range(W - 1, -1, -1):
            prev = bwd[:, x + 1] if x < W - 1 else 0
            bwd[:, x] = np.where(mask[:, x], prev + 1, 0)
    else:
        for y in range(H):
            if y == 0:
                fwd[y] = mask[y]
                continue
            sh = np.zeros(W, np.int32)
            if dx == 0: sh = fwd[y - 1]
            elif dx == 1: sh[1:] = fwd[y - 1][:-1]
            else: sh[:-1] = fwd[y - 1][1:]
            fwd[y] = np.where(mask[y], sh + 1, 0)
        bwd = np.zeros(mask.shape, np.int32)
        for y in range(H - 1, -1, -1):
            if y == H - 1:
                bwd[y] = mask[y]
                continue
            sh = np.zeros(W, np.int32)
            if dx == 0: sh = bwd[y + 1]
            elif dx == 1: sh[:-1] = bwd[y + 1][1:]
            else: sh[1:] = bwd[y + 1][:-1]
            bwd[y] = np.where(mask[y], sh + 1, 0)
    return mask & ((fwd + bwd - 1) >= MINRUN)

for rule in sys.argv[1:]:
    g = np.fromfile(root / "dumps" / f"{rule}.grid", dtype=np.uint8)
    v = np.fromfile(root / "dumps" / f"{rule}.visits", dtype=np.uint8)
    S = int(round(g.size ** 0.5)); g = g.reshape(S, S); v = v.reshape(S, S)
    seen = v > 0
    ys, xs = np.nonzero(seen)
    sl = (slice(ys.min(), ys.max() + 1), slice(xs.min(), xs.max() + 1))
    g, v, seen = g[sl], v[sl], seen[sl]
    n = len(rule)
    gv = int(np.bincount(v[seen]).argmax()); gc = int(np.bincount(g[seen], minlength=n).argmax())
    ng = seen & ~((v == gv) & (g == gc))
    dn, ax = [cover_fast(ng, s) for s in ((1, 1), (1, -1))], [cover_fast(ng, s) for s in ((0, 1), (1, 0))]
    d = (dn[0] | dn[1]).sum() / ng.sum(); a = (ax[0] | ax[1]).sum() / ng.sum()
    print(f"{rule}: ground=({gv}x,col {gc}) nonground={ng.sum()} ({ng.sum()/seen.sum():.3f} of visited) "
          f"diag-run cover={d:.3f} axial-run cover={a:.3f} score={d/max(a,1e-9):.2f}")
