# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "scipy", "polars"]
# ///
"""Frozen analysis of the confirmation (README "Freeze"). Writes results/analysis.json, predictions.csv.
    uv run experiments/archive/2026-10-kappa-first-passage/scripts/analyze.py [RESULTS_SUBDIR]   (default: confirm)
Run it on the pilot (RESULTS_SUBDIR=pilot) only as a smoke test of the code path, never for verdicts.
"""
import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import fpkernel  # noqa: E402
import load_runs  # noqa: E402

EXP = HERE.parent
SUB = sys.argv[1] if len(sys.argv) > 1 else "confirm"
import os
OUTDIR = Path(os.environ.get("FP_OUT", EXP / "results"))
MINSEED = int(os.environ.get("FP_MINSEED", "6"))
RES, PAIRS = Path(os.environ.get("FP_RES", EXP / "results" / SUB)), Path(os.environ.get("FP_PAIRS", EXP / "scratch" / SUB / "pairs"))
BOOT, BOOT_SEED, FLOOR = 2000, 202610207099, 20
KEYS = fpkernel.KEYS + fpkernel.NEXT


def agg_pairs(spec_files: list[Path], bands: list[int]) -> pl.DataFrame:
    parts = []
    for f in spec_files:
        d = pl.read_csv(f, null_values="NA").filter(pl.col("band").is_in(bands))
        parts.append(d.drop("spec").with_columns(pl.lit(0).alias("band")).group_by(KEYS).agg(pl.col("n").sum(), pl.col("time").sum(), pl.col("skipped").sum(), pl.col("jumps").sum(), pl.col("revisits").sum()))
    return pl.concat(parts).group_by(KEYS).agg(pl.all().sum()).with_columns(pl.lit(0).alias("band"))


def pairs_of(specs: list[str], bands: list[int]) -> pl.DataFrame:
    return agg_pairs([PAIRS / (s.replace("@", "_").replace(":", "_") + ".pairs.csv") for s in specs], bands)


