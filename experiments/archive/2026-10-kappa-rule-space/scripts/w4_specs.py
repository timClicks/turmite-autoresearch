# /// script
# dependencies = ["polars", "numpy"]
# ///
"""W4 specs: pool-192 rules x 6 patched seeds (301..306); 30 census blob non-pool rules, blank board (numpy seed 20261014+21);
controls rotor:1..6 and pw:0.5:1..6. Writes results/w4_specs.txt. usage (repo root): uv run experiments/archive/2026-10-kappa-rule-space/scripts/w4_specs.py"""
from pathlib import Path
import numpy as np, polars as pl
EXP = Path(__file__).resolve().parents[1]
pool = pl.read_csv(EXP / "results" / "rules_pool.csv")["base"].to_list()
cen = pl.read_csv(EXP / "results" / "rules_census.csv").filter(~pl.col("in_pool"))["rule"].to_list()
rng = np.random.default_rng(20261014 + 21)
extra = [cen[i] for i in sorted(rng.choice(len(cen), 30, replace=False))]
lines = [f"{r}@{s}" for r in sorted(pool) for s in range(301, 307)] + extra + [f"rotor:{s}" for s in range(1, 7)] + [f"pw:0.5:{s}" for s in range(1, 7)]
(EXP / "results" / "w4_specs.txt").write_text("\n".join(lines) + "\n")
print(len(pool), "pool rules;", len(extra), "extra census rules;", len(lines), "specs")
