# /// script
# dependencies = ["polars", "numpy", "scipy"]
# ///
"""Item 15: how many tethered (log-class) rules are 'hard' (home lost on a shuffled field)?
Input experiments/archive/2026-10-tether-rules/results/tether_screen.csv from: tetherlab screen 16777216 8388608 1 < experiments/archive/2026-10-log-growers/results/log_rules.txt"""
import numpy as np, polars as pl
from scipy import stats
d = pl.read_csv("experiments/archive/2026-10-tether-rules/results/tether_screen.csv", infer_schema_length=2000).filter(pl.col("spread_real").is_not_null())
print("shuffled trials that left the board (NaN spread, counted as lost):", d["spread_shuf"].is_nan().sum())
d = d.with_columns(spread_shuf=pl.when(pl.col("spread_shuf").is_nan()).then(1000.0).otherwise(pl.col("spread_shuf")))
print("rules screened", d.height, " escaped/failed:", 560 - d.height)
d = d.with_columns(n=pl.col("rule").str.len_chars(), fracR=pl.col("rule").map_elements(lambda s: s.count("R") / len(s), return_dtype=pl.Float64),
                   tethered=pl.col("spread_real") < 25, lost=pl.col("spread_shuf") >= 30)
t = d.filter(pl.col("tethered"))
print("tethered on the real field (spread<25):", t.height, "of", d.height)
hard = t.filter(pl.col("lost")); print("hard (tethered real, spread_shuf>=30):", hard.height, "= %.1f%% of tethered" % (100 * hard.height / t.height))
mid = t.filter((pl.col("spread_shuf") >= 15) & (pl.col("spread_shuf") < 30)); print("intermediate shuffled spread 15-30:", mid.height)
print("spread_shuf quantiles over tethered rules 10/25/50/75/90/99%:", np.round(np.quantile(t["spread_shuf"].to_numpy(), [.1, .25, .5, .75, .9, .99]), 1))
h, e = np.histogram(t["spread_shuf"].to_numpy(), bins=[0, 5, 10, 15, 20, 25, 30, 35, 40, 50, 100, 1000]); print("histogram of spread_shuf (edges 0,5,10,15,20,25,30,35,40,50,100,1000):", h.tolist())
for feat in ["n", "area", "extent", "fracR"]:
    print(f"Spearman(spread_shuf, {feat}) over tethered: rho={stats.spearmanr(t[feat], t['spread_shuf'])[0]:.3f}   ", f"Spearman(hard, {feat}): {stats.spearmanr(t[feat], t['lost'].cast(int))[0]:.3f}")
print("hard fraction by n:", {int(n[0]): (round(g['lost'].mean(), 2), g.height) for n, g in t.group_by('n', maintain_order=True) if g.height >= 5})
print("check on the five known rules:")
print(d.filter(pl.col("rule").is_in(["RRRRRLLLLLL", "RLLLLRRRRLR", "RRRLLRLLR", "RLLRRRRRLRLR", "RRRLLLLRRRLL"])).select(["rule", "area", "spread_real", "spread_shuf", "near_real", "near_shuf"]))
print("hard rules (first 40):", hard.sort("spread_shuf", descending=True)["rule"].head(40).to_list())

# --- what predicts hardness? (tethered rules only)
def feats(s):
    n = len(s); runs = [len(x) for x in __import__("re").findall(r"R+|L+", s)]
    return [n, s.count("R") / n, len(runs), max(runs), s[1:3].count("R"), s[:4].count("R"), s[-3:].count("R")]
