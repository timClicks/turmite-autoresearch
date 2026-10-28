# /// script
# requires-python = ">=3.12"
# dependencies = ["numpy"]
# ///
"""Task A, POST HOC (not the registered score): rectangle-only and light-cone readings of the same dumps.

usage: uv run experiments/archive/2026-10-rlrlll-macro-transition/scripts/window_cone.py WINDIR
For each scan event x <= -1549 (m >= 2): (a) rectangle match: colour and visited flag inside top_q.bulk^m.bottom_q on the
48 columns, plus ant heading; (b) cone violations: nonzero cells outside the rectangle that the sweeper could still read.
The cone is the rectangle widened by MARGIN rows at both ends behind the front, and ahead of the front (s columns west) by
MARGIN + s//3 rows (the wedge grows 1 row per side per 3-column cycle; checked on results/cycles.csv top/bot columns).
Also reports the nearest old-blob cell to the rectangle, in rows, so the cone margin can be judged.
"""
import sys
from pathlib import Path

import numpy as np

sys.argv_backup = sys.argv
sys.argv = [sys.argv[0], sys.argv[1], "none"]
exec(open(Path(__file__).with_name("window_compare.py")).read().replace("\nmain()\n", "\n"))
MARGIN = 3


def cone(e, p, m):
    a = e["a"]
    n = len(p["top"]) + m + len(p["bot"])
    top = (e["ay"] - p["dy"]) - e["y0"]
    c0 = e["ax"] - p["dx"] - e["x0"]
    rect = rows_of(p, m)
    sub = a[top:top + n, c0:c0 + 48]
    rect_col = np.array_equal(np.where(sub == 255, 0, sub), np.where(rect == 255, 0, rect))
    rect_flag = np.array_equal(sub == 255, rect == 255)
    viol, dmin = 0, None
    nz = np.where(a == 255, 0, a) != 0
    for c in range(c0 + 48):
        s = max(0, c0 - c)
        lo, hi = top - MARGIN - s // 3, top + n + MARGIN + s // 3
        col = nz[:, c].copy()
        if c >= c0:
            col[top:top + n] = False
        inside = col[max(lo, 0):hi]
        viol += int(inside.sum())
        # nearest nonzero cell outside the rectangle rows in this column (rows from the rectangle)
        ys = np.nonzero(col)[0]
        if len(ys):
            d = np.minimum(np.abs(ys - top), np.abs(ys - (top + n - 1))).min() if c >= c0 else None
            if d is not None:
                dmin = d if dmin is None else min(dmin, d)
    return rect_col, rect_flag, viol, dmin


ph = load_canonical()
win = Path(sys.argv_backup[1])
evs = {}
for p in win.glob("ev_*.bin"):
    e = load_ev(p)
    evs[e["x"]] = e
rows = []
for x in sorted((x for x in evs if -1699 <= x <= -1549), reverse=True):
    m, q = mq(x)
    rc, rf, v, d = cone(evs[x], ph[q], m)
    ant = evs[x]["h"] == ph[q]["h"]
    rows.append((x, m, q, rc and ant, rf and ant, v, d))
    print(f"{x:5d} m={m:4d} q={q} rect_colour={rc and ant} rect_flag={rf and ant} cone_violations={v} nearest_outside_cell_rows_from_rect(behind-front cols)={d}")
ok = [r for r in rows if r[3] and r[4] and r[5] == 0]
print(f"\nrect colour+flag+ant and zero cone violations: {len(ok)} of {len(rows)}; eastmost {max(r[0] for r in ok) if ok else None}")
print("rect only:", len([r for r in rows if r[3] and r[4]]), "of", len(rows), "; failing:", [r[0] for r in rows if not (r[3] and r[4])])
