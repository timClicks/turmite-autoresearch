# /// script
# dependencies = ["numpy", "polars"]
# ///
"""W6 pilot sample (registered in README, 'W6 pilot addendum'): 40 stationary pool bases (n=10/11/12 -> 12/14/14, numpy seed 20261014+21),
all single-letter mutants at positions 1..n-1 (canonicalised, primitive, deduplicated), plus the bases, seeds 401..406.
Writes results/w6_pairs.csv (base, pos, mutant), results/w6_specs.txt.
usage (repo root): uv run experiments/archive/2026-10-kappa-rule-space/scripts/w6_sample.py"""
from pathlib import Path
import numpy as np, polars as pl
EXP = Path(__file__).resolve().parents[1]
rng = np.random.default_rng(20261014 + 21)
pool = pl.read_csv(EXP / "results" / "rules_pool.csv").filter(pl.col("g_k").abs() < 0.05).sort("base")

def primitive(s):
    n = len(s)
    return not any(n % d == 0 and s == s[:d] * (n // d) for d in range(1, n))

def canon(s):
    return s if s[0] == "R" else s.translate(str.maketrans("LR", "RL"))

bases = []
for n, k in ((10, 12), (11, 14), (12, 14)):
    cand = pool.filter(pl.col("n") == n)["base"].to_list()
    bases += sorted(rng.choice(cand, size=k, replace=False).tolist())
pairs = []
for b in bases:
    for j in range(1, len(b)):
        m = canon(b[:j] + ("L" if b[j] == "R" else "R") + b[j + 1:])
        if m == b or m == "R" * len(b) or m == "L" * len(b) or not primitive(m):
            continue
        pairs.append((b, j, m))
pl.DataFrame(pairs, schema=["base", "pos", "mutant"], orient="row").write_csv(EXP / "results" / "w6_pairs.csv")
rules = sorted(set(bases) | {m for _, _, m in pairs})
(EXP / "results" / "w6_specs.txt").write_text("\n".join(f"{r}@{s}" for r in rules for s in range(401, 407)) + "\n")
print(len(bases), "bases,", len(pairs), "pairs,", len(rules), "distinct rules,", 6 * len(rules), "runs")
