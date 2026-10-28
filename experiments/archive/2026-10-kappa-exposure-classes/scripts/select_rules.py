"""Deterministic rule sample for 2026-10-kappa-exposure-classes.

64 rules drawn without replacement from the 2185 stationary census rules (cls == blob,
|g_k| < 0.05, the definition used in experiments/archive/2026-10-kappa-uniform-baseline), with
numpy default_rng(20261020). Writes results/specs.txt: per rule one blank-board run (RULE, which
must reproduce the committed census windows) and four patched starts RULE@1..RULE@4, then
calibration walkers mf:1..8 (uniform by construction), rotor:1..8, rw:1..8.
Only the class/stationarity columns are used for selection, not kappa.
"""
from pathlib import Path

import numpy as np
import polars as pl

ROOT = Path(__file__).resolve().parents[4]
EXP = Path(__file__).resolve().parents[1]
SEED = 20261020

df = pl.read_csv(ROOT / "experiments/archive/2026-10-probe-growth-census/results/probe_summary.csv")
stat = df.filter((pl.col("cls") == "blob") & (pl.col("g_k").abs() < 0.05)).sort("rule")
assert stat.height == 2185, stat.height
rng = np.random.default_rng(SEED)
pick = sorted(stat["rule"].to_numpy()[rng.choice(stat.height, 64, replace=False)].tolist())
lines = []
for r in pick:
    lines.append(r)
    lines += [f"{r}@{s}" for s in range(1, 5)]
for w in ("mf", "rotor", "rw"):
    lines += [f"{w}:{s}" for s in range(1, 9)]
(EXP / "results" / "specs.txt").write_text("\n".join(lines) + "\n")
print(len(pick), "rules;", len(lines), "specs; seed", SEED)
