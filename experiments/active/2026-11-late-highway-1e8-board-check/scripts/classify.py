"""Score the rechecks against the frozen criterion in README.md (written before the runs).
A rule is confirmed on a board iff its recheck reports the census period, dx, dy and onset exactly.
uv run --frozen experiments/active/2026-11-late-highway-1e8-board-check/scripts/classify.py > .../results/classify.txt
"""
from pathlib import Path

import polars as pl

ROOT = Path(__file__).resolve().parents[4]
EXP = Path(__file__).resolve().parents[1]
KEY = ["period", "dx", "dy", "onset"]
INT = {k: pl.Int64 for k in KEY + ["steps", "width", "height"]}

census = pl.read_csv(EXP / "results/census_rows.csv").cast(INT, strict=False)
ctrl = pl.read_csv(ROOT / "experiments/archive/2026-10-late-highway-board-check/results/control_65536.csv",
                   infer_schema_length=None).cast(INT, strict=False).filter(pl.col("rule") == "RRLRLR")
expected = pl.concat([census.select("rule", *KEY, "decade"),
                      ctrl.select("rule", *KEY).with_columns(decade=pl.lit("control"))])


def load(board: int) -> pl.DataFrame:
    files = sorted((EXP / f"results/recheck_{board}").glob("*.csv"))
    if not files:
        return None
    df = pl.concat([pl.read_csv(f, infer_schema_length=None).cast(INT, strict=False) for f in files], how="vertical_relaxed")
    return df.select("rule", "stop", "steps", *[pl.col(k).alias(f"{k}_{board}") for k in KEY],
                     pl.col("width").alias(f"w_{board}"), pl.col("height").alias(f"h_{board}")).drop("stop", "steps")


out = expected.sort("rule")
for board in (65536, 32768):
    got = load(board)
    if got is None:
        print(f"no rechecks on {board} yet")
        continue
    out = out.join(got, on="rule", how="left")
    same = pl.all_horizontal([pl.col(k).eq_missing(pl.col(f"{k}_{board}")) for k in KEY])
    out = out.with_columns(pl.when(pl.col(f"onset_{board}").is_null() & pl.col(f"w_{board}").is_null())
                           .then(pl.lit("missing")).when(same).then(pl.lit("confirmed")).otherwise(pl.lit("differs"))
                           .alias(f"status_{board}"))
with pl.Config(tbl_rows=30, tbl_width_chars=220, tbl_cols=30):
    print(out)
    if "status_65536" in out.columns:
        print(out.group_by("decade", "status_65536").len().sort("decade", "status_65536"))
if "status_65536" not in out.columns:
    raise SystemExit("primary rechecks missing")
c = out.filter(pl.col("rule") == "RRLRLR")["status_65536"][0]
print(f"control RRLRLR on tiled 65536: {c}")
cen = out.filter(pl.col("decade") != "control")
ok = cen.filter(pl.col("status_65536") == "confirmed")
print(f"confirmed on 65536: {ok.height} of {cen.height} (found-by-1e9-rerun binning: {ok.height}/854 = {ok.height / 854:.2%}); "
      f"by onset in (1e8,1e9]: {ok.filter(pl.col('decade') == '(1e8,1e9]').height}")
print("not confirmed:", cen.filter(pl.col("status_65536") != "confirmed")["rule"].to_list())
