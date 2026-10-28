# /// script
# dependencies = ["numpy"]
# ///
"""B3: random rules of length 10,12 (controls),14,16,20,24; 200 each; uniform over strings starting with R; seed 20261013.
Writes experiments/archive/2026-10-b3-long-rules/results/b3_rules.txt. usage: uv run experiments/archive/2026-10-b3-long-rules/scripts/b3_sample.py"""
import numpy as np
rng = np.random.default_rng(20261013)
def primitive(s):
    n = len(s)
    return not any(n % p == 0 and s[:p] * (n // p) == s for p in range(1, n))
out = []
for n in (10, 12, 14, 16, 20, 24):
    got = set()
    while len(got) < 200:
        s = "R" + "".join("RL"[b] for b in rng.integers(0, 2, n - 1))
        if "L" in s and primitive(s): got.add(s)
    out += sorted(got)
open("experiments/archive/2026-10-b3-long-rules/results/b3_rules.txt", "w").write("\n".join(out) + "\n")
print(len(out), "rules")
