"""Revision 4 depth–duration readout (frozen in README "Revision 4 registration").

Shared by synth_rev4.py (G1) and analyse_rev4.py (walkers): same bin selection, per-window OLS,
kind median and call thresholds.
"""
from __future__ import annotations

import csv
import math
from collections import defaultdict
from pathlib import Path

import numpy as np

D_LO = 4
BIN_MIN = 20
NBINS_MIN = 4
SPAN_MIN = 3.0
AREA_T = 1.70
LINE_T = 1.30
NWIN_MIN = 3
K_LO, K_HI = 16, 24
L_MIN = 12.0
TAU_LO = 16
G_NBINS_MIN = 4


def load_dhist(path: Path):
    """{(spec, k): {axis: [(lo, hi, count, sum_tau, sum_d, sum_distinct), ...]}}"""
    h: dict = defaultdict(lambda: defaultdict(list))
    with Path(path).open() as f:
        for r in csv.DictReader(f):
            h[(r["spec"], int(r["k"]))][r["axis"]].append(
                (int(r["lo"]), int(r["hi"]), int(r["count"]), int(r["sum_tau"]), int(r["sum_d"]), int(r["sum_distinct"]))
            )
    return h


def ols_slope(x, y) -> float:
    x = np.asarray(x, float)
    y = np.asarray(y, float)
    xc = x - x.mean()
    return float((xc * (y - y.mean())).sum() / (xc * xc).sum())


def window_beta(d_rows, L: float):
    """Per-window exponent: OLS of ln(mean tau) on ln(mean d) over d-bins inside [4, floor L] with count >= 20.
    Returns (beta or None, n_bins, span)."""
    lmax = math.floor(L)
    sel = [r for r in d_rows if r[0] >= D_LO and r[1] <= lmax and r[2] >= BIN_MIN]
    if len(sel) < NBINS_MIN:
        return None, len(sel), None
    md = [r[4] / r[2] for r in sel]
    mt = [r[3] / r[2] for r in sel]
    span = max(md) / min(md)
    if span < SPAN_MIN:
        return None, len(sel), span
    return ols_slope(np.log(md), np.log(mt)), len(sel), span


def window_gamma(tau_rows, L: float):
    """Revisit readout: OLS of ln(sum tau / sum N) on ln(mean tau) over tau-bins in [16, L^2] with count >= 20."""
    sel = [r for r in tau_rows if r[0] >= TAU_LO and r[1] <= L * L and r[2] >= BIN_MIN and r[5] > 0]
    if len(sel) < G_NBINS_MIN:
        return None
    x = [math.log(r[3] / r[2]) for r in sel]
    y = [math.log(r[3] / r[5]) for r in sel]
    return ols_slope(x, y)


def fitted_time_share(d_rows, L: float) -> float:
    tot = sum(r[3] for r in d_rows)
    lmax = math.floor(L)
    fit = sum(r[3] for r in d_rows if r[0] >= D_LO and r[1] <= lmax)
    return fit / tot if tot else float("nan")


def call(beta_med, n_windows: int) -> str:
    if n_windows < NWIN_MIN or beta_med is None:
        return "uninformative"
    if beta_med >= AREA_T:
        return "area"
    if beta_med <= LINE_T:
        return "line"
    return "inconclusive"


def kind_summary(per_window: list[dict]) -> dict:
    """per_window items: {seed, beta, ...}; returns pooled median, per-seed medians, between-seed SD, call."""
    betas = [w["beta"] for w in per_window]
    med = float(np.median(betas)) if betas else None
    by_seed = defaultdict(list)
    for w in per_window:
        by_seed[w["seed"]].append(w["beta"])
    seed_meds = {s: float(np.median(v)) for s, v in sorted(by_seed.items())}
    sd = float(np.std(list(seed_meds.values()), ddof=1)) if len(seed_meds) > 1 else float("nan")
    return {"n_windows": len(betas), "beta": med, "seed_medians": seed_meds, "between_seed_sd": sd,
            "call": call(med, len(betas))}
