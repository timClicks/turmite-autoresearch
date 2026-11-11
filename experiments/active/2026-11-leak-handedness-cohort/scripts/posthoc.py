# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy", "polars", "scipy"]
# ///
"""POST HOC (not registered): spread of the per-rule lag Lambda and its relation to rule composition.

usage (repo root): uv run --script experiments/active/2026-11-leak-handedness-cohort/scripts/posthoc.py
Reads the committed results/rules.csv and runs.csv; writes results/posthoc.txt. Written after P1 came out unresolved.
"""
from pathlib import Path

import numpy as np
import polars as pl
from scipy.stats import spearmanr

EXP = Path(__file__).resolve().parents[1]
r = pl.read_csv(EXP / "results/rules.csv").sort("rule")
runs = pl.read_csv(EXP / "results/runs.csv")
out = ["# POST HOC, not registered. Cohort C, 77 rules."]
lam = r["lam"].to_numpy()
out.append(f"Lambda: mean {lam.mean():+.3f}, sd {lam.std(ddof=1):.3f}, quartiles {np.quantile(lam, 0.25):+.3f} / {np.quantile(lam, 0.75):+.3f}, "
           f"min {lam.min():+.3f}, max {lam.max():+.3f}; |Lambda| > 0.4 in {int((np.abs(lam) > 0.4).sum())} rules")
sd = (runs.filter((pl.col("cohort") == "C") & pl.col("ef").is_in([0.3, 0.5]))
      .group_by(["rule", "arm", "ef"]).agg(pl.col("early_a").std())["early_a"].median())
dmed = float(np.median(r["delta_R"].to_numpy()))
out.append(f"median within-rule per-seed sd of early a at EF 0.3/0.5: {sd:.4f}; median Delta_R {dmed:.3f}; "
           f"implied seed noise on one rule's Lambda ~ {sd / 2 / dmed:.3f} (sd/sqrt(4)/Delta, x sqrt(2) arms, / sqrt(2) EFs)")
fr = np.array([s.count("R") / len(s) for s in r["rule"]])
rho = spearmanr(lam, fr)
out.append(f"Spearman(Lambda, fraction of R letters) = {rho.statistic:+.3f}, p = {rho.pvalue:.2g} (one of several looks; uncorrected)")
for lo, hi in [(0, 0.45), (0.45, 0.55), (0.55, 1.01)]:
    m = (fr >= lo) & (fr < hi)
    out.append(f"  R fraction in [{lo:.2f}, {min(hi, 1):.2f}): n {m.sum()}, median Lambda {np.median(lam[m]):+.3f}, Lambda > 0 in {int((lam[m] > 0).sum())}")
for pre in ("RLLL", "RRRR"):
    m = np.array([s.startswith(pre) for s in r["rule"]])
    out.append(f"  prefix {pre}: n {m.sum()}, median Lambda {np.median(lam[m]):+.3f}, Lambda > 0 in {int((lam[m] > 0).sum())}")
(EXP / "results/posthoc.txt").write_text("\n".join(out) + "\n")
print("\n".join(out))
