# /// script
# dependencies = ["numpy", "polars"]
# ///
"""Arm A selection (notes/kappa-experiment-design.md): six lowest and six highest rule-mean kappa among rules with >= 6
core-band runs in experiments/archive/2026-10-b2-between-rule-variance/results/b2_probe.csv and experiments/archive/2026-10-item21-slow-outliers/results/item21_probe.csv; blank-board ant rules, 12 rotor seeds, 6 memoryless seeds."""
import sys; sys.path.insert(0, "experiments/_lib")
import polars as pl
from analyse_probe import per_rule
r = pl.concat([per_rule(pl.read_csv(f)) for f in ["experiments/archive/2026-10-b2-between-rule-variance/results/b2_probe.csv", "experiments/archive/2026-10-item21-slow-outliers/results/item21_probe.csv"]])
r = r.filter((pl.col("alpha_w") > 0.25) & (pl.col("alpha_w") < 0.42)).with_columns(base=pl.col("rule").str.split("@").list.get(0))
m = r.group_by("base").agg(n=pl.len(), kappa=pl.col("kappa").mean()).filter(pl.col("n") >= 6).sort("kappa")
print(m.height, "rules with >=6 core-band runs")
lo, hi = m.head(6)["base"].to_list(), m.tail(6)["base"].to_list()
print("low", m.head(6)); print("high", m.tail(6))
# Exploratory follow-up (added after the extremes were run): the 12 rules with rule-mean kappa closest to 0.9.
mid = m.with_columns(dev=(pl.col("kappa") - 0.9).abs()).sort("dev").head(12)
print("typical", mid)
open("experiments/archive/2026-10-layers-colours/results/layers_specs_typical.txt", "w").write("\n".join(mid["base"].to_list()) + "\n")
open("experiments/archive/2026-10-layers-colours/results/layers_specs.txt", "w").write("\n".join(lo + hi + [f"rotor:{s}" for s in range(1, 13)] + [f"pw:0.5:{s}" for s in range(1, 7)]) + "\n")
