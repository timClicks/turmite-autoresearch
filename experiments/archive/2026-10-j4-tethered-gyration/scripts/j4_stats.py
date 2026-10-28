# /// script
# dependencies = ["polars", "numpy"]
# ///
"""J4: radius-of-gyration growth per octave for tethered rules (experiments/archive/2026-10-j4-tethered-gyration/results/j4_probe.csv from probe 28 8192 < experiments/archive/2026-10-j4-tethered-gyration/results/j4_specs.txt). Prediction: notes J4."""
import numpy as np, polars as pl
d = pl.read_csv("experiments/archive/2026-10-j4-tethered-gyration/results/j4_probe.csv").with_columns(R=pl.col("rg2").sqrt())
for (rule,), g in d.group_by("rule", maintain_order=True):
    g = g.sort("k"); R = g["R"].to_numpy(); k = g["k"].to_numpy(); A = g["area"].to_numpy()
    print(rule, "local d log2 R per octave:", " ".join(f"{kk}:{s:+.2f}" for kk, s in zip(k[1:], np.diff(np.log2(R)))), "| esc", bool(g["escaped"].any()))
    print("   R at k=14,20,24,28:", [round(float(R[k == kk][0]), 1) for kk in (14, 20, 24, 28) if (k == kk).any()], " A:", [int(A[k == kk][0]) for kk in (14, 20, 24, 28) if (k == kk).any()])
