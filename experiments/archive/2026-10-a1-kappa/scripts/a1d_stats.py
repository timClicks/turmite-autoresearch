# /// script
# dependencies = ["numpy", "polars"]
# ///
"""A1d: probe statistics of the memoryless persistent walker (pw:Q:SEED).
Produced from experiments/archive/2026-10-a1-kappa/results/a1d_probe.csv (cmd: probe 26 32768 < experiments/archive/2026-10-a1-kappa/results/a1d_specs.txt). Same windows as the census."""
import sys; sys.path.insert(0, "experiments/_lib")
import polars as pl
from analyse_probe import per_rule
r = per_rule(pl.read_csv("experiments/archive/2026-10-a1-kappa/results/a1d_probe.csv"))
r = r.with_columns(q=pl.col("rule").str.split(":").list.get(1).cast(pl.Float64))
print("rows fitted:", r.height, "of 30 (others dropped by the census filters)")
g = r.group_by("q").agg(n=pl.len(), a=pl.col("a").median(), alpha_w=pl.col("alpha_w").median(), beta=pl.col("beta").median(),
    c=pl.col("c").median(), kappa=pl.col("kappa").median(), kappa_sd=pl.col("kappa").std(), g_k=pl.col("g_k").median()).sort("q")
pl.Config.set_float_precision(3); print(g)
