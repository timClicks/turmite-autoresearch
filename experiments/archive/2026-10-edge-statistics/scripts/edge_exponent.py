# /// script
# dependencies = ["polars", "numpy", "scipy"]
# ///
"""Item 8: is the perimeter-vs-area exponent beta (finite-window 0.52) a finite-time effect that
converges to 1/2?  Inputs: long.csv (six ants to 2^32), calib_rotor.csv (rotor, 2^27), probe_all.csv.
Method: (a) local slope of log P vs log A between octaves k and k+4; (b) a fixed-exponent fit
P = c1 A^(1/2) + c0 and P = c1 A^b free, compare residuals over k in 17..32 (ants) / 17..27 (rotor).
Run: uv run experiments/archive/2026-10-edge-statistics/scripts/edge_exponent.py"""
import numpy as np
import polars as pl

long = pl.read_csv("experiments/archive/2026-10-probe-growth-census/results/long.csv")
rot = pl.read_csv("experiments/archive/2026-10-calib-instrument-calibration/results/calib_rotor.csv", infer_schema_length=5000)
print("calib_rotor columns:", rot.columns[:14])


def local(df, step=4, lo=14):
    out = {}
    ks = sorted(df["k"].unique().to_list())
    for k in ks:
        if k < lo or k + step not in ks:
            continue
        a = df.filter(pl.col("k").is_in([k, k + step])).sort("k")
        out[k] = np.log(a["perimeter"][1] / a["perimeter"][0]) / np.log(a["area"][1] / a["area"][0])
    return out


def fits(A, P):
    # free exponent
    b, lc = np.polyfit(np.log(A), np.log(P), 1)
    # P = c1 sqrt(A) + c0 by least squares
    M = np.c_[np.sqrt(A), np.ones_like(A)]
    (c1, c0), *_ = np.linalg.lstsq(M / P[:, None], np.ones_like(P), rcond=None)
    res_fixed = np.sqrt(np.mean((np.log(c1 * np.sqrt(A) + c0) - np.log(P)) ** 2))
    res_free = np.sqrt(np.mean((lc + b * np.log(A) - np.log(P)) ** 2))
    # constant-ratio model P = c1 sqrt(A): no offset
    c = np.exp(np.mean(np.log(P / np.sqrt(A))))
    res_pure = np.sqrt(np.mean((np.log(c * np.sqrt(A)) - np.log(P)) ** 2))
    return b, c1, c0, res_fixed, res_free, res_pure


print("\n== ants: six rules to 2^32; local slope (k..k+4) of log P vs log A")
tab = {}
for (r,), g in long.group_by("rule", maintain_order=True):
    g = g.filter(~pl.col("escaped"))
    loc = local(g)
    tab[r] = loc
    ks = sorted(loc)
    sel = [k for k in ks if k in (14, 18, 22, 26, 28)]
    print(f"{r:14s}", " ".join(f"k{k}:{loc[k]:.3f}" for k in sel))
    gg = g.filter(pl.col("k") >= 17)
    b, c1, c0, rf, rfree, rp = fits(gg["area"].to_numpy().astype(float), gg["perimeter"].to_numpy().astype(float))
    print(f"   k>=17 free beta={b:.3f}; P=c1*sqrt(A)+c0: c1={c1:.3f} c0={c0:.1f}; rms log-resid: fixed+offset {rf:.4f} free {rfree:.4f} pure-sqrt {rp:.4f}")
# average local slope across rules per window
ks = sorted(set.intersection(*[set(v) for v in tab.values()]))
print("mean local slope across the six rules:", " ".join(f"k{k}:{np.mean([tab[r][k] for r in tab]):.3f}" for k in ks if k % 2 == 0))

print("\n== rotor (calib_rotor.csv)")
if "rule" in rot.columns:
    rot = rot.rename({"rule": "seed"})
rot = rot.filter(~pl.col("escaped")) if "escaped" in rot.columns else rot
tabr = {}
for (s,), g in rot.group_by("seed", maintain_order=True):
    tabr[s] = local(g, lo=10)
ks = sorted(set.intersection(*[set(v) for v in tabr.values()]))
print(f"{len(tabr)} walkers; mean local slope:", " ".join(f"k{k}:{np.mean([tabr[s][k] for s in tabr]):.3f}" for k in ks if k % 2 == 0))
