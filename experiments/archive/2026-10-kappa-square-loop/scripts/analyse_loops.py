# /// script
# dependencies = ["numpy", "polars", "scipy"]
# ///
"""H-loop analysis (P2, P3, C1, C2, P4, reliability, C3) per ../README.md, ../PLAN.md section 3 and the frozen decisions in
../NOTEBOOK.md (entry 2026-10-16 21:58). Run once on dumps/loops_cohort.csv (and dumps/loops_mutants.csv for C3).
usage (repo root): uv run experiments/archive/2026-10-kappa-square-loop/scripts/analyse_loops.py"""
from pathlib import Path
import json, subprocess, sys
import numpy as np, polars as pl
from scipy.stats import spearmanr

EXP = Path(__file__).resolve().parents[1]
ROOT = EXP.parents[2]
PAR = ROOT / "experiments/archive/2026-10-kappa-leadrun-fresh"
sys.path.insert(0, str(ROOT / "experiments/archive/2026-10-kappa-rule-space/scripts"))
from kcommon import census, per_rule, rule_means, icc_groups  # noqa: E402
from prefix_audit import basis  # noqa: E402

SEED, NB, LCAP, KW = 20261016, 2000, 6, 26
rng = np.random.default_rng(SEED)
sha = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
out = [f"# cmd: uv run experiments/archive/2026-10-kappa-square-loop/scripts/analyse_loops.py  git: {sha} (working tree may be dirty)  seed {SEED}  bootstraps {NB}  window k={KW}"]
res = {}


def P(s=""):
    out.append(s)


def lead_of(s):
    return len(s) - len(s.lstrip(s[0]))


def run_feats(loops: pl.DataFrame, k: int) -> pl.DataFrame:
    d = loops.filter(pl.col("k") == k)
    ll, lo = pl.col("loop_lead_b") + pl.col("loop_lead_i"), pl.col("loop_other_b") + pl.col("loop_other_i")
    inter = pl.col("steps") - pl.col("boundary_steps")
    return d.select(
        "rule",
        frac_all=(ll + lo) / pl.col("steps"),
        frac_lead=ll / pl.col("steps"),
        frac_other=lo / pl.col("steps"),
        M_int=(pl.col("loop_lead_i") + pl.col("loop_other_i")) / inter,
        M_int_lead=pl.col("loop_lead_i") / inter,
        M_int_other=pl.col("loop_other_i") / inter,
        M_bnd=(pl.col("loop_lead_b") + pl.col("loop_other_b")) / pl.col("boundary_steps"),
        ent_int=(pl.col("entry_lead_i") + pl.col("entry_other_i")) / inter,
        ent_all=(pl.col("entry_lead_b") + pl.col("entry_lead_i") + pl.col("entry_other_b") + pl.col("entry_other_i")) / pl.col("steps"),
        B=pl.col("boundary_steps") / pl.col("steps"),
        lb=pl.col("loop_lead_b"), li=pl.col("loop_lead_i"),
        ob=pl.col("loop_other_b"), oi=pl.col("loop_other_i"),
        bsteps=pl.col("boundary_steps"), isteps=inter, steps=pl.col("steps"),
        lead_share=ll / (ll + lo),
    )


# ---------------------------------------------------------------- load + identity vs parent probe
raw = pl.read_csv(PAR / "dumps/probe.csv")
def load_loops(p):
    """Sampler column k is the window index (steps in [2^k, 2^(k+1))); the probe CSV labels the same window k+1 = log2(t_end). Use the probe convention (the parent kappa is its k = 26)."""
    d = pl.read_csv(p)
    return d.with_columns(kw=pl.col("k"), k=(pl.col("t").cast(pl.Float64).log(2.0)).round().cast(pl.Int64))


loops = load_loops(EXP / "dumps/loops_cohort.csv")
a = raw.filter(pl.col("k") >= 21).select("rule", "k", "area", "perimeter", "new_cells", "boundary_steps", "escaped").sort("rule", "k")
b = loops.select("rule", "k", "area", "perimeter", "new_cells", "boundary_steps", "escaped").sort("rule", "k")
ident = a.height == b.height and a.equals(b)
assert set(loops["k"].unique().to_list()) == set(range(21, 28))
P(f"IDENTITY vs parent dumps/probe.csv (probe-CSV k = log2(t_end) >= 21): rows parent {a.height}, sampler {b.height}, all of area/perimeter/new_cells/boundary_steps/escaped equal: {ident}")
assert ident, "sampler disagrees with the parent's probe rows"
res["identity_rows"] = a.height

