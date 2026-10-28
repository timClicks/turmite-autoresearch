# /// script
# dependencies = ["polars", "numpy"]
# ///
"""B4 (review follow-up): what are the 304 census 'builders'? census.py labels builder = did not reach 2^27 inside the growth grid OR steps/(w*h) < 20.
Join with experiments/archive/2026-10-census-sweeps/results/sweep_v2.csv (highway period if one was found) and experiments/archive/2026-10-census-sweeps/results/confirmed_v2.csv. usage: uv run experiments/archive/2026-10-b4-unfitted-rules/scripts/b4_builders.py"""
import polars as pl
c = pl.read_csv("experiments/archive/2026-10-census-sweeps/results/census.csv"); v = pl.read_csv("experiments/archive/2026-10-census-sweeps/results/sweep_v2.csv", schema_overrides={"period": pl.Utf8, "tail_period": pl.Utf8}).select("rule", "stop", "steps", "period", "tail_period", "width", "height")
cf = pl.read_csv("experiments/archive/2026-10-census-sweeps/results/confirmed_v2.csv").select("rule", "confirmed")
b = c.filter(pl.col("cls") == "builder").join(v, on="rule", how="left").join(cf, on="rule", how="left")
print("builders:", b.height)
hw = b.filter(pl.col("period").is_not_null() & (pl.col("period") != ""))
print("with a recognised highway period in sweep_v2:", hw.height, "; confirmed (second check) among them:", int(hw["confirmed"].fill_null(False).sum()))
no = b.filter(pl.col("period").is_null() | (pl.col("period") == ""))
print("builders with NO recognised highway:", no.height)
print(no.group_by("stop").len())
print("  of these, with a tail_period (periodic tail without translation):", int(no.filter(pl.col("tail_period").is_not_null() & (pl.col("tail_period") != "")).height))
print("  not full (left the growth grid before 2^27) vs full but spc < 20:", int((~no["full"]).sum()), int(no["full"].sum()))
print("  rule length distribution of these:", no.group_by("n").len().sort("n").rows())
print(no.select("rule", "stop", "steps", "spc", "width", "height").sort("steps").head(12))
