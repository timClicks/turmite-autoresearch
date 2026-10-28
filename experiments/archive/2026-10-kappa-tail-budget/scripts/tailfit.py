"""Frozen-candidate survival family F for interior return durations (G3).

Observed data are exactly what the instrument records: per log2 bin b,
count n_b and time sum s_b of completed episodes (bins.csv entry_count /
entry_time_sum).  Onset u0 = 64 = 2^6 is a bin edge, so the tail mass
p = sum_{b>=6} n_b / N is exact, and the short part (bins 0-5) enters E[T]
through its exact time sums.

Tail family: conditional on T >= u0, Y has survival
    S(y) = ((y/u0)^-a - (H/u0)^-a) / (1 - (H/u0)^-a),  u0 <= y <= H
and T = floor(Y).  Because bin edges are integers, P(T in bin b) = P(Y in
[2^b, 2^(b+1))) exactly.  (a, H) are fitted by multinomial maximum likelihood
on the tail-bin counts over a fixed grid; the mean uses Euler-Maclaurin.
Loss/fit are deterministic (no RNG inside).
"""
import numpy as np

U0 = 64
B0 = 6                      # first tail bin
NB = 35                     # tail bins 6..40
ALPHAS = np.round(np.arange(0.05, 4.0001, 0.05), 4)
LOGH = np.arange(6.5, 40.0001, 0.25)   # log2 H grid
_G_A, _G_H = np.meshgrid(ALPHAS, LOGH, indexing="ij")
G_A = _G_A.ravel()
G_LH = _G_H.ravel()
EDGES = 2.0 ** np.arange(B0, B0 + NB + 1)


def surv(y, a, lh):
    """Tail survival S(y) of Y given Y >= U0; broadcasting over arrays."""
    H = 2.0 ** lh
    hn = (H / U0) ** (-a)
    s = ((np.minimum(y, H) / U0) ** (-a) - hn) / (1.0 - hn)
    return np.where(y >= H, 0.0, np.where(y <= U0, 1.0, s))


def bin_probs(a, lh):
    """P(bin b | tail) for bins 6..40; a, lh arrays of shape (G,) -> (G, NB)."""
    a = np.atleast_1d(a)[:, None]
    lh = np.atleast_1d(lh)[:, None]
    s = surv(EDGES[None, :], a, lh)
    return np.clip(s[:, :-1] - s[:, 1:], 0.0, 1.0)


_LOGP = None


def logp_table():
    global _LOGP
    if _LOGP is None:
        p = bin_probs(G_A, G_LH)
        with np.errstate(divide="ignore"):
            lp = np.log(p)
        _LOGP = np.where(np.isfinite(lp), lp, -1e9)
    return _LOGP


def tail_mean(a, lh):
    """E[T | T>=U0] = (U0-1) + sum_{u=U0}^{floor(H)} S(u), by Euler-Maclaurin."""
    a = np.atleast_1d(np.asarray(a, float))
    lh = np.atleast_1d(np.asarray(lh, float))
    H = 2.0 ** lh
    b = np.floor(H)
    hn = (H / U0) ** (-a)
    x = b / U0
    with np.errstate(divide="ignore", invalid="ignore"):
        pw = np.where(np.abs(a - 1) < 1e-9, np.log(x), -np.expm1((1 - a) * np.log(x)) / (a - 1))
    integral = U0 * (pw - hn * (x - 1)) / (1 - hn)        # int_{U0}^{b} S
    f_a, f_b = 1.0, surv(b, a, lh)
    d = lambda y: (-a * (y / U0) ** (-a - 1) / U0) / (1 - hn)   # S'(y) (inside (U0,H))
    em = integral + (f_a + f_b) / 2 + (d(b) - d(float(U0))) / 12
    return (U0 - 1) + em


def fit(counts, return_ll=False):
    """MLE of (a, log2 H) on tail-bin counts (length NB). counts: (NB,) or (R, NB)."""
    c = np.atleast_2d(np.asarray(counts, float))
    ll = c @ logp_table().T                     # (R, G)
    g = ll.argmax(1)
    out = (G_A[g], G_LH[g])
    return (*out, ll[np.arange(len(g)), g]) if return_ll else out


def deviance(counts, a, lh):
    """Binned deviance 2 sum n log(n / e) under the fitted family."""
    c = np.atleast_2d(np.asarray(counts, float))
    n = c.sum(1)
    P = bin_probs(np.atleast_1d(a), np.atleast_1d(lh))
    e = n[:, None] * P
    with np.errstate(divide="ignore", invalid="ignore"):
        t = np.where(c > 0, c * np.log(c / e), 0.0)
    t = np.where((c > 0) & (e <= 0), 1e9, t)
    return 2 * t.sum(1)


def gof_pvalue(counts, rng, B=100):
    """Parametric-bootstrap lack-of-fit p-value for ONE count vector (refits each draw)."""
    c = np.asarray(counts, float)
    n = int(c.sum())
    a, lh = fit(c)
    d_obs = float(deviance(c, a, lh)[0])
    P = bin_probs(a, lh)[0]
    boot = rng.multinomial(n, P / P.sum(), size=B)
    ab, hb = fit(boot)
    db = deviance(boot, ab, hb)
    return float((1 + (db >= d_obs - 1e-9).sum()) / (B + 1)), d_obs, float(a[0]), float(lh[0])


def sample_tail(a, lh, n, rng):
    """Draw n values of T=floor(Y) from the tail law (inverse CDF)."""
    H = 2.0 ** lh
    hn = (H / U0) ** (-a)
    u = rng.random(n)
    y = U0 * (1 - u * (1 - hn)) ** (-1.0 / a)
    return np.floor(np.minimum(y, H))


def log2bin(t):
    """floor(log2 t) for positive integer-valued float array, exactly."""
    return np.frexp(t)[1] - 1


def tail_counts(t):
    b = log2bin(t).astype(int) - B0
    return np.bincount(b, minlength=NB)[:NB]
