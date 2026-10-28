# /// script
# dependencies = ["polars", "numpy", "scipy"]
# ///
"""EXPLORATORY follow-ups to W3b (not pre-registered): (1) bootstrap CI over fresh rules for the size-controlled gain at prefix 6 and 8,
(2) selection check: the 150 sampled rules vs the 89 with >= 6 core-band runs (229 runs escaped the 8192 board).
usage (repo root): uv run experiments/archive/2026-10-kappa-rule-space/scripts/x3_w3b_checks.py"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import numpy as np, polars as pl
from kcommon import *

raw = pl.read_csv(EXP / "dumps" / "w3b_probe.csv")
r = per_rule(raw).with_columns(base=pl.col("rule").str.split("@").list.first())
a22 = raw.filter(pl.col("k") == 22).select("rule", lnA22=pl.col("area").log())
r = r.join(a22, on="rule", how="left")
core = r.filter(pl.col("alpha_w").is_between(0.25, 0.42) & (pl.col("kappa") > 0))
fresh = rule_means(core, 6)
sampled = [l.strip() for l in open(EXP / "results" / "w3b_rules.txt") if l.strip()]
cen = census().filter((pl.col("kappa") > 0) & pl.col("lnA22").is_not_null())
tr_all = cen["rule"].to_list(); ty_all = np.log(cen["kappa"].to_numpy()); tA_all = cen["lnA22"].to_numpy(); tst = np.abs(cen["g_k"].to_numpy()) < 0.05
tr = [x for x, m in zip(tr_all, tst) if m]; ty = ty_all[tst]; tA = tA_all[tst]; gm = ty.mean()


def table(rules_, y_, pmax=8):
    t = {q: {} for q in range(1, pmax + 1)}
    for rr, v in zip(rules_, y_):
        for q in range(1, pmax + 1):
            t[q].setdefault(rr[:q], []).append(v)
    return t


T = table(tr, ty)


def lookup(rules_, p, min_n=3, loo=False, own=None):
    out_ = []
    for i, rr in enumerate(rules_):
        val = gm
        for q in range(p, 0, -1):
            g = T[q].get(rr[:q])
            if g is not None and loo:
                g = list(g); g.remove(ty[i]) if ty[i] in g else None
            if g is not None and len(g) >= min_n:
                val = float(np.mean(g)); break
        out_.append(val)
    return np.array(out_)


def ols(X, y):
    A = np.c_[np.ones(len(X)), X]; return np.linalg.lstsq(A, y, rcond=None)[0]


def app(b, X):
    return np.c_[np.ones(len(X)), X] @ b


out = []
fs = np.abs(fresh["g_k"].to_numpy()) < 0.05
fr = [x for x, m in zip(fresh["base"].to_list(), fs) if m]; fy = fresh["lnk"].to_numpy()[fs]; fA = fresh["lnA22"].to_numpy()[fs]
b1 = ols(tA[:, None], ty); p1 = app(b1, fA[:, None])
R = rng(13)
for p in (6, 8):
    loo = lookup(tr, p, loo=True); b2 = ols(np.c_[tA, loo], ty); pf = lookup(fr, p); p2 = app(b2, np.c_[fA, pf])
    den = ((fy - gm) ** 2)
    def gain(idx):
        s0 = ((fy[idx] - p1[idx]) ** 2).sum(); s1 = ((fy[idx] - p2[idx]) ** 2).sum(); return (s0 - s1) / ((fy[idx] - gm) ** 2).sum()
    g0 = gain(np.arange(len(fy))); bs = np.array([gain(R.integers(0, len(fy), len(fy))) for _ in range(2000)])
    out.append(f"prefix-{p} size-controlled gain (strict R^2 of ln A(22)+prefix minus ln A(22) alone) on {len(fy)} stationary fresh rules: {g0:+.3f}, bootstrap 95% CI {np.percentile(bs, 2.5):+.3f}..{np.percentile(bs, 97.5):+.3f}")
    out.append(f"   strict R^2: ln A(22) alone {1 - ((fy - p1) ** 2).sum() / den.sum():+.3f}; with prefix-{p} {1 - ((fy - p2) ** 2).sum() / den.sum():+.3f}")

# selection: sampled rules, included vs excluded; prefix-6 predicted value (from the training table, no fresh data)
inc = set(fresh["base"].to_list())
pred6 = lookup(sampled, 6)
m_in = np.array([s in inc for s in sampled])
out.append(f"\nselection: sampled {len(sampled)}, included (>=6 core-band runs) {int(m_in.sum())}; prefix-6 predicted ln kappa mean: included {pred6[m_in].mean():+.3f}, excluded {pred6[~m_in].mean():+.3f}")
esc = raw.filter(pl.col("escaped")).with_columns(base=pl.col("rule").str.split("@").list.first()).group_by("base").agg(n=pl.len())
esc_n = dict(zip(esc["base"], esc["n"]))
out.append(f"runs escaped per sampled rule: rules with 0 escapes {sum(1 for s in sampled if s not in esc_n)}, 1-4: {sum(1 for s in sampled if 1 <= esc_n.get(s, 0) <= 4)}, 5-8: {sum(1 for s in sampled if esc_n.get(s, 0) >= 5)}")
from scipy.stats import spearmanr
cnt = np.array([esc_n.get(s, 0) for s in sampled])
out.append(f"Spearman(prefix-6 predicted ln kappa, escapes per rule) over sampled rules: {spearmanr(pred6, cnt)[0]:+.3f}")
txt = header("uv run experiments/archive/2026-10-kappa-rule-space/scripts/x3_w3b_checks.py") + "EXPLORATORY\n" + "\n".join(out) + "\n"
(EXP / "results" / "x3_w3b_checks.txt").write_text(txt); print(txt)
