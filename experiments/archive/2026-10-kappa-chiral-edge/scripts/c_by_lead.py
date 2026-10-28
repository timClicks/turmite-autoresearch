# /// script
# dependencies = ["polars", "numpy"]
# ///
"""Descriptive (post hoc): c and kappa by opening run, census blob stationary rules. Not registered."""
from pathlib import Path

import numpy as np
import polars as pl

root = Path(__file__).resolve().parents[4]
d = pl.read_csv(root / "experiments/archive/2026-10-probe-growth-census/results/probe_summary.csv").filter(
    (pl.col("cls") == "blob") & (pl.col("c") > 0) & (pl.col("g_k").abs() < 0.05))


def run0(r):
    k = 1
    while k < len(r) and r[k] == r[0]:
        k += 1
    return k


L = np.array([run0(r) for r in d["rule"]])
c = d["c"].to_numpy()
n = np.array([len(r) for r in d["rule"]])
kap = d["kappa"].to_numpy()
print("lead    n  mean_c  sd_c  mean(1/c)  mean_kappa")
for m in range(1, 9):
    s = L == m
    if s.sum() > 3:
        print(f"{m:4d} {s.sum():5d} {c[s].mean():.3f} {c[s].std():.3f} {np.mean(1 / c[s]):.2f}  {kap[s].mean():.3f}")
for m in (1, 2, 3, 4):
    print("lead", m, "mean c by rule length:",
          {int(k): round(float(c[(L == m) & (n == k)].mean()), 3) for k in sorted(set(n)) if ((L == m) & (n == k)).sum() > 3})
