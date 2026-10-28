"""POST HOC exploration for 2026-10-kappa-exposure-classes (not registered; written after
reading results/analysis.txt). Reads results/rule_stats.csv, results/classes.csv and the census
summary; writes results/explore.txt.
Run: uv run experiments/archive/2026-10-kappa-exposure-classes/scripts/explore.py
"""
from pathlib import Path

import numpy as np
import polars as pl
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[4]
EXP = Path(__file__).resolve().parents[1]
RES = EXP / "results"
lines = []


def say(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    lines.append(s)


rules = pl.read_csv(RES / "rule_stats.csv")
census = pl.read_csv(ROOT / "experiments/archive/2026-10-probe-growth-census/results/probe_summary.csv").select(
    pl.col("rule").alias("base"), pl.col("c").alias("c_census"), pl.col("kappa").alias("kappa_census"))
rules = rules.join(census, on="base", how="left")

say("POST HOC, unregistered. 64 rules, rule means over complete patched starts.")
for c in ["rho1_ret", "rho2p_ret", "rho1", "rho2p", "first_share", "exposed_share", "Q"]:
    r = spearmanr(rules["rho"], rules[c])
    say(f"Spearman(rho, {c:13s}) = {r.statistic:+.3f}")
r = spearmanr(rules["Q"], rules["c_census"])
say(f"Spearman(Q, census c) = {r.statistic:+.3f}")
crust = rules.filter(pl.col("c_census") >= 0.6)
rest = rules.filter(pl.col("c_census") < 0.6)
for name, sub in [("crust proxy c>=0.6", crust), ("c<0.6", rest)]:
    say(f"{name}: n={sub.height} median Q {sub['Q'].median():.3f}, frac Q>1 {(sub['Q'] > 1).mean():.2f}, "
        f"median rho {sub['rho'].median():.3f}, rho1_ret {sub['rho1_ret'].median():.3f}, rho2p_ret {sub['rho2p_ret'].median():.3f}")

# Decomposition of rho into class shares: rho = sum_u w_u rho_u with w_u = M_u / M (pooled k=17..26).
df = pl.read_csv(RES / "classes.csv").filter((pl.col("k") >= 17) & (pl.col("k") <= 26))
df = df.with_columns(
    pl.when(pl.col("spec").str.starts_with("rotor:")).then(pl.lit("rotor"))
    .when(pl.col("spec").str.starts_with("rw:")).then(pl.lit("rw"))
    .when(pl.col("spec").str.starts_with("mf:")).then(pl.lit("mf"))
    .when(pl.col("spec").str.contains("@")).then(pl.lit("ant")).otherwise(pl.lit("blank")).alias("kind"))
g = df.group_by(["spec", "kind"]).agg([pl.len().alias("nwin")] + [pl.col(f"{x}{u}").sum().alias(f"{x.upper()}{u}") for x in "bfm" for u in range(1, 5)])
g = g.filter((pl.col("nwin") == 10) | (pl.col("kind") == "rw"))
M = sum(pl.col(f"M{u}") for u in range(1, 5))
g = g.with_columns(
    (pl.col("M1") / M).alias("w1"),
    ((pl.col("F1")) / M).alias("first1"), ((pl.col("F2") + pl.col("F3") + pl.col("F4")) / M).alias("first2p"),
    ((pl.col("B1") - pl.col("F1")) / M).alias("ret1"),
    ((pl.col("B2") + pl.col("B3") + pl.col("B4") - pl.col("F2") - pl.col("F3") - pl.col("F4")) / M).alias("ret2p"),
)
say("\nrho = first1 + first2p + ret1 + ret2p (contributions per unit of time-averaged P/A); w1 = flat share of P")
for kind in ["ant", "rotor", "rw", "mf"]:
    s = g.filter(pl.col("kind") == kind)
    vals = {c: float(s[c].median()) for c in ["w1", "first1", "first2p", "ret1", "ret2p"]}
    say(f"{kind:5s} (n={s.height}) median: " + ", ".join(f"{k} {v:.3f}" for k, v in vals.items())
        + f", sum {vals['first1'] + vals['first2p'] + vals['ret1'] + vals['ret2p']:.3f}")
(RES / "explore.txt").write_text("\n".join(lines) + "\n")

# ---- Sensitivity: patched runs that left the blob regime without escaping (board fillers).
# Flag: births per step in window 26 > 0.05 (all other ant runs are <= 0.0101; blank-board census
# rules are stationary blobs). Not in the registered plan, which excluded only escapes.
say("\nSENSITIVITY (post hoc): drop patched runs with births/step > 0.05 in window 26")
pat = g.filter(pl.col("kind") == "ant")
w26 = df.filter(pl.col("k") == 26).select("spec", (pl.col("new_cells") / pl.col("steps")).alias("birth_rate"),
                                           ((pl.col("p2") + pl.col("p3") + pl.col("p4")) / (pl.col("p1") + pl.col("p2") + pl.col("p3") + pl.col("p4"))).alias("exposed_share"))
pat = pat.join(w26, on="spec").with_columns(pl.col("spec").str.split("@").list.first().alias("base"))
flag = pat.filter(pl.col("birth_rate") > 0.05)
say(f"flagged runs: {flag.select('spec', 'birth_rate').rows()}")
pat = pat.filter(pl.col("birth_rate") <= 0.05)
B = sum(pl.col(f"B{u}") for u in range(1, 5))
pat = pat.with_columns(
    (B / M).alias("rho"),
    (((pl.col("B1") - pl.col("F1")) / pl.col("M1")) /
     ((pl.col("B2") + pl.col("B3") + pl.col("B4") - pl.col("F2") - pl.col("F3") - pl.col("F4")) / (pl.col("M2") + pl.col("M3") + pl.col("M4")))).alias("Q"),
    ((pl.col("B1") - pl.col("F1")) / pl.col("M1")).alias("rho1_ret"),
    ((pl.col("B2") + pl.col("B3") + pl.col("B4") - pl.col("F2") - pl.col("F3") - pl.col("F4")) / (pl.col("M2") + pl.col("M3") + pl.col("M4"))).alias("rho2p_ret"))
rr = pat.group_by("base").agg([pl.len().alias("n")] + [pl.col(c).mean() for c in ["rho", "Q", "rho1_ret", "rho2p_ret", "exposed_share"]]).sort("base")  # sorted: group_by order is per-process and feeds the seeded bootstrap below
Qs = rr["Q"].to_numpy()
rng = np.random.default_rng(20261020)
ci = np.percentile(np.median(rng.choice(Qs, size=(4000, len(Qs)), replace=True), axis=1), [2.5, 97.5])
say(f"rules {rr.height}; median rho {rr['rho'].median():.4f}, frac rho>=1 {(rr['rho'] >= 1).mean():.3f}; "
    f"median Q {np.median(Qs):.4f} [{ci[0]:.4f}, {ci[1]:.4f}], frac Q>1 {(Qs > 1).mean():.3f}; "
    f"Spearman(rho, exposed share) {spearmanr(rr['rho'], rr['exposed_share']).statistic:+.4f}; "
    f"Spearman(rho, rho1_ret) {spearmanr(rr['rho'], rr['rho1_ret']).statistic:+.4f}, (rho, rho2p_ret) {spearmanr(rr['rho'], rr['rho2p_ret']).statistic:+.4f}, (rho, Q) {spearmanr(rr['rho'], rr['Q']).statistic:+.4f}")
say(f"max rule-mean rho1_ret {rr['rho1_ret'].max():.3f}, rho2p_ret {rr['rho2p_ret'].max():.3f}")
(RES / "explore.txt").write_text("\n".join(lines) + "\n")
