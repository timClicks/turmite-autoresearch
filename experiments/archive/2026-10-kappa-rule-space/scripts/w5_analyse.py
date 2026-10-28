# /// script
# dependencies = ["polars", "numpy", "scipy"]
# ///
"""W5 analysis (README, log: 'W5: implementation addendum'; estimator frozen there).
Reads dumps/w5_bulk.csv (raw tallies from examples/kappa_rs_bulk.rs), writes results/w5_obs.csv (derived per-run observables),
results/w5_rules.csv (pool rule table) and results/w5_stats.txt.
usage (repo root): uv run experiments/archive/2026-10-kappa-rule-space/scripts/w5_analyse.py"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import numpy as np, polars as pl
from scipy.stats import spearmanr
from kcommon import *

OBS = ["I_turn", "msd64", "msd512", "msd4096", "msd_exp", "head64", "ret32", "ret_tail", "reuse64", "ent_pi", "mean_col"]
PRIMARY = ["I_turn", "msd512", "ret32"]
MIN_BULK, MIN_PAIRS, GROWTH_MAX = 1000, 1000, 1.5
out = []
P = out.append

# ---------------------------------------------------------------- per-run observables
raw = pl.read_csv(EXP / "dumps" / "w5_bulk.csv", infer_schema_length=0)
rows = []
for r in raw.iter_rows(named=True):
    d = dict(spec=r["spec"], status=r["status"])
    if r["status"] == "ok":
        n, ncol = int(r["ncol"]), int(r["ncol"])
        vec = lambda k: np.array([int(v) for v in r[k].split(":")], dtype=np.int64)
        nb = int(r["n_bulk"]); nrec = int(r["n_rec"])
        d.update(ncol=ncol, t_star=int(r["t_star"]), area0=int(r["area0"]), area_end=int(r["area_end"]), growth=int(r["area_end"]) / int(r["area0"]),
                 mask_cells=int(r["mask_cells"]), n_bulk=nb, bulk_frac=nb / nrec)
        ts, tn = vec("turn_s"), vec("turn_n")
        ms, mn = vec("msd_sum"), vec("msd_n")
        d.update(msd_n64=int(mn[0]), msd_n512=int(mn[1]), msd_n4096=int(mn[2]), head_n=int(r["head_n"]))
        if nb >= MIN_BULK:
            mean = int(r["sum_s"]) / nb; var = int(r["sum_s2"]) / nb - mean ** 2
            ok = tn > 0
            C = np.where(ok, (ts / np.maximum(tn, 1) - mean ** 2) / var, np.nan) if var > 0 else np.full(len(ts), np.nan)
            d["I_turn"] = float(C.sum()) if ok.all() and var > 0 else np.nan
            dh = vec("dh_hist"); d["uturn_frac"] = dh[2] / nb
            for a, L in enumerate((64, 512, 4096)):
                d[f"msd{L}"] = ms[a] / mn[a] / L if mn[a] >= MIN_PAIRS else np.nan
            d["msd_exp"] = float(np.log2((ms[2] / mn[2]) / (ms[0] / mn[0])) / 6) if mn[2] >= MIN_PAIRS and mn[0] >= MIN_PAIRS else np.nan
            d["head64"] = int(r["head_sum"]) / int(r["head_n"]) if int(r["head_n"]) >= MIN_PAIRS else np.nan
            d["ret32"] = int(r["ret_hit"]) / int(r["ret_elig"]) if int(r["ret_elig"]) >= MIN_PAIRS else np.nan
            gh = vec("gap_hist"); bins = np.arange(6, 12); cnt = gh[bins].astype(float)
            d["ret_tail"] = float(np.polyfit(np.log(1.5 * 2.0 ** bins), np.log(cnt / 2.0 ** bins), 1)[0]) if (cnt > 0).all() else np.nan
            d["reuse64"] = int(r["n_reuse"]) / nb
            cs, ch = vec("col_steps"), vec("core_hist")
            if ncol > 1 and ch.sum() > 0:
                pi = ch / ch.sum(); pi = pi[pi > 0]
                d["ent_pi"] = float(-(pi * np.log(pi)).sum() / np.log(ncol))
                d["mean_col"] = float((np.arange(ncol) * cs).sum() / nb / (ncol - 1))
        # rule length (ants only)
    rows.append(d)
runs = pl.DataFrame(rows, infer_schema_length=None)
runs = runs.with_columns(
    kind=pl.when(pl.col("spec").str.contains("@")).then(pl.lit("pool_patched"))
    .when(pl.col("spec").str.starts_with("rotor:")).then(pl.lit("rotor"))
    .when(pl.col("spec").str.starts_with("pw:")).then(pl.lit("pw"))
    .when(pl.col("spec").str.starts_with("rw:")).then(pl.lit("rw")).otherwise(pl.lit("blank")),
    rule=pl.col("spec").str.split("@").list.first())
for c in OBS + ["growth", "t_star", "bulk_frac"]:
    if c not in runs.columns: runs = runs.with_columns(pl.lit(None, dtype=pl.Float64).alias(c))
runs.write_csv(EXP / "results" / "w5_obs.csv", float_precision=8)

P(header("uv run experiments/archive/2026-10-kappa-rule-space/scripts/w5_analyse.py").rstrip())
P("specs %d; status counts by kind: " % runs.height + str({k: dict(sorted(g["status"].value_counts().iter_rows())) for (k,), g in sorted(runs.group_by("kind"), key=lambda kg: kg[0])}))
ant = runs.filter((pl.col("status") == "ok") & pl.col("kind").is_in(["pool_patched", "blank"]))
P(f"ant runs ok: {ant.height}; growth factor area_end/area0: median {ant['growth'].median():.3f}, 90th pct {ant['growth'].quantile(0.9):.3f}, share > {GROWTH_MAX}: {(ant['growth'] > GROWTH_MAX).mean():.3f}; "
  f"t*: median 2^{np.log2(ant['t_star'].median()):.2f}; bulk fraction of recorded steps: median {ant['bulk_frac'].median():.3f}, 10th pct {ant['bulk_frac'].quantile(0.1):.3f}")
P("usable pair counts at lag 4096 (msd_n4096): " + f"median {ant['msd_n4096'].median():.0f}, share of runs with < {MIN_PAIRS}: {(ant['msd_n4096'] < MIN_PAIRS).mean():.3f} (msd4096 / msd_exp are NaN there)")

# ---------------------------------------------------------------- targets
files = ["b2_probe.csv", "item21_probe.csv", "patched.csv"]
pr = pool_runs(files)  # core band, kappa>0 at the end of the fit (k=26), per run, with base rule
k25 = pl.concat([pl.read_csv(legacy(f)).filter(pl.col("k") == 25) for f in files]).select(
    "rule", kap25=(pl.col("boundary_steps") / (pl.col("t") // 2)) / (pl.col("perimeter") / pl.col("area")), esc25="escaped")
pr = pr.join(k25, on="rule", how="left").filter((pl.col("kap25") > 0) & (~pl.col("esc25").fill_null(True)))
tgt25 = pr.group_by("base").agg(n25=pl.len(), lnk25=pl.col("kap25").log().mean(), c25=pl.col("c").mean()).filter(pl.col("n25") >= 6)
pool = pl.read_csv(EXP / "results" / "rules_pool.csv").join(tgt25, on="base", how="inner").sort("base").with_columns(
    n=pl.col("base").str.len_chars(), stat=pl.col("g_k").abs() < 0.05)
P(f"\npool-192 rules: {192}; with >= 6 runs having a k=25 window: {pool.height}; stationary {int(pool['stat'].sum())}; "
  f"corr(lnk25, lnk26-mean) {np.corrcoef(pool['lnk25'], pool['lnk'])[0,1]:.3f}; sd lnk25 {pool['lnk25'].std():.3f}")

cen = pl.read_csv(EXP / "results" / "rules_census.csv").filter(~pl.col("in_pool") & (pl.col("kappa") > 0)).with_columns(
    lnk=pl.col("kappa").log(), stat=pl.col("g_k").abs() < 0.05, n=pl.col("rule").str.len_chars())

def usable(df):
    return df.filter((pl.col("status") == "ok") & (pl.col("growth") <= GROWTH_MAX) & (pl.col("n_bulk") >= MIN_BULK))

def usable_nogrowth(df):
    return df.filter((pl.col("status") == "ok") & (pl.col("n_bulk") >= MIN_BULK))

def pool_obs(use):
    pp = use(runs.filter(pl.col("kind") == "pool_patched"))
    agg = pp.group_by("rule").agg(n_seeds=pl.len(), t_star=pl.col("t_star").log().mean(), **{o: pl.col(o).mean() for o in OBS})
    return agg.filter(pl.col("n_seeds") >= 4).rename({"rule": "base", "t_star": "lnt_star"}).sort("base")

def disc_obs(use):
    return use(runs.filter(pl.col("kind") == "blank")).rename({"rule": "base"}).with_columns(lnt_star=pl.col("t_star").log()).sort("base")

# ---------------------------------------------------------------- estimator (frozen in the addendum)
def zfit(x_tr):
    lo, hi = np.nanpercentile(x_tr, [1, 99]); xc = np.clip(x_tr, lo, hi)
    return lo, hi, xc.mean(), xc.std() + 1e-12

def zapply(x, f):
    lo, hi, m, s = f; return (np.clip(x, lo, hi) - m) / s

def fit_gain(trA, trO, trY, teA, teO, teY):
    """Returns (gain, r2_A, r2_AO, coef, pred_A, pred_AO, z_te) with R^2 strict against the training mean."""
    f = zfit(trO); z_tr, z_te = zapply(trO, f), zapply(teO, f)
    XA = np.column_stack([np.ones_like(trA), trA]); XAO = np.column_stack([XA, z_tr])
    bA = np.linalg.lstsq(XA, trY, rcond=None)[0]; bAO = np.linalg.lstsq(XAO, trY, rcond=None)[0]
    pA = np.column_stack([np.ones_like(teA), teA]) @ bA
    pAO = np.column_stack([np.ones_like(teA), teA, z_te]) @ bAO
    den = ((teY - trY.mean()) ** 2).sum()
    rA, rAO = 1 - ((teY - pA) ** 2).sum() / den, 1 - ((teY - pAO) ** 2).sum() / den
    return rAO - rA, rA, rAO, bAO, pA, pAO, z_te

def cohort(dsc, pol, stat_only):
    if stat_only:
        dsc, pol = dsc.filter(pl.col("stat")), pol.filter(pl.col("stat"))
    return dsc, pol

def evaluate(dsc, pol, ycol_d, ycol_p, label, seedoff=0, boot=True):
    """Gain for each declared observable on one (train, test) cohort. Returns dict obs -> info."""
    res = {}
    rg = rng(41 + seedoff)
    for o in OBS:
        d = dsc.filter(pl.col(o).is_not_nan() & pl.col(o).is_not_null()); p = pol.filter(pl.col(o).is_not_nan() & pl.col(o).is_not_null())
        if d.height < 50 or p.height < 30:
            res[o] = None; continue
        g, rA, rAO, b, pA, pAO, zte = fit_gain(d["lnA22"].to_numpy(), d[o].to_numpy(), d[ycol_d].to_numpy(), p["lnA22"].to_numpy(), p[o].to_numpy(), p[ycol_p].to_numpy())
        y = p[ycol_p].to_numpy(); den = ((y - d[ycol_d].mean()) ** 2).sum()
        lo = hi = np.nan
        if boot:
            idx = rg.integers(0, len(y), size=(2000, len(y)))
            ybs = y[idx]; dens = ((ybs - d[ycol_d].mean()) ** 2).sum(1)
            gains = (((ybs - pA[idx]) ** 2).sum(1) - ((ybs - pAO[idx]) ** 2).sum(1)) / dens
            lo, hi = np.percentile(gains, [2.5, 97.5])
        res[o] = dict(gain=g, rA=rA, rAO=rAO, lo=lo, hi=hi, nd=d.height, nt=p.height, coef=b[2], base=pA, pAO=pAO, zte=zte, y=y, ids=p["base"].to_list(),
                      trmean=d[ycol_d].mean(), nn=p["n"].to_numpy(), bcoef=b)
    return res

def fmt(res, obs=OBS):
    s = []
    for o in obs:
        r = res.get(o)
        s.append(f"  {o:9s} " + ("unusable (too few rules)" if r is None else
                 f"gain {r['gain']:+.3f} [{r['lo']:+.3f}, {r['hi']:+.3f}]  R2(A) {r['rA']:.3f} -> R2(A+obs) {r['rAO']:.3f}  coef {r['coef']:+.3f}  train {r['nd']}, test {r['nt']}"))
    return "\n".join(s)

def perm_tests(res, nperm=10000):
    """Max-gain over OBS under (a) registered: pool targets permuted within n; (b) stricter: observable permuted within n."""
    ok = [o for o in OBS if res.get(o)]
    out_ = {}
    rgen = rng(43)
    for label in ("target", "obs"):
        mx = np.zeros(nperm); mx_pri = np.zeros(nperm)
        for k, o in enumerate(ok):
            r = res[o]; y, nn = r["y"], r["nn"]
            den = ((y - r["trmean"]) ** 2).sum()
            grp = [np.where(nn == v)[0] for v in np.unique(nn)]
            perms = np.tile(np.arange(len(y)), (nperm, 1))
            g2 = rng(43 + 1000 * k + (label == "obs"))
            for gi in grp:
                for i in range(nperm):
                    perms[i, gi] = gi[g2.permutation(len(gi))]
            if label == "target":
                yp = y[perms]; gains = (((yp - r["base"]) ** 2).sum(1) - ((yp - r["pAO"]) ** 2).sum(1)) / ((yp - r["trmean"]) ** 2).sum(1)
            else:
                zp = r["zte"][perms]; pp_ = r["base"] + r["coef"] * zp
                gains = (((y - r["base"]) ** 2).sum() - ((y - pp_) ** 2).sum(1)) / den
            mx = np.maximum(mx, gains) if k else gains
            if o in PRIMARY: mx_pri = np.maximum(mx_pri, gains) if np.any(mx_pri) or o != PRIMARY[0] else gains
        out_[label] = (mx, mx_pri)
    return out_

def run_cohort(name, dsc, pol, ycol_d, ycol_p, perm=True, boot=True):
    res = evaluate(dsc, pol, ycol_d, ycol_p, name, boot=boot)
    P(f"\n--- {name}: test = pool rule means (ln kappa k=25), train = census-minus-pool blank-board single runs ---\n" + fmt(res))
    best = max((o for o in OBS if res.get(o)), key=lambda o: res[o]["gain"])
    P(f"  best declared observable: {best} gain {res[best]['gain']:+.3f}; best primary: {max((o for o in PRIMARY if res.get(o)), key=lambda o: res[o]['gain'])}")
    if perm:
        pt = perm_tests(res)
        for lab, desc in (("target", "registered: pool targets permuted within n"), ("obs", "stricter, exploratory: observable permuted within n")):
            mx, mxp = pt[lab]
            gobs = max(res[o]["gain"] for o in OBS if res.get(o)); gpri = max(res[o]["gain"] for o in PRIMARY if res.get(o))
            P(f"  permutation null of max gain over declared observables ({desc}; 10^4): obs max {gobs:+.3f}, null median {np.median(mx):+.3f}, 95th pct {np.percentile(mx, 95):+.3f}, p = {(np.sum(mx >= gobs) + 1) / (len(mx) + 1):.4f}")
        P(f"  primary-three only, registered null: obs max {gpri:+.3f}, p = {(np.sum(pt['target'][1] >= gpri) + 1) / (len(pt['target'][1]) + 1):.4f}")
    return res

# ---------------------------------------------------------------- cohorts
pool_o = pool_obs(usable).join(pool, on="base", how="inner").sort("base")
disc_o = disc_obs(usable).join(cen.select(base="rule", n="n", lnk="lnk", stat="stat", lnA22="lnA22", c="c"), on="base", how="inner").sort("base")
P(f"\ndiscovery rules with usable blank run: {disc_o.height} of {cen.height} (stationary {int(disc_o['stat'].sum())}); "
  f"pool rules with >= 4 usable patched seeds: {pool_o.height} of {pool.height} (stationary {int(pool_o['stat'].sum())})")
P(f"growth-factor exclusion (> {GROWTH_MAX}) removed {1 - usable(runs.filter(pl.col('kind')=='pool_patched')).height / max(1, usable_nogrowth(runs.filter(pl.col('kind')=='pool_patched')).height):.3f} of otherwise-usable pool runs; "
  f"mean ln kappa of pool rules kept vs dropped by the 4-seed rule: {pool_o['lnk25'].mean():+.3f} vs {pool.filter(~pl.col('base').is_in(pool_o['base']))['lnk25'].mean():+.3f}")
for o in OBS:
    P(f"  usable fraction {o:9s} pool-runs {(usable(runs.filter(pl.col('kind')=='pool_patched'))[o].is_not_nan() & usable(runs.filter(pl.col('kind')=='pool_patched'))[o].is_not_null()).mean():.3f}  blank-runs {(disc_o[o].is_not_nan() & disc_o[o].is_not_null()).mean():.3f}")

# ---------------------------------------------------------------- P5.3 reproducibility
P("\n=== P5.3: ICC across patched seeds on the pool (groups with >= 4 usable seeds; unbalanced one-way ICC) ===")
pp = usable(runs.filter(pl.col("kind") == "pool_patched"))
iccs = {}
for o in OBS:
    groups = [g[o].drop_nulls().drop_nans().to_numpy() for _, g in pp.group_by("rule")]
    groups = [g for g in groups if len(g) >= 4]
    if len(groups) < 30: P(f"  {o:9s} too few groups ({len(groups)})"); continue
    sw2 = np.mean([g.var(ddof=1) for g in groups]); means = np.array([g.mean() for g in groups]); m = np.mean([len(g) for g in groups])
    sb2 = max(means.var(ddof=1) - sw2 / m, 0.0); iccs[o] = sb2 / (sb2 + sw2)
    P(f"  {o:9s} ICC {iccs[o]:.3f}  (groups {len(groups)}, mean seeds {m:.2f})")
hi_icc = [o for o in iccs if iccs[o] >= 0.7]
P(f"P5.3 (ICC >= 0.7): primary three {[f'{o}:{iccs.get(o, float('nan')):.2f}' for o in PRIMARY]} -> {'HELD' if all(iccs.get(o, 0) >= 0.7 for o in PRIMARY) else 'FAILED for at least one'}; observables >= 0.7: {hi_icc}")

# patched vs blank
bl = disc_obs(usable_nogrowth).select("base", **{f"{o}_b": o for o in OBS})  # discovery blank runs are census-only; pool blank runs are kind == blank with in-pool rules
poolblank = usable(runs.filter((pl.col("kind") == "blank") & pl.col("rule").is_in(pool["base"]))).select(base="rule", **{f"{o}_b": o for o in OBS})
cmp = pool_o.join(poolblank, on="base", how="inner").sort("base")
P(f"\npatched-vs-blank agreement on pool rules ({cmp.height} rules; Spearman of 6-seed patched mean vs the blank-board run):")
P("  " + "; ".join(f"{o} {spearmanr(cmp[o], cmp[o+'_b'], nan_policy='omit').statistic:+.2f}" for o in OBS))

# ---------------------------------------------------------------- P5.1 primary: stationary; all-rules beside it
P("\n=== P5.1 (frozen estimator) ===")
dS, pS = cohort(disc_o, pool_o, True); dA, pA_ = cohort(disc_o, pool_o, False)
resS = run_cohort("PRIMARY stationary cohort", dS, pS, "lnk", "lnk25")
resA = run_cohort("all-rules cohort", dA, pA_, "lnk", "lnk25")
best = max(r["gain"] for r in resS.values() if r)
P(f"\nP5.1 verdict rule (frozen): max declared gain >= 0.15 AND registered-permutation p <= 0.05 on the stationary cohort -> max {best:+.3f}")

# ---------------------------------------------------------------- added after review of the first result (exploratory unless stated)
P("\n=== added after review (exploratory): redundancy, concentration of the gain, section-4.4 positive control, dropped rules ===")
for lab, df in (("pool stationary rule means", pS), ("discovery stationary blank runs", dS)):
    trio = ["msd64", "ret32", "reuse64"]
    P(f"pairwise Spearman among msd64, ret32, reuse64 ({lab}, n={df.height}): " + "; ".join(
        f"{a}-{b} {spearmanr(df[a], df[b], nan_policy='omit').statistic:+.2f}" for i, a in enumerate(trio) for b in trio[i + 1:]))
for lab, df in (("pool stationary rule means", pS),):
    P(f"  ... and with the other observables ({lab}), |Spearman| with ret32: " + "; ".join(
        f"{o} {spearmanr(df['ret32'], df[o], nan_policy='omit').statistic:+.2f}" for o in OBS if o != "ret32"))
P("concentration of the held-out gain over pool rules (stationary cohort; per-rule SSE reduction (y-pA)^2 - (y-pAO)^2, gain = sum / SS_total):")
for coh_name, coh in (("stationary", resS), ("all-rules", resA)):
  P(f"  [{coh_name} cohort]")
  for o in ("msd64", "ret32", "reuse64", "msd_exp"):
    r = coh[o]; y = r["y"]; red = (y - r["base"]) ** 2 - (y - r["pAO"]) ** 2; den = ((y - r["trmean"]) ** 2).sum()
    order = np.argsort(-red)
    top5 = order[:5]; rest = np.setdiff1d(np.arange(len(y)), top5)
    gain_wo = red[rest].sum() / ((y[rest] - r["trmean"]) ** 2).sum()
    pos = (red > 0).mean()
    P(f"  {o:8s} gain {red.sum()/den:+.3f}; top 5 rules supply {red[top5].sum() / red.sum():.2f} of it; gain without them {gain_wo:+.3f}; share of rules with positive reduction {pos:.2f}; "
      f"top-5 rules (lnk25, z): " + ", ".join(f"{r['ids'][i]} ({y[i]:+.2f}, {r['zte'][i]:+.1f})" for i in top5))
# the section-4.4 positive control: letters predict c (W0 CHECK4: pool LOO ridge R^2 0.767), same strict-R^2 code, census-minus-pool -> pool
for lab, (dd, pp_) in (("stationary", (dS, pS)), ("all", (dA, pA_))):
    Xd = np.array([onehot(s) for s in dd["base"]]); Xp = np.array([onehot(s) for s in pp_["base"]])
    mu, sd = Xd.mean(0), Xd.std(0) + 1e-9
    Ad = np.column_stack([np.ones(len(Xd)), (Xd - mu) / sd]); Ap = np.column_stack([np.ones(len(Xp)), (Xp - mu) / sd]); lam = 10.0
    for tcol_d, tcol_p, nm in (("c", "c25", "c"), ("lnk", "lnk25", "ln kappa")):
        b = np.linalg.solve(Ad.T @ Ad + lam * np.eye(Ad.shape[1]), Ad.T @ dd[tcol_d].to_numpy())
        yt = pp_[tcol_p].to_numpy(); r2 = 1 - ((yt - Ap @ b) ** 2).sum() / ((yt - dd[tcol_d].mean()) ** 2).sum()
        P(f"letters (one-hot + n + nR, ridge 10) {lab}, census-minus-pool -> pool, strict held-out R^2 on {nm}: {r2:+.3f}" + (" (W0 pool LOO reference 0.767)" if nm == "c" else " (W0 letters on ln kappa: about 0)"))
rA_chk = [resS[o]["rA"] for o in ("I_turn",)]
P(f"ln A(22) alone, strict held-out R^2 on ln kappa, stationary: {rA_chk[0]:.3f} (W3b 0.569, W3c 0.497 with the same estimator family)")
# why were pool rules dropped?
kept = set(pool_o["base"]); dropped = [b for b in pool["base"] if b not in kept]
pp_all = runs.filter((pl.col("kind") == "pool_patched") & pl.col("rule").is_in(dropped))
P(f"pool rules without >= 4 usable seeds ({len(dropped)}): " + "; ".join(
    f"{b} (lnk25 {pool.filter(pl.col('base') == b)['lnk25'][0]:+.2f}, stationary {bool(pool.filter(pl.col('base') == b)['stat'][0])}): growth>{GROWTH_MAX} in {int((pp_all.filter(pl.col('rule') == b)['growth'] > GROWTH_MAX).sum())}/6, n_bulk<{MIN_BULK} in {int((pp_all.filter(pl.col('rule') == b)['n_bulk'] < MIN_BULK).sum())}/6, escaped/noA0 in {int((pp_all.filter(pl.col('rule') == b)['status'] != 'ok').sum())}/6" for b in dropped))

# ---------------------------------------------------------------- exploratory extras (not registered; run after seeing the primary table)
P("\n=== exploratory extras (NOT registered; added after the primary table was seen) ===")
def r2_strict(trX, trY, teX, teY):
    A = np.column_stack([np.ones(len(trX)), trX]); b = np.linalg.lstsq(A, trY, rcond=None)[0]
    return 1 - ((teY - np.column_stack([np.ones(len(teX)), teX]) @ b) ** 2).sum() / ((teY - trY.mean()) ** 2).sum()
for lab, (dd, pp_) in (("stationary", (dS, pS)), ("all", (dA, pA_))):
    line = []
    for o in OBS:
        d_ = dd.filter(pl.col(o).is_not_nan() & pl.col(o).is_not_null()); p_ = pp_.filter(pl.col(o).is_not_nan() & pl.col(o).is_not_null())
        f_ = zfit(d_[o].to_numpy())
        line.append(f"{o} {r2_strict(zapply(d_[o].to_numpy(), f_)[:, None], d_['lnk'].to_numpy(), zapply(p_[o].to_numpy(), f_)[:, None], p_['lnk25'].to_numpy()):+.3f}")
    P(f"observable ALONE (no ln A(22)), strict held-out R^2 on ln kappa, {lab}: " + "; ".join(line))
    cc = [o for o in OBS if o not in ("msd4096", "msd_exp", "ret_tail")]  # drop the observables with missing values so complete cases stay large
    okc = pl.all_horizontal([pl.col(o).is_not_nan() & pl.col(o).is_not_null() for o in cc]); d_ = dd.filter(okc); p_ = pp_.filter(okc)
    Zd = np.column_stack([zapply(d_[o].to_numpy(), zfit(d_[o].to_numpy())) for o in cc]); Zp = np.column_stack([zapply(p_[o].to_numpy(), zfit(d_[o].to_numpy())) for o in cc])
    rA = r2_strict(d_["lnA22"].to_numpy()[:, None], d_["lnk"].to_numpy(), p_["lnA22"].to_numpy()[:, None], p_["lnk25"].to_numpy())
    rAO = r2_strict(np.column_stack([d_["lnA22"].to_numpy(), Zd]), d_["lnk"].to_numpy(), np.column_stack([p_["lnA22"].to_numpy(), Zp]), p_["lnk25"].to_numpy())
    rO = r2_strict(Zd, d_["lnk"].to_numpy(), Zp, p_["lnk25"].to_numpy())
    P(f"JOINT model of {len(cc)} always-defined observables ({lab}, train {d_.height}, test {p_.height}): R2(A) {rA:.3f}; R2(A + all obs) {rAO:.3f} (joint gain {rAO - rA:+.3f}); R2(all obs, no A) {rO:.3f}")

# ---------------------------------------------------------------- sensitivity rows
P("\n=== sensitivity (unregistered, labelled as such) ===")
pool_o2 = pool_obs(usable_nogrowth).join(pool, on="base", how="inner").sort("base"); disc_o2 = disc_obs(usable_nogrowth).join(cen.select(base="rule", n="n", lnk="lnk", stat="stat", lnA22="lnA22", c="c"), on="base", how="inner").sort("base")
dS2, pS2 = cohort(disc_o2, pool_o2, True)
r2 = evaluate(dS2, pS2, "lnk", "lnk25", "nogrowth", boot=True)
P("stationary cohort, growth-factor exclusion removed (the registered exclusion could select on kappa):\n" + fmt(r2))
dA2, pA2 = cohort(disc_o2, pool_o2, False)
P(f"ALL-rules cohort, growth-factor exclusion removed (test set {pA2.height} rules instead of {pA_.height}; the dropped fast-growing rules are mostly non-stationary):\n" + fmt(evaluate(dA2, pA2, "lnk", "lnk25", "nogrowth_all", boot=True)))
pool_o3 = pool_o.with_columns(lnk25_alt=pl.col("lnk"))
r3 = evaluate(dS, cohort(disc_o, pool_o3, True)[1], "lnk", "lnk25_alt", "k26", boot=True)
P("stationary cohort, pool target = rules_pool lnk (k = 26 window) instead of the k = 25 recomputation:\n" + fmt(r3))
# size-leak
P("\nsize-leak diagnostic on pool rule means (Pearson with ln t*, ln A(22), ln kappa k=25 raw):")
for o in OBS:
    v = pool_o[o].to_numpy(); m = ~np.isnan(v)
    P(f"  {o:9s} r(ln t*) {np.corrcoef(v[m], pool_o['lnt_star'].to_numpy()[m])[0,1]:+.2f}  r(lnA22) {np.corrcoef(v[m], pool_o['lnA22'].to_numpy()[m])[0,1]:+.2f}  r(ln kappa) {np.corrcoef(v[m], pool_o['lnk25'].to_numpy()[m])[0,1]:+.2f}  Spearman(ln kappa) {spearmanr(v[m], pool_o['lnk25'].to_numpy()[m]).statistic:+.2f}")

# ---------------------------------------------------------------- positive control: c
P("\n=== positive control: the same pipeline on c (letters give R^2 0.66-0.78 on c) ===")
resC = evaluate(dS.with_columns(c=pl.col("c")), pS.with_columns(c=pl.col("c25")), "c", "c", "c", boot=True)
P("gain of each observable over ln A(22) for the stationary-cohort c target (pool c25 = mean new_cells/boundary_steps at the end of the 20..26 fit):\n" + fmt(resC))

# ---------------------------------------------------------------- planted-signal
P("\n=== planted-signal check (I_turn) ===")
d = dS.filter(pl.col("I_turn").is_not_nan()); p = pS.filter(pl.col("I_turn").is_not_nan())
bA = np.linalg.lstsq(np.column_stack([np.ones(d.height), d["lnA22"].to_numpy()]), d["lnk"].to_numpy(), rcond=None)[0]
resid_sd = (d["lnk"].to_numpy() - bA[0] - bA[1] * d["lnA22"].to_numpy()).std()
f = zfit(d["I_turn"].to_numpy()); rp = rng(47)
rec = []
for rep in range(20):
    mk = lambda df: bA[0] + bA[1] * df["lnA22"].to_numpy() + resid_sd * (np.sqrt(0.3) * zapply(df["I_turn"].to_numpy(), f) + np.sqrt(0.7) * rp.standard_normal(df.height))
    g, rA, rAO, *_ = fit_gain(d["lnA22"].to_numpy(), d["I_turn"].to_numpy(), mk(d), p["lnA22"].to_numpy(), p["I_turn"].to_numpy(), mk(p))
    rec.append((g, rA, g / (1 - rA)))
rec = np.array(rec)
P(f"planted residual R^2 0.30 in both discovery and pool; recovered gain {rec[:,0].mean():+.3f} (sd {rec[:,0].std():.3f}), R2(A) {rec[:,1].mean():.3f}, gain as a share of the unexplained variance {rec[:,2].mean():.3f}")
P(f"-> {'PASS' if abs(rec[:,2].mean() - 0.3) <= 0.1 else 'FAIL'} (criterion: share within 0.1 of 0.30)")

# ---------------------------------------------------------------- within-pool grouped CV
P("\n=== secondary: within-pool 5-fold CV grouped by (n, 5-prefix), stationary and all (no discovery set) ===")
for lab, sub in (("stationary", pool_o.filter(pl.col("stat"))), ("all", pool_o)):
    keys = [f"{len(b)}_{b[:5]}" for b in sub["base"]]; ukeys = sorted(set(keys)); rf = rng(45)
    fold_of = dict(zip(ukeys, rf.permutation(len(ukeys)) % 5)); fold = np.array([fold_of[k] for k in keys])
    P(f"{lab} ({sub.height} rules, {len(ukeys)} groups):")
    line = []
    for o in OBS:
        s2 = sub.filter(pl.col(o).is_not_nan() & pl.col(o).is_not_null()); kk = np.array([fold_of[f"{len(b)}_{b[:5]}"] for b in s2["base"]])
        num_a = num_ao = den = 0.0
        for k in range(5):
            tr, te = s2.filter(pl.Series(kk != k)), s2.filter(pl.Series(kk == k))
            if te.height == 0: continue
            g, rA, rAO, *_ = fit_gain(tr["lnA22"].to_numpy(), tr[o].to_numpy(), tr["lnk25"].to_numpy(), te["lnA22"].to_numpy(), te[o].to_numpy(), te["lnk25"].to_numpy())
            dn = ((te["lnk25"].to_numpy() - tr["lnk25"].mean()) ** 2).sum(); num_a += (1 - rA) * dn; num_ao += (1 - rAO) * dn; den += dn
        line.append(f"{o} {(1 - num_ao / den) - (1 - num_a / den):+.3f}")
    P("  gain: " + "; ".join(line))

# ---------------------------------------------------------------- controls
P("\n=== P5.4 / controls ===")
for kind in ("rotor", "pw", "rw"):
    k = runs.filter(pl.col("kind") == kind)
    ok = k.filter(pl.col("status") == "ok")
    P(f"{kind}: runs {k.height}, ok {ok.height}; n_bulk median {ok['n_bulk'].median() if ok.height else float('nan')}, mask_cells median {ok['mask_cells'].median() if ok.height else float('nan')}")
rot = runs.filter((pl.col("kind") == "rotor") & (pl.col("status") == "ok"))
if rot.height:
    P("rotor observables (mean over seeds, sd): " + "; ".join(f"{o} {rot[o].drop_nulls().drop_nans().mean():+.3f} ({rot[o].drop_nulls().drop_nans().std():.3f})" for o in OBS if rot[o].drop_nulls().drop_nans().len() > 1) + f"; bulk fraction {rot['bulk_frac'].mean():.2f}; growth {rot['growth'].mean():.2f}")
    P("rotor msd(L)/L at L = 64, 512, 4096: " + ", ".join(f"{rot[c].drop_nulls().drop_nans().mean():.2f}" for c in ("msd64", "msd512", "msd4096")) + " (a t^(1/3)-type subdiffusion would make MSD/L fall with L; no bar)")

# ---------------------------------------------------------------- pool rule table
rule_tab = pool_o.select("base", "n", "stat", "n_seeds", "lnk25", "lnk", "c25", "lnA22", "lnt_star", *OBS)
rule_tab.write_csv(EXP / "results" / "w5_rules.csv", float_precision=6)
txt = "\n".join(out) + "\n"
(EXP / "results" / "w5_stats.txt").write_text(txt)
print(txt)
