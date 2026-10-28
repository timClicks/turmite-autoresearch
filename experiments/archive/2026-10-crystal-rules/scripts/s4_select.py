# /// script
# dependencies = ["polars"]
# ///
"""Select the filled-box rules with Gv==2 or a lone highway on their own ground (inputs for the grid-level crystal score)."""
from pathlib import Path
import polars as pl

root = Path(__file__).resolve().parents[1]
df = pl.read_csv(root / "results" / "s4_census.csv").with_columns(
    filled=(pl.col("steps_per_visited") < 10) & (pl.col("visited_over_bbox") >= 0.9) & (~pl.col("left_board")),
    hw=((pl.col("lone_escape_mask") // (2 ** pl.col("Gc"))) % 2 == 1),
)
s = df.filter(pl.col("filled") & ((pl.col("Gv") == 2) | pl.col("hw")))
print("\n".join(s["rule"].to_list()))
