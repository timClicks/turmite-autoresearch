# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "scipy", "polars"]
# ///
"""Tail estimator for interior-return durations (README "Stage V2", V2-B).

Model on durations T >= t0 (the short-return component below t0 is left unmodelled):
    S(t) = (t / t0)^(-theta) * exp(-(t - t0) / tau),   fitted by conditional binned maximum likelihood.
Data are the sampler's 4-bins-per-octave histograms: hbin(d) = 4*floor(log2 d) + (floor(4 d / 2^o) & 3), o = floor(log2 d).
"""
from __future__ import annotations

import numpy as np
from scipy.optimize import minimize

T0_DEFAULT = 64


def bin_edges(nbins: int = 256) -> np.ndarray:
    """Real lower edges of the sampler's histogram bins: floor(4 d / 2^o) = 4 + sub for d in [(4+sub) 2^(o-2), (5+sub) 2^(o-2))."""
    edges = np.zeros(nbins + 1)
    for b in range(nbins):
        o, sub = divmod(b, 4)
        edges[b] = (4 + sub) * 2.0 ** (o - 2)
    edges[nbins] = 2.0 ** (nbins // 4)
    return edges


EDGES = bin_edges()


def _surv(t, t0, theta, tau):
    return (t / t0) ** (-theta) * np.exp(-(t - t0) / tau)


def fit(counts: np.ndarray, t0: float = T0_DEFAULT, x0: tuple[float, float] | None = None) -> dict:
    """counts[b] = durations in sampler bin b. Returns theta, tau, identifiable flag."""
    keep = EDGES[:-1] >= t0
    n = counts[keep].astype(float)
    total = n.sum()
    if total < 200:
        return dict(ok=False, reason="fewer than 200 durations above t0", n=float(total))
    e, e_hi = EDGES[:-1][keep], EDGES[1:][keep]

    def nll(p):
        theta, ltau = p
        tau = np.exp(ltau)
        pr = np.clip(_surv(e, t0, theta, tau) - _surv(e_hi, t0, theta, tau), 1e-300, None)
        return -(n * np.log(pr / pr.sum())).sum()

    starts = [x0] if x0 is not None else [(th, np.log(t0) + d) for th in (0.2, 0.6, 1.0) for d in (1.0, 4.0, 8.0)]
    best = None
    for s in starts:
        r = minimize(nll, list(s), method="Nelder-Mead", options=dict(xatol=1e-5, fatol=1e-7, maxiter=4000))
        if best is None or r.fun < best.fun:
            best = r
    theta, tau = float(best.x[0]), float(np.exp(best.x[1]))
    top = EDGES[:-1][counts > 0].max()
    return dict(ok=True, theta=theta, tau=tau, n=float(total), identifiable=bool(tau < 4 * top), top_edge=float(top), x=(float(best.x[0]), float(best.x[1])))


def sample_counts(rng: np.random.Generator, n_total: int, w_tail: float, theta: float, tau: float, t0: float = T0_DEFAULT, short_mean: float = 4.0) -> np.ndarray:
    """Synthetic durations: geometric short component (< t0) + tail S = (t/t0)^-theta exp(-(t-t0)/tau) above t0, binned like the sampler."""
    n_tail = rng.binomial(n_total, w_tail)
    grid = np.unique(np.round(np.exp(np.linspace(np.log(t0), np.log(t0) + 25, 400000))))
    s = _surv(grid, t0, theta, tau)
    u = rng.random(n_tail)
    idx = np.searchsorted(-s, -u)  # first grid point with S <= u
    t_tail = grid[np.clip(idx, 0, len(grid) - 1)]
    t_short = np.minimum(rng.geometric(1.0 / short_mean, n_total - n_tail), t0 - 1)
    d = np.concatenate([t_tail, t_short]).astype(np.int64)
    d = d[d >= 1]
    o = np.floor(np.log2(d)).astype(np.int64)
    b = o * 4 + (((d << 2) >> o) & 3)
    return np.bincount(np.clip(b, 0, 255), minlength=256)


def bootstrap_theta(counts: np.ndarray, fit0: dict, t0: float, rng: np.random.Generator, nboot: int = 40) -> tuple[float, float]:
    """Parametric-style multinomial resample of the observed counts, warm-started refits."""
    p = counts / counts.sum()
    vals = []
    for _ in range(nboot):
        c = rng.multinomial(int(counts.sum()), p)
        f = fit(c, t0, x0=fit0["x"])
        if f["ok"]:
            vals.append(f["theta"])
    return float(np.quantile(vals, 0.025)), float(np.quantile(vals, 0.975))
