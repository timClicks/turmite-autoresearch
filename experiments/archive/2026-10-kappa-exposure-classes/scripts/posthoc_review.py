"""POST HOC review statistics for 2026-10-kappa-exposure-classes (added 2026-10-25 in the
adversarial review; NOT registered, no new claims are scored). Reads only committed results
(results/classes.csv, results/rule_stats.csv); writes results/review.txt and results/review.json.

1. Uncertainty the original analysis did not report: Wilson and rule-bootstrap intervals for the
   fraction of rules with Q > 1, per-seed fractions, rules whose seed range straddles Q = 1; bootstrap
   intervals for the P4 Spearman, for Spearman(rho, rho1_ret) and for the P2 / P2b statistics.
2. Composition confound (flat cells are ~72% of the time-averaged boundary): rho per run is exactly
   birth + w1*rho1_ret + (1-w1)*rho2p_ret with w1 = M1/M and birth = sum F / M. We (a) split the
   between-rule variance of rho exactly into Cov(term, rho)/Var(rho), (b) recompute rho with the
   class weights frozen at the cohort median (and at 1/2), and (c) split the ant-rotor gap into
   birth, composition and return parts.
Run: uv run --frozen experiments/archive/2026-10-kappa-exposure-classes/scripts/posthoc_review.py
"""
import hashlib
import json
import subprocess
from pathlib import Path

import numpy as np
import polars as pl
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[4]
EXP = Path(__file__).resolve().parents[1]
RES = EXP / "results"
SEED = 20261020
NBOOT = 4000
K_LO, K_HI = 17, 26
KAPPA_UNIF = 1.105
lines = []


