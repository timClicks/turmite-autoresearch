# /// script
# dependencies = ["numpy"]
# ///
"""Stratified fresh sample for the leading-run test: 50 rules per leading-R-run length 1..6, split 25/25 over
rule lengths 13 and 14 (numpy default_rng(20261016 + 1)). Rule = R^k + 'L' + 13/14-k-1 uniform random letters,
so the leading run is exactly k. Excludes every rule in W3b, W3c and the census (census is length <= 12), rejects
non-primitive strings. 8 seeds 601..608 each. Writes results/rules.txt and results/specs.txt (RULE@SEED).
usage (repo root): uv run experiments/archive/2026-10-kappa-leadrun-fresh/scripts/sample.py"""
from pathlib import Path
import numpy as np
EXP = Path(__file__).resolve().parents[1]
KR = EXP.parents[2] / "experiments/archive/2026-10-kappa-rule-space" / "results"
rng = np.random.default_rng(20261016 + 1)

def primitive(s):
    n = len(s)
    return not any(n % d == 0 and s == s[:d] * (n // d) for d in range(1, n))

used = set((KR / "w3b_rules.txt").read_text().split()) | set((KR / "w3c_rules.txt").read_text().split())
rules = []
for k in range(1, 7):
    for n in (13, 14):
        seen = set()
        while len(seen) < 25:
            s = "R" * k + "L" + "".join("R" if b else "L" for b in rng.integers(0, 2, n - k - 1))
            if not primitive(s) or s in seen or s in used:
                continue
            seen.add(s)
        rules += sorted(seen)
assert len(set(rules)) == 300
(EXP / "results/rules.txt").write_text("\n".join(rules) + "\n")
(EXP / "results/specs.txt").write_text("\n".join(f"{r}@{sd}" for r in rules for sd in range(601, 609)) + "\n")
print(len(rules), "rules ->", 8 * len(rules), "runs")
