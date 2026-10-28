# /// script
# dependencies = ["polars", "numpy"]
# ///
"""A3 control: visit-density profile of ants on a full random-colour background (experiments/archive/2026-10-a3-background-cone-control/results/a3_shape_bg.csv, shape 24 16384) vs the formula
profile(r) = (1/(1-a)) (1 - (r/R)^(2(1-a)/a)) with the measured a, and vs the blank-board cone 3(1 - r/R). Prediction: notes/frontier-2026-10-13-results.md.
usage: uv run experiments/archive/2026-10-a3-background-cone-control/scripts/a3_stats.py"""
import numpy as np, polars as pl
cols = "kind,spec,k,A,rg2,aniso,rbar,rsd,h2,h4,h8,Wsurf,fill".split(",")
cp = pl.DataFrame([l.strip().split(",") for l in open("experiments/archive/2026-10-a3-background-cone-control/results/a3_shape_bg.csv") if l.startswith("cp,")], schema=cols, orient="row").with_columns([pl.col(c).cast(pl.Float64) for c in cols[2:]])
prof = {l.split(",")[1]: [float(v) for v in l.strip().split(",")[3].split(";")] for l in open("experiments/archive/2026-10-a3-background-cone-control/results/a3_shape_bg.csv") if l.startswith("prof,")}
print(f"runs with a profile: {len(prof)} of 12 specs; first line of a prof row has {len(next(iter(prof.values())))} values")
n_beat = 0; n = 0
for spec, p in prof.items():
    g = cp.filter(pl.col("spec") == spec).sort("k"); A = dict(zip(g["k"].to_list(), g["A"].to_list()))
    if 22 not in A or 24 not in A: continue
    a = np.log2(A[24] / A[22]) / 2; p = np.array(p); x = (np.arange(len(p)) + 0.5) * 0.075  # shell centre in units of R_eq
    occ = x < 1.0
    cone = 3 * (1 - x); form = (1 / (1 - a)) * (1 - x ** (2 * (1 - a) / a))
    rms = lambda m: float(np.sqrt(np.mean((p[occ] - m[occ]) ** 2)))
    n += 1; n_beat += rms(form) < rms(cone)
    print(f"{spec:22s} a={a:.3f}  centre(shell 0)={p[0]:.2f}  rms formula {rms(form):.2f}  rms cone {rms(cone):.2f}  predicted centre {form[0]:.2f}")
print(f"formula beats the cone in {n_beat} of {n} runs (prediction: >= 75% and a central value > 6)")
