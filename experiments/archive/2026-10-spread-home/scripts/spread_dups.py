# /// script
# dependencies = ["polars", "numpy"]
# ///
"""Review check: do different tethered rules share exactly equal spreads (a sign of shared orbits)?  Input experiments/archive/2026-10-tether-rules/results/tether_screen.csv."""
import polars as pl, numpy as np
d = pl.read_csv("experiments/archive/2026-10-tether-rules/results/tether_screen.csv").filter(pl.col("spread_real").is_not_null())
vc = d.group_by("spread_real").agg(n=pl.len(), rules=pl.col("rule"), areas=pl.col("area")).sort(["n", "spread_real"], descending=[True, False])
print("distinct spread_real values (2 decimals):", vc.height, "of", d.height, "rules")
print("values shared by >=2 rules:", vc.filter(pl.col("n") >= 2).height, "covering", int(vc.filter(pl.col("n") >= 2)["n"].sum()), "rules")
print(vc.head(12).select(["spread_real", "n"]).rows())
top = vc.head(1).row(0, named=True); print("most common value", top["spread_real"], "shared by", top["n"], "rules, e.g.", top["rules"][:6], "areas", top["areas"][:6])
# expected collisions if spreads were independent draws from the empirical distribution of values at 0.01 resolution
rng = np.random.default_rng(1); vals = d["spread_real"].to_numpy()
sim = [len(np.unique(rng.permutation(vals) + rng.uniform(-0.005, 0.005, len(vals)).round(2))) for _ in range(5)]
print("distinct values if the same values were jittered by +-0.005:", sim)
print("rules with spread_real < 5:", (d['spread_real'] < 5).sum(), " 5-10:", ((d['spread_real'] >= 5) & (d['spread_real'] < 10)).sum(), " >=10:", (d['spread_real'] >= 10).sum())
