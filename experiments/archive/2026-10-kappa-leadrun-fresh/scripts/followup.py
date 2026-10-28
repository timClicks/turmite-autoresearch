# /// script
# dependencies = ["numpy", "polars", "scipy"]
# ///
"""Part A of the registered follow-up (../README.md): refit-on-shuffle nulls and selection bounds.
Also exports results/fresh_rules.csv (one row per sampled rule) so notebook.ipynb need not read dumps/.
usage (repo root): uv run experiments/archive/2026-10-kappa-leadrun-fresh/scripts/followup.py"""
from pathlib import Path
import json, subprocess, sys
import numpy as np, polars as pl

EXP = Path(__file__).resolve().parents[1]
ROOT = EXP.parents[2]
sys.path.insert(0, str(ROOT / "experiments/archive/2026-10-kappa-rule-space/scripts"))
from kcommon import census, per_rule, rule_means  # noqa: E402
from prefix_audit import basis  # noqa: E402

SEED, NB, LCAP = 20261016, 2000, 6
rng = np.random.default_rng(SEED + 7)
lead = lambda s: len(s) - len(s.lstrip(s[0]))

raw = pl.read_csv(EXP / "dumps/probe.csv")
runs = per_rule(raw).with_columns(base=pl.col("rule").str.split("@").list.first())
runs = runs.join(raw.filter(pl.col("k") == 22).select("rule", lnA22=pl.col("area").log()), on="rule", how="left")
core = runs.filter(pl.col("alpha_w").is_between(.25, .42) & (pl.col("kappa") > 0))
fresh = rule_means(core, 6)
sampled = (EXP / "results/rules.txt").read_text().split()
esc = (raw.with_columns(base=pl.col("rule").str.split("@").list.first())
       .group_by("rule", "base").agg(pl.col("escaped").any())
       .group_by("base").agg(n_esc=pl.col("escaped").sum()))
tab = (pl.DataFrame({"rule": sampled})
       .with_columns(lead=pl.col("rule").map_elements(lead, return_dtype=pl.Int64), n=pl.col("rule").str.len_chars())
       .join(esc, left_on="rule", right_on="base", how="left")
       .join(fresh, left_on="rule", right_on="base", how="left")
       .with_columns(kept=pl.col("n_runs").is_not_null(), stationary=pl.col("g_k").abs() < .05)
       .with_columns(pl.col("stationary").fill_null(False)))
tab.write_csv(EXP / "results/fresh_rules.csv")
stat = tab.filter(pl.col("stationary"))

cen = census().filter((pl.col("kappa") > 0) & pl.col("lnA22").is_not_null()).sort("rule")
tr = cen.filter(pl.col("g_k").abs() < .05)
rules, tests = tr["rule"].to_list(), stat["rule"].to_list()
y, v = np.log(tr["kappa"].to_numpy()), stat["lnk"].to_numpy()
a, b = tr["lnA22"].to_numpy(), stat["lnA22"].to_numpy()
xa, za = basis(a, b, True)
den = ((v - y.mean()) ** 2).sum()


def ols(Xtr, ytr, Xte):
    return np.c_[np.ones(len(Xte)), Xte] @ np.linalg.lstsq(np.c_[np.ones(len(Xtr)), Xtr], ytr, rcond=None)[0]


base_pred = ols(xa, y, za)
trl = np.array([min(lead(s), LCAP) for s in rules], float)
tel = np.array([min(lead(s), LCAP) for s in tests], float)


def gain(ftr, fte):
    p = ols(np.c_[xa, ftr], y, np.c_[za, fte])
    return float((((v - base_pred) ** 2) - ((v - p) ** 2)).sum() / den)


obs = gain(trl, tel)
sha = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
out = [f"# cmd: uv run experiments/archive/2026-10-kappa-leadrun-fresh/scripts/followup.py  git: {sha} (tree dirty)  seed {SEED}",
       f"fresh stationary n={len(v)}, census stationary n={len(y)}; observed gain {obs:+.3f}"]
res = {"observed_gain": obs}

# A1: refit-on-shuffle nulls
qs = np.quantile(np.r_[a, b], [.2, .4, .6, .8])


def perm(l, lnA, within):
    if not within:
        return rng.permutation(l)
    o = l.copy()
    bins = np.digitize(lnA, qs)
    for k in range(5):
        i = np.where(bins == k)[0]
        o[i] = rng.permutation(l[i])
    return o


for name, within in (("unrestricted", False), ("within ln A quintile", True)):
    g = np.array([gain(perm(trl, a, within), perm(tel, b, within)) for _ in range(200)])
    res["A1 " + name] = dict(median=float(np.median(g)), p95=float(np.quantile(g, .95)),
                             p99=float(np.quantile(g, .99)), max=float(g.max()))
    out.append(f"A1 {name:20s} gain median {np.median(g):+.3f} p95 {np.quantile(g, .95):+.3f} "
               f"p99 {np.quantile(g, .99):+.3f} max {g.max():+.3f}  (obs {obs:+.3f}; |median|<=0.02: {abs(np.median(g)) <= .02})")

# A2: selection bounds. Fresh-only slope of ln kappa on spline(ln A) + lead, on a subset / weighted.
_, zf = basis(b, b, True)


def slope(ix, w=None):
    A = np.c_[np.ones(len(ix)), zf[ix], tel[ix]]
    W = np.ones(len(ix)) if w is None else w[ix]
    return np.linalg.lstsq(A * np.sqrt(W)[:, None], v[ix] * np.sqrt(W), rcond=None)[0][-1]


def boot(sel, w=None):
    ix = np.where(sel)[0]
    s0 = slope(ix, w)
    bs = [slope(rng.choice(ix, len(ix)), w) for _ in range(NB)]
    return float(s0), [float(q) for q in np.quantile(bs, [.025, .975])]


ret = {k: tab.filter(pl.col("lead") == k)["stationary"].sum() / 50 for k in range(1, 7)}
w = np.array([1 / max(ret[int(min(l, 6))], 1e-9) for l in tel])
nlen = stat["n"].to_numpy()
for name, sel, ww in (("all leads", np.ones(len(v), bool), None), ("leads 1-3", tel <= 3, None),
                      ("leads 1-4", tel <= 4, None), ("length 13", nlen == 13, None), ("length 14", nlen == 14, None),
                      ("all, inverse-retention weights", np.ones(len(v), bool), w)):
    s, ci = boot(sel, ww)
    res["A2 " + name] = dict(slope=s, ci=ci, n=int(sel.sum()))
    out.append(f"A2 slope [{name:32s}] {s:+.3f} CI [{ci[0]:+.3f},{ci[1]:+.3f}] n={int(sel.sum())}")
out.append("A2 dropouts by lead (50 sampled each): rules with >=1 escaped run, mean escaped runs/rule, kept, stationary")
for k in range(1, 7):
    t = tab.filter(pl.col("lead") == k)
    out.append(f"  lead {k}: any_escape {int((t['n_esc'] > 0).sum())}/50, mean {t['n_esc'].mean():.2f}, "
               f"kept {int(t['kept'].sum())}, stationary {int(t['stationary'].sum())}")
for n_ in (13, 14):
    t = tab.filter(pl.col("n") == n_)
    out.append(f"  length {n_}: kept {int(t['kept'].sum())}/150, stationary {int(t['stationary'].sum())}/150, "
               f"mean escaped runs {t['n_esc'].mean():.2f}")
(EXP / "results/followup.txt").write_text("\n".join(out) + "\n")
(EXP / "results/followup.json").write_text(json.dumps(res, indent=2) + "\n")
print("\n".join(out))
