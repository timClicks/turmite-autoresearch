# /// script
# dependencies = ["numpy", "polars", "scipy"]
# ///
"""Arm C: sign test of 'lower-kappa member of a matched pair has the larger depletion D = mean_{d=2..4}(1 - rho(d))'.
Inputs experiments/archive/2026-10-arm-kappa-depletion-arms/results/armc_layers.csv (layers 26 8192 < experiments/archive/2026-10-arm-kappa-depletion-arms/results/armc_specs.txt) and the pair list experiments/archive/2026-10-arm-kappa-depletion-arms/results/armc_pairs.txt."""
import ast, numpy as np, polars as pl
from scipy.stats import binomtest
src = open("experiments/archive/2026-10-layers-colours/scripts/layers_stats.py").read().split("pl.Config")[0].replace("experiments/archive/2026-10-layers-colours/results/layers.csv", "experiments/archive/2026-10-arm-kappa-depletion-arms/results/armc_layers.csv")
exec(src)
tab = {r["walker"]: r for r in t.to_dicts()}
pairs = [ast.literal_eval(l) for l in open("experiments/archive/2026-10-arm-kappa-depletion-arms/results/armc_pairs.txt") if l.startswith("(")]
D = lambda r: float(np.mean([1 - r[f"rho{d}"] for d in (2, 3, 4)]))
res = []
for a, b, ca, cb, ka, kb in pairs:
    if a not in tab or b not in tab: continue
    lo, hi = (a, b) if ka < kb else (b, a)
    res.append((lo, hi, D(tab[lo]) > D(tab[hi]), (tab[lo]["kappa_probe"] < tab[hi]["kappa_probe"])))
print("pairs usable:", len(res), "of", len(pairs), "(dropped: a member escaped the board or lacked a window)")
k = sum(r[2] for r in res); print("lower-kappa (selection means) member has larger D in", k, "of", len(res), binomtest(k, len(res), 0.5, alternative="greater"))
agree = sum(r[3] for r in res); print("blank-board kappa agrees with the selection ordering in", agree, "of", len(res), "pairs")
k2 = sum(r[2] for r in res if r[3]); n2 = sum(r[3] for r in res); print("restricted to pairs where it does:", k2, "of", n2)
