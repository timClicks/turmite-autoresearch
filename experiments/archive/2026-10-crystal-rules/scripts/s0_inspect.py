# /// script
# dependencies = ["numpy"]
# ///
"""S0/S1 inspection of crystal_s0 dumps: colour and visit histograms, and a raw patch on a ray.
usage: s0_inspect.py RULE"""
import sys
from pathlib import Path
import numpy as np

root = Path(__file__).resolve().parents[1]
rule = sys.argv[1]
g = np.fromfile(root / "dumps" / f"{rule}.grid", dtype=np.uint8)
v = np.fromfile(root / "dumps" / f"{rule}.visits", dtype=np.uint8)
S = int(round(g.size ** 0.5)); g = g.reshape(S, S); v = v.reshape(S, S)
n = len(rule)
seen = v > 0
print("visited", seen.sum())
print("visit-count histogram (1..10, >10):", [int((v == k).sum()) for k in range(1, 11)], int((v > 10).sum()))
print("final colour histogram over visited:", np.bincount(g[seen], minlength=n).tolist())
heavy = v >= 8
print("heavy(>=8) cells", int(heavy.sum()), "colour hist:", np.bincount(g[heavy], minlength=n).tolist())
# direction of heavy structure: count heavy cells with a heavy neighbour along each of 4 axes
def nb(dx, dy):
    return int((heavy & np.roll(np.roll(heavy, dy, 0), dx, 1)).sum())
print("heavy pairs  horiz", nb(1, 0), "vert", nb(0, 1), "diag(1,1)", nb(1, 1), "anti(1,-1)", nb(1, -1))
# patch around a long isolated heavy ray cell
ys, xs = np.nonzero(heavy)
i = len(ys) // 3
y0, x0 = ys[i], xs[i]
print("patch around", y0, x0, "colour / visits (centre 24x24)")
sl = (slice(y0 - 12, y0 + 12), slice(x0 - 12, x0 + 12))
for r_c, r_v in zip(g[sl], v[sl]):
    print("".join("." if c == 255 else str(c) for c in r_c), " ", "".join("." if q == 0 else ("+" if q > 9 else str(q)) for q in r_v))
