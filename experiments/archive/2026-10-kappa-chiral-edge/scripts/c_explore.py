# /// script
# dependencies = ["polars", "numpy"]
# ///
"""EXPLORATORY, unregistered (post hoc): linear model of 1/c on turn alignment p_j = s_0*s_j of the early letters.
Fit on census (stationary blob), scored on fresh rules. usage: uv run experiments/archive/2026-10-kappa-chiral-edge/scripts/c_explore.py"""
from pathlib import Path

import numpy as np
import polars as pl

root = Path(__file__).resolve().parents[4]
cen = pl.read_csv(root / "experiments/archive/2026-10-probe-growth-census/results/probe_summary.csv").filter(
    (pl.col("cls") == "blob") & (pl.col("c") > 0) & (pl.col("g_k").abs() < 0.05))
fr = pl.read_csv(root / "experiments/archive/2026-10-kappa-leadrun-fresh/results/fresh_rules.csv").filter(
    pl.col("kept") & pl.col("stationary"))


def feats(rs, K):
    """p_j = s_0 * s_j for j = 1..K-1 (letters past the rule's end repeat cyclically)."""
    out = []
    for r in rs:
        s = np.array([1 if r[j % len(r)] == "R" else -1 for j in range(K)])
        out.append(s[0] * s[1:])
    return np.array(out, float)


def run(K):
    Xc, Xf = feats(cen["rule"], K), feats(fr["rule"], K)
    yc, yf = 1 / cen["c"].to_numpy(), 1 / fr["c"].to_numpy()
    X1 = np.column_stack([np.ones(len(Xc)), Xc])
    w = np.linalg.lstsq(X1, yc, rcond=None)[0]
    pf = np.column_stack([np.ones(len(Xf)), Xf]) @ w
    cf = fr["c"].to_numpy()
    cp = 1 / pf
    r2 = 1 - ((cf - cp) ** 2).sum() / ((cf - cf.mean()) ** 2).sum()
    rin = 1 - ((yc - X1 @ w) ** 2).sum() / ((yc - yc.mean()) ** 2).sum()
    print(f"K={K}: census R2(1/c) {rin:.3f}; fresh R2(c) {r2:.3f}, median rel err {np.median(np.abs(cp - cf) / cf):.3f}; weights {np.round(w, 2).tolist()}")


for K in (3, 4, 6, 8, 10):
    run(K)