def say(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    lines.append(s)


def wilson(k, n, z=1.959964):
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return c - h, c + h


def ci(x):
    return np.percentile(x, [2.5, 97.5]).round(4).tolist()


rng = np.random.default_rng(SEED)
df = pl.read_csv(RES / "classes.csv")
w = df.filter((pl.col("k") >= K_LO) & (pl.col("k") <= K_HI))
agg = [pl.len().alias("nwin")] + [pl.col(f"{x}{u}").sum().alias(f"{x.upper()}{u}") for x in "bfm" for u in range(1, 5)]
g = w.group_by("spec", maintain_order=True).agg(agg)
w26 = w.filter(pl.col("k") == K_HI).select(
    "spec", (pl.col("new_cells") / pl.col("steps")).alias("birth_rate"),
    ((pl.col("p2") + pl.col("p3") + pl.col("p4")) / (pl.col("p1") + pl.col("p2") + pl.col("p3") + pl.col("p4"))).alias("exposed_share"),
    ((pl.col("b1") + pl.col("b2") + pl.col("b3") + pl.col("b4")) / pl.col("steps")
     / ((pl.col("p1") + pl.col("p2") + pl.col("p3") + pl.col("p4")) / pl.col("area"))).alias("kappa26"))
g = g.join(w26, on="spec", how="left")
M = sum(pl.col(f"M{u}") for u in range(1, 5))
B = sum(pl.col(f"B{u}") for u in range(1, 5))
F = sum(pl.col(f"F{u}") for u in range(1, 5))
M2 = pl.col("M2") + pl.col("M3") + pl.col("M4")
g = g.with_columns(
    pl.when(pl.col("spec").str.starts_with("rotor:")).then(pl.lit("rotor"))
    .when(pl.col("spec").str.starts_with("rw:")).then(pl.lit("rw"))
    .when(pl.col("spec").str.starts_with("mf:")).then(pl.lit("mf"))
    .when(pl.col("spec").str.contains("@")).then(pl.lit("ant")).otherwise(pl.lit("blank")).alias("kind"),
    pl.col("spec").str.split("@").list.first().alias("base"),
    pl.col("spec").str.split("@").list.last().alias("start"),
    (B / M).alias("rho"), (F / M).alias("birth"), (pl.col("M1") / M).alias("w1"),
    ((pl.col("B1") - pl.col("F1")) / pl.col("M1")).alias("r1"),
    ((pl.col("B2") + pl.col("B3") + pl.col("B4") - pl.col("F2") - pl.col("F3") - pl.col("F4")) / M2).alias("r2"),
).with_columns((pl.col("r1") / pl.col("r2")).alias("Q"))
# exact identity check
resid = g.select((pl.col("rho") - pl.col("birth") - pl.col("w1") * pl.col("r1") - (1 - pl.col("w1")) * pl.col("r2")).abs().max()).item()
say("POST HOC review (2026-10-25), unregistered. Inputs: committed results only.")
say(f"identity rho = birth + w1*r1 + (1-w1)*r2 per run: max |residual| {resid:.2e}")

ants = g.filter((pl.col("kind") == "ant") & (pl.col("nwin") == 10))
cols = ["rho", "birth", "w1", "r1", "r2", "Q", "exposed_share"]
ants = ants.with_columns((pl.col("w1") * pl.col("r1")).alias("t1"), ((1 - pl.col("w1")) * pl.col("r2")).alias("t2"))
rules_all = ants.group_by("base", maintain_order=True).agg(
    [pl.len().alias("n")] + [pl.col(c).mean() for c in cols + ["t1", "t2"]]
    + [pl.col("Q").min().alias("Qmin"), pl.col("Q").max().alias("Qmax")])
# cross-check against the registered analysis output
rs = pl.read_csv(RES / "rule_stats.csv").select("base", pl.col("Q").alias("Q_ref"), pl.col("rho").alias("rho_ref"))
chk = rules_all.join(rs, on="base")
dmax = chk.select(((pl.col("Q") - pl.col("Q_ref")).abs().max()), ((pl.col("rho") - pl.col("rho_ref")).abs().max())).row(0)
say(f"rule means reproduce rule_stats.csv: {chk.height} rules, max |dQ| {dmax[0]:.1e}, max |drho| {dmax[1]:.1e}")
FILLER = 0.05
fill_bases = ants.filter(pl.col("birth_rate") > FILLER)["spec"].to_list()
ants_nf = ants.filter(pl.col("birth_rate") <= FILLER)
rules_nf = ants_nf.group_by("base", maintain_order=True).agg([pl.len().alias("n")] + [pl.col(c).mean() for c in cols + ["t1", "t2"]])
out = {"seed": SEED, "nboot": NBOOT, "filler_runs": fill_bases}

# ---------------- 1. uncertainty
say("\n== 1. Uncertainty (rule = resampling unit, seed %d, %d resamples) ==" % (SEED, NBOOT))
Q = rules_all["Q"].to_numpy()
n = len(Q)
k = int((Q > 1).sum())
lo, hi = wilson(k, n)
bfrac = (rng.choice(Q, size=(NBOOT, n)) > 1).mean(axis=1)
say(f"P3 fraction Q>1: {k}/{n} = {k / n:.3f}; Wilson 95% [{lo:.3f}, {hi:.3f}]; bootstrap 95% {ci(bfrac)}; "
    f"bootstrap P(frac >= 0.75) = {(bfrac >= 0.75).mean():.3f}")
need = int(np.ceil(0.75 * n))
say(f"  the 0.75 threshold needs {need}/{n}; {need - k} more rules would have to cross Q = 1")
straddle = rules_all.filter((pl.col("Qmin") <= 1) & (pl.col("Qmax") > 1))
say(f"  rules whose patched-start Q range straddles 1: {straddle.height} ({straddle['base'].to_list()})")
say(f"  rules with mean Q in [0.9, 1.1]: {int(((Q >= 0.9) & (Q <= 1.1)).sum())}")
for s in ["1", "2", "3", "4"]:
    sub = ants.filter(pl.col("start") == s)
    say(f"  start @{s} alone: {sub.height} rules, frac Q>1 {(sub['Q'] > 1).mean():.3f}, median Q {sub['Q'].median():.3f}")
out["frac_Q_gt_1"] = {"k": k, "n": n, "wilson95": [lo, hi], "boot95": ci(bfrac), "boot_p_ge_075": float((bfrac >= 0.75).mean()),
                      "straddle": straddle.height}
mq = np.median(rng.choice(Q, size=(NBOOT, n)), axis=1)
say(f"P3 median Q {np.median(Q):.4f}, bootstrap 95% {ci(mq)} (re-derived; analysis.txt used its own draw)")


def boot_spearman(x, y, label):
    x = np.asarray(x)
    y = np.asarray(y)
    obs = spearmanr(x, y).statistic
    idx = rng.integers(0, len(x), size=(NBOOT, len(x)))
    bs = np.array([spearmanr(x[i], y[i]).statistic for i in idx])
    say(f"Spearman({label}) = {obs:+.3f}, bootstrap 95% {ci(bs)}, P(boot <= -0.4) = {(bs <= -0.4).mean():.3f}")
    return float(obs), ci(bs), bs


for name, R in [("all 64 rules", rules_all), ("fillers removed", rules_nf)]:
    say(f"-- {name}")
    o, c, bs = boot_spearman(R["rho"], R["exposed_share"], "rho, exposed share [P4]")
    out[f"P4_spearman_{'all' if 'all' in name else 'nf'}"] = {"obs": o, "boot95": c}
    o, c, _ = boot_spearman(R["rho"], R["r1"], "rho, rho1_ret [post hoc; part-whole]")
    out[f"sp_rho_r1_{'all' if 'all' in name else 'nf'}"] = {"obs": o, "boot95": c}
    boot_spearman(R["rho"], R["r2"], "rho, rho2p_ret [post hoc; part-whole]")
    boot_spearman(R["rho"], R["Q"], "rho, Q [post hoc]")

rho = rules_all["rho"].to_numpy()
b_med = np.median(rng.choice(rho, size=(NBOOT, n)), axis=1)
b_fr = (rng.choice(rho, size=(NBOOT, n)) >= 1).mean(axis=1)
say(f"P2 ant median rho {np.median(rho):.4f} bootstrap 95% {ci(b_med)}; frac rho>=1 {(rho >= 1).mean():.3f} "
    f"Wilson {np.round(wilson(int((rho >= 1).sum()), n), 3).tolist()} bootstrap {ci(b_fr)}")
blank = g.filter((pl.col("kind") == "blank") & (pl.col("nwin") == 10))
ratio = blank["rho"].to_numpy() * KAPPA_UNIF / blank["kappa26"].to_numpy()
dev = np.abs(np.log(ratio))
bd = np.median(rng.choice(dev, size=(NBOOT, len(dev))), axis=1)
say(f"P2b {len(dev)} blank runs: median |ln dev| {np.median(dev):.4f} bootstrap 95% {ci(bd)}; "
    f"ratio rho*1.105/kappa26 q05/50/95 {np.percentile(ratio, [5, 50, 95]).round(4).tolist()}, "
    f"|ln dev| > 0.05 in {int((dev > 0.05).sum())}/{len(dev)}, > 0.10 in {int((dev > 0.10).sum())}/{len(dev)}")
out["P2b"] = {"median_abs_ln_dev": float(np.median(dev)), "boot95": ci(bd), "n_gt_005": int((dev > 0.05).sum()), "n": len(dev)}

# ---------------- 2. composition
say("\n== 2. Composition (post hoc). rho = birth + w1*r1 + (1-w1)*r2, exact per run and in rule means ==")
for name, R in [("fillers removed (primary; fillers have rho ~140 and dominate variances)", rules_nf), ("all 64 rules", rules_all)]:
    say(f"-- {name}: n = {R.height} rules" + (f" (filler runs with birth_rate > {FILLER} dropped: {fill_bases}; each rule keeps its other starts)" if R is rules_nf else ""))
    rr = R["rho"].to_numpy()
    terms = {"birth": R["birth"].to_numpy(), "w1*r1 (flat returns)": R["t1"].to_numpy(), "(1-w1)*r2 (exposed returns)": R["t2"].to_numpy()}
    v = np.var(rr)
    tot = 0
    for t, x in terms.items():
        s = np.cov(x, rr, bias=True)[0, 1] / v
        tot += s
        say(f"  Cov({t}, rho)/Var(rho) = {s:+.3f}")
    say(f"  sum = {tot:.3f}; median w1 = {np.median(R['w1']):.3f} (q05-q95 {np.percentile(R['w1'], [5, 95]).round(3).tolist()})")
    say(f"  Spearman(rho, w1) = {spearmanr(rr, R['w1']).statistic:+.3f}; Spearman(w1, r1) = {spearmanr(R['w1'], R['r1']).statistic:+.3f}")
    for wl, wv in [("cohort median w1", float(np.median(R["w1"]))), ("w1 = 1/2", 0.5)]:
        rf = R["birth"].to_numpy() + wv * R["r1"].to_numpy() + (1 - wv) * R["r2"].to_numpy()
        a = wv * R["r1"].to_numpy()
        b = (1 - wv) * R["r2"].to_numpy()
        vf = np.var(rf)
        say(f"  fixed weights ({wl} = {wv:.3f}): Spearman(rho_fixed, rho) {spearmanr(rf, rr).statistic:+.3f}; "
            f"Cov share birth {np.cov(R['birth'], rf, bias=True)[0, 1] / vf:+.3f}, flat {np.cov(a, rf, bias=True)[0, 1] / vf:+.3f}, "
            f"exposed {np.cov(b, rf, bias=True)[0, 1] / vf:+.3f}; Spearman(rho_fixed, r1) {spearmanr(rf, R['r1']).statistic:+.3f}, "
            f"(rho_fixed, r2) {spearmanr(rf, R['r2']).statistic:+.3f}")
        if R is rules_nf and wl == "w1 = 1/2":
            out["fixed_half_flat_share"] = float(np.cov(a, rf, bias=True)[0, 1] / vf)
    if R is rules_nf:
        out["cov_shares_nf"] = {t: float(np.cov(x, rr, bias=True)[0, 1] / v) for t, x in terms.items()}
        out["median_w1_nf"] = float(np.median(R["w1"]))

say("\n-- ant vs rotor gap (medians of rule means, fillers removed; rotor 8 seeds)")
rot = g.filter((pl.col("kind") == "rotor") & (pl.col("nwin") == 10))
rw = g.filter((pl.col("kind") == "rw") & (pl.col("nwin") >= 3))
for nm, X in [("ant", rules_nf), ("rotor", rot), ("rw", rw)]:
    say(f"  {nm:5s}: rho {X['rho'].median():.3f} birth {X['birth'].median():.3f} w1 {X['w1'].median():.3f} "
        f"r1 {X['r1'].median():.3f} r2 {X['r2'].median():.3f}")
# gap decomposition at the medians (Shapley-style over the three ingredients is overkill; report a symmetric split)
a = {c: float(rules_nf[c].median()) for c in ["rho", "birth", "w1", "r1", "r2"]}
r = {c: float(rot[c].median()) for c in ["rho", "birth", "w1", "r1", "r2"]}
ret = lambda w_, r1_, r2_: w_ * r1_ + (1 - w_) * r2_
gap = r["rho"] - a["rho"]
g_birth = r["birth"] - a["birth"]
wbar = (a["w1"] + r["w1"]) / 2
g_r1 = wbar * (r["r1"] - a["r1"])
g_r2 = (1 - wbar) * (r["r2"] - a["r2"])
g_w = (r["w1"] - a["w1"]) * ((a["r1"] + r["r1"]) / 2 - (a["r2"] + r["r2"]) / 2)
say(f"  rotor - ant median rho = {gap:.3f}; split (symmetric, at medians; medians do not add exactly): "
    f"birth {g_birth:.3f}, flat returns {g_r1:.3f}, exposed returns {g_r2:.3f}, composition {g_w:.3f}, "
    f"sum {g_birth + g_r1 + g_r2 + g_w:.3f}")
say(f"  birth share of the summed gap {g_birth / (g_birth + g_r1 + g_r2 + g_w):.2f}; flat-return share "
    f"{g_r1 / (g_birth + g_r1 + g_r2 + g_w):.2f}; exposed-return share {g_r2 / (g_birth + g_r1 + g_r2 + g_w):.2f}")
for nm, X in [("rotor", rot), ("rw", rw)]:
    say(f"  ant/{nm} ratio of medians: rho {a['rho'] / X['rho'].median():.2f}, birth {a['birth'] / X['birth'].median():.2f}, "
        f"flat r1 {a['r1'] / X['r1'].median():.2f}, exposed r2 {a['r2'] / X['r2'].median():.2f}")
out["gap"] = {"total_at_medians": gap, "birth": g_birth, "flat": g_r1, "exposed": g_r2, "composition": g_w}

say("\n== 3. Mean-field kappa replication (post hoc; for evidence-ledger BO-04) ==")
say("  probe kappa per window = (sum_u b_u / steps) / (sum_u p_u / area) at the window end (end reference), k = 17..26")
mf = w.filter(pl.col("spec").str.starts_with("mf:")).with_columns(
    ((pl.col("b1") + pl.col("b2") + pl.col("b3") + pl.col("b4")) / pl.col("steps")
     / ((pl.col("p1") + pl.col("p2") + pl.col("p3") + pl.col("p4")) / pl.col("area"))).alias("kw"))
per = mf.group_by("spec", maintain_order=True).agg(pl.len().alias("nwin"), pl.col("kw").mean().alias("kappa"))
for sp, nwin, kap in per.iter_rows():
    say(f"  {sp}: {nwin} windows, mean kappa {kap:.4f}")
kv = per["kappa"].to_numpy()
say(f"  {len(kv)} seeds: mean {kv.mean():.4f}, between-seed SD {kv.std(ddof=1):.4f}, SE {kv.std(ddof=1) / np.sqrt(len(kv)):.4f}, "
    f"range [{kv.min():.4f}, {kv.max():.4f}]; all windows complete: {bool((per['nwin'] == K_HI - K_LO + 1).all())}")
say("  comparison (evidence ledger BO-02, not recomputed here): 1.118 (SD 0.009), seeds 2026101601..08, 2^23 steps, k = 12..22;"
    " formula 1.107. This run: seeds 1..8, 2^26 steps, board 8192, k = 17..26, instrument examples/kappa_exposure_classes.rs")
out["mf_kappa"] = {"per_seed": dict(zip(per["spec"].to_list(), kv.round(6).tolist())), "mean": float(kv.mean()), "sd": float(kv.std(ddof=1))}

prov = {"git": subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip(),
        "inputs": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in [RES / "classes.csv", RES / "rule_stats.csv"]}}
out["provenance"] = prov
say("\nprovenance", json.dumps(prov))
(RES / "review.txt").write_text("\n".join(lines) + "\n")
(RES / "review.json").write_text(json.dumps(out, indent=1) + "\n")
