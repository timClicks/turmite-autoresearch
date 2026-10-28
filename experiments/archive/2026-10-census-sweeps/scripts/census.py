import polars as pl, numpy as np
g = pl.read_csv("experiments/archive/2026-10-probe-growth-census/results/growth.csv")
v2 = pl.read_csv("experiments/archive/2026-10-census-sweeps/results/sweep_v2.csv").with_columns(spc=pl.col("steps") / (pl.col("width") * pl.col("height"))).select("rule", "n", "spc")
recs = []
for rule, curve in g.iter_rows():
    pts = [tuple(map(int, p.split(":"))) for p in (curve or "").split()]
    k = np.array([p[0] for p in pts]); e = np.array([p[1] for p in pts], float)
    full = bool(len(k) > 0 and k.max() == 27)
    sel = k >= 21
    alpha = float(np.polyfit(k[sel], np.log2(e[sel]), 1)[0]) if sel.sum() >= 3 else float("nan")
    step = float(np.mean(np.diff(e[sel]))) if sel.sum() >= 3 else float("nan")
    recs.append((rule, full, alpha, step, float(e[-1]) if len(e) else float("nan")))
d = pl.DataFrame(recs, schema={"rule": pl.Utf8, "full": pl.Boolean, "alpha": pl.Float64, "per_doubling": pl.Float64, "ext": pl.Float64}, orient="row").join(v2, on="rule")
d = d.with_columns(cls=pl.when(~pl.col("full") | (pl.col("spc") < 20)).then(pl.lit("builder"))
    .when(pl.col("alpha") < 0.15).then(pl.lit("log"))
    .otherwise(pl.lit("blob")))
d.write_csv("experiments/archive/2026-10-census-sweeps/results/census.csv")
