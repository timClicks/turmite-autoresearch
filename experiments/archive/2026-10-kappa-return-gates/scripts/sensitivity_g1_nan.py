"""EXPLORATORY sensitivity (not part of the registered verdict): band 0 excluded 2 rules because 3 runs with 2-6 crossing
events had a NaN g1 null (a Poisson null draw with zero total). Recompute with those runs' g1 ignored (g1_events set to 0
for them only). Same frozen model, features, seeds, bootstrap and permutations otherwise."""
from pathlib import Path
import json, sys
import polars as pl
sys.path.insert(0, str(Path(__file__).resolve().parent))
import analyse_confirm as ac
EXP = ac.EXP
runs = pl.read_csv(EXP / "results/confirm_runs.csv", schema_overrides={"ext_boundary": pl.Int64, "hole_boundary": pl.Int64})
bad = pl.col("g1_null").is_nan() | pl.col("g1_obs").is_nan()
print("runs with NaN g1 among events>0:", runs.filter(bad & (pl.col("g1_events") > 0)).height)
runs = runs.with_columns(pl.when(bad).then(0).otherwise(pl.col("g1_events")).alias("g1_events"))
rules = pl.read_csv(EXP / "results/cohort.csv")["base"].to_list()
S = json.loads((EXP / "results/seed_count.json").read_text())["S_pred"]
out = {str(b): {k: v for k, v in ac.analyse_band(runs, rules, b, S).items() if k != "per_rule"} for b in (0, 1)}
(EXP / "results/sensitivity_g1_nan.json").write_text(json.dumps(out, indent=1) + "\n")
for b, r in out.items():
    print(b, {k: r.get(k) for k in ("n_rules_evaluable", "r2_baseline", "r2_with_gates", "delta_r2", "delta_ci95", "permutation_p", "band_pass", "reliability")})
