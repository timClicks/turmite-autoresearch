# /// script
# dependencies = ["numpy", "polars"]
# ///
"""Registered in ../README.md (H1-H4, committed 17ad529 before this ran): run-structure keys of the rule opening vs the 8-letter prefix.
usage (repo root): uv run experiments/archive/2026-10-kappa-prefix-runs/scripts/runs.py"""
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
SEED, NB, MINN = 20261020, 2000, 3
rng = np.random.default_rng(SEED)

tr = (pl.read_csv(SRC_TRAIN).filter((pl.col("cls") == "blob") & (pl.col("g_k").abs() < .05) & (pl.col("kappa") > 0))
      .select("rule", y=pl.col("kappa").log()))
te = (pl.read_csv(SRC_TEST).filter((pl.col("cohort") == "stationary") & (pl.col("encoding") == "loo") & (pl.col("area") == "linear"))
      .select("rule", y="target").unique("rule"))
rules_tr, y_tr = tr["rule"].to_list(), tr["y"].to_numpy()
rules_te, y_te = te["rule"].to_list(), te["y"].to_numpy()
overlap = len(set(rules_tr) & set(rules_te))
mu = y_tr.mean()


def runs(r):
    return tuple(len(list(g)) for _, g in itertools.groupby(r))


def lookup(key, depth_max):
    groups = {d: {} for d in range(1, depth_max + 1)}
    for r, y in zip(rules_tr, y_tr):
        for d in groups:
            groups[d].setdefault(key(r, d), []).append(y)

    def predict(r):
        for d in range(depth_max, 0, -1):
            g = groups[d].get(key(r, d), [])
            if len(g) >= MINN:
                return float(np.mean(g))
        return float(mu)
    return predict


def r2(y, p):
    return float(1 - ((y - p) ** 2).sum() / ((y - mu) ** 2).sum())


models = {"P8": lookup(lambda r, d: r[:d], 8)}
for k in (1, 2, 3, 4):
    # key = lengths of the first d runs (d <= k); a rule with fewer than d runs shares its full run tuple
    models[f"R{k}"] = lookup(lambda r, d: runs(r)[:d], k)
pred = {m: np.array([f(r) for r in rules_te]) for m, f in models.items()}
res = {m: r2(y_te, p) for m, p in pred.items()}
n = len(y_te)
ix = rng.integers(0, n, (NB, n))
boot = {m: np.array([r2(y_te[i], p[i]) for i in ix]) for m, p in pred.items()}
ci = {m: [float(q) for q in np.quantile(b, [.025, .975])] for m, b in boot.items()}
dd = {m: [float(q) for q in np.quantile(boot[m] - boot["P8"], [.025, .975])] for m in ("R1", "R2", "R3", "R4")}
verdicts = {"H1 R1 >= 0.15": res["R1"] >= .15, "H2 R2 >= 0.40": res["R2"] >= .40,
            "H3 R3 within 0.10 of P8": res["P8"] - res["R3"] <= .10, "H4 no Rk exceeds P8 by > 0.05": all(res[f"R{k}"] - res["P8"] <= .05 for k in (1, 2, 3, 4))}
lines = [f"# cmd: uv run experiments/archive/2026-10-kappa-prefix-runs/scripts/runs.py  seed {SEED}  bootstraps {NB}  (registered; README commit 17ad529)",
         f"train {len(rules_tr)}, test {n}, overlap {overlap}; training mean ln kappa {mu:+.3f}"]
for m in ("P8", "R1", "R2", "R3", "R4"):
    extra = "" if m == "P8" else f"  vs P8 {res[m] - res['P8']:+.3f} [{dd[m][0]:+.3f}, {dd[m][1]:+.3f}]"
    lines.append(f"{m:3s} R^2 {res[m]:+.3f}  95% CI [{ci[m][0]:+.3f}, {ci[m][1]:+.3f}]{extra}")
lines += [f"{k}: {'HELD' if v else 'FAILED'}" for k, v in verdicts.items()]
(EXP / "results").mkdir(exist_ok=True)
(EXP / "results/runs.txt").write_text("\n".join(lines) + "\n")
(EXP / "results/runs.json").write_text(json.dumps(dict(r2=res, ci=ci, delta_vs_p8_ci=dd, verdicts=verdicts, n_train=len(rules_tr), n_test=n, overlap=overlap,
    input_sha256={p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (SRC_TRAIN, SRC_TEST)}), indent=2) + "\n")
print("\n".join(lines))
