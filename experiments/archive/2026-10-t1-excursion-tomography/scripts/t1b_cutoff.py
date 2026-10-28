"""Descriptive T1b cutoff follow-up; recipe and predictions in ../README.md."""
from pathlib import Path
import hashlib
import json
import subprocess

import numpy as np
import polars as pl
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[4]
EXP = Path(__file__).resolve().parents[1]
RES = EXP / "results"
SEED = 20261014  # No random operations in this analysis.
inputs = [RES / "t1b_windows.csv", RES / "t1b_bins.csv"]
w, bins = [pl.read_csv(p) for p in inputs]
assert w["conserved"].all()
escaped_rows = w.filter(pl.col("escaped")).height
w = w.filter(~pl.col("escaped"))
rows = []
for (spec, k), g in bins.group_by(["spec", "k"], maintain_order=True):
    g = g.sort("bin")
    total = int(g["count"].sum())
    target, cumulative = 0.999 * total, 0
    for b, count in g.select("bin", "count").iter_rows():
        if cumulative + count >= target:
            log_lo = b * np.log(2)
            log_hi = (b + 1) * np.log(2)
            log_q = log_lo + (target - cumulative) / count * np.log(2)
            rows.append(dict(spec=spec, k=k, completed_count=total,
                             lnL999=float(log_q), lnL999_lo=float(log_lo),
                             lnL999_hi=float(log_hi)))
            break
        cumulative += count
f = pl.DataFrame(rows).join(w, on=["spec", "k"], how="inner", validate="1:1").with_columns(
    (0.5 * (pl.col("area") / np.pi).log()).alias("lnR"),
    pl.col("kappa").log().alias("lnkappa"),
    (pl.col("part_open") / pl.col("interior_steps")).alias("open_share"),
).with_columns((pl.col("lnL999") - pl.col("lnR")).alias("ln_ratio"),
               (pl.col("lnL999_lo") - pl.col("lnR")).alias("ln_ratio_lo"),
               (pl.col("lnL999_hi") - pl.col("lnR")).alias("ln_ratio_hi"))
p = f.filter(pl.col("spec").str.contains("@" )).with_columns(
    pl.col("spec").str.split("@").list.get(0).alias("rule"),
    pl.col("spec").str.split("@").list.get(1).cast(pl.Int64).alias("seed"))
p = p.sort("rule", "seed", "k")
p.write_csv(RES / "t1b_cutoff_seeds.csv")
cols = ["ln_ratio", "ln_ratio_lo", "ln_ratio_hi", "lnkappa", "open_share"]
r = p.group_by("rule", "k").agg(
    pl.len().alias("n_seeds"),
    *[pl.col(c).mean().alias(c + "_mean") for c in cols],
    *[pl.col(c).std(ddof=1).alias(c + "_sd") for c in cols],
).sort("rule", "k")
r.write_csv(RES / "t1b_cutoff_rules.csv")
summary = {}
for k in (22, 25):
    a = r.filter(pl.col("k") == k)
    clean = p.filter((pl.col("k") == k) & (pl.col("open_share") <= 0.10))
    clean = clean.group_by("rule").agg(pl.col("ln_ratio").mean(), pl.col("lnkappa").mean())
    summary[str(k)] = dict(n_rules=a.height, min_seeds=a["n_seeds"].min(), max_seeds=a["n_seeds"].max(),
        rho=float(spearmanr(a["ln_ratio_mean"], a["lnkappa_mean"]).statistic),
        median_between_seed_sd=float(a["ln_ratio_sd"].median()),
        median_ratio=float(np.exp(a["ln_ratio_mean"].median())),
        median_open_share=float(a["open_share_mean"].median()),
        sensitivity_n_rules=clean.height,
        sensitivity_n_seeds=p.filter((pl.col("k") == k) & (pl.col("open_share") <= 0.10)).height,
        sensitivity_rho=float(spearmanr(clean["ln_ratio"], clean["lnkappa"]).statistic))
controls = {}
for kind in ("rotor", "rw"):
    c = f.filter(pl.col("spec").str.starts_with(kind) & (pl.col("k") == 25))
    controls[kind] = dict(n=c.height, kappa_mean=c["kappa"].mean(),
                          kappa_sd=c["kappa"].std(ddof=1))
out = dict(commit=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
    analysis_seed=SEED, command="uv run experiments/archive/2026-10-t1-excursion-tomography/scripts/t1b_cutoff.py",
    inputs={str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},
    script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    conserved=True, excluded_escaped_windows=escaped_rows, controls=controls, windows=summary,
    caveats=["Completed excursions only; open-time filtering cannot correct censoring.",
             "Binned quantile has one-octave resolution; log interpolation is approximate.",
             "Ratio still includes radius; this is not a size-controlled causal test."])
(RES / "t1b_cutoff.json").write_text(json.dumps(out, indent=2) + "\n")
print(json.dumps(out, indent=2))
