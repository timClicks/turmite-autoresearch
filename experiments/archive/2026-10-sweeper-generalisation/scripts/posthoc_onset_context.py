"""POST HOC (not registered): residuals dt - 8*swing around and before the exact-clock onset of RLLLRLRLLL.
usage: python3 posthoc_onset_context.py SCRATCH_DIR > results/stage1_onset_context.txt   (from the experiment directory)"""
import sys
from collections import Counter
from pathlib import Path

here = Path(__file__).resolve().parent
src = (here / "clock.py").read_text().replace("\nmain()\n", "\n")
ns = {}
exec(compile(src, "clock", "exec"), ns)
rows = ns["read_events"](Path(sys.argv[1]) / "RLLLRLRLLL" / "events_xmin.csv")
cyc = ns["cycles"](rows, 1)
res = [c[1] - 8 * c[2] for c in cyc]
print("POST HOC residuals dt-8*swing near the onset (cycle index, residual, swing):")
print([(i, res[i], cyc[i][2]) for i in range(2860, 2880)])
for lo, hi in ((0, 500), (500, 1500), (1500, 2400), (2400, 2860)):
    c = Counter(res[lo:hi])
    print(f"cycles {lo}-{hi}: distinct residuals {len(c)}, top {c.most_common(4)}")
print("swing at cycle 0:", cyc[0][2], "t_end of cycle 0:", cyc[0][0])
