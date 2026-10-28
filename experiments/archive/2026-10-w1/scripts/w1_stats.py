# /// script
# dependencies = ["numpy", "polars", "scipy"]
# ///
"""W1: is the ants' boundary-width exponent (Wsurf) tied to the crust class / kappa? Inputs experiments/archive/2026-10-w1/results/w1_shape.csv (shape 30 16384 on experiments/archive/2026-10-w-width-radius-refit/results/w_ants.txt)
and the class table of experiments/archive/2026-10-layers-colours/scripts/layers_classes.py. Design and predictions: notes/frontier-2026-10-13-results.md (W1). usage: uv run experiments/archive/2026-10-w1/scripts/w1_stats.py"""
import sys, numpy as np, polars as pl
from scipy.stats import spearmanr, mannwhitneyu
sys.argv = ["x"]
frames = []
for f in ["experiments/archive/2026-10-layers-colours/results/layers.csv", "experiments/archive/2026-10-layers-colours/results/layers_typical.csv"]:
    exec(open("experiments/archive/2026-10-layers-colours/scripts/layers_stats.py").read().split("pl.Config")[0].replace("experiments/archive/2026-10-layers-colours/results/layers.csv", f))
    frames.append(t.filter(pl.col("kind") == "ant"))
a = pl.concat(frames).unique("walker")
dev = np.max(np.abs(a.select(["rho2", "rho3", "rho4"]).to_numpy() - 1), axis=1)
cls = {w: bool(d > 0.3) for w, d in zip(a["walker"].to_list(), dev)}
kap = dict(zip(a["walker"].to_list(), a["kappa_probe"].to_list()))
cols = "kind,spec,k,A,rg2,aniso,rbar,rsd,h2,h4,h8,Wsurf,fill".split(",")
rows = [l.strip().split(",") for l in open("experiments/archive/2026-10-w1/results/w1_shape.csv") if l.startswith("cp,")]
d = pl.DataFrame(rows, schema=cols, orient="row").with_columns([pl.col(c).cast(pl.Float64) for c in cols[2:]])
esc = [l.strip() for l in open("experiments/archive/2026-10-w1/results/w1_shape.csv") if l.startswith("#")]
print("escaped:", esc)
res = []
for (spec,), g in d.group_by("spec"):
    g = g.sort("k"); k = g["k"].to_numpy().astype(int); W = g["Wsurf"].to_numpy()
    if k.max() < 30: print("dropped (no 2^30):", spec); continue
    loc = [(np.log(W[i + 1]) - np.log(W[i])) / (2 * np.log(2)) for i in range(len(k) - 1) if k[i] >= 22]
    res.append((spec, cls[spec], kap[spec], float(np.mean(loc))))
r = pl.DataFrame(res, schema=["spec", "crust", "kappa", "D"], orient="row").sort("crust", "D")
pl.Config.set_float_precision(3); pl.Config.set_tbl_rows(40); print(r)
cr = r.filter(pl.col("crust"))["D"].to_numpy(); un = r.filter(~pl.col("crust"))["D"].to_numpy()
print(f"n crust {len(cr)}, uniform {len(un)}; mean D crust {cr.mean():.3f} (sd {cr.std(ddof=1):.3f}), uniform {un.mean():.3f} (sd {un.std(ddof=1):.3f}); diff {cr.mean()-un.mean():+.3f}")
print("W1a Mann-Whitney one-sided (crust > uniform):", mannwhitneyu(cr, un, alternative="greater"))
print("W1b Spearman(D, log kappa):", spearmanr(r["D"], np.log(r["kappa"])))
print(f"W1c uniform class: min D {un.min():.3f}, median {np.median(un):.3f}; all > 0.18: {bool((un > 0.18).all())}; rotor reference 0.10-0.13")
