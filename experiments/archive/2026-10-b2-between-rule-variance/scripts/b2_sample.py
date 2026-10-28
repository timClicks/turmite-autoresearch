# /// script
# dependencies = ["polars", "numpy"]
# ///
"""B2: 100 random non-bursty blob rules (numpy seed 20261013), disjoint from the 40 rules of experiments/archive/2026-10-patched-starts/results/patched.csv, 12 patched seeds each.
Writes experiments/archive/2026-10-b2-between-rule-variance/results/b2_walkers.txt (RULE@SEED, seeds 101..112 to keep them disjoint from earlier patched seeds). usage: uv run experiments/archive/2026-10-b2-between-rule-variance/scripts/b2_sample.py"""
import numpy as np, polars as pl
s = pl.read_csv("experiments/archive/2026-10-probe-growth-census/results/probe_summary.csv").filter((~pl.col("bursty")) & (pl.col("cls") == "blob"))
old = set(l.split(",")[0].split("@")[0] for l in open("experiments/archive/2026-10-patched-starts/results/patched.csv").read().splitlines()[1:])
rules = sorted(r for r in s["rule"].to_list() if r not in old)
rng = np.random.default_rng(20261013); pick = sorted(rng.choice(len(rules), 100, replace=False))
open("experiments/archive/2026-10-b2-between-rule-variance/results/b2_walkers.txt", "w").write("\n".join(f"{rules[i]}@{sd}" for i in pick for sd in range(101, 113)) + "\n")
print(len(old), "old rules excluded;", len(pick), "rules ->", 12 * len(pick), "runs")
