# /// script
# dependencies = ["polars", "numpy"]
# ///
"""Review follow-up: the 560 tethered (log-class) rules share a few discrete spread values. Cluster spread_real (relative gap 2%) and describe the clusters."""
import polars as pl, numpy as np
d = pl.read_csv("experiments/archive/2026-10-tether-rules/results/tether_screen.csv").filter(pl.col("spread_real").is_not_null() & (pl.col("spread_real") < 25)).sort("spread_real")
v = d["spread_real"].to_numpy(); lab = np.zeros(len(v), int)
for i in range(1, len(v)): lab[i] = lab[i - 1] + (v[i] > v[i - 1] * 1.02)
d = d.with_columns(cluster=pl.Series(lab))
cl = d.group_by("cluster", maintain_order=True).agg(n=pl.len(), lo=pl.col("spread_real").min(), hi=pl.col("spread_real").max(), med_area=pl.col("area").median(),
                               min_area=pl.col("area").min(), max_area=pl.col("area").max(), ns=pl.col("rule").str.len_chars().mean(), ex=pl.col("rule").head(3)).sort("cluster")
pl.Config.set_tbl_rows(80); pl.Config.set_tbl_width_chars(200); pl.Config.set_fmt_str_lengths(60)
print("clusters:", cl.height, " sizes (n rules):", cl["n"].to_list())
print(cl.select(["cluster", "n", "lo", "hi", "min_area", "max_area", "ex"]).head(40))
big = cl.filter(pl.col("n") >= 5)
print("clusters with >= 5 rules:", big.height, "covering", int(big["n"].sum()), "of", d.height, "rules")
vals = np.sort(np.array([(a + b) / 2 for a, b in zip(cl["lo"], cl["hi"])]))
print("cluster centres:", np.round(vals, 2).tolist())
print("1/(spread/sqrt(6)) = v/D implied by an exponential law, for the large clusters:", np.round(np.sqrt(6) / np.array([(a + b) / 2 for a, b in zip(big['lo'], big['hi'])]), 3).tolist())

# which rule lengths / run structures populate each cluster?
import re
d = d.with_columns(n=pl.col("rule").str.len_chars(), runs=pl.col("rule").map_elements(lambda s: len(re.findall(r"R+|L+", s)), return_dtype=pl.Int64))
print("\ncluster -> (spread centre, rule lengths present, number of runs present)")
for c in range(0, 28):
    g = d.filter(pl.col("cluster") == c)
    if g.height >= 3:
        print(f"  {c:2d}: spread {g['spread_real'].median():5.2f}  n in {sorted(set(g['n'].to_list()))}  runs in {sorted(set(g['runs'].to_list()))}  count {g.height}")
two = d.filter(pl.col("runs") <= 3)
print("\nrules with <= 3 runs (blocky):", two.height, "; spread_real * n: quantiles 10/50/90% =", np.round(np.quantile((two["spread_real"] * two["n"]).to_numpy(), [.1, .5, .9]), 1))
print("by n (median spread of rules with <= 3 runs):", {int(n[0]): round(float(g['spread_real'].median()), 2) for n, g in two.group_by('n', maintain_order=True) if g.height >= 3})
