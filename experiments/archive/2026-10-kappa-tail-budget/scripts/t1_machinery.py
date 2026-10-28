"""G4: operating characteristics of the T1 decision rule on SYNTHETIC outcomes (no ant outcome used).

Rule-level quantities: tail law (p, a, H, short law, N) from the pilot-fitted TAIL bins of the
44 rules at bands 0 and 1 (results/pilot_tailbins.csv only); boundary mean sojourn m_B and P/A
are synthetic nuisance regressors (independent log-normals) because B/I/B-over-S pilot columns are off limits.

Predictor side is simulated honestly: 16 predictor seeds pooled -> episode bins -> estimate E[T] with
family F (E1) or the empirical binned mean (E0). Outcome: logit y = (1-lam)*baseline + lam*renewal
identity m_B/(m_B+E_T) (+ rule noise u, + seed-averaging noise sig/sqrt(16)). lam=0 is the null
(outcome independent of the tail given baseline regressors); lam=1 is the mechanism being true.

T1 statistic per band: PRESS-based leave-one-rule-out R2(full) - R2(baseline), baseline regressors
(log m_B, log P/A), full adds log E[T]-hat. Lower bound: 2000-draw percentile rule bootstrap over the
fixed leave-one-out residual pairs (rules resampled with replacement), seed 20261016.
T1 verdict = gain >= 0.10 and lower bound > 0 at BOTH bands 0 and 1 (thresholds unchanged from README).

  uv run scripts/t1_machinery.py [--sims 300] [--smoke]
"""
import os
for k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[k] = "1"
import argparse, hashlib, json, sys, time
from pathlib import Path
import numpy as np
import polars as pl
sys.path.insert(0, str(Path(__file__).parent))
import tailfit as tf

EXP = Path(__file__).resolve().parents[1]
SEED = 20261016
ap = argparse.ArgumentParser()
ap.add_argument("--sims", type=int, default=300)
ap.add_argument("--boot", type=int, default=2000)
ap.add_argument("--smoke", action="store_true")
args = ap.parse_args()
if args.smoke:
    args.sims, args.boot = 6, 200
df = pl.read_csv(EXP / "results/pilot_tailbins.csv")
rules = sorted(df["rule"].unique())
T_ALL = np.arange(1, 64)
SB = np.floor(np.log2(T_ALL)).astype(int)


def pooled(rule, band):
    d = df.filter((pl.col("rule") == rule) & (pl.col("band") == band))
    c = np.zeros(64)
    for b, n in zip(d["bin"], d["entry_count"]):
        c[b] += n
    return c


def truth(c):
    N4 = c.sum()
    w = c[:6] / max(c[:6].sum(), 1)
    q = w[SB] / (2.0 ** SB); q /= q.sum()
    nt = c[tf.B0:].sum()
    if nt >= 3:
        a, lh = tf.fit(c[tf.B0:tf.B0 + tf.NB])
        a, lh = float(a[0]), float(lh[0]); p = nt / N4
    else:
        a, lh, p = 1.0, 10.0, 0.0
    ET = (1 - p) * float((q * T_ALL).sum()) + p * float(tf.tail_mean(a, lh)[0])
    return dict(N=int(4 * N4), p=p, q=q, a=a, lh=lh, ET=ET)


T = {(r, k): truth(pooled(r, k)) for r in rules for k in (0, 1)}

# Real geometry: mean P/A at the mid-band census row over the pilot starts (area, P only).
cen = pl.read_csv(EXP / "results/pilot-v2.ants.census.csv").with_columns(
    rule=pl.col("spec").str.split("@").list.first(),
    pa=pl.col("P") / pl.col("area"))
cen = cen.with_columns(rank=pl.col("target").rank("ordinal").over("spec", "band"))
G = {(r, k): float(cen.filter((pl.col("rule") == r) & (pl.col("band") == k) & (pl.col("rank") == 2))["pa"].mean())
     for r in rules for k in (0, 1)}


def predictor_estimates(tr, rng, kind):
    nt = rng.binomial(tr["N"], tr["p"])
    t = tf.sample_tail(tr["a"], tr["lh"], nt, rng) if nt else np.zeros(0)
    ss = float((rng.multinomial(tr["N"] - nt, tr["q"]) * T_ALL).sum())
    e0 = (ss + t.sum()) / tr["N"]
    if nt < 3 or kind == "e0":
        return e0
    a, lh = tf.fit(tf.tail_counts(t))
    return (ss + nt * tf.tail_mean(a, lh)[0]) / tr["N"]


def press_gain(y, Xb, Xf):
    def loo(X):
        X1 = np.column_stack([np.ones(len(y)), X])
        H = X1 @ np.linalg.pinv(X1)
        e = (y - H @ y) / (1 - np.diag(H))
        return e
    eb, ef = loo(Xb), loo(Xf)
    sst = ((y - y.mean()) ** 2).sum()
    return eb, ef, sst


