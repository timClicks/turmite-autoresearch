"""Is the log/blob cut at alpha = 0.15 objective, and is the blob median insensitive to it?

Run from repo root:  uv run experiments/archive/2026-10-alpha-gap/scripts/gap_robustness.py
Reads only committed census.csv and probe_summary.csv. Writes results/gap_robustness.json and
results/alpha_gap.pdf (+png). Seeded: dip-test bootstrap and GMM use seed 20261015.
Tests were registered in README.md before this script was written.
"""
import json
import subprocess
from pathlib import Path

import diptest
import matplotlib
import numpy as np
import polars as pl
from sklearn.mixture import GaussianMixture

matplotlib.use("Agg")
import matplotlib.pyplot as plt

R = Path(__file__).resolve().parents[4]
OUT = R / "experiments/archive/2026-10-alpha-gap/results"
SEED = 20261015

census = pl.read_csv(R / "experiments/archive/2026-10-census-sweeps/results/census.csv")
summ = pl.read_csv(R / "experiments/archive/2026-10-probe-growth-census/results/probe_summary.csv")

res = {"seed": SEED, "n_census": census.height,
       "commit": subprocess.run(["git", "rev-parse", "HEAD"], cwd=R, capture_output=True, text=True).stdout.strip()}

# --- all rules, and non-builders (builder alpha is measured on a different, frame-like regime)
a_all = census["alpha"].to_numpy()
nb = census.filter(pl.col("cls") != "builder")
a_nb = nb["alpha"].to_numpy()
res["n_nonbuilder"] = nb.height
res["counts"] = {r["cls"]: int(r["count"]) for r in census["cls"].value_counts().iter_rows(named=True)}

# --- 1/2. dip test on the raw alpha distribution (stalled rules at alpha ~ 0 included)
for name, a in [("all", a_all), ("nonbuilder", a_nb), ("nonbuilder_alpha_gt_1e-3", a_nb[a_nb > 1e-3])]:
    dip, p = diptest.diptest(a)
    res[f"dip_{name}"] = {"n": int(len(a)), "dip": float(dip), "p": float(p)}

# local density: is there a trough near 0.15 at all?
hist, edges = np.histogram(a_nb, bins=np.arange(0, 0.62, 0.01))
res["hist_nonbuilder_0.01"] = {"edges_left": [round(float(e), 2) for e in edges[:-1]], "counts": hist.tolist()}
mid = (edges[:-1] + edges[1:]) / 2
win = (mid > 0.05) & (mid < 0.30)
res["trough_in_0.05_0.30"] = {"min_count": int(hist[win].min()), "at_alpha": float(mid[win][hist[win].argmin()]),
                              "count_at_0.145_0.155": int(((a_nb >= 0.145) & (a_nb < 0.155)).sum())}

# --- 3. cut sensitivity: median blob alpha_w when the cut moves; blob = non-builder with census alpha >= cut
# probe_summary carries census alpha for every fitted rule; the cut is applied to that column.
rows = []
for cut in [0.05, 0.10, 0.15, 0.20, 0.25]:
    b = summ.filter((pl.col("alpha") >= cut) & (pl.col("cls") != "builder"))
    x = b["alpha_w"].to_numpy()
    rows.append({"cut": cut, "n_blob_census": int(((a_nb >= cut)).sum()), "n_blob_fitted": int(len(x)),
                 "median_alpha_w": float(np.median(x)), "q25": float(np.percentile(x, 25)),
                 "q75": float(np.percentile(x, 75))})
res["cut_sensitivity"] = rows
m = [r["median_alpha_w"] for r in rows if 0.10 <= r["cut"] <= 0.25]
res["median_range_cuts_0.10_0.25"] = {"min": min(m), "max": max(m), "spread": max(m) - min(m)}
base = next(r for r in rows if r["cut"] == 0.15)["median_alpha_w"]
res["max_abs_dev_from_0.15_cut"] = max(abs(v - base) for v in m)

# --- 4. two-component GMM on non-builder alpha (with and without stalled rules)
for name, a in [("nonbuilder", a_nb), ("nonbuilder_alpha_gt_1e-3", a_nb[a_nb > 1e-3])]:
    g = GaussianMixture(2, random_state=SEED, n_init=10).fit(a.reshape(-1, 1))
    o = np.argsort(g.means_.ravel())
    res[f"gmm2_{name}"] = {"means": g.means_.ravel()[o].tolist(), "sd": np.sqrt(g.covariances_.ravel()[o]).tolist(),
                           "weights": g.weights_[o].tolist(), "bic": float(g.bic(a.reshape(-1, 1)))}
    g1 = GaussianMixture(1, random_state=SEED).fit(a.reshape(-1, 1))
    res[f"gmm2_{name}"]["bic_1comp"] = float(g1.bic(a.reshape(-1, 1)))

(OUT / "gap_robustness.json").write_text(json.dumps(res, indent=1))

# --- figure
fig, ax = plt.subplots(1, 2, figsize=(9, 3.4))
ax[0].hist(a_nb, bins=np.arange(0, 0.62, 0.01), color="0.45")
ax[0].axvline(0.15, color="C3", lw=1); ax[0].set_xlabel(r"census width exponent $\alpha$ ($2^{21}$–$2^{27}$)")
ax[0].set_ylabel("rules"); ax[0].set_title("non-builder rules (linear)")
ax[1].hist(a_nb, bins=np.arange(0, 0.62, 0.01), color="0.45"); ax[1].set_yscale("log")
ax[1].axvline(0.15, color="C3", lw=1, label="cut 0.15"); ax[1].legend(); ax[1].set_xlabel(r"$\alpha$")
ax[1].set_title("same, log counts")
fig.tight_layout(); fig.savefig(OUT / "alpha_gap.pdf"); fig.savefig(OUT / "alpha_gap.png", dpi=150)
print(json.dumps({k: v for k, v in res.items() if k != "hist_nonbuilder_0.01"}, indent=1))
print("hist:", res["hist_nonbuilder_0.01"]["counts"])
