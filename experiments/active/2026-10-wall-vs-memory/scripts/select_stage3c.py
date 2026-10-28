"""Write the Stage 3c run specs (no draw: both cohorts are the committed Stage 1 and Stage 3b rule lists).

usage (repo root): uv run --frozen python experiments/active/2026-10-wall-vs-memory/scripts/select_stage3c.py

Cohort A: Stage 1 rules x seeds 2026102601..08, sets RU, LU, RLU. Cohort B: Stage 3b rules x seed
2026102801, sets RU, RLU. Gate T3: fs:RULE:RL:2026102601 for the Stage 1 rules. Writes results/stage3c_specs.txt.
"""
from pathlib import Path

EXP = Path(__file__).resolve().parents[1]
a_rules = sorted((EXP / "results/rules.txt").read_text().split())
b_rules = sorted((EXP / "results/stage3b_rules.txt").read_text().split())
specs = [f"fs:{r}:{s}:{seed}" for s in ("RU", "LU", "RLU") for r in a_rules for seed in range(2026102601, 2026102609)]
specs += [f"fs:{r}:{s}:2026102801" for s in ("RU", "RLU") for r in b_rules]
specs += [f"fs:{r}:RL:2026102601" for r in a_rules]
(EXP / "results/stage3c_specs.txt").write_text("\n".join(specs) + "\n")
print(f"{len(specs)} specs")
