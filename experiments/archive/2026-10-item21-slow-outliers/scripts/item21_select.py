# /// script
# dependencies = ["polars", "numpy"]
# ///
"""Item 21: pick the extreme exponent outliers among blob rules (alpha_w > 0.40 or < 0.27) plus 30 random core
controls (0.30 < alpha_w < 0.37), numpy seed 20261013; write experiments/archive/2026-10-item21-slow-outliers/results/item21_walkers.txt (RULE@SEED, seeds 1..12)."""
import numpy as np, polars as pl
s = pl.read_csv("experiments/archive/2026-10-probe-growth-census/results/probe_summary.csv").filter(pl.col("cls") == "blob")
hi = s.filter(pl.col("alpha_w") > 0.40); lo = s.filter(pl.col("alpha_w") < 0.27)
core = s.filter((pl.col("alpha_w") > 0.30) & (pl.col("alpha_w") < 0.37)).sample(30, seed=20261013)
sel = [(r, "high") for r in hi["rule"]] + [(r, "low") for r in lo["rule"]] + [(r, "core") for r in core["rule"]]
pl.DataFrame({"rule": [a for a, _ in sel], "group": [b for _, b in sel]}).write_csv("experiments/archive/2026-10-item21-slow-outliers/results/item21_rules.csv")
open("experiments/archive/2026-10-item21-slow-outliers/results/item21_walkers.txt", "w").write("\n".join(f"{r}@{k}" for r, _ in sel for k in range(1, 13)) + "\n")
print(len(hi), len(lo), core.height, "rules;", len(sel) * 12, "runs")
