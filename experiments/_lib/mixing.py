"""Test the random-environment picture of the ant's interior motion.

For each dumped rule (experiments/archive/2026-10-knockout-maps/dumps/RULE.traj, experiments/archive/2026-10-knockout-maps/dumps/RULE.grid from examples/dump.rs):
  q_eff     fraction of turns that were R, vs q_rule = #R / n
  turn_corr correlation of successive turns (lags 1..8)
  msd_slope MSD(tau) / tau for tau in [16, 1024], vs the persistent-walk
            prediction (1 - a) / (1 + a), a = (2 q_eff - 1)^2
  colour TV total-variation distance of interior colours from uniform
  nbr_eq    P(horizontal neighbours share a colour) / sum_k p_k^2
  mix_ratio time to diffuse across the blob, R^2 / msd_slope, over elapsed t
"""
import sys
from pathlib import Path

import numpy as np
import polars as pl

S = 4096


def headings(p):
    d = np.diff(p, axis=0)
    # DIRS: 0 N (0,-1), 1 E (1,0), 2 S (0,1), 3 W (-1,0)
    h = np.select([d[:, 1] == -1, d[:, 0] == 1, d[:, 1] == 1, d[:, 0] == -1], [0, 1, 2, 3], -1)
    assert (h >= 0).all() and (np.abs(d).sum(axis=1) == 1).all()
    return h


def msd(p, lags, max_starts=400_000):
    out = []
    for tau in lags:
        n = len(p) - tau
        stride = max(1, n // max_starts)
        a, b = p[:n:stride], p[tau::stride][: len(p[:n:stride])]
        out.append(((b - a).astype(float) ** 2).sum(axis=1).mean())
    return np.array(out)


def analyse(rule, dumps):
    p = np.fromfile(dumps / f"{rule}.traj", dtype="<i2").reshape(-1, 2).astype(np.int64)
    g = np.fromfile(dumps / f"{rule}.grid", dtype=np.uint8).reshape(S, S)
    n = len(rule)
    h = headings(p)
    turn = (h[1:] - h[:-1]) % 4
    assert set(np.unique(turn)) <= {1, 3}
    s = np.where(turn == 1, 1.0, -1.0)
    q = (turn == 1).mean()
    sc = s - s.mean()
    corr = [float((sc[:-k] * sc[k:]).mean() / sc.var()) for k in range(1, 9)]
    lags = 2 ** np.arange(0, 15)
    m = msd(p, lags)
    sel = (lags >= 16) & (lags <= 1024)
    slope = float(np.mean(m[sel] / lags[sel]))
    expo = float(np.polyfit(np.log(lags[sel]), np.log(m[sel]), 1)[0])
    a = (2 * q - 1) ** 2
    pred = (1 - a) / (1 + a)
    vis = g != 255
    inner = vis.copy()
    for ax, sh in [(0, 1), (0, -1), (1, 1), (1, -1)]:
        inner &= np.roll(vis, sh, axis=ax)
    cols = g[inner]
    pk = np.bincount(cols, minlength=n)[:n] / len(cols)
    tv = 0.5 * np.abs(pk - 1 / n).sum()
    left, right = g[:, :-1], g[:, 1:]
    both = inner[:, :-1] & inner[:, 1:]
    eq = (left[both] == right[both]).mean() / (pk ** 2).sum()
    A = vis.sum()
    R2 = A / np.pi
    t = len(p) - 1  # the dump covers the last octave, which equals elapsed / 2
    return dict(rule=rule, n=n, q_rule=rule.count("R") / n, q_eff=float(q), turn_corr1=corr[0], turn_corr2=corr[1],
                max_abs_corr=float(np.max(np.abs(corr))), msd_slope=slope, msd_expo=expo, pred_slope=pred,
                colour_tv=float(tv), nbr_eq=float(eq), area=int(A), mix_ratio=float(R2 / max(slope, 1e-9) / (2 * t)))


if __name__ == "__main__":
    dumps = Path(sys.argv[1])
    rules = [l.strip() for l in open(sys.argv[2]) if l.strip()]
    rows = [analyse(r, dumps) for r in rules]
    df = pl.DataFrame(rows)
    df.write_csv(sys.argv[3])
    pl.Config.set_tbl_rows(80); pl.Config.set_float_precision(3); pl.Config.set_tbl_width_chars(250); pl.Config.set_tbl_cols(20)
    print(df)
