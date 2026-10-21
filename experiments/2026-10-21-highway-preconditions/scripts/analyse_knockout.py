"""Score Part 2 (knock-out of the pre-onset seed): controls K1, K2 and predictions Q1-Q3 (README).
uv run experiments/2026-10-21-highway-preconditions/scripts/analyse_knockout.py > experiments/2026-10-21-highway-preconditions/results/knockout_analysis.txt
"""
from pathlib import Path

import numpy as np
import polars as pl
from scipy.stats import spearmanr

RES = Path(__file__).resolve().parents[1] / "results"
ko = pl.read_csv(RES / "knockout.csv", infer_schema_length=None)
ev = pl.read_csv(RES / "events.csv", infer_schema_length=None, schema_overrides={"seed_key": pl.Utf8, "highway_key": pl.Utf8, "pre_key": pl.Utf8}).unique(subset="used", keep="first")


def frac(m: pl.Series) -> str:
    return f"{int(m.sum())}/{m.len()} = {m.mean():.3f}"


base = ko.filter(pl.col("kind") == "base")
ctrl = ko.filter(pl.col("kind") == "control")
seed = ko.filter(pl.col("kind") == "seed")
print(f"events {base.height}; seed knock-outs {seed.height}; control knock-outs {ctrl.height}")
print("seed cells rebuilt nonzero at tau_pre:", frac(base["seed_ok_or_colour"] == "true"))
print("K2 unmodified board launches:", frac(base["launches"]))
print("K1 non-seed knock-out leaves trajectory identical:", frac(ctrl["identical"]))
print("seed knock-outs that leave the trajectory identical (must be 0 unless the turn is unchanged forever):", frac(seed["identical"]))

per = seed.group_by("used").agg(
    pl.len().alias("cells"), pl.col("launches").sum().alias("survive"), pl.col("any_direction").sum().alias("survive_any"),
    pl.col("period").first(), pl.col("onset").first(),
).with_columns(frac=pl.col("survive") / pl.col("cells"), frac_any=pl.col("survive_any") / pl.col("cells"))
q = np.quantile(per["frac"].to_numpy(), [0.1, 0.25, 0.5, 0.75, 0.9])
print("\n== Q1 survival fraction per event: p10 p25 median p75 p90 =", " ".join(f"{x:.3f}" for x in q))
print("pooled survival:", frac(seed["launches"]), "; any direction (exploratory):", frac(seed["any_direction"]))
print("events where no knock-out survives:", frac(per["survive"] == 0), "; where all survive:", frac(per["survive"] == per["cells"]))
print("Q1 (median <= 0.3)", "HOLDS" if np.median(per["frac"]) <= 0.3 else ("FAILS (attractor side, >= 0.5)" if np.median(per["frac"]) >= 0.5 else "FAILS (in between)"))

single = per.filter((pl.col("cells") - pl.col("survive")) == 1)
print(f"\n== Q2 events with exactly one essential cell: {frac(pl.Series([u in set(single['used']) for u in per['used']]))}")
print("Q2 (< 25%)", "HOLDS" if single.height / per.height < 0.25 else "FAILS")

both = seed.group_by("used").agg(
    pl.col("cheb").filter(~pl.col("launches")).median().alias("ess"), pl.col("cheb").filter(pl.col("launches")).median().alias("surv")
).drop_nulls()
print(f"\n== Q3 events with both kinds: {both.height}; essential closer (median cheb smaller): {frac(both['ess'] < both['surv'])}; ties {int((both['ess'] == both['surv']).sum())}")
print("Q3 (>= 70%)", "HOLDS" if (both["ess"] < both["surv"]).mean() >= 0.7 else "FAILS")

print("\n== Exploratory")
print("survival by Chebyshev distance from the ant (pooled):")
print(seed.group_by(pl.col("cheb").clip(0, 8)).agg(pl.len().alias("n"), pl.col("launches").mean().alias("survive")).sort("cheb"))
m = per.join(ev.select("used", "h_min", "d_pre"), on="used")
for c in ["cells", "period", "onset", "h_min"]:
    print(f"spearman(survival fraction, {c}) = {spearmanr(m['frac'], m[c])[0]:.3f}")
print("survival by ant-frame position (cells within 2 of the ant; y < 0 is ahead):")
near = seed.filter(pl.col("cheb") <= 2).group_by("ax", "ay").agg(pl.len().alias("n"), pl.col("launches").mean().round(2).alias("survive")).sort("ay", "ax")
with pl.Config(tbl_rows=30):
    print(near)
