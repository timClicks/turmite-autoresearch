# /// script
# dependencies = ["polars", "numpy"]
# ///
"""Items 25 and 28 follow-ups: local exponents at late times for the turmite candidates (experiments/archive/2026-10-ext-other-lattices-turmites-noise/results/ext_tm_long.csv, k=16..26) and the cubic ants (experiments/archive/2026-10-ext-other-lattices-turmites-noise/results/ext_cube_long.csv, k=20..28)."""
import sys
import numpy as np, polars as pl
def local(path, windows):
    d = pl.read_csv(path)
    esc = set(d.filter(pl.col("k") == -1)["spec"].to_list())
    d = d.filter(pl.col("k") > 0)
    out = {w: [] for w in windows}; kept = 0
    for (sp,), g in d.group_by("spec", maintain_order=True):
        g = g.sort("k"); k = g["k"].to_numpy()
        if sp in esc or k.max() < max(w[1] for w in windows): continue
        kept += 1
        for lo, hi in windows:
            s = (k >= lo) & (k <= hi)
            out[(lo, hi)].append((np.polyfit(k[s] * np.log(2), np.log(g["area"].to_numpy()[s].astype(float)), 1)[0], np.polyfit(k[s] * np.log(2), np.log(g["extent"].to_numpy()[s].astype(float)), 1)[0]))
    return d["spec"].n_unique() , kept, out
which = sys.argv[1]
if which == "cube":
    tot, kept, out = local("experiments/archive/2026-10-ext-other-lattices-turmites-noise/results/ext_cube_long.csv", [(20, 24), (24, 28)])
    print(f"cube: {tot} rules, {kept} reached 2^28 inside the box")
    for w, v in out.items():
        v = np.array(v); print(f"  k{w[0]}-{w[1]}: volume exp median {np.median(v[:,0]):.3f} (IQR {np.quantile(v[:,0],.25):.3f}-{np.quantile(v[:,0],.75):.3f}); extent exp median {np.median(v[:,1]):.3f}")
else:
    tot, kept, out = local("experiments/archive/2026-10-ext-other-lattices-turmites-noise/results/ext_tm_long.csv", [(16, 20), (20, 24), (22, 26)])
    print(f"turmite candidates: {tot}, {kept} reached 2^26 inside the box")
    for w, v in out.items():
        v = np.array(v); a = v[:, 0]
        h, _ = np.histogram(a, bins=[0, .3, .5, .55, .6, .65, .7, .75, .8, .9, 1.2])
        print(f"  k{w[0]}-{w[1]}: area exp quantiles 10/25/50/75/90 {np.round(np.quantile(a, [.1,.25,.5,.75,.9]), 3).tolist()}; extent exp median {np.median(v[:,1]):.3f}; within 0.05 of 2/3: {np.mean(abs(a-2/3)<0.05):.2f}; hist(0,.3,.5,.55,.6,.65,.7,.75,.8,.9,1.2) {h.tolist()}")
