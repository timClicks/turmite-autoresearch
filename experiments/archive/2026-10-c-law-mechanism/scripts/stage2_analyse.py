# /// script
# dependencies = ["polars", "numpy", "scipy"]
# ///
"""Stage 2 analysis (README): T0 calibration, L1-L3, C1, N1, K4/V validation, flat band S1-S5.
usage: uv run experiments/archive/2026-10-c-law-mechanism/scripts/stage2_analyse.py"""
import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
from c_models import SEED, k3_fit, k3_predict, k4_fit, k4_predict, lead_fit, lead_predict, r2, run0  # noqa: E402

root = Path(__file__).resolve().parents[4]
R = root / "experiments/archive/2026-10-c-law-mechanism/results"
lines, res = [], {}


def say(s=""):
    print(s)
    lines.append(s)


def load(name):
    return [json.loads(l) for l in (R / name).read_text().splitlines() if l.strip()]


def cval(d):
    return d["births"] / d["boundary_steps"]


cen_all = pl.read_csv(root / "experiments/archive/2026-10-probe-growth-census/results/probe_summary.csv")
cen = cen_all.filter((pl.col("cls") == "blob") & (pl.col("c") > 0) & (pl.col("g_k").abs() < 0.05))
cmap = dict(zip(cen_all["rule"], cen_all["c"]))

# ---------------- T0
cal = load("trace_calib.jsonl")
ro = np.array([cval(d) for d in cal if d["spec"].startswith("rotor:")])
rw24 = [d for d in cal if d["spec"].startswith("rw:")]
cal_rw = load("trace_calib_rw.jsonl")
rw = np.array([cval(d) for d in cal_rw])
res["T0a"] = dict(mean=ro.mean(), sd=ro.std(ddof=1), n=len(ro), esc=sum(d["escaped"] for d in cal if d["spec"].startswith("rotor:")),
                  passed=bool(0.47 <= ro.mean() <= 0.52 and ro.std(ddof=1) <= 0.03))
res["T0b"] = dict(mean=rw.mean(), sd=rw.std(ddof=1), n=len(rw), esc_2e24=sum(d["escaped"] for d in rw24), esc_2e20=sum(d["escaped"] for d in cal_rw),
                  passed=bool(0.40 <= rw.mean() <= 0.48))
say(f"T0a rotor c: mean {ro.mean():.4f} sd {ro.std(ddof=1):.4f} (n={len(ro)}, escaped {res['T0a']['esc']}) -> {'PASS' if res['T0a']['passed'] else 'FAIL'}")
say(f"T0b random walk c: mean {rw.mean():.4f} sd {rw.std(ddof=1):.4f} (2^20 steps, n={len(rw)}, escaped {res['T0b']['esc_2e20']}; at 2^24 {res['T0b']['esc_2e24']}/32 escaped) -> {'PASS' if res['T0b']['passed'] else 'FAIL'}")
smp = load("trace_sample.jsonl")
rel = np.array([abs(cval(d) / cmap[d["spec"]] - 1) for d in smp if not d["escaped"]])
res["T0c"] = dict(n=len(rel), escaped=sum(d["escaped"] for d in smp), median_rel=float(np.median(rel)), passed=bool(np.median(rel) <= 0.06 and not any(d["escaped"] for d in smp)))
say(f"T0c sample: n={len(smp)}, escaped {res['T0c']['escaped']}, median |c_trace/c_census - 1| {np.median(rel):.4f} -> {'PASS' if res['T0c']['passed'] else 'FAIL'}")

# ---------------- L1-L3, C1, N1 on the sample
S = []
for d in smp:
    m = run0(d["spec"])
    S.append(dict(d=d, m=m, rule=d["spec"], B=d["births"], c=cval(d)))


def pooled_lag4(rows, ks_of):
    num = den = 0
    for q in rows:
        for k in ks_of(q["m"]):
            l = q["d"]["lag"][min(k, 7)]
            num += l[4]
            den += sum(l)
    return num / den, den


