# /// script
# dependencies = ["polars", "numpy"]
# ///
"""C3, A6a and the interior-TV part of A1 from colourstats output.
Inputs: experiments/archive/2026-10-colourstats/results/colourstats_mix.csv (40 random core rules, k=20..26), experiments/archive/2026-10-colourstats/results/colourstats_tether.csv (560 tethered rules, k=22),
experiments/archive/2026-10-probe-growth-census/results/probe_summary.csv (c, kappa drifts g_c, g_k; may lack some rules).
usage: uv run experiments/archive/2026-10-colourstats/scripts/colour_stats.py"""
import polars as pl, numpy as np
def parse(df):
    return df.filter(pl.col("k") != "escaped").with_columns(
        pl.col("k").cast(pl.Int64),
        pl.col("hist_all").str.split(":").list.eval(pl.element().cast(pl.Float64)).alias("ha"),
        pl.col("hist_boundary").str.split(":").list.eval(pl.element().cast(pl.Float64)).alias("hb"))
# ---- C3
m = pl.read_csv("experiments/archive/2026-10-colourstats/results/colourstats_mix.csv", schema_overrides={"k": pl.Utf8})
esc = m.filter(pl.col("k") == "escaped")["rule"].to_list()
m = parse(m)
rows = []; tv = {}
for (rule,), g in m.group_by("rule"):
    g = g.sort("k"); ks = g["k"].to_list()
    if ks[-3:] != [24, 25, 26]: continue
    hb = np.array(g["hb"].to_list()); ha = np.array(g["ha"].to_list()); n = hb.shape[1]
    sb = hb / hb.sum(1, keepdims=True)
    inter = ha - hb; si = inter / inter.sum(1, keepdims=True)
    tv[rule] = [0.5 * np.abs(si[i] - 1 / n).sum() for i in range(len(ks))]
    for c in range(n):
        s = sb[-3:, c]
        if s.max() >= 0.05: rows.append((rule, c, float(s.min()), float(s.max()), float(s.max() / s.min())))
d = pl.DataFrame(rows, schema=["rule", "colour", "smin", "smax", "ratio"], orient="row")
print(f"C3: rules analysed {len(tv)} (escaped: {esc}); (rule,colour) pairs with boundary share >= 0.05: {d.height}")
print(f"  fraction with max/min over k=24..26 < 1.05: {(d['ratio'] < 1.05).mean():.3f}; < 1.10: {(d['ratio'] < 1.10).mean():.3f}; median ratio {d['ratio'].median():.3f}; max {d['ratio'].max():.3f}")
bad = d.sort("ratio", descending=True).head(8); print(bad)
byrule = d.group_by("rule").agg(worst=pl.col("ratio").max()).sort("worst", descending=True)
print(f"  rules with every edge share stable (<1.05): {(byrule['worst'] < 1.05).sum()} of {byrule.height}")
# interior TV drift vs kappa drift
ps = pl.read_csv("experiments/archive/2026-10-probe-growth-census/results/probe_summary.csv").select("rule", "g_k", "g_c", "kappa")
t = pl.DataFrame({"rule": list(tv), "tv20": [v[0] for v in tv.values()], "tv26": [v[-1] for v in tv.values()]}).join(ps, on="rule", how="left")
t = t.with_columns(dtv=pl.col("tv26") - pl.col("tv20"))
print("\nA1-drift: interior colour TV distance from uniform (k=20 -> 26) vs kappa drift g_k")
print(t.sort("g_k").select("rule", "tv20", "tv26", "dtv", "g_k", "kappa").head(40))
tt = t.drop_nulls("g_k")
from numpy import corrcoef
def sp(a, b):
    ra = np.argsort(np.argsort(a)); rb = np.argsort(np.argsort(b)); return float(corrcoef(ra, rb)[0, 1])
if tt.height >= 8:
    print(f"  Spearman(g_k, tv26) = {sp(tt['g_k'].to_numpy(), tt['tv26'].to_numpy()):.2f}; Spearman(|g_k|, |dtv|) = {sp(np.abs(tt['g_k'].to_numpy()), np.abs(tt['dtv'].to_numpy())):.2f}  (n={tt.height})")
# ---- A6a
tdf = parse(pl.read_csv("experiments/archive/2026-10-colourstats/results/colourstats_tether.csv", schema_overrides={"k": pl.Utf8}))
res = []
for rule, ha in zip(tdf["rule"], tdf["ha"]):
    ha = np.array(ha); n = len(ha); sh = ha / ha.sum()
    rare = [int(c) for c in np.where(sh < 0.5 / n)[0]]
    res.append((rule, n, len(rare), float(sh.min() * n), rare))
