"""POST HOC (not registered): is the rule-level spread of Lambda in cohort H real, as in the development cohort?

usage (repo root): uv run --frozen python experiments/proposed/2026-11-leak-minority-turn/scripts/posthoc.py
Reads the committed results/rules.csv and runs.csv; writes results/posthoc.txt. Written after P1-P3 were scored.
Same seed-noise estimate as the leak-handedness posthoc.py.
"""
from pathlib import Path

import numpy as np
import polars as pl

EXP = Path(__file__).resolve().parents[1]
r = pl.read_csv(EXP / "results/rules.csv").filter(pl.col("scoreable")).sort("rule")
runs = pl.read_csv(EXP / "results/runs.csv").filter(pl.col("rule").is_in(r["rule"].to_list()))
lam = r["lam"].to_numpy()
sd = (runs.filter(pl.col("ef").is_in([0.3, 0.5])).group_by(["rule", "arm", "ef"]).agg(pl.col("early_a").std())
      .sort(["rule", "arm", "ef"])["early_a"].median())
dmed = float(np.median(r["delta_R"].to_numpy()))
out = [f"# POST HOC, not registered. Cohort H, {lam.size} scoreable rules.",
       f"Lambda: mean {lam.mean():+.3f}, sd {lam.std(ddof=1):.3f}, quartiles {np.quantile(lam, 0.25):+.3f} / "
       f"{np.quantile(lam, 0.75):+.3f}; |Lambda| > 0.4 in {int((np.abs(lam) > 0.4).sum())} rules",
       f"median within-rule per-seed sd of early a at EF 0.3/0.5: {sd:.4f}; median Delta_R {dmed:.3f}; "
       f"implied seed noise on one rule's Lambda ~ {sd / 2 / dmed:.3f}"]
(EXP / "results/posthoc.txt").write_text("\n".join(out) + "\n")
print("\n".join(out))
