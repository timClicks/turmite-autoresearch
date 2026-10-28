# /// script
# dependencies = ["numpy", "polars"]
# ///
"""Registered in ../README.md (A1-A4, committed 593d127 before this ran): per-position ablation of the 8-letter prefix lookup.
usage (repo root): uv run experiments/archive/2026-10-kappa-prefix-ablation/scripts/ablate.py"""
import hashlib
import json
from pathlib import Path

import numpy as np
import polars as pl

ROOT = Path(__file__).resolve().parents[4]
EXP = Path(__file__).resolve().parents[1]
SRC_TRAIN = ROOT / "experiments/archive/2026-10-probe-growth-census/results/probe_summary.csv"
SRC_TEST = ROOT / "experiments/archive/2026-10-kappa-rule-space/results/prefix_audit_predictions.csv"
SEED, NB, NPERM, MINN, P = 20261020, 2000, 200, 3, 8
rng = np.random.default_rng(SEED)

tr = (pl.read_csv(SRC_TRAIN).filter((pl.col("cls") == "blob") & (pl.col("g_k").abs() < .05) & (pl.col("kappa") > 0))
      .select("rule", y=pl.col("kappa").log()))
te = (pl.read_csv(SRC_TEST).filter((pl.col("cohort") == "stationary") & (pl.col("encoding") == "loo") & (pl.col("area") == "linear"))
      .select("rule", y="target").unique("rule"))
rules_tr, y_tr = tr["rule"].to_list(), tr["y"].to_numpy()
rules_te, y_te = te["rule"].to_list(), te["y"].to_numpy()
overlap = len(set(rules_tr) & set(rules_te))
mu = y_tr.mean()


def key(r, d, mask):
    s = r[:d]
    return s if mask is None or mask > len(s) else s[:mask - 1] + "*" + s[mask:]


def predict_all(train_rules, test_rules, mask=None):
    groups = {d: {} for d in range(1, P + 1)}
    for r, y in zip(train_rules, y_tr):
        for d in groups:
            groups[d].setdefault(key(r, d, mask), []).append(y)
    out = []
    for r in test_rules:
        v = mu
        for d in range(P, 0, -1):
            g = groups[d].get(key(r, d, mask), [])
            if len(g) >= MINN:
                v = float(np.mean(g))
                break
        out.append(v)
    return np.array(out)


def r2(y, p):
    return float(1 - ((y - p) ** 2).sum() / ((y - mu) ** 2).sum())


base = predict_all(rules_tr, rules_te)
r2_base = r2(y_te, base)
n = len(y_te)
ix = rng.integers(0, n, (NB, n))
res = {}
for j in range(1, P + 1):
    p = predict_all(rules_tr, rules_te, mask=j)
    loss = r2_base - r2(y_te, p)
    bl = np.array([r2(y_te[i], base[i]) - r2(y_te[i], p[i]) for i in ix])
    ctrl = []
    for _ in range(NPERM):
        perm = list(rules_tr)
        idx = [k for k, r in enumerate(perm) if len(r) >= j]
        letters = [perm[k][j - 1] for k in idx]
        rng.shuffle(letters)
        for k, ch in zip(idx, letters):
            perm[k] = perm[k][:j - 1] + ch + perm[k][j:]
        ctrl.append(r2(y_te, predict_all(perm, rules_te)))
    res[j] = dict(r2_ablated=r2(y_te, p), loss=loss, loss_ci=[float(q) for q in np.quantile(bl, [.025, .975])],
                  control_r2=float(np.mean(ctrl)), control_loss=r2_base - float(np.mean(ctrl)))
early = max(res[j]["loss"] for j in (2, 3, 4))
verdicts = {"A1 position 1 loss within 0.01 of 0": abs(res[1]["loss"]) <= .01,
            "A2 positions 2,3,4 each loss >= 0.05": all(res[j]["loss"] >= .05 for j in (2, 3, 4)),
            "A3 no position 5-8 loss above max of 2-4": all(res[j]["loss"] <= early for j in (5, 6, 7, 8)),
            "A4 control loss >= masking loss - 0.05 at every position": all(res[j]["control_loss"] >= res[j]["loss"] - .05 for j in res)}
lines = [f"# cmd: uv run experiments/archive/2026-10-kappa-prefix-ablation/scripts/ablate.py  seed {SEED}  bootstraps {NB}  permutations {NPERM}  (registered; README commit 593d127)",
         f"train {len(rules_tr)}, test {n}, overlap {overlap}; P8 held-out R^2 {r2_base:+.3f}",
         "pos  R^2 ablated   loss [95% CI]             control R^2 (permuted)  control loss"]
for j, r in res.items():
    lines.append(f"{j:3d}  {r['r2_ablated']:+.3f}      {r['loss']:+.3f} [{r['loss_ci'][0]:+.3f}, {r['loss_ci'][1]:+.3f}]   {r['control_r2']:+.3f}            {r['control_loss']:+.3f}")
lines += [f"{k}: {'HELD' if v else 'FAILED'}" for k, v in verdicts.items()]
(EXP / "results").mkdir(exist_ok=True)
(EXP / "results/ablate.txt").write_text("\n".join(lines) + "\n")
(EXP / "results/ablate.json").write_text(json.dumps(dict(r2_base=r2_base, positions=res, verdicts=verdicts, n_train=len(rules_tr), n_test=n, overlap=overlap,
    input_sha256={p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (SRC_TRAIN, SRC_TEST)}), indent=2) + "\n")
print("\n".join(lines))
