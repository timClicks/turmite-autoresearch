"""Analysis for 2026-10-kappa-exposure-classes (plan registered in README.md, P0-P4).

Reads results/classes.csv (from scripts/run.sh) and the committed census windows; writes
results/analysis.txt, results/analysis.json and results/rule_stats.csv.
Run: uv run experiments/archive/2026-10-kappa-exposure-classes/scripts/analyse.py
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
CENSUS = ROOT / "experiments/archive/2026-10-probe-growth-census/results/probe_all.csv"
K_LO, K_HI = 17, 26
KAPPA_UNIF = 1.105
U = [1, 2, 3, 4]

out_lines = []


def say(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    out_lines.append(s)


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


df = pl.read_csv(RES / "classes.csv")
df = df.with_columns(
    pl.col("spec").str.split("@").list.first().str.split(":").list.first().alias("base"),
    pl.when(pl.col("spec").str.starts_with("mf:")).then(pl.lit("mf"))
    .when(pl.col("spec").str.starts_with("rotor:")).then(pl.lit("rotor"))
    .when(pl.col("spec").str.starts_with("rw:")).then(pl.lit("rw"))
    .when(pl.col("spec").str.contains("@")).then(pl.lit("patched"))
    .otherwise(pl.lit("blank")).alias("kind"),
)

# ---- P0: reproduction of committed census windows by blank-board runs
census = pl.read_csv(CENSUS).select(["rule", "k", "area", "perimeter", "new_cells", "boundary_steps"])
blank = df.filter(pl.col("kind") == "blank").with_columns(
    (pl.col("p1") + pl.col("p2") + pl.col("p3") + pl.col("p4")).alias("perimeter"),
    (pl.col("b1") + pl.col("b2") + pl.col("b3") + pl.col("b4")).alias("boundary_steps"),
)
j = blank.select(["spec", "k", "area", "perimeter", "new_cells", "boundary_steps"]).rename({"spec": "rule"}).join(
    census, on=["rule", "k"], how="inner", suffix="_c")
mism = j.filter((pl.col("area") != pl.col("area_c")) | (pl.col("perimeter") != pl.col("perimeter_c"))
                | (pl.col("new_cells") != pl.col("new_cells_c")) | (pl.col("boundary_steps") != pl.col("boundary_steps_c")))
n_blank_rules = blank["spec"].n_unique()
say(f"P0 reproduction: {j.height} shared windows over {j['rule'].n_unique()} of {n_blank_rules} blank-board rules; mismatches {mism.height}")
p0_ok = mism.height == 0 and j["rule"].n_unique() == n_blank_rules

# ---- per-run pooled statistics over windows K_LO..K_HI
w = df.filter((pl.col("k") >= K_LO) & (pl.col("k") <= K_HI))
agg = [pl.len().alias("nwin"), pl.col("escaped").first().alias("escaped")]
for u in U:
    agg += [pl.col(f"b{u}").sum().alias(f"B{u}"), pl.col(f"f{u}").sum().alias(f"F{u}"), pl.col(f"m{u}").sum().alias(f"M{u}")]
runs = w.group_by(["spec", "base", "kind"], maintain_order=True).agg(agg)
last = w.filter(pl.col("k") == K_HI).select(
    "spec", (pl.col("p2") + pl.col("p3") + pl.col("p4")).alias("pex"),
    (pl.col("p1") + pl.col("p2") + pl.col("p3") + pl.col("p4")).alias("P26"), "area",
    (pl.col("b1") + pl.col("b2") + pl.col("b3") + pl.col("b4")).alias("B26"), "steps")
runs = runs.join(last, on="spec", how="left")
B = sum(pl.col(f"B{u}") for u in U)
M = sum(pl.col(f"M{u}") for u in U)
runs = runs.with_columns(
    (B / M).alias("rho"),
    (pl.col("B1") / pl.col("M1")).alias("rho1"),
    (pl.col("B2") / pl.col("M2")).alias("rho2"),
    (pl.col("B3") / pl.col("M3")).alias("rho3"),
    ((pl.col("B1") - pl.col("F1")) / pl.col("M1")).alias("rho1_ret"),
    ((pl.col("B2") + pl.col("B3") + pl.col("B4") - pl.col("F2") - pl.col("F3") - pl.col("F4"))
     / (pl.col("M2") + pl.col("M3") + pl.col("M4"))).alias("rho2p_ret"),
    ((pl.col("B2") + pl.col("B3") + pl.col("B4")) / (pl.col("M2") + pl.col("M3") + pl.col("M4"))).alias("rho2p"),
    ((pl.col("B1") - pl.col("F1") + pl.col("B2") + pl.col("B3") + pl.col("B4") - pl.col("F2") - pl.col("F3") - pl.col("F4")) / M).alias("rho_ret"),
    (sum(pl.col(f"F{u}") for u in U) / B).alias("first_share"),
    (pl.col("pex") / pl.col("P26")).alias("exposed_share"),
    ((pl.col("B26") / pl.col("steps")) / (pl.col("P26") / pl.col("area"))).alias("kappa26"),
).with_columns((pl.col("rho1_ret") / pl.col("rho2p_ret")).alias("Q"))
complete = pl.col("nwin") == (K_HI - K_LO + 1)

# ---- P1: mean-field calibration
mf = runs.filter(pl.col("kind") == "mf")
say("\nP1 mean-field calibration (per seed):")
p1_ok = mf.height == 8
for r in mf.iter_rows(named=True):
    f = sum(r[f"F{u}"] for u in U) / sum(r[f"B{u}"] for u in U)
    ok = (r["nwin"] == 10 and abs(r["rho"] - 1) <= 0.01 and abs(r["rho1"] - 1) <= 0.02 and abs(r["rho2"] - 1) <= 0.03
          and abs(r["rho3"] - 1) <= 0.10 and f < 0.001)
    p1_ok &= ok
    say(f"  {r['spec']}: nwin {r['nwin']} rho {r['rho']:.4f} rho1 {r['rho1']:.4f} rho2 {r['rho2']:.4f} rho3 {r['rho3']:.4f} first_share {f:.5f} {'ok' if ok else 'FAIL'}")
say(f"P1 {'HELD' if p1_ok else 'FAILED'}")

# ---- ants
pat = runs.filter(pl.col("kind") == "patched")
n_esc = pat.filter(~complete).height
say(f"\nAnts: {pat.height} patched runs, {n_esc} excluded (escaped before window {K_HI} complete)")
pat = pat.filter(complete)
cols = ["rho", "rho1", "rho2", "rho3", "rho2p", "rho1_ret", "rho2p_ret", "rho_ret", "Q", "first_share", "exposed_share"]
rules = pat.group_by("base", maintain_order=True).agg(
    [pl.len().alias("nseeds")] + [pl.col(c).mean().alias(c) for c in cols] + [pl.col(c).std().alias(c + "_sd") for c in ["rho", "Q", "rho1_ret", "rho2p_ret"]])
blank_runs = runs.filter((pl.col("kind") == "blank") & complete).select(
    pl.col("base"), pl.col("rho").alias("rho_blank"), pl.col("kappa26").alias("kappa26_blank"), pl.col("Q").alias("Q_blank"))
rules = rules.join(blank_runs, on="base", how="left")
rules.write_csv(RES / "rule_stats.csv", float_precision=6)


def q(x):
    x = np.asarray(x, float)
    return np.percentile(x, [5, 25, 50, 75, 95])


say(f"rules with >=1 complete patched run: {rules.height}; seeds per rule: min {rules['nseeds'].min()}")
for c in ["rho", "rho1", "rho2p", "rho1_ret", "rho2p_ret", "Q", "first_share", "exposed_share"]:
    say(f"  {c:14s} q05/25/50/75/95 = {np.round(q(rules[c]), 3).tolist()}")
say(f"  median between-seed sd: rho {np.nanmedian(rules['rho_sd']):.4f}, Q {np.nanmedian(rules['Q_sd']):.4f}, "
    f"rho1_ret {np.nanmedian(rules['rho1_ret_sd']):.4f}, rho2p_ret {np.nanmedian(rules['rho2p_ret_sd']):.4f}")

# ---- P2
med_rho = float(np.median(rules["rho"]))
frac_ge1 = float((rules["rho"] >= 1).mean())
rot = runs.filter((pl.col("kind") == "rotor"))
rot_c = rot.filter(complete)
rw = runs.filter(pl.col("kind") == "rw")
rw_u = rw.filter(pl.col("nwin") >= 3)
med_rot = float(np.median(rot_c["rho"])) if rot_c.height else float("nan")
med_rw = float(np.median(rw_u["rho"])) if rw_u.height else float("nan")
p2_ok = 0.70 <= med_rho <= 0.92 and 0.08 <= frac_ge1 <= 0.35 and 1.45 <= med_rot <= 1.95
rw_clause = None if not rw_u.height else (1.05 <= med_rw <= 1.45)
say(f"\nP2: ant median rho {med_rho:.4f}, fraction rho>=1 {frac_ge1:.3f}; rotor median rho {med_rot:.4f} "
    f"({rot_c.height}/{rot.height} complete, sd {rot_c['rho'].std():.4f}); rw median rho {med_rw:.4f} "
    f"({rw_u.height}/{rw.height} usable, windows {rw['nwin'].to_list()})")
say(f"P2 {'HELD' if p2_ok else 'FAILED'} (ant + rotor clauses); rw clause: {rw_clause}")

# ---- P2b
bb = rules.filter(pl.col("rho_blank").is_not_null())
dev = np.abs(np.log(bb["rho_blank"].to_numpy() / (bb["kappa26_blank"].to_numpy() / KAPPA_UNIF)))
med_dev = float(np.median(dev))
p2b_ok = med_dev <= 0.05
say(f"\nP2b: {bb.height} blank runs; median |ln(rho_blank/(kappa26/{KAPPA_UNIF}))| = {med_dev:.4f}; "
    f"q05/50/95 of ratio rho*1.105/kappa26 = {np.round(q(bb['rho_blank'].to_numpy() * KAPPA_UNIF / bb['kappa26_blank'].to_numpy())[[0, 2, 4]], 4).tolist()}")
say(f"P2b {'HELD' if p2b_ok else 'FAILED'}")

# ---- P3
Q = rules["Q"].to_numpy()
medQ = float(np.median(Q))
fracQ = float((Q > 1).mean())
verdict = "H-exposed" if medQ >= 1.18 else ("H-flat" if medQ <= 0.85 else "H-proportional")
p3_ok = medQ >= 1.18 and fracQ >= 0.75
# rule-bootstrap CI for the median Q
rng = np.random.default_rng(20261020)
boots = np.median(rng.choice(Q, size=(4000, len(Q)), replace=True), axis=1)
ci = np.percentile(boots, [2.5, 97.5])
say(f"\nP3: median Q {medQ:.4f} [rule bootstrap 95% {ci[0]:.4f}, {ci[1]:.4f}], fraction Q>1 {fracQ:.3f} -> outcome {verdict}")
say(f"P3 (H-exposed as registered) {'HELD' if p3_ok else 'FAILED'}")
say(f"  rotor Q median {np.median(rot_c['Q']) if rot_c.height else float('nan'):.4f} (sd {rot_c['Q'].std() if rot_c.height else float('nan'):.4f}); "
    f"rw Q median {np.median(rw_u['Q']) if rw_u.height else float('nan'):.4f}; mf Q median {np.median(mf['Q']):.4f}")
for name, sub in [("rotor", rot_c), ("rw", rw_u)]:
    if sub.height:
        say(f"  {name}: rho1 {np.median(sub['rho1']):.4f} rho2+ {np.median(sub['rho2p']):.4f} rho1_ret {np.median(sub['rho1_ret']):.4f} "
            f"rho2p_ret {np.median(sub['rho2p_ret']):.4f} first_share {np.median(sub['first_share']):.4f} exposed_share {np.median(sub['exposed_share']):.4f}")

# ---- P4
rs = spearmanr(rules["rho"], rules["exposed_share"])
p4_applies = verdict == "H-exposed"
say(f"\nP4: Spearman(rho, exposed share at k={K_HI}) = {rs.statistic:.4f} (p {rs.pvalue:.3g}); "
    f"{'applies' if p4_applies else 'conditional on H-exposed, which did not occur: not scored'}; "
    f"{'HELD' if rs.statistic <= -0.4 else 'not met'}")

prov = {
    "git": subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip(),
    "inputs": {str(p.relative_to(ROOT)): sha(p) for p in [RES / "classes.csv", RES / "specs.txt", CENSUS]},
    "windows": [K_LO, K_HI],
    "bootstrap_seed": 20261020,
}
summary = {
    "P0_reproduction_held": bool(p0_ok), "P0_shared_windows": j.height, "P0_mismatches": mism.height,
    "P1_held": bool(p1_ok),
    "P2_held": bool(p2_ok), "ant_median_rho": med_rho, "ant_frac_rho_ge_1": frac_ge1, "rotor_median_rho": med_rot,
    "rw_median_rho": med_rw, "rw_clause": rw_clause, "patched_runs_excluded": n_esc, "n_rules": rules.height,
    "P2b_held": bool(p2b_ok), "P2b_median_abs_ln_dev": med_dev,
    "P3_held": bool(p3_ok), "median_Q": medQ, "median_Q_ci95": ci.tolist(), "frac_Q_gt_1": fracQ, "P3_outcome": verdict,
    "P4_spearman": float(rs.statistic), "P4_scored": p4_applies,
    "median_between_seed_sd": {"rho": float(np.nanmedian(rules["rho_sd"])), "Q": float(np.nanmedian(rules["Q_sd"]))},
    "provenance": prov,
}
(RES / "analysis.json").write_text(json.dumps(summary, indent=1) + "\n")
say("\nprovenance", json.dumps(prov))
(RES / "analysis.txt").write_text("\n".join(out_lines) + "\n")
