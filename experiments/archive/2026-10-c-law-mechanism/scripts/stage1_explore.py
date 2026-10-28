# /// script
# dependencies = ["polars", "numpy"]
# ///
"""Stage 1 EXPLORATORY (post hoc, not registered): per-colour birth probability and toward/away-fresh fractions by lead.
usage: uv run experiments/archive/2026-10-c-law-mechanism/scripts/stage1_explore.py"""
from pathlib import Path

import numpy as np
import polars as pl

root = Path(__file__).resolve().parents[4]
out = root / "experiments/archive/2026-10-c-law-mechanism/results"
es = pl.read_csv(root / "experiments/archive/2026-10-edge-statistics/results/edgestats_sample.csv")
cen = pl.read_csv(root / "experiments/archive/2026-10-probe-growth-census/results/probe_summary.csv")
stat = set(cen.filter((pl.col("cls") == "blob") & (pl.col("c") > 0) & (pl.col("g_k").abs() < 0.05))["rule"].to_list())
lines = []


def say(s=""):
    print(s)
    lines.append(s)


def run0(r):
    k = 1
    while k < len(r) and r[k] == r[0]:
        k += 1
    return k


es = es.filter(pl.col("rule").is_in(list(stat))).with_columns(
    m=pl.col("rule").map_elements(run0, return_dtype=pl.Int64), n=pl.col("rule").str.len_chars())
# per rule: B total
B = es.group_by("rule").agg(B=pl.col("new_cells").sum())
es = es.join(B, on="rule").with_columns(
    toward=pl.when(pl.col("turn") == "R").then(pl.col("right_fresh")).otherwise(pl.col("left_fresh")),
    away=pl.when(pl.col("turn") == "R").then(pl.col("left_fresh")).otherwise(pl.col("right_fresh")))
say("check births == toward-fresh (turn side) per row: max |new - toward| / edge_steps = %.4f" %
    float(((es["new_cells"] - es["toward"]).abs() / es["edge_steps"].clip(lower_bound=1)).max()))
for m in (1, 2, 3, 4):
    sub = es.filter((pl.col("m") == m) & (pl.col("n") > m + 3) & (pl.col("colour") <= m + 2))
    nr = sub["rule"].n_unique()
    say(f"\nlead {m}: {nr} rules. per colour k: share of edge steps | p_birth=births/edge | away-fresh/edge | fraction of all births")
    for k in range(0, m + 3):
        s = sub.filter(pl.col("colour") == k)
        sh = (s["edge_steps"] / s["B"]).mean()          # r_k
        pb = (s["new_cells"] / s["edge_steps"].clip(lower_bound=1)).mean()
        aw = (s["away"] / s["edge_steps"].clip(lower_bound=1)).mean()
        fb = (s["new_cells"] / s["B"]).mean()
        tn = s["turn"][0] if s.height else "?"
        say(f"  k={k} r_k={sh:.3f}  p_birth={pb:.3f}  away_fresh={aw:.3f}  births_frac={fb:.3f}")
(out / "stage1_explore.txt").write_text("\n".join(lines) + "\n")
