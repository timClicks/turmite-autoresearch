# /// script
# dependencies = ["polars", "numpy"]
# ///
"""Item 4 rule selection: 12 primitive core-blob rules stratified over rule length (3..12)
and over the census width exponent (low/mid/high), numpy seed 20261012. Writes experiments/archive/2026-10-item4-exponent-rotor-calibrated/results/item4_rules.txt
and experiments/archive/2026-10-item4-exponent-rotor-calibrated/results/item4_walkers.txt (RULE@SEED, seeds 1..24)."""
import numpy as np, polars as pl
d = pl.read_csv("experiments/archive/2026-10-probe-growth-census/results/probe_summary.csv").filter((pl.col("cls") == "blob") & (pl.col("alpha_w") > 0.30) & (pl.col("alpha_w") < 0.37))
def root(s):
    n = len(s)
    for p in range(1, n):
        if n % p == 0 and s[:p] * (n // p) == s: return s[:p]
    return s
d = d.filter(pl.col("rule").map_elements(lambda s: root(s) == s, return_dtype=pl.Boolean))
rng = np.random.default_rng(20261012)
picked = ["RLR", "RLL"]  # shortest chaotic rules, definitely included
for n in (5, 6, 7, 8, 9, 10, 11, 12):
    g = d.filter(pl.col("n") == n).sort("alpha_w")
    q = len(picked) % 3  # cycle low / mid / high alpha
    i = int([0.1, 0.5, 0.9][q] * (g.height - 1))
    picked.append(g["rule"][i])
picked += list(d.filter(pl.col("n").is_in([3, 4])).sample(2, seed=1)["rule"])
picked = list(dict.fromkeys(picked))[:12]
print(picked)
open("experiments/archive/2026-10-item4-exponent-rotor-calibrated/results/item4_rules.txt", "w").write("\n".join(picked) + "\n")
open("experiments/archive/2026-10-item4-exponent-rotor-calibrated/results/item4_walkers.txt", "w").write("\n".join(f"{r}@{s}" for r in picked for s in range(1, 25)) + "\n")
print(d.filter(pl.col("rule").is_in(picked)).select(["rule", "alpha_w", "a", "beta", "c", "kappa"]))
