# /// script
# dependencies = ["polars", "numpy"]
# ///
"""G1 analysis of experiments/archive/2026-10-g1-ribbon-breakout/results/g1_ribbon.csv (made by examples/ribbon_trace.rs). Predictions: notes/research-frontier-2026-10-13-pm.md G1.
usage: uv run experiments/archive/2026-10-g1-ribbon-breakout/scripts/g1_stats.py > experiments/archive/2026-10-g1-ribbon-breakout/results/g1_stats.txt"""
import numpy as np, polars as pl
d = pl.read_csv("experiments/archive/2026-10-g1-ribbon-breakout/results/g1_ribbon.csv").with_columns(
    t0=pl.col("t_end").shift(1).fill_null(0),
    wx=pl.col("new_x1") - pl.col("new_x0") + 1, wy=pl.col("new_y1") - pl.col("new_y0") + 1,
    ax=pl.col("ant_x1") - pl.col("ant_x0") + 1, ay=pl.col("ant_y1") - pl.col("ant_y0") + 1)
d = d.with_columns(dt=pl.col("t_end") - pl.col("t0"))
coarse = d.filter(pl.col("dt") > 5_000_000); fine = d.filter(pl.col("dt") <= 5_000_000)
pl.Config.set_tbl_rows(30); pl.Config.set_tbl_cols(20)
print("coarse windows (1e8 steps):"); print(coarse.select("t_end", "new_cells", "steps_per_new", "wx", "wy", "ax", "ay"))
print(f"\nfine windows: {fine.height} of {fine['dt'].mean():.0f} steps, t {fine['t_end'].min()}..{fine['t_end'].max()}")
f = fine.with_columns(thin=pl.min_horizontal("wx", "wy"))
for col in ("steps_per_new", "wx", "wy", "thin"):
    v = f[col].to_numpy(); print(f"{col:14s} median {np.median(v):9.2f}  p5 {np.percentile(v,5):9.2f}  p95 {np.percentile(v,95):9.2f}  max {v.max():9.2f}")
print(f"fraction of fine windows with min(new-cell box side) <= 12: {(f['thin'] <= 12).mean():.3f}; <= 100: {(f['thin'] <= 100).mean():.3f}")
print(f"fraction with steps/new < 8: {(f['steps_per_new'] < 8).mean():.3f}; > 100: {(f['steps_per_new'] > 100).mean():.3f}")
print("\nfine windows, every 20th row:"); print(f.gather_every(20).select("t_end", "new_cells", "steps_per_new", "wx", "wy", "x", "y"))
# --- phase split: onset = first fine window after which steps_per_new stays < 8 to the end
f = f.sort("t_end"); s = f["steps_per_new"].to_numpy(); ok = s < 8
on = max(i for i in range(len(ok)) if not ok[i]) + 1
ph = f[on:]; pre = f[:on]
print(f"\nONSET of the steady phase: window ending t = {ph['t_end'][0]} ({ph.height} windows to the board edge; {pre.height} fine windows before it)")
print(f"steady phase: steps/new median {ph['steps_per_new'].median():.3f}, min {ph['steps_per_new'].min():.3f}, max {ph['steps_per_new'].max():.3f}; new cells/window median {ph['new_cells'].median():.0f}")
print(f"  new-cell box side wx: median {ph['wx'].median():.0f}, p5 {ph['wx'].quantile(.05):.0f}, p95 {ph['wx'].quantile(.95):.0f}; wy: first {ph['wy'][0]}, last {ph['wy'][-1]}, max {ph['wy'].max()}")
print(f"  fraction of steady-phase windows with wx <= 12: {(ph['wx'] <= 12).mean():.3f}; <= 100: {(ph['wx'] <= 100).mean():.3f}")
print(f"  ant x from {ph['x'][0]} to {ph['x'][-1]}; cells gained {ph['new_cells'].sum()}")
print("pre-onset fine windows (last 10):"); print(pre.tail(10).select("t_end", "new_cells", "steps_per_new", "wx", "wy"))
