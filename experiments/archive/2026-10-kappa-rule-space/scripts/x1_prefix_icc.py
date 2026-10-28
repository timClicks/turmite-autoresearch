# /// script
# dependencies = ["polars", "numpy"]
# ///
"""EXPLORATORY (not pre-registered), prompted by W1/W2: how much of ln kappa variance (census, single run) is shared by rules with the
same p-letter prefix, among stationary rules vs all? One-way ICC(1) with unequal group sizes, permutation null (equal-n shuffles).
usage (repo root): uv run experiments/archive/2026-10-kappa-rule-space/scripts/x1_prefix_icc.py"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import numpy as np, polars as pl
from kcommon import *

cen = census().filter(pl.col("kappa") > 0)
rules = np.array(cen["rule"].to_list()); y = np.log(cen["kappa"].to_numpy()); st = np.abs(cen["g_k"].to_numpy()) < 0.05
nlen = np.array([len(r) for r in rules])


def icc1(groups):
    gs = [g for g in groups if len(g) >= 2]
    N = sum(len(g) for g in gs); k = len(gs); grand = np.concatenate(gs).mean()
    ssb = sum(len(g) * (g.mean() - grand) ** 2 for g in gs); ssw = sum(((g - g.mean()) ** 2).sum() for g in gs)
    msb = ssb / (k - 1); msw = ssw / (N - k); n0 = (N - sum(len(g) ** 2 for g in gs) / N) / (k - 1)
    return (msb - msw) / (msb + (n0 - 1) * msw), k, N


def prefix_groups(mask, p):
    d = {}
    for r, v in zip(rules[mask], y[mask]):
        d.setdefault(r[:p], []).append(v)
    return [np.array(v) for v in d.values()]


R = rng(7); out = []
for label, mask in (("all", np.ones(len(y), bool)), ("stationary", st)):
    for p in (2, 3, 4, 5, 6):
        icc, k, N = icc1(prefix_groups(mask, p))
        # null: shuffle ln kappa within equal length (keeps size/length structure)
        nulls = []
        for _ in range(300):
            yp = y.copy()
            for n in np.unique(nlen):
                g = np.where((nlen == n))[0]; yp[g] = y[R.permutation(g)]
            d = {}
            for r, v in zip(rules[mask], yp[mask]):
                d.setdefault(r[:p], []).append(v)
            nulls.append(icc1([np.array(v) for v in d.values()])[0])
        out.append(f"{label:10s} prefix {p}: groups(>=2) {k:5d} rules {N:5d}  ICC {icc:+.3f}   null {np.mean(nulls):+.3f} +- {np.std(nulls):.3f}")
txt = header("uv run experiments/archive/2026-10-kappa-rule-space/scripts/x1_prefix_icc.py") + "EXPLORATORY: prefix-sharing ICC of ln kappa (census, single run)\n" + "\n".join(out) + "\n"
(EXP / "results" / "x1_prefix_icc.txt").write_text(txt); print(txt)
