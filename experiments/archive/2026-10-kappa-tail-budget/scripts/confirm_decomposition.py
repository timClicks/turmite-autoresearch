"""README item 5 decomposition + onset 16/256 sensitivities for confirm-v1 (written 2026-10-16 after T1/T2 were known).

Choices fixed here BEFORE running (no variants tried, apart from the labelled onset sensitivities):
  * Predictor seeds only, empirical entry-conditioned I_intersect bins pooled over seeds (as confirm_analysis.py).
    Bin k = durations [2^k, 2^(k+1)); tail = bins k >= log2(onset). Onsets 64 (primary), 16, 256 (sensitivities).
  * Model: f = mB / (mB + E_T), E_T = (1-p)*s + p*tm, p = entry fraction in tail, tm = tail conditional mean,
    s = short conditional mean (E_T = sum t / sum n, so exact). README lists three factors (p, tm, mB); the
    short mean s is a FOURTH factor needed for E_T to be exact, so it is reported as its own share (deviation noted).
  * Contrast: band 0 -> band 2 per rule (the area-scaling change T2 extrapolates over). Shapley value over all
    4! orderings of switching one factor from its band-0 to band-2 value; values sum to f2-f0 exactly.
  * Decision rule (registered here): per rule share_X = |phi_X| / sum|phi|. "Tail explanation survives" if the
    median over rules of (share_p + share_tm) > median share_mB; "only boundary transfers" (README: reject tail at
    these scales) if the median tail share < 0.25 or < median share_mB. Model counterfactuals, not causal.
  * Also: correlation across rules of model Delta f with observed Delta y (outcome seeds, band 2 - band 0).
  uv run experiments/archive/2026-10-kappa-tail-budget/scripts/confirm_decomposition.py
"""
import json, itertools
from pathlib import Path
import numpy as np
import polars as pl

EXP = Path(__file__).resolve().parents[1]
D = EXP / "dumps/confirm-v1/ants"
OUT = EXP / "results"


def rd(suffix):
    fs = sorted(D.glob(f"*.{suffix}.csv"))
    return pl.concat([pl.read_csv(f) for f in fs])


def prep(df):
    return df.with_columns(
        pl.col("spec").str.split("@").list.get(0).alias("rule"),
        (pl.col("spec").str.split("@").list.get(1).cast(pl.Int64) % 2).replace_strict({1: "pred", 0: "out"}).alias("role"))


bands, bins = prep(rd("bands")), prep(rd("bins"))
rules = sorted(bands["rule"].unique().to_list())
g = bands.filter(pl.col("role") == "pred").group_by("rule", "band").agg(
    pl.col("b_steps").sum().alias("bs"), pl.col("b_complete").sum().alias("bc"))
mB = {(r["rule"], r["band"]): r["bs"] / r["bc"] for r in g.iter_rows(named=True)}
yo = bands.filter(pl.col("role") == "out").group_by("rule", "band").agg(
    (pl.col("B").sum() / pl.col("steps").sum()).alias("y"))
y = {(r["rule"], r["band"]): r["y"] for r in yo.iter_rows(named=True)}
ii = bins.filter((pl.col("role") == "pred") & (pl.col("label") == "I_intersect")).group_by("rule", "band", "bin").agg(
    pl.col("entry_count").sum().alias("n"), pl.col("entry_time_sum").sum().alias("t"))
bn = {k: (s["bin"].to_numpy(), s["n"].to_numpy().astype(float), s["t"].to_numpy().astype(float))
      for k, s in ii.group_by(["rule", "band"])}
bn = {(k[0], k[1]): v for k, v in bn.items()}


def factors(rule, band, kmin):
    b, n, t = bn[(rule, band)]
    tl = b >= kmin
    N = n.sum()
    p = n[tl].sum() / N
    tm = t[tl].sum() / n[tl].sum()
    s = t[~tl].sum() / n[~tl].sum()
    return np.array([p, tm, s, mB[(rule, band)]])  # order: p, tail mean, short mean, mB


def f(v):
    p, tm, s, m = v
    return m / (m + (1 - p) * s + p * tm)


NAMES = ["p_tail", "tail_mean", "short_mean", "boundary_mean"]
out = {}
for onset in (64, 16, 256):
    kmin = int(np.log2(onset))
    shares, phis, rows, df_m, df_o = [], [], [], [], []
    for r in rules:
        a, b = factors(r, 0, kmin), factors(r, 2, kmin)
        phi = np.zeros(4)
        perms = list(itertools.permutations(range(4)))
        for pm in perms:
            cur = a.copy()
            for j in pm:
                before = f(cur)
                cur[j] = b[j]
                phi[j] += (f(cur) - before) / len(perms)
        assert abs(phi.sum() - (f(b) - f(a))) < 1e-12
        phis.append(phi)
        shares.append(np.abs(phi) / np.abs(phi).sum())
        df_m.append(f(b) - f(a))
        df_o.append(y[(r, 2)] - y[(r, 0)])
    S, P = np.array(shares), np.array(phis)
    med = {k: float(np.median(S[:, i])) for i, k in enumerate(NAMES)}
    tail_med = float(np.median(S[:, 0] + S[:, 1]))
    dominant = {k: int((S.argmax(1) == i).sum()) for i, k in enumerate(NAMES)}
    # signed contribution relative to total model change, pooled over rules (mean phi / mean total)
    out[str(onset)] = dict(
        median_share=med, median_tail_share_p_plus_tm=tail_med, dominant_count=dominant,
        sum_phi_over_sum_abs_delta={k: float(P[:, i].sum() / np.abs(np.array(df_m)).sum()) for i, k in enumerate(NAMES)},
        median_model_delta_f=float(np.median(df_m)), median_obs_delta_y=float(np.median(df_o)),
        corr_model_obs_delta=float(np.corrcoef(df_m, df_o)[0, 1]),
        tail_survives=bool(tail_med > med["boundary_mean"]),
        only_boundary_transfers=bool(tail_med < 0.25 or tail_med < med["boundary_mean"]))
    if onset == 64:
        pl.DataFrame({"rule": rules, **{f"phi_{k}": P[:, i] for i, k in enumerate(NAMES)},
                      "dF_model": df_m, "dY_obs": df_o}).write_csv(OUT / "confirm-v1.decomposition.csv")
(OUT / "confirm-v1.decomposition.json").write_text(json.dumps(out, indent=1))
print(json.dumps(out, indent=1))
