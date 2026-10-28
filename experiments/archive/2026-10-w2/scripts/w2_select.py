# /// script
# dependencies = ["polars"]
# ///
"""W2 selection: 10 sqrt-class and 10 chaotic-class 2x2 turmite tables, seed 20261013, from the 2^20 screen."""
import polars as pl
d = pl.read_csv("experiments/archive/2026-10-ext-other-lattices-turmites-noise/results/ext_tm_screen_class.csv").filter(pl.col("spec").str.starts_with("tm:2:2:"))
sq = d.filter((pl.col("cls") == "blob") & (pl.col("a") < 0.505) & (pl.col("A") > 500))
ch = d.filter((pl.col("cls") == "blob") & (pl.col("a") >= 0.55) & (pl.col("a") < 0.85) & (pl.col("A") > 500))
print(d.height, sq.height, ch.height, file=__import__("sys").stderr)
for name, s in (("sq", sq), ("ch", ch)):
    for r in s.sample(10, seed=20261013).sort("spec").iter_rows(named=True):
        print(r["spec"])
