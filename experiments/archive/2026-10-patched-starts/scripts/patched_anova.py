"""Within-rule vs between-rule scatter of fitted exponents.

Each of 40 core rules was run from 12 random 5x5 starting patches. If every
rule had the same true exponent, the spread of per-rule means would be just
what within-rule noise predicts (sd_within / sqrt(12)). One-way ANOVA tests
that; the intraclass correlation says what share of the total variance is
genuinely between rules.
"""
import json
import sys

import numpy as np
import polars as pl
from scipy import stats

sys.path.insert(0, "experiments/_lib")
import analyse_probe as ap  # noqa: E402

ap.KLO, ap.KHI = 20, 26
runs = ap.per_rule(pl.read_csv("experiments/archive/2026-10-patched-starts/results/patched.csv")).with_columns(
    base=pl.col("rule").str.split("@").list.first())
plain = pl.read_csv("experiments/archive/2026-10-probe-growth-census/results/probe_summary.csv").select(pl.col("rule").alias("base"), pl.col("alpha_w").alias("plain_w"), pl.col("alpha_rg").alias("plain_rg"))

# Drop runs whose fate changed (e.g. a patch that sends the ant onto a highway
# or into a tether): keep runs within the core band.
kept = runs.filter(pl.col("alpha_w").is_between(0.25, 0.42))
out = {"runs": runs.height, "kept": kept.height, "rules": kept["base"].n_unique()}
for k in ["alpha_w", "alpha_rg", "a"]:
    groups = [g[k].to_numpy() for _, g in kept.group_by("base") if g.height >= 6]
    F, p = stats.f_oneway(*groups)
    sw = np.sqrt(np.mean([g.var(ddof=1) for g in groups]))
    means = np.array([g.mean() for g in groups])
    m = np.mean([len(g) for g in groups])
    sb2 = max(means.var(ddof=1) - sw ** 2 / m, 0.0)
    icc = sb2 / (sb2 + sw ** 2)
    out[k] = {"sd_within": round(float(sw), 4), "sd_of_rule_means": round(float(means.std(ddof=1)), 4),
              "sd_between_true": round(float(np.sqrt(sb2)), 4), "icc": round(float(icc), 3),
              "F": round(float(F), 2), "p": float(p), "grand_mean": round(float(means.mean()), 4),
              "rule_means_range": [round(float(means.min()), 4), round(float(means.max()), 4)]}
j = kept.group_by("base").agg(pl.col("alpha_rg").mean().alias("patched_rg"), pl.col("alpha_w").mean().alias("patched_w")).join(plain, on="base")
out["plain_vs_patched_corr_rg"] = round(float(np.corrcoef(j["plain_rg"], j["patched_rg"])[0, 1]), 3)
out["plain_vs_patched_corr_w"] = round(float(np.corrcoef(j["plain_w"], j["patched_w"])[0, 1]), 3)
json.dump(out, open("experiments/archive/2026-10-calib-instrument-calibration/results/calib_patched.json", "w"), indent=1)
print(json.dumps(out, indent=1))