def main():
    man_p = Path(os.environ.get("FP_MAN", EXP / "results" / f"{SUB}_manifest.json"))
    man = json.loads(man_p.read_text())
    roles_p = Path(os.environ.get("FP_ROLES", EXP / "results" / f"{SUB}_roles.csv"))
    roles = pl.read_csv(roles_p) if roles_p.exists() else None
    runs = load_runs.runs(RES).join(roles, on="spec", how="left", suffix="_r") if roles is not None else load_runs.runs(RES)
    out: dict = {"subdir": SUB, "n_runs": runs["spec"].n_unique()}
    st = runs.unique("spec")
    out["stop_counts"] = {k: int(v) for k, v in st.group_by("stop").len().iter_rows()}
    out["unresolved_share_max"] = float(runs["unres_share"].max())
    out["depth_decreases"] = int(st["depth_decreases"].sum())
    out["overflowed"] = int(st["overflowed"].sum())

    # ---- eligibility ----
    rules = [r["rule"] for r in man["rules"]]
    meta = {r["rule"]: r for r in man["rules"]}
    elig, reasons = [], {}
    for rule in rules:
        k = runs.filter((pl.col("rule") == rule) & (pl.col("role") == "kernel"))
        o = runs.filter((pl.col("rule") == rule) & (pl.col("role") == "outcome"))
        nk = k.filter(pl.col("reached_hi") == 1).group_by("spec").len().filter(pl.col("len") == 3).height
        no = o.filter(pl.col("reached_hi") == 1).group_by("spec").len().filter(pl.col("len") == 3).height
        ks = k["spec"].unique().to_list()
        deep = pairs_of(ks, [0, 1]).filter(((pl.col("m") == 7) | (pl.col("nm") == 7)) & pl.col("nm").is_not_null())["n"].sum() if nk else 0
        ok = nk >= MINSEED and no >= MINSEED and deep >= 200 and float(runs.filter(pl.col("rule") == rule)["unres_share"].max()) <= 0.05
        reasons[rule] = dict(kernel_seeds_ok=nk, outcome_seeds_ok=no, deep_segments=int(deep), eligible=bool(ok))
        if ok:
            elig.append(rule)
    out["eligibility"] = dict(n_rules=len(rules), n_eligible=len(elig), fraction=len(elig) / len(rules), gate_ge_0p8=len(elig) / len(rules) >= 0.8, per_rule=reasons)

    # ---- per-rule predictions and observations ----
    recs = []
    for rule in elig:
        k = runs.filter((pl.col("rule") == rule) & (pl.col("role") == "kernel"))
        o = runs.filter((pl.col("rule") == rule) & (pl.col("role") == "outcome") & (pl.col("band") == 2) & (pl.col("reached_hi") == 1))
        kspecs = sorted(set(k.filter((pl.col("band") <= 1) & (pl.col("reached_hi") == 1)).group_by("spec").len().filter(pl.col("len") == 2)["spec"]))
        pk = pairs_of(kspecs, [0, 1])
        rec = dict(rule=rule, family=meta[rule]["family"], fold=meta[rule]["fold"], stratum=meta[rule]["stratum"],
                   obs_BS=float(o["BS"].mean()), obs_BS_sd=float(o["BS"].std()), obs_PA=float((o["perim_end"] / o["area_end"]).mean()),
                   obs_kappa=float(o["kappa"].mean()), n_outcome=o.height, n_kernel=len(kspecs))
        for lvl in (0, 1, 2):
            f = fpkernel.fit(pk, level=lvl, floor=FLOOR)
            rec[f"pred_M{lvl}"] = f.get("pred_BS"); rec[f"ET_M{lvl}"] = f.get("ET"); rec[f"status_M{lvl}"] = f["status"]
        rec["ED_k"] = f.get("ED"); rec["deep_share"] = fpkernel.fit(pk, level=0, floor=FLOOR).get("deep_share")
        k1 = k.filter((pl.col("band") == 1) & (pl.col("reached_hi") == 1))
        rec["B3_persist"] = float(k1["BS"].mean())
        d_n, d_s = k1["B_entered_complete"].sum(), k1["B_entered_complete_steps"].sum()
        t_n, t_s = k1["I_entered_complete"].sum(), k1["I_entered_complete_steps"].sum()
        rec["B4_ET_extrap"] = float((d_s / d_n) / (d_s / d_n + t_s / t_n))
        rec["obs_ET"] = float(o["I_entered_complete_steps"].sum() / o["I_entered_complete"].sum())
        rec["obs_ED"] = float(o["B_entered_complete_steps"].sum() / o["B_entered_complete"].sum())
        rec["kernel_ET_band1_emp"] = float(t_s / t_n)
        rec["kernel_obs_kappa_b1"] = float(k1["kappa"].mean())
        recs.append(rec)
    P = pl.DataFrame(recs)
    # leave-fold-out baselines
    b1, b2 = [], []
    for r in P.iter_rows(named=True):
        tr = P.filter(pl.col("fold") != r["fold"])
        b1.append(float(tr["obs_BS"].mean()))
        b2.append(float(tr["obs_kappa"].mean()) * r["obs_PA"])
    P = P.with_columns(B1_trainmean=pl.Series(b1), B2_geometry=pl.Series(b2))
    P.write_csv(OUTDIR / f"{SUB}_predictions.csv")
    y = P["obs_BS"].to_numpy()
    fams = P["family"].to_numpy()
    uf = sorted(set(fams))
    rng = np.random.default_rng(BOOT_SEED)

    def boot(stat):
        vals = []
        for _ in range(BOOT):
            pick = rng.integers(0, len(uf), len(uf))
            idx = np.concatenate([np.flatnonzero(fams == uf[i]) for i in pick])
            vals.append(stat(idx))
        v = np.array(vals)
        return [float(np.quantile(v, 0.025)), float(np.quantile(v, 0.975))]

    # ---- P2 ----
    pm2 = P["pred_M2"].to_numpy()
    ok2 = np.isfinite(pm2.astype(float))
    cols = {"M2": pm2, "M0": P["pred_M0"].to_numpy(), "M1": P["pred_M1"].to_numpy(), "B1_trainmean": P["B1_trainmean"].to_numpy(),
            "B2_geometry": P["B2_geometry"].to_numpy(), "B3_persist": P["B3_persist"].to_numpy(), "B4_ET_extrap": P["B4_ET_extrap"].to_numpy()}
    abs_err = {k: np.abs(v.astype(float) - y) for k, v in cols.items()}
    rel_err = {k: abs_err[k] / y for k in cols}
    p2 = dict(n_rules=len(y), median_rel_err={k: float(np.median(v)) for k, v in rel_err.items()}, mean_abs_err={k: float(v.mean()) for k, v in abs_err.items()})
    base = min(("B1_trainmean", "B2_geometry", "B3_persist", "B4_ET_extrap"), key=lambda k: p2["mean_abs_err"][k])
    p2["strongest_baseline"] = base
    imp = lambda idx: float((abs_err[base][idx] - abs_err["M2"][idx]).mean())
    p2["improvement_mean_abs"] = imp(np.arange(len(y)))
    p2["improvement_ci95_family_bootstrap"] = boot(imp)
    c1 = p2["median_rel_err"]["M2"] <= 0.20
    c2 = p2["mean_abs_err"]["M2"] <= 0.9 * p2["mean_abs_err"][base]
    c3 = p2["improvement_ci95_family_bootstrap"][0] > 0
    p2.update(criteria=dict(median_rel_err_le_0p20=bool(c1), abs_err_ge_10pct_smaller_than_strongest=bool(c2), ci_excludes_zero_in_favour=bool(c3)),
              verdict=("uninformative" if not out["eligibility"]["gate_ge_0p8"] else ("PASS" if (c1 and c2 and c3) else "FAIL")))
    for s in ("stationary", "drifting"):
        m = (P["stratum"] == s).to_numpy()
        p2[f"median_rel_err_M2_{s}"] = float(np.median(rel_err["M2"][m])) if m.any() else None
    p2["M0_M1_M2_ET_max_rel_diff"] = float(np.nanmax(np.abs(P["ET_M2"] / P["ET_M0"] - 1).to_numpy()))
    p2["obs_over_pred_M2_quartiles"] = [float(q) for q in np.quantile(y / pm2.astype(float), [0.25, 0.5, 0.75])]
    p2["frac_pred_above_obs"] = float((pm2.astype(float) > y).mean())
    p2["deep_share_quartiles"] = [float(q) for q in np.nanquantile(P["deep_share"].to_numpy().astype(float), [0.25, 0.5, 0.75])]
    p2["ET_pred_over_obs_quartiles"] = [float(q) for q in np.quantile(P["ET_M2"].to_numpy() / P["obs_ET"].to_numpy(), [0.25, 0.5, 0.75])]
    out["deep_dominance"] = dict(threshold=0.5, n_rules_deep_share_gt_threshold=int((P["deep_share"] > 0.5).sum()), n_rules=P.height,
                                 closure_uninformative_about_locality=bool((P["deep_share"] > 0.5).sum() > P.height / 2),
                                 rule="frozen: depth-64 share of fitted E[T] > 0.5 for more than half the rules => P2/P4 cannot be read as evidence about local closure")
    out["P2"] = p2

    # ---- P3 (weak form: rule-independent pooled chain per training fold) ----
    if os.environ.get("FP_SKIP_P3") == "1":
        out["P3"] = dict(verdict="untested (exploratory pooled-chain numbers skipped for runtime: FP_SKIP_P3=1)")
    else:
        folds = sorted(set(P["fold"]))
        pooled = {}
        for fo in folds:
            tr_rules = [r for r in elig if meta[r]["fold"] != fo]
            parts = []
            for r in tr_rules:
                ks = sorted(set(runs.filter((pl.col("rule") == r) & (pl.col("role") == "kernel") & (pl.col("band") <= 1) & (pl.col("reached_hi") == 1)).group_by("spec").len().filter(pl.col("len") == 2)["spec"]))
                if ks:
                    parts.append(pairs_of(ks, [0, 1]))
            agg = pl.concat(parts).group_by(KEYS).agg(pl.all().sum()).with_columns(pl.lit(0).alias("band"))
            pooled[fo] = {lvl: fpkernel.fit(agg, level=lvl, floor=FLOOR).get("pred_BS") for lvl in (0, 2)}
        pred3 = {lvl: np.array([pooled[f][lvl] for f in P["fold"]], float) for lvl in (0, 2)}
        trmean = np.array(b1)
    
        def r2(pred, idx):
            return 1 - ((y[idx] - pred[idx]) ** 2).sum() / ((y[idx] - trmean[idx]) ** 2).sum()
        allidx = np.arange(len(y))
        p3 = dict(form="weak: rule-independent pooled chain (turn-class states); constant per fold; no rule-conditional input",
                  r2_M0=float(r2(pred3[0], allidx)), r2_M2=float(r2(pred3[2], allidx)), pooled_pred_by_fold={str(k): v for k, v in pooled.items()})
        p3["r2_gain_M2_over_M0"] = p3["r2_M2"] - p3["r2_M0"]
        p3["ci95_gain_family_bootstrap"] = boot(lambda idx: r2(pred3[2], idx) - r2(pred3[0], idx))
        p3["ci95_r2_M2_family_bootstrap"] = boot(lambda idx: r2(pred3[2], idx))
        p3["verdict"] = "untested (the weak form has no rule-conditional input, so it cannot test transfer; numbers below are exploratory only)"
        out["P3"] = p3

    # ---- P4: untested (radius-4 context not recorded). Exploratory out-of-band log-loss. ----
    ll = {0: [], 1: [], 2: []}
    for rule in elig:
        ks = sorted(set(runs.filter((pl.col("rule") == rule) & (pl.col("role") == "kernel") & (pl.col("band") <= 1) & (pl.col("reached_hi") == 1)).group_by("spec").len().filter(pl.col("len") == 2)["spec"]))
        os_ = sorted(set(runs.filter((pl.col("rule") == rule) & (pl.col("role") == "outcome") & (pl.col("band") == 2) & (pl.col("reached_hi") == 1))["spec"]))
        tr = pairs_of(ks, [0, 1]).filter(pl.col("nm").is_not_null() & (pl.col("m") > 0))
        te = pairs_of(os_, [2]).filter(pl.col("nm").is_not_null() & (pl.col("m") > 0))
        te = te.with_columns((pl.col("nm") > pl.col("m")).alias("up"))
        tr = tr.with_columns((pl.col("nm") > pl.col("m")).alias("up"))
        codes_tr, codes_te = fpkernel.codes(tr, fpkernel.KEYS), fpkernel.codes(te, fpkernel.KEYS)
        tr = tr.with_columns(*(codes_tr[l].alias(f"c{l}") for l in range(3)))
        te = te.with_columns(*(codes_te[l].alias(f"c{l}") for l in range(3)))
        stats = {l: tr.group_by(f"c{l}").agg((pl.col("n") * pl.col("up")).sum().alias("u"), pl.col("n").sum().alias("N")) for l in range(3)}
        for lvl in range(3):
            cur = te.with_columns(pl.lit(None, dtype=pl.Float64).alias("p"))
            p = pl.Series([None] * te.height, dtype=pl.Float64)
            for l in range(lvl + 1):
                j = te.join(stats[l].filter(pl.col("N") >= FLOOR), left_on=f"c{l}", right_on=f"c{l}", how="left", maintain_order="left")
                assert j.height == te.height
                pl_l = ((j["u"] + 0.5) / (j["N"] + 1.0))
                p = pl.Series(np.where(np.isfinite(pl_l.to_numpy().astype(float)), pl_l.to_numpy().astype(float), p.to_numpy().astype(float)))
            pv = p.to_numpy().astype(float)
            pv = np.where(np.isfinite(pv), pv, 0.5)
            up = te["up"].to_numpy()
            n = te["n"].to_numpy().astype(float)
            ll[lvl].append(float(-(n * np.where(up, np.log(pv), np.log(1 - pv))).sum() / n.sum()))
    out["P4"] = dict(verdict="untested (instrument v1 does not record radius-4 context)",
                     exploratory_logloss_per_segment_mean_over_rules={f"M{l}": float(np.mean(v)) for l, v in ll.items()},
                     exploratory_note="out-of-band (kernel bands 0,1 -> outcome band 2) log-loss of next-milestone direction; not a registered prediction")

    # ---- P1 ----
    sl = []
    for rule in elig:
        o = runs.filter((pl.col("rule") == rule) & (pl.col("role") == "outcome") & (pl.col("reached_hi") == 1)).group_by("band").agg(pl.col("kappa").mean().alias("k"), (pl.col("area_end") / pl.col("perim_end")).mean().alias("L"))
        o = o.sort("band")
        if o.height == 3:
            sl.append(float(np.polyfit(np.log(o["L"].to_numpy()), np.log(o["k"].to_numpy()), 1)[0]))
    dl = []
    for rule in elig:
        o = runs.filter((pl.col("rule") == rule) & (pl.col("role") == "outcome") & (pl.col("reached_hi") == 1)).group_by("band").agg(pl.col("B_entered_complete_steps").sum().alias("ds"), pl.col("B_entered_complete").sum().alias("dn"), (pl.col("area_end") / pl.col("perim_end")).mean().alias("L")).sort("band")
        if o.height == 3:
            dl.append(float(np.polyfit(np.log(o["L"].to_numpy()), np.log((o["ds"] / o["dn"]).to_numpy()), 1)[0]))
    out["delta"] = dict(descriptive="slope of ln E[D] (entered complete boundary episodes) on ln(A/P) over the three bands, outcome seeds", n=len(dl), quartiles=[float(q) for q in np.quantile(dl, [0.25, 0.5, 0.75])] if dl else None)
    out["P1"] = dict(verdict="untested (no tail estimator was calibrated; the earlier truncated-power-law fit failed its calibration)",
                     descriptive_observed_dlogkappa_dlogL=dict(n=len(sl), quartiles=[float(q) for q in np.quantile(sl, [0.25, 0.5, 0.75])] if sl else None,
                                                              frac_abs_le_0p15=float(np.mean(np.abs(sl) <= 0.15)) if sl else None))
    (OUTDIR / f"{SUB}_analysis.json").write_text(json.dumps(out, indent=2, default=float))
    print(json.dumps({k: v for k, v in out.items() if k != "eligibility"}, indent=2, default=float))
    print("eligible", out["eligibility"]["n_eligible"], "/", out["eligibility"]["n_rules"])


if __name__ == "__main__":
    main()
