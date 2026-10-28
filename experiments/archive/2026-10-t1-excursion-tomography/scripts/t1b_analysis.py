# /// script
# dependencies = ["polars", "numpy", "scipy"]
# ///
"""T1b analysis (notes/excursion-tomography-2026-10-13.md section 7).
Run: uv run experiments/archive/2026-10-t1-excursion-tomography/scripts/t1b_analysis.py > experiments/archive/2026-10-t1-excursion-tomography/results/t1b_analysis.txt
Reads experiments/archive/2026-10-t1-excursion-tomography/results/t1b_windows.csv, experiments/archive/2026-10-t1-excursion-tomography/results/t1b_bins.csv (examples/sectors.rs), experiments/archive/2026-10-arm-kappa-depletion-arms/results/armc_pairs.txt.

Deviation from the pre-registered definition: the bins hold sum(dtheta) per log2 bin,
not sum(L * dtheta), so Theta_w(L0) is computed as sum_b time_b * mean_dtheta_b / sum_b time_b
over bins with 2^b >= L0 (assumes L and dtheta are uncorrelated inside one octave of L)."""
import json
import math
import numpy as np
import polars as pl
from scipy import stats
from scipy.optimize import minimize_scalar

SEED = 20261014
rng = np.random.default_rng(SEED)
W = pl.read_csv("experiments/archive/2026-10-t1-excursion-tomography/results/t1b_windows.csv")
B = pl.read_csv("experiments/archive/2026-10-t1-excursion-tomography/results/t1b_bins.csv")
print(f"windows rows {W.height}, bins rows {B.height}")
print("conserved all rows:", W["conserved"].all(), "| escaped rows:", int(W["escaped"].sum()))
print("rows by spec kind: patched", int(W["spec"].str.contains("@").sum()), "rotor", int(W["spec"].str.starts_with("rotor").sum()),
      "rw", int(W["spec"].str.starts_with("rw").sum()))


def features(bins, L0b=6):
    """bins: dict bin -> (count, time, dtheta_sum, dcells_sum, depth_sum). Returns feature dict."""
    cnt = {b: v[0] for b, v in bins.items()}
    n = sum(cnt.values())
    tot_time = sum(v[1] for v in bins.values())
    out = {"n": n, "Lbar": tot_time / n if n else np.nan}
    for name, lb in (("th16", 4), ("th64", 6), ("th256", 8)):
        num = sum(v[1] * v[2] / v[0] for b, v in bins.items() if b >= lb)
        den = sum(v[1] for b, v in bins.items() if b >= lb)
        out[name] = num / den if den else np.nan
    num = sum(v[1] * v[3] / v[0] for b, v in bins.items() if b >= 6)
    den = sum(v[1] for b, v in bins.items() if b >= 6)
    out["dc64"] = num / den if den else np.nan  # time-weighted return displacement in cells
    out["depth_mean"] = sum(v[4] for v in bins.values()) / n if n else np.nan
    # Hill-type fit: P(bin j) ∝ r^j over bins L0b..bc (bc = last bin before the first with < 10 counts)
    bc = L0b
    while cnt.get(bc + 1, 0) >= 10:
        bc += 1
    ks = np.arange(0, bc - L0b + 1)
    c = np.array([cnt.get(L0b + j, 0) for j in ks], float)
    out["bc"] = bc
    if len(ks) >= 3 and cnt.get(L0b, 0) >= 10:
        def nll(a):
            lr = -a * math.log(2)
            lp = ks * lr - np.log(np.sum(np.exp(ks * lr)))
            return -np.sum(c * lp)
        out["alpha"] = minimize_scalar(nll, bounds=(0.01, 6), method="bounded").x
    else:
        out["alpha"] = np.nan
    # 99.9th percentile of L (bin lower edge, log-linear within bin)
    order = sorted(cnt)
    cum, target = 0, 0.999 * n
    for b in order:
        if cum + cnt[b] >= target:
            out["lnL999"] = (b + (target - cum) / cnt[b]) * math.log(2)
            break
        cum += cnt[b]
    return out


rows = []
for (spec, k), g in B.group_by(["spec", "k"], maintain_order=True):
    bins = {int(r[0]): (r[1], r[2], r[3], r[4], r[5]) for r in g.select("bin", "count", "time_sum", "dtheta_sum", "dcells_sum", "depth_sum").iter_rows()}
    rows.append({"spec": spec, "k": k, **features(bins)})
F = pl.DataFrame(rows).join(W.select("spec", "k", "area", "perimeter", "kappa", "c", "part_open", "interior_steps"), on=["spec", "k"])
F = F.with_columns((pl.col("part_open") / pl.col("interior_steps")).alias("open_share"))

# controls
for name in ("rotor", "rw"):
    f = F.filter(pl.col("spec").str.starts_with(name))
    print(f"\ncontrol {name} (rows {f.height}): kappa {f['kappa'].mean():.3f}  th64 {f['th64'].mean():.3f}  alpha {f['alpha'].mean():.3f}  Lbar {f['Lbar'].mean():.1f}")

