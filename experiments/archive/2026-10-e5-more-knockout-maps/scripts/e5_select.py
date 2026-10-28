# /// script
# dependencies = ["polars", "numpy"]
# ///
"""E5 rule selection: tethered rules (all rules of experiments/archive/2026-10-tether-rules/results/tether_screen.csv) from spread clusters (2% gap, as spread_clusters.py): one random rule
each from clusters at spread ~2.3, ~2.7, ~4.2, ~7.0, and two from the cluster of the two studied rules (~14.6), numpy seed 20261013, excluding the studied rules.
Writes experiments/archive/2026-10-e5-more-knockout-maps/results/e5_rules.txt (rule per line, with cluster id as comment-free second column). usage: uv run experiments/archive/2026-10-e5-more-knockout-maps/scripts/e5_select.py"""
import numpy as np, polars as pl
d = pl.read_csv("experiments/archive/2026-10-tether-rules/results/tether_screen.csv").filter(pl.col("spread_real").is_not_null() & (pl.col("spread_real") < 25)).sort("spread_real")
v = d["spread_real"].to_numpy(); lab = np.zeros(len(v), int)
for i in range(1, len(v)): lab[i] = lab[i - 1] + (v[i] > v[i - 1] * 1.02)
d = d.with_columns(cl=pl.Series(lab)); rng = np.random.default_rng(20261013)
out = []
for lo, hi, k in ((2.2, 2.4, 1), (2.6, 2.75, 1), (4.1, 4.4, 1), (6.8, 7.3, 1), (13.5, 15.7, 2)):
    pool = d.filter(pl.col("spread_real").is_between(lo, hi) & ~pl.col("rule").is_in(["RRRRRLLLLLL", "RLLLLRRRRLR"]))
    # keep to the dominant cluster in the window
    print("window", lo, hi, "pool", pool.height)
    if pool.height == 0: continue
    c = pool["cl"].mode()[0]; pool = pool.filter(pl.col("cl") == c)
    for i in rng.choice(pool.height, k, replace=False): out.append((pool["rule"][int(i)], float(pool["spread_real"][int(i)]), int(c), int(pool["area"][int(i)])))
for o in out: print(o)
open("experiments/archive/2026-10-e5-more-knockout-maps/results/e5_rules.txt", "w").write("\n".join(o[0] for o in out) + "\n")
