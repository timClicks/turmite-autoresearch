# /// script
# dependencies = ["polars", "numpy", "scipy"]
# ///
"""EXPLORATORY follow-up to confirm_analyse.py. Nothing here is registered; no verdicts, no bars.

Motivation: the stat-phys design review of 2026-10-16 (NOTEBOOK.md), written before any confirmation outcome was read.
Reads results/confirm_pairs.csv (written by the registered analysis) and results/arms.csv only.
Writes results/confirm_exploratory.json. Development fits, validation scoring, as in the registered analysis.

E1  P2 re-posed: signed Y cannot be predicted by unsigned features, so refit on |Y| and on signed Y with flip direction.
E2  Is Lam_w a launch rate or a duration scale? Association of Y with X_w across w (rising with w suggests scale).
E3  Survivorship: association of the mutant's valid-run share with Y and X.
E4  Empirical per-seed sd of ln(B/S) implied by split halves, against the frozen S_POOL.
E5  Sign(X) vs sign(Y) on resolved pairs; R^2 against the validation mean; P1 fit repeated in band 0.
E6  Noise-corrected P3: rms signal sqrt(mean(Y^2) - se^2) of lead vs late arms.

usage (repo root): uv run experiments/archive/2026-10-kappa-prefix-exposure/scripts/confirm_exploratory.py [pairs.csv out.json]
"""
import json
import sys
from pathlib import Path

import numpy as np
import polars as pl
from scipy.stats import spearmanr

EXP = Path(__file__).resolve().parents[1]
RES = EXP / "results"
PAIRS = Path(sys.argv[1]) if len(sys.argv) > 2 else RES / "confirm_pairs.csv"
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else RES / "confirm_exploratory.json"
S_POOL = {0: 0.533, 1: 0.700}
SE = {k: S_POOL[k] * np.sqrt(2 / 32) for k in (0, 1)}
ARMS = ["a1", "a2", "m1", "l1", "l2"]

arms = pl.read_csv(RES / "arms.csv")
t = pl.read_csv(PAIRS, infer_schema_length=None).join(arms.select("rule", "side", "base", "arm", "pos").rename({"rule": "mutant"}), on=["mutant", "side", "base", "arm", "pos"], how="left")
# flip direction: the base letter at the altered position (1 = L->R, 0 = R->L)
t = t.with_columns(l_to_r=pl.struct("base", "pos").map_elements(lambda s: float(s["base"][s["pos"]] == "L"), return_dtype=pl.Float64))


def sel(side, band):
    return t.filter((pl.col("side") == side) & (pl.col("label") == "stationary") & (pl.col("band") == band) & pl.col("attained")
                    & pl.col("arm").is_in(ARMS) & pl.col("y_lnbs").is_finite())


def ols(x, y):
    a = np.c_[np.ones(len(x)), x]
    return np.linalg.lstsq(a, y, rcond=None)[0]


def pr(b, x):
    return np.c_[np.ones(len(x)), x] @ b


def r2(y, yh, ref):
    return float(1 - ((y - yh) ** 2).sum() / ((y - ref) ** 2).sum())


