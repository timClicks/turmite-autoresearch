# /// script
# dependencies = ["numpy", "polars"]
# ///
"""growth_fit.py : area and width exponents over octaves k in [K0, K1] per walker, grouped; between-seed sd."""
import sys, numpy as np, polars as pl
from pathlib import Path
R = Path(__file__).resolve().parents[1]
K0, K1 = 21, 27  # revised after seeing area/t per octave: regime change near k=16-18 (see README log); first try was 16-26
df = pl.read_csv(R / "results/growth_probe.csv")
def fit(g, col):
    g = g.filter((pl.col("k") >= K0) & (pl.col("k") <= K1)).sort("k")
    return np.polyfit(np.log(g["t"].to_numpy()), np.log(g[col].to_numpy().astype(float)), 1)[0]
rows = []
for rule in df["rule"].unique(maintain_order=True):
    g = df.filter(pl.col("rule") == rule)
    esc = g["escaped"][0]
    if esc: continue  # random walk leaves the board: uninformative here
    if esc: continue  # random walks leave the board: uninformative here
    last = g.filter(pl.col("k") == K1)
    rows.append((rule, fit(g, "area"), fit(g, "width"), last["area"][0] / last["t"][0], last["width"][0], esc))
out = pl.DataFrame(rows, schema=["walker", "area_exp", "width_exp", "area_per_t@k27", "width@k27", "escaped"], orient="row")
print(out)
seeds = out.filter(pl.col("walker").str.contains("@"))
print(f"\nRLLLLLLLRRLRR@seed (n={seeds.height}): area_exp {seeds['area_exp'].mean():.4f} sd {seeds['area_exp'].std():.4f};"
      f" width_exp {seeds['width_exp'].mean():.4f} sd {seeds['width_exp'].std():.4f}")
