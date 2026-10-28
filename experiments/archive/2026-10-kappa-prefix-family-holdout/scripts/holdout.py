# /// script
# dependencies = ["numpy", "polars"]
# ///
"""Registered in ../README.md (D1-D3, committed 1787ecc before this ran): grouped (prefix-family) vs random CV on the census.
usage (repo root): uv run experiments/archive/2026-10-kappa-prefix-family-holdout/scripts/holdout.py"""
import hashlib
import itertools
import json
from pathlib import Path

import numpy as np
import polars as pl

ROOT = Path(__file__).resolve().parents[4]
EXP = Path(__file__).resolve().parents[1]
SRC = ROOT / "experiments/archive/2026-10-probe-growth-census/results/probe_summary.csv"
SEED, NB, MINN, LAM, K, FAM = 20261020, 2000, 3, 1.0, 8, 6
rng = np.random.default_rng(SEED)

d = (pl.read_csv(SRC).filter((pl.col("cls") == "blob") & (pl.col("g_k").abs() < .05) & (pl.col("kappa") > 0))
     .select("rule", y=pl.col("kappa").log()))
rules, y = d["rule"].to_list(), d["y"].to_numpy()
n = len(rules)


def feats(r):
    return [1.0 if len(r) >= j and r[j - 1] == "L" else 0.0 for j in range(2, 9)] + [1.0 if len(r) < 8 else 0.0]


def design(rs, pairs):
    out = []
    for r in rs:
        f = feats(r)
        out.append(f + [f[a] * f[b] for a, b in itertools.combinations(range(7), 2)] if pairs else f)
    return np.array(out, float)


def ridge(Xtr, ytr, Xte):
    m, s = Xtr.mean(0), Xtr.std(0)
    s[s == 0] = 1
    A, B = (Xtr - m) / s, (Xte - m) / s
    beta = np.linalg.solve(A.T @ A + LAM * np.eye(A.shape[1]), A.T @ (ytr - ytr.mean()))
    return B @ beta + ytr.mean()


def lookup(train_rules, ytr, test_rules):
    mu = ytr.mean()
    groups = {k: {} for k in range(1, 9)}
    for r, v in zip(train_rules, ytr):
        for k in groups:
            groups[k].setdefault(r[:k], []).append(v)
    out = []
    for r in test_rules:
        p = mu
        for k in range(8, 0, -1):
            g = groups[k].get(r[:k], [])
            if len(g) >= MINN:
                p = float(np.mean(g))
                break
        out.append(p)
    return np.array(out)


def folds_random():
    perm = rng.permutation(n)
    return [perm[i::K] for i in range(K)]


def folds_grouped():
    fams = sorted({r[:FAM] for r in rules})
    order = rng.permutation(len(fams))
    fold_of = {fams[j]: i % K for i, j in enumerate(order)}
    f = np.array([fold_of[r[:FAM]] for r in rules])
    return [np.where(f == k)[0] for k in range(K)]


def oof(folds):
    pred = {m: np.zeros(n) for m in ("A", "A2", "P8")}
    mu_fold = np.zeros(n)
    for te in folds:
        tr = np.setdiff1d(np.arange(n), te)
        rt, rs = [rules[i] for i in tr], [rules[i] for i in te]
        pred["A"][te] = ridge(design(rt, False), y[tr], design(rs, False))
        pred["A2"][te] = ridge(design(rt, True), y[tr], design(rs, True))
        pred["P8"][te] = lookup(rt, y[tr], rs)
        mu_fold[te] = y[tr].mean()
    return pred, mu_fold


def r2(idx, p, mu):
    return float(1 - ((y[idx] - p[idx]) ** 2).sum() / ((y[idx] - mu[idx]) ** 2).sum())


res, ci = {}, {}
allidx = np.arange(n)
ix = rng.integers(0, n, (NB, n))
for name, folds in (("random", folds_random()), ("grouped", folds_grouped())):
    pred, mu_fold = oof(folds)
    for m, p in pred.items():
        res[(name, m)] = r2(allidx, p, mu_fold)
        b = [r2(i, p, mu_fold) for i in ix]
        ci[(name, m)] = [float(q) for q in np.quantile(b, [.025, .975])]
nfam = len({r[:FAM] for r in rules})
verdicts = {"D1 P8 random >= 0.45 and grouped < 0.30": res[("random", "P8")] >= .45 and res[("grouped", "P8")] < .30,
            "D2 A2 grouped within 0.10 of random": abs(res[("grouped", "A2")] - res[("random", "A2")]) <= .10,
            "D3 A2 grouped > P8 grouped": res[("grouped", "A2")] > res[("grouped", "P8")]}
lines = [f"# cmd: uv run experiments/archive/2026-10-kappa-prefix-family-holdout/scripts/holdout.py  seed {SEED}  folds {K}  bootstraps {NB}  (registered; README commit 1787ecc)",
         f"census stationary rules {n}; {nfam} families (first {FAM} letters); pooled out-of-fold strict R^2 against the training-fold mean",
         "model  random CV R^2 [95% CI]        grouped (family-held-out) CV R^2 [95% CI]"]
for m in ("A", "A2", "P8"):
    a, g = (res[("random", m)], ci[("random", m)]), (res[("grouped", m)], ci[("grouped", m)])
    lines.append(f"{m:5s}  {a[0]:+.3f} [{a[1][0]:+.3f}, {a[1][1]:+.3f}]      {g[0]:+.3f} [{g[1][0]:+.3f}, {g[1][1]:+.3f}]")
lines += [f"{k}: {'HELD' if v else 'FAILED'}" for k, v in verdicts.items()]
(EXP / "results").mkdir(exist_ok=True)
(EXP / "results/holdout.txt").write_text("\n".join(lines) + "\n")
(EXP / "results/holdout.json").write_text(json.dumps(dict(r2={f"{a}/{b}": v for (a, b), v in res.items()}, ci={f"{a}/{b}": v for (a, b), v in ci.items()},
    verdicts=verdicts, n=n, n_families=nfam, input_sha256={SRC.name: hashlib.sha256(SRC.read_bytes()).hexdigest()}), indent=2) + "\n")
print("\n".join(lines))
