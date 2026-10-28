"""Shared model code for the c-law mechanism experiment (imported by stage2_analyse.py; no I/O at import)."""
import numpy as np
from scipy.optimize import least_squares

SEED = 20261019


def run0(r):
    k = 1
    while k < len(r) and r[k] == r[0]:
        k += 1
    return k


def r2(y, p):
    y, p = np.asarray(y), np.asarray(p)
    return 1 - ((y - p) ** 2).sum() / ((y - y.mean()) ** 2).sum()


# ---- lead law: 1/c = a + b min(lead, 8)
def lead_fit(rules, c):
    L = np.minimum([run0(r) for r in rules], 8).astype(float)
    return np.linalg.lstsq(np.column_stack([np.ones(len(L)), L]), 1 / np.asarray(c), rcond=None)[0]


def lead_predict(rules, ab):
    L = np.minimum([run0(r) for r in rules], 8).astype(float)
    return 1 / (ab[0] + ab[1] * L)


# ---- K3: 1/c = e + rho * sum_k psi^{#K among s_1..s_{k-1}}
def _opp_counts(r, K=12):
    kk = min(len(r) - 1, K)
    cnt, c = [], 0
    for k in range(1, kk + 1):
        cnt.append(c)
        if r[k] != r[0]:
            c += 1
    return np.array(cnt)


def k3_fit(rules, c, grid=np.arange(0.0, 1.0001, 0.01)):
    y = 1.0 / np.asarray(c)
    cnts = [_opp_counts(r) for r in rules]
    best = None
    for psi in grid:
        T = np.array([np.sum(psi ** k) for k in cnts])
        X = np.column_stack([np.ones(len(T)), T])
        b = np.linalg.lstsq(X, y, rcond=None)[0]
        sse = ((y - X @ b) ** 2).sum()
        if best is None or sse < best[0]:
            best = (sse, psi, b[0], b[1])
    return best[1:]


def k3_predict(rules, par):
    psi, e, rho = par
    return 1.0 / (e + rho * np.array([np.sum(psi ** _opp_counts(r)) for r in rules]))


# ---- K4: 1/c = e + sum_{k=1}^{min(n-1,12)} prod_{j=0}^{k-1} phi[t_j], t_j = (type s_j, type s_{j+1}), CC=0 CK=1 KC=2 KK=3
def _k4_index(r, K=12):
    kk = min(len(r) - 1, K)
    typ = [0 if ch == r[0] else 1 for ch in r]
    # type pair encoded C=0, K=1: CC=0, CK=1, KC=2, KK=3
    return np.array([typ[j] * 2 + typ[j + 1] for j in range(kk)])


def _k4_feat(idx, phi):
    prod, tot = 1.0, 0.0
    for t in idx:
        prod *= phi[t]
        tot += prod
    return tot


def k4_fit(rules, c):
    y = 1.0 / np.asarray(c)
    idxs = [_k4_index(r) for r in rules]

    def resid(p):
        return np.array([p[0] + _k4_feat(i, p[1:]) for i in idxs]) - y

    best = None
    for start in ([1.1, 0.9, 0.5, 0.5, 0.5], [1.0, 0.8, 0.2, 0.8, 0.3], [1.3, 0.95, 0.7, 0.9, 0.6]):
        sol = least_squares(resid, start, bounds=([0.0, 0, 0, 0, 0], [5.0, 1.2, 1.2, 1.2, 1.2]))
        if best is None or sol.cost < best.cost:
            best = sol
    return best.x


def k4_predict(rules, p):
    return 1.0 / np.array([p[0] + _k4_feat(_k4_index(r), p[1:]) for r in rules])
