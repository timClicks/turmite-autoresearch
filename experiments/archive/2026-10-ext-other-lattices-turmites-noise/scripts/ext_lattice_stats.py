# /// script
# dependencies = ["polars", "numpy"]
# ///
"""Items 24, 28 (and 25 with kind=tm): classify growth of hex / cube / turmite screens.
usage: uv run experiments/archive/2026-10-ext-other-lattices-turmites-noise/scripts/ext_lattice_stats.py experiments/archive/2026-10-ext-other-lattices-turmites-noise/results/ext_hex.csv [KLO KHI]"""
import sys
import numpy as np, polars as pl

path = sys.argv[1]; klo = int(sys.argv[2]) if len(sys.argv) > 2 else 16; khi = int(sys.argv[3]) if len(sys.argv) > 3 else 24
d = pl.read_csv(path)
esc = set(d.filter(pl.col("k") == -1)["spec"].to_list())
rows = []
for (sp,), g in d.filter(pl.col("k") > 0).group_by("spec", maintain_order=True):
    g = g.sort("k"); k = g["k"].to_numpy().astype(float); A = g["area"].to_numpy().astype(float); E = g["extent"].to_numpy().astype(float)
    if sp in esc or k.max() < khi:
        rows.append(dict(spec=sp, cls="escaped", a=np.nan, w=np.nan, ratio=np.nan, A=np.nan)); continue
    s = (k >= klo) & (k <= khi)
    a = np.polyfit(k[s] * np.log(2), np.log(A[s]), 1)[0]; w = np.polyfit(k[s] * np.log(2), np.log(E[s]), 1)[0]
    ratio = A[k == khi][0] / A[k == klo][0]
    cls = "bounded" if ratio < 1.15 else ("slow" if a < 0.5 else ("blob" if a < 0.9 else "fast"))
    rows.append(dict(spec=sp, cls=cls, a=a, w=w, ratio=ratio, A=A[k == khi][0]))
r = pl.DataFrame(rows)
print(path, "specs", r.height)
print(r.group_by("cls", maintain_order=True).len().sort("len", descending=True))
b = r.filter(pl.col("cls") == "blob")
if b.height:
    a = b["a"].to_numpy(); w = b["w"].to_numpy()
    q = lambda x: np.round(np.quantile(x, [0.1, 0.25, 0.5, 0.75, 0.9]), 3)
    print(f"blob-like (0.5<=a<0.9): n={b.height}; area/volume exponent quantiles 10/25/50/75/90%:", q(a), "mean %.3f" % a.mean())
    print("  extent exponent quantiles:", q(w))
    print("  fraction with a within 0.1 of 2/3: %.2f; within 0.1 of 3/4: %.2f" % ((abs(a - 2 / 3) < 0.1).mean(), (abs(a - 0.75) < 0.1).mean()))
    # by rule length when spec is hex:/cube:
    b = b.with_columns(n=pl.col("spec").str.split(":").list.get(1).str.len_chars())
    print(b.group_by("n", maintain_order=True).agg(cnt=pl.len(), med_a=pl.col("a").median(), med_w=pl.col("w").median()).sort("n"))
sl = r.filter(pl.col("cls") == "slow")
if sl.height: print("slow-growth (a<0.5) examples:", sl.sort("a")["spec"].head(5).to_list(), "median a %.3f" % sl["a"].median())
fa = r.filter(pl.col("cls") == "fast")
if fa.height: print("fast (a>=0.9) examples:", fa["spec"].head(5).to_list(), "median a %.3f" % fa["a"].median())
r.write_csv(path.replace(".csv", "_class.csv"))
