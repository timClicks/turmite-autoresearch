# /// script
# requires-python = ">=3.12"
# dependencies = ["numpy", "polars"]
# ///
"""Stage 1, P1-P3 and P5: cycle clock, growth, reach and the |x|^2 slope from cycles.csv.

usage: uv run experiments/archive/2026-10-rlrlll-macro-transition/scripts/stage1_cycles.py CYCLES_CSV
Prints a report; the README quotes it. Deterministic (no randomness).
"""
import hashlib
import sys
from pathlib import Path

import numpy as np
import polars as pl

path = Path(sys.argv[1])
print(f"input {path} sha256 {hashlib.sha256(path.read_bytes()).hexdigest()}")
df = pl.read_csv(path)
print(f"cycles: {df.height}, first t_end {df['t_end'][0]}, last t_end {df['t_end'][-1]}")

T = df["steps"].to_numpy()
L = df["L_prev_col"].to_numpy()
span = (df["bot_prev_col"] - df["top_prev_col"] + 1).to_numpy()
reach = df["reach"].to_numpy()
x = df["x_f"].to_numpy()

print(f"\nL == top-to-bottom span for {np.mean(L == span):.4f} of cycles")


def affine_report(name, T, L):
    A = np.vstack([L, np.ones_like(L)]).T.astype(float)
    (a, b), *_ = np.linalg.lstsq(A, T.astype(float), rcond=None)
    print(f"\n[{name}] least squares T = {a:.6f} L + {b:.3f}")
    # Exact-integer test: most common integer slope from successive differences, then residual classes.
    dT, dL = np.diff(T), np.diff(L)
    ok = dL != 0
    slopes = dT[ok] / dL[ok]
    vals, cnt = np.unique(np.round(slopes, 6), return_counts=True)
    top = np.argsort(-cnt)[:5]
    print("  most common dT/dL:", [(float(vals[i]), int(cnt[i])) for i in top])
    for alpha in (12, int(round(a))):
        r = T - alpha * L
        vals, cnt = np.unique(r, return_counts=True)
        order = np.argsort(-cnt)[:6]
        share = cnt[order].sum() / len(r)
        print(f"  alpha={alpha}: beta = T - alpha L, top values {[(int(vals[i]), int(cnt[i])) for i in order]}"
              f" (top-6 share {share:.4f}; top-1 share {cnt[order[0]] / len(r):.4f})")


affine_report("L = visited count", T, L)

g = np.diff(L)
vals, cnt = np.unique(g, return_counts=True)
print(f"\nP2 growth g_k = L_(k+1) - L_k: mean {g.mean():.4f}, values {list(zip(vals.tolist(), cnt.tolist()))}")
for p in range(1, 9):
    tail = g[len(g) // 10:]
    if len(tail) > p and np.all(tail[p:] == tail[:-p]):
        print(f"  g is periodic with period {p} after the first 10% of cycles")
        break
else:
    print("  g is not periodic with period <= 8 after the first 10% of cycles")

print(f"\nP3 reach: max {reach.max()}, quantiles 50/95/99/100 {np.percentile(reach, [50, 95, 99, 100]).tolist()}")
print(f"  reach after first 10% of cycles: max {reach[len(reach) // 10:].max()}")

ax = np.abs(x).astype(float)
dx2 = np.diff(ax**2) / T[1:]
q = np.array_split(np.arange(len(dx2)), 10)
print("\nP5 d|x|^2/dt by decile of cycles (mean |x|, slope):")
for idx in q:
    print(f"  |x| {ax[1:][idx].mean():8.0f}  slope {dx2[idx].mean():.5f}  L {L[1:][idx].mean():8.1f}")
