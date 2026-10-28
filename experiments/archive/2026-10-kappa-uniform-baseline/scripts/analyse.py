# /// script
# dependencies = ["polars", "numpy"]
# ///
"""Probe kappa and area/perimeter exponents for the mean-field walker, vs the registered formula."""
from pathlib import Path
import numpy as np, polars as pl

root = Path(__file__).resolve().parents[1]
d = pl.read_csv(root / "results/mf_walker.csv").filter(pl.col("k") >= 12)
d = d.with_columns(
    kappa=(pl.col("boundary_steps") / (2.0 ** pl.col("k"))) / (pl.col("perimeter") / pl.col("area")),
    t_end=2.0 ** (pl.col("k") + 1),
)

def kunif(a, beta):
    p = a * (1 - beta)  # 2 * integral_{1/2}^{1} x^-p dx, closed form
    return 2 * (1 - 0.5 ** (1 - p)) / (1 - p)

lines = []
slopes, betas, kap = [], [], []
for s in sorted(d["seed"].unique()):
    g = d.filter(pl.col("seed") == s)
    lt, la, lp = np.log2(g["t_end"].to_numpy()), np.log2(g["area"].to_numpy()), np.log2(g["perimeter"].to_numpy())
    slopes.append(np.polyfit(lt, la, 1)[0]); betas.append(np.polyfit(la, lp, 1)[0]); kap.append(g["kappa"].to_numpy())
slopes, betas = np.array(slopes), np.array(betas); kap = np.array(kap)
a, b = slopes.mean(), betas.mean()
lines.append(f"seeds={len(slopes)}  windows k=12..{int(d['k'].max())}")
lines.append(f"area slope a = {a:.3f} (between-seed sd {slopes.std(ddof=1):.3f})")
lines.append(f"perimeter exponent beta = {b:.3f} (sd {betas.std(ddof=1):.3f})")
lines.append(f"kappa_unif(a,beta) = {kunif(a, b):.4f};  kappa_unif(2/3,1/2) = {kunif(2/3, .5):.4f}")
per_seed = kap.mean(axis=1)
lines.append(f"probe kappa, mean over windows & seeds = {per_seed.mean():.4f} (between-seed sd {per_seed.std(ddof=1):.4f})")
lines.append("probe kappa by window (mean over seeds): " + " ".join(f"{x:.3f}" for x in kap.mean(axis=0)))
(root / "results/analysis.txt").write_text("\n".join(lines) + "\n")
print("\n".join(lines))
