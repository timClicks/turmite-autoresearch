"""Confirmation analysis T1/T2 for confirm-v1, as registered in README (2026-10-16).

Written AFTER confirm-v1 finished but BEFORE any outcome column (B, steps -> B/S) was looked at; the
only things inspected were audit totals and column names. Interpretation choices where the
registration is silent (fixed here, not tuned):
  * B/S = B / steps in the band (bands.csv), per start; outcome y = mean over outcome seeds (odd last digit... see ROLE).
  * m_B = b_steps / b_complete (complete-contained boundary episodes), pooled over predictor seeds.
  * E[T] = sum entry_time_sum / sum entry_count over I_intersect bins, pooled over predictor seeds
    (empirical binned mean; family F not frozen). q999 = upper edge of the bin where cumulative entry count reaches 0.999.
  * log P/A at band start = log mean over predictor seeds of P/area at the census row with target == band lo.
  * T1 = leave-one-rule-out PRESS R2 gain (OLS, intercept), full adds log E[T]; bootstrap over fixed LOO residual
    pairs, 2000 draws, seed 2026101599, 95% percentile lower bound.
  * T2 primary prediction = renewal identity m_B/(m_B+E_T) from log-area-extrapolated (bands 0,1 -> 2, x = log band lo)
    predictor-seed parameters. Registered text does not say whether a P/A rescaling enters; reported as a variant
    (identity scaled by extrapolated (P/A)/(P/A at band 1) is NOT used: kept to the single identity to avoid a forking path).
    Comparators: q999 (identity with E_T replaced by extrapolated q999 times the band-1 E_T/q999 ratio) and persistence
    (extrapolate log y of outcome seeds linearly in log area).
  uv run experiments/archive/2026-10-kappa-tail-budget/scripts/confirm_analysis.py
"""
import json, hashlib
from pathlib import Path
import numpy as np
import polars as pl

EXP = Path(__file__).resolve().parents[1]
D = EXP / "dumps/confirm-v1/ants"
OUT = EXP / "results"
BOOT_SEED = 2026101599
LO = {0: 32768, 1: 131072, 2: 524288}


def rd(suffix):
    fs = sorted(D.glob(f"*.{suffix}.csv"))
    return pl.concat([pl.read_csv(f).with_columns(pl.lit(f.name.split(".")[0]).alias("stem")) for f in fs])


def prep(df):
    return df.with_columns(
        pl.col("spec").str.split("@").list.get(0).alias("rule"),
        pl.col("spec").str.split("@").list.get(1).cast(pl.Int64).alias("seed"),
    ).with_columns((pl.col("seed") % 2).replace_strict({1: "pred", 0: "out"}).alias("role"))


bands = prep(rd("bands"))
bins = prep(rd("bins"))
census = prep(pl.read_csv(OUT / "confirm-v1.ants.census.csv"))
rules = sorted(bands["rule"].unique().to_list())

# --- reliability gates
bands = bands.with_columns((pl.col("unresolved_overlap") / pl.col("steps")).alias("unres"))
ok = bands.filter((pl.col("reached_hi") == 1) & (pl.col("reached_lo") == 1))
cnt = ok.group_by("rule", "band", "role").len()
gate = {}
for b in (0, 1, 2):
    c = cnt.filter(pl.col("band") == b)
    good = c.group_by("rule").agg((pl.col("len") >= 12).all() & (pl.len() == 2)).get_column("len").sum()
    unres = bands.filter(pl.col("band") == b)
    gate[b] = dict(rules_with_12_per_role=int(good), n_rules=len(rules),
                   unresolved_fraction=float(unres["unresolved_overlap"].sum() / unres["steps"].sum()))
print("gate", gate)

# --- per rule/band/role parameters
def params(role):
    rows = {}
    bb = bands.filter(pl.col("role") == role)
    g = bb.group_by("rule", "band").agg(
        pl.col("b_steps").sum().alias("bs"), pl.col("b_complete").sum().alias("bc"),
        pl.col("B").sum().alias("B"), pl.col("steps").sum().alias("S"),
        pl.col("sum_pa").sum().alias("spa"))
    for r in g.iter_rows(named=True):
        rows[(r["rule"], r["band"])] = dict(mB=r["bs"] / r["bc"], B=r["B"], S=r["S"])
    ii = bins.filter((pl.col("role") == role) & (pl.col("label") == "I_intersect")).group_by("rule", "band", "bin").agg(
        pl.col("entry_count").sum().alias("n"), pl.col("entry_time_sum").sum().alias("t")).sort("bin")
    for (rule, band), s in ii.group_by(["rule", "band"], maintain_order=True):
        n, t = s["n"].to_numpy(), s["t"].to_numpy()
        cum = np.cumsum(n) / n.sum()
        k = int(np.searchsorted(cum, 0.999))
        rows[(rule, band)].update(ET=t.sum() / n.sum(), q999=2.0 ** (s["bin"].to_numpy()[k] + 1))
    pa = census.filter(pl.col("role") == role).with_columns(
        pl.col("band").alias("b"), (pl.col("P") / pl.col("area")).alias("pa"))
    pa = pa.filter(pl.col("target") == pl.col("b").replace_strict(LO)).group_by("rule", "b").agg(pl.col("pa").mean())
    for r in pa.iter_rows(named=True):
        rows[(r["rule"], r["b"])]["PA"] = r["pa"]
    return rows