P = F.filter(pl.col("spec").str.contains("@")).with_columns(pl.col("spec").str.split("@").list.get(0).alias("rule"))
R = {}
for k in (22, 25):
    R[k] = P.filter(pl.col("k") == k).group_by("rule").agg(pl.all().exclude("spec").mean()).sort("rule")


def pairs():
    out = []
    for line in open("experiments/archive/2026-10-arm-kappa-depletion-arms/results/armc_pairs.txt"):
        line = line.strip()
        if line.startswith("('"):
            r1, r2, c1, c2, k1, k2 = eval(line)
            out.append((r1, r2) if k1 < k2 else (r2, r1))  # (low-kappa, high-kappa) by the historical rule means
    return out


PR = pairs()
print(f"\n{len(PR)} pairs; rules with data at k=22: {R[22].height}, k=25: {R[25].height}")

# ---- Prediction 1: sector transport
print("\n=== Prediction 1: low-kappa member has larger Theta_w(64)")
def sign_test(col, k, label):
    d = {r["rule"]: r[col] for r in R[k].iter_rows(named=True)}
    wins = tot = 0
    for lo, hi in PR:
        if lo in d and hi in d and not (np.isnan(d[lo]) or np.isnan(d[hi])):
            tot += 1
            wins += d[lo] > d[hi]
    p = stats.binomtest(wins, tot, 0.5, alternative="greater").pvalue
    # rule-level bootstrap: resample rules, pair weight = mult(lo) * mult(hi)
    rules = sorted(d)
    fr = []
    for _ in range(2000):
        m = dict(zip(rules, np.bincount(rng.integers(0, len(rules), len(rules)), minlength=len(rules))))
        w = wl = 0
        for lo, hi in PR:
            if lo in d and hi in d:
                wt = m[lo] * m[hi]
                w += wt
                wl += wt * (d[lo] > d[hi])
        if w:
            fr.append(wl / w)
    print(f"  k={k} {label}: low>high in {wins}/{tot} pairs (sign p={p:.3g}); rule-bootstrap win fraction {np.mean(fr):.2f} [{np.percentile(fr,2.5):.2f},{np.percentile(fr,97.5):.2f}]")

for k in (22, 25):
    for col in ("th16", "th64", "th256"):
        sign_test(col, k, col)
for k in (22, 25):
    th = R[k]["th64"].to_numpy()
    print(f"  k={k} Theta_w(64): median {np.nanmedian(th):.3f}, quartiles {np.nanpercentile(th,[25,75]).round(3)}, share within 0.1 of pi/2: {np.nanmean(np.abs(th-math.pi/2)<0.1):.2f}")
    print(f"  k={k} Spearman(Theta_w(64), kappa) = {stats.spearmanr(th, R[k]['kappa'].to_numpy(), nan_policy='omit')[0]:+.3f}")

# ---- Prediction 2: tail shape vs cutoff
print("\n=== Prediction 2 (k=25): variance of ln Lbar explained")
d = R[25]
y = np.log(d["Lbar"].to_numpy())
for col, label in (("alpha", "alpha_hat"), ("lnL999", "ln L_99.9")):
    x = d[col].to_numpy()
    ok = ~np.isnan(x) & ~np.isnan(y)
    r = stats.pearsonr(x[ok], y[ok])[0]
    print(f"  {label}: n={ok.sum()} r={r:+.3f} r^2={r*r:.3f}")
ok = ~np.isnan(d["alpha"].to_numpy())
X = np.column_stack([np.ones(ok.sum()), d["alpha"].to_numpy()[ok], d["lnL999"].to_numpy()[ok]])
beta = np.linalg.lstsq(X, y[ok], rcond=None)[0]
print(f"  both: r^2={1-np.sum((y[ok]-X@beta)**2)/np.sum((y[ok]-y[ok].mean())**2):.3f}")
print(f"  alpha_hat summary: median {np.nanmedian(d['alpha'].to_numpy()):.2f}, range {np.nanmin(d['alpha'].to_numpy()):.2f}..{np.nanmax(d['alpha'].to_numpy()):.2f}")
print(f"  Spearman(alpha, kappa) = {stats.spearmanr(d['alpha'].to_numpy(), d['kappa'].to_numpy(), nan_policy='omit')[0]:+.3f}; Spearman(lnL999, kappa) = {stats.spearmanr(d['lnL999'].to_numpy(), d['kappa'].to_numpy())[0]:+.3f}")
print(f"  open-excursion share of interior time (k=25): median {np.median(d['open_share'].to_numpy()):.3f}, max {np.max(d['open_share'].to_numpy()):.3f}")

