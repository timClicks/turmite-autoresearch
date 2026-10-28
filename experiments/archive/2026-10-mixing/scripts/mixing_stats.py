"""Summarise the mixing test (experiments/archive/2026-10-mixing/results/mixing.csv) for the page."""
import json
import numpy as np
import polars as pl

m = pl.read_csv("experiments/archive/2026-10-mixing/results/mixing.csv")
s = pl.read_csv("experiments/archive/2026-10-probe-growth-census/results/probe_summary.csv").select("rule", "cls", "alpha_w")
m = m.join(s, on="rule", how="left").with_columns(ratio=pl.col("msd_slope") / pl.col("pred_slope"))
typ = m.filter((pl.col("cls") == "blob") & pl.col("alpha_w").is_between(0.30, 0.37))
uni = typ.filter(pl.col("colour_tv") < 0.05)
non = typ.filter(pl.col("colour_tv") >= 0.05)


def rng(df, col):
    v = df[col].to_numpy()
    return [round(float(np.min(v)), 3), round(float(np.median(v)), 3), round(float(np.max(v)), 3)]


out = {
    "typ_n": typ.height, "uni_n": uni.height, "non_n": non.height,
    "uni_ratio": rng(uni, "ratio"), "uni_expo": rng(uni, "msd_expo"), "uni_tv": rng(uni, "colour_tv"),
    "uni_corr1": rng(uni, "turn_corr1"), "uni_nbr": rng(uni, "nbr_eq"),
    "q_dev_max": round(float(np.max(np.abs(uni["q_eff"].to_numpy() - uni["q_rule"].to_numpy()))), 4),
    "non_ratio": rng(non, "ratio"), "non_expo": rng(non, "msd_expo"), "non_tv": rng(non, "colour_tv"),
    "mix": rng(typ, "mix_ratio"),
    "corr_ratio_tv": round(float(np.corrcoef(typ["ratio"], typ["colour_tv"])[0, 1]), 2),
    "points": [[r["rule"], round(r["pred_slope"], 3), round(r["msd_slope"], 3), round(r["colour_tv"], 3)] for r in typ.iter_rows(named=True)],
}
json.dump(out, open("experiments/archive/2026-10-mixing/results/mixing_stats.json", "w"))
print(json.dumps({k: v for k, v in out.items() if k != "points"}, indent=1))
