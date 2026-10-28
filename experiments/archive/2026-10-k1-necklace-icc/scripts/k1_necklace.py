# /// script
# dependencies = ["polars", "numpy"]
# ///
"""K1: ICC of log kappa (and log c, a) across cyclic rotations of the same rule, blob class. Design/prediction: notes (K1). usage: uv run experiments/archive/2026-10-k1-necklace-icc/scripts/k1_necklace.py"""
import numpy as np, polars as pl
d = pl.read_csv("experiments/archive/2026-10-probe-growth-census/results/probe_summary.csv").filter((pl.col("cls") == "blob") & (pl.col("kappa") > 0))
def canon(r): return min(r[i:] + r[:i] for i in range(len(r)))
d = d.with_columns(neck=pl.col("rule").map_elements(canon, return_dtype=pl.String))
g = d.group_by("neck").agg(n=pl.len()).filter(pl.col("n") >= 2)
d = d.join(g.select("neck"), on="neck").sort("rule")  # join order is not guaranteed
print(f"blob rules {d.height} in {d['neck'].n_unique()} necklaces with >= 2 blob members; sizes: " + str(dict(zip(*np.unique(g['n'].to_numpy(), return_counts=True)))))
def icc1(vals_by_group):
    k = len(vals_by_group); ns = np.array([len(v) for v in vals_by_group]); N = ns.sum(); allv = np.concatenate(vals_by_group); gm = allv.mean()
    msb = sum(n * (np.mean(v) - gm) ** 2 for n, v in zip(ns, vals_by_group)) / (k - 1)
    msw = sum(((v - np.mean(v)) ** 2).sum() for v in vals_by_group) / (N - k)
    n0 = (N - (ns ** 2).sum() / N) / (k - 1)
    return (msb - msw) / (msb + (n0 - 1) * msw)
rng = np.random.default_rng(20261013)
for label, col, tf in (("log kappa", "kappa", np.log), ("log c", "c", np.log), ("a (area exponent)", "a", lambda x: x)):
    groups = [tf(s[col].to_numpy()) for _, s in sorted(d.group_by("neck"), key=lambda kv: kv[0])]  # sorted: polars group order is per-process hash order; the seeded draws below depend on it
    icc = icc1(groups)
    # null: shuffle values across rules, same group sizes
    flat = np.concatenate(groups); sizes = [len(x) for x in groups]; nulls = []
    for _ in range(500):
        p = rng.permutation(flat); out = []; i = 0
        for s in sizes: out.append(p[i:i + s]); i += s
        nulls.append(icc1(out))
    print(f"{label:20s} ICC(1) = {icc:.3f}  (permutation null mean {np.mean(nulls):+.3f}, 95th pct {np.percentile(nulls, 95):+.3f}; {len(groups)} groups)")
