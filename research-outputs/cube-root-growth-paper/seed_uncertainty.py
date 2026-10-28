# /// script
# dependencies = ["polars", "numpy"]
# ///
"""Item 30: between-seed standard deviations (not fit standard errors) of the headline per-rule numbers.

Input: experiments/archive/2026-10-item4-exponent-rotor-calibrated/results/item4_probe.csv (11 rules x 24 random 5x5 starting patches, 2^30 steps, produced by
`probe 30 < experiments/archive/2026-10-item4-exponent-rotor-calibrated/results/item4_walkers.txt`). For every (rule, seed) the census fit is repeated on octave windows
k = 20..26 (as experiments/_lib/analyse_probe.py): alpha_w (max side), alpha_rg (rg2/2), a (area), beta (perimeter vs area), c, kappa.
Output: research-outputs/cube-root-growth-paper/seed_uncertainty.json  {rule: {stat: [mean, sd_between_seeds, n_seeds]}}, plus pooled medians.
Run from the repo root: uv run research-outputs/cube-root-growth-paper/seed_uncertainty.py   (fails loudly if the input is missing)"""
import json, sys
from pathlib import Path
import numpy as np, polars as pl

R = Path(__file__).resolve().parents[2]
src = R / "experiments/archive/2026-10-item4-exponent-rotor-calibrated/results/item4_probe.csv"
if not src.exists() or src.stat().st_size == 0:
    sys.exit(f"seed_uncertainty.py: missing or empty input {src}")
d = pl.read_csv(src).filter(~pl.col("escaped")).with_columns(
    rule_=pl.col("rule").str.split("@").list.get(0), seed=pl.col("rule").str.split("@").list.get(1).cast(pl.Int64))
slope = lambda x, y: float(np.polyfit(np.log(x), np.log(y), 1)[0])
out = {}
for (r,), g in d.group_by("rule_", maintain_order=True):
    rows = {k: [] for k in ["alpha_w", "alpha_rg", "a", "beta", "c", "kappa"]}
    for (s,), h in g.group_by("seed", maintain_order=True):
        h = h.filter((pl.col("k") >= 20) & (pl.col("k") <= 26)).sort("k")
        if h.height != 7: continue
        t = h["t"].to_numpy().astype(float); A = h["area"].to_numpy().astype(float); P = h["perimeter"].to_numpy().astype(float)
        w = np.maximum(h["width"].to_numpy(), h["height"].to_numpy()).astype(float)
        rows["alpha_w"].append(slope(t, w)); rows["alpha_rg"].append(0.5 * slope(t, h["rg2"].to_numpy()))
        rows["a"].append(slope(t, A)); rows["beta"].append(slope(A, P))
        rows["c"].append(float((h["new_cells"] / h["boundary_steps"]).mean()))
        steps = t / 2  # window (t/2, t]
        rows["kappa"].append(float(((h["boundary_steps"] / steps) / (P / A)).mean()))
    out[r] = {k: [float(np.mean(v)), float(np.std(v, ddof=1)), len(v)] for k, v in rows.items() if len(v) > 2}
pooled = {k: float(np.median([out[r][k][1] for r in out if k in out[r]])) for k in ["alpha_w", "alpha_rg", "a", "beta", "c", "kappa"]}
res = {"per_rule": out, "median_between_seed_sd": pooled, "n_rules": len(out), "source": "experiments/archive/2026-10-item4-exponent-rotor-calibrated/results/item4_probe.csv, windows k=20..26"}
(R / "research-outputs" / "cube-root-growth-paper" / "seed_uncertainty.json").write_text(json.dumps(res, indent=1))
print("median between-seed sd over", len(out), "rules:", {k: round(v, 4) for k, v in pooled.items()})
for r in sorted(out, key=lambda x: (len(x), x)):
    print(f"{r:14s}", " ".join(f"{k}={out[r][k][0]:.3f}+-{out[r][k][1]:.3f}" for k in out[r]))
