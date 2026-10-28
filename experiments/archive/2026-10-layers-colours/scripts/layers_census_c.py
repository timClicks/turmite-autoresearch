# /// script
# dependencies = ["numpy", "polars"]
# ///
"""EXPLORATORY: how common is the 'crust' class? Proxy: census edge-entry probability c (probe_summary.csv), since all
15 crust ants measured in experiments/archive/2026-10-layers-colours/results/layers_classes.txt have c in [0.44, 0.66] and 13 of 15 have c >= 0.61, while the 9 uniform ants have c <= 0.48."""
import numpy as np, polars as pl
d = pl.read_csv("experiments/archive/2026-10-probe-growth-census/results/probe_summary.csv").filter((pl.col("cls") == "blob") & ~pl.col("bursty"))
c = d["c"].to_numpy()
print("blob rules:", len(c), " c quantiles 5/25/50/75/95:", np.round(np.quantile(c, [.05, .25, .5, .75, .95]), 3))
for th in [0.55, 0.6]:
    hi = d.filter(pl.col("c") >= th)
    print(f"c >= {th}: {hi.height} rules ({hi.height/len(c):.0%}); kappa median {hi['kappa'].median():.2f} IQR {np.round(np.quantile(hi['kappa'].to_numpy(), [.25,.75]),2)}; c < {th}: kappa median {d.filter(pl.col('c')<th)['kappa'].median():.2f}")
hist, edges = np.histogram(c, bins=np.arange(0.0, 0.8, 0.05)); print("c histogram (0.05 bins from 0):", dict(zip(np.round(edges[:-1], 2), hist)))
