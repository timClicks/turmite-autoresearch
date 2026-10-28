"""Select the 24-rule cohort from pre-existing labels only (no gate statistic, no new ant outcome).

Labels, both from experiments/archive/2026-10-kappa-rule-space/results/rules_pool.csv (192 rules, no missing values):
  crust       iff pool c >= 0.60  (the layers-experiment threshold; pool c is bimodal, gap 0.586 -> 0.609)
  stationary  iff |pool g_k| < 0.05  (same definition as the field-age cohort audit)
6 rules per (crust, stationary) cell, taking the first 6 by sha256("return-gates-cohort-v1|"+rule).
Missing labels: none exist; the script asserts that and would abort rather than impute.
"""
from pathlib import Path
import hashlib, json, subprocess
import polars as pl

ROOT = Path(__file__).resolve().parents[4]
EXP = Path(__file__).resolve().parents[1]
SRC = ROOT / "experiments/archive/2026-10-kappa-rule-space/results/rules_pool.csv"
SALT = "return-gates-cohort-v1|"
PER_CELL = 6

d = pl.read_csv(SRC)
assert d.select(pl.col("c").is_null().any() | pl.col("g_k").is_null().any()).item() is False
d = d.with_columns(
    (pl.col("c") >= 0.60).alias("crust"),
    (pl.col("g_k").abs() < 0.05).alias("stationary"),
    pl.col("base").map_elements(lambda r: hashlib.sha256((SALT + r).encode()).hexdigest(), return_dtype=pl.String).alias("key"),
)
parts = []
for crust in (True, False):
    for stat in (True, False):
        cell = d.filter((pl.col("crust") == crust) & (pl.col("stationary") == stat)).sort("key")
        assert cell.height >= PER_CELL, (crust, stat, cell.height)
        parts.append(cell.head(PER_CELL))
cohort = pl.concat(parts).select("base", "crust", "stationary", "c", "g_k", "kappa", "key")
cohort.write_csv(EXP / "results/cohort.csv")
manifest = dict(
    command=f"uv run {Path(__file__).relative_to(ROOT).as_posix()}",
    git_commit=subprocess.check_output(["git", "rev-parse", "HEAD"], text=True, cwd=ROOT).strip(),
    input=str(SRC.relative_to(ROOT).as_posix()), input_sha256=hashlib.sha256(SRC.read_bytes()).hexdigest(),
    script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    cohort_sha256=hashlib.sha256((EXP / "results/cohort.csv").read_bytes()).hexdigest(),
    salt=SALT, per_cell=PER_CELL, pool_cell_sizes={f"crust={c},stationary={s}": d.filter((pl.col("crust") == c) & (pl.col("stationary") == s)).height for c in (True, False) for s in (True, False)},
    rules=cohort["base"].to_list(),
)
(EXP / "results/cohort_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
print(cohort)
