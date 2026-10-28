# /// script
# dependencies = ["polars", "numpy"]
# ///
"""E1c: Rayleigh test on lobe bearings across the tethered ages of RRRRRLLLLLL. Rule: notes/frontier-2026-10-13-results.md."""
import math, numpy as np, polars as pl
from pathlib import Path
rng = np.random.default_rng(0)
def lobe(d):
    b = pl.read_csv(d / "base.csv"); B = float(b["near_home"][0]); mx, my = float(b["mx"][0]), float(b["my"][0])
    c = pl.read_csv(d / "coarse.csv").filter(pl.col("ok") == 1).with_columns(loss=B - pl.col("near_home"))
    null = c.filter(pl.col("kind") == "swap")["loss"].to_numpy(); p95 = np.quantile(null, .95); p3 = np.quantile(rng.choice(null, size=(20000, 3)).mean(axis=1), .95)
    t = c.filter((pl.col("kind") == "patch") & (pl.col("nvis") > 0)).group_by("x", "y").agg(n=pl.len(), loss=pl.col("loss").mean(), nex=(pl.col("loss") > p95).sum()).filter(pl.col("n") >= 3)
    h = t.filter((pl.col("loss") > p3) & (pl.col("nex") >= 2))
    dx = h["x"].to_numpy() + 2.5 - mx; dy = h["y"].to_numpy() + 2.5 - my; th = np.arctan2(dx, -dy)
    return B, h.height, th
maps = {"k24": Path("experiments/archive/2026-10-knockout-maps/knock/RRRRRLLLLLL")}
for k in (20, 21, 22, 23, 25, 26, 27): maps[f"k{k}"] = Path(f"experiments/archive/2026-10-e1-one-sided-hot-region/knock_e1/RRRRRLLLLLL_k{k}")
rows = []
for name, p in maps.items():
    try: B, n, th = lobe(p)
    except Exception as e: print(name, "missing", type(e).__name__); continue
    R = float(np.hypot(np.cos(th).mean(), np.sin(th).mean())) if n else float("nan"); mean = math.degrees(math.atan2(np.sin(th).mean(), np.cos(th).mean())) % 360 if n else float("nan")
    ok = B >= 0.3 and n >= 5; rows.append((name, B, n, mean, R, ok)); print(f"{name}: intact near_home {B:.3f}, hot tiles {n}, bearing {mean:.0f} deg, R {R:.2f}, {'USED' if ok else 'excluded (untethered or < 5 hot tiles)'}")
u = [r for r in rows if r[5]]
if len(u) >= 3:
    ang = np.radians([r[3] for r in u]); R = float(np.hypot(np.cos(ang).mean(), np.sin(ang).mean())); n = len(u); Z = n * R * R
    p = math.exp(math.sqrt(1 + 4 * n + 4 * (n * n - (n * R) ** 2)) - (1 + 2 * n))
    print(f"\nRayleigh test on {n} ages: mean resultant length {R:.2f}, Z = {Z:.2f}, p = {p:.3f}; verdict: {'rule-fixed lobe' if p < 0.05 else 'no concentration (field-tied)' if p >= 0.2 and n >= 5 else 'inconclusive'}")
