"""Known-answer check of the renewal estimator on the mean-field walker (registered in NOTEBOOK.md).

kappa_inst = (E[D]/(E[D]+E[T])) / g, E[D] = complete-contained B steps/count, E[T] = entered I steps/count,
g = sum_pa/steps.  kappa_direct = (b_dep/steps)/g.  Expected values by construction: 1.
Input: results/meanfield_renewal.csv from
  target/release/examples/kappa_tail_budget_meanfield 2026101801 16 536870912 16384-17408,65536-69632,262144-278528 <csv> 2
  uv run experiments/archive/2026-10-kappa-tail-budget/scripts/meanfield_renewal.py
"""
import hashlib, json, subprocess
from pathlib import Path
import numpy as np
import polars as pl

ROOT = Path(__file__).resolve().parents[4]
EXP = Path(__file__).resolve().parents[1]
src = EXP / "results/meanfield_renewal.csv"
df = pl.read_csv(src)
assert df["reached_hi"].min() == 1 and df["unresolved_overlap"].sum() == 0
df = df.with_columns(
    g=pl.col("sum_pa") / pl.col("steps"),
    ED=pl.col("b_complete_steps") / pl.col("b_complete_n"),
    ET=pl.col("t_entered_steps") / pl.col("t_entered_n"),
).with_columns(
    f_pred=pl.col("ED") / (pl.col("ED") + pl.col("ET")),
    f_dir=pl.col("b_dep") / pl.col("steps"),
).with_columns(
    kappa_inst=pl.col("f_pred") / pl.col("g"),
    kappa_direct=pl.col("f_dir") / pl.col("g"),
    ED_pred=1 / (1 - pl.col("g")), ET_pred=1 / pl.col("g"),
).with_columns(
    ED_rel=pl.col("ED") / pl.col("ED_pred") - 1, ET_rel=pl.col("ET") / pl.col("ET_pred") - 1,
)
out = {"command": "see docstring", "n_seeds": df["seed"].n_unique(),
       "input_sha256": hashlib.sha256(src.read_bytes()).hexdigest(),
       "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True, cwd=ROOT).strip(), "bands": {}}
ok = True
for b in sorted(df["band"].unique()):
    d = df.filter(pl.col("band") == b)
    r = {}
    for c in ("g", "ED", "ET", "kappa_inst", "kappa_direct", "ED_rel", "ET_rel", "b_complete_n"):
        v = d[c].to_numpy()
        r[c] = {"mean": float(v.mean()), "sd": float(v.std(ddof=1)), "se": float(v.std(ddof=1) / np.sqrt(len(v)))}
    r["pass"] = bool(abs(r["kappa_inst"]["mean"] - 1) <= 0.02 and r["kappa_inst"]["sd"] <= 0.02
                     and abs(r["kappa_direct"]["mean"] - 1) <= 0.01
                     and abs(r["ED_rel"]["mean"]) <= 0.03 and abs(r["ET_rel"]["mean"]) <= 0.03)
    ok &= r["pass"]
    out["bands"][int(b)] = r
out["all_pass"] = bool(ok)
(EXP / "results/meanfield_renewal.json").write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
print(json.dumps(out, indent=1))