def sp(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    m = np.isfinite(a) & np.isfinite(b)
    return float(spearmanr(a[m], b[m]).statistic) if m.sum() > 3 else None


out = {"note": "exploratory, unregistered; see NOTEBOOK.md 2026-10-16 design-review entry", "pairs": str(PAIRS)}
k = 1
d, v = sel("dev", k), sel("val", k)
out["n"] = {"dev": d.height, "val": v.height}

# E1 -------------------------------------------------------------------------------------------------------------
def feats(x, extra=()):
    cols = [x["lead"].cast(float).to_numpy(), x["mid"].cast(float).to_numpy(), x["mean_depth"].to_numpy(), x["ln_bshare"].to_numpy()]
    return np.c_[tuple(cols) + tuple(extra)]


e1 = {}
dd, vv = d.filter(pl.col("mean_depth").is_finite()), v.filter(pl.col("mean_depth").is_finite())
if dd.height > 6 and vv.height > 6:
    for name, tr in (("abs_y", lambda y: np.abs(y)), ("signed_y_with_flip_direction", lambda y: y)):
        extra_d = (dd["l_to_r"].to_numpy(),) if name.startswith("signed") else ()
        extra_v = (vv["l_to_r"].to_numpy(),) if name.startswith("signed") else ()
        yd, yv = tr(dd["y_lnbs"].to_numpy()), tr(vv["y_lnbs"].to_numpy())
        fd, fv = feats(dd, extra_d), feats(vv, extra_v)
        pos_cols = [0, 1] + ([4] if extra_d else [])
        bp, be = ols(fd[:, pos_cols], yd), ols(fd, yd)
        e1[name] = dict(r2_position=r2(yv, pr(bp, fv[:, pos_cols]), yd.mean()), r2_exposure=r2(yv, pr(be, fv), yd.mean()),
                        beta_exposure=be.tolist(), beta_position=bp.tolist())
out["E1_P2_reposed"] = e1

# E2 -------------------------------------------------------------------------------------------------------------
e2 = {}
for w in (64, 256, 1024):
    for nm, tab in (("dev", d), ("val", v)):
        e2[f"w{w}_{nm}"] = dict(spearman_x_y=sp(tab[f"x_lnLam{w}"], tab["y_lnbs"]), sd_x=float(tab[f"x_lnLam{w}"].std()) if tab.height > 1 else None)
pool = pl.concat([d, v])
e2["corr_x64_x1024_pooled"] = sp(pool["x_lnLam64"], pool["x_lnLam1024"])
e2["interpretation_rule"] = "association flat in w -> amplitude (launch); rising with w -> duration scale"
out["E2_lam_vs_w"] = e2

# E3 -------------------------------------------------------------------------------------------------------------
allb = t.filter((pl.col("label") == "stationary") & (pl.col("band") == k) & pl.col("arm").is_in(ARMS)).with_columns(vs=pl.col("mut_valid") / pl.col("mut_runs"))
a = allb.filter(pl.col("attained"))
out["E3_survivorship"] = dict(valid_share_early=float(allb.filter(pl.col("early"))["mut_valid"].sum() / allb.filter(pl.col("early"))["mut_runs"].sum()),
                              valid_share_late=float(allb.filter(~pl.col("early"))["mut_valid"].sum() / allb.filter(~pl.col("early"))["mut_runs"].sum()),
                              unattained_pairs=int(allb.height - a.height),
                              spearman_validshare_y=sp(a["vs"], a["y_lnbs"]), spearman_validshare_absy=sp(a["vs"], a["y_lnbs"].abs()),
                              spearman_validshare_x256=sp(a["vs"], a["x_lnLam256"]))

# E4 -------------------------------------------------------------------------------------------------------------
e4 = {}
for kk in (0, 1):
    h = pl.concat([sel("dev", kk), sel("val", kk)]).filter(pl.col("y_half1").is_finite() & pl.col("y_half2").is_finite())
    if h.height > 3:
        # var(h1-h2) = 2 * (2 S^2 / 16) for 16-seed halves, so S = 2 sd(h1-h2)
        e4[f"band{kk}"] = dict(n=h.height, implied_S=float(2 * (h["y_half1"] - h["y_half2"]).std()), frozen_S=S_POOL[kk])
out["E4_empirical_noise"] = e4

# E5 -------------------------------------------------------------------------------------------------------------
e5 = {}
for kk in (1, 0):
    dk, vk = sel("dev", kk), sel("val", kk)
    if dk.height > 3 and vk.height > 3:
        yd, yv = dk["y_lnbs"].to_numpy(), vk["y_lnbs"].to_numpy()
        b = ols(dk["x_lnLam256"].to_numpy()[:, None], yd)
        yh = pr(b, vk["x_lnLam256"].to_numpy()[:, None])
        res = np.abs(yv) > 2 * SE[kk]
        e5[f"band{kk}"] = dict(beta=b.tolist(), r2_vs_dev_mean=r2(yv, yh, yd.mean()), r2_vs_val_mean=r2(yv, yh, yv.mean()),
                               n_resolved=int(res.sum()),
                               sign_agree_x_vs_y_resolved=float((np.sign(vk["x_lnLam256"].to_numpy()[res]) == -np.sign(yv[res])).mean()) if res.any() else None,
                               spearman_val=sp(vk["x_lnLam256"], vk["y_lnbs"]), spearman_dev=sp(dk["x_lnLam256"], dk["y_lnbs"]))
out["E5_p1_variants"] = e5

# E6 -------------------------------------------------------------------------------------------------------------
def rms_signal(x):
    y = x["y_lnbs"].to_numpy()
    return float(np.sqrt(max((y ** 2).mean() - SE[k] ** 2, 0.0))) if len(y) else None


lead, late = v.filter(pl.col("lead")), v.filter(~pl.col("early"))
rl, rt = rms_signal(lead), rms_signal(late)
out["E6_noise_corrected_p3"] = dict(rms_signal_lead=rl, rms_signal_late=rt, ratio=(rl / rt if rt else None), n_lead=lead.height, n_late=late.height)

OUT.write_text(json.dumps(out, indent=1, default=str) + "\n")
print(json.dumps(out, indent=1, default=str))