runs = per_rule(raw).with_columns(base=pl.col("rule").str.split("@").list.first())
runs = runs.join(raw.filter(pl.col("k") == 22).select("rule", lnA22=pl.col("area").log()), on="rule", how="left")
core = runs.filter(pl.col("alpha_w").is_between(.25, .42) & (pl.col("kappa") > 0))
fr = pl.read_csv(PAR / "results/fresh_rules.csv")
sampled = [l.strip() for l in (PAR / "results/rules.txt").read_text().split()]

# check we reproduce the parent's rule table
fresh = rule_means(core, 6)
st_par = set(fr.filter(pl.col("stationary"))["rule"])
st_here = set(fresh.filter(pl.col("g_k").abs() < .05)["base"])
assert st_par == st_here and len(st_par) == 176, (len(st_par), len(st_here))
chk = fresh.join(fr.select(base="rule", lnk_p="lnk"), on="base")
assert np.allclose(chk["lnk"], chk["lnk_p"]), "ln kappa differs from the parent's fresh_rules.csv"
P(f"parent table reproduced: {fresh.height} kept rules, {len(st_here)} stationary, ln kappa equal to fresh_rules.csv to float precision")


def per_rule_loops(core_runs: pl.DataFrame, lp: pl.DataFrame, k: int) -> pl.DataFrame:
    j = core_runs.select("rule", "base").join(run_feats(lp, k), on="rule", how="inner")
    assert j.height == core_runs.height, (j.height, core_runs.height)
    feats = ["frac_all", "frac_lead", "frac_other", "M_int", "M_int_lead", "M_int_other", "M_bnd", "ent_int", "ent_all", "B", "lead_share"]
    agg = j.group_by("base").agg(
        *[pl.col(f).mean() for f in feats],
        n_runs=pl.len(),
        sb=pl.col("bsteps").sum(), si=pl.col("isteps").sum(), lb=pl.col("lb").sum(), li=pl.col("li").sum(), ob=pl.col("ob").sum(), oi=pl.col("oi").sum(),
    )
    # pooled boundary-vs-interior ratio (P4), per rule
    return agg.with_columns(p4=((pl.col("lb") + pl.col("ob")) / pl.col("sb")) / ((pl.col("li") + pl.col("oi")) / pl.col("si")))


tab = per_rule_loops(core, loops, KW)
fresh_t = fresh.join(tab, on="base", how="left").join(fr.select(base="rule", lead="lead", stationary="stationary"), on="base", how="left")
stat = fresh_t.filter(pl.col("stationary")).sort("base")
tab_out = fresh_t.drop("lead").with_columns(lead=pl.col("base").map_elements(lead_of, return_dtype=pl.Int64)).sort("base")
hdr = f"# cmd: uv run experiments/archive/2026-10-kappa-square-loop/scripts/analyse_loops.py  git: {sha}  window k={KW}; per-rule means over core-band runs\n"
(EXP / "results/loops_per_rule.csv").write_text(hdr + tab_out.write_csv())

# ---------------------------------------------------------------- retention (by lead)
kept, stset = set(fresh["base"]), set(stat["base"])
ret = {}
for k in range(1, 7):
    rs = [r for r in sampled if lead_of(r) == k]
    ret[k] = dict(n=len(rs), kept=sum(r in kept for r in rs), stat=sum(r in stset for r in rs))
RET = "retention (of 50 sampled per lead): " + "; ".join(f"L{k}: kept {v['kept']}, stationary {v['stat']}" for k, v in ret.items())
res["retention"] = ret
P(RET)

