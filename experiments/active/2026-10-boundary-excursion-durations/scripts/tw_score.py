"""Revision 3 time-weighted survival Score (frozen in README "Revision 3 registration").

Shared by analyse_rev3.py (walkers) and synth_rev3.py (G1 synthetic gate), so both
use the same fine binning, S_tw evaluation, retention and verdict code.
"""
from __future__ import annotations

import math

import numpy as np

MARGIN = 0.75
# u_j = 2^{-8 + j/2}, j = 0..32 -> 1/256 .. 256 (the code grid of analyse.py)
U_GRID = np.array([2 ** (-8 + j / 2) for j in range(33)], dtype=float)
FINE_PER_OCT = 8
N_MIN = 200
NEFF_MIN = 30.0


def fine_index(tau: np.ndarray) -> np.ndarray:
    """f = 8*floor(log2 tau) + ((tau << 3) >> b) - 8 for integer tau >= 1 (matches the Rust instrument)."""
    tau = np.asarray(tau, dtype=np.int64)
    b = np.floor(np.log2(tau.astype(np.float64))).astype(np.int64)
    # guard float rounding at exact powers of two
    b = np.where((np.int64(1) << (b + 1)) <= tau, b + 1, b)
    b = np.where((np.int64(1) << b) > tau, b - 1, b)
    sub = ((tau << 3) >> b) - 8
    return b * FINE_PER_OCT + sub


