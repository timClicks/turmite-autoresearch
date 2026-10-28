# /// script
# dependencies = ["numpy", "polars"]
# ///
"""Registered in ../README.md (B1-B3, committed 32c0f82 before this ran): additive vs pairwise letter-by-position models of ln kappa.
usage (repo root): uv run experiments/archive/2026-10-kappa-prefix-additive/scripts/additive.py"""
import hashlib
import itertools
import json
from pathlib import Path

import numpy as np
import polars as pl

ROOT = Path(__file__).resolve().parents[4]
EXP = Path(__file__).resolve().parents[1]
SRC_TRAIN = ROOT / "experiments/archive/2026-10-probe-growth-census/results/probe_summary.csv"
SRC_TEST = ROOT / "experiments/archive/2026-10-kappa-rule-space/results/prefix_audit_predictions.csv"
SEED, NB, MINN, LAM = 20261020, 2000, 3, 1.0
rng = np.random.default_rng(SEED)

tr = (pl.read_csv(SRC_TRAIN).filter((pl.col("cls") == "blob") & (pl.col("g_k").abs() < .05) & (pl.col("kappa") > 0))
      .select("rule", y=pl.col("kappa").log()))
te = (pl.read_csv(SRC_TEST).filter((pl.col("cohort") == "stationary") & (pl.col("encoding") == "loo") & (pl.col("area") == "linear"))
      .select("rule", y="target").unique("rule", keep="first", maintain_order=True))  # ordered: unique() alone is hash order, and the seeded bootstrap indexes rows
rules_tr, y_tr = tr["rule"].to_list(), tr["y"].to_numpy()
rules_te, y_te = te["rule"].to_list(), te["y"].to_numpy()
overlap = len(set(rules_tr) & set(rules_te))
mu = y_tr.mean()


def base_feats(r):
    return [1.0 if len(r) >= j and r[j - 1] == "L" else 0.0 for j in range(2, 9)] + [1.0 if len(r) < 8 else 0.0]


def with_pairs(f):
    return f + [f[a] * f[b] for a, b in itertools.combinations(range(7), 2)]


def design(rules, pairs):
    return np.array([with_pairs(base_feats(r)) if pairs else base_feats(r) for r in rules], float)


def ridge(Xtr, y, Xte):
    m, s = Xtr.mean(0), Xtr.std(0)
    s[s == 0] = 1
    A, B = (Xtr - m) / s, (Xte - m) / s
    beta = np.linalg.solve(A.T @ A + LAM * np.eye(A.shape[1]), A.T @ (y - y.mean()))
    return B @ beta + y.mean()


def lookup(rules_te_):
    groups = {d: {} for d in range(1, 9)}
    for r, y in zip(rules_tr, y_tr):
        for d in groups:
            groups[d].setdefault(r[:d], []).append(y)
    out = []
    for r in rules_te_:
        v = mu
        for d in range(8, 0, -1):
            g = groups[d].get(r[:d], [])
            if len(g) >= MINN:
                v = float(np.mean(g))
                break
        out.append(v)
    return np.array(out)


def r2(y, p):
    return float(1 - ((y - p) ** 2).sum() / ((y - mu) ** 2).sum())


pred = {"A": ridge(design(rules_tr, False), y_tr, design(rules_te, False)),
        "A2": ridge(design(rules_tr, True), y_tr, design(rules_te, True)), "P8": lookup(rules_te)}
res = {k: r2(y_te, p) for k, p in pred.items()}
n = len(y_te)
ix = rng.integers(0, n, (NB, n))
boot = {k: np.array([r2(y_te[i], p[i]) for i in ix]) for k, p in pred.items()}
ci = {k: [float(q) for q in np.quantile(b, [.025, .975])] for k, b in boot.items()}
d_pa = [float(q) for q in np.quantile(boot["P8"] - boot["A"], [.025, .975])]
verdicts = {"B1 additive A < 0.40": res["A"] < .40, "B2 pairwise A2 >= 0.50": res["A2"] >= .50, "B3 P8 - A >= 0.15": res["P8"] - res["A"] >= .15}
lines = [f"# cmd: uv run experiments/archive/2026-10-kappa-prefix-additive/scripts/additive.py  seed {SEED}  bootstraps {NB}  ridge lambda {LAM}  (registered; README commit 32c0f82)",
         f"train {len(rules_tr)}, test {n}, overlap {overlap}; training mean ln kappa {mu:+.3f}"]
for k, label in (("A", "additive (7 position indicators)"), ("A2", "additive + 21 pairwise products"), ("P8", "8-letter lookup")):
    lines.append(f"{k:3s} {label:34s} R^2 {res[k]:+.3f}  95% CI [{ci[k][0]:+.3f}, {ci[k][1]:+.3f}]")
lines.append(f"P8 - A = {res['P8'] - res['A']:+.3f} [{d_pa[0]:+.3f}, {d_pa[1]:+.3f}]")
lines += [f"{k}: {'HELD' if v else 'FAILED'}" for k, v in verdicts.items()]
(EXP / "results").mkdir(exist_ok=True)
(EXP / "results/additive.txt").write_text("\n".join(lines) + "\n")
(EXP / "results/additive.json").write_text(json.dumps(dict(r2=res, ci=ci, p8_minus_a_ci=d_pa, verdicts=verdicts, n_train=len(rules_tr), n_test=n, overlap=overlap,
    input_sha256={p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (SRC_TRAIN, SRC_TEST)}), indent=2) + "\n")
print("\n".join(lines))