p, n_ = pooled_lag4([q for q in S if 3 <= q["m"] <= 7], lambda m: range(1, m))
res["L1"] = dict(frac_lag4=p, n_reads=n_, n_rules=sum(1 for q in S if 3 <= q["m"] <= 7), passed=bool(p >= 0.60))
say(f"L1 (m>=3): lag-4 fraction of circulating reads at colours 1..m-1 = {p:.3f} ({n_} reads, {res['L1']['n_rules']} rules) -> {'PASS' if p >= 0.60 else 'FAIL'}")
p, n_ = pooled_lag4([q for q in S if 2 <= q["m"] <= 6], lambda m: [m])
res["L2"] = dict(frac_lag4=p, n_reads=n_, passed=bool(p >= 0.50))
say(f"L2 (m>=2): lag-4 fraction of reads at colour m = {p:.3f} ({n_} reads) -> {'PASS' if p >= 0.50 else 'FAIL'}")
# full lag distribution for context (pooled over circulating reads and over killing reads)
for nm, rows, ksf in (("circulating(m>=3)", [q for q in S if 3 <= q["m"] <= 7], lambda m: range(1, m)), ("killing(m>=2)", [q for q in S if 2 <= q["m"] <= 6], lambda m: [m])):
    tot = np.zeros(41)
    for q in rows:
        for k in ksf(q["m"]):
            tot += np.array(q["d"]["lag"][min(k, 7)])
    top = np.argsort(-tot)[:6]
    say(f"   lag distribution {nm}: " + ", ".join(f"{int(i)}:{tot[i] / tot.sum():.3f}" for i in sorted(top)) + f"  (even lags share {tot[::2].sum() / tot.sum():.3f})")
r1 = {m: [] for m in (1, 2)}
r14 = {m: [] for m in (1, 2)}
for q in S:
    g = 1 if q["m"] == 1 else 2 if q["m"] >= 2 and q["m"] < len(q["rule"]) else None
    if g:
        r1[g].append(q["d"]["edge"][1] / q["B"])
        r14[g].append(q["d"]["lag"][1][4] / q["B"])
dr1, dr14 = np.mean(r1[2]) - np.mean(r1[1]), np.mean(r14[2]) - np.mean(r14[1])
res["L3"] = dict(r1_lead1=np.mean(r1[1]), r1_lead2plus=np.mean(r1[2]), r14_lead1=np.mean(r14[1]), r14_lead2plus=np.mean(r14[2]),
                 share=dr14 / dr1, passed=bool(dr14 / dr1 >= 0.70))
say(f"L3: r_1 lead1 {np.mean(r1[1]):.3f} vs lead>=2 {np.mean(r1[2]):.3f} (excess {dr1:.3f}); lag-4 part {np.mean(r14[1]):.3f} vs {np.mean(r14[2]):.3f} (excess {dr14:.3f}); "
    f"share {dr14 / dr1:.2f} -> {'PASS' if res['L3']['passed'] else 'FAIL'}")

# C1 chains (lengths 1..16 recorded)
chains = np.zeros(17)
for q in S:
    if q["m"] <= 4:
        chains += np.array(q["d"]["chain"])
ge = lambda L: chains[L:].sum()
qs = [ge(L + 1) / ge(L) for L in (1, 2, 3, 4)]
res["C1"] = dict(q=qs, n_chains=float(ge(1)), mean_len=float((np.arange(17) * chains).sum() / ge(1)),
                 passed=bool(0.45 <= qs[0] <= 0.58 and abs(qs[1] - qs[0]) <= 0.10 and abs(qs[2] - qs[0]) <= 0.10))
say(f"C1 chains (m<=4, {int(ge(1))} chains, mean length {res['C1']['mean_len']:.2f}): q1..q4 = " + ", ".join(f"{x:.3f}" for x in qs) + f" -> {'PASS' if res['C1']['passed'] else 'FAIL'}")

# N1 Little
EN, INV, M = [], [], []
for q in S:
    h = np.array(q["d"]["nb_resolved"]) + np.array(q["d"]["nb_censored"])
    EN.append((np.arange(41) * h).sum() / h.sum())
    INV.append(1 / q["c"])
    M.append(min(q["m"], 6))
EN, INV, M = map(np.array, (EN, INV, M))
ratio = np.abs(EN / INV - 1)
sl = lambda y: np.polyfit(M, y, 1)[0]
res["N1"] = dict(median_abs_ratio_minus1=float(np.median(ratio)), median_ratio=float(np.median(EN / INV)), slope_EN=sl(EN), slope_inv_c=sl(INV),
                 passed=bool(np.median(ratio) <= 0.15 and abs(sl(EN) - sl(INV)) <= 0.15))
