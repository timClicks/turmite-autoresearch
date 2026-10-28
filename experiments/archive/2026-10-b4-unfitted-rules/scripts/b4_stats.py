# /// script
# dependencies = ["polars", "numpy"]
# ///
"""B4: why were 153 rules unfitted? Compare probe_all.csv (8192 board) with the 32768 rerun experiments/archive/2026-10-b4-unfitted-rules/results/b4_probe.csv.
Prediction/decision: notes/frontier-2026-10-13-results.md. usage: uv run experiments/archive/2026-10-b4-unfitted-rules/scripts/b4_stats.py"""
import polars as pl, numpy as np
rules = [l.strip() for l in open("experiments/archive/2026-10-b4-unfitted-rules/results/b4_unfitted.txt") if l.strip()]
old = pl.read_csv("experiments/archive/2026-10-probe-growth-census/results/probe_all.csv").filter(pl.col("rule").is_in(rules))
new = pl.read_csv("experiments/archive/2026-10-b4-unfitted-rules/results/b4_probe.csv")
print("153 rules; in original probe_all.csv:", old["rule"].n_unique(), " escaped on 8192 board:", int(old.group_by("rule").agg(e=pl.col("escaped").first())["e"].sum()))
print("rerun on 32768 board: rules", new["rule"].n_unique(), " escaped:", int(new.group_by("rule").agg(e=pl.col("escaped").first())["e"].sum()))
def stall(df):
    w = df.filter(pl.col("k").is_between(20, 26))
    g = w.group_by("rule").agg(n_win=pl.len(), zero=(pl.col("new_cells") == 0).sum(), last_new=pl.col("new_cells").sort_by("k").last(), area26=pl.col("area").sort_by("k").last())
    return g
gn = stall(new)
print(f"windows k=20..26 present in {int((gn['n_win'] == 7).sum())} of {gn.height} rules (rerun); rules with at least one window with zero new cells: {int((gn['zero'] > 0).sum())}")
print("rules with zero new cells in the LAST window (k=26):", int((gn["last_new"] == 0).sum()))
pa = pl.read_csv("experiments/archive/2026-10-probe-growth-census/results/probe_summary.csv")
print("area at 2^26 for these rules: quantiles 10/50/90% =", np.round(np.quantile(gn["area26"].to_numpy(), [.1, .5, .9]), 0).tolist(), "; census median area at k=26 for fitted blob rules:",
      float(pl.read_csv("experiments/archive/2026-10-probe-growth-census/results/probe_all.csv").filter((pl.col("k") == 26) & pl.col("rule").is_in(pa.filter(pl.col("cls") == "blob")["rule"])).get_column("area").median()))
print("rule lengths:", new.group_by("rule").agg(n=pl.col("rule").first().str.len_chars())["n"].value_counts().sort("n").rows())
