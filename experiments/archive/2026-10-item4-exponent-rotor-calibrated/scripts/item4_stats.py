# /// script
# dependencies = ["polars", "numpy"]
# ///
"""Item 4: asymptotic area exponent per rule from the 24-seed, 2^30 ensemble (experiments/archive/2026-10-item4-exponent-rotor-calibrated/results/item4_probe.csv)."""
import numpy as np, polars as pl
import sys
PATH = sys.argv[1] if len(sys.argv) > 1 else "experiments/archive/2026-10-item4-exponent-rotor-calibrated/results/item4_probe.csv"
SEP = ":" if "rotor" in PATH.rsplit("/", 1)[-1] else "@"  # rotor walkers are named rotor:SEED, patched ants RULE@SEED
d = pl.read_csv(PATH).filter(~pl.col("escaped")).with_columns(
    rule=pl.col("rule").str.split(SEP).list.get(0), seed=pl.col("rule").str.split(SEP).list.get(1).cast(pl.Int64))
print("rows", d.height, "runs", d.select(["rule", "seed"]).unique().height)
rules = sorted(d["rule"].unique().to_list(), key=lambda r: (len(r), r))
KS = list(range(12, 31))
res = {}
for r in rules:
    g = d.filter(pl.col("rule") == r)
    seeds = sorted(g["seed"].unique().to_list())
    L = np.full((len(seeds), len(KS)), np.nan)
    for i, s in enumerate(seeds):
        h = g.filter(pl.col("seed") == s)
        for k, a in zip(h["k"].to_list(), h["area"].to_list()):
            if k in KS: L[i, KS.index(k)] = np.log(a)
    res[r] = (seeds, L)
def local(L, i0, i1):
    k = np.array(KS[i0:i1 + 1]) * np.log(2)
    return np.array([np.polyfit(k, row[i0:i1 + 1], 1)[0] for row in L])
print("\n%-14s %5s | local area exponent a(k) (3-octave windows, mean of seeds) at k=" % ("rule", "seeds"), "16 20 24 28 29(=k-2..k)")
fits = []
for r in rules:
    seeds, L = res[r]
    ok = ~np.isnan(L).any(axis=0)
    if ok[KS.index(30)] if 30 in KS else False: pass
    lastk = max(k for k, o in zip(KS, ok) if o)
    row = []
    for kk in (16, 20, 24, 28, lastk):
        if kk > lastk: row.append(float("nan")); continue
        i1 = KS.index(kk); loc = local(L, i1 - 2, i1); row.append(loc.mean())
    # per-k ensemble a(k) with SE for the asymptotic fit
    A, SE, KK = [], [], []
    for kk in range(16, lastk + 1):
        i1 = KS.index(kk); loc = local(L, i1 - 2, i1); A.append(loc.mean()); SE.append(loc.std(ddof=1) / np.sqrt(len(loc))); KK.append(kk)
    A, SE, KK = np.array(A), np.array(SE), np.array(KK, float)
    out = {}
    for name, delta in [("d=1/6", 1 / 6), ("d=1/3", 1 / 3), ("d=1/2", 1 / 2)]:
        X = np.c_[np.ones_like(KK), 2.0 ** (-KK * delta)]; W = 1 / SE ** 2
        cov = np.linalg.inv(X.T @ (X * W[:, None])); beta = cov @ X.T @ (W * A)
        chi2 = float((W * (A - X @ beta) ** 2).sum() / (len(A) - 2))
        out[name] = (beta[0], np.sqrt(cov[0, 0]), beta[1], chi2)
    # plain mean over last 6 octaves
    fits.append((r, out, A[-6:].mean(), SE[-6:].mean() / np.sqrt(6), lastk))
    print("%-14s %5d | %s | last k=%d" % (r, len(seeds), " ".join(f"{x:.3f}" for x in row), lastk))
print("\nasymptotic area exponent a_inf from a(k) = a_inf + b 2^(-delta k), k=16..last (weights 1/SE^2); chi2 per dof in brackets; target 2/3 = 0.667")
print("%-14s %-22s %-22s %-22s | mean of last 6 a(k)" % ("rule", "delta=1/6", "delta=1/3", "delta=1/2"))
z3 = []
for r, out, m6, se6, lastk in fits:
    s = " ".join("%.3f+-%.3f(%.1f)  " % (out[n][0], out[n][1], out[n][3]) for n in ["d=1/6", "d=1/3", "d=1/2"])
    print("%-14s %s| %.3f+-%.3f" % (r, s, m6, se6))
    z3.append((out["d=1/3"][0] - 2 / 3) / out["d=1/3"][1])
z3 = np.array(z3)
print("\nz = (a_inf - 2/3)/SE for delta=1/3:", np.round(z3, 1).tolist())
print("rules within 2 SE of 2/3: %d of %d" % ((abs(z3) < 2).sum(), len(z3)))
a_inf = np.array([f[1]["d=1/3"][0] for f in fits]); se = np.array([f[1]["d=1/3"][1] for f in fits])
print("a_inf (delta=1/3): mean %.4f, sd across rules %.4f, mean SE %.4f => between-rule true sd ~ %.4f" % (a_inf.mean(), a_inf.std(ddof=1), se.mean(), np.sqrt(max(a_inf.var(ddof=1) - (se ** 2).mean(), 0))))
a6 = np.array([f[2] for f in fits]); print("mean of last-6 a(k): across-rule mean %.4f sd %.4f; range %.3f..%.3f" % (a6.mean(), a6.std(ddof=1), a6.min(), a6.max()))
print("\nCV across seeds of A / t^(2/3):")
print("%-14s %8s %8s %8s %8s" % ("rule", "k=16", "k=22", "k=28", "last"))
for r in rules:
    seeds, L = res[r]
    cv = lambda kk: np.std(np.exp(L[:, KS.index(kk)] - kk * np.log(2) * 2 / 3), ddof=1) / np.mean(np.exp(L[:, KS.index(kk)] - kk * np.log(2) * 2 / 3))
    ok = ~np.isnan(L).any(axis=0); lastk = max(k for k, o in zip(KS, ok) if o)
    print("%-14s %8.4f %8.4f %8.4f %8.4f (k=%d)" % (r, cv(16), cv(22), cv(min(28, lastk)), cv(lastk), lastk))
# also the correction amplitude b vs the 2^27-window deviation
print("\nb (delta=1/3) amplitude:", {r: round(f[1]["d=1/3"][2], 2) for r, f in zip(rules, fits)})
