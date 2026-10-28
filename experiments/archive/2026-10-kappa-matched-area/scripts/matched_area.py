# /// script
# requires-python = ">=3.12"
# dependencies = ["numpy", "scipy", "polars"]
# ///
"""M1-M3 of ../README.md on the committed T1b windows. No simulation; bootstrap seed 20261014."""
import hashlib
import subprocess
from pathlib import Path

import numpy as np
import polars as pl
from scipy.stats import rankdata

root = Path(__file__).resolve().parents[1]
src = root.parents[2] / "experiments/archive/2026-10-t1-excursion-tomography" / "results"
rng = np.random.default_rng(20261014)
out = []


def P(*a):
    s = " ".join(str(x) for x in a)
    out.append(s)
    print(s)


seeds = pl.read_csv(src / "t1b_cutoff_seeds.csv").filter(~pl.col("escaped"))
seeds = seeds.with_columns(pl.col("area").log().alias("lnA"))
P("# kappa matched-area; commit", subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip())
P("# input sha256[:16]", hashlib.sha256((src / "t1b_cutoff_seeds.csv").read_bytes()).hexdigest()[:16])
P(f"windows {seeds.height}, rules {seeds['rule'].n_unique()}")


def icc(y, g):
    levels = np.unique(g)
    k = len(levels)
    n_i = np.array([np.sum(g == l) for l in levels])
    N = n_i.sum()
    means = np.array([y[g == l].mean() for l in levels])
    gm = y.mean()
    msb = np.sum(n_i * (means - gm) ** 2) / (k - 1)
    msw = sum(np.sum((y[g == l] - m) ** 2) for l, m in zip(levels, means)) / (N - k)
    n0 = (N - np.sum(n_i**2) / N) / (k - 1)
    return (msb - msw) / (msb + (n0 - 1) * msw)


def resid(yy, xx):
    return yy - np.polyval(np.polyfit(xx, yy, 1), xx)


y, x, g = seeds["lnkappa"].to_numpy(), seeds["lnA"].to_numpy(), seeds["rule"].to_numpy()
P(f"M1 pooled slope {np.polyfit(x, y, 1)[0]:.3f}; ICC(ln kappa) {icc(y, g):.3f}; ICC(area-adjusted residual) {icc(resid(y, x), g):.3f}")
for k in (22, 25):
    s = seeds.filter(pl.col("k") == k)
    yy, xx, gg = s["lnkappa"].to_numpy(), s["lnA"].to_numpy(), s["rule"].to_numpy()
    P(f"   k={k}: ICC raw {icc(yy, gg):.3f}, adjusted {icc(resid(yy, xx), gg):.3f}, n={len(yy)}")


def slopes(df):
    d = df.with_columns(
        (pl.col("lnkappa") - pl.col("lnkappa").mean().over("rule")).alias("dy"),
        (pl.col("lnA") - pl.col("lnA").mean().over("rule")).alias("dx"),
    )
    within = float((d["dx"] * d["dy"]).sum() / (d["dx"] ** 2).sum())
    m = d.group_by("rule").agg(pl.col("lnkappa").mean().alias("y"), pl.col("lnA").mean().alias("x"))
    return float(np.polyfit(m["x"], m["y"], 1)[0]), within


between, within = slopes(seeds)
rules = seeds["rule"].unique().to_list()
by = {r: seeds.filter(pl.col("rule") == r) for r in rules}
bs = []
for _ in range(500):
    pick = rng.choice(len(rules), len(rules))
    # relabel so repeated draws of one rule count as separate clusters
    boot = pl.concat([by[rules[j]].with_columns(pl.lit(f"{rules[j]}#{i}").alias("rule")) for i, j in enumerate(pick)])
    bs.append(slopes(boot))
bs = np.array(bs)
lo = lambda c: np.percentile(bs[:, c], 2.5)
hi = lambda c: np.percentile(bs[:, c], 97.5)
P(f"M2 between-rule slope {between:.3f} [{lo(0):.3f}, {hi(0):.3f}]; within-rule {within:.3f} [{lo(1):.3f}, {hi(1):.3f}]; within - between = {within - between:.3f} (needs >= 0.3)")


def pspearman(a, b, c):
    ra, rb, rc = rankdata(a), rankdata(b), rankdata(c)
    return float(np.corrcoef(resid(ra, rc), resid(rb, rc))[0, 1])


for label, filt in (("all seeds", seeds), ("open share <= 0.10", seeds.filter(pl.col("open_share") <= 0.10))):
    for k in (22, 25):
        s = filt.filter(pl.col("k") == k).group_by("rule").agg(pl.col("ln_ratio").mean(), pl.col("lnkappa").mean(), pl.col("lnA").mean())
        a, b, c = s["ln_ratio"].to_numpy(), s["lnkappa"].to_numpy(), s["lnA"].to_numpy()
        boots = []
        for _ in range(2000):
            i = rng.integers(0, len(a), len(a))
            boots.append(pspearman(a[i], b[i], c[i]))
        P(f"M3 [{label}] k={k} rules={len(a)}: partial rho {pspearman(a, b, c):+.3f}, rule-boot95 [{np.percentile(boots, 2.5):+.3f}, {np.percentile(boots, 97.5):+.3f}]")

(root / "results" / "matched_area.txt").write_text("\n".join(out) + "\n")
