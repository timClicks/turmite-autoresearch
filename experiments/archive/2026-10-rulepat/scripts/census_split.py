# /// script
# dependencies = ["polars"]
# ///
"""census_split.py : POST-HOC split of census members into regular (plateau>=0.98) and irregular (0.5..0.98)."""
import polars as pl
from pathlib import Path
R = Path(__file__).resolve().parents[1]
pl.Config.set_tbl_rows(80); pl.Config.set_fmt_str_lengths(20)
df = pl.read_csv(R / "results/census_scan.csv").with_columns(
    n=pl.col("rule").str.len_chars(), apt=pl.col("area") / pl.col("steps"))
mem = df.filter((pl.col("plateau") >= 0.5) & (pl.col("apt") >= 0.05) & ~pl.col("escaped"))
reg, irr = mem.filter(pl.col("plateau") >= 0.98), mem.filter(pl.col("plateau") < 0.98)
print("regular", reg.height, "irregular", irr.height)
print("regular: apt*mode_visits (1 = every cell visited m times, area=t/m):",
      reg.select((pl.col("apt") * pl.col("mode_visits")).round(2).alias("x")).group_by("x").len().sort("x").rows()[:8])
print("irregular by n:", irr.group_by("n").len().sort("n").rows())
print("irregular prefix RLL:", irr.filter(pl.col("rule").str.starts_with("RLL")).height,
      "pc==2:", irr.filter(pl.col("plateau_colour") == 2).height, "mode==2:", irr.filter(pl.col("mode_visits") == 2).height)
print(irr.sort(["n", "rule"]).select("rule", "mode_visits", "plateau", "plateau_colour", "apt", "alt_frac", "long_alt_runs", "max_visits"))
