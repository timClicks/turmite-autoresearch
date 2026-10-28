# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "polars"]
# ///
"""P4 (README Stage V2, V2-D): does radius-4 context add information about the next milestone beyond the M2 state?
Data: kernel-role runs re-run with FP_CTX4_ROWS (scratch/confirm_v2/pairs/*.ctx4.csv, bands 0 and 1). Train on kernel seeds 8001-8004,
validate on 8005-8008 (same rule). Per rule: held-out log-loss of 'next milestone is higher' under M2 (count floor 20, backoff
M2 -> M1 -> M0) and under M2 + radius-4 (floor 20, otherwise falls back to the M2 prediction).
DeltaLL = LL(M2) - LL(M2+r4) (positive = context helps). Tolerance per rule = 95th percentile of DeltaLL when radius-4 labels are
permuted among rows of the same M2 state (context irrelevant by construction), 40 permutations, seed 202610207000 + 2000 + rule index.
Rule (registered): UNINFORMATIVE if the median share of validation segments whose radius-4 state has training support >= 20 is < 0.30;
else PASS if DeltaLL <= tolerance for >= 80% of eligible rules, FAIL if it exceeds tolerance for > 20%.
Criterion 1 (predicted E[T] changes < 10% when context is added) is vacuous in-sample (maximum-likelihood identity) and is reported as such.
    uv run experiments/archive/2026-10-kappa-first-passage/scripts/p4_test.py
"""
import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
EXP = HERE.parent
R = EXP / "results"
V2 = EXP / "scratch" / "confirm_v2" / "pairs"
FLOOR = 20
TRAIN, VAL = list(range(202610208001, 202610208005)), list(range(202610208005, 202610208009))
man = json.loads((R / "confirm_manifest.json").read_text())
elig = pl.read_csv(R / "confirm_predictions.csv")["rule"].to_list()
M2 = ["m", "dir", "heading", "phase", "patch", "hist"]


def load(rule: str, seeds: list[int]) -> pl.DataFrame:
    parts = []
    for s in seeds:
        d = pl.read_csv(V2 / f"{rule}_{s}.ctx4.csv", schema_overrides={"r4": pl.UInt64}).filter(pl.col("band") <= 1)
        parts.append(d.drop("spec", "band").group_by(M2 + ["r4"]).agg(pl.col("n").sum(), pl.col("up").sum()))
    return pl.concat(parts).group_by(M2 + ["r4"]).agg(pl.col("n").sum(), pl.col("up").sum())


def keys(df: pl.DataFrame, lvl: int):
    cols = {0: ["m", "dir"], 1: ["m", "dir", "heading", "phase"], 2: M2}[lvl]
    return cols


def m2_prob(train: pl.DataFrame, val: pl.DataFrame) -> np.ndarray:
    """Smoothed P(up) per validation row with backoff M2 -> M1 -> M0 at count floor."""
    p = np.full(val.height, np.nan)
    for lvl in (2, 1, 0):
        cols = keys(train, lvl)
        st = train.group_by(cols).agg(pl.col("n").sum().alias("N"), pl.col("up").sum().alias("U")).filter(pl.col("N") >= FLOOR)
        j = val.select(cols).join(st, on=cols, how="left", maintain_order="left")
        q = ((j["U"] + 0.5) / (j["N"] + 1.0)).to_numpy().astype(float)
        p = np.where(np.isnan(p) & np.isfinite(q), q, p)
    return np.where(np.isnan(p), 0.5, p)


def r4_prob(train: pl.DataFrame, val: pl.DataFrame, pm2: np.ndarray):
    cols = M2 + ["r4"]
    st = train.filter(pl.col("r4") != 0).group_by(cols).agg(pl.col("n").sum().alias("N"), pl.col("up").sum().alias("U")).filter(pl.col("N") >= FLOOR)
    j = val.select(cols).join(st, on=cols, how="left", maintain_order="left")
    q = ((j["U"] + 0.5) / (j["N"] + 1.0)).to_numpy().astype(float)
    supported = np.isfinite(q) & (val["r4"].to_numpy() != 0)
    return np.where(supported, q, pm2), supported


def ll(p, n, up):
    p = np.clip(p, 1e-9, 1 - 1e-9)
    return float(-(up * np.log(p) + (n - up) * np.log(1 - p)).sum() / n.sum())


rows = []
for i, rule in enumerate(elig):
    tr, va = load(rule, TRAIN), load(rule, VAL)
    n, up = va["n"].to_numpy().astype(float), va["up"].to_numpy().astype(float)
    pm2 = m2_prob(tr, va)
    pr4, sup = r4_prob(tr, va, pm2)
    dll = ll(pm2, n, up) - ll(pr4, n, up)
    share = float(n[sup].sum() / n.sum())
    rng = np.random.default_rng(202610207000 + 2000 + i)
    nulls = []
    for _ in range(40):
        # permute r4 labels among training rows of the same M2 state
        perm = tr.with_columns(pl.col("r4").shuffle(seed=int(rng.integers(0, 2**31))).over(M2))
        pr4n, _ = r4_prob(perm, va, pm2)
        nulls.append(ll(pm2, n, up) - ll(pr4n, n, up))
    tol = float(np.quantile(nulls, 0.95))
    rows.append(dict(rule=rule, delta_ll=dll, tolerance=tol, supported_share=share, exceeds=bool(dll > tol), ll_m2=ll(pm2, n, up),
                     n_val_segments=float(n.sum()), folded_share=float(n[va["r4"].to_numpy() == 0].sum() / n.sum())))
share_med = float(np.median([r["supported_share"] for r in rows]))
frac_exceed = float(np.mean([r["exceeds"] for r in rows]))
if share_med < 0.30:
    verdict = "UNINFORMATIVE (median supported share below 0.30)"
elif frac_exceed <= 0.20:
    verdict = "PASS"
else:
    verdict = "FAIL"
out = dict(n_rules=len(rows), median_supported_share=share_med, frac_rules_context_helps_beyond_tolerance=frac_exceed,
           median_delta_ll=float(np.median([r["delta_ll"] for r in rows])), median_tolerance=float(np.median([r["tolerance"] for r in rows])),
           criterion1="vacuous in-sample (identity): predicted E[T] is the empirical mean for any partition", verdict=verdict, rows=rows)
(R / "p4_test.json").write_text(json.dumps(out, indent=2, default=float))
print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=2))
