# /// script
# dependencies = ["numpy"]
# ///
"""W3c fresh sample: 150 rules each of length 13 and 14 (numpy seed 20261014+23), excluding every W3b rule, uniform over strings starting with R,
rejecting all-R and non-primitive strings, 8 patched seeds 501..508 each. Writes results/w3c_specs.txt (RULE@SEED) and results/w3c_rules.txt.
usage (repo root): uv run experiments/archive/2026-10-kappa-rule-space/scripts/w3c_sample.py"""
from pathlib import Path
import numpy as np
EXP = Path(__file__).resolve().parents[1]
rng = np.random.default_rng(20261014 + 23)

def primitive(s):
    n = len(s)
    return not any(n % d == 0 and s == s[:d] * (n // d) for d in range(1, n))

rules = []
for n in (13, 14):
    seen = set(); w3b = {l.strip() for l in (EXP / "results" / "w3b_rules.txt").read_text().split()}
    while len(seen) < 150:
        s = "R" + "".join("R" if b else "L" for b in rng.integers(0, 2, n - 1))
        if s == "R" * n or not primitive(s) or s in seen or s in w3b:
            continue
        seen.add(s)
    rules += sorted(seen)
(EXP / "results" / "w3c_rules.txt").write_text("\n".join(rules) + "\n")
(EXP / "results" / "w3c_specs.txt").write_text("\n".join(f"{r}@{sd}" for r in rules for sd in range(501, 509)) + "\n")
print(len(rules), "rules ->", 8 * len(rules), "runs")
