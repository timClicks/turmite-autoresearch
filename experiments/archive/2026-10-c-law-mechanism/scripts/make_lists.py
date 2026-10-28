# /// script
# dependencies = ["polars", "numpy"]
# ///
"""Freeze the rule lists for Stage 2 (written before any tracer run).
Outputs results/lists/{sample.txt, valid_candidates.txt, band.txt, calib.txt}.
usage: uv run experiments/archive/2026-10-c-law-mechanism/scripts/make_lists.py"""
from pathlib import Path

import numpy as np
import polars as pl

root = Path(__file__).resolve().parents[4]
out = root / "experiments/archive/2026-10-c-law-mechanism/results/lists"
out.mkdir(exist_ok=True)
cen = pl.read_csv(root / "experiments/archive/2026-10-probe-growth-census/results/probe_summary.csv")
stat = cen.filter((pl.col("cls") == "blob") & (pl.col("c") > 0) & (pl.col("g_k").abs() < 0.05))
es = pl.read_csv(root / "experiments/archive/2026-10-edge-statistics/results/edgestats_sample.csv")
fresh = pl.read_csv(root / "experiments/archive/2026-10-kappa-leadrun-fresh/results/fresh_rules.csv")


def run0(r):
    k = 1
    while k < len(r) and r[k] == r[0]:
        k += 1
    return k


def primitive(x):
    n = len(x)
    return not any(n % p == 0 and x[:p] * (n // p) == x for p in range(1, n))


# 1. blank-board sample: the edgestats sample's stationary blob rules (profile baseline exists)
sample = [r for r in es["rule"].unique(maintain_order=True).to_list() if r in set(stat["rule"].to_list())]
(out / "sample.txt").write_text("\n".join(sample) + "\n")

# 2. validation candidates: random rules never simulated before (not in census, edgestats or fresh sets)
seen = set(cen["rule"].to_list()) | set(fresh["rule"].to_list()) | set(es["rule"].to_list())
rng = np.random.default_rng(20261020)
cand = []
while len(cand) < 600:
    n = int(rng.integers(11, 17))
    r = "".join(rng.choice(list("LR"), n))
    if r[0] != "R":                      # canonical: chirality-flip so that s_0 = R (the ant is mirror symmetric)
        r = r.translate(str.maketrans("LR", "RL"))
    if r in seen or r in cand or not primitive(r) or len(set(r)) < 2:
        continue
    cand.append(r)
(out / "valid_candidates.txt").write_text("\n".join(cand) + "\n")

# 3. flat-band rules: 12 per lead 1..5 from the census stationary blob, 10 <= n <= 14
rng = np.random.default_rng(20261019)
rules = stat.filter(pl.col("rule").str.len_chars().is_between(10, 14))["rule"].to_list()
band = []
for m in range(1, 6):
    pool = sorted(r for r in rules if run0(r) == m)
    pick = [pool[i] for i in rng.permutation(len(pool))[:12]]
    band += pick
    print(f"lead {m}: pool {len(pool)}, picked {len(pick)}")
(out / "band.txt").write_text("\n".join(band) + "\n")

# 4. calibration walkers
(out / "calib.txt").write_text("\n".join([f"rotor:{s}" for s in range(1, 33)] + [f"rw:{s}" for s in range(1, 33)]) + "\n")
print(len(sample), "sample;", len(cand), "valid candidates;", len(band), "band rules")
