# /// script
# requires-python = ">=3.12"
# dependencies = ["numpy"]
# ///
"""Stage 1, P4: does every front-window snapshot decompose as top_q . B^m . bottom_q?

usage: uv run experiments/2026-10-20-rlrlll-macro-transition/scripts/stage1_snapshots.py SNAPDIR [WIN]
Each snapshot (written by examples/rlrlll_macro_transition_trace.rs) is the front window at a cycle boundary.
Only the first WIN columns are compared (default: all). For each snapshot: find the smallest row period p <= 12 of
the middle third, grow the periodic band up and down as far as it holds, and cut the rows above (top block) and below
(bottom block) at band boundaries aligned to the period. Blocks are compared across snapshots by hash; the ant's
position and heading relative to the top of the window are part of the phase.
"""
import hashlib
import sys
from collections import Counter
from pathlib import Path

import numpy as np

snapdir = Path(sys.argv[1])
win_arg = int(sys.argv[2]) if len(sys.argv) > 2 else None


def load(p):
    raw = p.read_bytes()
    nl = raw.index(b"\n")
    k, t, xf, ax, ay, h, y0, y1, win = map(int, raw[:nl].split())
    a = np.frombuffer(raw[nl + 1:], dtype=np.uint8).reshape(y1 - y0 + 1, win)
    return dict(k=k, t=t, xf=xf, ax=ax, ay=ay, h=h, y0=y0, y1=y1, a=a)


def h8(a):
    return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()[:12]


snaps = sorted((load(p) for p in snapdir.glob("snap_*.bin")), key=lambda s: s["k"])
print(f"{len(snaps)} snapshots from {snapdir}")
tops, bots, bulks, phases, fails = Counter(), Counter(), Counter(), Counter(), []
rows_out = []
for s in snaps:
    a = s["a"] if win_arg is None else s["a"][:, :win_arg]
    n = a.shape[0]
    mid = slice(n // 3, 2 * n // 3)
    period = None
    for p in range(1, 13):
        m = a[mid]
        if m.shape[0] > p and np.array_equal(m[p:], m[:-p]):
            period = p
            break
    if period is None:
        fails.append(s["k"])
        rows_out.append((s["k"], n, None, None, None))
        continue
    p = period
    # Grow the band: rows i with a[i] == a[i + p] contiguous around the middle.
    eq = np.all(a[p:] == a[:-p], axis=1)  # eq[i]: row i equals row i+p
    lo = n // 3
    while lo > 0 and eq[lo - 1]:
        lo -= 1
    hi = 2 * n // 3  # eq index
    while hi < len(eq) and eq[hi]:
        hi += 1
    # Periodic band covers rows [lo, hi + p). Align the top cut to the band start, bottom cut to whole periods.
    band_len = (hi + p) - lo
    reps = band_len // p
    top, bulk = a[:lo], a[lo:lo + p]
    bot = a[lo + reps * p:]
    phase = (s["ax"] - s["xf"], s["ay"] - s["y0"], s["h"]) if s["ay"] - s["y0"] < lo else (
        s["ax"] - s["xf"], s["ay"] - s["y1"], s["h"], "bottom")
    tops[h8(top)] += 1
    bots[h8(bot)] += 1
    bulks[(p, h8(bulk))] += 1
    phases[phase] += 1
    rows_out.append((s["k"], n, p, top.shape[0], bot.shape[0]))

print(f"no period <= 12 in the middle third: {len(fails)} snapshots {fails[:20]}")
print("bulk (period, block hash) counts:", bulks.most_common(5))
print("top-block hash counts:", tops.most_common(6), "distinct", len(tops))
print("bottom-block hash counts:", bots.most_common(6), "distinct", len(bots))
print("ant phase counts (dx from front, dy from an end, heading):", phases.most_common(8), "distinct", len(phases))
print("\nk, rows, period, top rows, bottom rows")
for r in rows_out[:10] + rows_out[-10:]:
    print(" ", r)