say(f"N1 Little: median E[N_b]/(1/c) = {np.median(EN / INV):.3f}, median |ratio-1| {np.median(ratio):.3f}; slope on min(m,6): E[N_b] {sl(EN):.3f} vs 1/c {sl(INV):.3f} -> {'PASS' if res['N1']['passed'] else 'FAIL'}")

# r_k by lead from the tracer (replicates the edgestats profile)
say("tracer profile r_k by lead (mean over rules):")
for m in range(1, 7):
    rows = [q for q in S if q["m"] == m]
    if rows:
        mat = np.array([np.array(q["d"]["edge"][:m + 4]) / q["B"] for q in rows])
        say(f"  m={m} (n={len(rows)}): " + " ".join(f"{v:.2f}" for v in mat.mean(0)))

# ---------------- K4 on census (A/B) and V
rules, c = cen["rule"].to_list(), cen["c"].to_numpy()
perm = np.random.default_rng(SEED).permutation(len(rules))
A, B_ = perm[: len(perm) // 2], perm[len(perm) // 2:]
p4A = k4_fit([rules[i] for i in A], c[A])
r2B = r2(np.log(c[B_]), np.log(k4_predict([rules[i] for i in B_], p4A)))
res["K4_census"] = dict(params_A=p4A.tolist(), r2_lnc_B=r2B, passed=bool(r2B >= 0.90))
say(f"K4 fit on A: e {p4A[0]:.3f}, phi CC/CK/KC/KK = {p4A[1]:.3f} {p4A[2]:.3f} {p4A[3]:.3f} {p4A[4]:.3f}; held-out R2(ln c) on B {r2B:.3f} (lead-only 0.842, K3 0.875) -> {'PASS' if r2B >= 0.90 else 'FAIL'}")
ab = lead_fit(rules, c)
k3p = k3_fit(rules, c)
k4p = k4_fit(rules, c)
say(f"census fits: lead law a {ab[0]:.3f} b {ab[1]:.3f}; K3 psi {k3p[0]:.2f} e {k3p[1]:.3f} rho {k3p[2]:.3f}; K4 e {k4p[0]:.3f} phi {np.round(k4p[1:], 3).tolist()}")

raw = load("trace_valid_raw.jsonl")
V = [d for d in raw if (not d["escaped"]) and d["births"] >= 200 and 1.3 <= d["area"] / d["area_t0"] <= 1.9]
say(f"validation: {len(raw)} candidates, kept {len(V)} (escaped {sum(d['escaped'] for d in raw)}, births<200 {sum((not d['escaped']) and d['births'] < 200 for d in raw)})")
vr, vc = [d["spec"] for d in V], np.array([cval(d) for d in V])
vlead = np.array([run0(r) for r in vr])
say("validation lead distribution: " + ", ".join(f"{m}:{(vlead == m).sum()}" for m in range(1, 10) if (vlead == m).any()))
preds = {"lead": lead_predict(vr, ab), "K3": k3_predict(vr, k3p), "K4": k4_predict(vr, k4p)}
res["V"] = {"n": len(V)}
for nm, pr in preds.items():
    res["V"][nm] = dict(r2=r2(vc, pr), median_rel=float(np.median(np.abs(pr - vc) / vc)))
    say(f"  V {nm:5s}: R2(c) {res['V'][nm]['r2']:.3f}, median rel err {res['V'][nm]['median_rel']:.3f}")
res["V1"] = bool(res["V"]["lead"]["r2"] >= 0.80)
res["V2"] = bool(res["V"]["K3"]["r2"] >= res["V"]["lead"]["r2"] + 0.02)
res["V3"] = bool(res["V"]["K4"]["r2"] >= 0.90 and res["V"]["K4"]["r2"] >= res["V"]["K3"]["r2"] + 0.01)
res["V4"] = bool(0.80 <= k4p[1] <= 1.0 and k4p[2] <= k4p[1] - 0.10)
say(f"V1 {'PASS' if res['V1'] else 'FAIL'}; V2 {'PASS' if res['V2'] else 'FAIL'}; V3 {'PASS' if res['V3'] else 'FAIL'}; V4 (phi_CC in [0.8,1], phi_CK <= phi_CC-0.1) {'PASS' if res['V4'] else 'FAIL'}")
res["K4_params_full"] = k4p.tolist()
# validation by lead for context
for m in range(1, 7):
    s = vlead == m
    if s.sum() >= 5:
        say(f"   V lead {m}: n={s.sum()} mean c obs {vc[s].mean():.3f} lead {preds['lead'][s].mean():.3f} K3 {preds['K3'][s].mean():.3f} K4 {preds['K4'][s].mean():.3f}")

# ---------------- band S1-S5
area0 = 256 * 512  # prefilled (visited) cells; the band to be eaten is the same size
byL = {L: load(f"trace_band_L{L}.jsonl") for L in range(24, 30)}
band, chosen = [], {}
for i in range(len(byL[24])):
    pick = None
    for L in range(24, 30):                       # frozen rule: smallest L with >= 50% of the band eaten at the end
        if (byL[L][i]["area"] - area0) / area0 >= 0.5:
            pick = L
            break
    if pick is not None:
        band.append(byL[pick][i])
        chosen[byL[pick][i]["spec"]] = pick
(R / "lists/band_chosen_L.txt").write_text("\n".join(f"{k}@{v}" for k, v in chosen.items()) + "\n")
kept = [d for d in band if (d["area"] - area0) / area0 <= 0.9 and d["births"] >= 5000]
say(f"band: {len(byL[24])} rules, {len(band)} reached 50% consumption by L=29; kept {len(kept)} (consumption > 0.9: {sum((d['area'] - area0) / area0 > 0.9 for d in band)}, births<5000: {sum(d['births'] < 5000 for d in band)}); "
    f"chosen L counts: " + ", ".join(f"{L}:{sum(1 for v in chosen.values() if v == L)}" for L in range(24, 30)))
if len(kept) >= 10:
    bm = np.array([min(run0(d["spec"]), 5) for d in kept], float)
    bc = np.array([cval(d) for d in kept])
    cc = np.array([cmap[d["spec"]] for d in kept])
    a_b = np.polyfit(bm, 1 / bc, 1)
    a_c = np.polyfit(bm, 1 / cc, 1)
    corr2 = np.corrcoef(bc, cc)[0, 1] ** 2
    p0 = np.array([d["col_births"][0] / max(d["edge"][0], 1) for d in kept])
    ratio = bc / cc
    res["S"] = dict(n=len(kept), band_slope=a_b[0], band_intercept=a_b[1], census_slope_same_rules=a_c[0], census_intercept_same_rules=a_c[1],
                    corr2=corr2, p0_median=float(np.median(p0)), ratio_median=float(np.median(ratio)))
    res["S"].update(S1=bool(0.55 <= a_b[0] <= 0.85), S2=bool(1.0 <= a_b[1] <= 1.7), S3=bool(corr2 >= 0.60),
                    S4=bool(0.45 <= np.median(p0) <= 0.58), S5=bool(np.median(ratio) > 1))
    say(f"S1 band 1/c = {a_b[1]:.3f} + {a_b[0]:.3f} min(m,5) (same rules in census: {a_c[1]:.3f} + {a_c[0]:.3f}); "
        f"S1 {'PASS' if res['S']['S1'] else 'FAIL'}, S2 {'PASS' if res['S']['S2'] else 'FAIL'}")
    say(f"S3 corr^2(c_band, c_census) = {corr2:.3f} -> {'PASS' if res['S']['S3'] else 'FAIL'}; S4 median p0 {np.median(p0):.3f} -> {'PASS' if res['S']['S4'] else 'FAIL'}; "
        f"S5 median c_band/c_census {np.median(ratio):.3f} -> {'PASS' if res['S']['S5'] else 'FAIL'}")
    for m in range(1, 6):
        s = bm == m
        if s.any():
            say(f"   band lead {m}: n={s.sum()} mean c_band {bc[s].mean():.3f} mean c_census {cc[s].mean():.3f}")

(R / "stage2_analysis.json").write_text(json.dumps(res, indent=1, default=float))
(R / "stage2_analysis.txt").write_text("\n".join(lines) + "\n")
