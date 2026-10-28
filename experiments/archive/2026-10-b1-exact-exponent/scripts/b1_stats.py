# /// script
# dependencies = ["polars", "numpy"]
# ///
"""B1 and A2: 20 ants + 8 rotors run to 2^34 (experiments/archive/2026-10-b1-exact-exponent/results/b1_probe_NN.csv). Design and decision rules: notes/frontier-2026-10-13-results.md.
B1: local area exponent a(k) = dlog2 A / dk over 3-octave windows ending at k = 14,16,...,34; fit a(k) = a_inf + b 2^(-k/3) over the last 5 windows (k=26..34);
    also the width exponent. Rotor = calibration of the estimator (true 2/3, 1/3).
A2: beta(k) = dlog P / dlog A between octaves k-4 and k, fit beta(k) = beta_inf + b 2^(-x k) with x = 1/3 and x = 1/2 fixed and with x free (grid), last 6 points.
usage: uv run experiments/archive/2026-10-b1-exact-exponent/scripts/b1_stats.py"""
import glob, numpy as np, polars as pl
raw = pl.concat([pl.read_csv(f) for f in sorted(glob.glob("experiments/archive/2026-10-b1-exact-exponent/results/b1_probe_??.csv"))])
raw = raw.with_columns(w=pl.max_horizontal("width", "height"))
res = {}; info = {}
for (rule,), g in raw.group_by("rule"):
    g = g.sort("k"); info[rule] = (bool(g["escaped"][0]), int(g["k"].max()))
    k = g["k"].to_numpy(); A = g["area"].to_numpy().astype(float); P = g["perimeter"].to_numpy().astype(float); W = g["w"].to_numpy().astype(float)
    d = {kk: i for i, kk in enumerate(k)}
    out = {}
    def loc(arr, ends, span):
        return {e: (np.log2(arr[d[e]]) - np.log2(arr[d[e - span]])) / span for e in ends if e in d and e - span in d}
    ends = list(range(14, 35, 2))
    out["a"] = loc(A, ends, 3); out["w"] = loc(W, ends, 3)
    out["beta"] = {e: (np.log(P[d[e]]) - np.log(P[d[e - 4]])) / (np.log(A[d[e]]) - np.log(A[d[e - 4]])) for e in ends if e in d and e - 4 in d}
    res[rule] = out
def fit_inf(series, kk, x):
    if len(kk) < 4: return float("nan"), float("nan")
    X = np.c_[np.ones(len(kk)), 2.0 ** (-x * np.array(kk))]; y = np.array([series[k] for k in kk])
    beta, *_ = np.linalg.lstsq(X, y, rcond=None); r = y - X @ beta; dof = max(len(y) - 2, 1)
    cov = (r @ r / dof) * np.linalg.inv(X.T @ X); return float(beta[0]), float(np.sqrt(cov[0, 0]))
rot = sorted(r for r in res if r.startswith("rotor"))
ants = [l.strip() for l in open("experiments/archive/2026-10-b1-exact-exponent/results/b1_rules.txt") if l.strip()]
print("runs present:", len(res), " escaped:", [r for r, v in info.items() if v[0]], " max k per run (min over runs):", min(v[1] for v in info.values()))
def last(series, n=5): ks = sorted(series)[-n:]; return ks
print("\n== B1: area exponent. rule | a(26) a(30) a(34) | a_inf (fit SE) over k=26..34 [x=1/3] | w_inf")
tab = {}
for r in rot + ants:
    if r not in res or 34 not in res[r]["a"]: print(r, "no k=34"); continue
    a = res[r]["a"]; w = res[r]["w"]; ks = [26, 28, 30, 32, 34]
    ai, se = fit_inf(a, ks, 1 / 3); wi, wse = fit_inf(w, ks, 1 / 3)
    tab[r] = (a[26], a[30], a[34], ai, se, wi); print(f"{r:14s} | {a[26]:.3f} {a[30]:.3f} {a[34]:.3f} | {ai:.3f} ({se:.3f}) | {wi:.3f}")
rv = np.array([tab[r][3] for r in rot if r in tab]); rw = np.array([tab[r][5] for r in rot if r in tab])
print(f"\nrotor calibration: a_inf mean {rv.mean():.4f} sd {rv.std(ddof=1):.4f} (n={len(rv)}), true 2/3 -> estimator bias {rv.mean()-2/3:+.4f}; raw a(34) mean {np.mean([tab[r][2] for r in rot if r in tab]):.4f}; width a_inf mean {rw.mean():.4f}")
av = {r: tab[r][3] for r in ants if r in tab}
n_raw = sum(abs(v - 2 / 3) < 0.005 for v in av.values()); bias = rv.mean() - 2 / 3
n_cor = sum(abs(v - bias - 2 / 3) < 0.005 for v in av.values())
print(f"ants with |a_inf - 2/3| < 0.005: raw {n_raw} of {len(av)}; after subtracting the rotor estimator bias: {n_cor} of {len(av)}  (decision rule: >= 15 of 20)")
print(f"between-rule sd of a_inf (ants) {np.std(list(av.values()), ddof=1):.4f}; median a(34) {np.median([tab[r][2] for r in ants if r in tab]):.4f}")
mono = 0
for r in ants:
    if r in tab:
        s = [res[r]["a"][e] for e in (26, 28, 30, 32, 34) if e in res[r]["a"]]; mono += (np.diff(s) <= 0.005).all() if tab[r][2] > 2 / 3 else (np.diff(s) >= -0.005).all()
