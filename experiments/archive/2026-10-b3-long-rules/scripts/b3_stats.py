# /// script
# dependencies = ["polars", "numpy"]
# ///
"""B3: rule-length extension. Input experiments/archive/2026-10-b3-long-rules/results/b3_probe.csv (probe to 2^27). Decision rule: notes/frontier-2026-10-13-results.md.
usage: uv run experiments/archive/2026-10-b3-long-rules/scripts/b3_stats.py"""
import sys
sys.path.insert(0, "experiments/_lib")
import polars as pl, numpy as np
from analyse_probe import per_rule
rng = np.random.default_rng(20261013)
raw = pl.read_csv("experiments/archive/2026-10-b3-long-rules/results/b3_probe.csv")
rules = raw["rule"].unique().to_list()
pr = per_rule(raw)
# census-style class from the probe: extent exponent over k=21..27
cls = {}
for (rule,), g in raw.group_by("rule"):
    n_win = g.height
    esc = bool(g["escaped"][0])
    g = g.sort("k"); last = g.tail(1)
    spc = float(last["t"][0]) / 2 / (float(last["width"][0]) * float(last["height"][0])) if n_win else 0
    gg = g.filter(pl.col("k") >= 21)
    full = (not esc) and gg.height >= 7
    if not full or spc < 20: cls[rule] = "builder"; continue
    e = np.maximum(gg["width"].to_numpy(), gg["height"].to_numpy()).astype(float)
    alpha = np.polyfit(gg["k"].to_numpy().astype(float), np.log2(e), 1)[0]
    cls[rule] = "log" if alpha < 0.15 else "blob"
c = pl.DataFrame({"rule": list(cls), "cls": list(cls.values())}).with_columns(n=pl.col("rule").str.len_chars())
def boot(x, f, B=2000):
    x = np.asarray(x); return float(np.std([f(rng.choice(x, len(x))) for _ in range(B)]))
print("n | rules | builder | blob | log | log frac of non-builders (+-bootstrap SE) | blob width-exp median (+-SE) | blob area-exp median")
res = {}
for n in (10, 12, 14, 16, 20, 24):
    cc = c.filter(pl.col("n") == n)
    nb = cc.filter(pl.col("cls") != "builder"); lg = (nb["cls"] == "log").to_numpy().astype(float)
    bl = pr.join(cc.filter(pl.col("cls") == "blob"), on="rule")
    w = bl["alpha_w"].to_numpy()
    res[n] = (lg.mean(), boot(lg, np.mean), np.median(w), boot(w, np.median) if len(w) > 3 else float("nan"))
    print(f"{n:2d} | {cc.height} | {(cc['cls']=='builder').sum()} | {(cc['cls']=='blob').sum()} | {(cc['cls']=='log').sum()} | {res[n][0]:.3f} +- {res[n][1]:.3f} | {res[n][2]:.4f} +- {res[n][3]:.4f} (blob n={len(w)}) | {np.median(bl['a'].to_numpy()):.4f}")
ns = sorted(res); rk = lambda a: np.argsort(np.argsort(a))
print("Spearman(n, log frac) =", round(float(np.corrcoef(rk(ns), rk([res[n][0] for n in ns]))[0, 1]), 2), "; Spearman(n, width exp) =", round(float(np.corrcoef(rk(ns), rk([res[n][2] for n in ns]))[0, 1]), 2))
for n in (14, 16, 20, 24):
    d = res[n][0] - res[12][0]; se = np.hypot(res[n][1], res[12][1]); print(f"n={n} vs control 12: log frac diff {d:+.3f} ({d/se:.1f} SE); width exp diff {res[n][2]-res[12][2]:+.4f}")

# c model (trained on n<=12 calibration sample) on the new rules; only the definitions are exec'd (c_model.py's tail rewrites c_model.csv)
exec(open("experiments/archive/2026-10-probe-growth-census/scripts/c_model.py").read().split("\ns = pl.read_csv")[0])
bl = pr.join(c.filter(pl.col("cls") == "blob"), on="rule", suffix="_c")
bl = bl.with_columns(c_pred=pl.col("rule").map_elements(predict, return_dtype=pl.Float64))
print("\nc-model R^2 on blob rules from this sample (measured c = new cells / boundary steps, k=26 window):")
for lo, hi in ((10, 12), (14, 16), (20, 24)):
    t = bl.filter(pl.col("n").is_between(lo, hi)); y, yh = t["c"].to_numpy(), t["c_pred"].to_numpy()
    print(f"  n in [{lo},{hi}]: {t.height} rules, R^2 = {1 - ((y-yh)**2).sum()/((y-y.mean())**2).sum():.3f}, corr {np.corrcoef(y, yh)[0,1]:.3f}")
