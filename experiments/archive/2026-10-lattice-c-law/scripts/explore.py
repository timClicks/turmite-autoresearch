# /// script
# dependencies = ["polars", "numpy"]
# ///
"""POST HOC (unregistered) look at the hex strata after analyse.py: per-lead medians of 1/c, robust slopes, outliers.
usage: uv run experiments/archive/2026-10-lattice-c-law/scripts/explore.py > results/explore.txt"""
import runpy, sys
from pathlib import Path
import numpy as np
import polars as pl
sys.argv = ["analyse"]
import io, contextlib
with contextlib.redirect_stdout(io.StringIO()):
    ns = runpy.run_path(str(Path(__file__).with_name("analyse.py")))
kept = ns["kept"]
for (lat, s0), g in kept.group_by(["lattice", "stratum"], maintain_order=True):
    print(f"== {lat}/{s0}")
    for m in range(1, 6):
        x = 1 / g.filter(pl.col("lead") == m)["c"].to_numpy()
        print(f" lead {m}: n={len(x)} median 1/c {np.median(x):.2f}  q10/q90 {np.percentile(x,10):.2f}/{np.percentile(x,90):.2f}  max {x.max():.1f}")
    L, y = g["lead"].to_numpy().astype(float), 1 / g["c"].to_numpy()
    # Theil-Sen slope on per-lead medians
    med = [np.median(y[L == m]) for m in range(1, 6)]
    print(" slope of per-lead medians (lead 1->5)/4:", round((med[4] - med[0]) / 4, 3), " OLS on medians:", round(np.polyfit(range(1, 6), med, 1)[0], 3))