# ---- Prediction 3: held-out
print("\n=== Prediction 3: leave-one-rule-out, features at k=22 -> ln kappa at k=25")
a, b = R[22], R[25]
j = a.join(b.select("rule", pl.col("kappa").alias("kappa25")), on="rule")
y = np.log(j["kappa25"].to_numpy())
feat = {"lnA": np.log(j["area"].to_numpy()), "th64": j["th64"].to_numpy(), "alpha": j["alpha"].to_numpy(), "lndepth": np.log(j["depth_mean"].to_numpy())}
ok = np.ones(len(y), bool)
for v in feat.values():
    ok &= ~np.isnan(v)
print(f"  rules usable: {ok.sum()} of {len(y)}")
y = y[ok]
def loo(cols):
    X = np.column_stack([np.ones(ok.sum())] + [feat[c][ok] for c in cols])
    pred = np.empty(len(y))
    for i in range(len(y)):
        tr = np.arange(len(y)) != i
        pred[i] = X[i] @ np.linalg.lstsq(X[tr], y[tr], rcond=None)[0]
    return 1 - np.sum((y - pred) ** 2) / np.sum((y - y.mean()) ** 2)  # vs constant fit on all data (slightly generous)
r_base = loo(["lnA"])
r_full = loo(["lnA", "th64", "alpha", "lndepth"])
r_ex = loo(["th64", "alpha", "lndepth"])
print(f"  held-out R^2: baseline ln A(22) {r_base:.3f}; baseline+excursion features {r_full:.3f} (gain {r_full-r_base:+.3f}); excursion features alone {r_ex:.3f}")
# the same, for held-out ln kappa at k=22 itself (same-window, to show what the features can do contemporaneously)


# ======================================================================
# EXPLORATORY (added after seeing the registered results above; not pre-registered)
# Question: are the Prediction-1 and L_99.9 results just territory size (kappa sets area at fixed t)?
print("\n=== EXPLORATORY: size controls")
def partial(x, y, z):
    ok = ~np.isnan(x) & ~np.isnan(y) & ~np.isnan(z)
    x, y, z = x[ok], y[ok], z[ok]
    rx = x - np.polyval(np.polyfit(z, x, 1), z)
    ry = y - np.polyval(np.polyfit(z, y, 1), z)
    return stats.pearsonr(rx, ry), ok.sum()
for k in (22, 25):
    d = R[k]
    lnA = np.log(d["area"].to_numpy()); lk = np.log(d["kappa"].to_numpy())
    Req = np.sqrt(d["area"].to_numpy() / math.pi)
    d = d.with_columns(pl.Series("thR", d["th64"].to_numpy() * Req))
    print(f"k={k}: r(ln A, ln kappa) = {stats.pearsonr(lnA, lk)[0]:+.3f}")
    for col in ("th64", "thR", "dc64", "lnL999", "Lbar", "alpha", "depth_mean"):
        x = d[col].to_numpy()
        if col in ("Lbar", "depth_mean"):
            x = np.log(x)
        (r, p), n = partial(x, lk, lnA)
        print(f"  partial r({col}, ln kappa | ln A) = {r:+.3f} (p={p:.2g}, n={n})")
for col in ("dc64", "thR"):
    for k in (22, 25):
        d = R[k].with_columns((pl.col("th64") * (pl.col("area") / math.pi).sqrt()).alias("thR"))
        m = {r["rule"]: r[col] for r in d.iter_rows(named=True)}
        w = n = 0
        for lo, hi in PR:
            if lo in m and hi in m and not (np.isnan(m[lo]) or np.isnan(m[hi])):
                n += 1; w += m[lo] > m[hi]
        print(f"  pair sign, {col} low>high at k={k}: {w}/{n} (p={stats.binomtest(w, n, .5, alternative='greater').pvalue:.3g})")
print("\nlnL999 vs ln R_eq across rules, per window:")
for k in (22, 23, 24, 25):
    pk = P.filter(pl.col("k") == k).group_by("rule").agg(pl.all().exclude("spec").mean())
    x = np.log(np.sqrt(pk["area"].to_numpy() / math.pi)); y = pk["lnL999"].to_numpy()
    print(f"  k={k}: slope d lnL999 / d ln R = {np.polyfit(x, y, 1)[0]:.2f}, r = {stats.pearsonr(x, y)[0]:+.3f}, n={len(x)}")
a = P.filter(pl.col("k") == 22).group_by("rule").agg(pl.all().exclude("spec").mean())
b = P.filter(pl.col("k") == 25).group_by("rule").agg(pl.all().exclude("spec").mean())
j = a.join(b, on="rule", suffix="_b")
dl = (j["lnL999_b"] - j["lnL999"]).to_numpy() / (3 * math.log(2))
dr = 0.5 * np.log(j["area_b"].to_numpy() / j["area"].to_numpy()) / (3 * math.log(2))
print(f"within-rule exponents vs t (22->25): L999 median {np.median(dl):.2f} (IQR {np.percentile(dl,25):.2f}..{np.percentile(dl,75):.2f}); R median {np.median(dr):.2f}")
