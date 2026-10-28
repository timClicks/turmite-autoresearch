# /// script
# dependencies = ["polars", "numpy"]
# ///
"""Item 28 follow-up: local volume/extent exponents for cubic ants and the rotor3 control, plus V/E^3."""
import numpy as np, polars as pl
c = pl.read_csv("experiments/archive/2026-10-ext-other-lattices-turmites-noise/results/ext_cube_class.csv").filter(pl.col("cls") == "blob")["spec"].to_list()
d = pl.read_csv("experiments/archive/2026-10-ext-other-lattices-turmites-noise/results/ext_cube.csv").filter(pl.col("spec").is_in(c) & (pl.col("k") > 0))
def loc(g, lo, hi):
    g = g.filter((pl.col("k") >= lo) & (pl.col("k") <= hi)).sort("k"); k = g["k"].to_numpy() * np.log(2)
    return np.polyfit(k, np.log(g["area"].to_numpy()), 1)[0], np.polyfit(k, np.log(g["extent"].to_numpy()), 1)[0]
res = {}
for lo, hi in [(14, 18), (18, 22), (20, 24)]:
    v = np.array([loc(g, lo, hi) for _, g in d.group_by("spec", maintain_order=True)]); res[(lo, hi)] = v
    print(f"k{lo}-{hi}: volume exp median {np.median(v[:,0]):.3f} (IQR {np.quantile(v[:,0],.25):.3f}-{np.quantile(v[:,0],.75):.3f}); extent exp median {np.median(v[:,1]):.3f}")
fill = d.with_columns(f=pl.col("area") / pl.col("extent").cast(pl.Float64) ** 3).group_by("k", maintain_order=True).agg(f=pl.col("f").median()).sort("k")
print("median V/E^3 by k:", {int(k): round(f, 3) for k, f in zip(fill["k"], fill["f"])})
r = pl.read_csv("experiments/archive/2026-10-ext-other-lattices-turmites-noise/results/ext_rotor3.csv"); print("rotor3 runs reaching k=20:", r.filter(pl.col("k") == 20).height, "of", r["spec"].n_unique(), " (others escaped the 512 board)")
x = r.filter(pl.col("k") == 15)["area"].to_numpy() / 2 ** 15; print("rotor3: area / t at 2^15 (1 = ballistic): mean %.2f" % x.mean())
