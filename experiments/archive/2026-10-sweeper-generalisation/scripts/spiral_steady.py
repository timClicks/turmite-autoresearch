"""Stage 2 probe, steady-state test: is the outer band of the configuration at T1 the band at T0 moved outward (cell by cell, by depth from
the edge) on the straight stretch of each side?  (stdlib only)
usage: python3 spiral_steady.py DIR T0 T1 D"""
import sys
from collections import Counter
from pathlib import Path

d = Path(sys.argv[1])
T0, T1, D = int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])


def load(t):
    lines = (d / f"band_{t}.txt").read_text().split("\n")
    hdr = list(map(int, lines[0].split()))
    cells = {}
    for ln in lines[1:]:
        if ln:
            x, y, c = ln.split()
            cells[(int(x), int(y))] = int(c)
    return hdr, cells


h0, c0 = load(T0)
h1, c1 = load(T1)
x0, x1, y0, y1 = h0[1:5]
X0, X1, Y0, Y1 = h1[1:5]
print("bbox T0", (x0, x1, y0, y1), "bbox T1", (X0, X1, Y0, Y1), "growth per side", (x0 - X0, X1 - x1, y0 - Y0, Y1 - y1))
# per side: a function giving the cell at (depth, along) for each time; the 'along' coordinate shifts by an unknown even s.
sides = {
    "west": (lambda cells, bb, dep, a: cells.get((bb[0] + dep, a), 0), (y0 + 200, y1 - 200), None),
    "east": (lambda cells, bb, dep, a: cells.get((bb[1] - dep, a), 0), (y0 + 200, y1 - 200), None),
    "north": (lambda cells, bb, dep, a: cells.get((a, bb[2] + dep), 0), (x0 + 200, x1 - 200), None),
    "south": (lambda cells, bb, dep, a: cells.get((a, bb[3] - dep), 0), (x0 + 200, x1 - 200), None),
}
for name, (get, (a0, a1), _) in sides.items():
    best = None
    for s in range(-8, 9):
        mism = tot = 0
        for a in range(a0, a1, 3):
            for dep in range(0, D, 4):
                tot += 1
                if get(c0, (x0, x1, y0, y1), dep, a) != get(c1, (X0, X1, Y0, Y1), dep, a + s):
                    mism += 1
        if best is None or mism < best[0]:
            best = (mism, tot, s)
    mism, tot, s = best
    print(f"{name}: best along-shift {s}: {mism} of {tot} sampled cells differ ({mism / tot:.3f})")
    # mismatches by depth at the best shift
    byd = Counter()
    for a in range(a0, a1, 3):
        for dep in range(0, D, 1):
            if get(c0, (x0, x1, y0, y1), dep, a) != get(c1, (X0, X1, Y0, Y1), dep, a + s):
                byd[dep] += 1
    print("   mismatching depths (count):", sorted(byd.items())[:24], "...")
