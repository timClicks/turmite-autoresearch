# /// script
# dependencies = ["numpy", "polars", "scipy"]
# ///
"""Part B analysis M1-M4 (../README.md, registered before the mutant run): paired single-flip mutants vs their bases.
usage (repo root): uv run experiments/archive/2026-10-kappa-leadrun-fresh/scripts/analyse_mutants.py"""
from pathlib import Path
import json, subprocess, sys
import numpy as np, polars as pl

EXP = Path(__file__).resolve().parents[1]
ROOT = EXP.parents[2]
sys.path.insert(0, str(ROOT / "experiments/archive/2026-10-kappa-rule-space/scripts"))
from kcommon import per_rule, rule_means  # noqa: E402

SEED, NB, LCAP = 20261016, 2000, 6
rng = np.random.default_rng(SEED + 11)

raw = pl.read_csv(EXP / "dumps/mutants.csv")
runs = per_rule(raw).with_columns(base=pl.col("rule").str.split("@").list.first())
runs = runs.join(raw.filter(pl.col("k") == 22).select("rule", lnA22=pl.col("area").log()), on="rule", how="left")
core = runs.filter(pl.col("alpha_w").is_between(.25, .42) & (pl.col("kappa") > 0))
mt = rule_means(core, 6).with_columns(stationary=pl.col("g_k").abs() < .05)
mut = pl.read_csv(EXP / "results/mutants.csv")
fr = pl.read_csv(EXP / "results/fresh_rules.csv").select("rule", b_lnk="lnk", b_lnA="lnA22")
pairs = (mut.join(fr, left_on="base", right_on="rule", how="inner")
         .join(mt.select("base", m_lnk="lnk", m_lnA="lnA22", m_stat="stationary"), left_on="mutant", right_on="base", how="left")
         .with_columns(kept=pl.col("m_lnk").is_not_null()))
ok = pairs.filter(pl.col("kept") & pl.col("m_stat")).with_columns(
    d=pl.col("m_lnk") - pl.col("b_lnk"), dA=pl.col("m_lnA") - pl.col("b_lnA"),
    dlead=pl.min_horizontal(pl.col("new_lead"), pl.lit(LCAP)) - pl.col("base_lead"))
sha = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
out = [f"# cmd: uv run experiments/archive/2026-10-kappa-leadrun-fresh/scripts/analyse_mutants.py  git: {sha} (tree dirty)  seed {SEED}",
       f"mutants {mut.height}, with base stationary-fresh row {pairs.height}, mutant kept {int(pairs['kept'].sum())}, kept+stationary pairs {ok.height}"]
res = {}


def ci(x, f=np.mean):
    x = np.asarray(x)
    bs = [f(x[rng.integers(0, len(x), len(x))]) for _ in range(NB)]
    return float(f(x)), [float(q) for q in np.quantile(bs, [.025, .975])]


arms = {}
for arm in "ESC":
    p = ok.filter(pl.col("arm") == arm)
    arms[arm] = p
    m, c = ci(p["d"].to_numpy())
    mA, cA = ci(p["dA"].to_numpy())
    res["arm " + arm] = dict(n=p.height, mean_d=m, ci=c, mean_dA=mA, ci_dA=cA, mean_dlead=float(p["dlead"].mean()))
    out.append(f"arm {arm}: n={p.height} mean d={m:+.3f} CI [{c[0]:+.3f},{c[1]:+.3f}]  mean dlnA22={mA:+.3f} [{cA[0]:+.3f},{cA[1]:+.3f}]  mean dlead={p['dlead'].mean():+.2f}")

# M1: pooled paired regression d ~ 1 + dlead + dA, bootstrap over pairs
D, X = ok["d"].to_numpy(), np.c_[np.ones(ok.height), ok["dlead"].to_numpy(), ok["dA"].to_numpy()]
coef = lambda ix: np.linalg.lstsq(X[ix], D[ix], rcond=None)[0]
b0 = coef(np.arange(len(D)))
bs = np.array([coef(rng.integers(0, len(D), len(D))) for _ in range(NB)])
bci = np.quantile(bs[:, 1], [.025, .975]); cci = np.quantile(bs[:, 2], [.025, .975])
res["M1 regression"] = dict(intercept=float(b0[0]), b_dlead=float(b0[1]), ci_b=[float(q) for q in bci], c_dA=float(b0[2]), ci_c=[float(q) for q in cci])
mE = res["arm E"]
m1 = mE["ci"][0] > 0 and bci[0] > 0
out.append(f"M1 arm E mean d {mE['mean_d']:+.3f} CI lower {mE['ci'][0]:+.3f}; pooled d ~ c0 + b*dlead + c*dA: b={b0[1]:+.3f} [{bci[0]:+.3f},{bci[1]:+.3f}], c={b0[2]:+.3f} [{cci[0]:+.3f},{cci[1]:+.3f}], c0={b0[0]:+.3f} -> {'HELD' if m1 else 'FAILED'}")

# M2: E - C
e, c_ = arms["E"]["d"].to_numpy(), arms["C"]["d"].to_numpy()
diff = np.array([e[rng.integers(0, len(e), len(e))].mean() - c_[rng.integers(0, len(c_), len(c_))].mean() for _ in range(NB)])
dci = np.quantile(diff, [.025, .975])
res["M2"] = dict(diff=float(e.mean() - c_.mean()), ci=[float(q) for q in dci])
out.append(f"M2 E - C mean d {e.mean() - c_.mean():+.3f} CI [{dci[0]:+.3f},{dci[1]:+.3f}] -> {'HELD' if dci[0] > 0 else 'FAILED'}")

# M3: S
sres = res["arm S"]
out.append(f"M3 arm S mean d {sres['mean_d']:+.3f} CI upper {sres['ci'][1]:+.3f} -> {'HELD' if sres['ci'][1] < 0 else 'FAILED'}")

# M4 retention (descriptive)
out.append("M4 retention of mutant given base stationary-fresh: arm, mutants, kept, kept+stationary")
for arm in "ESC":
    p = pairs.filter(pl.col("arm") == arm)
    k = int(p["kept"].sum()); ks = int((p["kept"] & p["m_stat"].fill_null(False)).sum())
    res["M4 " + arm] = dict(n=p.height, kept=k, kept_stat=ks)
    out.append(f"  {arm}: {p.height}, {k}, {ks}")

# descriptive: d per unit dlead in arms E and S, and area-matched E pairs
for arm in "ES":
    p = arms[arm]
    out.append(f"desc arm {arm}: d/dlead mean {np.mean(p['d'].to_numpy() / p['dlead'].to_numpy()):+.3f}; |dA|<0.15 pairs n={int((p['dA'].abs() < .15).sum())}, mean d {p.filter(pl.col('dA').abs() < .15)['d'].mean():+.3f}")
ok.write_csv(EXP / "results/mutant_pairs.csv")
(EXP / "results/mutants_analysis.txt").write_text("\n".join(out) + "\n")
(EXP / "results/mutants_analysis.json").write_text(json.dumps(res, indent=2) + "\n")
print("\n".join(out))
