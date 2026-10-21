"""Classify census escapes with a highway as board fillers (escape footprint >= 0.99 of the board in both directions)
or not, and recompute the late-highway counts per decade. Post hoc rule, chosen after seeing the footprints (see README).
uv run experiments/2026-10-21-late-highway-board-check/scripts/classify.py > experiments/2026-10-21-late-highway-board-check/results/classify.txt
"""
from pathlib import Path

import polars as pl

ROOT = Path(__file__).resolve().parents[3]
H = ROOT / "experiments/2026-10-13-highways-unresolved-rules-1e10-1e11/results"
C = ROOT / "experiments/2026-10-13-census-sweeps/results"


def load(paths, grid, label):
    df = pl.concat([pl.read_csv(p, infer_schema_length=None) for p in paths], how="vertical_relaxed")
    df = df.with_columns(pl.col("onset", "width", "height", "period", "dx", "dy").cast(pl.Int64, strict=False))
    return df.filter(pl.col("onset").is_not_null()).with_columns(
        cohort=pl.lit(label), grid=pl.lit(grid),
        filler=(pl.col("width") >= 0.99 * grid) & (pl.col("height") >= 0.99 * grid),
        onset_over_2_31=pl.col("onset") / 2**31,
    )


late = pl.concat([
    load(sorted((H / "h1e10").glob("*.csv")), 32768, "(1e9,1e10]"),
    load(sorted((H / "h1e11").glob("*.csv")), 32768, "(1e10,1e11]"),
])
with pl.Config(tbl_rows=60, tbl_width_chars=160):
    print(late.sort("onset").select("cohort", "rule", "period", "dx", "dy", "onset", "onset_over_2_31", "width", "height", "filler"))
    print(late.group_by("cohort", "filler").agg(pl.len().alias("rules"), pl.col("onset").n_unique().alias("distinct_onsets")).sort("cohort", "filler"))

# Survivor denominators from the census notes: 807 rules entered (1e9,1e10], 732 entered (1e10,1e11].
for cohort, denom in [("(1e9,1e10]", 807), ("(1e10,1e11]", 732)]:
    c = late.filter(pl.col("cohort") == cohort)
    real = c.filter(~pl.col("filler"))
    print(f"{cohort}: {c.height} reported, {real.height} not board fillers -> {real.height / denom:.2%} of {denom} "
          f"(was {c.height / denom:.2%}); distinct onsets among real: {real['onset'].n_unique()}")

# Earlier census sweeps: same signature? Grid per file is not stored in the CSV; use the max footprint seen as the board.
for f in ["sweep_v2.csv", "sweep_1B.csv", "sweep_1B_extra.csv"]:
    df = pl.read_csv(C / f, infer_schema_length=None)
    g = int(max(df["width"].max(), df["height"].max()))
    hw = df.filter(pl.col("onset").is_not_null())
    fill = hw.filter((pl.col("width") >= 0.99 * g) & (pl.col("height") >= 0.99 * g))
    print(f"{f}: max footprint {g}; highways {hw.height}; with full-board footprint {fill.height}: {fill['rule'].to_list()[:10]}")
