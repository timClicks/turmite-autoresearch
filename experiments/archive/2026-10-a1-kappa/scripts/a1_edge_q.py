# /// script
# dependencies = ["polars", "numpy"]
# ///
"""A1, exploratory (not pre-registered): does the edge-weighted turn probability q_edge = sum_c share_boundary(c) * [rule[c] == R] explain kappa across the 40 mixing-sample rules?
Inputs experiments/archive/2026-10-colourstats/results/colourstats_mix.csv (k=26 boundary colour histograms), experiments/archive/2026-10-probe-growth-census/results/probe_summary.csv (kappa). usage: uv run experiments/archive/2026-10-a1-kappa/scripts/a1_edge_q.py"""
import numpy as np, polars as pl
m = pl.read_csv("experiments/archive/2026-10-colourstats/results/colourstats_mix.csv", schema_overrides={"k": pl.Utf8}).filter(pl.col("k") == "26")
ps = pl.read_csv("experiments/archive/2026-10-probe-growth-census/results/probe_summary.csv").select("rule", "kappa", "c", "n")
rows = []
for rule, hb in zip(m["rule"], m["hist_boundary"]):
    h = np.array([float(v) for v in hb.split(":")]); s = h / h.sum()
    qe = float(sum(s[i] for i, ch in enumerate(rule) if ch == "R")); q = rule.count("R") / len(rule)
    rows.append((rule, qe, q, float(0.5 * np.abs(s - 1 / len(rule)).sum())))
d = pl.DataFrame(rows, schema=["rule", "q_edge", "q", "tv_edge"], orient="row").join(ps, on="rule")
rk = lambda v: np.argsort(np.argsort(v))
print(f"{d.height} rules")
for col in ("q_edge", "q", "tv_edge"):
    x, k, c = d[col].to_numpy(), d["kappa"].to_numpy(), d["c"].to_numpy()
    print(f"Spearman(kappa, {col}) = {np.corrcoef(rk(x), rk(k))[0,1]:+.2f}   Spearman(c, {col}) = {np.corrcoef(rk(x), rk(c))[0,1]:+.2f}")
X = np.c_[np.ones(d.height), d["q_edge"].to_numpy(), d["tv_edge"].to_numpy()]; y = d["kappa"].to_numpy()
loo = []
for i in range(d.height):
    tr = np.arange(d.height) != i; b = np.linalg.lstsq(X[tr], y[tr], rcond=None)[0]; loo.append(X[i] @ b)
loo = np.array(loo); print(f"leave-one-out R^2 of kappa ~ q_edge + tv_edge: {1 - ((y - loo) ** 2).sum() / ((y - y.mean()) ** 2).sum():.3f}  (kappa sd {y.std():.2f}, median {np.median(y):.2f})")
