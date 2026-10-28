# /// script
# dependencies = ["polars", "numpy"]
# ///
"""What labels the discrete home types?  Within-group spread of spread_real for groupings of the 556 tethered rules by simple rule invariants."""
import polars as pl, numpy as np
d = pl.read_csv("experiments/archive/2026-10-tether-rules/results/tether_screen.csv").filter(pl.col("spread_real").is_not_null() & (pl.col("spread_real") < 25))
d = d.with_columns(n=pl.col("rule").str.len_chars(), nR=pl.col("rule").str.count_matches("R")).with_columns(
    nL=pl.col("n") - pl.col("nR")).with_columns(net=pl.col("nR") - pl.col("nL")).with_columns(net4=pl.col("net") % 4, net8=pl.col("net") % 8)
lv = np.log(d["spread_real"].to_numpy())
def explained(keys):
    g = d.with_columns(lv=pl.Series(lv)).group_by(keys, maintain_order=True).agg(m=pl.col("lv").mean(), v=pl.col("lv").var(ddof=0), k=pl.len())
    within = float((g["v"].fill_null(0) * g["k"]).sum() / g["k"].sum()); tot = float(lv.var())
    return 1 - within / tot, g.height
for keys in [["n"], ["nR"], ["n", "nR"], ["n", "net4"], ["n", "net8"], ["net"], ["net4"]]:
    r2, k = explained(keys)
    print(f"group by {keys}: {k:3d} groups, share of var(log spread) explained {r2:.3f}")
g = d.group_by(["n", "nR"], maintain_order=True).agg(k=pl.len(), med=pl.col("spread_real").median(), lo=pl.col("spread_real").min(), hi=pl.col("spread_real").max()).sort(["n", "nR"])
pl.Config.set_tbl_rows(80)
print(g.filter(pl.col("k") >= 5))
