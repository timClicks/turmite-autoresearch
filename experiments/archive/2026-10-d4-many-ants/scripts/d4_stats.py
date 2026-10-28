# /// script
# dependencies = ["polars", "numpy"]
# ///
"""D4: m-dependence of A_m(t)/A_1(m t) from experiments/archive/2026-10-ext-other-lattices-turmites-noise/results/ext_many.csv (spec sq:RULE:m=M, k=12..26, area per tick).
A_1(m t) is interpolated log-log on the octave grid of the m=1 run. Prediction and falsifier: notes/frontier-2026-10-13-results.md.
usage: uv run experiments/archive/2026-10-d4-many-ants/scripts/d4_stats.py"""
import numpy as np, polars as pl
d = pl.read_csv("experiments/archive/2026-10-ext-other-lattices-turmites-noise/results/ext_many.csv").filter(pl.col("k") > 0)
d = d.with_columns(rule=pl.col("spec").str.split(":").list.get(1), m=pl.col("spec").str.split("m=").list.get(1).cast(pl.Int64))
res = {}
for rule in d["rule"].unique().sort():
    base = d.filter((pl.col("rule") == rule) & (pl.col("m") == 1)).sort("k")
    lk, la = base["k"].to_numpy().astype(float), np.log2(base["area"].to_numpy().astype(float))
    for m in (2, 4, 8):
        g = d.filter((pl.col("rule") == rule) & (pl.col("m") == m)).sort("k")
        for k, a in zip(g["k"].to_numpy(), g["area"].to_numpy()):
            kk = k + np.log2(m)  # A_1(m t): m ants make m steps per tick, so compare with the single ant at m*t = 2^(k+log2 m)
            if kk < lk.min() or kk > lk.max(): continue
            res[(rule, m, int(k))] = float(a) / 2 ** np.interp(kk, lk, la)
rows = [(r, m, k, v) for (r, m, k), v in res.items()]
t = pl.DataFrame(rows, schema=["rule", "m", "k", "ratio"], orient="row")
print("mean log2 ratio by k range and m (per rule):")
for rule in t["rule"].unique().sort():
    for lo, hi in ((16, 18), (21, 23)):
        s = t.filter((pl.col("rule") == rule) & pl.col("k").is_between(lo, hi))
        print(f"  {rule:12s} k={lo}-{hi}: " + "  ".join(f"m={m}: {2 ** s.filter(pl.col('m') == m)['ratio'].log(2).mean():.3f}" for m in (2, 4, 8)))
early = t.filter(pl.col("k").is_between(16, 18)).group_by("m").agg(r=pl.col("ratio").log(2).mean()).sort("m")
late = t.filter(pl.col("k").is_between(21, 23)).group_by("m").agg(r=pl.col("ratio").log(2).mean()).sort("m")
print("pooled mean ratio early (16-18) by m:", [round(2 ** x, 3) for x in early["r"]], " late (21-23, the latest k where A_1(m t) exists in the m=1 run to k=26):", [round(2 ** x, 3) for x in late["r"]])
late8 = t.filter((pl.col("m") == 8) & pl.col("k").is_between(21, 23)).group_by("rule").agg(r=pl.col("ratio").mean())
print("m=8 late ratio per rule:", {r: round(v, 3) for r, v in late8.rows()})
print("rules with |late ratio - 1| > 0.08 at m=8:", int((abs(late8["r"] - 1) > 0.08).sum()))
