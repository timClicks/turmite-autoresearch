"""Earliest cycle from which dt = a*swing + b[k mod p] holds exactly to the end of the log (the onset of the exact clock).
usage: python3 onset.py OUTDIR DIR P A B0,B1,...        (b in reverse-chronological order from the last cycle; rotations are tried)
   or: python3 onset.py OUTDIR DIR P A --derive PERIOD  (b taken from the last PERIOD cycles of the log itself)"""
import sys
from pathlib import Path

src = (Path(__file__).resolve().parent / "clock.py").read_text().replace("\nmain()\n", "\n")
ns = {}
exec(compile(src, "clock", "exec"), ns)
out, name, P, a = Path(sys.argv[1]), sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
rows = ns["read_events"](out / f"events_{name}.csv")
cyc = ns["cycles"](rows, P)
n = len(cyc)
if sys.argv[5] == "--derive":
    per = int(sys.argv[6])
    bs = [cyc[n - 1 - i][1] - a * cyc[n - 1 - i][2] for i in range(per)]
else:
    bs = [int(v) for v in sys.argv[5].split(",")]
best = None
for rot in range(len(bs)):
    k = n - 1
    while k >= 0 and cyc[k][1] - a * cyc[k][2] == bs[(rot + (n - 1 - k)) % len(bs)]:
        k -= 1
    first = k + 1
    if best is None or first < best[0]:
        best = (first, rot)
first, rot = best
print(f"{name} P={P} a={a} phase period {len(bs)}: {n} cycles; exact clock from cycle {first} (of {n}); cycles in the exact regime {n - first}")
if first < n:
    print(f"onset: cycle {first} ends t = {cyc[first][0]}, swing {cyc[first][2]}; the cycle before it ends t = {cyc[first-1][0] if first else None}, swing {cyc[first-1][2] if first else None}, residual {cyc[first-1][1] - a*cyc[first-1][2] if first else None}")
