"""Score controls C2-C4 and predictions P1-P5 (README) from the scan outputs.

uv run experiments/2026-10-21-highway-preconditions/scripts/analyse.py > experiments/2026-10-21-highway-preconditions/results/analysis.txt
Reads results/events.csv, results/seeds.tsv, results/control.csv. Deterministic (no randomness).
"""
import math
from pathlib import Path

import numpy as np
import polars as pl
from scipy.stats import spearmanr

RES = Path(__file__).resolve().parents[1] / "results"

ev = pl.read_csv(RES / "events.csv", infer_schema_length=None, schema_overrides={"seed_key": pl.Utf8, "highway_key": pl.Utf8, "pre_key": pl.Utf8})
seeds = pl.read_csv(RES / "seeds.tsv", separator="\t", infer_schema_length=None, quote_char=None)
ctrl = pl.read_csv(RES / "control.csv", infer_schema_length=None)


def frac(mask: pl.Series) -> str:
    return f"{int(mask.sum())}/{mask.len()} = {mask.mean():.3f}"


print(f"rules scanned: {ev.height}; offboard: {ev.filter(pl.col('period').is_null()).height}")
ev = ev.filter(pl.col("period").is_not_null())
ev = ev.with_columns(
    excess=pl.col("d_star") - pl.col("h_min"),
    pre_excess=pl.col("d_pre") - pl.col("h_min"),
    star_rel=(pl.col("tau_star") - pl.col("onset")) / pl.col("period"),
    pre_rel=(pl.col("tau_pre") - pl.col("onset")) / pl.col("period"),
    launch_rel=(pl.col("launch") - pl.col("onset")) / pl.col("period"),
    leave_rel=(pl.col("t_leave") - pl.col("tau_star")) / pl.col("period"),
)

print("\n== Controls")
print("C2 transplant exact through t_end2:", frac(ev["transplant_ok"]))
print("C2 seed size equals |D(tau*)|:", frac(ev["seed_cells"] == ev["d_star"]))
print("C3 onset recomputed equals census:", frac(ev["onset_recomputed"] == ev["onset"]))
# Independent events: rules whose run never reached their last colour share a trajectory with every rule of that prefix.
cons = ev.group_by("used").agg(pl.col("tau_star").n_unique().alias("a"), pl.col("seed_key").n_unique().alias("b"), pl.len().alias("rules"))
print("dedupe consistency (same tau*, seed key within a 'used' group):", frac((cons["a"] == 1) & (cons["b"] == 1)))
evi = ev.unique(subset="used", keep="first", maintain_order=True)
print(f"independent events: {evi.height} (of {ev.height} rules)")
hw_star = evi["dtrunc_star"].median()
ok = ctrl.filter(pl.col("status") == "ok")
print(f"C4 control rules ok: {ok.height}/{ctrl.height}; their min D_delta over the window: {sorted(ok['dtrunc_min'].to_list())}")
print(f"C4 highway median D_delta(tau*) = {hw_star}; controls with min >= 10x that: {frac(ok['dtrunc_min'] >= 10 * hw_star)}")
print("C4 holds" if (ok["dtrunc_min"] >= 10 * hw_star).all() else "C4 FAILS")

print("\n== Descriptive (independent events)")
for c in ["onset", "period", "d_star", "h_min", "h_max", "excess", "d_onset", "d_pre", "pre_excess", "star_rel", "pre_rel", "launch_rel", "leave_rel", "word_letters"]:
    v = evi[c].cast(pl.Float64).to_numpy()
    q = np.nanquantile(v, [0, 0.1, 0.25, 0.5, 0.75, 0.9, 1])
    print(f"{c:>12}: " + " ".join(f"{x:.4g}" for x in q) + "   (min p10 p25 median p75 p90 max)")
print("tau* before onset:", frac(evi["tau_star"] < evi["onset"]), " tau* in highway phase (excess 0):", frac(evi["excess"] == 0))
print("pre-onset seed equal to h_min:", frac(evi["pre_excess"] == 0), "; <= 5:", frac(evi["pre_excess"] <= 5))