def decide(y, Xb, Xf, rng):
    eb, ef, sst = press_gain(y, Xb, Xf)
    gain = ((eb ** 2).sum() - (ef ** 2).sum()) / sst
    idx = rng.integers(0, len(y), (args.boot, len(y)))
    sstb = np.array([((y[i] - y[i].mean()) ** 2).sum() for i in idx])
    gb = ((eb[idx] ** 2).sum(1) - (ef[idx] ** 2).sum(1)) / sstb
    lo = np.quantile(gb, 0.025)
    return gain, lo, bool(gain >= 0.10 and lo > 0)


def one_sim(sim, lam, sig, kind, nl):
    rng = np.random.default_rng([SEED, 7, sim, int(lam * 100), int(sig * 100), 0 if kind == "e0" else 1, int(nl)])
    n = len(rules)
    lmB = rng.normal(np.log(3.0), 0.3, n)
    verdicts, gains = [], []
    for k in (0, 1):
        ET = np.array([T[(r, k)]["ET"] for r in rules])
        lg = np.log(np.array([G[(r, k)] for r in rules]))
        mB = np.exp(lmB)
        ren = np.log(mB / ET)                                  # logit of m_B/(m_B+E_T) up to its own sign convention: logit(mB/(mB+ET)) = log(mB/ET)
        z = lambda v: (v - v.mean()) / v.std()
        if nl:   # curvature in log P/A and an m_B x P/A interaction that a linear baseline cannot fit
            zg, zm = z(lg), z(lmB)
            raw = 0.5 * zm + 0.5 * zg + 0.7 * (zg ** 2 - 1) / np.sqrt(2) + 0.3 * zm * zg
            base = ren.mean() + ren.std() * (raw - raw.mean()) / raw.std()
        else:
            base = ren.mean() + ren.std() * (0.7 * z(lmB) + 0.7 * z(lg)) / np.sqrt(0.98)
        eta = (1 - lam) * base + lam * ren + rng.normal(0, 0.2, n)
        y = eta + rng.normal(0, sig / 4.0, n)                  # 16 seeds averaged
        Eh = np.array([predictor_estimates(T[(r, k)], rng, kind) for r in rules])
        mBh = lmB + rng.normal(0, 0.03, n); lgh = lg + rng.normal(0, 0.02, n)
        Xb = np.column_stack([mBh, lgh]); Xf = np.column_stack([mBh, lgh, np.log(Eh)])
        g, lo, v = decide(y, Xb, Xf, rng)
        verdicts.append(v); gains.append(g)
    return all(verdicts), gains


rows = []
t0 = time.time()
for sig in (0.1, 0.3):
    for lam in (0.0, 0.5, 1.0):
      for nl in (False, True):
        for kind in ("e1", "e0"):
            res = [one_sim(s, lam, sig, kind, nl) for s in range(args.sims)]
            rows.append(dict(seed_noise_sd_logit=sig, lam=lam, baseline="nonlinear" if nl else "linear", estimator={"e1": "family F", "e0": "empirical binned"}[kind],
                             sims=args.sims, t1_positive_rate=float(np.mean([r[0] for r in res])),
                             median_gain_band0=float(np.median([r[1][0] for r in res])),
                             median_gain_band1=float(np.median([r[1][1] for r in res]))))
            print(rows[-1], f"{time.time()-t0:.0f}s", flush=True)
out = pl.DataFrame(rows)
sfx = "_smoke" if args.smoke else ""
out.write_csv(EXP / f"results/t1_machinery{sfx}.csv")
null = out.filter(pl.col("lam") == 0)
pos = out.filter((pl.col("lam") == 1) & (pl.col("seed_noise_sd_logit") == 0.1))   # registered: power gated at sig=0.1; sig=0.3 reported in the CSV only
summary = dict(command="uv run experiments/archive/2026-10-kappa-tail-budget/scripts/t1_machinery.py" + (" --smoke" if args.smoke else ""),
               seed=SEED, sims=args.sims, boot=args.boot,
               input_sha256=hashlib.sha256((EXP / "results/pilot_tailbins.csv").read_bytes()).hexdigest(),
               source_sha256=dict(t1_machinery=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), tailfit=hashlib.sha256((EXP / "scripts/tailfit.py").read_bytes()).hexdigest()),
               null_false_positive_max_family=float(null.filter(pl.col("estimator") == "family F")["t1_positive_rate"].max()),
               null_false_positive_max_empirical=float(null.filter(pl.col("estimator") == "empirical binned")["t1_positive_rate"].max()),
               power_lam1_min_family=float(pos.filter(pl.col("estimator") == "family F")["t1_positive_rate"].min()),
               power_lam1_min_empirical=float(pos.filter(pl.col("estimator") == "empirical binned")["t1_positive_rate"].min()),
               G4_pass_family=None, runtime_seconds=time.time() - t0)
summary["G4_pass_family"] = bool(summary["null_false_positive_max_family"] <= 0.075 and summary["power_lam1_min_family"] >= 0.80)
summary["G4_pass_empirical"] = bool(summary["null_false_positive_max_empirical"] <= 0.075 and summary["power_lam1_min_empirical"] >= 0.80)
(EXP / f"results/t1_machinery{sfx}.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
print(json.dumps(summary, indent=1))
