# /// script
# dependencies = ["polars", "numpy", "scipy"]
# ///
"""EXPLORATORY follow-up to W3c (not registered; added after seeing that the all-rules gain fell to ~0): cross training/test cohorts.
Same estimator as w3c_analyse.py. Train on {stationary, all} census rules, score on {stationary (162), all (176)} fresh rules.
usage (repo root): uv run experiments/archive/2026-10-kappa-rule-space/scripts/w3c_cross.py"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import numpy as np, polars as pl
from kcommon import *

raw = pl.read_csv(EXP / "dumps" / "w3c_probe.csv")
r = per_rule(raw).with_columns(base=pl.col("rule").str.split("@").list.first())
r = r.join(raw.filter(pl.col("k") == 22).select("rule", lnA22=pl.col("area").log()), on="rule", how="left")
core = r.filter(pl.col("alpha_w").is_between(0.25, 0.42) & (pl.col("kappa") > 0))
fresh = rule_means(core, 6)
fst = np.abs(fresh["g_k"].to_numpy()) < 0.05
cen = census().filter((pl.col("kappa") > 0) & pl.col("lnA22").is_not_null())
c_rules = cen["rule"].to_list(); c_y = np.log(cen["kappa"].to_numpy()); c_st = np.abs(cen["g_k"].to_numpy()) < 0.05; c_A = cen["lnA22"].to_numpy()
f_rules = np.array(fresh["base"].to_list()); f_y = fresh["lnk"].to_numpy(); f_A = fresh["lnA22"].to_numpy()


def table(rules_, y_, pmax=8):
    t = {q: {} for q in range(1, pmax + 1)}
    for rr, v in zip(rules_, y_):
        for q in range(1, pmax + 1):
            t[q].setdefault(rr[:q], []).append(v)
    return t


def lookup(t, test_rules, p, gm, loo_y=None):
    o = []
    for i, rr in enumerate(test_rules):
        val = gm
        for q in range(p, 0, -1):
            g = t[q].get(rr[:q])
            if g is not None and loo_y is not None:
                g = list(g)
                if loo_y[i] in g:
                    g.remove(loo_y[i])
            if g is not None and len(g) >= 3:
                val = float(np.mean(g)); break
        o.append(val)
    return np.array(o)


def ols(X, y):
    return np.linalg.lstsq(np.c_[np.ones(len(X)), X], y, rcond=None)[0]


def app(b, X):
    return np.c_[np.ones(len(X)), X] @ b


out = [f"fresh rules: all {len(f_y)}, stationary {int(fst.sum())}, non-stationary {int((~fst).sum())}",
       f"training census: all {len(c_y)} (sd {c_y.std():.3f}), stationary {int(c_st.sum())} (sd {c_y[c_st].std():.3f})"]
R = rng(31)
for trl, tmask in (("train=stationary", c_st), ("train=all", np.ones(len(c_y), bool))):
    tr = [x for x, m in zip(c_rules, tmask) if m]; ty = c_y[tmask]; tA = c_A[tmask]; gm = ty.mean(); T = table(tr, ty)
    for tel, fmask in (("test=stationary", fst), ("test=all", np.ones(len(f_y), bool))):
        fr = list(f_rules[fmask]); fy = f_y[fmask]; fA = f_A[fmask]
        b1 = ols(tA[:, None], ty); p1 = app(b1, fA[:, None]); den = ((fy - gm) ** 2)
        line = f"{trl:17s} {tel:16s} n={len(fy):3d} ln A alone R2 {1 - ((fy - p1) ** 2).sum() / den.sum():+.3f}"
        for p in (6, 8):
            b2 = ols(np.c_[tA, lookup(T, tr, p, gm, loo_y=ty)], ty); p2 = app(b2, np.c_[fA, lookup(T, fr, p, gm)])
            gain = lambda idx: (((fy[idx] - p1[idx]) ** 2).sum() - ((fy[idx] - p2[idx]) ** 2).sum()) / den[idx].sum()
            g0 = gain(np.arange(len(fy))); bs = [gain(R.integers(0, len(fy), len(fy))) for _ in range(2000)]
            line += f" | p={p} gain {g0:+.3f} [{np.percentile(bs, 2.5):+.3f}, {np.percentile(bs, 97.5):+.3f}]"
        out.append(line)
txt = header("uv run experiments/archive/2026-10-kappa-rule-space/scripts/w3c_cross.py") + "EXPLORATORY (unregistered)\n" + "\n".join(out) + "\n"
(EXP / "results" / "w3c_cross.txt").write_text(txt); print(txt)
