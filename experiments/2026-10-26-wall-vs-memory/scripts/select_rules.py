"""Draw the rule cohort for the wall-vs-memory factorial, and write the run specs.

usage (repo root): uv run --frozen experiments/2026-10-26-wall-vs-memory/scripts/select_rules.py

Rules: 6 drawn uniformly (numpy default_rng seed 20261026) from the census core class, the same
definition as notes/mixing-random-sample.md: cls == blob, 0.30 < alpha_w < 0.37, not bursty.
Writes results/rules.txt and results/specs.txt (one probe spec per line).
"""
from pathlib import Path

import numpy as np
import polars as pl

ROOT = Path(__file__).resolve().parents[3]
EXP = Path(__file__).resolve().parents[1]
SEEDS = range(2026102601, 2026102609)
# (eps_visited, eps_fresh) conditions that depend on the rule. (0, 0) is the deterministic ant;
# (1, 0) and (1, 1) do not depend on the rule (canonical rules turn R on colour 0) and run once.
RULE_CONDS = [(0, 1), (0, 0.1), (0.01, 0), (0.1, 0), (0.1, 0.1)]

census = pl.read_csv(ROOT / "experiments/2026-10-13-probe-growth-census/results/probe_summary.csv")
core = census.filter(
    (pl.col("cls") == "blob") & (pl.col("alpha_w") > 0.30) & (pl.col("alpha_w") < 0.37) & ~pl.col("bursty")
).sort("rule")
rng = np.random.default_rng(20261026)
rules = sorted(core["rule"][int(i)] for i in rng.choice(core.height, size=6, replace=False))
(EXP / "results/rules.txt").write_text("\n".join(rules) + "\n")

specs = [f"hy:{r}:0:0:0" for r in rules]
specs += [f"hy:{r}:{ev}:{ef}:{s}" for r in rules for ev, ef in RULE_CONDS for s in SEEDS]
specs += [f"hy:R:1:0:{s}" for s in SEEDS]  # the hybrid wall walker
specs += [f"hy:R:1:1:{s}" for s in SEEDS]  # memoryless, no wall (= pw:0.5:SEED)
specs += [f"rotor:{s}" for s in SEEDS]  # calibration
(EXP / "results/specs.txt").write_text("\n".join(specs) + "\n")
print(f"core class {core.height} rules; drew {rules}; {len(specs)} specs")
