# /// script
# dependencies = ["polars", "numpy"]
# ///
"""W3: profile of noisy rotors / memoryless walkers at 2^26 vs formula (with own a, k=20..26) and cone. Input experiments/archive/2026-10-w3/results/w3_shape.csv. Predictions: notes (W3)."""
import numpy as np, polars as pl
cols = "kind,spec,k,A,rg2,aniso,rbar,rsd,h2,h4,h8,Wsurf,fill".split(",")
cp = pl.DataFrame([l.strip().split(",") for l in open("experiments/archive/2026-10-w3/results/w3_shape.csv") if l.startswith("cp,")], schema=cols, orient="row").with_columns([pl.col(c).cast(pl.Float64) for c in cols[2:]])
prof = {l.split(",")[1]: np.array([float(v) for v in l.strip().split(",")[3].split(";")]) for l in open("experiments/archive/2026-10-w3/results/w3_shape.csv") if l.startswith("prof,")}
x = (np.arange(20) + 0.5) * 0.075; occ = x < 1.0
rows = []
for s, p in prof.items():
    g = cp.filter(pl.col("spec") == s); A = dict(zip(g["k"].to_list(), g["A"].to_list()))
    a = np.log2(A[26] / A[20]) / 6
    cone = 3 * (1 - x); form = (1 / (1 - a)) * (1 - x ** (2 * (1 - a) / a))
    rms = lambda m: float(np.sqrt(np.mean((p[occ] - m[occ]) ** 2)))
    rows.append((s, a, p[0], form[0], rms(form), rms(cone)))
    print(f"{s:14s} a={a:.3f} centre={p[0]:.2f} formula-centre={form[0]:.2f} rms formula {rms(form):.2f} cone {rms(cone):.2f}")
sel = [r for r in rows if r[1] >= 0.75]
print(f"runs with a >= 0.75: {len(sel)}; formula beats cone in {sum(r[4] < r[5] for r in sel)}; centre > 3.5 in {sum(r[2] > 3.5 for r in sel)}; centre within 3+-0.5 in {sum(abs(r[2]-3) <= 0.5 for r in sel)}")
