# /// script
# dependencies = ["polars", "numpy"]
# ///
"""Checks on W2/W3 (added after review): (1) local area exponent drift for W2 chaotic turmites, k=22..24 vs 26..28; (2) aniso/fill at last checkpoint for W3 runs;
(3) anisotropy of all 10 W2 sqrt-class tables at their last checkpoint. usage: uv run experiments/archive/2026-10-w-width-radius-refit/scripts/w_checks.py"""
import numpy as np, polars as pl
cols = "kind,spec,k,A,rg2,aniso,rbar,rsd,h2,h4,h8,Wsurf,fill".split(",")
def load(p):
    return pl.DataFrame([l.strip().split(",") for l in open(p) if l.startswith("cp,")], schema=cols, orient="row").with_columns([pl.col(c).cast(pl.Float64) for c in cols[2:]])
w2 = load("experiments/archive/2026-10-w2/results/w2_shape.csv"); w3 = load("experiments/archive/2026-10-w3/results/w3_shape.csv")
print("(1) W2 chaotic turmites: a(22-24), a(24-26), a(26-28), centre density")
prof = {l.split(",")[1]: float(l.split(",")[3].split(";")[0]) for l in open("experiments/archive/2026-10-w2/results/w2_shape.csv") if l.startswith("prof,")}
for s in [l.strip() for l in open("experiments/archive/2026-10-w2/results/w2_specs.txt")][10:]:
    g = w2.filter(pl.col("spec") == s); A = dict(zip(g["k"].to_list(), g["A"].to_list()))
    a = [np.log2(A[k + 2] / A[k]) / 2 for k in (22, 24, 26)]
    print(f"  {s:16s} " + " ".join(f"{x:.3f}" for x in a) + f"  centre {prof[s]:.2f}")
print("(2) W3 last checkpoint: spec k aniso fill rsd")
for s, g in w3.group_by("spec", maintain_order=True):
    l = g.sort("k").tail(1).row(0, named=True); print(f"  {s[0]:14s} k={int(l['k'])} aniso={l['aniso']:.3f} fill={l['fill']:.3f} rsd={l['rsd']:.3f}")
print("(3) W2 sqrt tables last checkpoint: spec k aniso")
for s in [l.strip() for l in open("experiments/archive/2026-10-w2/results/w2_specs.txt")][:10]:
    l = w2.filter(pl.col("spec") == s).sort("k").tail(1).row(0, named=True); print(f"  {s:16s} k={int(l['k'])} aniso={l['aniso']:.4f} A={int(l['A'])} fill={l['fill']:.3f}")
