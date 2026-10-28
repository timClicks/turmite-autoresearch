# /// script
# dependencies = ["polars", "numpy"]
# ///
"""Stage 3 (README): 1/c = a + b*lead fitted on census, predicted on fresh rules; prefix lookups for c.
usage: uv run experiments/archive/2026-10-kappa-chiral-edge/scripts/c_law.py"""
import json
from pathlib import Path

import numpy as np
import polars as pl

root = Path(__file__).resolve().parents[4]
out = root / "experiments/archive/2026-10-kappa-chiral-edge/results"
SEED, NB = 20261019, 2000
cen = pl.read_csv(root / "experiments/archive/2026-10-probe-growth-census/results/probe_summary.csv").filter(
    (pl.col("cls") == "blob") & (pl.col("c") > 0) & (pl.col("g_k").abs() < 0.05))
fr = pl.read_csv(root / "experiments/archive/2026-10-kappa-leadrun-fresh/results/fresh_rules.csv").filter(
    (pl.col("kept")) & (pl.col("stationary")))


def run0(r):
    k = 1
    while k < len(r) and r[k] == r[0]:
        k += 1
    return k


def lead(rs, cap=8):
    return np.minimum([run0(r) for r in rs], cap).astype(float)


Lc, cc = lead(cen["rule"]), cen["c"].to_numpy()
Lf, cf = lead(fr["rule"]), fr["c"].to_numpy()
res = {"n_census": len(cc), "n_fresh": len(cf)}


def lin(L, y):
    X = np.column_stack([np.ones(len(L)), L])
    return np.linalg.lstsq(X, y, rcond=None)[0]


a, b = lin(Lc, 1 / cc)
pred = 1 / (a + b * Lf)
r2 = 1 - ((cf - pred) ** 2).sum() / ((cf - cf.mean()) ** 2).sum()
rel = np.median(np.abs(pred - cf) / cf)
rng = np.random.default_rng(SEED)
bb = []
for _ in range(NB):
    i = rng.integers(0, len(cf), len(cf))
    bb.append(lin(Lf[i], 1 / cf[i])[1])
af, bf = lin(Lf, 1 / cf)
res["C1"] = {"a": a, "b": b, "r2": r2, "median_rel_err": rel}
res["C2"] = {"fresh_a": af, "fresh_b": bf, "ci_b": [np.percentile(bb, 2.5), np.percentile(bb, 97.5)]}
res["C3"] = {"b_census": b, "naive_range": [0.85, 1.15]}
print(f"census fit 1/c = {a:.3f} + {b:.3f} lead  (n={len(cc)}); fresh n={len(cf)}")
print(f"C1 fresh R2(c) = {r2:.3f}, median |rel err| = {rel:.3f}")
print(f"C2 fresh refit 1/c = {af:.3f} + {bf:.3f} lead, b CI [{np.percentile(bb, 2.5):.3f}, {np.percentile(bb, 97.5):.3f}] (census b {b:.3f})")
print(f"C3 census b = {b:.3f}: outside [0.85,1.15]: {not (0.85 <= b <= 1.15)}")
for m in range(1, 7):
    s = Lf == m
    if s.sum():
        print(f"   fresh lead {m}: n={s.sum()} mean c {cf[s].mean():.3f} pred {np.mean(pred[s]):.3f}")

# C4: prefix lookups, random half split
rules = cen["rule"].to_list()
y = np.log(cc)
perm = np.random.default_rng(SEED).permutation(len(rules))
A, B = perm[: len(perm) // 2], perm[len(perm) // 2:]


def lookup_r2(k):
    """Fit group means on A keyed by prefix k (fall back to lead-mean, then global), score on B."""
    key = lambda r: r[:k]
    tr = {}
    for i in A:
        tr.setdefault(key(rules[i]), []).append(y[i])
    tm = {p: np.mean(v) for p, v in tr.items()}
    lm = {}
    for i in A:
        lm.setdefault(int(Lc[i]), []).append(y[i])
    lm = {p: np.mean(v) for p, v in lm.items()}
    g = y[A].mean()
    p = np.array([tm.get(key(rules[i]), lm.get(int(Lc[i]), g)) for i in B])
    cover = np.mean([key(rules[i]) in tm for i in B])
    return 1 - ((y[B] - p) ** 2).sum() / ((y[B] - y[B].mean()) ** 2).sum(), cover


# lead-only lookup for reference
lm = {}
for i in A:
    lm.setdefault(int(Lc[i]), []).append(y[i])
lm = {p: np.mean(v) for p, v in lm.items()}
pl_ = np.array([lm.get(int(Lc[i]), y[A].mean()) for i in B])
r2_lead = 1 - ((y[B] - pl_) ** 2).sum() / ((y[B] - y[B].mean()) ** 2).sum()
res["C4"] = {"lead_only": r2_lead}
print(f"C4 held-out R2 of ln c: lead-only {r2_lead:.3f}")
for k in (2, 3, 4, 5, 6, 8):
    r, cov = lookup_r2(k)
    res["C4"][f"prefix{k}"] = {"r2": r, "coverage": cov}
    print(f"   prefix-{k} lookup: R2 {r:.3f} (test prefixes seen in train: {cov:.2f})")
(out / "c_law.json").write_text(json.dumps(res, indent=1, default=float))
