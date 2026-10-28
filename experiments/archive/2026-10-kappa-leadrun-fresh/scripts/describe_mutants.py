# /// script
# dependencies = ["polars"]
# ///
"""POST HOC descriptive breakdown of Part B pairs (written after reading analyse_mutants.py output; not a registered test).
Reads results/mutant_pairs.csv, writes results/mutants_describe.txt.
usage (repo root): uv run experiments/archive/2026-10-kappa-leadrun-fresh/scripts/describe_mutants.py"""
from pathlib import Path
import polars as pl

EXP = Path(__file__).resolve().parents[1]
pl.Config.set_tbl_rows(50)
p = pl.read_csv(EXP / "results/mutant_pairs.csv")
agg = dict(n=pl.len(), mean_d=pl.col("d").mean(), sd_d=pl.col("d").std(), mean_dA=pl.col("dA").mean())
parts = ["# POST HOC descriptive; cmd: uv run experiments/archive/2026-10-kappa-leadrun-fresh/scripts/describe_mutants.py",
         "## arm E by dlead (capped at 6)", str(p.filter(pl.col("arm") == "E").group_by("dlead").agg(**agg).sort("dlead")),
         "## by arm x base_lead", str(p.group_by("arm", "base_lead").agg(**agg).sort("arm", "base_lead")),
         "## residual after d - 1.037*dA (pooled c from analyse_mutants) by arm",
         str(p.with_columns(r=pl.col("d") - 1.037 * pl.col("dA")).group_by("arm").agg(n=pl.len(), mean_r=pl.col("r").mean(), mean_dlead=pl.col("dlead").mean()).sort("arm"))]
(EXP / "results/mutants_describe.txt").write_text("\n".join(parts) + "\n")
print("\n".join(parts))
