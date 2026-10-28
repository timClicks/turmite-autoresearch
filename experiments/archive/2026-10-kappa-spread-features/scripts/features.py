# /// script
# dependencies = ["numpy", "polars"]
# ///
"""Registered in ../README.md (predictions F1-F4, committed d5e0ff0 before this ran). Prefix vs suffix vs composition models of
ln kappa, trained on stationary census rules and tested on the fresh stationary rules of audit 12 / W3c.
usage (repo root): uv run experiments/archive/2026-10-kappa-spread-features/scripts/features.py"""
import hashlib
import json
from pathlib import Path
import re

import numpy as np
import polars as pl

ROOT = Path(__file__).resolve().parents[4]
EXP = Path(__file__).resolve().parents[1]
SRC_TRAIN = ROOT / "experiments/archive/2026-10-probe-growth-census/results/probe_summary.csv"
SRC_TEST = ROOT / "experiments/archive/2026-10-kappa-rule-space/results/prefix_audit_predictions.csv"
SEED, NB, P, MINN = 20261020, 2000, 8, 3
rng = np.random.default_rng(SEED)

tr = (pl.read_csv(SRC_TRAIN).filter((pl.col("cls") == "blob") & (pl.col("g_k").abs() < .05) & (pl.col("kappa") > 0))
      .select("rule", y=pl.col("kappa").log()))
te = (pl.read_csv(SRC_TEST).filter((pl.col("cohort") == "stationary") & (pl.col("encoding") == "loo") & (pl.col("area") == "linear"))
      .select("rule", y="target").unique("rule"))
overlap = len(set(tr["rule"]) & set(te["rule"]))
rules_tr, y_tr = tr["rule"].to_list(), tr["y"].to_numpy()
rules_te, y_te = te["rule"].to_list(), te["y"].to_numpy()
mu = y_tr.mean()


def lookup(key, depth_max=P):
    """Group-mean lookup on key(rule, depth); fall back to shorter keys with >= MINN training rules, then the training mean."""
    groups = {d: {} for d in range(1, depth_max + 1)}
    for r, y in zip(rules_tr, y_tr):
        for d in groups:
            groups[d].setdefault(key(r, d), []).append(y)

    def predict(r, exclude=None):
        for d in range(depth_max, 0, -1):
            g = groups[d].get(key(r, d), [])
            if exclude is not None:
                g = list(g)
                g.remove(exclude)
            if len(g) >= MINN:
                return float(np.mean(g))
        return float(mu)
    return predict


def comp(r):
    runs = re.findall(r"R+|L+", r)
    return [len(r), r.count("R"), len(runs), max([len(x) for x in runs if x[0] == "L"] or [0]), max(len(x) for x in runs if x[0] == "R")]


def ols(X, y):
    A = np.column_stack([np.ones(len(X)), X])
    beta = np.linalg.lstsq(A, y, rcond=None)[0]
    return lambda Z: np.column_stack([np.ones(len(Z)), Z]) @ beta


def r2(y, p):
    return float(1 - ((y - p) ** 2).sum() / ((y - mu) ** 2).sum())  # strict: against the TRAINING mean, as in W3c


p8 = lookup(lambda r, d: r[:d])
s8 = lookup(lambda r, d: r[-d:])
pred = {"P8": np.array([p8(r) for r in rules_te]), "S8": np.array([s8(r) for r in rules_te])}
Xtr, Xte = np.array([comp(r) for r in rules_tr], float), np.array([comp(r) for r in rules_te], float)
pred["C"] = ols(Xtr, y_tr)(Xte)
# P8+C: second-stage OLS on [leave-one-out P8 prediction on train, composition]
p8_loo = np.array([p8(r, exclude=y) for r, y in zip(rules_tr, y_tr)])
pred["P8+C"] = ols(np.column_stack([p8_loo, Xtr]), y_tr)(np.column_stack([pred["P8"], Xte]))

res = {k: r2(y_te, p) for k, p in pred.items()}
n = len(y_te)
ix = rng.integers(0, n, (NB, n))
boot = {k: np.array([r2(y_te[i], p[i]) for i in ix]) for k, p in pred.items()}
ci = {k: [float(q) for q in np.quantile(b, [.025, .975])] for k, b in boot.items()}
d_sp = boot["P8"] - boot["S8"]
d_pc = boot["P8+C"] - boot["P8"]
verdicts = {
    "F1 P8 within 0.1 of 0.633": abs(res["P8"] - .633) <= .1,
    "F2 S8 at least 0.2 below P8": res["P8"] - res["S8"] >= .2,
    "F3 C < 0.2": res["C"] < .2,
    "F4 P8+C improves on P8 by < 0.05": res["P8+C"] - res["P8"] < .05,
}
lines = [f"# cmd: uv run experiments/archive/2026-10-kappa-spread-features/scripts/features.py  seed {SEED}  bootstraps {NB}  (registered; README commit d5e0ff0)",
         f"train rules {len(rules_tr)} (stationary blob census), test rules {n} (fresh stationary); rules in both: {overlap}; training mean ln kappa {mu:+.3f}, test sd {y_te.std():.3f}"]
for k in ("P8", "S8", "C", "P8+C"):
    lines.append(f"{k:5s} strict held-out R^2 {res[k]:+.3f}  95% CI [{ci[k][0]:+.3f}, {ci[k][1]:+.3f}]")
lines.append(f"P8 - S8 = {res['P8'] - res['S8']:+.3f} CI [{np.quantile(d_sp, .025):+.3f}, {np.quantile(d_sp, .975):+.3f}];  (P8+C) - P8 = {res['P8+C'] - res['P8']:+.3f} CI [{np.quantile(d_pc, .025):+.3f}, {np.quantile(d_pc, .975):+.3f}]")
lines += [f"{k}: {'HELD' if v else 'FAILED'}" for k, v in verdicts.items()]
# POST HOC control (not registered): is the suffix lookup informative where lengths match? Leave-one-out inside the training set.
loo = {k: np.array([f(r, exclude=y) for r, y in zip(rules_tr, y_tr)]) for k, f in (("P8", p8), ("S8", s8))}
lens = np.array([len(r) for r in rules_tr])
res_loo = {k: float(1 - ((y_tr - v) ** 2).sum() / ((y_tr - y_tr.mean()) ** 2).sum()) for k, v in loo.items()}
lines.append(f"POST HOC (unregistered) leave-one-out R^2 inside the training set (n={len(rules_tr)}): P8 {res_loo['P8']:+.3f}, S8 {res_loo['S8']:+.3f}; "
             f"training rule lengths {int(lens.min())}-{int(lens.max())} (test 13-14)")
(EXP / "results").mkdir(exist_ok=True)
(EXP / "results/features.txt").write_text("\n".join(lines) + "\n")
(EXP / "results/features.json").write_text(json.dumps(dict(r2=res, ci=ci, verdicts=verdicts, n_train=len(rules_tr), n_test=n, overlap=overlap,
    input_sha256={p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (SRC_TRAIN, SRC_TEST)}), indent=2) + "\n")
print("\n".join(lines))
