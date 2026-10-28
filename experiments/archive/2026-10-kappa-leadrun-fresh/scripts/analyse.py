# /// script
# dependencies = ["numpy", "polars", "scipy"]
# ///
"""Leading-run test on fresh lead-stratified rules; predictions L1-L6 in ../README.md (registered before the probe run).
usage (repo root): uv run experiments/archive/2026-10-kappa-leadrun-fresh/scripts/analyse.py"""
from pathlib import Path
import json, subprocess, sys
import numpy as np, polars as pl

EXP = Path(__file__).resolve().parents[1]
ROOT = EXP.parents[2]
KR = ROOT / "experiments/archive/2026-10-kappa-rule-space/scripts"
sys.path.insert(0, str(KR))
from kcommon import census, per_rule, rule_means  # noqa: E402
from prefix_audit import basis, predict  # noqa: E402

SEED, NB = 20261016, 2000
rng = np.random.default_rng(SEED)
LCAP = 6

def lead(s):
    return len(s) - len(s.lstrip(s[0]))

raw = pl.read_csv(EXP / "dumps/probe.csv")
runs = per_rule(raw).with_columns(base=pl.col("rule").str.split("@").list.first())
runs = runs.join(raw.filter(pl.col("k") == 22).select("rule", lnA22=pl.col("area").log()), on="rule", how="left")
core = runs.filter(pl.col("alpha_w").is_between(.25, .42) & (pl.col("kappa") > 0))
fresh = rule_means(core, 6)
sampled = [l.strip() for l in (EXP / "results/rules.txt").read_text().split()]
fresh_all = fresh
stat = fresh.filter(pl.col("g_k").abs() < .05)
sha = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
out = [f"# cmd: uv run experiments/archive/2026-10-kappa-leadrun-fresh/scripts/analyse.py  git: {sha} (tree dirty)  seed {SEED}",
       f"runs {raw['rule'].n_unique()}, escaped {raw.filter(pl.col('escaped'))['rule'].n_unique()}, fitted {runs.height}, core {core.height}; "
       f"rules with >=6 core runs {fresh.height}/300; stationary {stat.height}"]

# L5: retention by stratum
kept, st = set(fresh["base"]), set(stat["base"])
out.append("L5 retention by lead stratum (of 50 sampled): lead, kept(>=6 core runs), stationary")
ret = {}
for k in range(1, 7):
    rs = [r for r in sampled if lead(r) == k]
    ret[k] = (sum(r in kept for r in rs) / len(rs), sum(r in st for r in rs) / len(rs))
    out.append(f"  {k}: {ret[k][0]:.2f} {ret[k][1]:.2f}  (n={len(rs)})")
l5 = abs(ret[1][1] - ret[6][1]) < 0.20 and abs(ret[1][0] - ret[6][0]) < 0.20
out.append(f"L5 |lead1-lead6| both < 0.20: {'HELD' if l5 else 'FAILED'}")

cen = census().filter((pl.col("kappa") > 0) & pl.col("lnA22").is_not_null()).sort("rule")
tr = cen.filter(pl.col("g_k").abs() < .05)
rules, tests = tr["rule"].to_list(), stat["base"].to_list()
assert not set(rules) & set(tests)
y, v = np.log(tr["kappa"].to_numpy()), stat["lnk"].to_numpy()
a, b = tr["lnA22"].to_numpy(), stat["lnA22"].to_numpy()
xa, za = basis(a, b, True)
den = (v - y.mean()) ** 2
base_pred = predict(xa, y, za)
out.append(f"census stationary train n={len(y)}; fresh stationary test n={len(v)}; spline-only strict R2 on fresh = {1 - ((v-base_pred)**2).sum()/den.sum():.3f}")
tl = np.array([min(lead(s), LCAP) for s in tests], float)
out.append("fresh stationary rules per lead: " + ", ".join(f"{k}:{int((tl==k).sum())}" for k in range(1, 7)))
out.append(f"corr(lead, ln A22) fresh {np.corrcoef(tl, b)[0,1]:+.3f}; census {np.corrcoef([min(lead(s),LCAP) for s in rules], a)[0,1]:+.3f}")

def gain_ci(pred, idx_boot):
    c = (v - base_pred) ** 2 - (v - pred) ** 2
    return float(c.sum() / den.sum()), [float(q) for q in np.quantile(c[idx_boot].sum(1) / den[idx_boot].sum(1), [.025, .975])]

idx = rng.integers(0, len(v), (NB, len(v)))
res = {}

def fit_pred(feat_tr, feat_te):
    A = np.c_[np.ones(len(y)), xa, feat_tr]
    beta = np.linalg.lstsq(A, y, rcond=None)[0]
    return np.c_[np.ones(len(v)), za, feat_te] @ beta, beta[-feat_tr.shape[1]:] if feat_tr.ndim > 1 else beta[-1]

