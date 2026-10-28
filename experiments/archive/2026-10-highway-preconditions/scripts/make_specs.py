"""Spec files for highway_preconditions_scan.

highway_specs.txt: confirmed census highways (confirmed_v2.csv, confirmed_1B.csv), primitive rules,
`RULE PERIOD DX DY ONSET` in input file order. control_specs.txt: the first 20 primitive `budget` rows of
sweep_v2.csv (README C4). Run from anywhere: uv run experiments/archive/2026-10-highway-preconditions/scripts/make_specs.py
"""
from pathlib import Path

import polars as pl

ROOT = Path(__file__).resolve().parents[4]
CENSUS = ROOT / "experiments/archive/2026-10-census-sweeps/results"
OUT = Path(__file__).resolve().parents[1] / "results"


def primitive(r: str) -> bool:
    n = len(r)
    return not any(n % p == 0 and r[:p] * (n // p) == r for p in range(1, n))


hw = pl.concat([pl.read_csv(CENSUS / f, infer_schema_length=None) for f in ("confirmed_v2.csv", "confirmed_1B.csv")])
hw = hw.filter(pl.col("confirmed") & pl.col("rule").map_elements(primitive, return_dtype=pl.Boolean))
lines = [f"{r['rule']} {r['period']} {r['dx']} {r['dy']} {r['onset']}" for r in hw.iter_rows(named=True)]
(OUT / "highway_specs.txt").write_text("\n".join(lines) + "\n")

sw = pl.read_csv(CENSUS / "sweep_v2.csv", infer_schema_length=None)
ctrl = sw.filter((pl.col("stop") == "budget") & pl.col("rule").map_elements(primitive, return_dtype=pl.Boolean)).head(20)
(OUT / "control_specs.txt").write_text("\n".join(ctrl["rule"]) + "\n")
print(len(lines), "highway specs;", ctrl.height, "control rules")
