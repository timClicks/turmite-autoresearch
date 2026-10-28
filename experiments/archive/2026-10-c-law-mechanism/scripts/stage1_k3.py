# /// script
# dependencies = ["polars", "numpy"]
# ///
"""Stage 1 forward model K3 (README): 1/c = e + rho * sum_{k=1}^{min(n-1,12)} prod_{j<k} phi_j, phi_j = 1 if s_j == s_0 else psi.
Scoring frozen to c_law.py (census half split, seed 20261019; fresh 176 rules).
usage: uv run experiments/archive/2026-10-c-law-mechanism/scripts/stage1_k3.py"""
import json
from pathlib import Path

import numpy as np
import polars as pl

root = Path(__file__).resolve().parents[4]
out = root / "experiments/archive/2026-10-c-law-mechanism/results"
SEED = 20261019
cen = pl.read_csv(root / "experiments/archive/2026-10-probe-growth-census/results/probe_summary.csv").filter(
    (pl.col("cls") == "blob") & (pl.col("c") > 0) & (pl.col("g_k").abs() < 0.05))
fr = pl.read_csv(root / "experiments/archive/2026-10-kappa-leadrun-fresh/results/fresh_rules.csv").filter(
    (pl.col("kept")) & (pl.col("stationary")))
lines = []


def say(s=""):
    print(s)
    lines.append(s)


def run0(r):
    k = 1
    while k < len(r) and r[k] == r[0]:
        k += 1
    return k


def opp_counts(r, K=12):
    """cnt[k-1] = number of letters among s_1..s_{k-1} that differ from s_0, for k = 1..min(n-1, K)."""
    kk = min(len(r) - 1, K)
    cnt, c = [], 0
    for k in range(1, kk + 1):
        cnt.append(c)
        if k < len(r) and r[k] != r[0]:
            c += 1
    return np.array(cnt)


def feat(rules, psi):
    return np.array([np.sum(psi ** opp_counts(r)) for r in rules])


def fit(rules, c, grid=np.arange(0.0, 1.0001, 0.01)):
    y = 1.0 / c
    best = None
    for psi in grid:
        T = feat(rules, psi)
        X = np.column_stack([np.ones(len(T)), T])
        b = np.linalg.lstsq(X, y, rcond=None)[0]
        sse = ((y - X @ b) ** 2).sum()
        if best is None or sse < best[0]:
            best = (sse, psi, b[0], b[1])
    return best[1:]


def predict(rules, par):
    psi, e, rho = par
    return 1.0 / (e + rho * feat(rules, psi))


def r2(y, p):
    return 1 - ((y - p) ** 2).sum() / ((y - y.mean()) ** 2).sum()


rules, c = cen["rule"].to_list(), cen["c"].to_numpy()
perm = np.random.default_rng(SEED).permutation(len(rules))
A, B = perm[: len(perm) // 2], perm[len(perm) // 2:]
rA, rB = [rules[i] for i in A], [rules[i] for i in B]
# lead-only baseline on split B (same lookup as c_law.py)
lead = np.minimum([run0(r) for r in rules], 8).astype(float)
lm = {}
for i in A:
    lm.setdefault(int(lead[i]), []).append(np.log(c[i]))
lm = {k: np.mean(v) for k, v in lm.items()}
base = r2(np.log(c[B]), np.array([lm.get(int(lead[i]), np.log(c[A]).mean()) for i in B]))
par = fit(rA, c[A])
pB = predict(rB, par)
r2B = r2(np.log(c[B]), np.log(pB))
res = {"split": {"nA": len(A), "nB": len(B), "lead_only_r2_lnc": base, "K3_psi": par[0], "K3_e": par[1], "K3_rho": par[2], "K3_r2_lnc_B": r2B}}
say(f"split A/B = {len(A)}/{len(B)}; lead-only held-out R2(ln c) {base:.3f}")
say(f"K3 fit on A: psi {par[0]:.2f}, e {par[1]:.3f}, rho {par[2]:.3f}; held-out R2(ln c) on B {r2B:.3f}")
# full census -> fresh
parF = fit(rules, c)
fr_rules, fr_c = fr["rule"].to_list(), fr["c"].to_numpy()
pF = predict(fr_rules, parF)
r2F = r2(fr_c, pF)
rel = float(np.median(np.abs(pF - fr_c) / fr_c))
# lead law on fresh for reference
X = np.column_stack([np.ones(len(rules)), lead])
ab = np.linalg.lstsq(X, 1 / c, rcond=None)[0]
lf = np.minimum([run0(r) for r in fr_rules], 8)
r2_lead_fresh = r2(fr_c, 1 / (ab[0] + ab[1] * lf))
res["fresh"] = {"n": len(fr_c), "K3_psi": parF[0], "K3_e": parF[1], "K3_rho": parF[2], "K3_r2_c": r2F, "median_rel_err": rel, "lead_law_r2_c": r2_lead_fresh}
say(f"K3 fit on full census: psi {parF[0]:.2f}, e {parF[1]:.3f}, rho {parF[2]:.3f}; fresh (n={len(fr_c)}) R2(c) {r2F:.3f}, median rel err {rel:.3f}; lead law {r2_lead_fresh:.3f}")
res["K3-1"] = bool(r2B >= 0.90 and r2B >= base + 0.04)
res["K3-2"] = bool(r2F >= 0.90)
res["K3-3"] = bool(par[0] < 0.7)
say(f"K3-1 (B R2>=0.90 and >= lead-only+0.04): {'PASS' if res['K3-1'] else 'FAIL'}; K3-2 (fresh R2>=0.90): {'PASS' if res['K3-2'] else 'FAIL'}; "
    f"K3-3 (psi<0.7, fit on A): {'PASS' if res['K3-3'] else 'FAIL'}")
# reference: pooled chirality model (c_model.py) on fresh rules
import importlib.util  # noqa: E402
(out / "stage1_k3.json").write_text(json.dumps(res, indent=1, default=float))
(out / "stage1_k3.txt").write_text("\n".join(lines) + "\n")
