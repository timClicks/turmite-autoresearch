# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "scipy", "polars"]
# ///
"""P3 (README Stage V2, V2-C): the only frozen-model form of unseen-family transfer: a rule-independent pooled chain per training fold
(turn-class states), applied to the held-out fold. Same definitions as analyze.py's P3 block (R2 against the leave-fold-out training mean of
band-2 B/S, pooled out-of-fold, family bootstrap seed 202610207099), run to completion with the checked iterative solver. Verdict
(registered): UNINFORMATIVE, since the model carries no rule-conditional input; the numbers are reported with it.
    uv run experiments/archive/2026-10-kappa-first-passage/scripts/p3_pooled.py
Per-rule kernel aggregates are cached in scratch/p3_cache (regenerated from scratch/confirm/pairs, which confirm.sh regenerates).
"""
import json
import sys
import time
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import fpkernel  # noqa: E402
import load_runs  # noqa: E402

EXP = HERE.parent
R = EXP / "results"
PAIRS = EXP / "scratch" / "confirm" / "pairs"
CACHE = EXP / "scratch" / "p3_cache"
CACHE.mkdir(parents=True, exist_ok=True)
KEYS = fpkernel.KEYS + fpkernel.NEXT
FLOOR, BOOT, BOOT_SEED = 20, 2000, 202610207099

pred = pl.read_csv(R / "confirm_predictions.csv")
man = json.loads((R / "confirm_manifest.json").read_text())
meta = {r["rule"]: r for r in man["rules"]}
roles = pl.read_csv(R / "confirm_roles.csv")
runs = load_runs.runs(R / "confirm").join(roles.select("spec", "role"), on="spec", how="left")
t0 = time.time()


def rule_kernel(rule: str) -> pl.DataFrame:
    f = CACHE / f"{rule}.parquet"
    if f.exists():
        return pl.read_parquet(f)
    k = runs.filter((pl.col("rule") == rule) & (pl.col("role") == "kernel") & (pl.col("band") <= 1) & (pl.col("reached_hi") == 1))
    specs = sorted(set(k.group_by("spec").len().filter(pl.col("len") == 2)["spec"]))
    parts = []
    for s in specs:
        d = pl.read_csv(PAIRS / (s.replace("@", "_") + ".pairs.csv"), null_values="NA").filter(pl.col("band") <= 1)
        parts.append(d.drop("spec").group_by(KEYS).agg(pl.col("n").sum(), pl.col("time").sum(), pl.col("skipped").sum(), pl.col("jumps").sum(), pl.col("revisits").sum()))
    agg = pl.concat(parts).group_by(KEYS).agg(pl.all().sum()).with_columns(pl.lit(0).alias("band"))
    agg.write_parquet(f)
    return agg


rules = pred["rule"].to_list()
fold = {r: meta[r]["fold"] for r in rules}
fams = np.array([meta[r]["family"] for r in rules])
y = pred["obs_BS"].to_numpy()
trmean = np.array([float(pred.filter(pl.col("fold") != fold[r])["obs_BS"].mean()) for r in rules])
cache = {r: rule_kernel(r) for r in rules}
print("kernels cached", round(time.time() - t0, 1), "s", flush=True)

pooled = {}
for fo in sorted(set(fold.values())):
    agg = pl.concat([cache[r] for r in rules if fold[r] != fo]).group_by(KEYS).agg(pl.all().sum()).with_columns(pl.lit(0).alias("band"))
    pooled[fo] = {}
    for lvl in (0, 1, 2):
        f = fpkernel.fit(agg, level=lvl, floor=FLOOR)
        pooled[fo][lvl] = dict(pred_BS=f.get("pred_BS"), n_states=f.get("n_states"), status=f["status"], ET=f.get("ET"), ED=f.get("ED"))
        print("fold", fo, "level", lvl, f["status"], f.get("n_states"), f.get("pred_BS"), round(time.time() - t0, 1), "s", flush=True)

pr = {lvl: np.array([pooled[fold[r]][lvl]["pred_BS"] for r in rules], float) for lvl in (0, 1, 2)}
r2 = lambda p, idx: 1 - ((y[idx] - p[idx]) ** 2).sum() / ((y[idx] - trmean[idx]) ** 2).sum()
allidx = np.arange(len(y))
uf = sorted(set(fams))
rng = np.random.default_rng(BOOT_SEED)


def boot(stat):
    v = []
    for _ in range(BOOT):
        pick = rng.integers(0, len(uf), len(uf))
        idx = np.concatenate([np.flatnonzero(fams == uf[i]) for i in pick])
        v.append(stat(idx))
    return [float(np.quantile(v, 0.025)), float(np.quantile(v, 0.975))]


out = dict(form="rule-independent pooled chain per training fold (turn-class states); constant per fold; no rule-conditional input",
           n_rules=len(rules), pooled=pooled,
           r2={f"M{l}": float(r2(pr[l], allidx)) for l in (0, 1, 2)},
           gain_M2_over_M0=float(r2(pr[2], allidx) - r2(pr[0], allidx)),
           gain_ci95_family_bootstrap=boot(lambda idx: r2(pr[2], idx) - r2(pr[0], idx)),
           r2_M2_ci95_family_bootstrap=boot(lambda idx: r2(pr[2], idx)),
           verdict="UNINFORMATIVE (registered): the model predicts one constant per fold and has no rule-conditional input, so it cannot test transfer to unseen families",
           seconds=time.time() - t0)
(R / "p3_pooled.json").write_text(json.dumps(out, indent=2, default=float))
print(json.dumps({k: v for k, v in out.items() if k != "pooled"}, indent=2))
