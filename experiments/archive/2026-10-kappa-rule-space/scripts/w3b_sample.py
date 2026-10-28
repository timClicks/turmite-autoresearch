# /// script
# dependencies = ["numpy"]
# ///
"""W3b fresh sample: 75 rules each of length 13 and 14 (numpy seed 20261014+11), uniform over strings starting with R,
rejecting all-R and non-primitive strings, 8 patched seeds 201..208 each. Writes results/w3b_specs.txt (RULE@SEED) and results/w3b_rules.txt.
usage (repo root): uv run experiments/archive/2026-10-kappa-rule-space/scripts/w3b_sample.py"""
from pathlib import Path
import numpy as np
EXP = Path(__file__).resolve().parents[1]
rng = np.random.default_rng(20261014 + 11)

def primitive(s):
    n = len(s)
    return not any(n % d == 0 and s == s[:d] * (n // d) for d in range(1, n))

rules = []
for n in (13, 14):
    seen = set()
    while len(seen) < 75:
        s = "R" + "".join("R" if b else "L" for b in rng.integers(0, 2, n - 1))
        if s == "R" * n or not primitive(s) or s in seen:
            continue
        seen.add(s)
    rules += sorted(seen)
(EXP / "results" / "w3b_rules.txt").write_text("\n".join(rules) + "\n")
(EXP / "results" / "w3b_specs.txt").write_text("\n".join(f"{r}@{sd}" for r in rules for sd in range(201, 209)) + "\n")
print(len(rules), "rules ->", 8 * len(rules), "runs")
