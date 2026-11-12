"""Amendment A1: log versus power growth of the 143 slow survivors (numpy; reads committed CSVs only).

  uv run --frozen experiments/active/2026-11-survivor-slow-growers/scripts/growth_fit.py

Registered in README "Amendment A1" (commit b1014be) before this script existed. Every threshold below is copied from there.
Order of work: (1) synthetic calibration, which reads no box; (2) data and gate G2; (3) 4-point fits k = 8..11, labels, P1, P2, G1,
P3 (parametric bootstrap), P4 (backcast to 1e7), P5; (4) supplementary stage (5 points, sigma-scale sensitivity, 2e11 check).
Deterministic: all randomness from numpy Generators seeded 20261112 (calibration, then bootstrap LOG arm, then POWER arm).
Writes results/growth_fit.txt and results/growth_fit.csv (LF)."""
import csv, glob, math, os, pathlib
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[4]
HERE = ROOT / "experiments/active/2026-11-survivor-slow-growers"
ARCH = ROOT / "experiments/archive"
CENSUS = ARCH / "2026-10-census-sweeps/results"
SEED, B_BOOT, N_CAL = 20261112, 2000, 3000
ALPHA = np.linspace(0.0, 1.0 / 3.0, 334)
THR_D, CHI2_CONST_5, CHI2_LOG_5 = 4.0, 7.815, 5.991   # D threshold; 3-df and 2-df 95% points (registered)

def sigma(y, scale=1.0):
    return np.maximum(1.0, 0.03 * np.abs(y)) * scale

def fit_all(Y, X, scale=1.0):
    """Weighted LS fits of const, log, power to rows of Y at x = log10 t. sigma from the observed Y (registered).
    Returns chi2 const/log/power, alpha_hat, log (a, b), power C (at t = 1e11) and the log/power predictors."""
    Y = np.atleast_2d(np.asarray(Y, float)); X = np.asarray(X, float)
    W = 1.0 / sigma(Y, scale) ** 2
    c = (W * Y).sum(1) / W.sum(1)
    chiC = (W * (Y - c[:, None]) ** 2).sum(1)
    Sw, Sx, Sxx = W.sum(1), (W * X).sum(1), (W * X * X).sum(1)
    Sy, Sxy = (W * Y).sum(1), (W * X * Y).sum(1)
    b = (Sw * Sxy - Sx * Sy) / (Sw * Sxx - Sx ** 2)
    a = (Sy - b * Sx) / Sw
    chiL = (W * (Y - (a[:, None] + b[:, None] * X)) ** 2).sum(1)
    F = 10.0 ** (ALPHA[:, None] * (X - 11.0))                      # (A, K)
    C = np.einsum("nk,ak,nk->na", W, F, Y) / np.einsum("nk,ak->na", W, F ** 2)
    res = np.einsum("nk,nak->na", W, (Y[:, None, :] - C[:, :, None] * F[None]) ** 2)
    j = res.argmin(1); n = np.arange(len(Y))
    return dict(chiC=chiC, chiL=chiL, chiP=res[n, j], alpha=ALPHA[j], a=a, b=b, C=C[n, j], c=c)

def labels(f, dfC_extra=0):
    aicC, aicL, aicP = f["chiC"] + 2, f["chiL"] + 4, f["chiP"] + 4
    D = f["chiP"] - f["chiL"]
    lab = np.full(len(D), "ambiguous", dtype=object)
    lab[D >= THR_D] = "log"; lab[D <= -THR_D] = "power"
    lab[aicC <= np.minimum(aicL, aicP)] = "const"
    return lab, D

def pred_log(f, x): return f["a"] + f["b"] * x
def pred_pow(f, x): return f["C"] * 10.0 ** (f["alpha"] * (x - 11.0))

def binom_two_sided(k, n):
    k = min(k, n - k)
    return min(1.0, 2.0 * sum(math.comb(n, i) for i in range(k + 1)) / 2.0 ** n)

out = []
P = out.append
def counts(lab): return " ".join(f"{k} {int((lab == k).sum())}" for k in ("const", "log", "power", "ambiguous"))

