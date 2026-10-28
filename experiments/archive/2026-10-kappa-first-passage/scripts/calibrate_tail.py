# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "scipy", "polars"]
# ///
"""C6 (README Stage V2): calibrate the tail estimator on synthetic duration histograms, before applying it to ants.
Sample sizes and the tail share come from the real per-rule-band interior-duration counts (counts only, not tail shapes).
    uv run experiments/archive/2026-10-kappa-first-passage/scripts/calibrate_tail.py [--quick]
Seeds: 202610207000 + 1000 + k.
"""
import json
import sys
import time
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import tailfit  # noqa: E402

EXP = HERE.parent
BASE = 202610207000 + 1000
quick = "--quick" in sys.argv

roles = pl.read_csv(EXP / "results/confirm_roles.csv").filter(pl.col("role") == "outcome")
hist = pl.concat([pl.read_csv(f) for f in sorted((EXP / "results/confirm").glob("*.hist.csv"))]).filter(pl.col("label") == "I")
hist = hist.join(roles.select("spec", "rule"), on="spec").group_by("rule", "band", "bin").agg(pl.col("n").sum())
sizes = hist.group_by("rule", "band").agg(pl.col("n").sum().alias("n"), pl.col("n").filter(pl.col("bin") >= 24).sum().alias("n_tail"))
sizes = sizes.with_columns((pl.col("n_tail") / pl.col("n")).alias("w"))
n_q = [int(x) for x in np.quantile(sizes["n"].to_numpy(), [0.1, 0.5, 0.9])]
w_med = float(sizes["w"].median())
print("real per-rule-band counts: n quantiles 10/50/90 =", n_q, "tail share (bin>=24, d>=64) median =", round(w_med, 3))

rows = []
t0 = time.time()
rng = np.random.default_rng(BASE)
reps, nboot = (6, 15) if quick else (30, 40)
for theta in (0.3, 0.5, 0.7):
    for tau in (2e3, 2e4, 2e5):
        for n_total in (n_q[0], n_q[1]):
            est, ltau, ident, cover = [], [], 0, 0
            for _ in range(reps):
                c = tailfit.sample_counts(rng, n_total, w_med, theta, tau)
                f = tailfit.fit(c)
                if not f["ok"]:
                    continue
                if f["identifiable"]:
                    ident += 1
                    est.append(f["theta"])
                    ltau.append(np.log(f["tau"] / tau))
                    lo, hi = tailfit.bootstrap_theta(c, f, 64, rng, nboot)
                    cover += lo <= theta <= hi
            rows.append(dict(theta=theta, tau=tau, n=n_total, identifiable=ident, reps=reps,
                             bias_theta=float(np.mean(est) - theta) if est else None, sd_theta=float(np.std(est)) if est else None,
                             bias_ln_tau=float(np.mean(ltau)) if ltau else None,
                             coverage=cover / ident if ident else None))
tot_ident = sum(r["identifiable"] for r in rows)
ok_rows = [r for r in rows if r["identifiable"] >= 3]
cov = sum(r["coverage"] * r["identifiable"] for r in ok_rows) / max(1, sum(r["identifiable"] for r in ok_rows))
out = dict(seed_base=BASE, real_n_quantiles=n_q, real_tail_share_median=w_med, rows=rows, pooled_coverage_theta=float(cov),
           max_abs_bias_theta=float(max(abs(r["bias_theta"]) for r in ok_rows)), max_abs_bias_ln_tau=float(max(abs(r["bias_ln_tau"]) for r in ok_rows)),
           criteria="|bias theta| < 0.05, |bias ln tau| < 0.2 where identifiable, pooled 95% coverage of theta in [0.90, 0.99]", seconds=time.time() - t0)
out["pass"] = bool(out["max_abs_bias_theta"] < 0.05 and out["max_abs_bias_ln_tau"] < 0.2 and 0.90 <= cov <= 0.99)
dest = EXP / "results" / ("calibration_c6_quick.json" if quick else "calibration_c6.json")
dest.write_text(json.dumps(out, indent=2))
print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=2))
for r in rows:
    print(r)
