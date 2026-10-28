# /// script
# dependencies = ["polars", "numpy"]
# ///
"""E6: fraction of the 2^24-hot tiles that are hot (fresh permutations) at earlier ages. Design: notes/frontier-2026-10-13-results.md. usage: uv run experiments/archive/2026-10-e6-hot-window-age/scripts/e6_stats.py"""
import numpy as np, polars as pl
rng = np.random.default_rng(0)
for rule in ("RRRRRLLLLLL", "RLLLLRRRRLR"):
    print(f"\n{rule}")
    out = {}
    for A in (18, 20, 22, 24):
        try:
            b = pl.read_csv(f"experiments/archive/2026-10-knockout-maps/knock/{rule}/e6_base_k{A}.txt"); B = float(b["near_home"][0])
            c = pl.read_csv(f"experiments/archive/2026-10-knockout-maps/knock/{rule}/e6_k{A}.csv").filter(pl.col("ok") == 1).with_columns(loss=B - pl.col("near_home"))
        except Exception as e:
            print(f"  age 2^{A}: no data ({type(e).__name__})"); continue
        null = c.filter(pl.col("kind") == "swap")["loss"].to_numpy(); p95 = float(np.quantile(null, .95)); p95m3 = float(np.quantile(rng.choice(null, size=(20000, 3)).mean(axis=1), .95))
        p = c.filter((pl.col("kind") == "patch") & (pl.col("nvis") > 0))
        t = p.group_by("x", "y").agg(n=pl.len(), loss=pl.col("loss").mean(), nex=(pl.col("loss") > p95).sum()).filter(pl.col("n") >= 3)
        t = t.with_columns(hot=(pl.col("loss") > p95m3) & (pl.col("nex") >= 2))
        n_all = c.filter(pl.col("kind") == "patch").select(pl.struct("x", "y").n_unique()).item()
        out[A] = (B, t.height, int(t["hot"].sum()), n_all)
        print(f"  age 2^{A}: intact near_home {B:.3f}{' (below 0.2: no home yet, excluded)' if B < 0.2 else ''}; hot-list tiles present (visited cells) {t.height} of {n_all}; hot among present {int(t['hot'].sum())} ({t['hot'].mean() if t.height else float('nan'):.2f}); null p95 loss {p95:.4f}, mean-of-3 p95 {p95m3:.4f}; mean tile loss {t['loss'].mean() if t.height else float('nan'):.4f}")