# ---------------------------------------------------------------- (1) synthetic calibration (no real data)
P("== Calibration (synthetic; seed %d, %d draws per cell, x = 8..11, sigma model as registered)" % (SEED, N_CAL))
rng = np.random.default_rng(SEED)
X4 = np.array([8.0, 9.0, 10.0, 11.0])
for y8 in (30, 60, 120):
    for kind, par in (("log", 0.1), ("log", 0.2), ("power", 0.03), ("power", 0.06), ("power", 0.10), ("power", 0.15)):
        fT = (lambda x: y8 + par * y8 * (x - 8.0)) if kind == "log" else (lambda x: y8 * 10.0 ** (par * (x - 8.0)))
        T = fT(X4)
        Y = T[None] + rng.normal(size=(N_CAL, 4)) * sigma(T)[None]
        y7 = fT(7.0) + rng.normal(size=N_CAL) * sigma(fT(7.0))
        f = fit_all(Y, X4); lab, D = labels(f)
        eL, eP = np.abs(y7 - pred_log(f, 7.0)), np.abs(y7 - pred_pow(f, 7.0))
        P(f"y8={y8:3d} truth {kind:5s} {par:4.2f}: {counts(lab)} (of {N_CAL}); mean D {D.mean():+.2f}; "
          f"backcast N_log/N {np.mean(eL < eP):.3f}; median chi2 best {np.median(np.minimum(f['chiL'], f['chiP'])):.2f}")

# ---------------------------------------------------------------- (2) data
def chunks(d):
    rows = {}
    for fn in sorted(glob.glob(str(ARCH / "2026-10-highways-unresolved-rules-1e10-1e11/results" / d / "chunk_*.csv"))):
        for r in csv.DictReader(open(fn)):
            rows[r["rule"]] = r
    return rows
def flat(name): return {r["rule"]: r for r in csv.DictReader(open(CENSUS / name))}
SRC = {7: flat("sweep_2_10.csv"), 8: flat("sweep_v2.csv"), 9: flat("sweep_1B.csv"), 10: chunks("h1e10"), 11: chunks("h1e11")}
slow = [r["rule"] for r in csv.DictReader(open(HERE / "results/classes.csv")) if r["cls"] == "slow"]
used, dropped = [], []
for k in slow:
    ok = all(kk in SRC[e] and SRC[e][kk]["stop"] == "budget" and SRC[e][kk]["steps"] == str(10 ** e) for e in SRC for kk in [k])
    (used if ok else dropped).append(k)
side = lambda r: max(int(r["width"]), int(r["height"]))
Y5 = np.array([[side(SRC[e][k]) for e in (7, 8, 9, 10, 11)] for k in used], float)
n = len(used)
P(f"\n== Data and G2: slow rules {len(slow)}, used {n}, dropped {len(dropped)} {' '.join(dropped)}; G2 (>= 135 used) -> {'PASS' if n >= 135 else 'FAIL'}")
anom = int((Y5[:, 0] > Y5[:, 1]).sum())
P(f"instrument guard: rules with side(1e7) > side(1e8): {anom} of {n} ({anom / n:.3f}); rules with 1e7 side < 1e8 side: {int((Y5[:, 0] < Y5[:, 1]).sum())}, equal: {int((Y5[:, 0] == Y5[:, 1]).sum())}")

# ---------------------------------------------------------------- (3) stage 1: four points k = 8..11
Y4 = Y5[:, 1:]
f4 = fit_all(Y4, X4); lab4, D4 = labels(f4)
P("\n== Stage 1 (k = 8..11): labels " + counts(lab4) + f"; sum D = {D4.sum():+.2f}, median D {np.median(D4):+.3f}")
p1 = float(np.mean(f4["chiC"] > CHI2_CONST_5)); p2 = float(np.mean(f4["chiL"] <= CHI2_LOG_5))
g1 = float(np.median(np.minimum(f4["chiL"], f4["chiP"])))
G1 = 0.3 <= g1 <= 3.0
P(f"G1: median min(chi2_log, chi2_power) = {g1:.3f}, registered [0.3, 3.0] -> {'PASS' if G1 else 'FAIL (P2, P3 reported as numbers, not verdicts)'}")
P(f"P1: chi2_const > 7.815 in {int((f4['chiC'] > CHI2_CONST_5).sum())}/{n} = {p1:.3f} (registered >= 0.80) -> {'HOLD' if p1 >= 0.8 else 'FAIL'}")
P(f"P2: chi2_log <= 5.991 in {int((f4['chiL'] <= CHI2_LOG_5).sum())}/{n} = {p2:.3f} (registered >= 0.75) -> {'HOLD' if p2 >= 0.75 else 'FAIL'}"
  + ("" if G1 else " [G1 failed: number only]"))
