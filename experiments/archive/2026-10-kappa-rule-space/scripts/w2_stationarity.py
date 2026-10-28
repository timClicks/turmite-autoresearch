# /// script
# dependencies = ["polars", "numpy", "scipy"]
# ///
"""W2: how much of kappa's tail and rule-dependence is drift (g_k = log-log slope of kappa over k=20..26)?
usage (repo root): uv run experiments/archive/2026-10-kappa-rule-space/scripts/w2_stationarity.py"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import numpy as np, polars as pl
from kcommon import *

files = ["b2_probe.csv", "item21_probe.csv", "patched.csv"]
runs = pool_runs(files)
pool = rule_means(runs)
cen = census().filter(pl.col("kappa") > 0)
out = []
out.append(f"pool-192 rules: {pool.height}; census non-bursty with kappa>0: {cen.height}")
out.append(f"pool g_k (median over runs): quantiles 5/25/50/75/95 = " + " ".join(f"{q:+.3f}" for q in np.quantile(pool['g_k'].to_numpy(), [.05, .25, .5, .75, .95])))

y = pool["lnk"].to_numpy(); kap = pool["kappa"].to_numpy(); gk = pool["g_k"].to_numpy()
X = np.array([onehot(s) for s in pool["base"].to_list()])
rules = pool["base"].to_list()

def block(thr):
    st = np.abs(gk) < thr
    res = {"thr": thr, "n_stat": int(st.sum()), "share": st.mean()}
    tail = kap > 3
    res["tail_n"] = int(tail.sum()); res["tail_nonstat"] = float((~st[tail]).mean()) if tail.any() else float("nan")
    res["sd_all"] = y.std(ddof=1); res["sd_stat"] = y[st].std(ddof=1)
    # ICC on stationary rules (runs)
    sr = set(np.array(rules)[st])
    g = [grp["kappa"].log().to_numpy() for b, grp in runs.group_by("base") if b[0] in sr]
    res["icc_stat"] = icc_groups(g)[0]; res["n_icc"] = icc_groups(g)[3]
    ns = set(np.array(rules)[~st]); g2 = [grp["kappa"].log().to_numpy() for b, grp in runs.group_by("base") if b[0] in ns]
    res["icc_nonstat"] = icc_groups(g2)[0] if len(g2) > 5 else float("nan"); res["n_icc_ns"] = icc_groups(g2)[3] if len(g2) > 5 else 0
    res["r2_stat"] = loo_ridge_r2(X[st], y[st], 10) if st.sum() > 30 else float("nan")
    res["r2_nonstat"] = loo_ridge_r2(X[~st], y[~st], 10) if (~st).sum() > 30 else float("nan")
    return res

out.append("\nsensitivity table (pool-192 rules, stationary = |median g_k| < thr):")
out.append("thr    n_stat  share  tail(k>3): n, nonstationary share | sd ln k all -> stat (ratio) | ICC stat (rules) / nonstat (rules) | letter LOO R^2 stat / nonstat")
R = {}
for thr in (0.03, 0.05, 0.10):
    r = block(thr); R[thr] = r
    out.append(f"{thr:.2f}  {r['n_stat']:6d}  {r['share']:.2f}   n={r['tail_n']:3d}, {r['tail_nonstat']:.2f}   | {r['sd_all']:.3f} -> {r['sd_stat']:.3f} ({r['sd_stat']/r['sd_all']:.2f})   | "
               f"{r['icc_stat']:.3f} ({r['n_icc']}) / {r['icc_nonstat']:.3f} ({r['n_icc_ns']})   | {r['r2_stat']:+.3f} / {r['r2_nonstat']:+.3f}")

# census version of P2.1 / P2.2 (single run kappa; noisier)
cg = np.abs(cen["g_k"].to_numpy()) < 0.05; ck = cen["kappa"].to_numpy(); cl = np.log(ck)
out.append(f"\ncensus (single runs, non-bursty, kappa>0; stationary |g_k|<0.05 share {cg.mean():.3f}): kappa>3: n={int((ck > 3).sum())}, non-stationary share {(~cg[ck > 3]).mean():.2f}; kappa<0.3: n={int((ck < 0.3).sum())}, non-stationary share {(~cg[ck < 0.3]).mean():.2f}")
out.append(f"census sd ln kappa all {cl.std(ddof=1):.3f} -> stationary {cl[cg].std(ddof=1):.3f} (ratio {cl[cg].std(ddof=1)/cl.std(ddof=1):.2f}); quantiles of kappa among stationary 1/10/50/90/99: " + " ".join(f"{q:.2f}" for q in np.quantile(ck[cg], [.01, .1, .5, .9, .99])))
out.append(f"census kappa distribution all 1/10/50/90/99: " + " ".join(f"{q:.2f}" for q in np.quantile(ck, [.01, .1, .5, .9, .99])))

# pool rules with kappa>5: drift and kappa(k) flattening (rule-mean kappa per k from the raw windows)
hi = [(b, k, g) for b, k, g in zip(rules, kap, gk) if k > 5]
out.append(f"\npool rules with rule-mean kappa > 5: {len(hi)}; list (rule, kappa, median g_k):")
for b, k, g in sorted(hi, key=lambda t: -t[1])[:15]:
    out.append(f"  {b:14s} kappa {k:8.2f}  g_k {g:+.3f}")
if hi:
    out.append(f"  stationary (|g_k|<0.05) among them: {sum(abs(g) < 0.05 for _, _, g in hi)}/{len(hi)}")

# which armc rules (T1 range 0.24..183.9) -- g_k
armc = [l.strip() for l in open(legacy("armc_specs.txt")) if l.strip()]
sub = pool.filter(pl.col("base").is_in(armc))
out.append(f"armc rules in pool-192: {sub.height}/{len(armc)}; kappa>5: {int((sub['kappa'] > 5).sum())}, of which |g_k|>=0.05: {int(((sub['kappa'] > 5) & (sub['g_k'].abs() >= 0.05)).sum())}")

# Pre-registered verdicts at thr=0.05
r = R[0.05]
out.append("\nPre-registered verdicts at |g_k|<0.05 (pool-192; README W2):")
out.append(f"P2.1 >=50% of rules with kappa>3 non-stationary: {r['tail_nonstat']:.2f} (n={r['tail_n']}) -> {'HELD' if r['tail_nonstat'] >= 0.5 else 'FAILED'}")
out.append(f"P2.2 sd ratio stationary/all <= 0.7: {r['sd_stat']/r['sd_all']:.2f} -> {'HELD' if r['sd_stat']/r['sd_all'] <= 0.7 else 'FAILED'}")
out.append(f"P2.3 ICC(ln kappa) among stationary rules >= 0.45: {r['icc_stat']:.3f} -> {'HELD' if r['icc_stat'] >= 0.45 else 'FAILED'}")
out.append(f"P2.4 letter LOO R^2 on stationary <= 0.10: {r['r2_stat']:+.3f} -> {'HELD' if r['r2_stat'] <= 0.10 else 'FAILED'}")
txt = header("uv run experiments/archive/2026-10-kappa-rule-space/scripts/w2_stationarity.py") + "\n".join(out) + "\n"
(EXP / "results" / "w2_stationarity.txt").write_text(txt); print(txt)
