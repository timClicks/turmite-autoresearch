# /// script
# dependencies = ["numpy", "polars", "scipy"]
# ///
"""EXPLORATORY (added after seeing Arm A): do the 24 ants (12 extreme + 12 typical kappa) split into a 'crust' class
(layers 2-4 nearly unvisited) and a 'uniform' class? Reuses the tables of layers_stats*.py; class = max |rho(d)-1|, d=2..4, < 0.3."""
import re, subprocess, sys, numpy as np, polars as pl
from scipy.stats import spearmanr
sys.argv = ["x"]
frames = []
for f in ["experiments/archive/2026-10-layers-colours/results/layers.csv", "experiments/archive/2026-10-layers-colours/results/layers_typical.csv"]:
    exec(open("experiments/archive/2026-10-layers-colours/scripts/layers_stats.py").read().split("pl.Config")[0].replace("experiments/archive/2026-10-layers-colours/results/layers.csv", f))
    frames.append(t.filter(pl.col("kind") == "ant"))
a = pl.concat(frames).unique("walker")
dev = np.max(np.abs(a.select(["rho2", "rho3", "rho4"]).to_numpy() - 1), axis=1)
a = a.with_columns(crust=pl.Series(dev > 0.3), dev=pl.Series(dev))
pl.Config.set_float_precision(2); pl.Config.set_tbl_rows(40)
print(a.select("walker", "crust", "rho0", "rho1", "rho2", "rho3", "rho4", "v_e", "c", "kappa_probe").sort("crust", "v_e"))
print(a.group_by("crust").agg(n=pl.len(), v_e_min=pl.col("v_e").min(), v_e_max=pl.col("v_e").max(), c_med=pl.col("c").median(),
      kappa_med=pl.col("kappa_probe").median(), kappa_min=pl.col("kappa_probe").min(), kappa_max=pl.col("kappa_probe").max()))
u = a.filter(~pl.col("crust"))
print("uniform class: Spearman(kappa, v_e) =", spearmanr(u["kappa_probe"], u["v_e"]), "n =", u.height)