names = ["n", "fracR", "n_runs", "longest_run", "R_in_1-2", "R_in_first4", "R_in_last3"]
X = np.array([feats(s) for s in t["rule"]], float); y = t["lost"].to_numpy().astype(int)
def auc(score, y):
    rk = stats.rankdata(score); n1 = y.sum(); n0 = len(y) - n1
    return (rk[y == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0)
print("\nsingle-feature AUC for 'hard' among tethered rules:", {nm: round(float(auc(X[:, i], y)), 3) for i, nm in enumerate(names)})
print("AUC of territory area alone: %.3f" % auc(t["area"].to_numpy(), y))
# does hardness remain after conditioning on territory size? compare spread_shuf within area terciles
a = t["area"].to_numpy(); q = np.quantile(a, [1/3, 2/3])
for lo, hi in [(0, q[0]), (q[0], q[1]), (q[1], 1e9)]:
    s = t.filter((pl.col("area") >= lo) & (pl.col("area") < hi))
    print(f"  area in [{lo:.0f},{hi:.0f}): n={s.height}, hard {s['lost'].mean():.2f}, median spread_shuf {s['spread_shuf'].median():.1f}, median spread_real {s['spread_real'].median():.1f}")
# shuffled spread relative to the cup size sqrt(area/pi)/sqrt2 (RMS radius of a uniform disc of area A is R/sqrt2)
cup = np.sqrt(t["area"].to_numpy() / np.pi) / np.sqrt(2)
ratio = t["spread_shuf"].to_numpy() / cup
print("spread_shuf / cup-RMS-radius: quantiles 10/50/90%:", np.round(np.quantile(ratio, [.1, .5, .9]), 2), "; spread_real / cup:", np.round(np.quantile(t["spread_real"].to_numpy() / cup, [.1, .5, .9]), 2))

# --- review fix (2026-10-13): the absolute cutoff spread_shuf >= 30 is confounded with territory size. Use size-free quantities:
# q = spread_shuf / cup_rms (cup_rms = sqrt(A/pi)/sqrt2, RMS radius of a uniform disc with the territory's area) and
# rho = spread_shuf / spread_real.
print("\n== size-free hardness")
cup = np.sqrt(d["area"].to_numpy() / np.pi) / np.sqrt(2)
q = d["spread_shuf"].to_numpy() / cup; rho = d["spread_shuf"].to_numpy() / d["spread_real"].to_numpy()
d2 = d.with_columns(q=pl.Series(q), rho=pl.Series(rho), cup=pl.Series(cup))
t2 = d2.filter(pl.col("spread_real") < 25)
print("q = spread_shuf/cup_rms over tethered rules: quantiles 10/25/50/75/90%:", np.round(np.quantile(t2["q"].to_numpy(), [.1, .25, .5, .75, .9]), 2))
print("rho = spread_shuf/spread_real: quantiles 10/25/50/75/90%:", np.round(np.quantile(t2["rho"].to_numpy(), [.1, .25, .5, .75, .9]), 2))
h, e = np.histogram(t2["q"].to_numpy(), bins=np.arange(0, 1.6, 0.1)); print("histogram of q (0.1 bins from 0):", h.tolist())
for thr in (0.4, 0.5, 0.6):
    hard_q = t2.filter(pl.col("q") >= thr)
    print(f"hard_q := spread_shuf >= {thr} cup_rms: {hard_q.height} of {t2.height} = {hard_q.height / t2.height:.1%}; Spearman(hard_q, area) = {stats.spearmanr(t2['area'], (t2['q'] >= thr).cast(int))[0]:.3f}; "
          f"Spearman(hard_q, n) = {stats.spearmanr(t2['rule'].str.len_chars(), (t2['q'] >= thr).cast(int))[0]:.3f}; AUC(area) = {auc(t2['area'].to_numpy(), (t2['q'] >= thr).to_numpy().astype(int)):.3f}")
hq = (t2["q"] >= 0.5).to_numpy().astype(int)
print("by n, share with q >= 0.5:", {int(n[0]): (round(float(g["q"].gt(0.5).mean()), 2), g.height) for n, g in t2.with_columns(n=pl.col("rule").str.len_chars()).group_by("n", maintain_order=True) if g.height >= 5})
Xq = np.array([feats(s) for s in t2["rule"]], float)
print("single-feature AUC for q>=0.5:", {nm: round(float(auc(Xq[:, i], hq)), 3) for i, nm in enumerate(names)})
print("Spearman(q, spread_real) = %.3f ; Spearman(q, area) = %.3f" % (stats.spearmanr(t2["q"], t2["spread_real"])[0], stats.spearmanr(t2["q"], t2["area"])[0]))
print("known five:", t2.filter(pl.col("rule").is_in(["RLLLLRRRRLR", "RRRLLRLLR", "RLLRRRRRLRLR", "RRRLLLLRRRLL"])).select(["rule", "area", "spread_real", "spread_shuf", "q", "rho"]).rows())
