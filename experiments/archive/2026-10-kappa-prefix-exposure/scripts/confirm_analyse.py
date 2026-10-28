# /// script
# dependencies = ["polars", "numpy", "scipy"]
# ///
"""Registered analysis for kappa-prefix-exposure (estimators frozen in README.md 'Registration').

Reads dumps/confirm_dev and dumps/confirm_val (sampler output), results/arms.csv, results/cohort.csv.
Writes results/confirm_pairs.csv and results/confirm_analysis.json. Nothing here is tuned on
validation outcomes: development coefficients come from development bases only.

usage (repo root):
  uv run experiments/archive/2026-10-kappa-prefix-exposure/scripts/confirm_analyse.py
  uv run experiments/archive/2026-10-kappa-prefix-exposure/scripts/confirm_analyse.py --dry-run   # pilot data, 2 pred + 2 target seeds, stdout only
"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import polars as pl
from scipy.stats import spearmanr

sys.path.insert(0, str(Path(__file__).parent))
from kpe_lib import EXP, RES, ROOT, WS, colour_exposure, load_bands, load_reads, pooled  # noqa: E402

DRY = "--dry-run" in sys.argv
PRED = [2026101571001 + i for i in range(32)]
TGT = [2026101571001 + 32 + i for i in range(32)]
MIN_VALID = 16                      # valid runs needed in each arm and role for an attained comparison
S_POOL = {0: 0.533, 1: 0.700}       # pilot pooled between-seed sd of ln(B/S) (results/pilot_stats.txt), per band
SE_PAIR = {k: S_POOL[k] * np.sqrt(2 / 32) for k in (0, 1)}
RESOLVE_Z = 2.0
BOOT_B, BOOT_SEED = 2000, 7015001
PRIMARY_BAND = 1                    # A = 131072
if DRY:
    PRED, TGT, MIN_VALID = [2026101570001, 2026101570002], [2026101570003, 2026101570004], 1
    SE_PAIR = {k: S_POOL[k] * np.sqrt(2 / 2) for k in (0, 1)}

arms = pl.read_csv(RES / "arms.csv")
cohort = pl.read_csv(RES / "cohort.csv").select("side", "base", "label", "n")
dirs = {"dev": EXP / "dumps" / ("pilot" if DRY else "confirm_dev"), "val": EXP / "dumps" / ("pilot" if DRY else "confirm_val")}


def lnr(a, b):
    return float(np.log(a / b))


def pair_table(side: str) -> pl.DataFrame:
    bands, reads = load_bands(dirs[side]), load_reads(dirs[side])
    a = arms.filter((pl.col("side") == side) & (pl.col("arm") != "base"))
    rows = []
    pt, pp = (pooled(bands.filter(pl.col("seed").is_in(s)), ["rule", "band_id"]) for s in (TGT, PRED))
    half = [pooled(bands.filter(pl.col("seed").is_in(s)), ["rule", "band_id"]) for s in (TGT[: len(TGT) // 2], TGT[len(TGT) // 2:])]

    def get(tab, rule, k):
        r = tab.filter((pl.col("rule") == rule) & (pl.col("band_id") == k))
        return r.row(0, named=True) if r.height and r["n_seeds"][0] >= (MIN_VALID if tab is not half[0] and tab is not half[1] else max(MIN_VALID // 2, 1)) else None

    for r in a.iter_rows(named=True):
        for k in (0, 1):
            bt, mt, bp, mp = get(pt, r["base"], k), get(pt, r["rule"], k), get(pp, r["base"], k), get(pp, r["rule"], k)
            h1b, h1m, h2b, h2m = get(half[0], r["base"], k), get(half[0], r["rule"], k), get(half[1], r["base"], k), get(half[1], r["rule"], k)
            row = dict(side=side, base=r["base"], arm=r["arm"], pos=int(r["pos"]), band=k, mutant=r["rule"], attained=all(x is not None for x in (bt, mt, bp, mp)))
            # run-level outcomes of the mutation, over all runs of both roles (not only attained ones)
            allm = bands.filter((pl.col("rule") == r["rule"]) & (pl.col("band_id") == k))
            row |= dict(mut_runs=allm.height, mut_valid=int(allm["valid"].sum()))
            if row["attained"]:
                j = int(r["pos"])
                ex = colour_exposure(reads, bands, r["base"], PRED, k, j)
                row |= dict(
                    y_lnbs=lnr(mt["bs"], bt["bs"]), y_lnkappa=lnr(mt["kappa_end"], bt["kappa_end"]),
                    **{f"x_lnLam{w}": lnr(mp[f"Lam_{w}"], bp[f"Lam_{w}"]) for w in (64, 256, 1024)},
                    mean_depth=ex["mean_depth"], ln_bshare=float(np.log((ex["by_depth"][0] + .5) / (ex["reads"] + 1))), reads=ex["reads"],
                    y_half1=lnr(h1m["bs"], h1b["bs"]) if h1b and h1m else np.nan, y_half2=lnr(h2m["bs"], h2b["bs"]) if h2b and h2m else np.nan)
            rows.append(row)
    t = pl.DataFrame(rows, infer_schema_length=None)
    return t.join(cohort.select("base", "label"), on="base").with_columns(early=(pl.col("pos") < 8), lead=(pl.col("pos") <= 2), mid=((pl.col("pos") >= 3) & (pl.col("pos") < 8)))


def ols(x, y):
    a = np.c_[np.ones(len(x)), x]
    return np.linalg.lstsq(a, y, rcond=None)[0]


def pred(beta, x):
    return np.c_[np.ones(len(x)), x] @ beta


def r2(y, yhat, ref_mean):
    return float(1 - ((y - yhat) ** 2).sum() / ((y - ref_mean) ** 2).sum())


def bootstrap(val: pl.DataFrame, stat):
    """Resample validation BASES with replacement (all their pairs move together)."""
    rng = np.random.default_rng(BOOT_SEED)
    bases = sorted(val["base"].unique().to_list())
    groups = {b: val.filter(pl.col("base") == b) for b in bases}
    vals = []
    for _ in range(BOOT_B):
        pick = rng.choice(len(bases), len(bases))
        v = stat(pl.concat([groups[bases[i]] for i in pick]))
        if v is not None and np.isfinite(v):
            vals.append(v)
    return (float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5)), len(vals)) if vals else (np.nan, np.nan, 0)


dev = pair_table("dev")
val = dev if DRY else pair_table("val")  # dry run: no validation data exist; metrics are then in-sample mechanics only
if not DRY:
    pl.concat([dev, val], how="diagonal").write_csv(RES / "confirm_pairs.csv")
out: dict = {"dry_run": DRY, "git": subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip(),
             "se_pair": SE_PAIR, "min_valid": MIN_VALID, "resolve_z": RESOLVE_Z, "boot": {"B": BOOT_B, "seed": BOOT_SEED}}
k = PRIMARY_BAND
std = lambda t: t.filter((pl.col("label") == "stationary") & (pl.col("band") == k) & pl.col("attained") & pl.col("arm").is_in(["a1", "a2", "m1", "l1", "l2"]) & pl.col("y_lnbs").is_finite())
dtr, vte = std(dev), std(val)
out["coverage"] = {"dev_pairs": dtr.height, "val_pairs": vte.height, "val_bases_informative": vte["base"].n_unique(),
                   "val_early": int(vte["early"].sum()), "val_late": int((~vte["early"]).sum())}
out["inadequate_coverage"] = vte["base"].n_unique() < 8

# ---- reliability gate: does the target effect replicate across disjoint halves of the target seeds?
rel = dtr.filter(pl.col("y_half1").is_finite() & pl.col("y_half2").is_finite())
out["reliability"] = {"n_pairs": rel.height, "spearman_half1_half2": float(spearmanr(rel["y_half1"], rel["y_half2"]).statistic) if rel.height > 3 else None}
out["reliability"]["informative"] = bool(out["reliability"]["spearman_half1_half2"] is not None and out["reliability"]["spearman_half1_half2"] >= 0.30)

# ---- P1: out-of-sample link between the change in long-episode launch rate and the change in B/S
y_dev, y_val = dtr["y_lnbs"].to_numpy(), vte["y_lnbs"].to_numpy()
p1 = {}
for w in (256, 64, 1024):
    col = f"x_lnLam{w}"
    beta = ols(dtr[col].to_numpy()[:, None], y_dev)
    yhat = pred(beta, vte[col].to_numpy()[:, None])
    resolved = np.abs(y_val) > RESOLVE_Z * SE_PAIR[k]
    agree = float((np.sign(y_val[resolved]) == np.sign(yhat[resolved])).mean()) if resolved.any() else None

    def stat_r2(t, beta=beta, col=col):
        return r2(t["y_lnbs"].to_numpy(), pred(beta, t[col].to_numpy()[:, None]), float(y_dev.mean()))
    lo, hi, nb = bootstrap(vte, stat_r2)
    p1[f"w{w}"] = dict(beta=beta.tolist(), heldout_r2=r2(y_val, yhat, float(y_dev.mean())), boot_ci=[lo, hi], boot_n=nb,
                       n_resolved=int(resolved.sum()), direction_agreement=agree, spearman=float(spearmanr(vte[col], vte["y_lnbs"]).statistic),
                       dev_spearman=float(spearmanr(dtr[col], dtr["y_lnbs"]).statistic))
prim = p1["w256"]
prim["verdict"] = None if (out["inadequate_coverage"] or not out["reliability"]["informative"]) else bool(
    prim["beta"][1] < 0 and prim["heldout_r2"] >= 0.20 and prim["boot_ci"][0] > 0 and prim["n_resolved"] >= 10 and prim["direction_agreement"] is not None and prim["direction_agreement"] >= 0.70)
out["P1_primary_w256"] = prim
out["P1_secondary"] = {k_: v for k_, v in p1.items() if k_ != "w256"}

# ---- P2: ex-ante exposure model (base-run features on prediction seeds) vs position-only
feat = lambda t: np.c_[t["lead"].to_numpy().astype(float), t["mid"].to_numpy().astype(float), t["mean_depth"].to_numpy(), t["ln_bshare"].to_numpy()]
ok_d, ok_v = dtr.filter(pl.col("mean_depth").is_finite()), vte.filter(pl.col("mean_depth").is_finite())
if ok_d.height > 5 and ok_v.height > 5:
    yd, yv = ok_d["y_lnbs"].to_numpy(), ok_v["y_lnbs"].to_numpy()
    bp, be = ols(feat(ok_d)[:, :2], yd), ols(feat(ok_d), yd)
    allm = pl.concat([ok_d, ok_v])
    e, l = allm.filter(pl.col("early")), allm.filter(~pl.col("early"))
    lo_l, hi_l = float(l["mean_depth"].min()), float(l["mean_depth"].max())
    overlap = float(((e["mean_depth"] >= lo_l) & (e["mean_depth"] <= hi_l)).mean())
    n_in = int(((e["mean_depth"] >= lo_l) & (e["mean_depth"] <= hi_l)).sum()), int(((l["mean_depth"] >= float(e["mean_depth"].min())) & (l["mean_depth"] <= float(e["mean_depth"].max()))).sum())

    def dr2(t, bp=bp, be=be):
        y = t["y_lnbs"].to_numpy()
        return r2(y, pred(be, feat(t)), float(yd.mean())) - r2(y, pred(bp, feat(t)[:, :2]), float(yd.mean()))
    lo, hi, nb = bootstrap(ok_v, dr2)
    out["P2"] = dict(r2_position=r2(yv, pred(bp, feat(ok_v)[:, :2]), float(yd.mean())), r2_exposure=r2(yv, pred(be, feat(ok_v)), float(yd.mean())),
                     delta_r2=dr2(ok_v), boot_ci=[lo, hi], boot_n=nb, beta_position=bp.tolist(), beta_exposure=be.tolist(),
                     early_inside_late_range=overlap, pairs_inside_overlap=n_in, identifiable=bool(overlap >= 0.30 and min(n_in) >= 6))
    out["P2"]["verdict"] = None if (out["inadequate_coverage"] or not out["reliability"]["informative"] or not out["P2"]["identifiable"]) else bool(
        out["P2"]["delta_r2"] >= 0.10 and out["P2"]["boot_ci"][0] > 0)
else:
    out["P2"] = {"note": "too few pairs with finite exposure"}

# ---- P5 (sign-mixed expectation from kappa-rule-space W6m): leading-letter edits (positions 1-2, arms a1, a2) of stationary
# bases move kappa at fixed area in BOTH directions, so the signed mean shift is small next to the typical size.
# Held if, over attained pairs pooled across dev and val (n >= 20): share with ln(kappa_mut/kappa_base) > 0 lies in [0.25, 0.75]
# AND |mean| <= 0.5 * median |shift|. Base-bootstrap interval for the mean is reported (resampling bases), no extra bar.
lead_all = pl.concat([dev, val], how="diagonal") if not DRY else dev
lp = lead_all.filter((pl.col("label") == "stationary") & (pl.col("band") == k) & pl.col("attained") & pl.col("arm").is_in(["a1", "a2"]) & pl.col("y_lnkappa").is_finite())
if lp.height:
    yk = lp["y_lnkappa"].to_numpy()
    lo3, hi3, nb3 = bootstrap(lp, lambda t: float(t["y_lnkappa"].mean()))
    out["P5_sign_mixed_kappa"] = dict(n=lp.height, share_positive=float((yk > 0).mean()), mean=float(yk.mean()), median_abs=float(np.median(np.abs(yk))),
                                mean_boot_ci=[lo3, hi3], by_arm={a_: float(lp.filter(pl.col("arm") == a_)["y_lnkappa"].mean()) for a_ in ("a1", "a2")},
                                verdict=bool(lp.height >= 20 and 0.25 <= (yk > 0).mean() <= 0.75 and abs(yk.mean()) <= 0.5 * np.median(np.abs(yk))))

# ---- P3: the position gradient of the effect size at fixed area (replication of the W6 matched-area finding on fresh mutants)
def ratio_stat(t):
    a_ = t.filter(pl.col("lead"))["y_lnbs"].abs().to_numpy()
    b_ = t.filter(~pl.col("early"))["y_lnbs"].abs().to_numpy()
    return float(np.median(a_) / np.median(b_)) if len(a_) and len(b_) else None


lo, hi, nb = bootstrap(vte, ratio_stat)
out["P3"] = dict(ratio_lead_over_late=ratio_stat(vte), boot_ci=[lo, hi], boot_n=nb, n_lead=int(vte["lead"].sum()), n_late=int((~vte["early"]).sum()),
                 verdict=None if out["inadequate_coverage"] else bool((ratio_stat(vte) or 0) >= 1.5 and lo > 1))
res_lead = vte.filter(pl.col("lead") & (pl.col("y_lnbs").abs() > RESOLVE_Z * SE_PAIR[k]))
out["P4_sign_mix_descriptive"] = dict(n_resolved_lead=res_lead.height, share_positive=float((res_lead["y_lnbs"] > 0).mean()) if res_lead.height else None)

# ---- descriptive, not tested: kappa, escape/budget, anchor, nonstationary, early vs late
allp = pl.concat([dev, val], how="diagonal")
d = {}
for name, t in (("dev", dev), ("val", val)):
    s = t.filter((pl.col("label") == "stationary") & (pl.col("band") == k) & pl.col("arm").is_in(["a1", "a2", "m1", "l1", "l2"]))
    d[name] = dict(early_valid_share=float(s.filter(pl.col("early"))["mut_valid"].sum() / max(s.filter(pl.col("early"))["mut_runs"].sum(), 1)),
                   late_valid_share=float(s.filter(~pl.col("early"))["mut_valid"].sum() / max(s.filter(~pl.col("early"))["mut_runs"].sum(), 1)))
    a_ = s.filter(pl.col("attained") & pl.col("y_lnbs").is_finite())
    d[name] |= dict(median_abs_y_early=float(a_.filter(pl.col("early"))["y_lnbs"].abs().median()), median_abs_y_late=float(a_.filter(~pl.col("early"))["y_lnbs"].abs().median()),
                    median_abs_ykappa_early=float(a_.filter(pl.col("early"))["y_lnkappa"].abs().median()), median_abs_ykappa_late=float(a_.filter(~pl.col("early"))["y_lnkappa"].abs().median()))
out["descriptive"] = d
p0 = allp.filter((pl.col("arm") == "p0") & (pl.col("band") == k) & pl.col("attained"))
out["position0_anchor"] = dict(n=p0.height, median_abs_y_lnbs=float(p0["y_lnbs"].abs().median()) if p0.height else None)
ns = allp.filter((pl.col("label") == "nonstationary") & (pl.col("band") == k) & pl.col("attained"))
out["nonstationary"] = ns.select("side", "base", "arm", "pos", "y_lnbs", "x_lnLam256").to_dicts()
inputs = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in [RES / "arms.csv", RES / "cohort.csv", Path(__file__), Path(__file__).parent / "kpe_lib.py"]}
out["inputs_sha256"] = inputs
txt = json.dumps(out, indent=1, sort_keys=True, default=lambda o: None if isinstance(o, float) and not np.isfinite(o) else str(o))
if DRY:
    print(txt)
else:
    (RES / "confirm_analysis.json").write_text(txt + "\n")
    print(txt)
