"""Calibration part A: put rotor walkers (true range exponent 2/3, width 1/3,
proven by Bou-Rabee & Peres 2026) and simple random walks through the same
per-rule fitting used for the ants, and compare the scatter of the fitted
exponents with the spread across chaotic ant rules.
"""
import json
import sys

import numpy as np
import polars as pl

sys.path.insert(0, "experiments/_lib")
import analyse_probe as ap  # noqa: E402


def fit(path, klo, khi):
    ap.KLO, ap.KHI = klo, khi
    return ap.per_rule(pl.read_csv(path))


def q(x):
    x = np.asarray(x, float)
    return {"median": round(float(np.median(x)), 4), "iqr": [round(float(np.percentile(x, 25)), 4), round(float(np.percentile(x, 75)), 4)],
            "sd": round(float(np.std(x, ddof=1)), 4), "range": [round(float(x.min()), 4), round(float(x.max()), 4)], "n": len(x)}


rot = fit("experiments/archive/2026-10-calib-instrument-calibration/results/calib_rotor.csv", 20, 26)
rw = fit("experiments/archive/2026-10-calib-instrument-calibration/results/calib_rw.csv", 17, 23)
ants = pl.read_csv("experiments/archive/2026-10-probe-growth-census/results/probe_summary.csv").filter(~pl.col("bursty") & (pl.col("cls") == "blob") & pl.col("alpha_w").is_between(0.30, 0.37))
ants_all = pl.read_csv("experiments/archive/2026-10-probe-growth-census/results/probe_summary.csv").filter(~pl.col("bursty") & (pl.col("cls") == "blob"))

out = {}
for name, df in [("rotor", rot), ("random_walk", rw), ("ants_core", ants), ("ants_blob", ants_all)]:
    out[name] = {k: q(df[k]) for k in ["alpha_w", "alpha_rg", "a", "beta", "c", "g_c", "kappa", "g_k", "fill"]}

# Is the ant spread wider than fitting noise? Compare SDs of alpha (width and rg).
for k in ["alpha_w", "alpha_rg"]:
    out[f"sd_ratio_{k}"] = round(out["ants_blob"][k]["sd"] / out["rotor"][k]["sd"], 2)

json.dump(out, open("experiments/archive/2026-10-calib-instrument-calibration/results/calib_partA.json", "w"), indent=1)
for name in ["rotor", "random_walk", "ants_core", "ants_blob"]:
    print(f"\n== {name} (n={out[name]['alpha_w']['n']})")
    for k, v in out[name].items():
        print(f"  {k:8s} median {v['median']:+.4f}  IQR {v['iqr'][0]:+.4f}..{v['iqr'][1]:+.4f}  sd {v['sd']:.4f}  range {v['range'][0]:+.4f}..{v['range'][1]:+.4f}")
print("\nSD ratio ants/rotor:", out["sd_ratio_alpha_w"], "(width)", out["sd_ratio_alpha_rg"], "(radius of gyration)")
