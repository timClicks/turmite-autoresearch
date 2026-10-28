# /// script
# dependencies = ["polars", "numpy"]
# ///
"""EXPLORATORY follow-up to x1: is the prefix effect real out of sample, and is it more than size or c?
Discovery: census (non-bursty, single run) minus pool-192 rules. Confirmation: pool-192 patched rule means (independent runs).
Predictor: mean ln kappa of discovery rules sharing the first p letters (p=2..8; fall back to the p-1 prefix mean if no discovery match).
Held-out R^2 is vs the discovery-set mean. Also with ln A(22) and c as covariates, and on the stationary subset.
usage (repo root): uv run experiments/archive/2026-10-kappa-rule-space/scripts/x2_prefix_heldout.py"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import numpy as np, polars as pl
from kcommon import *

cen = census().filter(pl.col("kappa") > 0)
pool = pl.read_csv(EXP / "results" / "rules_pool.csv")
pset = set(pool["base"].to_list())
disc = cen.filter(~pl.col("rule").is_in(list(pset)))
d_rules = disc["rule"].to_list(); d_y = np.log(disc["kappa"].to_numpy()); d_st = np.abs(disc["g_k"].to_numpy()) < 0.05
d_c = disc["c"].to_numpy(); d_A = disc["lnA22"].to_numpy()
p_rules = pool["base"].to_list(); p_y = pool["lnk"].to_numpy(); p_st = np.abs(pool["g_k"].to_numpy()) < 0.05
p_c = pool["c"].to_numpy(); p_A = pool["lnA22"].to_numpy()
out = [f"discovery rules {len(d_rules)} (stationary {int(d_st.sum())}); confirmation pool rules {len(p_rules)} (stationary {int(p_st.sum())})"]


def r2(y, pred):
    return 1 - ((y - pred) ** 2).sum() / ((y - y.mean()) ** 2).sum()


def prefix_pred(train_rules, train_y, test_rules, p, min_n=3):
    tabs = {q: {} for q in range(1, p + 1)}
    for r, v in zip(train_rules, train_y):
        for q in range(1, p + 1):
            tabs[q].setdefault(r[:q], []).append(v)
    gm = train_y.mean(); pred = []
    for r in test_rules:
        val = gm
        for q in range(p, 0, -1):
            g = tabs[q].get(r[:q])
            if g is not None and len(g) >= min_n:
                val = np.mean(g); break
        pred.append(val)
    return np.array(pred)


def fit_cov(Xtr, ytr, Xte):
    A = np.c_[np.ones(len(Xtr)), Xtr]; b = np.linalg.lstsq(A, ytr, rcond=None)[0]
    return np.c_[np.ones(len(Xte)), Xte] @ b

for label, dmask, pmask in (("all rules", np.ones(len(d_y), bool), np.ones(len(p_y), bool)), ("stationary only", d_st, p_st)):
    out.append(f"\n[{label}] discovery n={int(dmask.sum())}, pool n={int(pmask.sum())}; sd ln kappa discovery {d_y[dmask].std():.3f}, pool {p_y[pmask].std():.3f}")
    dr = [r for r, m in zip(d_rules, dmask) if m]; pr_ = [r for r, m in zip(p_rules, pmask) if m]
    for p in (2, 3, 4, 5, 6, 7, 8):
        pred = prefix_pred(dr, d_y[dmask], pr_, p)
        out.append(f"  prefix<={p}: held-out R^2 on pool patched means {r2(p_y[pmask], pred):+.3f}   corr {np.corrcoef(pred, p_y[pmask])[0, 1]:+.3f}")
    # covariates alone, and prefix-6 + covariates (size and c)
    covs = {"ln A(22)": (d_A[dmask][:, None], p_A[pmask][:, None]), "c": (d_c[dmask][:, None], p_c[pmask][:, None]),
            "ln A(22)+c": (np.c_[d_A[dmask], d_c[dmask]], np.c_[p_A[pmask], p_c[pmask]])}
    for nm, (Xd, Xp) in covs.items():
        out.append(f"  covariates {nm:11s} only: held-out R^2 {r2(p_y[pmask], fit_cov(Xd, d_y[dmask], Xp)):+.3f}")
    # prefix-6 mean as an extra regressor on top of covariates (prefix mean for discovery rules is leave-one-out)
    p6_tr = np.array([np.mean([v for rr, v in zip(dr, d_y[dmask]) if rr[:6] == r[:6] and rr != r] or [d_y[dmask].mean()]) for r in dr])
    p6_te = prefix_pred(dr, d_y[dmask], pr_, 6)
    for nm, (Xd, Xp) in covs.items():
        pred = fit_cov(np.c_[Xd, p6_tr], d_y[dmask], np.c_[Xp, p6_te])
        out.append(f"  prefix-6 mean + {nm:11s}: held-out R^2 {r2(p_y[pmask], pred):+.3f}")
    n_groups = len({r[:6] for r in dr}); out.append(f"  (prefix-6 groups in discovery: {n_groups})")

txt = header("uv run experiments/archive/2026-10-kappa-rule-space/scripts/x2_prefix_heldout.py") + "EXPLORATORY: prefix model held out on independent runs\n" + "\n".join(out) + "\n"
(EXP / "results" / "x2_prefix_heldout.txt").write_text(txt); print(txt)
