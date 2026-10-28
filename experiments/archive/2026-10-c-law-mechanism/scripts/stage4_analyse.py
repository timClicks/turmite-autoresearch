# /// script
# dependencies = ["polars", "numpy"]
# ///
"""Stage 4 (README): 4a collider check, 4b growth identity on Part B pairs, 4c lead-preserving early flips (P1/P2).
usage: uv run experiments/archive/2026-10-c-law-mechanism/scripts/stage4_analyse.py"""
import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

root = Path(__file__).resolve().parents[4]
EXP = root / "experiments/archive/2026-10-c-law-mechanism"
R = EXP / "results"
LR = root / "experiments/archive/2026-10-kappa-leadrun-fresh/results"
sys.path.insert(0, str(root / "experiments/archive/2026-10-kappa-rule-space/scripts"))
from kcommon import per_rule, rule_means  # noqa: E402

SEED, NB = 20261019, 2000
rng = np.random.default_rng(SEED)
lines, res = [], {}


def say(s=""):
    print(s)
    lines.append(s)


def lead(s):
    k = 1
    while k < len(s) and s[k] == s[0]:
        k += 1
    return k


def ols(X, y):
    X = np.column_stack([np.ones(len(y))] + list(X))
    return np.linalg.lstsq(X, y, rcond=None)[0]


# ---------------------------------------------------------------- 4a
fr = pl.read_csv(LR / "fresh_rules.csv").filter(pl.col("kept") & pl.col("stationary"))
Y, Z, W = fr["lnk"].to_numpy(), np.log(fr["c"].to_numpy()), fr["lnA22"].to_numpy()
X = np.minimum(fr["lead"].to_numpy(), 6).astype(float)
say(f"4a: n = {len(Y)} fresh rules (kept, stationary), lead capped 6")
say(f"  marginal slopes on lead: ln kappa {ols([X], Y)[1]:+.3f}, ln c {ols([X], Z)[1]:+.3f}, ln A22 {ols([X], W)[1]:+.3f}")
bw = ols([Z, Y], W)
resid = W - (bw[0] + bw[1] * Z + bw[2] * Y)
say(f"  growth fit ln A22 = {bw[0]:.2f} + {bw[1]:.3f} ln c + {bw[2]:.3f} ln kappa, residual sd {resid.std(ddof=3):.3f}")
obs = ols([X, W], Y)
say(f"  observed Y ~ 1 + lead + lnA22: coef lead {obs[1]:+.3f}, lnA22 {obs[2]:+.3f}")
bX, bWn = [], []
for _ in range(NB):
    yp = rng.permutation(Y)
    wst = bw[0] + bw[1] * Z + bw[2] * yp + resid
    b = ols([X, wst], yp)
    bX.append(b[1])
    bWn.append(b[2])
bX, bWn = np.array(bX), np.array(bWn)
lo, hi = np.percentile(bX, [2.5, 97.5])
q1 = bool(lo <= obs[1] <= hi and abs(bX.mean() - obs[1]) <= 0.05)
q2 = bool(abs(bWn.mean() - obs[2]) <= 0.25)
say(f"  null (Y independent of lead and c, linked only through lnA22): coef lead mean {bX.mean():+.3f} [95% {lo:+.3f}, {hi:+.3f}], lnA22 mean {bWn.mean():+.3f} [{np.percentile(bWn, 2.5):+.3f}, {np.percentile(bWn, 97.5):+.3f}]")
say(f"  Q1 {'PASS' if q1 else 'FAIL'} (observed {obs[1]:+.3f} inside null interval and within 0.05 of its mean); Q2 {'PASS' if q2 else 'FAIL'} (observed lnA22 coef {obs[2]:+.3f} vs null {bWn.mean():+.3f})")
b3 = ols([X, W, Z], Y)
bs = []
for _ in range(NB):
    i = rng.integers(0, len(Y), len(Y))
    bs.append(ols([X[i], W[i], Z[i]], Y[i])[1])
ci3 = np.percentile(bs, [2.5, 97.5])
q3 = bool(abs(b3[1]) <= 0.07 or ci3[0] <= 0 <= ci3[1])
say(f"  Y ~ 1 + lead + lnA22 + ln c: coef lead {b3[1]:+.3f} [bootstrap {ci3[0]:+.3f}, {ci3[1]:+.3f}], lnA22 {b3[2]:+.3f}, ln c {b3[3]:+.3f} -> Q3 {'PASS' if q3 else 'FAIL'}")
res["4a"] = dict(n=len(Y), marginal_lead_on_lnk=float(ols([X], Y)[1]), marginal_lead_on_lnc=float(ols([X], Z)[1]), growth_fit=bw.tolist(),
                 obs_lead=float(obs[1]), obs_lnA=float(obs[2]), null_lead_mean=float(bX.mean()), null_lead_ci=[float(lo), float(hi)], null_lnA_mean=float(bWn.mean()),
                 with_c=dict(lead=float(b3[1]), ci=ci3.tolist(), lnA=float(b3[2]), lnc=float(b3[3])), Q1=q1, Q2=q2, Q3=q3)

