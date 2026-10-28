# /// script
# dependencies = ["polars", "numpy"]
# ///
"""W5 specs (README, log: 'W5: implementation addendum'): pool-192 x patched seeds 601..606; pool-192 blank board;
census (non-bursty) minus pool blank board; controls rotor:1..6, pw:0.5:1..6, rw:1..6. Writes results/w5_specs.txt.
usage (repo root): uv run experiments/archive/2026-10-kappa-rule-space/scripts/w5_specs.py"""
from pathlib import Path
import polars as pl
EXP = Path(__file__).resolve().parents[1]
pool = sorted(pl.read_csv(EXP / "results" / "rules_pool.csv")["base"].to_list())
cen = pl.read_csv(EXP / "results" / "rules_census.csv").filter(~pl.col("in_pool"))["rule"].to_list()
lines = ([f"{r}@{s}" for r in pool for s in range(601, 607)] + pool + sorted(cen)
         + [f"rotor:{s}" for s in range(1, 7)] + [f"pw:0.5:{s}" for s in range(1, 7)] + [f"rw:{s}" for s in range(1, 7)])
(EXP / "results" / "w5_specs.txt").write_text("\n".join(lines) + "\n")
print(len(pool), "pool;", len(cen), "census-minus-pool;", len(lines), "specs")
