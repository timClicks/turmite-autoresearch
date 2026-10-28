# /// script
# dependencies = ["numpy", "polars", "scipy"]
# ///
"""Arm B (notes/kappa-experiment-design.md): noisy rotor. Input experiments/archive/2026-10-arm-kappa-depletion-arms/results/armb_probe.csv
(probe 27 16384 < experiments/archive/2026-10-arm-kappa-depletion-arms/results/armb_specs.txt). Windows k = 20..26 (design said 22..28; the run stops at 2^27)."""
import sys; sys.path.insert(0, "experiments/_lib")
import numpy as np, polars as pl
from scipy.stats import spearmanr
from analyse_probe import per_rule, slope
raw = pl.read_csv("experiments/archive/2026-10-arm-kappa-depletion-arms/results/armb_probe.csv")
r = per_rule(raw).with_columns(eps=pl.col("rule").str.split(":").list.get(1).cast(pl.Float64))
# local area exponent early (k 20..23) and late (k 23..26)
loc = []
for (w,), g in raw.filter(~pl.col("escaped")).group_by("rule"):
    g = g.sort("k")
    for lo, hi, nm in [(20, 23, "a_early"), (23, 26, "a_late")]:
        h = g.filter((pl.col("k") >= lo) & (pl.col("k") <= hi))
        if h.height == hi - lo + 1: loc.append((w, nm, slope(h["t"].to_numpy().astype(float), h["area"].to_numpy().astype(float))))
loc = pl.DataFrame(loc, schema=["rule", "nm", "v"], orient="row").pivot(on="nm", index="rule", values="v")
r = r.join(loc, on="rule", how="left")
pl.Config.set_float_precision(3); pl.Config.set_tbl_rows(30)
g = r.group_by("eps").agg(n=pl.len(), a=pl.col("a").median(), a_early=pl.col("a_early").median(), a_late=pl.col("a_late").median(),
    alpha_w=pl.col("alpha_w").median(), beta=pl.col("beta").median(), c=pl.col("c").median(), kappa=pl.col("kappa").median(), kappa_sd=pl.col("kappa").std(), g_k=pl.col("g_k").median()).sort("eps")
print("walkers fitted:", r.height, "of 48"); print(g)
m = g.filter(pl.col("eps") <= 0.03)
print("B2: Spearman(kappa, eps) over eps <= 0.03:", spearmanr(m["eps"], m["kappa"]))
print("B3: median |kappa*c - (new/S)*(A/P)| / (kappa*c):")
raw2 = raw.filter((pl.col("k") == 26) & ~pl.col("escaped")).with_columns(lhs=(pl.col("new_cells") / pl.col("boundary_steps")) * (pl.col("boundary_steps") / (pl.col("t") // 2)) / (pl.col("perimeter") / pl.col("area")), rhs=(pl.col("new_cells") / (pl.col("t") // 2)) / (pl.col("perimeter") / pl.col("area")))
print(float(((raw2["lhs"] - raw2["rhs"]).abs() / raw2["rhs"]).median()), "(identity, expected ~0)")
