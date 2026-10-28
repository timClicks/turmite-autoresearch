# /// script
# dependencies = ["polars", "numpy"]
# ///
"""Item 3 / P2.1: how much of the rule-to-rule variation of c is carried by letters 1,2 vs later ones?
Core blob rules, non-bursty, n>=8, primitive. Linear model c ~ [letter_j == R], j=1..5 plus n.
Reports R^2 of subsets and a 5-fold CV R^2. Run: uv run experiments/archive/2026-10-probe-growth-census/scripts/c_letters.py"""
import numpy as np, polars as pl
s = pl.read_csv("experiments/archive/2026-10-probe-growth-census/results/probe_summary.csv").filter((~pl.col("bursty")) & (pl.col("cls") == "blob") & (pl.col("n") >= 8))
def root(x):
    n = len(x)
    for p in range(1, n):
        if n % p == 0 and x[:p] * (n // p) == x: return x[:p]
    return x
s = s.filter(pl.col("rule").map_elements(lambda x: root(x) == x, return_dtype=pl.Boolean))
rules = s["rule"].to_list(); c = s["c"].to_numpy()
L = np.array([[1.0 if r[j] == "R" else 0.0 for j in range(1, 6)] for r in rules])
fr = np.array([r.count("R") / len(r) for r in rules])
print("rules", len(c), "sd(c) %.3f" % c.std())
def r2(X, y):
    X = np.c_[np.ones(len(y)), X]; b, *_ = np.linalg.lstsq(X, y, rcond=None); return 1 - ((y - X @ b) ** 2).sum() / ((y - y.mean()) ** 2).sum(), b
for name, cols in [("letter1", [0]), ("letter2", [1]), ("letters1-2", [0, 1]), ("letters3-5", [2, 3, 4]), ("letters1-5", [0, 1, 2, 3, 4])]:
    print(f"{name:12s} R2 = {r2(L[:, cols], c)[0]:.3f}")
print("fracR only R2 = %.3f" % r2(fr[:, None], c)[0])
print("letters1-2 + later-letters ... R2 %.3f; all five + fracR %.3f" % (r2(L, c)[0], r2(np.c_[L, fr], c)[0]))
r, b = r2(L, c); print("coefficients (letters 1..5, effect of R vs L on c):", np.round(b[1:], 3))
# 5-fold CV
rng = np.random.default_rng(20261012); idx = rng.permutation(len(c)); folds = np.array_split(idx, 5)
for name, cols in [("letters1-2", [0, 1]), ("letters1-5", [0, 1, 2, 3, 4])]:
    pred = np.zeros(len(c))
    for f in folds:
        tr = np.setdiff1d(idx, f); X = np.c_[np.ones(len(tr)), L[tr][:, cols]]; bb, *_ = np.linalg.lstsq(X, c[tr], rcond=None)
        pred[f] = np.c_[np.ones(len(f)), L[f][:, cols]] @ bb
    print(f"CV R2 {name}: {1 - ((c - pred) ** 2).sum() / ((c - c.mean()) ** 2).sum():.3f}")