# ---------------------------------------------------------------- design
cen = census().filter((pl.col("kappa") > 0) & pl.col("lnA22").is_not_null()).sort("rule")
cen = cen.filter(pl.col("g_k").abs() < .05)
y = stat["lnk"].to_numpy()
lnA = stat["lnA22"].to_numpy()
lead = np.array([min(lead_of(s), LCAP) for s in stat["base"]], float)
_, Z = basis(cen["lnA22"].to_numpy(), lnA, True)
_, Zf = basis(lnA, lnA, True)
n = len(y)
P(f"stationary fresh rules n={n}; per lead " + ", ".join(f"{k}:{int((lead == k).sum())}" for k in range(1, 7)))
IDX = rng.integers(0, n, (NB, n))


def zs(v):
    v = np.asarray(v, float)
    return (v - v.mean()) / v.std()


def ols(ix, feats, spl=Z):
    A = np.column_stack([np.ones(len(ix)), spl[ix], lead[ix]] + [f[ix] for f in feats])
    return np.linalg.lstsq(A, y[ix], rcond=None)[0]


def mediation(feats, mask=None, spl=Z, boots=True):
    """b0 (lead coefficient without mediator), b1 (with), ratio, g. Bootstrap over rules within the mask."""
    base_ix = np.arange(n) if mask is None else np.where(mask)[0]
    m = len(base_ix)
    c0, c1 = ols(base_ix, [], spl), ols(base_ix, feats, spl)
    b0, b1 = c0[spl.shape[1] + 1], c1[spl.shape[1] + 1]
    g = c1[spl.shape[1] + 2:]
    r = dict(b0=float(b0), b1=float(b1), ratio=float(b1 / b0), g=[float(v) for v in g], n=int(m))
    if boots:
        rb = np.random.default_rng(SEED + 7)
        bi = base_ix[rb.integers(0, m, (NB, m))]
        rat, gg = [], []
        for ix in bi:
            c0b, c1b = ols(ix, [], spl), ols(ix, feats, spl)
            rat.append(c1b[spl.shape[1] + 1] / c0b[spl.shape[1] + 1]); gg.append(c1b[spl.shape[1] + 2])
        r["ratio_ci"] = [float(q) for q in np.quantile(rat, [.025, .975])]
        r["g_ci"] = [float(q) for q in np.quantile(gg, [.025, .975])]
    return r


def fmt_med(name, r):
    s = f"  {name:34s} n={r['n']:3d} b0={r['b0']:+.3f} b1={r['b1']:+.3f} ratio b1/b0={r['ratio']:+.3f}"
    if "ratio_ci" in r:
        s += f" [{r['ratio_ci'][0]:+.3f},{r['ratio_ci'][1]:+.3f}]  g(per SD)={r['g'][0]:+.3f} [{r['g_ci'][0]:+.3f},{r['g_ci'][1]:+.3f}]"
    return s


col = lambda name: stat[name].to_numpy()  # noqa: E731
M = zs(col("M_int"))
lead14 = lead <= 4

# ---------------------------------------------------------------- P2
P(); P("=== P2: loop-step fraction (all loop steps / steps, k=26) by lead; retention beside it ===")
P("lead  n  kept/50 stat/50  frac_all   frac_lead_colour  M_int(interior rate)  lead_colour_share_of_loop_steps  mean_resid_lnk(vs spline-only fit)")
ra = np.linalg.lstsq(np.column_stack([np.ones(n), Z]), y, rcond=None)[0]
resid = y - np.column_stack([np.ones(n), Z]) @ ra
mono_vals = []
p2tab = {}
for k in range(1, 7):
    m = lead == k
    row = dict(n=int(m.sum()), frac_all=float(col("frac_all")[m].mean()), frac_lead=float(col("frac_lead")[m].mean()), M_int=float(col("M_int")[m].mean()),
               lead_share=float(col("lead_share")[m].mean()), resid=float(resid[m].mean()))
    p2tab[k] = row; mono_vals.append(row["frac_all"])
    P(f"{k:3d} {row['n']:3d}   {ret[k]['kept']:3d}   {ret[k]['stat']:3d}   {row['frac_all']:.5f}   {row['frac_lead']:.5f}   {row['M_int']:.5f}   {row['lead_share']:.3f}   {row['resid']:+.3f}")
