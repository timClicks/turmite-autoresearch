# /// script
# dependencies = ["polars", "numpy"]
# ///
"""E2b: sensitive-disc radius vs near_home radius R (4,6,10,15,22) with an all-tile weighted estimator and the hot-tile estimator. Decision: notes/frontier-2026-10-13-results.md."""
import numpy as np, polars as pl
def load(rule, R):
    sfx = "" if R == 10 else f"_r{R}"
    d = pl.read_csv(f"experiments/archive/2026-10-knockout-maps/knock/{rule}/coarse{sfx}.csv").filter(pl.col("ok") == 1)
    b = pl.read_csv(f"experiments/archive/2026-10-knockout-maps/knock/{rule}/base.csv" if R == 10 else f"experiments/archive/2026-10-knockout-maps/knock/{rule}/base_r{R}.txt")
    return d, float(b["near_home"][0]), float(b["mx"][0]), float(b["my"][0])
rng = np.random.default_rng(20261013)
for rule in ("RRRRRLLLLLL", "RLLLLRRRRLR"):
    print("\n" + rule); out = {}
    for R in (4, 6, 10, 15, 22):
        try: d, B, mx, my = load(rule, R)
        except Exception as e: print(f"  R={R}: missing ({type(e).__name__})"); continue
        sw = d.filter(pl.col("kind") == "swap"); null = (B - sw["near_home"].to_numpy()) / B
        t = d.filter((pl.col("kind") == "patch") & (pl.col("nvis") >= 5)).group_by("x", "y").agg(loss=((B - pl.col("near_home")) / B).mean())
        r = np.hypot(t["x"].to_numpy() + 2.5 - mx, t["y"].to_numpy() + 2.5 - my); w = np.maximum(t["loss"].to_numpy() - null.mean(), 0)
        est = lambda w, r: np.sqrt((w * r ** 2).sum() / max(w.sum(), 1e-12))
        rad = est(w, r); bs = [est(w[i], r[i]) for i in (rng.integers(0, len(w), len(w)) for _ in range(1000))]
        p95 = np.quantile(null, .95); hot = t["loss"].to_numpy() > p95
        radh = est(t["loss"].to_numpy()[hot], r[hot]) if hot.sum() > 2 else float("nan")
        out[R] = (rad, np.std(bs)); print(f"  R={R:2d}: base {B:.3f}; all-tile radius {rad:.1f} +- {np.std(bs):.1f}; hot-tile radius {radh:.1f} ({int(hot.sum())} tiles)")
    if 4 in out and 22 in out:
        q = out[22][0] / out[4][0]; se = q * np.hypot(out[22][1] / out[22][0], out[4][1] / out[4][0])
        print(f"  ratio r(22)/r(4) = {q:.2f} +- {se:.2f} (R ratio 5.5): {'tracks R' if q >= 2.5 else 'excursion scale' if q <= 1.5 else 'inconclusive'}")
