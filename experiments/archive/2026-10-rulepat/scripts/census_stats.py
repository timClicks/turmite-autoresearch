# /// script
# dependencies = ["polars"]
# ///
"""census_stats.py : tests C1-C4 on results/census_scan.csv. Member = plateau>=0.5 & area/t>=0.05 & not escaped."""
import polars as pl
from pathlib import Path
R = Path(__file__).resolve().parents[1]
df = pl.read_csv(R / "results/census_scan.csv").with_columns(
    n=pl.col("rule").str.len_chars(), apt=pl.col("area") / pl.col("steps"))
df = df.with_columns(member=(pl.col("plateau") >= 0.5) & (pl.col("apt") >= 0.05) & ~pl.col("escaped"))
m = df.filter(pl.col("member"))
print("rules", df.height, "members", m.height, f"({m.height/df.height:.3%})")
print("by length:", df.group_by("n").agg(pl.col("member").sum().alias("members"), pl.len().alias("rules")).sort("n").rows())
print("escaped:", df["escaped"].sum())
print("C2 prefix RLL:", m.filter(pl.col("rule").str.starts_with("RLL")).height, "/", m.height,
      "; plateau_colour==2:", m.filter(pl.col("plateau_colour") == 2).height)
print("C3 prefix RLLLL:", m.filter(pl.col("rule").str.starts_with("RLLLL")).height)
print("mode_visits among members:", m.group_by("mode_visits").len().sort("mode_visits").rows())
print("plateau_colour among members:", m.group_by("plateau_colour").len().sort("plateau_colour").rows())
ms = set(m["rule"].to_list())
short = [r for r in ms if len(r) <= 11]
fam = [r for r in short if any(r + e in ms for e in ("R","L","RR","RL","LR","LL","RRR","RRL","RLR","RLL","LRR","LRL","LLR","LLL"))]
print(f"C4 members n<=11: {len(short)}; with a member extension of 1-3 letters: {len(fam)}")
print(m.sort(["n", "rule"]).select("rule", "mode_visits", "plateau", "plateau_colour", "apt", "long_alt_runs").head(60))
