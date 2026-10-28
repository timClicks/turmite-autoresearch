# /// script
# dependencies = ["polars", "numpy", "scipy"]
# ///
"""W3c confirmation of the prefix size-controlled gain (predictions P3c.1-P3c.6 in README, registered before any W3c rule was sampled).
Estimator = x3_w3b_checks.py / w3b_analyse.py logic, unchanged; training table = census only (W3b rules NOT added).
usage (repo root): uv run experiments/archive/2026-10-kappa-rule-space/scripts/w3c_analyse.py"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import numpy as np, polars as pl
from kcommon import *

raw = pl.read_csv(EXP / "dumps" / "w3c_probe.csv")
r = per_rule(raw).with_columns(base=pl.col("rule").str.split("@").list.first())
a22 = raw.filter(pl.col("k") == 22).select("rule", lnA22=pl.col("area").log())
r = r.join(a22, on="rule", how="left")
core = r.filter(pl.col("alpha_w").is_between(0.25, 0.42) & (pl.col("kappa") > 0))
fresh = rule_means(core, 6).with_columns(n=pl.col("base").str.len_chars())
esc = raw.filter(pl.col("escaped"))["rule"].n_unique()
out = [f"runs in probe csv: {raw['rule'].n_unique()}; runs that escaped the board: {esc}; runs fitted by per_rule: {r.height}; core-band runs: {core.height}",
       f"fresh rules with >= 6 core-band runs: {fresh.height} (n=13: {int((fresh['n'] == 13).sum())}, n=14: {int((fresh['n'] == 14).sum())}); of 300 sampled"]
fst_all = np.abs(fresh["g_k"].to_numpy()) < 0.05
out.append(f"stationary share of fresh core-band rules: {fst_all.mean():.3f} ({int(fst_all.sum())}/{fresh.height})")

cen = census().filter((pl.col("kappa") > 0) & pl.col("lnA22").is_not_null())
c_rules = cen["rule"].to_list(); c_y = np.log(cen["kappa"].to_numpy()); c_st = np.abs(cen["g_k"].to_numpy()) < 0.05; c_A = cen["lnA22"].to_numpy()
f_rules = fresh["base"].to_list(); f_y = fresh["lnk"].to_numpy(); f_A = fresh["lnA22"].to_numpy()


def table(rules_, y_, pmax=8):
    t = {q: {} for q in range(1, pmax + 1)}
    for rr, v in zip(rules_, y_):
        for q in range(1, pmax + 1):
            t[q].setdefault(rr[:q], []).append(v)
    return t


def lookup(t, test_rules, p, gm, min_n=3, loo_y=None):
    """Group-mean lookup with fallback; loo_y given -> leave-one-out for training rules (as x3: remove own value)."""
    out_ = []
    for i, rr in enumerate(test_rules):
        val = gm
        for q in range(p, 0, -1):
            g = t[q].get(rr[:q])
            if g is not None and loo_y is not None:
                g = list(g)
                if loo_y[i] in g:
                    g.remove(loo_y[i])
            if g is not None and len(g) >= min_n:
                val = float(np.mean(g)); break
        out_.append(val)
    return np.array(out_)


def r2_strict(y, pred, train_mean):
    return 1 - ((y - pred) ** 2).sum() / ((y - train_mean) ** 2).sum()


def ols(X, y):
    A = np.c_[np.ones(len(X)), X]; return np.linalg.lstsq(A, y, rcond=None)[0]


def app(b, X):
    return np.c_[np.ones(len(X)), X] @ b


res = {}
for label, tmask, fmask in (("stationary", c_st, fst_all), ("all", np.ones(len(c_y), bool), np.ones(len(f_y), bool))):
    tr = [x for x, m in zip(c_rules, tmask) if m]; ty = c_y[tmask]; tA = c_A[tmask]; gm = ty.mean()
    fr = [x for x, m in zip(f_rules, fmask) if m]; fy = f_y[fmask]; fA = f_A[fmask]
    T = table(tr, ty)
    out.append(f"\n[{label}] training census rules {len(tr)}, sd ln kappa {ty.std():.3f}; fresh rules {len(fr)}, sd ln kappa {fy.std():.3f}, mean {fy.mean():+.3f} vs training mean {gm:+.3f}")
    rs = {}
    for p in range(3, 9):
        rs[p] = r2_strict(fy, lookup(T, fr, p, gm), gm)
        out.append(f"  prefix<={p}: strict held-out R^2 {rs[p]:+.3f}")
    res[label] = rs
    b1 = ols(tA[:, None], ty); p1 = app(b1, fA[:, None]); a_alone = r2_strict(fy, p1, gm)
    out.append(f"  ln A(22) alone strict R^2 {a_alone:+.3f}")
    R = rng(31)
    for p in (6, 8):
        loo = lookup(T, tr, p, gm, loo_y=ty)
        b2 = ols(np.c_[tA, loo], ty); p2 = app(b2, np.c_[fA, lookup(T, fr, p, gm)])
        den = (fy - gm) ** 2

        def gain(idx):
            return (((fy[idx] - p1[idx]) ** 2).sum() - ((fy[idx] - p2[idx]) ** 2).sum()) / den[idx].sum()
        g0 = gain(np.arange(len(fy))); bs = np.array([gain(R.integers(0, len(fy), len(fy))) for _ in range(2000)])
        lo, hi = np.percentile(bs, [2.5, 97.5])
        out.append(f"  prefix-{p} size-controlled gain: {g0:+.3f}, bootstrap 95% CI {lo:+.3f}..{hi:+.3f} (B=2000, rule resample); with prefix {r2_strict(fy, p2, gm):+.3f} vs alone {a_alone:+.3f}")
        res[f"{label}_gain{p}"] = (g0, lo, hi); res[f"{label}_alone"] = a_alone
    if label == "stationary":
        Rs = rng(11); sh = [r2_strict(fy, lookup(table(tr, Rs.permutation(ty)), fr, 6, gm), gm) for _ in range(200)]
        out.append(f"  shuffled-label control, prefix-6 strict R^2 over 200 permutations: median {np.median(sh):+.3f}, 95th pct {np.percentile(sh, 95):+.3f}")
        res["shuffle"] = (np.median(sh), np.percentile(sh, 95)); res["n_stat"] = len(fr)

s = res["stationary"]; g8 = res["stationary_gain8"]; g6 = res["stationary_gain6"]; m, q95 = res["shuffle"]
nk = fresh.height
out += ["\nPre-registered verdicts (README 'W3c'):",
        f"P3c.1 p=8 gain >= 0.15 and CI lower > 0: {g8[0]:+.3f} [{g8[1]:+.3f}, {g8[2]:+.3f}] -> {'HELD' if g8[0] >= 0.15 and g8[1] > 0 else 'FAILED'}"
        + ("" if g8[0] < 0.15 or g8[1] > 0 else " (point >= 0.15 but lower bound <= 0: inconclusive)"),
        f"P3c.2 p=6 gain >= 0.15 and CI lower > 0: {g6[0]:+.3f} [{g6[1]:+.3f}, {g6[2]:+.3f}] -> {'HELD' if g6[0] >= 0.15 and g6[1] > 0 else 'FAILED'}",
        f"P3c.3 stationary strict R^2 p=8 >= 0.40 and p=6 >= 0.30: {s[8]:+.3f}, {s[6]:+.3f} -> {'HELD' if s[8] >= 0.40 and s[6] >= 0.30 else 'FAILED'}",
        f"P3c.4 ln A(22)-alone R^2 within 0.15 of 0.569: {res['stationary_alone']:+.3f} -> {'HELD' if abs(res['stationary_alone'] - 0.569) <= 0.15 else 'FAILED'}",
        f"P3c.5 shuffle median <= +0.02 and 95th <= +0.08: {m:+.3f}, {q95:+.3f} -> {'HELD' if m <= 0.02 and q95 <= 0.08 else 'FAILED'}",
        f"P3c.6 >= 120 of 300 rules kept (>= 6 core-band runs): {nk} -> {'HELD' if nk >= 120 else 'FAILED'}" + ("; < 100 kept, P3c.1/P3c.2 not judged" if nk < 100 else "")]
txt = header("uv run experiments/archive/2026-10-kappa-rule-space/scripts/w3c_analyse.py") + "\n".join(out) + "\n"
(EXP / "results" / "w3c_stats.txt").write_text(txt); print(txt)
