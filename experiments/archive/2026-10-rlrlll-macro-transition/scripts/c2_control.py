"""C2d control: the exact criterion must flag a one-cell change of the real dump on a cell the ideal ant visits outside the
rectangle (and inside it), and must NOT flag a change on a cell it never visits. usage: python3 c2_control.py WINDIR"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from c1_ant import *

win = Path(sys.argv[1])
x = -1552
raw = (win / f"ev_{x}.bin").read_bytes()
nl = raw.index(b"\n")
_, _, ax, ay, _, x0, y0, w, hgt = map(int, raw[:nl].split())
a = bytearray(raw[nl + 1:])
ph = parse_canonical()
m, q = 4, 1
p = ph[q]
T, Bt = len(p["top"]), len(p["bottom"])
n = T + m + Bt
apron = (hgt - 1) // 2
cells, pos, h = start_state(p, m)
init = dict(cells)
ant = Ant("RLRLLL", cells, pos, h)
V, xmin = set(), 0
while xmin > -3 * 98:
    V.add(ant.pos)
    ant.step()
    xmin = min(xmin, ant.pos[0])
V.add(ant.pos)
idx = lambda X, Y: (Y - p["dy"] + apron) * w + (X + 320)
mism = lambda arr: sum(1 for (X, Y) in V if (0 if arr[idx(X, Y)] == 255 else arr[idx(X, Y)]) != init.get((X, Y), 0))
print("unmodified dump: mismatches", mism(a))
vout = sorted((X, Y) for (X, Y) in V if Y < 0 and X < 0)[len(V) // 100]
b = bytearray(a); b[idx(*vout)] = 3
print(f"change real colour at visited cell outside the rectangle {vout} -> 3: mismatches {mism(b)}")
vin = sorted((X, Y) for (X, Y) in V if 0 <= X < 48 and 0 <= Y < n and init.get((X, Y), 0) not in (0,))[5]
b = bytearray(a); b[idx(*vin)] = (init[vin] % 5) + 1
print(f"change real colour at visited cell inside the rectangle {vin} (ideal {init[vin]}) -> {b[idx(*vin)]}: mismatches {mism(b)}")
unv = (-100, -60)
assert unv not in V
b = bytearray(a); b[idx(*unv)] = 3
print(f"change real colour at a cell the ideal ant never visits {unv}: mismatches {mism(b)} (must stay 0)")