print(f"ants whose a(k) approaches 2/3 monotonically (steps toward 2/3 within 0.005) over k=26..34: {mono} of {len(av)}")
print("\n== A2: edge exponent beta. beta(k) local slopes, mean over 8 rotor seeds:", {e: round(float(np.mean([res[r]['beta'][e] for r in rot if e in res[r]['beta']])), 4) for e in range(18, 35, 2)})
def beta_fits(series_by_run, label):
    ks = [e for e in range(24, 35, 2)]
    for x in (1 / 3, 1 / 2):
        v = [fit_inf(s, [k for k in ks if k in s], x)[0] for s in series_by_run]; v = np.array([u for u in v if np.isfinite(u)])
        print(f"  {label}: beta_inf (x={x:.2f} fixed, k=24..34): mean {v.mean():.4f}, between-run sd {v.std(ddof=1):.4f}, n={len(v)}")
    best = None
    for x in np.linspace(0.05, 1.5, 59):
        v = np.array([fit_inf(s, [k for k in ks if k in s], x)[0] for s in series_by_run]); rss = 0
        for s in series_by_run:
            kk = [k for k in ks if k in s]; X = np.c_[np.ones(len(kk)), 2.0 ** (-x * np.array(kk))]; y = np.array([s[k] for k in kk]); b, *_ = np.linalg.lstsq(X, y, rcond=None); rss += ((y - X @ b) ** 2).sum()
        if best is None or rss < best[0]: best = (rss, x, v.mean())
    print(f"  {label}: free-x best x = {best[1]:.2f}, beta_inf there = {best[2]:.4f} (rss {best[0]:.2e})")
beta_fits([res[r]["beta"] for r in rot if len(res[r]["beta"]) > 5], "rotor (8 seeds)")
pooled = {e: float(np.mean([res[r]['beta'][e] for r in rot if e in res[r]['beta']])) for e in range(18, 35, 2)}
print("  rotor pooled-mean series fit beta_inf (x=1/3, 1/2):", [round(fit_inf(pooled, [24, 26, 28, 30, 32, 34], x)[0], 4) for x in (1 / 3, 1 / 2)])
print("  ants beta_inf (x=1/3) per rule [last-5 local slopes 26..34]:")
for r in ants:
    if r in res and 34 in res[r]["beta"]:
        s = res[r]["beta"]; print(f"    {r:14s} beta(26..34) = {[round(s[e], 3) for e in (26, 28, 30, 32, 34)]}  beta_inf(x=1/3) = {fit_inf(s, [24, 26, 28, 30, 32, 34], 1/3)[0]:.3f}")

# ---- additional summary requested by the calibration (added after the first run, see notes): ants vs the rotor's seed scatter
sd = rv.std(ddof=1); mu = rv.mean()
rot_pass = int(sum(abs(v - 2 / 3) < 0.005 for v in rv))
print(f"\nrotor itself: {rot_pass} of {len(rv)} seeds satisfy |a_inf - 2/3| < 0.005 (the B1 criterion needs 15/20 = 75%)")
usable = {r: v for r, v in av.items() if tab[r][4] < 0.02}
within = {r: v for r, v in usable.items() if abs(v - mu) < 2 * sd}
print(f"ants with fit SE < 0.02: {len(usable)} of {len(av)}; of those, within 2 rotor-sd ({2*sd:.4f}) of the rotor mean {mu:.4f}: {len(within)}; outside: {sorted((r, round(v, 3)) for r, v in usable.items() if r not in within)}")
print("ants with fit SE >= 0.02 (a(k) too erratic to fit):", sorted((r, round(tab[r][3], 3), round(tab[r][4], 3)) for r in av if r not in usable))
bi = {r: fit_inf(res[r]["beta"], [24, 26, 28, 30, 32, 34], 1 / 3)[0] for r in ants if r in res and 34 in res[r]["beta"]}
print(f"ants beta_inf (x=1/3): mean {np.mean(list(bi.values())):.4f}, median {np.median(list(bi.values())):.4f}, range {min(bi.values()):.3f}-{max(bi.values()):.3f}; rotor seed sd of beta_inf {0.0148:.4f}")