r = pl.DataFrame(res, schema=["rule", "n", "n_rare", "min_share_x_n", "rare"], orient="row")
print(f"\nA6a: tethered rules with colourstats at k=22: {r.height}")
print(f"  with >=1 rare colour (share < 0.5/n): {(r['n_rare'] >= 1).sum()} ({(r['n_rare'] >= 1).mean():.3f}); >=2: {(r['n_rare'] >= 2).mean():.3f}; >=3: {(r['n_rare'] >= 3).mean():.3f}")
print("  median (rarest share x n):", r["min_share_x_n"].median(), "quantiles 10/90%:", np.round(np.quantile(r['min_share_x_n'].to_numpy(), [.1, .9]), 3))
print(r.group_by("n").agg(k=pl.len(), frac_rare=(pl.col("n_rare") >= 1).mean(), med_min=pl.col("min_share_x_n").median()).sort("n"))
for ru in ("RRRRRLLLLLL", "RLLLLRRRRLR"): print(" ", r.filter(pl.col("rule") == ru).rows())

# A6a control: the same rarity statistic on the 40 random blob rules (k=22 row of colourstats_mix.csv)
cm = parse(pl.read_csv("experiments/archive/2026-10-colourstats/results/colourstats_mix.csv", schema_overrides={"k": pl.Utf8})).filter(pl.col("k") == 22)
ctl = []
for rule, ha in zip(cm["rule"], cm["ha"]):
    ha = np.array(ha); n = len(ha); sh = ha / ha.sum(); ctl.append((int((sh < 0.5 / n).sum()), float(sh.min() * n)))
print(f"\nA6a control (40 blob rules, k=22): >=1 rare colour {np.mean([c[0] >= 1 for c in ctl]):.3f}, >=2 {np.mean([c[0] >= 2 for c in ctl]):.3f}, >=3 {np.mean([c[0] >= 3 for c in ctl]):.3f}; median rarest share x n {np.median([c[1] for c in ctl]):.3f}")
print("tethered rules (n>=8 only, to match lengths): >=1:", round(float((r.filter(pl.col('n') >= 8)['n_rare'] >= 1).mean()), 3), " >=2:", round(float((r.filter(pl.col('n') >= 8)['n_rare'] >= 2).mean()), 3), " >=3:", round(float((r.filter(pl.col('n') >= 8)['n_rare'] >= 3).mean()), 3))

# ---- C3 sampling floor (added after review): if every edge share were exactly constant and the boundary samples at k=24,25,26 were independent,
# how often would max/min over the three octaves still exceed 1.05 / 1.10?  Binomial simulation per (rule, colour) pair, same pairs as above.
rng2 = np.random.default_rng(20261013)
sim_frac05, sim_frac10, sim_med = [], [], []
pairs = 0
for (rule,), g in sorted(m.group_by("rule"), key=lambda kv: kv[0]):  # sorted: polars group order is per-process hash order; the seeded draws below depend on it
    g = g.sort("k"); ks = g["k"].to_list()
    if ks[-3:] != [24, 25, 26]: continue
    hb = np.array(g["hb"].to_list())[-3:]; hb = hb.astype(np.int64); N = hb.sum(1)
    for c in range(hb.shape[1]):
        s = hb[:, c] / N
        if s.max() < 0.05: continue
        p = hb[:, c].sum() / N.sum()
        draws = rng2.binomial(N[None, :], p, size=(4000, 3)) / N[None, :]
        r = draws.max(1) / np.maximum(draws.min(1), 1e-12)
        sim_frac05.append(float((r < 1.05).mean())); sim_frac10.append(float((r < 1.10).mean())); sim_med.append(float(np.median(r))); pairs += 1
print(f"\nC3 sampling floor ({pairs} pairs): under constant true shares and independent boundary samples the expected fraction with max/min < 1.05 is {np.mean(sim_frac05):.3f}, < 1.10 is {np.mean(sim_frac10):.3f}, median ratio {np.median(sim_med):.3f}")
print("observed:", f"< 1.05: {(d['ratio'] < 1.05).mean():.3f}; < 1.10: {(d['ratio'] < 1.10).mean():.3f}; median ratio {d['ratio'].median():.3f}")
bn = m.filter(pl.col("k").is_in([24, 25, 26])).with_columns(nb=pl.col("boundary"))["nb"]
print("boundary cell counts at k=24..26: median", int(bn.median()), " min", int(bn.min()))
