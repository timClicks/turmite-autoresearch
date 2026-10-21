"""Post hoc checks on analysis.txt (exploratory, registered nothing): is the h_min ~ onset link carried by period
or rule length; are the P4 classes prefix families; are seeds shared across unrelated rules.
uv run experiments/2026-10-21-highway-preconditions/scripts/followup.py > experiments/2026-10-21-highway-preconditions/results/followup.txt
"""
from pathlib import Path

import numpy as np
import polars as pl
from scipy.stats import rankdata, spearmanr

RES = Path(__file__).resolve().parents[1] / "results"
ev = pl.read_csv(RES / "events.csv", infer_schema_length=None, schema_overrides={"seed_key": pl.Utf8, "highway_key": pl.Utf8, "pre_key": pl.Utf8})
evi = ev.unique(subset="used", keep="first", maintain_order=True)
e = evi.filter(pl.col("onset") >= 1000)
y = np.log10(e["onset"].to_numpy())


def partial(x, y, z):
    """Spearman partial correlation of x, y given the columns of z (rank-transformed OLS residuals)."""
    rx, ry = rankdata(x), rankdata(y)
    Z = np.column_stack([np.ones(len(x))] + [rankdata(c) for c in z])
    res = lambda v: v - Z @ np.linalg.lstsq(Z, v, rcond=None)[0]
    return np.corrcoef(res(rx), res(ry))[0, 1]


cols = {c: e[c].to_numpy().astype(float) for c in ["h_min", "h_max", "d_pre", "period", "n"]}
cols["dist"] = np.hypot(e["dx"].to_numpy(), e["dy"].to_numpy()).astype(float)
cols["speed"] = cols["dist"] / cols["period"]
cols["h_min_bits"] = cols["h_min"] * np.log2(cols["n"])
print(f"independent events with onset >= 1e3: {e.height}")
for k, v in cols.items():
    print(f"spearman({k:>10}, log10 onset) = {spearmanr(v, y)[0]:.3f}")
print(f"partial(h_min, onset | period)      = {partial(cols['h_min'], y, [cols['period']]):.3f}")
print(f"partial(h_min, onset | period, n)   = {partial(cols['h_min'], y, [cols['period'], cols['n']]):.3f}")
print(f"partial(period, onset | h_min)      = {partial(cols['period'], y, [cols['h_min']]):.3f}")
print(f"partial(h_min, onset | n)           = {partial(cols['h_min'], y, [cols['n']]):.3f}")

# Linear fit of log10 onset on h_min: slope = decades per extra overlap cell.
b, a = np.polyfit(cols["h_min"][cols["h_min"] < 200], y[cols["h_min"] < 200], 1)
print(f"OLS log10 onset = {a:.2f} + {b:.4f} h_min (h_min < 200, n {int((cols['h_min'] < 200).sum())})")
for lo, hi in [(0, 10), (10, 20), (20, 40), (40, 80), (80, 10**6)]:
    m = (cols["h_min"] >= lo) & (cols["h_min"] < hi)
    print(f"  h_min in [{lo},{hi}): n {m.sum():3d}, median log10 onset {np.median(y[m]):.2f}")

print("\nP4 classes: longest common prefix of member rules vs letters actually used")
cls = evi.group_by("highway_key").agg(pl.col("rule"), pl.col("used"), pl.len().alias("k")).filter(pl.col("k") >= 3)
for r in cls.sort("k", descending=True).iter_rows(named=True):
    rules = r["rule"]
    lcp = 0
    while all(len(x) > lcp and x[lcp] == rules[0][lcp] for x in rules):
        lcp += 1
    print(f"  {r['k']:2d} events, common prefix {rules[0][:lcp]!r} ({lcp} letters); used: {sorted(r['used'])[:4]}...")

print("\nSeed keys shared by events whose rules do not share a 4-letter prefix")
for key in ["seed_key", "pre_key"]:
    g = evi.group_by(key).agg(pl.col("rule"), pl.col("period").unique().alias("periods")).filter(pl.col("rule").list.len() >= 2)
    unrelated = g.filter(pl.col("rule").map_elements(lambda rs: len({x[:4] for x in rs}) > 1, return_dtype=pl.Boolean))
    print(f"  {key}: {g.height} keys shared by >= 2 events; {unrelated.height} of them across different 4-letter prefixes")
    for r in unrelated.head(8).iter_rows(named=True):
        print(f"    periods {r['periods']}: {r['rule'][:6]}")
