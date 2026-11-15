"""POST HOC (not registered): spread of the per-rule lag Lambda and its relation to rule composition.

usage (repo root): uv run --frozen python experiments/active/2026-11-leak-handedness-cohort/scripts/posthoc.py
Reads the committed results/rules.csv and runs.csv; writes results/posthoc.txt. Written after P1 came out unresolved.
Section "reliability" added 2026-11-16 in response to PR #38 review S2 (still post hoc; no new data, no new runs):
split-half Lambda, the unnormalised a_L - a_R difference, and composition after regressing out a0_R - a0_L.
"""
from pathlib import Path

import numpy as np
import polars as pl
from scipy.stats import spearmanr

EXP = Path(__file__).resolve().parents[1]
r = pl.read_csv(EXP / "results/rules.csv").sort("rule")
runs = pl.read_csv(EXP / "results/runs.csv")
out = ["# POST HOC, not registered. Cohort C, 77 rules."]
lam = r["lam"].to_numpy()
out.append(f"Lambda: mean {lam.mean():+.3f}, sd {lam.std(ddof=1):.3f}, quartiles {np.quantile(lam, 0.25):+.3f} / {np.quantile(lam, 0.75):+.3f}, "
           f"min {lam.min():+.3f}, max {lam.max():+.3f}; |Lambda| > 0.4 in {int((np.abs(lam) > 0.4).sum())} rules")
sd = (runs.filter((pl.col("cohort") == "C") & pl.col("ef").is_in([0.3, 0.5]))
      .group_by(["rule", "arm", "ef"]).agg(pl.col("early_a").std())["early_a"].median())
dmed = float(np.median(r["delta_R"].to_numpy()))
out.append(f"median within-rule per-seed sd of early a at EF 0.3/0.5: {sd:.4f}; median Delta_R {dmed:.3f}; "
           f"implied seed noise on one rule's Lambda ~ {sd / 2 / dmed:.3f} (sd/sqrt(4)/Delta, x sqrt(2) arms, / sqrt(2) EFs)")
fr = np.array([s.count("R") / len(s) for s in r["rule"]])
rho = spearmanr(lam, fr)
out.append(f"Spearman(Lambda, fraction of R letters) = {rho.statistic:+.3f}, p = {rho.pvalue:.2g} (one of several looks; uncorrected)")
for lo, hi in [(0, 0.45), (0.45, 0.55), (0.55, 1.01)]:
    m = (fr >= lo) & (fr < hi)
    out.append(f"  R fraction in [{lo:.2f}, {min(hi, 1):.2f}): n {m.sum()}, median Lambda {np.median(lam[m]):+.3f}, Lambda > 0 in {int((lam[m] > 0).sum())}")
for pre in ("RLLL", "RRRR"):
    m = np.array([s.startswith(pre) for s in r["rule"]])
    out.append(f"  prefix {pre}: n {m.sum()}, median Lambda {np.median(lam[m]):+.3f}, Lambda > 0 in {int((lam[m] > 0).sum())}")

# --- reliability (added 2026-11-16, review S2; post hoc) ---
# Lambda recomputed from two disjoint seed halves at EF 0.3/0.5, keeping each rule's committed a0_R, a0_L, Delta_R, Delta_L.
out.append("# reliability (added 2026-11-16 for review S2; post hoc, same committed data)")
c = (runs.filter((pl.col("cohort") == "C") & pl.col("ef").is_in([0.3, 0.5]))
     .with_columns(pl.col("spec").str.split(":").list.last().str.slice(-2).cast(pl.Int64).alias("seed")))
base = r.select(["rule", "a0_R", "a0_L", "delta_R", "delta_L", "lam"])


def lam_from(seeds: list[int]) -> np.ndarray:
    m = (c.filter(pl.col("seed").is_in(seeds) & pl.col("early_a").is_not_nan())
         .group_by(["rule", "arm", "ef"]).agg(pl.col("early_a").mean().alias("a"))
         .pivot(on="arm", index=["rule", "ef"], values="a")
         .join(base, on="rule")
         .with_columns(((pl.col("R") - pl.col("a0_R")) / pl.col("delta_R") - (pl.col("L") - pl.col("a0_L")) / pl.col("delta_L")).alias("d"))
         .group_by("rule").agg(pl.col("d").mean()).sort("rule"))
    return m["d"].to_numpy()


for h1, h2 in [([1, 2], [3, 4]), ([1, 3], [2, 4]), ([1, 4], [2, 3])]:
    x1, x2 = lam_from(h1), lam_from(h2)
    rr = float(np.corrcoef(x1, x2)[0, 1])
    sb = 2 * rr / (1 + rr)
    noise = float(np.std(x1 - x2, ddof=1) / 2)  # sd of (half1 - half2)/2 ~ noise sd on the full-seed mean
    out.append(f"split-half seeds {h1} vs {h2}: r = {rr:.3f} (Spearman-Brown full-seed reliability {sb:.3f}); "
               f"implied seed noise on full Lambda ~ {noise:.3f} vs between-rule sd {lam.std(ddof=1):.3f}")
raw = (c.filter(pl.col("early_a").is_not_nan()).group_by(["rule", "arm"]).agg(pl.col("early_a").mean().alias("a"))
       .pivot(on="arm", index="rule", values="a").sort("rule"))
draw = (raw["L"] - raw["R"]).to_numpy()
assert raw["rule"].to_list() == r["rule"].to_list()
hs = []
for h in ([1, 2], [3, 4]):
    q = (c.filter(pl.col("seed").is_in(h) & pl.col("early_a").is_not_nan()).group_by(["rule", "arm"])
         .agg(pl.col("early_a").mean().alias("a")).pivot(on="arm", index="rule", values="a").sort("rule"))
    hs.append((q["L"] - q["R"]).to_numpy())
out.append(f"unnormalised abar_L - abar_R (EF 0.3/0.5 mean): between-rule sd {draw.std(ddof=1):.4f}; "
           f"split-half seed noise ~ {np.std(hs[0] - hs[1], ddof=1) / 2:.4f}; "
           f"Spearman with R fraction {spearmanr(draw, fr).statistic:+.3f} (sign flips: L - R)")
off = (r["a0_R"] - r["a0_L"]).to_numpy()
X = np.column_stack([np.ones_like(off), off])
beta, *_ = np.linalg.lstsq(X, lam, rcond=None)
res = lam - X @ beta
r2 = 1 - res.var() / lam.var()
rp = spearmanr(res, fr)
out.append(f"Lambda regressed on a0_R - a0_L: R^2 {r2:.3f}; Spearman(residual, R fraction) = {rp.statistic:+.3f}, p = {rp.pvalue:.2g}")
out.append(f"Spearman(|Lambda|, min(Delta_R, Delta_L)) = {spearmanr(np.abs(lam), np.minimum(r['delta_R'], r['delta_L'])).statistic:+.3f} "
           "(noise is largest where Delta is small, so the median-Delta figure above understates it for those rules)")
(EXP / "results/posthoc.txt").write_text("\n".join(out) + "\n")
print("\n".join(out))