# ---------------------------------------------------------------- tracer c
tc = {}
for l in (R / "trace_s4.jsonl").read_text().splitlines():
    d = json.loads(l)
    tc[d["spec"]] = (np.log(d["births"] / d["boundary_steps"]) if d["boundary_steps"] and not d["escaped"] else np.nan)
say(f"tracer c available for {sum(np.isfinite(v) for v in tc.values())} of {len(tc)} rules")

# ---------------------------------------------------------------- 4b
pr = pl.read_csv(LR / "mutant_pairs.csv").filter(pl.col("kept") & pl.col("m_stat"))
pr = pr.with_columns(dc=pl.struct("mutant", "base").map_elements(lambda s: tc.get(s["mutant"], np.nan) - tc.get(s["base"], np.nan), return_dtype=pl.Float64))
pr = pr.filter(pl.col("dc").is_finite())
d_, dA_, dc_ = pr["d"].to_numpy(), pr["dA"].to_numpy(), pr["dc"].to_numpy()
s = dc_ + d_
g = float((dA_ * s).sum() / (s * s).sum())
say(f"4b: {pr.height} Part B pairs with tracer c; dA = g (dc + d): g = {g:.3f}")
res["4b"] = dict(n=pr.height, g=g, arms={})
ok_arms = []
for arm in ("E", "S", "C"):
    m = (pr["arm"] == arm).to_numpy()
    pred, obsm = g * s[m].mean(), dA_[m].mean()
    ok_arms.append(abs(pred - obsm) <= 0.08)
    res["4b"]["arms"][arm] = dict(n=int(m.sum()), mean_dc=float(dc_[m].mean()), mean_d=float(d_[m].mean()), mean_dA_obs=float(obsm), mean_dA_pred=float(pred))
    say(f"   arm {arm} (n={m.sum()}): mean dc {dc_[m].mean():+.3f}, d {d_[m].mean():+.3f}, dA observed {obsm:+.3f}, predicted {pred:+.3f}")
res["4b"]["Q4"] = bool(0.5 <= g <= 0.9 and all(ok_arms))
say(f"   Q4 (g in [0.5, 0.9] and every arm within 0.08): {'PASS' if res['4b']['Q4'] else 'FAIL'}")

