# /// script
# requires-python = ">=3.12"
# dependencies = ["numpy"]
# ///
"""Write the canonical sweeper configurations C(m, q) read off three consecutive snapshots.

usage: uv run experiments/2026-10-20-rlrlll-macro-transition/scripts/extract_canonical.py SNAPDIR K OUT
Reads snap_K, snap_K+1, snap_K+2 (three consecutive cycle boundaries, one per phase) and writes OUT, the input of
examples/rlrlll_macro_transition_check.rs. Per phase: the ant (dx from the front column, dy from the window's top row,
heading), the top block (rows above the bulk), the bulk row and its count m, and the bottom block. Cells are written as
colour digits, '.' for never visited. This only proposes the family; the checker decides whether it is closed.
"""
import hashlib
import sys
from pathlib import Path

import numpy as np

snapdir, k0, out = Path(sys.argv[1]), int(sys.argv[2]), Path(sys.argv[3])


def load(p):
    raw = p.read_bytes()
    nl = raw.index(b"\n")
    k, t, xf, ax, ay, h, y0, y1, win = map(int, raw[:nl].split())
    a = np.frombuffer(raw[nl + 1:], dtype=np.uint8).reshape(y1 - y0 + 1, win)
    return dict(k=k, t=t, xf=xf, ax=ax, ay=ay, h=h, y0=y0, y1=y1, a=a, sha=hashlib.sha256(raw).hexdigest())


def row_str(r):
    return "".join("." if v == 255 else str(v) for v in r)


lines = [f"# extracted by extract_canonical.py from {snapdir} snapshots {k0}..{k0 + 2}"]
for q in range(3):
    s = load(snapdir / f"snap_{k0 + q}.bin")
    a, n = s["a"], s["a"].shape[0]
    eq = np.all(a[1:] == a[:-1], axis=1)  # eq[i]: row i == row i+1
    mid = n // 2
    assert eq[mid], "middle row is not in a period-1 bulk"
    lo, hi = mid, mid
    while lo > 0 and eq[lo - 1]:
        lo -= 1
    while hi + 1 < len(eq) and eq[hi + 1]:
        hi += 1
    # Bulk rows are lo .. hi + 1 inclusive.
    top, bulk, bot = a[:lo], a[lo], a[hi + 2:]
    m = hi + 2 - lo
    lines.append(f"# snap_{s['k']}.bin sha256 {s['sha']} t_end {s['t']} x_f {s['xf']}")
    lines.append(f"phase {q} k {s['k']} m {m} ant {s['ax'] - s['xf']} {s['ay'] - s['y0']} {s['h']} width {a.shape[1]}")
    lines.append(f"top {top.shape[0]}")
    lines += [row_str(r) for r in top]
    lines.append("bulk")
    lines.append(row_str(bulk))
    lines.append(f"bottom {bot.shape[0]}")
    lines += [row_str(r) for r in bot]
out.write_text("\n".join(lines) + "\n")
print(f"wrote {out}")
