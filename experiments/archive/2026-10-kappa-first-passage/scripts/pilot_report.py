# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "scipy", "polars"]
# ///
"""Feasibility summary of the pilot (README stage 2). Reads results/pilot and scratch/pilot/pairs.
Nothing here selects a model: it reports runtime, resolution gates and whether the estimator pipeline runs.
    uv run experiments/archive/2026-10-kappa-first-passage/scripts/pilot_report.py
"""
import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import fpkernel  # noqa: E402
import load_runs  # noqa: E402

EXP = HERE.parent
res, pairs = EXP / "results" / "pilot", EXP / "scratch" / "pilot" / "pairs"
r = load_runs.runs(res)
out: dict = {"n_runs": r["spec"].n_unique(), "n_complete": int(r.filter(pl.col("stop") == "complete")["spec"].n_unique())}
out["seconds_per_run"] = dict(mean=float(r.unique("spec")["seconds"].mean()), max=float(r.unique("spec")["seconds"].max()))
out["t_final_max"] = int(r["t_final"].max())
out["unresolved_share_max"] = float(r["unres_share"].max())
out["pair_rows_max"] = int(r.unique("spec")["pair_rows"].max())
out["overflowed_total"] = int(r.unique("spec")["overflowed"].sum())
out["depth_decreases_total"] = int(r.unique("spec")["depth_decreases"].sum())
out["lipschitz_violations_total"] = int(r.unique("spec")["lipschitz_violations"].sum())
out["seg_overlap_equals_steps"] = bool((r["seg_overlap"] == r["steps"]).all())

rows = []
for rule in sorted(r["rule"].unique().to_list()):
    rr = r.filter(pl.col("rule") == rule)
    files = sorted(str(p) for p in pairs.glob(f"{rule}_*.pairs.csv"))
    df = fpkernel.read_pairs(files)
    deep = df.filter(((pl.col("m") == 7) | (pl.col("nm") == 7)) & pl.col("nm").is_not_null())
    row = dict(rule=rule, n_seeds=rr["spec"].n_unique(), deep_segments=int(deep["n"].sum()),
               skipped=int(df["skipped"].sum()), jumps=int(df["jumps"].sum()),
               bs_band=[float(rr.filter(pl.col("band") == b)["BS"].mean()) for b in range(3)],
               bs_band_sd=[float(rr.filter(pl.col("band") == b)["BS"].std()) for b in range(3)],
               kappa_band=[float(rr.filter(pl.col("band") == b)["kappa"].mean()) for b in range(3)])
    for lvl in (0, 1, 2):
        f = fpkernel.fit(df, level=lvl, floor=20, bands=[0, 1])
        row[f"M{lvl}"] = {k: f.get(k) for k in ("status", "n_states", "ED", "ET", "pred_BS", "deep_share", "dead_end_mass", "entry_lost", "unreachable_states")}
    rows.append(row)
out["rules"] = rows
(EXP / "results" / "pilot_summary.json").write_text(json.dumps(out, indent=2))
print(json.dumps({k: v for k, v in out.items() if k != "rules"}, indent=2))
for row in rows:
    print(row["rule"], "deep", row["deep_segments"], "BS", np.round(row["bs_band"], 3), "pred(M0,M1,M2)",
          [None if row[f"M{l}"].get("pred_BS") is None else round(row[f"M{l}"]["pred_BS"], 3) for l in range(3)],
          "status", [row[f"M{l}"]["status"] for l in range(3)], "deep_share(M0)", row["M0"].get("deep_share"))
