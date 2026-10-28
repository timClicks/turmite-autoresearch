"""G4: per-window steps per new cell and new-cell box aspect (signature S: spc < 8 and aspect >= 20).
usage: python3 windows.py OUTDIR T_LO T_HI [WIN=1000000]"""
import sys
from pathlib import Path

out, t_lo, t_hi = Path(sys.argv[1]), int(float(sys.argv[2])), int(float(sys.argv[3]))
win = int(sys.argv[4]) if len(sys.argv) > 4 else 1_000_000
n = s = 0
spcs, aspects = [], []
for ln in (out / "windows.csv").read_text().splitlines()[1:]:
    t, new, x0, x1, y0, y1 = map(int, ln.split(","))
    if not (t_lo <= t <= t_hi) or new == 0:
        continue
    spc = win / new
    w, h = x1 - x0 + 1, y1 - y0 + 1
    asp = max(w, h) / min(w, h)
    n += 1
    s += spc < 8 and asp >= 20
    spcs.append(spc)
    aspects.append(asp)
spcs.sort(); aspects.sort()
med = lambda v: v[len(v) // 2] if v else float("nan")
print(f"windows={n} S_holds={s} ({s / max(n, 1):.3f}) median_spc={med(spcs):.3f} median_aspect={med(aspects):.2f}")
