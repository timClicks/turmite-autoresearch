# /// script
# dependencies = ["numpy", "polars"]
# ///
"""Item 2 calibration: run mixing.py's MSD-slope estimator on a walker whose answer is
exact: an i.i.d. persistent walk (each step turns R with prob q else L, then moves).
Prediction (written 2026-10-12 before running): measured/predicted slope = 1.00 +- 0.03
at lags 16..1024 over 2^22 steps for q in {0.3,0.5,0.7,0.9}. Also checks the
estimator on a ballistic-biased control (q=0.9 has a = 0.64, strong anticorrelation).
Run: uv run experiments/archive/2026-10-mixing/scripts/mixing_calib.py"""
import sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "_lib"))
from mixing import msd

DX = np.array([0, 1, 0, -1]); DY = np.array([-1, 0, 1, 0])
rng = np.random.default_rng(20261012)
for q in (0.3, 0.5, 0.7, 0.9):
    for rep in range(3):
        n = 1 << 22
        turn = np.where(rng.random(n) < q, 1, 3)
        h = np.cumsum(turn) % 4
        p = np.c_[np.cumsum(DX[h]), np.cumsum(DY[h])]
        lags = 2 ** np.arange(0, 15)
        m = msd(p, lags)
        sel = (lags >= 16) & (lags <= 1024)
        slope = float(np.mean(m[sel] / lags[sel]))
        a = (2 * q - 1) ** 2
        pred = (1 - a) / (1 + a)
        print(f"q={q} rep={rep} measured={slope:.4f} pred={pred:.4f} ratio={slope/pred:.3f}")
