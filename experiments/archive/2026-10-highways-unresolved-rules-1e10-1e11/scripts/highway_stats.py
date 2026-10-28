# /// script
# dependencies = ["polars", "numpy", "scipy"]
# ///
"""Items 18-20: highway onset-time tail, catalogue, and a rule-statistics classifier.
Inputs: sweep_v2.csv (len 2-12, 1e8 budget), sweep_1B.csv (len<=10 unresolved, 1e9),
confirmed_v2.csv. Run: uv run experiments/archive/2026-10-highways-unresolved-rules-1e10-1e11/scripts/highway_stats.py"""
import numpy as np
import polars as pl
from scipy import stats

v2 = pl.read_csv("experiments/archive/2026-10-census-sweeps/results/sweep_v2.csv", infer_schema_length=10000)
b1 = pl.read_csv("experiments/archive/2026-10-census-sweeps/results/sweep_1B.csv", infer_schema_length=10000)
cf = pl.read_csv("experiments/archive/2026-10-census-sweeps/results/confirmed_v2.csv", infer_schema_length=10000)


def root(s):
    n = len(s)
    for p in range(1, n):
        if n % p == 0 and s[:p] * (n // p) == s:
            return s[:p]
    return s


def prim(df):
    return df.filter(pl.col("rule").map_elements(lambda s: root(s) == s, return_dtype=pl.Boolean))


print("v2 stop:", v2.group_by("stop", maintain_order=True).len().to_dicts())
hw = prim(v2.filter(pl.col("stop") == "escaped"))
print("v2 primitive escaped (highway) rules:", hw.height, " with onset null:", hw["onset"].null_count())

# --- H18: onset per decade (length <= 10, primitive), v2 plus 1B continuation
on = hw.filter(pl.col("n") <= 10)["onset"].drop_nulls().to_numpy().astype(float)
b1e = prim(b1.filter(pl.col("stop") == "escaped"))
on1b = b1e["onset"].drop_nulls().to_numpy().astype(float)
alle = np.concatenate([on, on1b])
edges = 10.0 ** np.arange(1, 11)
h, _ = np.histogram(alle, bins=np.append([0], edges))
print("onset decade counts (len<=10 primitive; bins [0,1e1),[1e1,1e2)...):", h.tolist())
print("  of which found only by the 1e9 rerun:", len(on1b), " onsets of those:", sorted(int(x) for x in on1b)[:40])
print("  still unresolved at 1e9 (len<=10, incl repeats):", b1.filter(pl.col("stop") == "budget").height)
dec = h[4:10]  # decades 1e3-1e4 ... 1e8-1e9
print("  decade counts 1e3..1e9:", dec.tolist())
print("  ratios of successive decades:", [round(float(dec[i + 1] / dec[i]), 2) if dec[i] else None for i in range(len(dec) - 1)])
x = np.arange(len(dec)); ok = dec > 0
sl = np.polyfit(x[ok], np.log10(dec[ok]), 1)[0]
print("  slope of log10(count) per decade: %.3f" % sl)
# unresolved estimate: counts in the 1e8-1e9 decade came from a rerun of 854 survivors of 1e8
n_surv = 854
found = len(on1b)
print("  of %d survivors at 1e8, %d (%.1f%%) turned into highways in the next decade" % (n_surv, found, 100 * found / n_surv))
r = 0.5
for rr in (1.0, 0.7, 0.5, 0.3):
    # if each further decade yields found*rr^k more highways
    tot = found * rr / (1 - rr) if rr < 1 else float("inf")
    print("  if decade yield decays by x%.1f per decade, expected further highways among survivors: %s" % (rr, "inf" if tot == float("inf") else "%.0f" % tot))
print("onset median by n (primitive, v2):", {int(n[0]): float(np.median(g["onset"].drop_nulls().to_numpy())) for n, g in hw.group_by("n", maintain_order=True) if g["onset"].drop_nulls().len() > 3})
print("largest onset in v2 / 1B:", int(hw["onset"].max()), int(b1e["onset"].max()))
# fraction of highways with onset >= 1e4 by length
for n in range(6, 13):
    o = hw.filter(pl.col("n") == n)["onset"].drop_nulls().to_numpy()
    if len(o) > 5:
        print("  n=%d: highways %d, onset>=1e4: %.2f, >=1e6: %.2f" % (n, len(o), (o >= 1e4).mean(), (o >= 1e6).mean()))

# --- H19 catalogue
c = prim(cf.filter(pl.col("confirmed")))
c = c.with_columns(dmin=pl.min_horizontal(pl.col("dx").abs(), pl.col("dy").abs()), dmax=pl.max_horizontal(pl.col("dx").abs(), pl.col("dy").abs()))
print("\ncatalogue: confirmed primitive highways", c.height)
print("  |dx|==|dy| fraction %.3f" % (c["dmin"] == c["dmax"]).mean(), " period even fraction %.3f" % ((c["period"] % 2 == 0).mean()))
print("  Spearman(period, n) = %.3f" % stats.spearmanr(c["period"], c["n"])[0])
print(c.group_by(["period", "dmin", "dmax"], maintain_order=True).len().sort("len", descending=True).head(10))
print("  distinct (period,dmin,dmax):", c.select(["period", "dmin", "dmax"]).unique().height, "distinct periods:", c["period"].n_unique())
print("  period mod 4 counts:", c.group_by(pl.col("period") % 4, maintain_order=True).len().sort("period").to_dicts())
print("  dx+dy parity vs period/2 parity:", c.group_by([(pl.col("dx") + pl.col("dy")) % 2, (pl.col("period") // 2) % 2], maintain_order=True).len().to_dicts())
sp = (c["dmax"] / c["period"]).to_numpy()
print("  speed (max coord / step): max %.3f median %.4f" % (sp.max(), np.median(sp)))
print("  period quantiles by n:", {int(n[0]): [int(q) for q in np.quantile(g["period"].to_numpy(), [0.1, 0.5, 0.9])] for n, g in c.group_by("n", maintain_order=True) if g.height > 10})


# --- H20: classifier over rule statistics
def feats(s):
    n = len(s); r = s.count("R")
    runs = max(len(x) for x in s.replace("L", " ").split() + s.replace("R", " ").split())
    flips = sum(s[i] != s[(i + 1) % n] for i in range(n))
    pal = s == s[::-1]
    anti = s == "".join("L" if ch == "R" else "R" for ch in s[::-1])
    return [n, r, r / n, runs, flips, int(pal), int(anti), s[1:3].count("R"), s[:4].count("R")]


names = ["n", "#R", "fracR", "longest_run", "flips", "palindrome", "antipalin", "R_in_pos1-2", "R_in_first4"]
d = prim(v2).filter(pl.col("n") >= 6)
X = np.array([feats(s) for s in d["rule"]], float)
y = (d["stop"] == "escaped").to_numpy().astype(int)
print("\nclassifier set: primitive n>=6 rules", len(y), "highways", int(y.sum()))
rng = np.random.default_rng(20261012)


def auc(score, y):
    rk = stats.rankdata(score); n1 = y.sum(); n0 = len(y) - n1
    return (rk[y == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0)


print("  single-feature AUC:", {nm: round(float(auc(X[:, i], y)), 3) for i, nm in enumerate(names)})


def fit(X, y, l2=1.0, it=50):
    mu, sd = X.mean(0), X.std(0) + 1e-9
    Z = np.c_[np.ones(len(X)), (X - mu) / sd]; w = np.zeros(Z.shape[1])
    for _ in range(it):
        p = 1 / (1 + np.exp(-Z @ w))
        g = Z.T @ (p - y) + l2 * w
        H = (Z.T * (p * (1 - p))) @ Z + l2 * np.eye(len(w))
        w -= np.linalg.solve(H, g)
    return lambda Xn: np.c_[np.ones(len(Xn)), (Xn - mu) / sd] @ w


idx = rng.permutation(len(y)); folds = np.array_split(idx, 5); sc = np.zeros(len(y))
for f in folds:
    tr = np.setdiff1d(idx, f)
    sc[f] = fit(X[tr], y[tr])(X[f])
print("  5-fold CV AUC, logistic on all features: %.3f" % auc(sc, y))
d = d.with_columns(score=sc, y=y)
print("  highways the model finds least plausible:", d.filter(pl.col("y") == 1).sort("score").head(8)["rule"].to_list())
print("  chaotic rules the model finds most highway-like:", d.filter(pl.col("y") == 0).sort("score", descending=True).head(8)["rule"].to_list())

# --- correction (2026-10-13): explicit, labelled decades and a Poisson trend test. The block above labelled its
# decades one too low (it printed h[4:10], which is 1e4..1e10, as "1e3..1e9"); this block is the authoritative H18 result.
print("\n== H18 corrected: onsets per decade, length<=10 primitive (v2 + 1B rerun)")
edges = [10.0 ** k for k in range(3, 10)]  # 1e3 .. 1e9
cnt = np.array([int(((alle > lo) & (alle <= hi)).sum()) for lo, hi in zip(edges[:-1], edges[1:])])
print("decades (1e3,1e4] ... (1e8,1e9]:", cnt.tolist())
x = np.arange(len(cnt)) - (len(cnt) - 1) / 2
w = np.zeros(2)
Xd = np.c_[np.ones(len(cnt)), x]
w = np.array([np.log(cnt.mean()), 0.0])
for _ in range(50):  # Poisson log-linear regression by Newton
    mu = np.exp(Xd @ w); g = Xd.T @ (cnt - mu); H = (Xd.T * mu) @ Xd; w += np.linalg.solve(H, g)
cov = np.linalg.inv((Xd.T * np.exp(Xd @ w)) @ Xd)
print("log10 slope per decade %.3f +- %.3f  (counts multiply by %.2f per decade)" % (w[1] / np.log(10), np.sqrt(cov[1, 1]) / np.log(10), np.exp(w[1])))
prev = cnt[:-1]; lam = prev.mean()
from scipy.stats import poisson
print("last decade %d vs mean of the previous five %.1f: Poisson P(X <= %d) = %.3f" % (cnt[-1], lam, cnt[-1], poisson.cdf(cnt[-1], lam)))
print("web page (build.py) decade counts (1e2..1e8) + found:", [26, 17, 17, 15, 17, 23], "+ 10 (+1 older)")
