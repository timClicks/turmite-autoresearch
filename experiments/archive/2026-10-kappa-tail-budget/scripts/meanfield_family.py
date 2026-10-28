"""Family-F estimator (tailfit.py) on the mean-field episode bins (registered in NOTEBOOK.md).

E[T]_F = exact short sum (bins 0-5 time sums) / N + p * tail_mean_F(a_hat, H_hat); kappa_inst_F = (E[D]/(E[D]+E[T]_F))/g.
Reads results/meanfield_renewal.csv and .bins.csv (command in meanfield_renewal.py).
  uv run experiments/archive/2026-10-kappa-tail-budget/scripts/meanfield_family.py
"""
import os
for k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[k] = "1"
import hashlib, json, subprocess, sys
from pathlib import Path
import numpy as np
import polars as pl
sys.path.insert(0, str(Path(__file__).parent))
import tailfit as tf

ROOT = Path(__file__).resolve().parents[4]
EXP = Path(__file__).resolve().parents[1]
main = pl.read_csv(EXP / "results/meanfield_renewal.csv")
bins = pl.read_csv(EXP / "results/meanfield_renewal.bins.csv")
rng = np.random.default_rng([20261016, 31])


def counts(d):
    c = np.zeros(64); s = np.zeros(64)
    for b, n, t in zip(d["bin"], d["entry_count"], d["entry_time_sum"]):
        c[b] += n; s[b] += t
    return c, s


def et_family(c, s):
    N = c.sum()
    nt = c[tf.B0:].sum()
    e0 = s.sum() / N
    a, lh = tf.fit(c[tf.B0:tf.B0 + tf.NB])
    ef = (s[:tf.B0].sum() + nt * tf.tail_mean(a, lh)[0]) / N
    return e0, float(ef), float(a[0]), float(lh[0]), int(nt)


out = {"input_sha256": {"main": hashlib.sha256((EXP / "results/meanfield_renewal.csv").read_bytes()).hexdigest(),
                        "bins": hashlib.sha256((EXP / "results/meanfield_renewal.bins.csv").read_bytes()).hexdigest()},
       "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True, cwd=ROOT).strip(), "bands": {}}
for band in sorted(main["band"].unique()):
    m = main.filter(pl.col("band") == band)
    g = float(m["sum_pa"].sum() / m["steps"].sum())
    ED = float(m["b_complete_steps"].sum() / m["b_complete_n"].sum())
    c, s = counts(bins.filter(pl.col("band") == band))
    e0, ef, a, lh, nt = et_family(c, s)
    pv, dev, _, _ = tf.gof_pvalue(c[tf.B0:tf.B0 + tf.NB], rng, B=200)
    k = lambda ET: (ED / (ED + ET)) / g
    per = []
    for seed in sorted(m["seed"].unique()):
        cc, ss = counts(bins.filter((pl.col("band") == band) & (pl.col("seed") == seed)))
        _, e1, *_ = et_family(cc, ss)
        per.append(e1)
    per = np.array(per)
    out["bands"][int(band)] = dict(
        g=g, ED=ED, ET_geometric_truth=1 / g, ET_empirical=e0, ET_family=ef, a_hat=a, log2H_hat=lh, tail_events=nt,
        kappa_inst_empirical=k(e0), kappa_inst_family=k(ef), kappa_inst_geometric_truth=k(1 / g),
        gof_p=pv, gof_deviance=dev, gof_flag_p01=bool(pv < 0.01),
        single_seed_family_ET_relbias_median=float(np.median(per * g - 1)),
        single_seed_family_ET_relbias_sd=float(np.std(per * g - 1, ddof=1)),
        pass_bias_le_0p05=bool(abs(k(ef) - 1) <= 0.05))
(EXP / "results/meanfield_family.json").write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
for b, r in out["bands"].items():
    print(b, {k: (round(v, 4) if isinstance(v, float) else v) for k, v in r.items()})
