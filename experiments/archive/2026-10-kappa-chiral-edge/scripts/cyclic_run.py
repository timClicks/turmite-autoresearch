# /// script
# dependencies = ["polars", "numpy"]
# ///
"""Stage 1b (README): is ln kappa explained by the longest cyclic same-letter run M rather than the opening run?
usage: uv run experiments/archive/2026-10-kappa-chiral-edge/scripts/cyclic_run.py"""
import json
from pathlib import Path

import numpy as np
import polars as pl

root = Path(__file__).resolve().parents[4]
out = root / "experiments/archive/2026-10-kappa-chiral-edge/results"
SEED, NB, CAP = 20261019, 2000, 6
d = pl.read_csv(root / "experiments/archive/2026-10-probe-growth-census/results/probe_summary.csv").filter(
    (pl.col("cls") == "blob") & (pl.col("kappa") > 0) & (pl.col("c") > 0) & (pl.col("g_k").abs() < 0.05))


def canon(r):
    return min(r[i:] + r[:i] for i in range(len(r)))


def run0(r):
    k = 1
    while k < len(r) and r[k] == r[0]:
        k += 1
    return k


def maxcyc(r):
    return max(run0(r[i:] + r[:i]) for i in range(len(r)))


rules = d["rule"].to_list()
neck = np.array([canon(r) for r in rules])
lead = np.minimum([run0(r) for r in rules], CAP).astype(float)
M = np.minimum([maxcyc(r) for r in rules], CAP).astype(float)
n = np.array([len(r) for r in rules], float)
y = np.log(d["kappa"].to_numpy())
yc = np.log(d["c"].to_numpy())


def ols(X, y):
    X1 = np.column_stack([np.ones(len(y))] + X)
    b, *_ = np.linalg.lstsq(X1, y, rcond=None)
    return b, 1 - ((y - X1 @ b) ** 2).sum() / ((y - y.mean()) ** 2).sum()


res = {}
for lab, yy in (("lnk", y), ("lnc", yc)):
    bl, r2l = ols([lead], yy)
    bm, r2m = ols([M], yy)
    bb, r2b = ols([lead, M], yy)
    bn, r2n = ols([lead, M, n], yy)
    res[lab] = {"lead": [bl.tolist(), r2l], "M": [bm.tolist(), r2m], "lead+M": [bb.tolist(), r2b], "lead+M+len": [bn.tolist(), r2n]}
    print(f"{lab}: n={len(yy)}  lead b={bl[1]:+.3f} R2={r2l:.3f} | M b={bm[1]:+.3f} R2={r2m:.3f} | both lead={bb[1]:+.3f} M={bb[2]:+.3f} R2={r2b:.3f} | +len lead={bn[1]:+.3f} M={bn[2]:+.3f} len={bn[3]:+.3f} R2={r2n:.3f}")
b1 = res["lnk"]["lead"][0][1]
print(f"M2 ratio lead coef (both)/(lead only) = {res['lnk']['lead+M'][0][1] / b1:.2f}")

# M3: necklace level
keys = sorted(set(neck))
idx = {k: np.flatnonzero(neck == k) for k in keys}
nm = np.array([y[idx[k]].mean() for k in keys])
Mm = np.array([M[idx[k][0]] for k in keys])
def slope(a, b):
    return np.polyfit(a, b, 1)[0]
rng = np.random.default_rng(SEED)
bs = [slope(Mm[s], nm[s]) for s in (rng.integers(0, len(keys), len(keys)) for _ in range(NB))]
print(f"M3 necklace-level slope of mean ln kappa on M: {slope(Mm, nm):+.3f} CI [{np.percentile(bs, 2.5):+.3f}, {np.percentile(bs, 97.5):+.3f}] over {len(keys)} necklaces")
res["M3"] = {"slope": slope(Mm, nm), "ci": [np.percentile(bs, 2.5), np.percentile(bs, 97.5)], "n_neck": len(keys)}
# descriptive: mean ln kappa by M
for m in range(1, CAP + 1):
    s = M == m
    if s.sum():
        print(f"  M={m}: n={s.sum()} mean ln kappa {y[s].mean():+.3f}  mean ln c {yc[s].mean():+.3f}")
(out / "cyclic_run.json").write_text(json.dumps(res, indent=1, default=float))
