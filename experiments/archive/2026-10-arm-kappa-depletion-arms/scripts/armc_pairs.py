# /// script
# dependencies = ["numpy", "polars"]
# ///
"""Arm C feasibility (notes/kappa-experiment-design.md): pairs of rules with equal n and equal number of R, rule-mean c within
0.02, rule-mean kappa differing by >= 0.5, among the rules with >= 6 core-band runs in b2_probe.csv + item21_probe.csv."""
import sys; sys.path.insert(0, "experiments/_lib")
import polars as pl
from analyse_probe import per_rule
r = pl.concat([per_rule(pl.read_csv(f)) for f in ["experiments/archive/2026-10-b2-between-rule-variance/results/b2_probe.csv", "experiments/archive/2026-10-item21-slow-outliers/results/item21_probe.csv"]])
r = r.filter((pl.col("alpha_w") > 0.25) & (pl.col("alpha_w") < 0.42)).with_columns(base=pl.col("rule").str.split("@").list.get(0))
m = r.group_by("base").agg(n=pl.len(), c=pl.col("c").mean(), kappa=pl.col("kappa").mean()).filter(pl.col("n") >= 6).to_dicts()
pairs = [(a["base"], b["base"], round(a["c"], 3), round(b["c"], 3), round(a["kappa"], 2), round(b["kappa"], 2)) for i, a in enumerate(m) for b in m[i+1:]
         if len(a["base"]) == len(b["base"]) and a["base"].count("R") == b["base"].count("R") and abs(a["c"] - b["c"]) <= 0.02 and abs(a["kappa"] - b["kappa"]) >= 0.5]
print(len(m), "rules;", len(pairs), "matched pairs (design needs >= 10)")
for p in pairs: print(p)
open("experiments/archive/2026-10-arm-kappa-depletion-arms/results/armc_specs.txt", "w").write("\n".join(sorted({x for p in pairs for x in p[:2]})) + "\n")
