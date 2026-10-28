# /// script
# dependencies = ["polars", "numpy"]
# ///
"""A1b: ICC of kappa across rules with 12 patched seeds per rule. Design/decision: notes/frontier-2026-10-13-results.md. usage: uv run experiments/archive/2026-10-a1-kappa/scripts/a1b_icc.py"""
import sys
sys.path.insert(0, "experiments/_lib")
import numpy as np, polars as pl
from analyse_probe import per_rule
def icc(groups):
    groups = [g for g in groups if len(g) >= 6]
    sw = np.sqrt(np.mean([g.var(ddof=1) for g in groups])); means = np.array([g.mean() for g in groups]); m = np.mean([len(g) for g in groups])
    sb2 = max(means.var(ddof=1) - sw ** 2 / m, 0.0); return sb2 / (sb2 + sw ** 2), sw, np.sqrt(sb2), len(groups)
for path in ("experiments/archive/2026-10-b2-between-rule-variance/results/b2_probe.csv", "experiments/archive/2026-10-item21-slow-outliers/results/item21_probe.csv"):
    r = per_rule(pl.read_csv(path)).with_columns(base=pl.col("rule").str.split("@").list.first())
    for label, rr in (("all runs", r), ("core band 0.25<alpha_w<0.42", r.filter(pl.col("alpha_w").is_between(0.25, 0.42)))):
        for col, tr in (("kappa", lambda x: x), ("log kappa", np.log)):
            v = "kappa"
            groups = [tr(g[v].to_numpy()) for _, g in rr.filter(pl.col(v) > 0).group_by("base")]
            i, sw, sb, n = icc(groups)
            print(f"{path:24s} {label:30s} {col:10s}: rules {n}, sd within {sw:.3f}, true sd between {sb:.3f}, ICC {i:.3f}")
