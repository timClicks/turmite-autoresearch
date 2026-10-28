# /// script
# dependencies = ["polars", "numpy", "scipy"]
# ///
"""W3b confirmatory test of the prefix lookup on fresh length-13/14 rules (predictions P3b.1-P3b.6 in README, registered before the run).
usage (repo root): uv run experiments/archive/2026-10-kappa-rule-space/scripts/w3b_analyse.py"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import numpy as np, polars as pl
from scipy.stats import spearmanr
from kcommon import *

raw = pl.read_csv(EXP / "dumps" / "w3b_probe.csv")
r = per_rule(raw).with_columns(base=pl.col("rule").str.split("@").list.first())
a22 = raw.filter(pl.col("k") == 22).select("rule", lnA22=pl.col("area").log())
r = r.join(a22, on="rule", how="left")
n_runs_total = raw["rule"].n_unique(); esc = raw.filter(pl.col("escaped"))["rule"].n_unique()
core = r.filter(pl.col("alpha_w").is_between(0.25, 0.42) & (pl.col("kappa") > 0))
fresh = rule_means(core, 6).with_columns(n=pl.col("base").str.len_chars())
out = [f"runs in probe csv: {n_runs_total}; runs that escaped the board: {esc}; runs fitted by per_rule: {r.height}; core-band runs: {core.height}",
       f"fresh rules with >= 6 core-band runs: {fresh.height} (n=13: {int((fresh['n'] == 13).sum())}, n=14: {int((fresh['n'] == 14).sum())}); of 150 sampled"]
fst = np.abs(fresh["g_k"].to_numpy()) < 0.05
out.append(f"stationary (|median g_k|<0.05) share of fresh core-band rules: {fst.mean():.3f} ({int(fst.sum())}/{fresh.height})")

cen = census().filter((pl.col("kappa") > 0) & pl.col("lnA22").is_not_null())
c_rules = cen["rule"].to_list(); c_y = np.log(cen["kappa"].to_numpy()); c_st = np.abs(cen["g_k"].to_numpy()) < 0.05; c_A = cen["lnA22"].to_numpy()
f_rules = fresh["base"].to_list(); f_y = fresh["lnk"].to_numpy(); f_A = fresh["lnA22"].to_numpy()


def table(rules_, y_, pmax=8):
    t = {q: {} for q in range(1, pmax + 1)}
    for rr, v in zip(rules_, y_):
        for q in range(1, pmax + 1):
            t[q].setdefault(rr[:q], []).append(v)
    return t


def lookup(t, test_rules, p, gm, min_n=3):
    out_ = []
    for rr in test_rules:
        val = gm
        for q in range(p, 0, -1):
            g = t[q].get(rr[:q])
            if g is not None and len(g) >= min_n:
                val = float(np.mean(g)); break
        out_.append(val)
    return np.array(out_)


def r2_strict(y, pred, train_mean):
    return 1 - ((y - pred) ** 2).sum() / ((y - train_mean) ** 2).sum()


def r2_fresh(y, pred):
    return 1 - ((y - pred) ** 2).sum() / ((y - y.mean()) ** 2).sum()


results = {}
for label, tmask, fmask in (("stationary", c_st, fst), ("all", np.ones(len(c_y), bool), np.ones(len(f_y), bool))):
    tr = [x for x, m in zip(c_rules, tmask) if m]; ty = c_y[tmask]; gm = ty.mean()
    fr = [x for x, m in zip(f_rules, fmask) if m]; fy = f_y[fmask]
    T = table(tr, ty)
    out.append(f"\n[{label}] training census rules {len(tr)}, sd ln kappa {ty.std():.3f}; fresh rules {len(fr)}, sd ln kappa {fy.std():.3f}, mean {fy.mean():+.3f} vs training mean {gm:+.3f}")
    rs = {}
    for p in range(3, 9):
        pred = lookup(T, fr, p, gm)
        rs[p] = r2_strict(fy, pred, gm)
        out.append(f"  prefix<={p}: strict held-out R^2 {rs[p]:+.3f}; vs fresh mean {r2_fresh(fy, pred):+.3f}; corr {np.corrcoef(pred, fy)[0, 1]:+.3f}")
    results[label] = rs
    if label == "stationary":
        sp = spearmanr(list(range(4, 9)), [rs[p] for p in range(4, 9)])[0]
        out.append(f"  P3b.6 Spearman(R^2, p) over p=4..8: {sp:+.3f}")
        # shuffled-label control for prefix-6
        R = rng(11); sh = []
        for _ in range(200):
            Tp = table(tr, R.permutation(ty))
            sh.append(r2_strict(fy, lookup(Tp, fr, 6, gm), gm))
        out.append(f"  P3b.4 shuffled-label control, prefix-6 strict R^2 over 200 permutations: median {np.median(sh):+.3f}, 95th pct {np.percentile(sh, 95):+.3f}")
        results["shuffle"] = (np.median(sh), np.percentile(sh, 95))
        # size control
        a_tr = c_A[tmask]
        def ols(X, y):
            A_ = np.c_[np.ones(len(X)), X]; return np.linalg.lstsq(A_, y, rcond=None)[0]
        def app(b, X):
            return np.c_[np.ones(len(X)), X] @ b
        b1 = ols(a_tr[:, None], ty); p1 = app(b1, f_A[fmask][:, None])
        # leave-one-out prefix-6 mean for training rules
        loo = np.array([np.mean([v for rr2, v in zip(tr, ty) if rr2[:6] == rr[:6] and rr2 is not rr] or [gm]) for rr in tr])
        b2 = ols(np.c_[a_tr, loo], ty); p6 = lookup(T, fr, 6, gm); p2 = app(b2, np.c_[f_A[fmask], p6])
        out.append(f"  size control: ln A(22) alone strict R^2 {r2_strict(fy, p1, gm):+.3f}; ln A(22)+prefix-6 mean {r2_strict(fy, p2, gm):+.3f}; gain {r2_strict(fy, p2, gm) - r2_strict(fy, p1, gm):+.3f}")
        results["gain"] = r2_strict(fy, p2, gm) - r2_strict(fy, p1, gm)

out.append("\nPre-registered verdicts (README 'W3b addendum'):")
s, a = results["stationary"], results["all"]
out.append(f"P3b.1 stationary strict R^2 prefix-6 >= 0.20 and prefix-8 >= 0.25: {s[6]:+.3f}, {s[8]:+.3f} -> {'HELD' if s[6] >= 0.20 and s[8] >= 0.25 else 'FAILED'}")
out.append(f"P3b.2 all-rules prefix-6 >= 0.08: {a[6]:+.3f} -> {'HELD' if a[6] >= 0.08 else 'FAILED'}")
out.append(f"P3b.3 size-controlled gain < 0.15 (bar NOT cleared): {results['gain']:+.3f} -> {'HELD (bar not cleared)' if results['gain'] < 0.15 else 'FAILED (bar cleared)'}")
m, q95 = results["shuffle"]
out.append(f"P3b.4 shuffle control median <= +0.02 and 95th pct <= +0.08: {m:+.3f}, {q95:+.3f} -> {'HELD' if m <= 0.02 and q95 <= 0.08 else 'FAILED'}")
out.append(f"P3b.5 stationary share >= 0.75: {fst.mean():.3f} -> {'HELD' if fst.mean() >= 0.75 else 'FAILED'}")
txt = header("uv run experiments/archive/2026-10-kappa-rule-space/scripts/w3b_analyse.py") + "\n".join(out) + "\n"
(EXP / "results" / "w3b_stats.txt").write_text(txt); print(txt)
