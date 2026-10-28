# /// script
# dependencies = ["polars", "numpy", "scipy"]
# ///
"""T1 audit: is D_med/R vs kappa a normalisation artefact (D in cells ~ 1)?
Run: uv run experiments/archive/2026-10-t1-excursion-tomography/scripts/t1_audit.py > experiments/archive/2026-10-t1-excursion-tomography/results/t1_audit.txt"""
import numpy as np, polars as pl
from scipy import stats
df = pl.read_csv("experiments/archive/2026-10-t1-excursion-tomography/results/t1_excursions.csv").filter(pl.col("spec").str.contains("@"))
df = df.with_columns(pl.col("spec").str.split("@").list.get(0).alias("rule"),
    (pl.col("area")/np.pi).sqrt().alias("R"))
df = df.with_columns((pl.col("disp_med")*pl.col("R")).alias("D_cells"),
    (pl.col("depth_med")*pl.col("R")).alias("depth_cells"),
    (pl.col("depth_mean")*pl.col("R")).alias("depthmean_cells"),
    pl.col("area").log().alias("lnA"))
print("rows", df.height, "escaped rows", df.filter(pl.col("escaped")=="true").height)
for k in (22,25):
    d = df.filter(pl.col("k")==k).group_by("rule").agg(pl.all().exclude("spec","escaped").mean())
    kap = d["kappa"].to_numpy()
    print(f"\nk={k}, {d.height} rules")
    for name in ["disp_med","D_cells","depth_med","depth_cells","depthmean_cells","R","area","n_completed","l_mean","l_med","top1_share","edge_dwell_mean","unresolved_share"]:
        r,p = stats.spearmanr(d[name].to_numpy(), kap)
        print(f"  rho({name:16s}, kappa) = {r:+.3f} (p={p:.1e})")
    print("  D_cells quantiles", np.quantile(d["D_cells"].to_numpy(),[0,.25,.5,.75,1]).round(2))
    print("  R quantiles", np.quantile(d["R"].to_numpy(),[0,.25,.5,.75,1]).round(0))
    # partial: does disp_med/R still correlate once ln A is controlled?
    x=d["disp_med"].to_numpy(); la=d["lnA"].to_numpy(); y=np.log(kap)
    def resid(v,z): b=np.polyfit(z,v,1); return v-np.polyval(b,z)
    r,p=stats.pearsonr(resid(np.log(x),la),resid(y,la))
    print(f"  partial r(ln D/R, ln kappa | ln A) = {r:+.3f} (p={p:.1e})")
    print(f"  r(ln A, ln kappa) = {stats.pearsonr(la,y)[0]:+.3f}")

# depth in cells, per rule at k=25
d = df.filter(pl.col("k")==25).group_by("rule").agg(pl.all().exclude("spec","escaped").mean())
for name in ["depth_cells","depthmean_cells","l_mean","l_med"]:
    print(name, "quantiles", np.quantile(d[name].to_numpy(),[0,.25,.5,.75,1]).round(2))
kap=d["kappa"].to_numpy(); o=np.argsort(kap)
print("lowest-6 kappa rules: depth_cells", d["depth_cells"].to_numpy()[o[:6]].round(2), "R", d["R"].to_numpy()[o[:6]].round(0))
print("highest-6 kappa rules: depth_cells", d["depth_cells"].to_numpy()[o[-6:]].round(2), "R", d["R"].to_numpy()[o[-6:]].round(0))