trl = np.array([min(lead(s), LCAP) for s in rules], float)
p_lead, b_cen = fit_pred(trl[:, None], tl[:, None])
b_cen = float(np.ravel(b_cen)[0])
g, ci = gain_ci(p_lead, idx)
res["L1"] = dict(gain=g, ci=ci, b_census=b_cen)
out.append(f"L1 gain of lead term {g:+.3f} CI [{ci[0]:+.3f},{ci[1]:+.3f}]; census slope b = {b_cen:+.3f}/step -> "
           f"{'HELD' if g >= .15 and ci[0] > 0 else 'FAILED'}")

# L2: refit slope on fresh
_, zf = basis(b, b, True)
def fresh_slope(ix):
    A = np.c_[np.ones(len(ix)), zf[ix], tl[ix]]
    return np.linalg.lstsq(A, v[ix], rcond=None)[0][-1]
sl = fresh_slope(np.arange(len(v))); bs = np.array([fresh_slope(i) for i in idx])
sci = [float(q) for q in np.quantile(bs, [.025, .975])]
l2 = .07 <= b_cen <= .13 and sci[0] > 0 and sci[0] <= b_cen <= sci[1]
res["L2"] = dict(slope_fresh=float(sl), ci=sci)
out.append(f"L2 census slope {b_cen:+.3f} in [0.07,0.13]: {.07<=b_cen<=.13}; fresh refit slope {sl:+.3f} CI [{sci[0]:+.3f},{sci[1]:+.3f}] -> {'HELD' if l2 else 'FAILED'}")

# L3: within-tertile slopes of (ln kappa - census spline-only prediction) on lead
resid = v - base_pred
cuts = np.quantile(b, [1/3, 2/3]); ter = np.digitize(b, cuts)
def within(ix):
    sl_t, num, den_ = [], 0.0, 0.0
    for t in range(3):
        m = ix[ter[ix] == t]
        if len(m) < 5 or tl[m].std() == 0:
            sl_t.append(np.nan); continue
        c = tl[m] - tl[m].mean(); num += (c * (resid[m] - resid[m].mean())).sum(); den_ += (c ** 2).sum()
        sl_t.append(float((c * (resid[m] - resid[m].mean())).sum() / (c ** 2).sum()))
    return sl_t, num / den_
tsl, pooled = within(np.arange(len(v)))
pb = np.array([within(i)[1] for i in idx]); pci = [float(q) for q in np.quantile(pb, [.025, .975])]
l3 = all(s > 0 for s in tsl) and pci[0] > 0
res["L3"] = dict(tertile_slopes=tsl, pooled=float(pooled), ci=pci)
out.append(f"L3 tertile slopes {[round(s,3) for s in tsl]}; pooled within-tertile {pooled:+.3f} CI [{pci[0]:+.3f},{pci[1]:+.3f}] -> {'HELD' if l3 else 'FAILED'}")

# L4: shuffle lead among fresh rules
gs = []
for rep in range(200):
    pl_, _ = fit_pred(trl[:, None], np.random.default_rng(SEED + 1000 + rep).permutation(tl)[:, None])
    c = (v - base_pred) ** 2 - (v - pl_) ** 2; gs.append(c.sum() / den.sum())
l4 = abs(np.median(gs)) <= .02 and np.quantile(gs, .95) <= .05
res["L4"] = dict(median=float(np.median(gs)), p95=float(np.quantile(gs, .95)))
out.append(f"L4 shuffled-lead gain median {np.median(gs):+.3f}, 95th {np.quantile(gs,.95):+.3f} -> {'HELD' if l4 else 'FAILED'}")
res["L5"] = dict(retention=ret, held=bool(l5))

# L6 descriptive alternatives, trained on census, scored on fresh
def r8(s): return sum(c == "R" for c in s[:8])
for name, f in (("R count first 8", r8), ("letter 2 is R", lambda s: s[1] == "R"), ("lead (capped 6)", lambda s: min(lead(s), LCAP))):
    ft = np.array([f(s) for s in rules], float); fe = np.array([f(s) for s in tests], float)
    p_, _ = fit_pred(ft[:, None], fe[:, None]); g_, c_ = gain_ci(p_, idx)
    res["L6 " + name] = dict(gain=g_, ci=c_)
    out.append(f"L6 {name:18s} gain {g_:+.3f} CI [{c_[0]:+.3f},{c_[1]:+.3f}]")
# per-lead mean residual (fresh), compare with decode table
out.append("mean residual vs census spline-only prediction, fresh stationary, by lead (compare leadrun_table.txt: -0.11,+0.04,+0.14,+0.24,+0.34,+0.45):")
for k in range(1, 7):
    m = tl == k
    out.append(f"  lead {k}: n={int(m.sum())} mean {resid[m].mean():+.3f} sd {resid[m].std(ddof=1):.3f}")
(EXP / "results/analysis.txt").write_text("\n".join(out) + "\n")
(EXP / "results/analysis.json").write_text(json.dumps(res, indent=2, default=float) + "\n")
print("\n".join(out))
