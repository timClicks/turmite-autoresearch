"""POST HOC (not registered; written after reading results/analysis.txt). Two questions the registered tests leave open:

1. Does the fitted K3 survival kernel of experiments/archive/2026-10-c-law-mechanism (full-census refit: e = 1.1215,
   rho = 0.6922, psi = 0.16; stage1_k3.json "fresh") already predict the Pi cohort's excess over the lead law? If so,
   the crawler limit (P1) is "more s_0 letters after the kill", which K3 encodes, and H-crawl adds no information there.
2. How does the census residual 1/c - LL(m) depend on the second run j (the number of s_0 letters straight after the
   first opposite letter), by lead m? This is descriptive and uses all stationary census blobs.

usage: uv run --frozen experiments/archive/2026-10-crawler-cost-chaotic-edge/scripts/posthoc_k3.py > .../results/posthoc_k3.txt
"""
from pathlib import Path

import numpy as np
import polars as pl

ROOT = Path(__file__).resolve().parents[4]
RES = Path(__file__).resolve().parents[1] / "results"
E, RHO, PSI = 1.121488436069519, 0.6921567990007209, 0.16


def lead(r):
    k = 1
    while k < len(r) and r[k] == r[0]:
        k += 1
    return k


def run2(r):
    m, n, j = lead(r), len(r), 0
    while j < 3 * n and r[(m + 1 + j) % n] == r[0]:
        j += 1
    return j


def k3(r):
    phi = [1.0 if r[j] == r[0] else PSI for j in range(len(r))]
    return E + RHO * sum(np.prod(phi[1:k]) for k in range(1, min(len(r) - 1, 12) + 1))


def LL(m):
    return 1.363 + 0.696 * min(m, 8)


rows = pl.read_csv(RES / "p1p3_rules.csv")
rows = rows.with_columns(
    pl.col("rule").map_elements(k3, return_dtype=pl.Float64).alias("k3"),
    pl.col("m").map_elements(LL, return_dtype=pl.Float64).alias("ll"),
    pl.col("role").str.starts_with("ctrl").alias("is_ctrl"),
)
rows = rows.with_columns((pl.col("inv_c_census") - pl.col("k3")).alias("res_k3"),
                         (pl.col("inv_c_census") - pl.col("ll")).alias("res_ll"),
                         (pl.col("m") + 1.25).alias("crawler"))
print("1. Census 1/c residuals for the P1 cohort (median over rules; controls are counted per draw, as in P1b)")
for name, g in rows.group_by("is_ctrl", maintain_order=True):
    lab = "controls" if name[0] else "Pi"
    print(f"  {lab:9s} n={len(g)}: 1/c - LL = {g['res_ll'].median():+.3f}; 1/c - K3 = {g['res_k3'].median():+.3f}; "
          f"K3 - LL = {(g['k3'] - g['ll']).median():+.3f}; crawler - LL = {(g['crawler'] - g['ll']).median():+.3f}")
pi = rows.filter(~pl.col("is_ctrl"))
print("  Pi by m (median): m, n, 1/c, LL, K3, crawler")
for (m,), g in pi.group_by("m", maintain_order=True):
    print(f"    m={m} n={len(g)}: {g['inv_c_census'].median():.3f} {LL(m):.3f} {g['k3'].median():.3f} {m + 1.25:.3f}")

print("\n2. All stationary census blobs: median of 1/c - LL(m) by lead m and second run j (capped at m+2)")
cen = pl.read_csv(ROOT / "experiments/archive/2026-10-probe-growth-census/results/probe_summary.csv").filter(
    (pl.col("cls") == "blob") & (pl.col("c") > 0) & (pl.col("g_k").abs() < 0.05))
t = [(lead(r), min(run2(r), lead(r) + 2), 1 / c - LL(lead(r)), 1 / c - k3(r)) for r, c in cen.select("rule", "c").iter_rows()
     if lead(r) < len(r)]
df = pl.DataFrame(t, schema=["m", "j", "res_ll", "res_k3"], orient="row")
for (m,), g in df.filter(pl.col("m") <= 4).group_by("m", maintain_order=True):
    s = g.group_by("j").agg(pl.col("res_ll").median(), pl.col("res_k3").median(), pl.len()).sort("j")
    print(f"  m={m}: " + "; ".join(f"j={j}: LL {a:+.3f}, K3 {b:+.3f} (n={n})" for j, a, b, n in s.iter_rows()))
