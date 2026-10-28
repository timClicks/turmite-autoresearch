"""G3: calibrate survival family F (tailfit.py) on synthetic data with known answers
plus negative controls, at the sample sizes of the planned design.

Reads ONLY results/pilot_tailbins.csv (log2 entry-duration bins; no B/I/B-over-S).
Writes results/fit_calibration.json and results/fit_calibration_cells.csv.
Every replicate has its own seeded stream default_rng([20261016, scenario, cell, rep]).
Single-threaded by design (OMP/OpenBLAS pinned to 1).

  uv run scripts/calibrate_fit.py [--reps 200] [--gof-reps 60] [--cells N]  (smoke: --cells 3 --reps 20 --gof-reps 5 --out-suffix _smoke)
"""
import os
for k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[k] = "1"
import argparse, hashlib, json, sys, time
from pathlib import Path
import numpy as np
import polars as pl
from scipy import stats
sys.path.insert(0, str(Path(__file__).parent))
import tailfit as tf

EXP = Path(__file__).resolve().parents[1]
ROOT = Path(__file__).resolve().parents[4]
SEED = 20261016
ap = argparse.ArgumentParser()
ap.add_argument("--reps", type=int, default=200)
ap.add_argument("--gof-reps", type=int, default=60)
ap.add_argument("--gof-boot", type=int, default=100)
ap.add_argument("--cells", type=int, default=0)
ap.add_argument("--out-suffix", default="")
args = ap.parse_args()

df = pl.read_csv(EXP / "results/pilot_tailbins.csv")
T_ALL = np.arange(1, 64)
SHORT_BIN = np.floor(np.log2(T_ALL)).astype(int)


def pooled(rule, band, seeds=None):
    d = df.filter((pl.col("rule") == rule) & (pl.col("band") == band))
    if seeds is not None:
        d = d.filter(pl.col("seed").is_in(seeds))
    c = np.zeros(64); s = np.zeros(64)
    for b, n, t in zip(d["bin"], d["entry_count"], d["entry_time_sum"]):
        c[b] += n; s[b] += t
    return c, s


rules = sorted(df["rule"].unique())
seeds = sorted(df["seed"].unique())
cells = []
for r in rules:
    for band in (0, 1, 2):
        c, s = pooled(r, band)
        if c[tf.B0:].sum() >= 3:
            cells.append((r, band, c, s))
