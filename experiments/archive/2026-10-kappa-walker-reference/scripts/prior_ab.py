# /// script
# dependencies = ["polars", "numpy"]
# ///
"""Prior (a, beta, kappa) of pw and rotor from EXISTING probe CSVs; used only to register numeric predictions."""
from pathlib import Path
import numpy as np, polars as pl
root = Path(__file__).resolve().parents[4]
def kunif(a, b):
    p = a * (1 - b); return 2 * (1 - 0.5 ** (1 - p)) / (1 - p)
def summ(path, prefixes, klo, khi):
    d = pl.read_csv(root / path).filter((pl.col("k") >= klo) & (pl.col("k") <= khi) & ~pl.col("escaped"))
    for pre in prefixes:
        A, B, K = [], [], []
        for r in sorted(r for r in d["rule"].unique() if r.startswith(pre)):
            g = d.filter(pl.col("rule") == r).sort("k")
            if g.height < 4: continue
            t, ar, p = (g[c].to_numpy().astype(float) for c in ("t", "area", "perimeter"))
            A.append(np.polyfit(np.log(t), np.log(ar), 1)[0]); B.append(np.polyfit(np.log(ar), np.log(p), 1)[0])
            K.append(np.mean((g["boundary_steps"] / (g["t"] // 2) / (g["perimeter"] / g["area"])).to_numpy()))
        a, b, k = np.mean(A), np.mean(B), np.mean(K)
        print(f"{path.split('/')[1][:30]:30s} {pre:10s} n={len(A):3d} a={a:.3f} beta={b:.3f} kappa={k:.3f} kunif={kunif(a,b):.3f} ratio={k/kunif(a,b):.3f}")
summ("experiments/archive/2026-10-a1-kappa/results/a1d_probe.csv", ["pw:0.25:", "pw:0.5:", "pw:0.75:"], 12, 22)
summ("experiments/archive/2026-10-calib-instrument-calibration/results/calib_rotor.csv", ["rotor:"], 12, 22)