monotone = all(np.diff(mono_vals) > 0)
cuts = np.quantile(lnA, [1 / 3, 2 / 3]); ter = np.digitize(lnA, cuts)
sp, spci = [], []
for t in range(3):
    ix = np.where(ter == t)[0]
    r = spearmanr(lead[ix], col("frac_all")[ix]).statistic
    bs = [spearmanr(lead[ix][j], col("frac_all")[ix][j]).statistic for j in (np.random.default_rng(SEED + 11 + t).integers(0, len(ix), (NB, len(ix))))]
    sp.append(float(r)); spci.append([float(q) for q in np.nanquantile(bs, [.025, .975])])
    P(f"  lnA22 tertile {t + 1}: n={len(ix)}, Spearman(frac_all, lead) = {r:+.3f} CI [{spci[-1][0]:+.3f},{spci[-1][1]:+.3f}]")
r_all = spearmanr(lead, col("frac_all")).statistic
P(f"  pooled Spearman(frac_all, lead) = {r_all:+.3f}; strictly monotone mean over leads 1..6: {monotone}")
# leads 1-4 monotone as well (selection)
p2_hold = bool(monotone and all(s > 0.5 for s in sp))
P(f"P2 {'HELD' if p2_hold else 'FAILED'} (monotone: {monotone}; tertile Spearman > 0.5 in all: {all(s > 0.5 for s in sp)})")
P("  secondary windows (frac_all by lead, mean over stationary rules):")
sec = {}
for kk in (22, 24):
    tk = per_rule_loops(core, loops, kk).join(stat.select("base"), on="base").sort("base")
    v = [float(tk["frac_all"].to_numpy()[lead == k].mean()) for k in range(1, 7)]
    sec[kk] = v
    P(f"    k={kk}: " + " ".join(f"{x:.5f}" for x in v) + f"   monotone {all(np.diff(v) > 0)}")
res["P2"] = dict(by_lead=p2tab, monotone=bool(monotone), tertile_spearman=sp, tertile_ci=spci, pooled_spearman=float(r_all), secondary_windows=sec, held=p2_hold)

# ---------------------------------------------------------------- reliability
P(); P("=== Reliability of the deciding mediator M_int (frozen rule: ICC(1) across core-band runs < 0.5 => P3/C1/C2 uninformative) ===")
j = core.select("rule", "base").join(run_feats(loops, KW), on="rule").filter(pl.col("base").is_in(list(stset)))
groups = [g["M_int"].to_numpy() for _, g in j.group_by("base")]
icc, sw, sb, ng = icc_groups(groups)
mbar = float(np.mean([len(g) for g in groups if len(g) >= 6]))
icc_mean = mbar * icc / (1 + (mbar - 1) * icc)
P(f"  M_int: ICC(1) single run = {icc:.3f} (between-rule sd {sb:.5f}, within-rule (between-seed) sd {sw:.5f}, {ng} rules, mean runs/rule {mbar:.2f}); reliability of the rule mean (Spearman-Brown) = {icc_mean:.3f}")
rel_ok = icc >= 0.5
for nm in ("frac_all", "M_int_lead", "M_int_other", "ent_int"):
    jj = j.select("base", nm)
    gi = icc_groups([g[nm].to_numpy() for _, g in jj.group_by("base")])
    P(f"  {nm}: ICC(1) = {gi[0]:.3f}")
    res.setdefault("icc_other", {})[nm] = float(gi[0])
P(f"  reliability rule: {'ICC >= 0.5, mediation test is informative' if rel_ok else 'ICC < 0.5: mediation tests UNINFORMATIVE (not a null)'}")
res["reliability"] = dict(icc=float(icc), sw=float(sw), sb=float(sb), icc_mean=float(icc_mean), ok=bool(rel_ok))

