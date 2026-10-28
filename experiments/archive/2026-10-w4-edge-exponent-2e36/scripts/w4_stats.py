# /// script
# dependencies = ["polars", "numpy"]
# ///
"""W4: ants' local edge exponent beta(k) = dlog P / dlog A between k-4 and k, to 2^36. Input experiments/archive/2026-10-w4-edge-exponent-2e36/results/w4_probe.csv. Decision rule: notes (W4), copied from A2b."""
import numpy as np, polars as pl
d = pl.read_csv("experiments/archive/2026-10-w4-edge-exponent-2e36/results/w4_probe.csv")
res = {}
for (r,), g in d.group_by("rule"):
    g = g.sort("k"); P = dict(zip(g["k"].to_list(), g["perimeter"].to_list())); A = dict(zip(g["k"].to_list(), g["area"].to_list()))
    res[r] = {e: np.log(P[e] / P[e - 4]) / np.log(A[e] / A[e - 4]) for e in range(20, 37, 2) if e in P and e - 4 in P}
    print(f"{r:20s} " + " ".join(f"{e}:{res[r][e]:.3f}" for e in sorted(res[r])))
print("escaped/short:", [r for r, v in res.items() if 36 not in v])
for e in range(24, 37, 2):
    v = [s[e] for s in res.values() if e in s]
    if v: print(f"k={e}: mean {np.mean(v):.4f} +- {np.std(v, ddof=1)/np.sqrt(len(v)):.4f} (n={len(v)}, sd {np.std(v, ddof=1):.4f})")
v = [s[36] for s in res.values() if 36 in s]
if v: m = np.mean(v); print("decision:", "favours 1/2" if m <= 0.506 else "plateau above 1/2" if m >= 0.511 else "inconclusive", f"(mean beta(36) = {m:.4f})")
# Paired statistic (W4 addendum): delta = beta(36) - beta(32) per run; SE over the 6 rule means (blank + patched start averaged per rule).
dl = {r: res[r][36] - res[r][32] for r in res if 36 in res[r] and 32 in res[r]}
if dl:
    by = {}
    for r, x in dl.items(): by.setdefault(r.split("@")[0], []).append(x)
    m = np.array([np.mean(v) for v in by.values()])
    print(f"paired delta = beta(36)-beta(32): runs {len(dl)}, rules {len(m)}, mean {m.mean():+.4f} +- {m.std(ddof=1)/np.sqrt(len(m)):.4f} (SE over rule means; rotor reference about -0.012 +- 0.004)")
    print("paired decision:", "plateau (delta > -0.006)" if m.mean() > -0.006 else "falls like the rotor (delta <= -0.010)" if m.mean() <= -0.010 else "inconclusive")
