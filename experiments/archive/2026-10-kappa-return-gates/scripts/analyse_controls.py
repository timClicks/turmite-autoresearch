"""Rotor / random-walk controls: known walkers through the same instrument (descriptive calibration)."""
from pathlib import Path
import json, sys
import polars as pl
sys.path.insert(0, str(Path(__file__).resolve().parent))
EXP = Path(__file__).resolve().parents[1]
runs = pl.read_csv(EXP / "results/controls_runs.csv", schema_overrides={"ext_boundary": pl.Int64, "hole_boundary": pl.Int64})
runs = runs.with_columns(pl.col("rule").alias("walker"), (pl.col("g1_obs") - pl.col("g1_null")).alias("g1"), (pl.col("B") / pl.col("steps")).alias("q"),
                         (pl.col("hole_boundary") / (pl.col("hole_boundary") + pl.col("ext_boundary"))).alias("hole_frac"))
g = runs.group_by("walker", "band").agg(pl.len().alias("n"), pl.col("g1").mean().alias("g1_mean"), pl.col("g1").std().alias("g1_sd_between_seeds"),
    pl.col("q").mean().alias("boundary_occupancy_mean"), pl.col("q").std().alias("boundary_occupancy_sd"),
    (pl.col("exits").sum() / pl.col("steps").sum()).alias("exit_rate"), pl.col("hole_frac").mean().alias("hole_boundary_fraction"),
    pl.col("g1_events").median().alias("median_events"), pl.col("t_final").median().alias("median_t_final")).sort("walker", "band")
(EXP / "results/controls_analysis.json").write_text(json.dumps(g.to_dicts(), indent=1) + "\n")
print(g)