# ---------------------------------------------------------------- P3 (deciding = M_int, interior-only)
P(); P("=== P3: ln kappa ~ spline(ln A22) + b*min(lead,6) [+ g*mediator]; census-quantile spline knots, OLS on the stationary fresh rules ===")
P(f"  {RET}")
P("  Pass (frozen): b1/b0 <= 0.5 and ratio CI upper < 0.8 and g > 0 with CI excluding 0. DECIDING mediator = M_int (interior-only loop-step rate). Others are accounting/robustness.")
variants = {
    "M_int (DECIDING)": [M],
    "log M_int": [zs(np.log(col("M_int")))],
    "rank M_int": [zs(np.argsort(np.argsort(col("M_int"))))],
    "ent_int (interior entry rate)": [zs(col("ent_int"))],
    "M_int, fresh-quantile knots": [M],
    "ACCOUNTING all-loop frac_all": [zs(col("frac_all"))],
    "ACCOUNTING boundary loop rate M_bnd": [zs(col("M_bnd"))],
    "ACCOUNTING all-loop entry rate": [zs(col("ent_all"))],
}
p3 = {}
for nm, f in variants.items():
    spl = Zf if "fresh-quantile" in nm else Z
    r_all_ = mediation(f, None, spl); r_14 = mediation(f, lead14, spl)
    p3[nm] = dict(all=r_all_, l14=r_14)
    P(fmt_med(nm + " | all leads", r_all_)); P(fmt_med(nm + " | leads 1-4", r_14))
d = p3["M_int (DECIDING)"]
pass_main = bool(d["all"]["ratio"] <= 0.5 and d["all"]["ratio_ci"][1] < 0.8 and d["all"]["g_ci"][0] > 0)
pass_14 = bool(d["l14"]["ratio"] <= 0.5)
corrB = float(np.corrcoef(col("M_int"), col("B"))[0, 1])
P(f"  corr(M_int, B/S) across stationary rules = {corrB:+.3f}; corr(M_int, lead) = {np.corrcoef(M, lead)[0, 1]:+.3f}; corr(M_int, ln A22) = {np.corrcoef(M, lnA)[0, 1]:+.3f}")
if not rel_ok:
    verdict = "UNINFORMATIVE (reliability rule)"
elif not p2_hold:
    verdict = "not evaluated as support (P2 failed)"
else:
    verdict = ("HELD" if pass_main else "FAILED") + ((", robust to leads 1-4" if pass_14 else ", NOT robust to leads 1-4 (point ratio > 0.5)") if pass_main else "")
P(f"P3 verdict: {verdict}  (main pass {pass_main}; leads 1-4 point ratio {d['l14']['ratio']:+.3f})")
res["P3"] = dict(variants=p3, corr_M_B=corrB, pass_main=pass_main, pass_l14=pass_14, verdict=verdict)

# ---------------------------------------------------------------- C1
P(); P("=== C1 (specificity): mediation fraction f = 1 - b1/b0 for interior lead-colour loops vs interior other loops ===")
c1 = {}
for nm, f in (("lead-colour interior rate", [zs(col("M_int_lead"))]), ("other-loop interior rate", [zs(col("M_int_other"))]),
              ("both jointly", [zs(col("M_int_lead")), zs(col("M_int_other"))])):
    c1[nm] = dict(all=mediation(f, None), l14=mediation(f, lead14))
    P(fmt_med(nm + " | all", c1[nm]["all"])); P(fmt_med(nm + " | leads 1-4", c1[nm]["l14"]))
fl, fo = 1 - c1["lead-colour interior rate"]["all"]["ratio"], 1 - c1["other-loop interior rate"]["all"]["ratio"]
c1_hold = bool(fl > 0 and fo < 0.5 * fl)
P(f"  f_lead = {fl:+.3f}, f_other = {fo:+.3f}; C1 {'HELD' if c1_hold else 'FAILED'} (needs f_lead > 0 and f_other < 0.5 f_lead; informative only if reliability ok: {rel_ok})")
res["C1"] = dict(detail=c1, f_lead=float(fl), f_other=float(fo), held=c1_hold)

# ---------------------------------------------------------------- C2
P(); P("=== C2 (identity caveat) ===")
c2_hold = pass_main
P(f"  C2 holds iff the interior-only M_int passes P3: {c2_hold}. Boundary-loop mediator (accounting) ratio = {p3['ACCOUNTING boundary loop rate M_bnd']['all']['ratio']:+.3f}; "
  f"all-loop accounting ratio = {p3['ACCOUNTING all-loop frac_all']['all']['ratio']:+.3f}; interior entry-rate ratio = {p3['ent_int (interior entry rate)']['all']['ratio']:+.3f}")
