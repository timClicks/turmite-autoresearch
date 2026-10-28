# /// script
# dependencies = ["polars", "numpy", "scipy"]
# ///
"""W1: is kappa smooth in rule space? Hamming-1 neighbours (mirror-canonicalised), plus n+-1 and a variogram.
usage (repo root): uv run experiments/archive/2026-10-kappa-rule-space/scripts/w1_smooth.py"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import numpy as np, polars as pl
from scipy.stats import spearmanr
from kcommon import *

NPERM, NBOOT = 10000, 2000
cen = census().filter((pl.col("kappa") > 0) & pl.col("lnA22").is_not_null())
rules = cen["rule"].to_list(); idx = {r: i for i, r in enumerate(rules)}
cols = {"lnk": np.log(cen["kappa"].to_numpy()), "c": cen["c"].to_numpy(), "lnA22": cen["lnA22"].to_numpy(),
        "alpha_w": cen["alpha_w"].to_numpy()}
stat = np.abs(cen["g_k"].to_numpy()) < 0.05
nlen = np.array([len(r) for r in rules])
# residual of ln kappa on ln A(22): global linear fit (size control)
A = np.c_[np.ones(len(rules)), cols["lnA22"]]
cols["lnk_resA"] = cols["lnk"] - A @ np.linalg.lstsq(A, cols["lnk"], rcond=None)[0]


def flip_pairs():
    """Undirected Hamming-1 pairs (a<b index) with the flipped position j (0-based, in the original string)."""
    P = {}
    for r in rules:
        for j in range(len(r)):
            s = r[:j] + ("L" if r[j] == "R" else "R") + r[j + 1:]
            nb = canon(s)
            if nb in idx and nb != r:
                a, b = sorted((idx[r], idx[nb]))
                P.setdefault((a, b), j)
    return P


def length_pairs():
    P = set()
    for r in rules:
        for ext in ("R", "L"):
            nb = r + ext
            if nb in idx:
                P.add((idx[r], idx[nb]))
    return P


def pearson_pairs(v, a, b, w=None):
    x = np.r_[v[a], v[b]]; y = np.r_[v[b], v[a]]
    if w is None:
        return np.corrcoef(x, y)[0, 1]
    w2 = np.r_[w, w]
    mx = np.average(x, weights=w2); my = np.average(y, weights=w2)
    cov = np.average((x - mx) * (y - my), weights=w2)
    return cov / np.sqrt(np.average((x - mx) ** 2, weights=w2) * np.average((y - my) ** 2, weights=w2))


def perm_null(v, a, b, R):
    """Shuffle v among rules of equal length; recompute pair r. Returns array of NPERM r's."""
    groups = [np.where(nlen == n)[0] for n in np.unique(nlen)]
    out = np.empty(NPERM)
    for p in range(NPERM):
        vp = v.copy()
        for g in groups:
            vp[g] = v[R.permutation(g)]
        out[p] = pearson_pairs(vp, a, b)
    return out


def boot_ci(v, a, b, R, nb=NBOOT):
    N = len(v); rs = np.empty(nb)
    for i in range(nb):
        m = np.bincount(R.integers(0, N, N), minlength=N).astype(float)
        w = m[a] * m[b]
        rs[i] = pearson_pairs(v, a, b, w) if w.sum() > 0 else np.nan
    return np.nanpercentile(rs, [2.5, 97.5])


out = []
P = flip_pairs(); pairs = np.array(sorted(P)); a, b = pairs[:, 0], pairs[:, 1]; jpos = np.array([P[tuple(p)] for p in pairs])
out.append(f"census cohort used: {len(rules)} non-bursty blob rules with kappa>0 and area; Hamming-1 pairs (mirror-canonicalised): {len(pairs)}")
out.append("pairs per length n: " + ", ".join(f"{n}:{int(((nlen[a] == n)).sum())}" for n in np.unique(nlen)))
out.append(f"pairs by flipped position j: " + ", ".join(f"{j}:{int((jpos == j).sum())}" for j in range(12)))
out.append(f"power gate: need >= 300 Hamming-1 pairs -> {'OK' if len(pairs) >= 300 else 'UNDERPOWERED'}")

R = rng(1)
res = {}
for name in ("c", "lnk", "lnk_resA", "lnA22", "alpha_w"):
    v = cols[name]; r = pearson_pairs(v, a, b); rho = spearmanr(np.r_[v[a], v[b]], np.r_[v[b], v[a]])[0]
    null = perm_null(v, a, b, R); lo, hi = boot_ci(v, a, b, R)
    res[name] = r
    out.append(f"{name:9s}: pair Pearson r = {r:+.3f}  (Spearman {rho:+.3f}); boot 95% CI [{lo:+.3f}, {hi:+.3f}]; "
               f"perm null mean {null.mean():+.3f} sd {null.std():.3f}, p(null >= r) = {(null >= r).mean():.4f}")
out.append(f"attenuation: ln kappa r_obs/0.6 = {res['lnk'] / 0.6:+.3f} (single-run reliability ~0.6, a1b_icc)")

# stationary-only pairs
s_ok = stat[a] & stat[b]
out.append(f"stationary-only pairs (|g_k|<0.05 both): {int(s_ok.sum())}; r(ln kappa) = {pearson_pairs(cols['lnk'], a[s_ok], b[s_ok]):+.3f}; r(c) = {pearson_pairs(cols['c'], a[s_ok], b[s_ok]):+.3f}")

