# /// script
# dependencies = ["polars", "numpy"]
# ///
"""B1b: patched-start ants to 2^34 (seeds 301-303), criterion vs the rotor (mean 0.6676, seed sd 0.0063): |mean a_inf - 0.6676| < 0.0145. Design: notes/frontier-2026-10-13-results.md."""
import glob, numpy as np, polars as pl
raw = pl.concat([pl.read_csv(f) for f in sorted(glob.glob("experiments/archive/2026-10-b1-exact-exponent/results/b1b_probe_??.csv"))])
res = {}
for (r,), g in raw.group_by("rule"):
    g = g.sort("k"); k = g["k"].to_list(); A = dict(zip(k, g["area"].to_list()))
    if 34 not in A: res[r] = None; continue
    a = {e: (np.log2(A[e]) - np.log2(A[e - 3])) / 3 for e in (26, 28, 30, 32, 34)}
    X = np.c_[np.ones(5), 2.0 ** (-np.array([26, 28, 30, 32, 34]) / 3)]; res[r] = np.linalg.lstsq(X, np.array(list(a.values())), rcond=None)[0][0]
rules = sorted({r.split("@")[0] for r in res}); n_match = 0; n_ok = 0
print("rule | a_inf per seed | mean | sd | match (|mean - 0.6676| < 0.0145)")
for ru in rules:
    v = [res[f"{ru}@{s}"] for s in (301, 302, 303) if res.get(f"{ru}@{s}") is not None]
    nesc = sum(res.get(f"{ru}@{s}", 0) is None for s in (301, 302, 303))
    if len(v) < 2: print(f"{ru:14s} fewer than 2 runs reached 2^34 ({nesc} escaped)"); continue
    m = np.mean(v); ok = abs(m - 0.6676) < 0.0145; n_ok += 1; n_match += ok
    print(f"{ru:14s} {np.round(v, 3).tolist()} mean {m:.4f} sd {np.std(v, ddof=1):.4f} {'MATCH' if ok else 'differs'}" + (f" ({nesc} escaped)" if nesc else ""))
print(f"\nrules matching the rotor: {n_match} of {n_ok} evaluable (prediction >= 12 of 15; RLL and RLR expected not to match)")
