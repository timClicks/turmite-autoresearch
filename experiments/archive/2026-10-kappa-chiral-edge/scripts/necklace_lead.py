# /// script
# dependencies = ["polars", "numpy"]
# ///
"""Stage 1 (README): within-necklace regression of ln kappa / ln c on the opening and closing same-letter runs.
usage: uv run experiments/archive/2026-10-kappa-chiral-edge/scripts/necklace_lead.py"""
import json
from pathlib import Path

import numpy as np
import polars as pl

root = Path(__file__).resolve().parents[4]
out = root / "experiments/archive/2026-10-kappa-chiral-edge/results"
SEED, NB, CAP = 20261019, 2000, 6
d = pl.read_csv(root / "experiments/archive/2026-10-probe-growth-census/results/probe_summary.csv").filter(
    (pl.col("cls") == "blob") & (pl.col("kappa") > 0) & (pl.col("c") > 0))


def canon(r):
    return min(r[i:] + r[:i] for i in range(len(r)))


def run0(r):
    k = 1
    while k < len(r) and r[k] == r[0]:
        k += 1
    return k


rows = [(canon(r), run0(r), run0(r[::-1]), np.log(kap), np.log(c), abs(gk) < 0.05)
        for r, kap, c, gk in zip(d["rule"], d["kappa"], d["c"], d["g_k"])]
neck = np.array([x[0] for x in rows])
lead = np.array([x[1] for x in rows], float)
trail = np.array([x[2] for x in rows], float)
lk = np.array([x[3] for x in rows])
lc = np.array([x[4] for x in rows])
stat = np.array([x[5] for x in rows])


def groups(mask, L):
    idx = {}
    for i in np.flatnonzero(mask):
        idx.setdefault(neck[i], []).append(i)
    return [np.array(v) for v in idx.values() if len(v) >= 2 and len(set(L[v])) > 1]


def demean(v, gs):
    return np.concatenate([v[g] - v[g].mean() for g in gs])


def fit(gs, ycol, xcols):
    y = demean(ycol, gs)
    X = np.column_stack([demean(x, gs) for x in xcols])
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    r2 = 1 - ((y - X @ beta) ** 2).sum() / (y ** 2).sum()
    return beta, r2


rng = np.random.default_rng(SEED)
res = {}


def analyse(label, mask, cap):
    L = np.minimum(lead, cap) if cap else lead
    T = np.minimum(trail, cap) if cap else trail
    gs = groups(mask, L)
    o = {"n_groups": len(gs), "n_rules": int(sum(len(g) for g in gs))}
    for name, y in (("lnk", lk), ("lnc", lc)):
        for xn, xs in (("lead", [L]), ("trail", [T]), ("lead+trail", [L, T])):
            b, r2 = fit(gs, y, xs)
            bs = np.array([fit([gs[i] for i in rng.integers(0, len(gs), len(gs))], y, xs)[0] for _ in range(NB)])
            o[f"{name}~{xn}"] = {"beta": b.tolist(), "r2": r2,
                                  "ci_lo": np.percentile(bs, 2.5, axis=0).tolist(),
                                  "ci_hi": np.percentile(bs, 97.5, axis=0).tolist()}
    res[label] = o
    print(f"== {label}: {o['n_groups']} necklaces, {o['n_rules']} rules")
    for k, v in o.items():
        if isinstance(v, dict):
            print(f"  {k:16s} beta={np.round(v['beta'], 3).tolist()} CI lo={np.round(v['ci_lo'], 3).tolist()} "
                  f"hi={np.round(v['ci_hi'], 3).tolist()} R2={v['r2']:.3f}")


allm = np.ones(len(rows), bool)
analyse("all blob, lead capped 6", allm, CAP)
analyse("stationary |g_k|<0.05, capped 6", stat, CAP)
analyse("all blob, uncapped", allm, None)
(out / "necklace_lead.json").write_text(json.dumps(res, indent=1))
