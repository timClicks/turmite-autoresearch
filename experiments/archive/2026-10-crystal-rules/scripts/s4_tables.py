# /// script
# dependencies = ["polars"]
# ///
"""S4 tables from results/s4_census.csv (made by examples/crystal_s4.rs). usage: s4_tables.py"""
from pathlib import Path
import polars as pl

root = Path(__file__).resolve().parents[1]
df = pl.read_csv(root / "results" / "s4_census.csv")
df = df.with_columns(
    filled=(pl.col("steps_per_visited") < 10) & (pl.col("visited_over_bbox") >= 0.9) & (~pl.col("left_board")),
    hw_on_own_ground=((pl.col("lone_escape_mask") // (2 ** pl.col("Gc"))) % 2 == 1),
    any_lone_hw=pl.col("lone_escape_mask") > 0,
    ground_dom=pl.col("ground_frac") >= 0.5,
)
print("census rules:", df.height, " left 2048 board in 2^22:", int(df["left_board"].sum()))
print("\nfilled box (steps/visited<10, visited/bbox>=0.9):", int(df["filled"].sum()))
print(df.filter(pl.col("filled")).group_by(["Gv", "Gc", "hw_on_own_ground"]).agg(pl.len().alias("rules"), pl.col("ground_frac").median().alias("med_ground_frac"), pl.col("max_visits").median().alias("med_maxv")).sort("rules", descending=True).head(25))
print("\nlone-ant highway on SOME uniform colour g: ", int(df["any_lone_hw"].sum()), "rules;  of which filled:", int((df["any_lone_hw"] & df["filled"]).sum()))
print("\nfilled & hw_on_own_ground, by (Gv, Gc) and n:")
print(df.filter(pl.col("filled") & pl.col("hw_on_own_ground")).group_by(["Gv", "Gc"]).agg(pl.len().alias("rules"), pl.col("n").min().alias("nmin"), pl.col("n").max().alias("nmax")).sort("rules", descending=True))
print("\nExamples filled & hw_on_own_ground & ground_frac<0.95 (crystal candidates):")
c = df.filter(pl.col("filled") & pl.col("hw_on_own_ground") & ~(pl.col("ground_frac") > 0.95))
print(c.height); print(c.select("rule", "Gv", "Gc", "ground_frac", "steps_per_visited", "max_visits", "lone_escape_mask").head(40))
