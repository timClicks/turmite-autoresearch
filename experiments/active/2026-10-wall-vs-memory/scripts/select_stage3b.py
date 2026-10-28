"""Draw the Stage 3b cohort and write its run specs.

usage (repo root): uv run --frozen python experiments/active/2026-10-wall-vs-memory/scripts/select_stage3b.py

100 rules drawn uniformly without replacement (numpy default_rng seed 20261028) from the census core
class (cls == blob, 0.30 < alpha_w < 0.37, not bursty) sorted by rule, after removing the six
Stage 1 rules. Writes results/stage3b_rules.txt and results/stage3b_specs.txt (ft:RULE:T, T = R, L, U).
"""
from pathlib import Path

import numpy as np
import polars as pl

ROOT = Path(__file__).resolve().parents[4]
EXP = Path(__file__).resolve().parents[1]

stage1 = set((EXP / "results/rules.txt").read_text().split())
census = pl.read_csv(ROOT / "experiments/archive/2026-10-probe-growth-census/results/probe_summary.csv")
core = census.filter(
    (pl.col("cls") == "blob") & (pl.col("alpha_w") > 0.30) & (pl.col("alpha_w") < 0.37) & ~pl.col("bursty")
)
pool = sorted(set(core["rule"].to_list()) - stage1)
rng = np.random.default_rng(20261028)
rules = sorted(pool[int(i)] for i in rng.choice(len(pool), size=100, replace=False))
(EXP / "results/stage3b_rules.txt").write_text("\n".join(rules) + "\n")
specs = [f"ft:{r}:{t}" for t in "RLU" for r in rules]
(EXP / "results/stage3b_specs.txt").write_text("\n".join(specs) + "\n")
print(f"pool {len(pool)} rules; drew {len(rules)}; {len(specs)} specs")
