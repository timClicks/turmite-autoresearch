# /// script
# dependencies = ["polars", "numpy"]
# ///
"""E5: knockout maps on more tethered rules and a shifted tile origin. Inputs experiments/archive/2026-10-e5-more-knockout-maps/knock_e5/*/{base.csv,coarse.csv} (+ the original maps for RRRRRLLLLLL / RLLLLRRRRLR).
Design/predictions: notes/frontier-2026-10-13-results.md. usage: uv run experiments/archive/2026-10-e5-more-knockout-maps/scripts/e5_stats.py"""
import numpy as np, polars as pl
from pathlib import Path
rng = np.random.default_rng(0)
def tiles(d):
    b = pl.read_csv(d / "base.csv"); B = float(b["near_home"][0]); mx, my = float(b["mx"][0]), float(b["my"][0])
    c = pl.read_csv(d / "coarse.csv").filter(pl.col("ok") == 1).with_columns(loss=B - pl.col("near_home"))
    null = c.filter(pl.col("kind") == "swap")["loss"].to_numpy()
    p95 = float(np.quantile(null, .95)); p95m3 = float(np.quantile(rng.choice(null, size=(20000, 3)).mean(axis=1), .95))
    t = c.filter((pl.col("kind") == "patch") & (pl.col("nvis") > 0)).group_by("x", "y").agg(n=pl.len(), loss=pl.col("loss").mean(), nex=(pl.col("loss") > p95).sum()).filter(pl.col("n") >= 3)
    t = t.with_columns(hot=(pl.col("loss") > p95m3) & (pl.col("nex") >= 2), r=(((pl.col("x") + 2.5 - mx) ** 2 + (pl.col("y") + 2.5 - my) ** 2) ** 0.5))
    return B, t, float(np.mean(null))
dirs = {}
for p in sorted(Path("experiments/archive/2026-10-e5-more-knockout-maps/knock_e5").glob("*")):
    if (p / "done").exists(): dirs[p.name] = p
dirs["RRRRRLLLLLL_orig"] = Path("experiments/archive/2026-10-knockout-maps/knock/RRRRRLLLLLL"); dirs["RLLLLRRRRLR_orig"] = Path("experiments/archive/2026-10-knockout-maps/knock/RLLLLRRRRLR")
res = {}
print("map | base near_home | tiles | hot tiles (frac) | max tile loss (relative to base) | mean swap-null loss")
for name, d in dirs.items():
    B, t, nm = tiles(d); res[name] = (B, t)
    print(f"{name:26s} | {B:.4f} | {t.height:4d} | {int(t['hot'].sum()):3d} ({t['hot'].mean():.3f}) | {t['loss'].max():.4f} ({t['loss'].max()/B:.3f}) | {nm:+.4f}")
rules = sorted({n.rsplit("_", 1)[0] for n in dirs if n.endswith(("_off0", "_off2"))})
print("\nper rule: hot fraction offset0 vs offset2; hot-set overlap (hot tile at one offset has a hot tile within 5 cells at the other)")
ok_frac = 0; ok_max = 0; n_new = 0
for r in rules:
    a, b = res.get(r + "_off0"), res.get(r + "_off2")
    if r == "RRRRRLLLLLL": a = res.get("RRRRRLLLLLL_orig")
    if not a or not b: continue
    ha, hb = a[1].filter(pl.col("hot")), b[1].filter(pl.col("hot"))
    def cover(h1, h2):
        if h1.height == 0: return float("nan")
        c2 = np.c_[h2["x"].to_numpy() + 2.5, h2["y"].to_numpy() + 2.5] if h2.height else np.zeros((0, 2))
        return float(np.mean([np.min(np.hypot(c2[:, 0] - x - 2.5, c2[:, 1] - y - 2.5)) <= 5 if len(c2) else False for x, y in zip(h1["x"], h1["y"])]))
    print(f"{r:14s} hot frac {a[1]['hot'].mean():.3f} vs {b[1]['hot'].mean():.3f} (diff {100*(b[1]['hot'].mean()-a[1]['hot'].mean()):+.1f} pts); coverage a->b {cover(ha, hb):.2f}, b->a {cover(hb, ha):.2f}; n hot {ha.height}/{hb.height}")
    if r != "RRRRRLLLLLL":
        n_new += 1; ok_frac += (0.02 <= a[1]["hot"].mean() <= 0.06); ok_max += (a[1]["loss"].max() / a[0] >= 0.10)
print(f"\nnew rules (offset 0): hot fraction in [2%,6%]: {ok_frac} of {n_new}; max coarse-tile relative loss >= 0.10: {ok_max} of {n_new} (prediction: all in band; >= 4 of 6 for the loss criterion)")
print("\nradial profile of mean tile loss (relative to base), 4 bins of r/r_max, for the cluster-19 rules and the studied pair:")
for name in ["RLLLLLLRLRR_off0", "RRRLLRRLLLL_off0", "RRRRRLLLLLL_orig", "RLLLLRRRRLR_orig"]:
    if name in res:
        B, t = res[name]; rr = t["r"].to_numpy(); edges = np.quantile(rr, [0, .25, .5, .75, 1.0])
        prof = [float(t["loss"].to_numpy()[(rr >= lo) & (rr <= hi)].mean() / B) for lo, hi in zip(edges[:-1], edges[1:])]
        print(f"  {name:22s} {np.round(prof, 4).tolist()}")
