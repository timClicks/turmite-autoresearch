# /// script
# requires-python = ">=3.10"
# dependencies = ["polars"]
# ///
"""Walk the turnaround log backwards from T_END while the ant is still on the checked sweeper law.
Law (results/check_k0.txt, stage 2): one cycle = (max turnaround, min turnaround); L = swing; consecutive
cycles shift 3 columns west and add 2 rows; cycle time = 12 L + c, c in a period-3 set. Criterion per cycle
pair of same-kind turnarounds: x moves west by 2..4, swing grows by 1..3 and cycle time T satisfies
T - 12 swing in [300, 600]. Reports the westmost point where the whole later run satisfies it."""
import sys
import polars as pl

T = pl.read_csv(f"{sys.argv[1]}/turns.csv")
rows = T.rows()
mx = [r for r in rows if r[3] == 1]
ok_from = len(mx) - 1
bad = []
for i in range(len(mx) - 1, 0, -1):
    (t0, x0, y0, _), (t1, x1, y1, _) = mx[i - 1], mx[i]
    # swing of the cycle: nearest min turnaround after the max
    cond = 2 <= x0 - x1 <= 4 and 0 <= y1 - y0 <= 2 and 1 <= t1 - t0
    if cond:
        ok_from = i - 1
    else:
        bad.append((i, mx[i - 1], mx[i]))
        break
print("maxima:", len(mx), "contiguous law-like run (max-turnaround x steps west 2..4, top rises 0..2 per cycle) from index", ok_from)
t0, x0, y0, _ = mx[ok_from]
print("run starts at t =", t0, "x =", x0, "y =", y0, " steps before T_END:", 12676421767 - t0, "cycles:", len(mx) - ok_from)
print("break point:", bad)
# print the 12 maxima before the break to show what the wake looks like
for r in mx[max(0, ok_from - 12): ok_from + 6]:
    print(r)
# swing along the run
mins = [r for r in rows if r[3] == -1]
import bisect
mt = [r[0] for r in mins]
print("\ncycle swings along the run (t, x_max, y_max, next_min_y, swing, T_cycle - 12 swing):")
for j in range(ok_from, len(mx) - 1, max(1, (len(mx) - ok_from) // 25)):
    t, x, y, _ = mx[j]
    k = bisect.bisect_right(mt, t)
    if k < len(mins):
        sw = y - mins[k][2]
        Tc = mx[j + 1][0] - t
        print(t, x, y, mins[k][2], sw, Tc - 12 * sw)

# Full check on every cycle of the run (the table above samples every third).
vals = []; prev_sw = None
for j in range(ok_from, len(mx) - 1):
    t, x, y, _ = mx[j]
    k = bisect.bisect_right(mt, t)
    sw = y - mins[k][2]
    vals.append((mx[j + 1][0] - t - 12 * sw, 0 if prev_sw is None else sw - prev_sw)); prev_sw = sw
from collections import Counter
print("\nall cycles: T - 12 swing counts:", Counter(v for v, _ in vals))
print("swing increments per cycle:", Counter(d for _, d in vals))
