"""POST HOC: residual histogram dt - a*swing for a chosen (direction, P, a) in a window.
usage: python3 residuals.py OUTDIR DIR P A T_LO T_HI"""
import sys
from collections import Counter
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
src = (Path(__file__).resolve().parent / "clock.py").read_text().replace("\nmain()\n", "\n")
ns = {}
exec(compile(src, "clock", "exec"), ns)
out, name, P, a, lo, hi = Path(sys.argv[1]), sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), int(float(sys.argv[5])), int(float(sys.argv[6]))
rows = ns["read_events"](out / f"events_{name}.csv")
cyc = [c for c in ns["cycles"](rows, P) if lo <= c[0] <= hi]
res = [c[1] - a * c[2] for c in cyc]
cnt = Counter(res)
print(f"{name} P={P} a={a}: {len(cyc)} cycles; swing range {min(c[2] for c in cyc)}..{max(c[2] for c in cyc)}; distinct residuals {len(cnt)}")
print("top residuals:", cnt.most_common(10))
print("first 24 residuals:", res[:24])
print("first 12 (dt, swing):", [(c[1], c[2]) for c in cyc[:12]])
