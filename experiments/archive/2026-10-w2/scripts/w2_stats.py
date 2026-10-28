# /// script
# dependencies = ["polars", "numpy"]
# ///
"""W2: visit-density profile of 2x2 turmites at 2^28 vs the uniform-occupancy formula (1/(1-a))(1-(r/R)^(2(1-a)/a)) with the run's own a (k=22..28)
and the rotor cone 3(1-r/R). Input experiments/archive/2026-10-w2/results/w2_shape.csv (shape 28 8192 on experiments/archive/2026-10-w2/results/w2_specs.txt; first 10 specs sqrt class, last 10 chaotic).
Predictions: notes/frontier-2026-10-13-results.md (W2). usage: uv run experiments/archive/2026-10-w2/scripts/w2_stats.py"""
import numpy as np, polars as pl
cols = "kind,spec,k,A,rg2,aniso,rbar,rsd,h2,h4,h8,Wsurf,fill".split(",")
cp = pl.DataFrame([l.strip().split(",") for l in open("experiments/archive/2026-10-w2/results/w2_shape.csv") if l.startswith("cp,")], schema=cols, orient="row").with_columns([pl.col(c).cast(pl.Float64) for c in cols[2:]])
prof = {l.split(",")[1]: np.array([float(v) for v in l.strip().split(",")[3].split(";")]) for l in open("experiments/archive/2026-10-w2/results/w2_shape.csv") if l.startswith("prof,")}
print("escaped/missing:", [l.strip() for l in open("experiments/archive/2026-10-w2/results/w2_shape.csv") if l.startswith("#")])
specs = [l.strip() for l in open("experiments/archive/2026-10-w2/results/w2_specs.txt")]
import sys
KMIN, KMAX = (22, 28)
x = (np.arange(20) + 0.5) * 0.075
out = {"sqrt": [], "chaotic": []}
for i, s in enumerate(specs):
    cls = "sqrt" if i < 10 else "chaotic"
    if s not in prof: print(s, cls, "no profile"); continue
    g = cp.filter(pl.col("spec") == s); A = dict(zip(g["k"].to_list(), g["A"].to_list()))
    a = np.log2(A[KMAX] / A[KMIN]) / (KMAX - KMIN); p = prof[s]; occ = x < 1.0
    cone = 3 * (1 - x); form = (1 / (1 - a)) * (1 - x ** (2 * (1 - a) / a))
    rms = lambda m: float(np.sqrt(np.mean((p[occ] - m[occ]) ** 2)))
    inrange = (0.40 <= a <= 0.56) if cls == "sqrt" else (0.55 <= a <= 0.85)
    out[cls].append((s, a, p[0], form[0], rms(form), rms(cone), inrange))
    print(f"{cls:8s} {s:16s} a={a:.3f} centre={p[0]:.2f} formula-centre={form[0]:.2f} rms formula {rms(form):.2f} cone {rms(cone):.2f} in-class-range={inrange}")
for cls, v in out.items():
    n = len(v); beat = sum(r[4] < r[5] for r in v); c2 = sum(abs(r[2] - 2) <= 0.5 for r in v); c3 = sum(abs(r[2] - 3) <= 0.5 for r in v)
    print(f"{cls}: n={n}; formula beats cone in {beat}; centre within 2+-0.5 in {c2}, within 3+-0.5 in {c3}; in-range runs {sum(r[6] for r in v)}")