# EXPLORATORY (not pre-registered): stationary subset, rank correlation, CI, by position
sa, sb = a[s_ok], b[s_ok]
v = cols["lnk"]
out.append("EXPLORATORY stationary pairs: Spearman = %+.3f; boot 95%% CI (Pearson) [%+.3f, %+.3f]" % (
    spearmanr(np.r_[v[sa], v[sb]], np.r_[v[sb], v[sa]])[0], *boot_ci(v, sa, sb, rng(5), 1000)))
nl = perm_null(v, sa, sb, rng(6)) if False else None
for lab, sel in (("j<=1", jpos[s_ok] <= 1), ("2<=j<=3", (jpos[s_ok] >= 2) & (jpos[s_ok] <= 3)), ("j>=4", jpos[s_ok] >= 4)):
    out.append(f"EXPLORATORY stationary position {lab:8s}: pairs {int(sel.sum()):5d} r(ln kappa) = {pearson_pairs(v, sa[sel], sb[sel]):+.3f}")
# how much of the tail drives the Pearson r: drop pairs with a member beyond |z|>3
z = (v - v.mean()) / v.std()
ok = (np.abs(z[a]) < 3) & (np.abs(z[b]) < 3)
out.append(f"EXPLORATORY trimmed (|z|<3 both): pairs {int(ok.sum())}, r(ln kappa) = {pearson_pairs(v, a[ok], b[ok]):+.3f}; ln kappa sd {v.std():.2f}, min {v.min():.2f}, max {v.max():.2f}; share non-stationary rules {1 - stat.mean():.3f}")

# by position
for lab, sel in (("j<=1", jpos <= 1), ("2<=j<=3", (jpos >= 2) & (jpos <= 3)), ("j>=4", jpos >= 4)):
    if sel.sum() > 30:
        out.append(f"position {lab:8s}: pairs {int(sel.sum()):5d}  r(ln kappa) = {pearson_pairs(cols['lnk'], a[sel], b[sel]):+.3f}  r(c) = {pearson_pairs(cols['c'], a[sel], b[sel]):+.3f}")
r_lo = pearson_pairs(cols["lnk"], a[jpos <= 1], b[jpos <= 1]); r_hi = pearson_pairs(cols["lnk"], a[jpos >= 4], b[jpos >= 4])
out.append(f"P1.3 check: r(j>=4) - r(j<=1) = {r_hi - r_lo:+.3f} (prediction: <= 0.10)")

# n +- 1 neighbours
Lp = np.array(sorted(length_pairs()))
if len(Lp):
    la, lb = Lp[:, 0], Lp[:, 1]
    out.append(f"append-one-letter pairs: {len(Lp)}; r(ln kappa) = {pearson_pairs(cols['lnk'], la, lb):+.3f}; r(c) = {pearson_pairs(cols['c'], la, lb):+.3f}")

# pool subset (patched means)
pool = pl.read_csv(EXP / "results" / "rules_pool.csv"); pidx = {r: i for i, r in enumerate(pool["base"].to_list())}
plnk = pool["lnk"].to_numpy()
pp = [(pidx[rules[i]], pidx[rules[j]]) for i, j in pairs if rules[i] in pidx and rules[j] in pidx]
if len(pp) >= 5:
    pa, pb = np.array(pp).T
    out.append(f"pairs with both members in pool-192: {len(pp)}; r(pool ln kappa) = {pearson_pairs(plnk, pa, pb):+.3f} (too few for conclusions if < 30)")

# variogram: canonical Hamming distance 1..4 among same-n rules (distance-1 here = all canonical single flips at j>=1)
out.append("variogram (same-n pairs, canonical Hamming distance d; r is pairwise Pearson of ln kappa and of c; null = equal-n permutation mean +- sd over 200 perms):")
bits = {n: None for n in np.unique(nlen)}
vg = {d: ([], []) for d in (1, 2, 3, 4)}
for n in np.unique(nlen):
    ii = np.where(nlen == n)[0]
    B = np.array([[ch == "R" for ch in rules[i]] for i in ii], dtype=np.int8)
    D = (B[:, None, :] != B[None, :, :]).sum(-1) if len(ii) <= 2500 else None
    iu = np.triu_indices(len(ii), 1)
    for d in (1, 2, 3, 4):
        m = D[iu] == d
        vg[d][0].extend(ii[iu[0][m]]); vg[d][1].extend(ii[iu[1][m]])
Rv = rng(2)
for d in (1, 2, 3, 4):
    va, vb = np.array(vg[d][0]), np.array(vg[d][1])
    if len(va) < 30:
        continue
    r1 = pearson_pairs(cols["lnk"], va, vb); rc = pearson_pairs(cols["c"], va, vb)
    groups = [np.where(nlen == n)[0] for n in np.unique(nlen)]; nl = []
    for _ in range(200):
        vp = cols["lnk"].copy()
        for g in groups:
            vp[g] = cols["lnk"][Rv.permutation(g)]
        nl.append(pearson_pairs(vp, va, vb))
    out.append(f"  d={d}: pairs {len(va):7d}  r(ln kappa) = {r1:+.3f}  (null {np.mean(nl):+.3f} +- {np.std(nl):.3f})   r(c) = {rc:+.3f}")

# Pre-registered verdicts
out.append("")
out.append("Pre-registered verdicts (see README section 5/W1):")
out.append(f"P1.1 r(c) >= 0.5: r = {res['c']:+.3f} -> {'HELD' if res['c'] >= 0.5 else 'FAILED'}")
out.append(f"P1.2 r_obs(ln kappa) <= 0.15 and CI upper < 0.30: see numbers above (r = {res['lnk']:+.3f})")
txt = header("uv run experiments/archive/2026-10-kappa-rule-space/scripts/w1_smooth.py") + "\n".join(out) + "\n"
(EXP / "results" / "w1_stats.txt").write_text(txt); print(txt)
