# /// script
# dependencies = ["polars", "numpy"]
# ///
"""A2b: rotor edge exponent to 2^36 (seeds 11-16) pooled with the 2^34 seeds 1-8 (experiments/archive/2026-10-b1-exact-exponent/results/b1_probe_*.csv). Decision rule: notes/frontier-2026-10-13-results.md."""
import glob, numpy as np, polars as pl
new = pl.read_csv("experiments/archive/2026-10-a2-edge-exponent/results/a2b_probe.csv")
old = pl.concat([pl.read_csv(f) for f in sorted(glob.glob("experiments/archive/2026-10-b1-exact-exponent/results/b1_probe_??.csv"))]).filter(pl.col("rule").str.starts_with("rotor:"))
def beta(df):
    out = {}
    for (r,), g in df.group_by("rule"):
        g = g.sort("k"); k = g["k"].to_list(); P = dict(zip(k, g["perimeter"].to_list())); A = dict(zip(k, g["area"].to_list()))
        out[r] = {e: np.log(P[e] / P[e - 4]) / np.log(A[e] / A[e - 4]) for e in range(20, 37, 2) if e in P and e - 4 in P}
    return out
bn, bo = beta(new), beta(old)
print("mean local beta(k) over seeds (n): ")
for e in range(24, 37, 2):
    v = [s[e] for s in list(bn.values()) + list(bo.values()) if e in s]; vn = [s[e] for s in bn.values() if e in s]
    print(f"  k={e}: all {np.mean(v):.4f} +- {np.std(v, ddof=1)/np.sqrt(len(v)):.4f} (n={len(v)}); seeds 11-16 only {np.mean(vn):.4f} +- {np.std(vn, ddof=1)/np.sqrt(len(vn)):.4f}")
v36 = np.array([s[36] for s in bn.values()]); print(f"beta(36), seeds 11-16: {v36.mean():.4f} +- {v36.std(ddof=1)/np.sqrt(len(v36)):.4f} (seed sd {v36.std(ddof=1):.4f})")
print("decision: <= 0.506 favours 1/2; >= 0.511 favours a plateau above 1/2; between inconclusive ->", "favours 1/2" if v36.mean() <= 0.506 else "plateau above 1/2" if v36.mean() >= 0.511 else "inconclusive")
# refit beta_inf with k = 26..36 using all seeds with data to the relevant k
allb = {**bo, **bn}
for x in (1 / 3, 1 / 2, 1.0):
    ks = [26, 28, 30, 32, 34]; y = np.array([np.mean([s[e] for s in allb.values() if e in s]) for e in ks]); X = np.c_[np.ones(len(ks)), 2.0 ** (-x * np.array(ks))]
    b0 = np.linalg.lstsq(X, y, rcond=None)[0][0]; print(f"  fit on k=26..34 (all seeds), x={x:.2f}: beta_inf = {b0:.4f}; its prediction for k=36: {np.linalg.lstsq(X, y, rcond=None)[0] @ [1, 2.0 ** (-x * 36)]:.4f}")
