# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "scipy", "polars"]
# ///
"""P1 (README Stage V2, V2-B): tail-law prediction of the kappa drift. Applies the calibrated tail estimator
(calibrate_tail.py, results/calibration_c6.json must have pass == true) to the confirmation histograms. Frozen rule:
identifiable rules (all three bands identifiable, >= 200 durations above t0): predicted slope = 1 + delta - z (1 - theta_mean),
z = slope of ln tau on ln(A/P), delta = slope of ln E[D] on ln(A/P). PASS if median |predicted - observed slope of ln kappa| <= 0.15
AND below the zero-drift error median |observed|, with >= 80% of eligible rules identifiable; FAIL if >= 80% identifiable and the rule
is not met; UNINFORMATIVE otherwise (including a failed calibration).
    uv run experiments/archive/2026-10-kappa-first-passage/scripts/p1_test.py
"""
import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import load_runs  # noqa: E402
import tailfit  # noqa: E402

EXP = HERE.parent
R = EXP / "results"
cal = json.loads((R / "calibration_c6.json").read_text())
roles = pl.read_csv(R / "confirm_roles.csv")
runs = load_runs.runs(R / "confirm").join(roles.select("spec", "role"), on="spec", how="left")
elig = pl.read_csv(R / "confirm_predictions.csv")["rule"].to_list()
hist = pl.concat([pl.read_csv(f) for f in sorted((R / "confirm").glob("*.hist.csv"))]).filter(pl.col("label") == "I")
hist = hist.join(roles.filter(pl.col("role") == "outcome").select("spec", "rule"), on="spec")


def slope(x, y):
    return float(np.polyfit(np.log(x), np.log(y), 1)[0])


out = dict(calibration_pass=cal["pass"], t0_main=64, sensitivity_t0=[32, 128])
per = {}
for t0 in (64, 32, 128):
    rows = []
    for rule in elig:
        o = runs.filter((pl.col("rule") == rule) & (pl.col("role") == "outcome") & (pl.col("reached_hi") == 1))
        g = o.group_by("band").agg((pl.col("area_end") / pl.col("perim_end")).mean().alias("L"), pl.col("kappa").mean().alias("k"),
                                   (pl.col("B_entered_complete_steps").sum() / pl.col("B_entered_complete").sum()).alias("ED")).sort("band")
        if g.height < 3:
            continue
        h = hist.filter(pl.col("rule") == rule)
        fits = []
        for b in range(3):
            c = np.zeros(256)
            for bin_, n in h.filter(pl.col("band") == b).select("bin", "n").iter_rows():
                c[bin_] += n
            fits.append(tailfit.fit(c, float(t0)))
        ident = all(f["ok"] and f["identifiable"] for f in fits)
        row = dict(rule=rule, identifiable=ident, theta=[f.get("theta") for f in fits], tau=[f.get("tau") for f in fits])
        L = g["L"].to_numpy()
        row["obs_slope_kappa"] = slope(L, g["k"].to_numpy())
        row["delta"] = slope(L, g["ED"].to_numpy())
        if ident:
            row["z"] = slope(L, np.array([f["tau"] for f in fits]))
            row["theta_mean"] = float(np.mean([f["theta"] for f in fits]))
            row["pred_slope_kappa"] = 1 + row["delta"] - row["z"] * (1 - row["theta_mean"])
        rows.append(row)
    idr = [r for r in rows if r["identifiable"]]
    res = dict(n_eligible=len(rows), n_identifiable=len(idr), frac_identifiable=len(idr) / max(1, len(rows)))
    if idr:
        err = np.array([abs(r["pred_slope_kappa"] - r["obs_slope_kappa"]) for r in idr])
        zero = np.array([abs(r["obs_slope_kappa"]) for r in idr])
        res.update(median_abs_err=float(np.median(err)), median_zero_drift_err=float(np.median(zero)),
                   median_theta=float(np.median([r["theta_mean"] for r in idr])), median_z=float(np.median([r["z"] for r in idr])),
                   theta_quartiles=[float(q) for q in np.quantile([r["theta_mean"] for r in idr], [0.25, 0.5, 0.75])],
                   z_quartiles=[float(q) for q in np.quantile([r["z"] for r in idr], [0.25, 0.5, 0.75])])
        met = res["median_abs_err"] <= 0.15 and res["median_abs_err"] < res["median_zero_drift_err"]
    else:
        met = False
    if not cal["pass"] or res["frac_identifiable"] < 0.8:
        res["verdict"] = "UNINFORMATIVE" + ("" if cal["pass"] else " (calibration C6 failed)") + ("" if res["frac_identifiable"] >= 0.8 else " (fewer than 80% of eligible rules identifiable)")
    else:
        res["verdict"] = "PASS" if met else "FAIL"
    per[str(t0)] = dict(summary=res, rows=rows)
out["by_t0"] = {k: v["summary"] for k, v in per.items()}
out["verdict_main_t0_64"] = per["64"]["summary"]["verdict"]
(R / "p1_test.json").write_text(json.dumps(dict(out, rows_t0_64=per["64"]["rows"]), indent=2, default=float))
print(json.dumps(out, indent=2, default=float))
