"""POST HOC (not registered): RLLLLRRL's residual dt - 8*swing over time, and the residual period in its late regime.
usage: python3 posthoc_rlllrrl.py SCRATCH_DIR > results/stage1_posthoc_rlllrrl.txt   (from the experiment directory)"""
import sys
from collections import Counter
from pathlib import Path

here = Path(__file__).resolve().parent
src = (here / "clock.py").read_text().replace("\nmain()\n", "\n")
ns = {}
exec(compile(src, "clock", "exec"), ns)
d = Path(sys.argv[1]) / "RLLLLRRL"

print("POST HOC: RLLLLRRL, xmax P=1: residual dt - 8*swing by block of 400 cycles (cycle, t_end, swing, share of residual in 80..110, median, min)")
rows = ns["read_events"](d / "events_xmax.csv")
cyc = ns["cycles"](rows, 1)
res = [c[1] - 8 * c[2] for c in cyc]
print("cycles", len(cyc), "swing range", cyc[0][2], cyc[-1][2])
for i in range(0, len(cyc), 400):
    blk = res[i:i + 400]
    if len(blk) < 50:
        break
    share = sum(80 <= r <= 110 for r in blk) / len(blk)
    s = sorted(blk)
    print(f"cycle {i:5d} t={cyc[i][0]:>12d} swing={cyc[i][2]:6d} share(80..110)={share:.2f} median={s[len(s) // 2]} min={s[0]}")
print()
print("POST HOC: RLLLLRRL late regime, all four directions: distinct residuals dt - 8*swing and smallest period of the residual sequence (cycles 28000..32000)")
for name in ("xmin", "xmax", "ymin", "ymax"):
    rows = ns["read_events"](d / f"events_{name}.csv")
    cyc = ns["cycles"](rows, 1)
    seg = cyc[28000:32000] if len(cyc) > 32000 else cyc[-4000:]
    res = [c[1] - 8 * c[2] for c in seg]
    cnt = Counter(res)
    per = next((p for p in range(1, 400) if all(res[i] == res[i + p] for i in range(len(res) - p))), None)
    print(name, "cycles", len(cyc), "distinct residuals", len(cnt), "top", cnt.most_common(6), "exact period of residual sequence:", per)
    print("   first 24:", res[:24])
