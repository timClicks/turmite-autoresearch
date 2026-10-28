# /// script
# dependencies = ["polars", "numpy", "scipy"]
# ///
"""Item 21: re-measurement of exponent outliers. Input experiments/archive/2026-10-item21-slow-outliers/results/item21_probe.csv (probe 27 < experiments/archive/2026-10-item21-slow-outliers/results/item21_walkers.txt), experiments/archive/2026-10-item21-slow-outliers/results/item21_rules.csv, experiments/archive/2026-10-probe-growth-census/results/probe_summary.csv."""
import numpy as np, polars as pl
from scipy import stats
d = pl.read_csv("experiments/archive/2026-10-item21-slow-outliers/results/item21_probe.csv").filter(~pl.col("escaped")).with_columns(
    rule_=pl.col("rule").str.split("@").list.get(0), seed=pl.col("rule").str.split("@").list.get(1).cast(pl.Int64))
grp = pl.read_csv("experiments/archive/2026-10-item21-slow-outliers/results/item21_rules.csv"); summ = pl.read_csv("experiments/archive/2026-10-probe-growth-census/results/probe_summary.csv")
rows = []
for (r,), g in d.group_by("rule_", maintain_order=True):
    al = []
    for (s,), h in g.group_by("seed", maintain_order=True):
        h = h.filter((pl.col("k") >= 20) & (pl.col("k") <= 26)).sort("k")
        if h.height != 7: continue
        w = np.maximum(h["width"].to_numpy(), h["height"].to_numpy()).astype(float)
        al.append(float(np.polyfit(np.log(h["t"].to_numpy().astype(float)), np.log(w), 1)[0]))
    if len(al) >= 6: rows.append(dict(rule=r, n_ok=len(al), mean=float(np.mean(al)), sd=float(np.std(al, ddof=1)), lo=float(np.min(al)), hi=float(np.max(al)), frac_high=float(np.mean(np.array(al) > 0.37)), frac_low=float(np.mean(np.array(al) < 0.30))))
r = pl.DataFrame(rows).join(grp, on="rule").join(summ.select(["rule", "alpha_w", "g_k", "kappa", "c"]).rename({"alpha_w": "alpha_census"}), on="rule")
print("rules re-measured:", r.height, "of", grp.height, " (others left the board or had < 6 usable runs)")
for gname in ["high", "low", "core"]:
    s = r.filter(pl.col("group") == gname)
    if s.height == 0: continue
    print(f"\n== {gname}: {s.height} rules; census alpha median {s['alpha_census'].median():.3f}; 12-seed mean alpha median {s['mean'].median():.3f}; between-seed sd median {s['sd'].median():.3f}")
    if gname == "high":
        reg = (s["mean"] < 0.37).mean(); pers = s.filter(pl.col("frac_high") >= 10 / 12)
        print(f"   regress below 0.37: {reg:.2f} of rules; persistent (>=10/12 seeds above 0.37): {pers.height} rules; g_k median persistent {pers['g_k'].median() if pers.height else float('nan'):.3f} vs regressed {s.filter(pl.col('frac_high') < 10/12)['g_k'].median():.3f}")
    if gname == "low":
        reg = (s["mean"] > 0.30).mean(); pers = s.filter(pl.col("frac_low") >= 10 / 12)
        print(f"   rise above 0.30: {reg:.2f} of rules; persistent (>=10/12 seeds below 0.30): {pers.height} rules; g_k median persistent {pers['g_k'].median() if pers.height else float('nan'):.3f} vs regressed {s.filter(pl.col('frac_low') < 10/12)['g_k'].median():.3f}")
    if gname == "core":
        print(f"   12-seed mean inside 0.30-0.37: {((s['mean'] > 0.30) & (s['mean'] < 0.37)).mean():.2f}")
x = r.filter(pl.col("group") != "core")
print("\nSpearman(census alpha, 12-seed mean) over outliers: %.3f ; regression slope of mean on census alpha: %.3f" % (stats.spearmanr(x["alpha_census"], x["mean"])[0], np.polyfit(x["alpha_census"].to_numpy(), x["mean"].to_numpy(), 1)[0]))
print("Spearman(g_k, 12-seed mean) over outliers: %.3f" % stats.spearmanr(x["g_k"], x["mean"])[0])
print("\nmost persistent high:", r.filter(pl.col("group") == "high").sort("mean", descending=True).select(["rule", "alpha_census", "mean", "sd", "g_k"]).head(6).rows())
print("most persistent low:", r.filter(pl.col("group") == "low").sort("mean").select(["rule", "alpha_census", "mean", "sd", "g_k"]).head(6).rows())