skipped = 3 * len(rules) - len(cells)
if args.cells:
    cells = cells[:: max(1, len(cells) // args.cells)][: args.cells]


def short_law(c):
    """T in 1..63 with P ∝ bin mass / bin width (uniform integers inside each bin)."""
    w = c[:6] / max(c[:6].sum(), 1)
    q = w[SHORT_BIN] / (2.0 ** SHORT_BIN)
    return q / q.sum()


def rng_for(scn, cell, rep):
    return np.random.default_rng([SEED, scn, cell, rep])


def sim_infamily(cell_i, truth, rep, rng):
    N, p, q, a, lh = truth["N"], truth["p"], truth["q"], truth["a"], truth["lh"]
    nt = rng.binomial(N, p)
    t = tf.sample_tail(a, lh, nt, rng) if nt else np.zeros(0)
    sc = rng.multinomial(N - nt, q)
    s_short = float((sc * T_ALL).sum())
    return N, nt, s_short, t


def estimate(N, nt, s_short, t):
    e0 = (s_short + t.sum()) / N
    if nt == 0:
        return e0, e0, np.nan, np.nan, None
    counts = tf.tail_counts(t)
    ah, lhh = tf.fit(counts)
    m = tf.tail_mean(ah, lhh)[0]
    return e0, (s_short + nt * m) / N, ah[0], lhh[0], counts


cell_rows = []
t0 = time.time()
# ---------------- scenario 1: in-family known answer ----------------
inf = []
for ci, (rule, band, c, s) in enumerate(cells):
    ah, lhh = tf.fit(c[tf.B0:tf.B0 + tf.NB])
    jr = np.random.default_rng([SEED, 0, ci, 99999])
    a_true = float(np.clip(ah[0] + jr.uniform(-0.025, 0.025), 0.06, 3.95))
    lh_true = float(np.clip(lhh[0] + jr.uniform(-0.125, 0.125), 6.6, 39.9))
    q = short_law(c)
    N4 = c.sum()
    truth = dict(N=int(4 * N4), p=float(c[tf.B0:].sum() / N4), q=q, a=a_true, lh=lh_true)
    m_tail = float(tf.tail_mean(a_true, lh_true)[0])
    truth["E"] = (1 - truth["p"]) * float((q * T_ALL).sum()) + truth["p"] * m_tail
    e0s, e1s, ahs, lhs = [], [], [], []
    for rep in range(args.reps):
        rng = rng_for(1, ci, rep)
        N, nt, ss, t = sim_infamily(ci, truth, rep, rng)
        e0, e1, ah_, lh_, _ = estimate(N, nt, ss, t)
        e0s.append(e0); e1s.append(e1); ahs.append(ah_); lhs.append(lh_)
    e0s, e1s, ahs, lhs = map(np.array, (e0s, e1s, ahs, lhs))
    E = truth["E"]
    # GOF size under in-family truth
    pv = []
    for rep in range(args.gof_reps):
        rng = rng_for(2, ci, rep)
        N, nt, ss, t = sim_infamily(ci, truth, rep, rng)
        if nt >= 3:
            pv.append(tf.gof_pvalue(tf.tail_counts(t), rng, args.gof_boot)[0])
    pv = np.array(pv)
    inf.append(dict(
        rule=rule, band=band, pilot_tail_events=int(c[tf.B0:].sum()), N=truth["N"], p=truth["p"], a_true=a_true, lh_true=lh_true, E_true=E,
        tail_events_mean=float(truth["N"] * truth["p"]),
        e0_med_relbias=float(np.median(e0s / E - 1)), e1_med_relbias=float(np.median(e1s / E - 1)),
        e0_rmse_log=float(np.sqrt(np.mean(np.log(e0s / E) ** 2))), e1_rmse_log=float(np.sqrt(np.mean(np.log(e1s / E) ** 2))),
        e0_mean_relbias=float(np.mean(e0s / E - 1)), e1_mean_relbias=float(np.mean(e1s / E - 1)),
        a_med_bias=float(np.nanmedian(ahs - a_true)), lh_med_bias=float(np.nanmedian(lhs - lh_true)),
        gof_n=int(len(pv)), gof_rej01=float((pv < 0.01).mean()) if len(pv) else np.nan, gof_rej05=float((pv < 0.05).mean()) if len(pv) else np.nan))
    print(f"[1] cell {ci+1}/{len(cells)} {rule} b{band} {time.time()-t0:.0f}s", flush=True)

# ---------------- scenario 2: misspecified, realistic shape (pilot empirical bins) ----------------
EXACT_BIN_MEAN = {}
for b in range(0, 21):                      # E[floor(2^(b+U))] for log-uniform on integers in [2^b, 2^(b+1))
    t = np.arange(2 ** b, 2 ** (b + 1), dtype=float)
    pm = np.log((t + 1) / t) / np.log(2)
    EXACT_BIN_MEAN[b] = float((t * pm).sum())


def bin_mean(b):
    return EXACT_BIN_MEAN[b] if b in EXACT_BIN_MEAN else 2.0 ** b / np.log(2) - 0.5


mis = []
for ci, (rule, band, c, s) in enumerate(cells):
    N4 = c.sum()
    N = int(4 * N4)
    qb = c / N4
    E_true = sum(qb[b] * bin_mean(b) for b in range(64) if qb[b] > 0)
    e0s, e1s = [], []
    rej = []
    for rep in range(args.reps):
        rng = rng_for(3, ci, rep)
        nb = rng.multinomial(N, qb)
        ss = 0.0; tails = []
        for b in np.nonzero(nb)[0]:
            x = np.floor(2.0 ** (b + rng.random(nb[b])))
            if b < tf.B0:
                ss += x.sum()
            else:
                tails.append(x)
        t = np.concatenate(tails) if tails else np.zeros(0)
        e0, e1, _, _, counts = estimate(N, len(t), ss, t)
        e0s.append(e0); e1s.append(e1)
        if rep < args.gof_reps and len(t) >= 3:
            rej.append(tf.gof_pvalue(counts, rng, args.gof_boot)[0])
    e0s, e1s, rej = map(np.array, (e0s, e1s, rej))
    mis.append(dict(rule=rule, band=band, pilot_tail_events=int(c[tf.B0:].sum()), E_true=float(E_true),
                    e0_med_relbias=float(np.median(e0s / E_true - 1)), e1_med_relbias=float(np.median(e1s / E_true - 1)),
                    e0_rmse_log=float(np.sqrt(np.mean(np.log(e0s / E_true) ** 2))), e1_rmse_log=float(np.sqrt(np.mean(np.log(e1s / E_true) ** 2))),
                    gof_n=int(len(rej)), gof_rej01=float((rej < 0.01).mean()) if len(rej) else np.nan,
                    gof_rej05=float((rej < 0.05).mean()) if len(rej) else np.nan))
    print(f"[2] cell {ci+1}/{len(cells)} {time.time()-t0:.0f}s", flush=True)

# ---------------- scenario 3: negative controls with simple known laws ----------------
def lognormal_mixture_mean(w, mu, sg, short_mean):
    k = np.arange(2, 20_000_001, dtype=float)
    ex = 1 + stats.lognorm.sf(k, s=sg, scale=np.exp(mu)).sum()
    return (1 - w) * short_mean + w * ex


neg = {}
N = 66000
for name in ("geometric_mean20", "lognormal_tail", "geometric_mean4_notail"):
    e0s, e1s, rej, flags = [], [], [], 0
    if name == "geometric_mean20":
        E_true = 20.0
    elif name == "geometric_mean4_notail":
        E_true = 4.0
    else:
        E_true = lognormal_mixture_mean(0.05, np.log(300), 1.0, 3.0)
    n_tail_zero = 0
    for rep in range(args.reps):
        rng = rng_for(4, {"geometric_mean20": 0, "lognormal_tail": 1, "geometric_mean4_notail": 2}[name], rep)
        if name.startswith("geometric"):
            t_all = rng.geometric(1 / (20.0 if name == "geometric_mean20" else 4.0), N).astype(float)
        else:
            m = rng.random(N) < 0.05
            t_all = np.where(m, np.maximum(1, np.floor(np.exp(rng.normal(np.log(300), 1.0, N)))), rng.geometric(1 / 3.0, N)).astype(float)
        short = t_all < tf.U0
        ss = t_all[short].sum(); t = t_all[~short]
        e0, e1, _, _, counts = estimate(N, len(t), ss, t)
        e0s.append(e0); e1s.append(e1)
        if len(t) == 0:
            n_tail_zero += 1
        elif rep < args.gof_reps and len(t) >= 3:
            rej.append(tf.gof_pvalue(counts, rng, args.gof_boot)[0])
    e0s, e1s, rej = map(np.array, (e0s, e1s, rej))
    neg[name] = dict(E_true=float(E_true), e0_med_relbias=float(np.median(e0s / E_true - 1)), e1_med_relbias=float(np.median(e1s / E_true - 1)),
                     e0_rmse_log=float(np.sqrt(np.mean(np.log(e0s / E_true) ** 2))), e1_rmse_log=float(np.sqrt(np.mean(np.log(e1s / E_true) ** 2))),
                     reps_without_any_tail_event=int(n_tail_zero), gof_n=int(len(rej)),
                     gof_reject_rate_p01=float((rej < 0.01).mean()) if len(rej) else None)
    print(f"[3] {name} {time.time()-t0:.0f}s", flush=True)

# ---------------- scenario 4: independent right-censoring ----------------
cens = []
for ci, (rule, band, c, s) in enumerate(cells):
    ah, lhh = tf.fit(c[tf.B0:tf.B0 + tf.NB])
    a_true, lh_true = float(ah[0]), float(lhh[0])
    q = short_law(c); N4 = c.sum(); p = c[tf.B0:].sum() / N4
    N = int(4 * N4); Htrue = 2.0 ** lh_true
    E = (1 - p) * float((q * T_ALL).sum()) + p * float(tf.tail_mean(a_true, lh_true)[0])
    inb, naive_b, wid, ncen = 0, [], [], []
    for rep in range(max(args.reps // 2, 10)):
        rng = rng_for(5, ci, rep)
        nt = rng.binomial(N, p)
        t = tf.sample_tail(a_true, lh_true, nt, rng)
        sc = rng.multinomial(N - nt, q); ss = float((sc * T_ALL).sum())
        horizon = np.floor(Htrue * rng.random(nt) ** 2)           # independent follow-up horizon per episode
        cens_m = t > horizon
        lo = (ss + np.where(cens_m, horizon, t).sum()) / N
        hi = (ss + np.where(cens_m, Htrue, t).sum()) / N
        inb += (lo <= E <= hi)
        naive_b.append((ss + t[~cens_m].sum()) / (N - cens_m.sum()) / E - 1)
        wid.append((hi - lo) / E); ncen.append(cens_m.sum() / max(nt, 1))
    cens.append(dict(rule=rule, band=band, coverage=inb / max(args.reps // 2, 10), median_width_over_E=float(np.median(wid)),
                     median_naive_completed_only_relbias=float(np.median(naive_b)), median_censored_frac_of_tail=float(np.median(ncen))))
    print(f"[4] cell {ci+1}/{len(cells)} {time.time()-t0:.0f}s", flush=True)

# ---------------- pilot split-seed descriptive check (tail data only) ----------------
split = []
for rule, band, c, s in cells:
    for A, B in (([seeds[0], seeds[1]], [seeds[2], seeds[3]]), ([seeds[2], seeds[3]], [seeds[0], seeds[1]])):
        cA, sA = pooled(rule, band, A); cB, sB = pooled(rule, band, B)
        if cA[tf.B0:].sum() < 3 or cB.sum() == 0:
            continue
        N_A, N_B = cA.sum(), cB.sum()
        target = sB.sum() / N_B
        e0 = sA.sum() / N_A
        ah, lhh = tf.fit(cA[tf.B0:tf.B0 + tf.NB])
        e1 = (sA[:tf.B0].sum() + cA[tf.B0:].sum() * tf.tail_mean(ah, lhh)[0]) / N_A
        split.append(dict(rule=rule, band=band, tail_events_A=int(cA[tf.B0:].sum()), target=float(target), e0=float(e0), e1=float(e1)))
sp = pl.DataFrame(split).with_columns(
    (pl.col("e0") / pl.col("target")).log().abs().alias("err0"), (pl.col("e1") / pl.col("target")).log().abs().alias("err1"))

# ---------------- criteria ----------------
I = pl.DataFrame(inf); M = pl.DataFrame(mis); C = pl.DataFrame(cens)
big = M.filter(pl.col("pilot_tail_events") >= 30)
crit = {}
crit["C1_median_abs_relbias_e1"] = float(I["e1_med_relbias"].abs().median())
crit["C1_frac_cells_abs_relbias_le_0.15"] = float((I["e1_med_relbias"].abs() <= 0.15).mean())
crit["C1_median_alpha_bias"] = float(I["a_med_bias"].median())
crit["C1_pass"] = bool(crit["C1_median_abs_relbias_e1"] <= 0.05 and crit["C1_frac_cells_abs_relbias_le_0.15"] >= 0.9 and abs(crit["C1_median_alpha_bias"]) <= 0.10)
crit["C2_frac_cells_e1_beats_e0_rmse"] = float((I["e1_rmse_log"] < I["e0_rmse_log"]).mean())
crit["C2_pass"] = bool(crit["C2_frac_cells_e1_beats_e0_rmse"] >= 0.70)
gi = I.filter(pl.col("gof_n") > 0)
crit["C3_size_in_family_rej01"] = float((gi["gof_rej01"] * gi["gof_n"]).sum() / gi["gof_n"].sum())
crit["C3_size_in_family_rej05"] = float((gi["gof_rej05"] * gi["gof_n"]).sum() / gi["gof_n"].sum())
gb = big.filter(pl.col("gof_n") > 0)
crit["C3_power_misspecified_real_shape_rej01_pooled"] = float((gb["gof_rej01"] * gb["gof_n"]).sum() / gb["gof_n"].sum()) if len(gb) else None
crit["C3_cells_ge30_tail_events"] = int(len(gb))
crit["C3_pass"] = bool(crit["C3_size_in_family_rej01"] <= 0.10 and crit["C3_power_misspecified_real_shape_rej01_pooled"] is not None
                       and crit["C3_power_misspecified_real_shape_rej01_pooled"] >= 0.80)
crit["C3_misspecified_e1_vs_e0_rmse_win_frac"] = float((M["e1_rmse_log"] < M["e0_rmse_log"]).mean())
crit["C3_misspecified_median_abs_relbias_e1"] = float(M["e1_med_relbias"].abs().median())
crit["C3_misspecified_median_abs_relbias_e0"] = float(M["e0_med_relbias"].abs().median())
crit["C4_geometric20_gof_reject"] = neg["geometric_mean20"]["gof_reject_rate_p01"]
crit["C4_lognormal_gof_reject"] = neg["lognormal_tail"]["gof_reject_rate_p01"]
crit["C4_pass"] = bool(all(v is not None and v >= 0.80 for v in (crit["C4_geometric20_gof_reject"], crit["C4_lognormal_gof_reject"])))
crit["C5_min_coverage"] = float(C["coverage"].min()); crit["C5_frac_cells_cov_ge_0.99"] = float((C["coverage"] >= 0.99).mean())
crit["C5_median_width_over_E"] = float(C["median_width_over_E"].median())
crit["C5_median_naive_completed_only_relbias"] = float(C["median_naive_completed_only_relbias"].median())
crit["C5_pass"] = bool(crit["C5_frac_cells_cov_ge_0.99"] >= 0.99)
crit["pilot_split_check"] = dict(n=int(len(sp)), median_abs_log_err_empirical=float(sp["err0"].median()), median_abs_log_err_family=float(sp["err1"].median()),
                                 family_better_frac=float((sp["err1"] < sp["err0"]).mean()))
crit["ALL_PASS"] = bool(crit["C1_pass"] and crit["C2_pass"] and crit["C3_pass"] and crit["C4_pass"] and crit["C5_pass"])
out = dict(command="uv run experiments/archive/2026-10-kappa-tail-budget/scripts/calibrate_fit.py " + " ".join(sys.argv[1:]),
           seed=SEED, reps=args.reps, gof_reps=args.gof_reps, gof_boot=args.gof_boot, cells=len(cells), cells_skipped_lt3_tail_events=skipped,
           input_sha256=hashlib.sha256((EXP / "results/pilot_tailbins.csv").read_bytes()).hexdigest(),
           source_sha256=dict(calibrate_fit=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                              tailfit=hashlib.sha256((EXP / "scripts/tailfit.py").read_bytes()).hexdigest()),
           grid=dict(alpha=[float(tf.ALPHAS[0]), float(tf.ALPHAS[-1]), 0.05], log2H=[float(tf.LOGH[0]), float(tf.LOGH[-1]), 0.25]),
           criteria=crit, negative_controls=neg, runtime_seconds=time.time() - t0)
sfx = args.out_suffix
(EXP / f"results/fit_calibration{sfx}.json").write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
I.with_columns(pl.lit("in_family").alias("scenario")).write_csv(EXP / f"results/fit_calibration_infamily{sfx}.csv")
M.with_columns(pl.lit("misspecified_real_shape").alias("scenario")).write_csv(EXP / f"results/fit_calibration_misspecified{sfx}.csv")
C.write_csv(EXP / f"results/fit_calibration_censoring{sfx}.csv")
sp.write_csv(EXP / f"results/fit_pilot_split{sfx}.csv")
print(json.dumps(crit, indent=1))