P(f"   adequacy of power: chi2_power <= 5.991 in {int((f4['chiP'] <= CHI2_LOG_5).sum())}/{n}; H-cube control (alpha = 1/3 fixed) is read below")
Fc = 10.0 ** ((1.0 / 3.0) * (X4 - 11.0)); Wc = 1.0 / sigma(Y4) ** 2
Cc = (Wc * Fc * Y4).sum(1) / (Wc * Fc ** 2).sum(1)
chiCube = (Wc * (Y4 - Cc[:, None] * Fc) ** 2).sum(1)
P(f"control H-cube (alpha = 1/3 fixed, 3 df): chi2 > 7.815 in {int((chiCube > CHI2_CONST_5).sum())}/{n} rules rejected; median chi2 {np.median(chiCube):.1f}")
P(f"alpha_hat (power fit, 4 points): median {np.median(f4['alpha']):.4f}, quartiles {np.percentile(f4['alpha'], 25):.4f} {np.percentile(f4['alpha'], 75):.4f}; "
  f"at 0: {int((f4['alpha'] == 0).sum())}, at 1/3: {int((f4['alpha'] >= 1 / 3 - 1e-12).sum())}")
P(f"log slope b (cells per decade): median {np.median(f4['b']):.2f}; relative b/y(1e11) median {np.median(f4['b'] / Y4[:, 3]):.4f}")

# P3: parametric bootstrap of S = sum D
S_obs = float(D4.sum())
rb = np.random.default_rng(SEED)
def boot(truth):
    s = np.empty(B_BOOT)
    for i in range(B_BOOT):
        Ys = truth + rb.normal(size=truth.shape) * sigma(truth)
        g = fit_all(Ys, X4); s[i] = (g["chiP"] - g["chiL"]).sum()
    return s
T_log = f4["a"][:, None] + f4["b"][:, None] * X4
T_pow = f4["C"][:, None] * 10.0 ** (f4["alpha"][:, None] * (X4 - 11.0))
S_log, S_pow = boot(T_log), boot(T_pow)
p_pow = float(np.mean(S_pow >= S_obs)); p_log = float(np.mean(S_log <= S_obs))
if p_pow < 0.05 and p_log >= 0.05: v3 = "LOG favoured"
elif p_log < 0.05 and p_pow >= 0.05: v3 = "POWER favoured"
elif p_log < 0.05 and p_pow < 0.05: v3 = "both rejected"
else: v3 = "indistinguishable"
P(f"P3: S_obs {S_obs:+.2f}; LOG arm S* mean {S_log.mean():+.2f} (5-95%: {np.percentile(S_log, 5):+.1f} {np.percentile(S_log, 95):+.1f}); "
  f"POWER arm S* mean {S_pow.mean():+.2f} (5-95%: {np.percentile(S_pow, 5):+.1f} {np.percentile(S_pow, 95):+.1f}); "
  f"p_pow {p_pow:.4f}, p_log {p_log:.4f} -> {v3} -> P3 {'HOLD' if v3 == 'LOG favoured' else 'FAIL'}" + ("" if G1 else " [G1 failed: number only]"))

# P4: backcast to 1e7
y7 = Y5[:, 0]
eL, eP = np.abs(y7 - pred_log(f4, 7.0)), np.abs(y7 - pred_pow(f4, 7.0))
N_log, N_pow, N_tie = int((eL < eP).sum()), int((eL > eP).sum()), int((eL == eP).sum())
N = N_log + N_pow
pv = binom_two_sided(N_log, N)
if pv < 0.05 and N_log > N / 2: v4 = "HOLD (log wins the backcast)"
elif pv < 0.05: v4 = "FAIL (power wins the backcast)"
else: v4 = "FAIL (indistinguishable)"
P(f"P4: backcast to 1e7: e_log < e_pow in {N_log}, e_pow < e_log in {N_pow}, ties {N_tie}; two-sided exact binomial p = {pv:.4g} -> {v4}")
P(f"    mean signed error (observed - predicted): log {np.mean(y7 - pred_log(f4, 7.0)):+.2f}, power {np.mean(y7 - pred_pow(f4, 7.0)):+.2f}; "
  f"median |err|: log {np.median(eL):.2f}, power {np.median(eP):.2f}; const-model (weighted mean) median |err| {np.median(np.abs(y7 - f4['c'])):.2f}; "
  f"sum of squared standardised backcast errors: log {np.sum(((y7 - pred_log(f4, 7.0)) / sigma(y7)) ** 2):.1f}, power {np.sum(((y7 - pred_pow(f4, 7.0)) / sigma(y7)) ** 2):.1f}")