pred = params("pred")
outc = params("out")
y = {k: v["B"] / v["S"] for k, v in outc.items()}


def press_resid(X, yv):
    n = len(yv)
    H = X @ np.linalg.pinv(X.T @ X) @ X.T
    e = yv - H @ yv
    return e / (1 - np.diag(H))


def t1(band, extra="ET", seed=BOOT_SEED):
    yv = np.array([y[(r, band)] for r in rules])
    mB = np.log([pred[(r, band)]["mB"] for r in rules])
    pa = np.log([pred[(r, band)]["PA"] for r in rules])
    ex = np.log([pred[(r, band)][extra] for r in rules])
    one = np.ones(len(rules))
    eb = press_resid(np.c_[one, mB, pa], yv)
    ef = press_resid(np.c_[one, mB, pa, ex], yv)

    def gain(idx):
        yy = yv[idx]
        sst = ((yy - yy.mean()) ** 2).sum()
        return (eb[idx] ** 2).sum() / sst - (ef[idx] ** 2).sum() / sst
    g = gain(np.arange(len(rules)))
    rng = np.random.default_rng(seed)
    bs = np.array([gain(rng.integers(0, len(rules), len(rules))) for _ in range(2000)])
    return dict(gain=float(g), lo95=float(np.percentile(bs, 2.5)), hi95=float(np.percentile(bs, 97.5)),
                r2_base=float(1 - (eb ** 2).sum() / ((yv - yv.mean()) ** 2).sum()))


res = {"gate": gate, "T1": {}, "T1_q999": {}}
for b in (0, 1):
    res["T1"][b] = t1(b, "ET")
    res["T1_q999"][b] = t1(b, "q999")
res["T1_pass"] = all(res["T1"][b]["gain"] >= 0.10 and res["T1"][b]["lo95"] > 0 for b in (0, 1))
res["T1_q999_pass"] = all(res["T1_q999"][b]["gain"] >= 0.10 and res["T1_q999"][b]["lo95"] > 0 for b in (0, 1))


def extrap(v0, v1):  # log-linear in log area from lo0 -> lo1 -> lo2
    s = (np.log(v1) - np.log(v0)) / (np.log(LO[1]) - np.log(LO[0]))
    return float(np.exp(np.log(v1) + s * (np.log(LO[2]) - np.log(LO[1]))))


errs = {"identity": [], "q999": [], "persistence": []}
rows = []
for r in rules:
    p0, p1 = pred[(r, 0)], pred[(r, 1)]
    mB2, ET2, q2 = (extrap(p0[k], p1[k]) for k in ("mB", "ET", "q999"))
    yobs = y[(r, 2)]
    ident = mB2 / (mB2 + ET2)
    qq = mB2 / (mB2 + q2 * p1["ET"] / p1["q999"])
    pers = extrap(y[(r, 0)], y[(r, 1)])
    for k, v in (("identity", ident), ("q999", qq), ("persistence", pers)):
        errs[k].append(abs(v - yobs) / yobs)
    rows.append(dict(rule=r, y_out_band2=yobs, identity=ident, q999=qq, persistence=pers))
res["T2"] = {k: dict(median_rel_err=float(np.median(v)), iqr=[float(np.percentile(v, 25)), float(np.percentile(v, 75))])
             for k, v in errs.items()}
res["T2_pass"] = res["T2"]["identity"]["median_rel_err"] <= 0.20
res["inputs"] = {"manifest_sha256": hashlib.sha256((OUT / "confirm-v1.manifest.json").read_bytes()).hexdigest(),
                 "census_sha256": hashlib.sha256((OUT / "confirm-v1.ants.census.csv").read_bytes()).hexdigest()}
pl.DataFrame(rows).write_csv(OUT / "confirm-v1.t2_predictions.csv")
(OUT / "confirm-v1.analysis.json").write_text(json.dumps(res, indent=1, default=str))
print(json.dumps({k: v for k, v in res.items() if k != "inputs"}, indent=1, default=str))
