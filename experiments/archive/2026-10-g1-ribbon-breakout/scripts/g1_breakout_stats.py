# /// script
# dependencies = ["polars", "numpy"]
# ///
import polars as pl
import numpy as np

df = pl.read_csv("experiments/archive/2026-10-g1-ribbon-breakout/results/g1_ribbon.csv").with_columns(
    t0=pl.col("t_end").shift(1).fill_null(0),
    wx=pl.col("new_x1") - pl.col("new_x0") + 1,
    wy=pl.col("new_y1") - pl.col("new_y0") + 1,
    ax=pl.col("ant_x1") - pl.col("ant_x0") + 1,
    ay=pl.col("ant_y1") - pl.col("ant_y0") + 1,
).with_columns(
    dt=pl.col("t_end") - pl.col("t0"),
    thin=pl.min_horizontal("wx", "wy")
)
fine = df.filter(pl.col("dt") <= 5_000_000)
breakout = fine.filter(pl.col("steps_per_new") < 10)
print("Total fine windows:", fine.height)
print("Breakout windows (steps_per_new < 10):", breakout.height)
print("Breakout t range:", breakout["t_end"].min(), "to", breakout["t_end"].max())
print(f"Breakout steps_per_new mean: {breakout['steps_per_new'].mean():.3f}, min: {breakout['steps_per_new'].min():.3f}, max: {breakout['steps_per_new'].max():.3f}")
v_thin = breakout["thin"].to_numpy()
print(f"Breakout thin (transverse width) median: {np.median(v_thin):.1f}, min: {v_thin.min()}, max: {v_thin.max()}, p95: {np.percentile(v_thin, 95):.1f}")
print(f"Fraction of breakout windows with thin <= 12: {(v_thin <= 12).mean():.3f}")
print(f"Fraction of breakout windows with thin <= 60: {(v_thin <= 60).mean():.3f}")
print(f"Fraction of breakout windows with thin <= 100: {(v_thin <= 100).mean():.3f}")
print("\nFirst 5 breakout windows:")
print(breakout.head(5).select("t_end", "new_cells", "steps_per_new", "wx", "wy", "thin", "x", "y"))
print("\nLast 5 breakout windows:")
print(breakout.tail(5).select("t_end", "new_cells", "steps_per_new", "wx", "wy", "thin", "x", "y"))
