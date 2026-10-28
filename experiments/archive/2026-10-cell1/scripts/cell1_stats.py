# /// script
# dependencies = ["polars", "numpy"]
# ///
"""Item 10: summarise examples/cell1.rs output (experiments/archive/2026-10-cell1/results/RULE_{scan,null,greedy,lone}.csv).
Loss = baseline near_home - near_home. Baselines from experiments/archive/2026-10-knockout-maps/knock/RULE/summary.json (read only)."""
import json
import numpy as np
import polars as pl

for rule in ["RRRRRLLLLLL", "RLLLLRRRRLR"]:
    B = json.load(open(f"experiments/archive/2026-10-knockout-maps/knock/{rule}/summary.json"))["baseline_near_home"]
    sc = pl.read_csv(f"experiments/archive/2026-10-cell1/results/{rule}_scan.csv").with_columns(loss=B - pl.col("near_home"))
    nu = pl.read_csv(f"experiments/archive/2026-10-cell1/results/{rule}_null.csv").with_columns(loss=B - pl.col("near_home"))
    gr = pl.read_csv(f"experiments/archive/2026-10-cell1/results/{rule}_greedy.csv").with_columns(loss=B - pl.col("near_home"))
    lo = pl.read_csv(f"experiments/archive/2026-10-cell1/results/{rule}_lone.csv").with_columns(loss=B - pl.col("near_home"))
    print(f"\n=== {rule}: baseline {B}")
    nl = nu["loss"].to_numpy()
    print(f"single-cell NULL (200 random visited cells): mean {nl.mean():.4f} sd {nl.std(ddof=1):.4f} p95 {np.quantile(nl, .95):.4f} p99 {np.quantile(nl, .99):.4f} max {nl.max():.4f}")
    cells = sc.group_by(["x", "y"], maintain_order=True).agg(old=pl.col("old").first(), worst=pl.col("loss").max(), mean=pl.col("loss").mean()).sort("worst", descending=True)
    print(f"scan: {cells.height} cells ({sc.height} recolourings); cells with worst loss > null p95: {(cells['worst'] > np.quantile(nl, .95)).sum()}, > null max: {(cells['worst'] > nl.max()).sum()}")
    print("top 10 cells (x,y,old colour,worst loss,mean loss over recolourings):")
    print(cells.head(10))
    print("greedy cumulative (k most damaging cells, each at its worst colour):")
    print(gr.select(["k", "x", "y", "new", "loss"]))
    top = cells.row(0)
    l2 = lo["loss"].to_numpy()
    print(f"after fixing the top cell {top[:2]} (loss {top[3]:.4f}): second-cell rescan max loss {l2.max():.4f}, mean {l2.mean():.4f}; n above top-alone: {(l2 > top[3]).sum()} of {len(l2)}")
