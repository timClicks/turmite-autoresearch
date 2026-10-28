# /// script
# dependencies = ["polars", "numpy"]
# ///
"""Frontier item 23: how many census rules are exact repeats u^k of a shorter
rule (identical dynamics), and does dropping them move the headline exponent?
Run: uv run experiments/archive/2026-10-census-sweeps/scripts/equiv_census.py"""
import polars as pl, numpy as np

def root(s):
    n = len(s)
    for p in range(1, n):
        if n % p == 0 and s[:p] * (n // p) == s:
            return s[:p]
    return s

c = pl.read_csv("experiments/archive/2026-10-census-sweeps/results/census.csv").with_columns(
    root=pl.col("rule").map_elements(root, return_dtype=pl.String))
c = c.with_columns(power=pl.col("root") != pl.col("rule"))
print("census rules", c.height, "non-primitive (exact repeats)", c["power"].sum())
print(c.group_by("cls").agg(n=pl.len(), repeats=pl.col("power").sum()).sort("cls"))
b = c.filter(pl.col("cls") == "blob")
for name, d in [("all blob", b), ("primitive blob", b.filter(~pl.col("power")))]:
    a = d["alpha"].drop_nulls().to_numpy()
    print(name, len(a), "median alpha %.4f  mean %.4f sd %.4f" % (np.median(a), a.mean(), a.std()))
# does the repeat share the root's census alpha? (would be bitwise identical)
m = c.filter(pl.col("power")).join(c.select(pl.col("rule").alias("root"), pl.col("alpha").alias("alpha_root")), on="root", how="left")
d = m.filter(pl.col("alpha_root").is_not_null()).with_columns(diff=(pl.col("alpha")-pl.col("alpha_root")).abs())
print("repeats whose root is in census:", d.height, "max |alpha diff| %.3g" % d["diff"].max())
print("by length of repeat: ", c.filter(pl.col("power")).group_by("n").len().sort("n").to_dicts())
