# /// script
# dependencies = ["polars", "numpy"]
# ///
"""E1: TSAW (examples/tsaw.rs; experiments/archive/2026-10-e2-sensitive-disc/results/e2_tsaw.csv, tsaw 26 16384 < experiments/archive/2026-10-e1-one-sided-hot-region/results/e1_specs.txt). Area exponent over k=16..22 (all runs reach 2^22) and kappa in the k=22 octave window, per g. Predictions: notes (E1)."""
import numpy as np, polars as pl
d = pl.read_csv("experiments/archive/2026-10-e2-sensitive-disc/results/e2_tsaw.csv", comment_prefix="#").with_columns(g=pl.col("spec").str.split(":").list.get(0).cast(pl.Float64))
esc = sum(1 for l in open("experiments/archive/2026-10-e2-sensitive-disc/results/e2_tsaw.csv") if l.startswith("#"))
print(f"{esc} of 12 runs left the 16384 board before 2^26")
for (g,), s in d.group_by("g", maintain_order=True):
    ex, kp, kmax = [], [], []
    for (sp,), r in s.group_by("spec"):
        r = r.sort("k"); A = dict(zip(r["k"].to_list(), r["A"].to_list())); kk = dict(zip(r["k"].to_list(), r["kappa"].to_list()))
        ex.append(np.log2(A[22] / A[16]) / 6); kp.append(kk[22]); kmax.append(r["k"].max())
    print(f"g={g:<5} runs {len(ex)}  area exponent k16..22: {np.mean(ex):.3f} (sd {np.std(ex, ddof=1):.3f})  kappa(k=22): {np.mean(kp):.2f} (sd {np.std(kp, ddof=1):.2f})  last full window k: {min(kmax)}-{max(kmax)}")
