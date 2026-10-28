# /// script
# dependencies = ["polars", "numpy"]
# ///
"""Spread of census kappa relative to the per-rule uniform reference kappa_unif(a, beta).

Run: uv run experiments/archive/2026-10-kappa-uniform-baseline/scripts/census_spread.py
Single run per rule, so values carry run-to-run noise (ln-kappa reliability ~0.6).
"""
from pathlib import Path
import numpy as np, polars as pl

root = Path(__file__).resolve().parents[4]
d = pl.read_csv(root / "experiments/archive/2026-10-probe-growth-census/results/probe_summary.csv").filter(pl.col("cls") == "blob")
out = []
def show(name, x):
    q = np.quantile(x, [.05, .25, .5, .75, .95])
    out.append(f"{name}: n={len(x)} q05/25/50/75/95={np.round(q,3).tolist()} geomean={np.exp(np.log(x).mean()):.3f} sd_ln={np.log(x).std():.3f}")
k = d["kappa"].to_numpy(); s = np.abs(d["g_k"].to_numpy()) < 0.05
a = d["a"].to_numpy(); b = d["beta"].to_numpy()
e = a * (1 - b)
ku = 2 * (1 - 0.5 ** (1 - e)) / (1 - e)  # 2 * int_{1/2}^1 x^-e dx
show("kappa, all blob", k)
show("kappa, stationary (|g_k|<0.05)", k[s])
show("kappa_unif(a,beta), stationary", ku[s])
show("kappa/kappa_unif, stationary", (k / ku)[s])
out.append(f"fraction stationary rules with kappa/kappa_unif >= 1: {np.mean((k/ku)[s] >= 1):.3f}")
(root / "experiments/archive/2026-10-kappa-uniform-baseline/results/census_spread.txt").write_text("\n".join(out) + "\n")
print("\n".join(out))