print("\n== P1 collapse (onset >= 1e4, chaos level defined)")
p1 = evi.filter((pl.col("onset") >= 10_000) & pl.col("chaos_level").is_not_null() & pl.col("chaos_level").is_not_nan())
print(f"eligible {p1.height}; excluded (onset >= 1e4, no chaos level): {evi.filter((pl.col('onset') >= 10_000)).height - p1.height}")
ratio = p1["d_star"] / p1["chaos_level"]
print("ratio <= 0.1:", frac(ratio <= 0.1), f"; median ratio {ratio.median():.4g}; max {ratio.max():.4g}")
print("P1", "HOLDS" if (ratio <= 0.1).mean() >= 0.95 and ratio.median() <= 0.02 else "FAILS")

print("\n== P2 excess |D(tau*)| - h_min, median <= 10")
print(f"median excess {evi['excess'].median()}")
print("P2", "HOLDS" if evi["excess"].median() <= 10 else "FAILS", "(caveat: tau* after onset makes this trivially 0; see pre-onset excess above)")

print("\n== P3 frontier and outward")
cos_ok = evi["cos_out"].is_not_nan() & (evi["cos_out"] > 0)
print("cos_out > 0:", frac(cos_ok), "; leaves old bbox within 50 periods:", frac(evi["leave_rel"] <= 50))
print("P3", "HOLDS" if cos_ok.mean() >= 0.95 and (evi["leave_rel"] <= 50).mean() >= 0.90 else "FAILS")

print("\n== P4 shared seeds within highway classes (classes with >= 3 independent events)")
def class_table(key: str) -> pl.DataFrame:
    return (
        evi.group_by("highway_key")
        .agg(
            pl.len().alias("events"),
            pl.col("period").first(),
            pl.col(key).n_unique().alias("distinct"),
            pl.col(key).value_counts(sort=True).first().struct.field("count").alias("modal"),
            pl.col("rule").sort().head(4).alias("example_rules"),
        )
        .filter(pl.col("events") >= 3)
        .with_columns(share=pl.col("modal") / pl.col("events"))
        .sort(["events", "period"], descending=[True, False])
    )
ct = class_table("seed_key")
print(f"classes: {ct.height}; with modal seed share >= 0.5: {frac(ct['share'] >= 0.5)}")
print("P4", "HOLDS" if ct.height and (ct["share"] >= 0.5).mean() >= 0.5 else "FAILS")
with pl.Config(tbl_rows=40, fmt_str_lengths=60, tbl_width_chars=160):
    print(ct.select("period", "events", "distinct", "modal", "share", "example_rules"))
cp = class_table("pre_key")
print(f"(exploratory) pre-onset seed: classes with modal share >= 0.5: {frac(cp['share'] >= 0.5)}")
with pl.Config(tbl_rows=40, fmt_str_lengths=60, tbl_width_chars=160):
    print(cp.select("period", "events", "distinct", "modal", "share"))
print(f"distinct highway keys over all independent events: {evi['highway_key'].n_unique()}")

print("\n== P5 Spearman(excess, log10 onset), onset >= 1e3")
p5 = evi.filter(pl.col("onset") >= 1000)
lo = np.log10(p5["onset"].to_numpy())
for name in ["excess", "pre_excess", "d_pre", "h_min"]:
    v = p5[name].to_numpy()
    rho, pv = spearmanr(v, lo) if np.ptp(v) > 0 else (math.nan, math.nan)
    print(f"  {name:>10}: rho {rho:.3f} (p {pv:.2g}), n {len(v)}{'   <- registered' if name == 'excess' else '   (exploratory)'}")
rho = spearmanr(p5["excess"], lo)[0] if np.ptp(p5["excess"].to_numpy()) > 0 else math.nan
print("P5", "HOLDS" if rho >= 0.3 else "FAILS")
