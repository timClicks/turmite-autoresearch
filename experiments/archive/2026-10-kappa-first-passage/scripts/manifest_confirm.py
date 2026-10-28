# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "polars"]
# ///
"""Freeze the confirmation cohort (README stage 3). Run once, before any confirmation outcome exists.

Eligible: blob rules of length >= 6 in the committed probe census, in families (first six letters) that
are NOT pilot families. Strata (pre-labelled from the committed census, never from this experiment):
stationary = |g_k| < 0.05, drifting otherwise. Selection ignores kappa, tail length and success:
seeded shuffle of the non-pilot families, first 12; within each family 2 rules per stratum drawn by
the seeded rng (if a stratum has fewer, the other stratum fills and the shortfall is recorded).
Folds: the 12 families are split into 4 folds of 3 by a seeded shuffle; folds always hold whole families.
Seeds: kernel 202610208001..8, outcome 202610209001..8 per rule (README).
    uv run experiments/archive/2026-10-kappa-first-passage/scripts/manifest_confirm.py
"""
import hashlib
import json
import subprocess
from pathlib import Path

import numpy as np
import polars as pl

ROOT = Path(__file__).resolve().parents[4]
EXP = Path(__file__).resolve().parents[1]
SRC = ROOT / "experiments/archive/2026-10-probe-growth-census/results/probe_summary.csv"
SEL_SEED, FOLD_SEED = 202610207097, 202610207096
KSEEDS = [202610208001 + i for i in range(8)]
OSEEDS = [202610209001 + i for i in range(8)]
NFAM, PER_STRATUM = 12, 2

pilot = {f["family"] for f in json.loads((EXP / "results/pilot_manifest.json").read_text())["families"]}
df = pl.read_csv(SRC).filter((pl.col("cls") == "blob") & (pl.col("rule").str.len_chars() >= 6))
df = df.with_columns(stratum=pl.when(pl.col("g_k").abs() < 0.05).then(pl.lit("stationary")).otherwise(pl.lit("drifting")))
rows = sorted(zip(df["rule"].to_list(), df["stratum"].to_list()))
fams: dict = {}
for r, s in rows:
    if r[:6] not in pilot:
        fams.setdefault(r[:6], {"stationary": [], "drifting": []})[s].append(r)
names = sorted(fams)
rng = np.random.default_rng(SEL_SEED)
order = [names[i] for i in rng.permutation(len(names))][:NFAM]
cohort, shortfalls = [], []
for f in order:
    picked = []
    for s, other in (("stationary", "drifting"), ("drifting", "stationary")):
        pool = sorted(set(fams[f][s]))
        take = [pool[i] for i in rng.permutation(len(pool))[:PER_STRATUM]]
        picked += [(r, s) for r in take]
        if len(take) < PER_STRATUM:
            shortfalls.append(dict(family=f, stratum=s, missing=PER_STRATUM - len(take)))
    while len(picked) < 2 * PER_STRATUM:  # fill from whichever stratum has unpicked rules
        left = sorted(r for s in ("stationary", "drifting") for r in fams[f][s] if r not in {p[0] for p in picked})
        r = left[int(rng.integers(len(left)))]
        picked.append((r, "stationary" if r in fams[f]["stationary"] else "drifting"))
    cohort += [(f, r, s) for r, s in picked]
frng = np.random.default_rng(FOLD_SEED)
fam_order = [order[i] for i in frng.permutation(len(order))]
fold_of = {f: i // 3 for i, f in enumerate(fam_order)}
specs = []
for f, r, s in cohort:
    for role, seeds in (("kernel", KSEEDS), ("outcome", OSEEDS)):
        specs += [dict(spec=f"{r}@{sd}", rule=r, family=f, stratum=s, fold=fold_of[f], role=role, seed=sd) for sd in seeds]
man = dict(
    purpose="confirmation cohort, frozen before any confirmation run",
    source=str(SRC.relative_to(ROOT)), source_sha256=hashlib.sha256(SRC.read_bytes()).hexdigest(),
    pilot_families_excluded=sorted(pilot), n_candidate_families=len(names), selection_seed=SEL_SEED, fold_seed=FOLD_SEED,
    families=order, folds={str(k): [f for f in order if fold_of[f] == k] for k in range(4)},
    shortfalls=shortfalls, n_rules=len(cohort), n_specs=len(specs),
    strata_counts={s: sum(1 for _, _, x in cohort if x == s) for s in ("stationary", "drifting")},
    rules=[dict(family=f, rule=r, stratum=s, fold=fold_of[f]) for f, r, s in cohort],
    kernel_seeds=KSEEDS, outcome_seeds=OSEEDS,
    git=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
)
res = EXP / "results"
(res / "confirm_manifest.json").write_text(json.dumps(man, indent=2))
pl.DataFrame(specs).write_csv(res / "confirm_roles.csv")
(res / "confirm_specs.txt").write_text("\n".join(s["spec"] for s in specs) + "\n")
print(json.dumps({k: v for k, v in man.items() if k != "rules"}, indent=2))
