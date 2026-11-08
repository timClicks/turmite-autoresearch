"""Write the recheck specs (RULE BUDGET, sorted by rule) for the late highways found by the 1e9 census rerun.
Source: rows of experiments/archive/2026-10-census-sweeps/results/sweep_1B.csv (16384 board) with an onset, i.e. the
12 rules of results/1B_highways.txt; budget = census onset + 1e8 (as B2 in 2026-10-late-highway-board-check).
Control RRLRLR (onset from the dense 65536 control in that experiment) is appended last.
uv run --frozen experiments/active/2026-11-late-highway-1e8-board-check/scripts/specs.py
"""
from pathlib import Path

import polars as pl

ROOT = Path(__file__).resolve().parents[4]
EXP = Path(__file__).resolve().parents[1]
C = ROOT / "experiments/archive/2026-10-census-sweeps/results"
B = ROOT / "experiments/archive/2026-10-late-highway-board-check/results"

census = pl.read_csv(C / "sweep_1B.csv", infer_schema_length=None)
hw = census.filter(pl.col("onset").is_not_null()).sort("rule")
listed = sorted((C / "1B_highways.txt").read_text().split())
assert hw["rule"].to_list() == listed, "census rows with onset differ from 1B_highways.txt"
G = 16384  # sweep_1B board (max footprint 16383 in the file; confirm.rs used 8192 and 16384)
hw = hw.with_columns(
    budget=pl.col("onset").cast(pl.Int64) + 100_000_000,
    filler=(pl.col("width") >= 0.99 * G) & (pl.col("height") >= 0.99 * G),
    decade=pl.when(pl.col("onset") > 100_000_000).then(pl.lit("(1e8,1e9]")).otherwise(pl.lit("(1e7,1e8]")),
)
hw.select("rule", "n", "steps", "period", "dx", "dy", "onset", "width", "height", "filler", "decade", "budget").write_csv(
    EXP / "results/census_rows.csv")
ctrl = pl.read_csv(B / "control_65536.csv").filter(pl.col("rule") == "RRLRLR").row(0, named=True)
lines = [f"{r} {b}" for r, b in zip(hw["rule"], hw["budget"])] + [f"RRLRLR {ctrl['onset'] + 100_000_000}"]
(EXP / "results/recheck_specs.txt").write_text("\n".join(lines) + "\n")
print(hw.select("rule", "period", "dx", "dy", "onset", "width", "height", "filler", "decade"))
print("fillers by frozen criterion:", hw["filler"].sum())
