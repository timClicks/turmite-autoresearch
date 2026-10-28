# /// script
# requires-python = ">=3.12"
# dependencies = ["numpy"]
# ///
"""Task B: clock law below the family's range (x in [-1537, -1471]); events from examples/rlrlll_macro_transition_window.

usage: uv run experiments/archive/2026-10-rlrlll-macro-transition/scripts/window_seed.py WINDIR_B TARGETS_FILE
Reports, per consecutive event pair, dt, the family formula 12 m(x) + c_q(x), and the extent L of cells first visited after
T_track2 in the column 3 east of the front (ref.bin is the board at T_track2). B3 uses dt - 12 L.
"""
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[4]
exec((Path(__file__).with_name("window_compare.py")).read_text().replace("\nmain()\n", "\n"))

win = Path(sys.argv[1])
targets = sorted(map(int, Path(sys.argv[2]).read_text().strip().split(",")), reverse=True)
ref = load_ev(win / "ref.bin")
evs = {}
for p in win.glob("ev_*.bin"):
    e = load_ev(p)
    evs[e["x"]] = e
skipped = [x for x in targets if x not in evs]
print(f"B1: {len(evs)} of {len(targets)} targets fired; skipped {skipped} ({len(skipped)})")
ts = [evs[x]["t"] for x in sorted(evs, reverse=True)]
print("   t strictly increasing with decreasing x:", all(b > a for a, b in zip(ts, ts[1:])))


def new_extent(e, col_x):
    """Rows of cells in column col_x visited after T_track2 (visited now, not visited in ref)."""
    c = col_x - e["x0"]
    ys = [y for y in range(e["a"].shape[0]) if e["a"][y, c] != 255 and was_old(ref, col_x, e["y0"] + y) is False]
    return (len(ys), (max(ys) - min(ys) + 1) if ys else 0)


print("x     m    q  dt     formula  diff   L(new, col x+3)  dt-12L")
xs = sorted(evs, reverse=True)
d12 = []
fail_m_le_m6 = []
for x, nx in zip(xs, xs[1:]):
    if nx != x - 3:
        continue
    m, q = mq(x)
    dt = evs[nx]["t"] - evs[x]["t"]
    f = 12 * m + CLOCK[q]
    n, L = new_extent(evs[x], x + 3)
    print(f"{x:5d} {m:4d} {q}  {dt:6d} {f:6d} {dt - f:6d}   n={n:3d} L={L:3d}      {dt - 12 * L}")
    if m <= -6:
        fail_m_le_m6.append(dt == f)
        d12.append(dt - 12 * L)
print(f"B2: pairs with m <= -6: {len(fail_m_le_m6)}, formula holds on {sum(fail_m_le_m6)}")
if d12:
    print(f"B3: dt - 12 L over those pairs: sd {np.std(d12):.1f}, values {d12}")
