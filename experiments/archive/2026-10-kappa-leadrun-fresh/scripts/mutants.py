# /// script
# dependencies = ["numpy", "polars"]
# ///
"""Part B sampler (../README.md, registered before any mutant run): single-letter mutants of the fresh stationary rules
with lead 1..5. arm E flips index k (L->R, extends the lead), arm S flips index k-1 (R->L, k>=2, shortens it),
arm C flips a random L at index >= 8 to R (control: lead unchanged). numpy default_rng(20261016 + 2).
Writes results/mutants.csv and results/mutant_specs.txt (RULE@SEED, seeds 601..608, same as the base runs).
usage (repo root): uv run experiments/archive/2026-10-kappa-leadrun-fresh/scripts/mutants.py"""
from pathlib import Path
import numpy as np, polars as pl

EXP = Path(__file__).resolve().parents[1]
rng = np.random.default_rng(20261016 + 2)
lead = lambda s: len(s) - len(s.lstrip(s[0]))


def primitive(s):
    n = len(s)
    return not any(n % d == 0 and s == s[:d] * (n // d) for d in range(1, n))


def flip(s, i):
    return s[:i] + ("R" if s[i] == "L" else "L") + s[i + 1:]


fresh = pl.read_csv(EXP / "results/fresh_rules.csv").filter(pl.col("stationary") & (pl.col("lead") <= 5)).sort("rule")
sampled = set((EXP / "results/rules.txt").read_text().split())
rows, seen = [], set()
for base, k in zip(fresh["rule"], fresh["lead"]):
    cand = [("E", k)]
    if k >= 2:
        cand.append(("S", k - 1))
    late = [i for i in range(8, len(base)) if base[i] == "L"]
    if late:
        cand.append(("C", int(rng.choice(late))))
    for arm, i in cand:
        m = flip(base, i)
        if not primitive(m) or m in seen:
            continue
        seen.add(m)
        rows.append(dict(mutant=m, base=base, arm=arm, idx=i, base_lead=int(k), new_lead=lead(m), in_base_sample=m in sampled))
df = pl.DataFrame(rows)
df.write_csv(EXP / "results/mutants.csv")
(EXP / "results/mutant_specs.txt").write_text("\n".join(f"{r}@{sd}" for r in df["mutant"] for sd in range(601, 609)) + "\n")
print(df.group_by("arm").agg(n=pl.len(), mean_dlead=(pl.col("new_lead") - pl.col("base_lead")).mean()).sort("arm"))
print(len(df), "mutants ->", 8 * len(df), "runs;", int(df["in_base_sample"].sum()), "coincide with base-sample rules")
