"""Pilot analysis: coverage, split-seed reliability of the two gate features, seed-count rule.
Deliberately does NOT regress occupation on gate features: the pilot only fixes the confirmation design.
"""
from pathlib import Path
import hashlib, json, subprocess, sys
import numpy as np, polars as pl
from scipy.stats import spearmanr
sys.path.insert(0, str(Path(__file__).resolve().parent))
import rg_lib

ROOT = Path(__file__).resolve().parents[4]
EXP = Path(__file__).resolve().parents[1]
runs = pl.read_csv(EXP / "results/pilot_runs.csv", schema_overrides={"ext_boundary": pl.Int64, "hole_boundary": pl.Int64})
rules = pl.read_csv(EXP / "results/cohort.csv")["base"].to_list()
seeds = sorted(runs["seed"].unique().to_list())
A, B = seeds[0::2], seeds[1::2]
rep = dict(bands={})
sb = lambda r, k: k * r / (1 + (k - 1) * r)
S_need = {}
for band in (0, 1):
    allv = rg_lib.table(runs, rules, band)
    ta, tb = rg_lib.table(runs, rules, band, A), rg_lib.table(runs, rules, band, B)
    out = dict(n_rules_all_8_seeds_reached=int((allv["n_seeds"] == 8).sum()),
               coverage_g1_g2_defined_pooled8=int(allv.filter(pl.col("g1").is_not_nan() & pl.col("g2").is_not_nan()).height))
    for f in ("g1", "g2", "y"):
        m = ta[f].is_not_nan() & tb[f].is_not_nan()
        r = float(spearmanr(ta.filter(m)[f], tb.filter(m)[f]).statistic) if m.sum() > 3 else float("nan")
        out[f] = dict(n_rules=int(m.sum()), split_half_spearman_4v4=r, projected={str(S): sb(r, S / 4) for S in (8, 16, 32, 64)})
    out["median_events_per_run"] = float(runs.filter(pl.col("band") == band)["g1_events"].median())
    out["median_bins_per_run"] = float(runs.filter(pl.col("band") == band)["g1_bins"].median())
    out["reclass_share_median"] = float(allv["reclass_share"].median())
    out["hole_boundary_fraction_median"] = float((runs.filter((pl.col("band") == band) & pl.col("ext_boundary").is_not_null()).select(pl.col("hole_boundary") / (pl.col("hole_boundary") + pl.col("ext_boundary"))).to_series().median()))
    rep["bands"][str(band)] = out
    for f in ("g1", "g2"):
        for S in (8, 16, 32, 64):
            S_need.setdefault(S, []).append(out[f]["projected"][str(S)] >= 0.7)
S_pred = next((S for S in (8, 16, 32, 64) if all(S_need[S])), None)
cov_ok = all(rep["bands"][b]["coverage_g1_g2_defined_pooled8"] >= 20 for b in ("0", "1"))
rep.update(S_pred=S_pred, coverage_gate_ge_20_of_24_at_both_bands=cov_ok, reliability_gate="PASS" if S_pred else "FAIL (no S<=64 projects both features to >=0.7 at both bands)",
           pilot_seeds=seeds, halves=dict(A=A, B=B), git_commit=subprocess.check_output(["git", "rev-parse", "HEAD"], text=True, cwd=ROOT).strip(),
           input_sha256=hashlib.sha256((EXP / "results/pilot_runs.csv").read_bytes()).hexdigest())
(EXP / "results/pilot_analysis.json").write_text(json.dumps(rep, indent=2) + "\n")
if S_pred and cov_ok:
    (EXP / "results/seed_count.json").write_text(json.dumps(dict(S_pred=S_pred, rule="smallest S in {8,16,32,64} with Spearman-Brown projection >=0.7 for g1 and g2 at both bands", source="results/pilot_analysis.json")) + "\n")
print(json.dumps(rep, indent=1))
