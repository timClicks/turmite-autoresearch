# /// script
# requires-python = ">=3.10"
# dependencies = ["polars"]
# ///
"""Entry probe analysis: turnaround log vs the registered predictions E1a/E1b/E2 (README, 'Entry probe')."""
import sys
import polars as pl

d = sys.argv[1]
T = pl.read_csv(f"{d}/turns.csv")
C = pl.read_csv(f"{d}/columns.csv")
# Half-cycle records: consecutive turnarounds (max->min or min->max).
T = T.with_columns(
    swing=(pl.col("y") - pl.col("y").shift(1)).abs(),
    dt=pl.col("t") - pl.col("t").shift(1),
    dx=pl.col("x") - pl.col("x").shift(1),
).drop_nulls()
print("turnarounds:", T.height, " t range", T["t"].min(), T["t"].max())

print("\n== E1a: visited-cell count per column (L) vs x, west end (front at x=-1820)")
w = C.filter((pl.col("x") >= -1820) & (pl.col("x") <= -1500) & (pl.col("count") > 50))
for lo in range(-1820, -1500, 40):
    s = w.filter((pl.col("x") >= lo) & (pl.col("x") < lo + 40))
    if s.height > 1:
        xs, ys = s["x"].to_list(), s["count"].to_list()
        n = len(xs); mx = sum(xs) / n; my = sum(ys) / n
        b = sum((a - mx) * (c - my) for a, c in zip(xs, ys)) / sum((a - mx) ** 2 for a in xs)
        print(f"x in [{lo},{lo+40}): count {min(ys)}..{max(ys)} slope {b:+.2f}/col")

print("\n== E1b/E2: swing and dt of turnarounds by time before T_end, cycle law dt ~ 6 swing? (half cycle)")
T_END = 12676421767
for back in [1e6, 3e6, 1e7, 3e7, 1e8, 3e8, 5e8]:
    s = T.filter(pl.col("t") >= T_END - int(back))
    print(f"last {back:.0e} steps: n={s.height} median swing {s['swing'].median()} median |dx| {s['dx'].abs().median()}")

print("\n== last 60 turnarounds (t_end - t, x, y, swing, dt)")
for r in T.tail(60).iter_rows(named=True):
    print(T_END - r["t"], r["x"], r["y"], r["swing"], r["dt"])

print("\n== westward-sweep test: for each 1e7-step window, ant's min x and number of turnarounds with swing>=200")
for k in range(50):
    lo = T_END - (k + 1) * 10_000_000; hi = T_END - k * 10_000_000
    s = T.filter((pl.col("t") >= lo) & (pl.col("t") < hi))
    if s.height:
        big = s.filter(pl.col("swing") >= 200)
        print(f"-{(k+1)*10}M..-{k*10}M: n={s.height} big={big.height} x range {s['x'].min()}..{s['x'].max()} swing median {s['swing'].median()}")
