# /// script
# dependencies = ["polars", "numpy"]
# ///
"""Item 12: when does the field first support a home? Input experiments/archive/2026-10-formage-age/results/formage_all.csv (tetherlab formage, 24 patched seeds + blank start, ages 2^7..2^24, trial 2^19)."""
import numpy as np, polars as pl
d = pl.read_csv("experiments/archive/2026-10-formage-age/results/formage_all.csv", has_header=False, new_columns=["rule", "seed", "k", "area", "extent", "real", "shuf"])
for rule in d["rule"].unique(maintain_order=True):
    g = d.filter(pl.col("rule") == rule)
    print(f"\n{rule}: spread of a fresh ant on the real field / on a shuffled field, by age 2^k (mean over {g['seed'].n_unique()} starts; sd of real in brackets); area")
    for k in range(7, 25, 1):
        h = g.filter(pl.col("k") == k)
        if h.height == 0: continue
        r, s = h["real"].to_numpy(), h["shuf"].to_numpy()
        if k in (7, 8, 9, 10, 11, 12, 14, 16, 18, 20, 22, 24):
            print(f"  k={k:2d}: real {r.mean():5.1f} ({r.std(ddof=1):3.1f})  shuffled {s.mean():5.1f}  area {h['area'].mean():7.0f} extent {h['extent'].mean():5.0f}")
    late = g.filter(pl.col("k") >= 16)
    print(f"  starts whose real spread at k>=16 ever exceeds 1.5 x the rule's median late real spread ({late['real'].median():.1f}):", late.filter(pl.col("real") > 1.5 * late["real"].median()).select(["seed", "k"]).rows())