# P5 descriptive
den = (Y5[:, 2] - Y5[:, 0])      # d7 + d8 = y9 - y7
numr = (Y5[:, 4] - Y5[:, 2])     # d9 + d10 = y11 - y9
m = den > 0
P(f"P5 (descriptive): median (d9 + d10)/(d7 + d8) = {np.median(numr[m] / den[m]):.3f} over {int(m.sum())} rules with d7 + d8 > 0 ({n - int(m.sum())} excluded); H-log ~ 1, power alpha 0.05 ~ 1.26")

# ---------------------------------------------------------------- (4) supplementary
X5 = np.array([7.0, 8.0, 9.0, 10.0, 11.0])
f5 = fit_all(Y5, X5); lab5, D5 = labels(f5)
P("\n== Stage 2 (descriptive, k = 7..11): labels " + counts(lab5) + f"; sum D = {D5.sum():+.2f}; median alpha_hat {np.median(f5['alpha']):.4f}; "
  f"alpha at 0: {int((f5['alpha'] == 0).sum())}, at 1/3: {int((f5['alpha'] >= 1 / 3 - 1e-12).sum())}; chi2_const > 9.488 (4 df): {int((f5['chiC'] > 9.488).sum())}/{n}; "
  f"chi2_log <= 7.815 (3 df): {int((f5['chiL'] <= 7.815).sum())}/{n}; chi2_power <= 7.815: {int((f5['chiP'] <= 7.815).sum())}/{n}")
P("\n== Sigma-scale sensitivity (descriptive only; 4 points)")
for sc in (0.5, 1.0, 2.0):
    g = fit_all(Y4, X4, sc); lb, Dg = labels(g)
    P(f"scale {sc}: labels {counts(lb)}; sum D {Dg.sum():+.2f}; P1 frac {np.mean(g['chiC'] > CHI2_CONST_5):.3f}; P2 frac {np.mean(g['chiL'] <= CHI2_LOG_5):.3f}; "
      f"median min chi2 {np.median(np.minimum(g['chiL'], g['chiP'])):.2f}")

P("\n== 2e11 consistency check, 8 P3 rules (the 2e11 sides were already known: not a test)")
x2 = math.log10(2e11)
for r in (HERE / "results/p3_sample.txt").read_text().split():
    if r not in used: continue
    i = used.index(r)
    row = next(csv.DictReader(open(HERE / "results/p3" / f"{r}.csv")))
    s2 = side(row)
    P(f"{r}: sides 1e8..1e11 {' '.join(str(int(v)) for v in Y4[i])}, observed 2e11 {s2}; log predicts {pred_log(f4, x2)[i]:.1f}, power predicts {pred_pow(f4, x2)[i]:.1f} "
      f"(alpha_hat {f4['alpha'][i]:.3f})")

txt = "\n".join(out) + "\n"
print(txt)
(HERE / "results/growth_fit.txt").write_text(txt)
with open(HERE / "results/growth_fit.csv", "w", newline="") as fh:
    w = csv.writer(fh, lineterminator="\n")
    w.writerow(["rule", "s1e7", "s1e8", "s1e9", "s1e10", "s1e11", "chi2_const", "chi2_log", "chi2_power", "alpha_hat", "log_a", "log_b", "D", "label4",
                "pred1e7_log", "pred1e7_power", "alpha_hat5", "D5", "label5"])
    for i, k in enumerate(used):
        w.writerow([k, *(int(v) for v in Y5[i]), f"{f4['chiC'][i]:.4f}", f"{f4['chiL'][i]:.4f}", f"{f4['chiP'][i]:.4f}", f"{f4['alpha'][i]:.5f}",
                    f"{f4['a'][i]:.4f}", f"{f4['b'][i]:.4f}", f"{D4[i]:.4f}", lab4[i], f"{pred_log(f4, 7.0)[i]:.3f}", f"{pred_pow(f4, 7.0)[i]:.3f}",
                    f"{f5['alpha'][i]:.5f}", f"{D5[i]:.4f}", lab5[i]])