def fine_range(f: int) -> tuple[int, int]:
    b, sub = divmod(int(f), FINE_PER_OCT)
    lo = -(-((8 + sub) << b) // 8)
    hi = -(-((9 + sub) << b) // 8) - 1
    return lo, hi


def bin_taus(tau: np.ndarray) -> dict[int, tuple[int, int]]:
    """Fine histogram {f: (count, sum_tau)} of integer durations."""
    f = fine_index(tau)
    out: dict[int, tuple[int, int]] = {}
    uniq, inv = np.unique(f, return_inverse=True)
    cnt = np.bincount(inv)
    sm = np.bincount(inv, weights=np.asarray(tau, dtype=np.float64))
    for i, ff in enumerate(uniq):
        out[int(ff)] = (int(cnt[i]), int(round(sm[i])))
    return out


def window_stats(fbins: dict[int, tuple[int, int]]) -> dict:
    n = sum(c for c, _ in fbins.values())
    tot = sum(s for _, s in fbins.values())
    sq = sum((s * s) / c for c, s in fbins.values() if c > 0)
    neff = (tot * tot) / sq if sq > 0 else 0.0
    return {"n": n, "total": tot, "n_eff": neff}


def mass_above(fbins: dict[int, tuple[int, int]], s: np.ndarray) -> np.ndarray:
    """M(s) = sum_{tau > s} tau: exact at fine-bin upper edges, linear in s between
    consecutive upper edges (contiguous ranges incl. empty bins), M = total for s < 1."""
    tot = float(sum(v[1] for v in fbins.values()))
    if not fbins:
        return np.zeros_like(s, dtype=float)
    fmax = max(fbins)
    xs, ys = [], []
    cum = 0.0
    for f in range(0, fmax + 1):
        lo, hi = fine_range(f)
        if lo > hi:
            continue
        cum += fbins.get(f, (0, 0))[1]
        xs.append(float(hi))
        ys.append(tot - cum)
    xs = np.asarray(xs)
    ys = np.asarray(ys)
    m = np.interp(s, xs, ys, left=tot, right=0.0)
    return np.where(s < 1.0, tot, m)


def s_tw_on_grid(fbins, scale: float, censored_tau: float | None = None) -> np.ndarray:
    s = U_GRID * scale
    M = mass_above(fbins, s)
    tot = float(sum(v[1] for v in fbins.values()))
    if censored_tau is not None and censored_tau > 0:
        M = M + np.where(s < censored_tau, censored_tau, 0.0)
        tot += censored_tau
    if tot <= 0:
        return np.full_like(U_GRID, np.nan)
    return M / tot


def pairwise_score(survivals: list[np.ndarray]) -> float:
    stack = np.vstack(survivals)
    mask = np.any((stack > 0.05) & (stack < 0.95), axis=0)
    if mask.sum() < 3 or stack.shape[0] < 2:
        return float("nan")
    G = stack[:, mask]
    n = G.shape[0]
    acc, pairs = 0.0, 0
    for i in range(n):
        for j in range(i + 1, n):
            acc += np.abs(G[i] - G[j]).mean()
            pairs += 1
    return float(acc / pairs)


def verdict(sL: float, sL2: float, uninformative: bool = False) -> str:
    if uninformative:
        return "uninformative"
    if not (math.isfinite(sL) and math.isfinite(sL2)):
        return "inconclusive"
    if sL2 <= MARGIN * sL:
        return "D"
    if sL <= MARGIN * sL2:
        return "S"
    return "inconclusive"


def score_tw(windows: list[dict]) -> dict:
    """windows: dicts with keys L, fbins, and optional censored_tau. Already retained."""
    if len(windows) < 2:
        return {"Score_L": None, "Score_L2": None, "verdict": "uninformative",
                "Score_L_cens": None, "Score_L2_cens": None, "verdict_cens": "uninformative",
                "censoring_fragile": False, "L_range_ratio": None}
    Ls = [w["L"] for w in windows]
    ratio = max(Ls) / min(Ls)
    unin = ratio < 2.0
    sL = pairwise_score([s_tw_on_grid(w["fbins"], w["L"]) for w in windows])
    sL2 = pairwise_score([s_tw_on_grid(w["fbins"], w["L"] ** 2) for w in windows])
    cL = pairwise_score([s_tw_on_grid(w["fbins"], w["L"], w.get("censored_tau")) for w in windows])
    cL2 = pairwise_score([s_tw_on_grid(w["fbins"], w["L"] ** 2, w.get("censored_tau")) for w in windows])
    v = verdict(sL, sL2, unin)
    vc = verdict(cL, cL2, unin)
    fragile = (not unin) and vc != v
    return {"Score_L": sL, "Score_L2": sL2, "verdict": "censoring-fragile" if fragile else v,
            "verdict_primary": v, "Score_L_cens": cL, "Score_L2_cens": cL2, "verdict_cens": vc,
            "censoring_fragile": fragile, "L_range_ratio": ratio, "L_min": min(Ls), "L_max": max(Ls)}


def number_weighted_score(windows: list[dict]) -> dict:
    """Frozen Rev2 number-weighted Score from coarse log2 bins (bin-midpoint taus), equivalent to
    analyse.survival_on_grid on expand_durations, evaluated in closed form."""
    def surv(coarse: dict[int, int], scale: float) -> np.ndarray:
        n = sum(coarse.values())
        mids = np.array([1.0 if b == 0 else 2.0 ** b + 2.0 ** (b - 1) for b in coarse])
        cs = np.array(list(coarse.values()), dtype=float)
        return np.array([cs[(mids / scale) > u].sum() / n for u in U_GRID])
    if len(windows) < 2:
        return {"Score_L": None, "Score_L2": None, "verdict": "uninformative"}
    Ls = [w["L"] for w in windows]
    unin = max(Ls) / min(Ls) < 2.0
    sL = pairwise_score([surv(w["coarse"], w["L"]) for w in windows])
    sL2 = pairwise_score([surv(w["coarse"], w["L"] ** 2) for w in windows])
    return {"Score_L": sL, "Score_L2": sL2, "verdict": verdict(sL, sL2, unin)}


def coarse_from_fine(fbins) -> dict[int, int]:
    out: dict[int, int] = {}
    for f, (c, _) in fbins.items():
        out[f // FINE_PER_OCT] = out.get(f // FINE_PER_OCT, 0) + c
    return out
