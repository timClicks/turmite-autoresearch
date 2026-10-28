# /// script
# dependencies = ["numpy", "scipy"]
# ///
"""Ground state and a raw patch across a thin ray. usage: s1_patch.py RULE"""
import sys
from pathlib import Path
import numpy as np
from scipy.ndimage import uniform_filter

root = Path(__file__).resolve().parents[1]
rule = sys.argv[1]
g = np.fromfile(root / "dumps" / f"{rule}.grid", dtype=np.uint8)
v = np.fromfile(root / "dumps" / f"{rule}.visits", dtype=np.uint8)
S = int(round(g.size ** 0.5)); g = g.reshape(S, S); v = v.reshape(S, S)
n = len(rule)
seen = v > 0
vc = np.bincount(v[seen], minlength=12)[:12]
gv = int(np.argmax(vc)); gc = int(np.bincount(g[seen], minlength=n).argmax())
print(f"{rule}: ground = visited {gv}x, colour {gc} (turn {rule[gc]}); frac of visited cells in ground state:",
      round(float(((v == gv) & (g == gc)).sum() / seen.sum()), 4))
dens = uniform_filter((v > gv).astype(float), 11) * 121
cand = np.argwhere((v > gv) & (dens >= 9) & (dens <= 13))
y0, x0 = cand[len(cand) // 2]
print("thin-ray patch at", y0, x0, " (colours; ground shown as '.'),  then visit counts")
sl = (slice(y0 - 14, y0 + 14), slice(x0 - 14, x0 + 14))
for rc, rv in zip(g[sl], v[sl]):
    print("".join("." if c == gc else str(c) for c in rc), " ", "".join("." if q == gv else ("+" if q > 9 else str(q)) for q in rv))
