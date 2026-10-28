# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "polars"]
# ///
"""Freeze the feasibility-pilot manifest (README stage 2).

Eligible: blob rules of length >= 6 in the committed probe census; family = first six letters.
Selection never looks at kappa, drift, tail length or success: a seeded shuffle of the distinct
families, one seeded-random rule per family, the first 8 families. Starts (seeds) are fixed by the
README: 202610207001..202610207004.
    uv run experiments/archive/2026-10-kappa-first-passage/scripts/manifest_pilot.py
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
SEED = 202610207098
NFAM, SEEDS = 8, [202610207001 + i for i in range(4)]

df = pl.read_csv(SRC).filter((pl.col("cls") == "blob") & (pl.col("rule").str.len_chars() >= 6))
rules = sorted(df["rule"].to_list())
fams = {}
for r in rules:
    fams.setdefault(r[:6], []).append(r)
names = sorted(fams)
rng = np.random.default_rng(SEED)
order = [names[i] for i in rng.permutation(len(names))]
chosen = []
for f in order[:NFAM]:
    members = fams[f]
    chosen.append((f, members[int(rng.integers(len(members)))], len(members)))
specs = [f"{r}@{s}" for _, r, _ in chosen for s in SEEDS]
man = dict(
    purpose="feasibility pilot only: no ant-outcome model selection",
    source=str(SRC.relative_to(ROOT)), source_sha256=hashlib.sha256(SRC.read_bytes()).hexdigest(),
    eligibility="cls == blob and len(rule) >= 6; family = first six letters", n_eligible_rules=len(rules), n_families=len(names),
    shuffle_seed=SEED, families=[dict(family=f, rule=r, family_size=n) for f, r, n in chosen], start_seeds=SEEDS, specs=specs,
    git=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
)
(EXP / "results").mkdir(exist_ok=True)
(EXP / "results" / "pilot_manifest.json").write_text(json.dumps(man, indent=2))
(EXP / "results" / "pilot_specs.txt").write_text("\n".join(specs) + "\n")
print(json.dumps(man, indent=2))
