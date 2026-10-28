# /// script
# dependencies = ["polars", "numpy"]
# ///
"""E4: loss vs count of rare cells lost, patches vs swaps. Input experiments/archive/2026-10-knockout-maps/knock/RULE/e4.csv (+ coarse.csv for the determinism check).
Decision rule: notes/frontier-2026-10-13-results.md. usage: uv run experiments/archive/2026-10-e4-patch-vs-swap/scripts/e4_stats.py"""
import numpy as np, polars as pl
for rule in ("RRRRRLLLLLL", "RLLLLRRRRLR"):
    d = pl.read_csv(f"experiments/archive/2026-10-knockout-maps/knock/{rule}/e4.csv").filter(pl.col("ok") == 1)
    B = float(pl.read_csv(f"experiments/archive/2026-10-knockout-maps/knock/{rule}/base.csv")["near_home"][0])
    c0 = pl.read_csv(f"experiments/archive/2026-10-knockout-maps/knock/{rule}/coarse.csv")
    n0 = c0.height; same = bool(np.allclose(d.head(n0)["near_home"].to_numpy(), c0["near_home"].to_numpy(), atol=1e-4, equal_nan=True))
    d = d.with_columns(loss=B - pl.col("near_home"), ncell=pl.col("nvis") * 1.0,
                       stratum=pl.when(pl.col("rare_lost") == 0).then(pl.lit("0")).when(pl.col("rare_lost") == 1).then(pl.lit("1"))
                       .when(pl.col("rare_lost") == 2).then(pl.lit("2")).when(pl.col("rare_lost") <= 4).then(pl.lit("3-4"))
                       .when(pl.col("rare_lost") <= 8).then(pl.lit("5-8")).otherwise(pl.lit("9+")))
    pa = d.filter(pl.col("kind") == "patch"); sw = d.filter(pl.col("kind") == "swap")
    print(f"\n{rule}: base near_home {B:.4f}; determinism check vs stored coarse.csv: {'identical' if same else 'DIFFERENT'}; patches {pa.height}, swaps {sw.height}")
    rk = lambda v: np.argsort(np.argsort(v))
    for col in ("rare_lost", "rare_gained", "changed"):
        for kind, x in (("patch", pa), ("swap", sw), ("all", d)):
            v = x[col].to_numpy().astype(float); l = x["loss"].to_numpy()
            if v.std() > 0: print(f"  Spearman(loss, {col}) {kind}: {np.corrcoef(rk(v), rk(l))[0,1]:+.3f} (n={len(v)})")
    print("  stratum | patch n, mean loss +- SE | swap n, mean loss +- SE | diff / SE")
    ndiff = 0; nstr = 0
    for s in ("0", "1", "2", "3-4", "5-8", "9+"):
        a = pa.filter(pl.col("stratum") == s)["loss"].to_numpy(); b = sw.filter(pl.col("stratum") == s)["loss"].to_numpy()
        if len(a) >= 10 and len(b) >= 10:
            se = np.hypot(a.std(ddof=1) / np.sqrt(len(a)), b.std(ddof=1) / np.sqrt(len(b))); z = (a.mean() - b.mean()) / se
            nstr += 1; ndiff += abs(z) >= 2
            print(f"  {s:4s} | {len(a):4d}, {a.mean():+.4f} +- {a.std(ddof=1)/np.sqrt(len(a)):.4f} | {len(b):4d}, {b.mean():+.4f} +- {b.std(ddof=1)/np.sqrt(len(b)):.4f} | {z:+.1f}")
        else:
            print(f"  {s:4s} | patch n={len(a)}, swap n={len(b)}: fewer than 10 of one kind, not compared")
    print(f"  strata compared {nstr}, with |z| >= 2: {ndiff}  ->", "same curve" if nstr and ndiff == 0 else "contiguity matters / mixed" if nstr else "not testable")

# ---- refinement added after the first run (post hoc; the pre-registered "9+" stratum is open-ended and swaps of 100-400 cells fill it with far more rare cells than patches do)
print("\n== finer strata of rare_lost above 8 (post hoc)")
for rule in ("RRRRRLLLLLL", "RLLLLRRRRLR"):
    d = pl.read_csv(f"experiments/archive/2026-10-knockout-maps/knock/{rule}/e4.csv").filter(pl.col("ok") == 1)
    B = float(pl.read_csv(f"experiments/archive/2026-10-knockout-maps/knock/{rule}/base.csv")["near_home"][0]); d = d.with_columns(loss=B - pl.col("near_home"))
    print(rule)
    for lo, hi in ((9, 12), (13, 20), (21, 40), (41, 1000)):
        a = d.filter((pl.col("kind") == "patch") & pl.col("rare_lost").is_between(lo, hi))["loss"].to_numpy(); b = d.filter((pl.col("kind") == "swap") & pl.col("rare_lost").is_between(lo, hi))["loss"].to_numpy()
        if len(a) >= 5 and len(b) >= 5:
            z = (a.mean() - b.mean()) / np.hypot(a.std(ddof=1) / np.sqrt(len(a)), b.std(ddof=1) / np.sqrt(len(b)))
            print(f"  rare_lost {lo}-{hi}: patch n={len(a)} {a.mean():+.4f}; swap n={len(b)} {b.mean():+.4f}; z {z:+.1f}")
        else:
            print(f"  rare_lost {lo}-{hi}: patch n={len(a)}, swap n={len(b)} (too few)")
    # slope of loss on rare_lost for each kind, over rare_lost <= 20
    for kind in ("patch", "swap"):
        x = d.filter((pl.col("kind") == kind) & (pl.col("rare_lost") <= 20)); xs, ys = x["rare_lost"].to_numpy().astype(float), x["loss"].to_numpy()
        if len(xs) > 10: print(f"  {kind}: OLS slope of loss on rare_lost (rare_lost <= 20): {np.polyfit(xs, ys, 1)[0]:.5f} per rare cell (n={len(xs)})")