res["C2"] = dict(held=c2_hold)

# ---------------------------------------------------------------- P4
P(); P("=== P4: P(loop | boundary step) / P(loop | interior step), k=26, per rule (pooled over its core runs), stationary rules ===")
p4 = col("p4")
rb = np.random.default_rng(SEED + 13).integers(0, n, (NB, n))
med = float(np.median(p4)); mci = [float(q) for q in np.quantile(np.median(p4[rb], axis=1), [.025, .975])]
P(f"  median ratio {med:.3f} CI [{mci[0]:.3f},{mci[1]:.3f}]; quartiles {np.quantile(p4, [.25, .75]).round(3).tolist()}; by lead median: " + ", ".join(f"{k}:{np.median(p4[lead == k]):.2f}" for k in range(1, 7)))
p4_hold = med >= 2.0
P(f"  P4 {'HELD' if p4_hold else 'FAILED'} (median >= 2). Partly accounting by construction (the loop step is classed by its start cell).")
res["P4"] = dict(median=med, ci=mci, held=bool(p4_hold))

# ---------------------------------------------------------------- C3
mp = EXP / "dumps/loops_mutants.csv"
P(); P("=== C3 (mutation link) ===")
if mp.exists() and (PAR / "dumps/mutants.csv").exists():
    mraw = pl.read_csv(PAR / "dumps/mutants.csv")
    mruns = per_rule(mraw).with_columns(base=pl.col("rule").str.split("@").list.first())
    mcore = mruns.filter(pl.col("alpha_w").is_between(.25, .42) & (pl.col("kappa") > 0))
    ml = load_loops(mp)
    mt = per_rule_loops(mcore, ml, KW).select(mutant="base", M_mut="M_int", F_mut="frac_all")
    bt = tab.select(base="base", M_base="M_int", F_base="frac_all")
    pairs = pl.read_csv(PAR / "results/mutant_pairs.csv").filter(pl.col("kept") & pl.col("arm").is_in(["E", "S"]))
    pairs = pairs.join(mt, on="mutant", how="inner").join(bt, on="base", how="inner").with_columns(dM=pl.col("M_mut") - pl.col("M_base"), dF=pl.col("F_mut") - pl.col("F_base"))
    pairs.write_csv(EXP / "results/c3_pairs.csv")
    dd, dm, dfr = pairs["d"].to_numpy(), pairs["dM"].to_numpy(), pairs["dF"].to_numpy()
    r3 = float(spearmanr(dm, dd).statistic); r3f = float(spearmanr(dfr, dd).statistic)
    bsr = [spearmanr(dm[i], dd[i]).statistic for i in np.random.default_rng(SEED + 17).integers(0, len(dd), (NB, len(dd)))]
    ci3 = [float(q) for q in np.nanquantile(bsr, [.025, .975])]
    P(f"  pairs (arms E+S, both kept): n={len(dd)} (E {int((pairs['arm'] == 'E').sum())}, S {int((pairs['arm'] == 'S').sum())}); Spearman(d M_int, d ln kappa) = {r3:+.3f} CI [{ci3[0]:+.3f},{ci3[1]:+.3f}]; accounting Spearman(d frac_all, d) = {r3f:+.3f}")
    for arm in ("E", "S"):
        m = (pairs["arm"] == arm).to_numpy()
        P(f"    arm {arm}: n={int(m.sum())}, mean dM_int = {dm[m].mean():+.5f}, mean d ln kappa = {dd[m].mean():+.3f}, Spearman = {spearmanr(dm[m], dd[m]).statistic:+.3f}")
    c3_hold = r3 > 0.3
    P(f"  C3 {'HELD' if c3_hold else 'FAILED'} (Spearman > 0.3; not powered)")
    res["C3"] = dict(n=int(len(dd)), spearman=r3, ci=ci3, spearman_all_loop=r3f, held=bool(c3_hold))
else:
    P("  loops_mutants.csv not present: C3 not evaluated.")

(EXP / "results/analysis.txt").write_text("\n".join(out) + "\n")
(EXP / "results/analysis.json").write_text(json.dumps(res, indent=1, default=float))
print("\n".join(out))