# ---------------------------------------------------------------- 4c
done = EXP / "dumps/p1_probe.done"
if done.exists():
    raw = pl.read_csv(EXP / "dumps/p1_probe.csv")
    runs = per_rule(raw).with_columns(base=pl.col("rule").str.split("@").list.first())
    runs = runs.join(raw.filter(pl.col("k") == 22).select("rule", lnA22=pl.col("area").log()), on="rule", how="left")
    core = runs.filter(pl.col("alpha_w").is_between(.25, .42) & (pl.col("kappa") > 0))
    mt = rule_means(core, 6).with_columns(stationary=pl.col("g_k").abs() < .05)
    mt.write_csv(R / "p1/p1_rule_means.csv")
    pm = pl.read_csv(R / "p1/p1_mutants.csv")
    fb = pl.read_csv(LR / "fresh_rules.csv").select("rule", b_lnk="lnk", b_lnA="lnA22", b_c="c")
    pp = (pm.join(fb, left_on="base", right_on="rule", how="inner")
          .join(mt.select("base", m_lnk="lnk", m_lnA="lnA22", m_stat="stationary"), left_on="mutant", right_on="base", how="left", suffix="_m"))
    pp = pp.with_columns(kept=pl.col("m_lnk").is_not_null())
    ok = pp.filter(pl.col("kept") & pl.col("m_stat")).with_columns(d=pl.col("m_lnk") - pl.col("b_lnk"), dA=pl.col("m_lnA") - pl.col("b_lnA"))
    ok = ok.with_columns(dc=pl.struct("mutant", "base").map_elements(lambda s: tc.get(s["mutant"], np.nan) - tc.get(s["base"], np.nan), return_dtype=pl.Float64))
    ok.write_csv(R / "p1/p1_pairs.csv")
    say(f"4c: {pm.height} P mutants; kept {int(pp['kept'].sum())}; kept and stationary pairs {ok.height} (retention {ok.height / pm.height:.2f}; "
        f"P1 {int((ok['arm'] == 'P1').sum())}/{int((pm['arm'] == 'P1').sum())}, P2 {int((ok['arm'] == 'P2').sum())}/{int((pm['arm'] == 'P2').sum())})")
    d, dA = ok["d"].to_numpy(), ok["dA"].to_numpy()
    bases = ok["base"].to_numpy()
    ub = np.unique(bases)
    idx = {b: np.where(bases == b)[0] for b in ub}

    def cluster_boot(f):
        out = []
        for _ in range(NB):
            pick = rng.integers(0, len(ub), len(ub))
            ii = np.concatenate([idx[ub[j]] for j in pick])
            out.append(f(ii))
        return np.percentile(out, [2.5, 97.5])

    md = float(d.mean())
    ci = cluster_boot(lambda ii: d[ii].mean())
    beta = float(np.polyfit(dA, d, 1)[0])
    resid = d - beta * dA
    ci_r = cluster_boot(lambda ii: (d[ii] - np.polyfit(dA[ii], d[ii], 1)[0] * dA[ii]).mean())
    p1 = bool(abs(md) <= 0.08 and ci[0] >= -0.15 and ci[1] <= 0.15)
    p2 = bool(md <= -0.10 and ci[1] < -0.03)
    p3 = bool(abs(resid.mean()) <= 0.08)
    say(f"  mean d = {md:+.3f} [cluster 95% {ci[0]:+.3f}, {ci[1]:+.3f}], mean dA {dA.mean():+.3f}, sd d {d.std(ddof=1):.3f}")
    say(f"  P-1 {'PASS' if p1 else 'FAIL'}; P-2 {'PASS' if p2 else 'FAIL'}; area-adjusted: beta {beta:+.3f}, residual mean {resid.mean():+.3f} [{ci_r[0]:+.3f}, {ci_r[1]:+.3f}] -> P-3 {'PASS' if p3 else 'FAIL'}")
    for arm in ("P1", "P2"):
        m = (ok["arm"] == arm).to_numpy()
        say(f"   arm {arm} (n={m.sum()}): mean d {d[m].mean():+.3f}, mean dA {dA[m].mean():+.3f}, mean dc(tracer) {ok['dc'].to_numpy()[m].mean():+.3f}")
    # sign split, as flip direction (base letter at idx)
    ok = ok.with_columns(flip_dir=pl.struct("base", "idx").map_elements(lambda s: s["base"][s["idx"]] + ">" + ("R" if s["base"][s["idx"]] == "L" else "L"), return_dtype=pl.String))
    for fd in ("L>R", "R>L"):
        m = (ok["flip_dir"] == fd).to_numpy()
        if m.sum():
            say(f"   flip {fd} (n={m.sum()}): mean d {d[m].mean():+.3f}, mean dA {dA[m].mean():+.3f}")
    fm = np.isfinite(ok["dc"].to_numpy()); dcv = ok["dc"].to_numpy()[fm]; d = d[fm]; dA = dA[fm]
    s_ = dcv + d
    g_ = float((dA * s_).sum() / (s_ * s_).sum())
    r2 = 1 - ((dA - g_ * s_) ** 2).sum() / ((dA - dA.mean()) ** 2).sum()
    p4 = bool(0.4 <= g_ <= 1.0 and r2 >= 0.5)
    say(f"  P-4 dA = g (dc + d): g {g_:.3f}, R2 {r2:.3f} -> {'PASS' if p4 else 'FAIL'}")
    res["4c"] = dict(n_mutants=pm.height, n_pairs=ok.height, retention=ok.height / pm.height, mean_d=md, ci=ci.tolist(), mean_dA=float(dA.mean()), beta=beta,
                     resid_mean=float(resid.mean()), resid_ci=ci_r.tolist(), g=g_, r2=float(r2), P1=p1, P2=p2, P3=p3, P4=p4)
else:
    # Writing outputs without the 4c section would silently clobber the committed full results.
    sys.exit("4c: dumps/p1_probe.done missing (dumps are gitignored; run run_p1.sh first). "
             "Refusing to overwrite results/stage4_analysis.{txt,json}.")
(R / "stage4_analysis.json").write_text(json.dumps(res, indent=1, default=float))
(R / "stage4_analysis.txt").write_text("\n".join(lines) + "\n")
