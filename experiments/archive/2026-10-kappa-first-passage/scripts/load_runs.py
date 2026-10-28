# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "polars"]
# ///
"""Load sampler outputs (bands/status/hist/pairs) into polars frames and compute run-level quantities.

    uv run experiments/archive/2026-10-kappa-first-passage/scripts/load_runs.py RESULTS_DIR [PAIRS_DIR]
prints a feasibility/readiness summary (does not choose models).
"""
from __future__ import annotations

import sys
from pathlib import Path

import polars as pl


def load(res: Path, name: str) -> pl.DataFrame:
    files = sorted(res.glob(f"*.{name}.csv"))
    return pl.concat([pl.read_csv(f, null_values="NA") for f in files]) if files else pl.DataFrame()


def runs(res: Path) -> pl.DataFrame:
    b, s = load(res, "bands"), load(res, "status")
    b = b.with_columns(
        rule=pl.col("spec").str.split("@").list.first(),
        seed=pl.col("spec").str.split("@").list.last().cast(pl.Int64, strict=False),
        BS=pl.col("b_dep") / pl.col("steps"),
        kappa=(pl.col("b_dep") / pl.col("steps")) / (pl.col("perim_end") / pl.col("area_end")),
        unres_share=(pl.col("B_unresolved_overlap") + pl.col("I_unresolved_overlap")) / pl.col("steps"),
    )
    return b.join(s, on="spec")


if __name__ == "__main__":
    res = Path(sys.argv[1])
    r = runs(res)
    pl.Config.set_tbl_rows(200)
    pl.Config.set_tbl_cols(30)
    print(r.select("spec", "band", "reached_hi", "stop", "t_end", "steps", "BS", "kappa", "unres_share", "seconds").sort("spec", "band"))
    print(r.group_by("band").agg(pl.col("seconds").sum().alias("sec_sum_band_ignores_split"), pl.col("reached_hi").mean().alias("frac_reached")))
    print(r.group_by("spec").agg(pl.col("stop").first(), pl.col("t_final").first(), pl.col("seconds").first()).sort("spec"))
