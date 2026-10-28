# /// script
# requires-python = ">=3.10"
# dependencies = ["polars"]
# ///
"""Earliest cycle from which the sweeper law holds without a break, using the fine (MINSWING=3) turnaround log.
Cycle = successive y-maxima; law: x - 3, y_max + 1, and T - 12 swing = 358 (swing = y_max - following y_min)."""
import sys, bisect
import polars as pl
rows = pl.read_csv(f"{sys.argv[1]}/turns.csv").rows()
mx = [r for r in rows if r[3] == 1]
mins = [r for r in rows if r[3] == -1]
mt = [r[0] for r in mins]
def good(i):
    (t0, x0, y0, _), (t1, x1, y1, _) = mx[i], mx[i + 1]
    k = bisect.bisect_right(mt, t0)
    if k >= len(mins):
        return False
    sw = y0 - mins[k][2]
    return x1 - x0 == -3 and y1 - y0 == 1 and (t1 - t0) - 12 * sw == 358
start = len(mx) - 2
while start > 0 and good(start - 1):
    start -= 1
t0, x0, y0, _ = mx[start]
k = bisect.bisect_right(mt, t0)
print(f"law holds (x-3, ymax+1, T-12*swing=358) on every cycle from max #{start}: t={t0} x={x0} y_max={y0} swing={y0-mins[k][2]}")
print(f"cycles checked: {len(mx)-1-start}; last t in log {mx[-1][0]}")
print("the 6 cycles before the break:")
for j in range(max(0, start - 6), min(start + 3, len(mx) - 1)):
    print(mx[j], good(j) if j < len(mx) - 1 else None)
