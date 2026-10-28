"""G1 confirmation analysis (frozen in README.md before any confirmation seed was run).

Target  y_r  = ln(sum B / sum steps) over the TARGET seeds of rule r, per band (boundary occupation).
B0 (4)       = [ln mean P/A, ln mean completed boundary-run length, ln(d1/(d1+..+d4)), ln(d5/(d1+..+d4))]
               from PREDICTOR seeds only. d0 (boundary occupancy itself) is excluded on purpose.
G  (B0 + 2)  = B0 + [g1, g2]; g1 = mean over predictor seeds of (top-decile share - Poisson-null share),
               g2 = max-min over exit headings (>= 50 pooled excursions) of ln mean excursion duration.
Model        = ridge, lambda = 1.0 on features standardised with training-fold mean/sd, unpenalised intercept.
Folds        = leave-one-rule-out over rules with every feature defined.
R2_oos       = 1 - sum (y - yhat)^2 / sum (y - ybar_train)^2 ; DeltaR2 = R2(G) - R2(B0).
Bootstrap    = 2000 rule resamples (seed 2026102099) of the stored held-out predictions, 95% percentile interval.
Band pass    : DeltaR2 >= 0.10, bootstrap 2.5th percentile > 0, and permutation p <= 0.05
               (gate features g1,g2 shuffled together across rules, 500 permutations, seed 2026102199, B0 unshuffled).   G1 passes iff both bands pass.
Gates        : coverage >= 20/24 rules evaluable per band; split-seed Spearman of g1, g2 over predictor seeds >= 0.7
               (Spearman-Brown NOT applied); headroom: R2(B0) <= 0.90.
Verdict      : PASS | FAIL (informative) | UNINFORMATIVE (a gate failed) -- see main().
Exploratory (labelled, never gating): g1-only, g2-only increments; B0+ln q oracle; stratum splits.
"""
from pathlib import Path
import hashlib, json, subprocess, sys
import numpy as np, polars as pl
from scipy.stats import spearmanr
sys.path.insert(0, str(Path(__file__).resolve().parent))
import rg_lib

ROOT = Path(__file__).resolve().parents[4]
EXP = Path(__file__).resolve().parents[1]
LAM, NBOOT, BSEED, PERMS = 1.0, 2000, 2026102099, 500
B0 = ["f_lnpa", "f_lnbrun", "f_rimshape", "f_interior"]
GATES = ["g1", "g2"]


def loo(X, y):
    n = len(y)
    pred, base = np.empty(n), np.empty(n)
    for i in range(n):
        tr = np.arange(n) != i
        mu, sd = X[tr].mean(0), X[tr].std(0, ddof=1)
        sd[sd == 0] = 1.0
        Z = (X[tr] - mu) / sd
        ym = y[tr].mean()
        w = np.linalg.solve(Z.T @ Z + LAM * np.eye(Z.shape[1]), Z.T @ (y[tr] - ym))
        pred[i] = ym + ((X[i] - mu) / sd) @ w
        base[i] = ym
    return pred, base


def r2(y, p, b):
    return 1 - ((y - p) ** 2).sum() / ((y - b) ** 2).sum()


def analyse_band(runs, rules, band, S):
    pr = runs.filter(pl.col("role") == "predictor")
    pseeds = sorted(pr["seed"].unique().to_list())[:S]
    pt = rg_lib.table(pr, rules, band, pseeds)
    tg = rg_lib.table(runs.filter(pl.col("role") == "target"), rules, band)
    m = pt.join(tg.select("rule", pl.col("y").alias("y_target"), pl.col("n_seeds").alias("n_target_seeds")), on="rule")
    feats = B0 + GATES
    ok = m.filter(pl.all_horizontal([pl.col(f).is_not_nan() & pl.col(f).is_not_null() for f in feats + ["y_target"]]))
    rep = dict(n_rules_total=len(rules), n_rules_evaluable=ok.height, excluded=sorted(set(rules) - set(ok["rule"].to_list())),
               predictor_seeds=len(pseeds), mean_target_seeds=float(m["n_target_seeds"].mean()))
    # reliability over predictor seeds (halves, interleaved)
    ha, hb = pseeds[0::2], pseeds[1::2]
    ta, tb = rg_lib.table(pr, rules, band, ha), rg_lib.table(pr, rules, band, hb)
    rel = {}
    for f in GATES:
        mm = ta[f].is_not_nan() & tb[f].is_not_nan()
        rel[f] = dict(n_rules=int(mm.sum()), split_half_spearman=float(spearmanr(ta.filter(mm)[f], tb.filter(mm)[f]).statistic))
    rep["reliability"] = rel
    if ok.height < 8:
        rep["verdict_inputs"] = "too few evaluable rules"
        return rep
    y = ok["y_target"].to_numpy()
    XB, XG = ok.select(B0).to_numpy(), ok.select(B0 + GATES).to_numpy()
    pB, base = loo(XB, y)
    pG, _ = loo(XG, y)
    rB, rG = r2(y, pB, base), r2(y, pG, base)
    rng = np.random.default_rng(BSEED + band)
    n = len(y)
    boots = []
    for _ in range(NBOOT):
        i = rng.integers(0, n, n)
        boots.append(r2(y[i], pG[i], base[i]) - r2(y[i], pB[i], base[i]))
    lo, hi = np.percentile(boots, [2.5, 97.5])
    rng2 = np.random.default_rng(BSEED + 100 + band)  # = 2026102199 (+band)
    Gm = ok.select(GATES).to_numpy()
    nulls = []
    for _ in range(PERMS):
        p, _ = loo(np.hstack([XB, Gm[rng2.permutation(n)]]), y)
        nulls.append(r2(y, p, base) - rB)
    p_perm = float((np.sum(np.array(nulls) >= rG - rB) + 1) / (PERMS + 1))
    rep.update(r2_baseline=float(rB), r2_with_gates=float(rG), delta_r2=float(rG - rB), delta_ci95=[float(lo), float(hi)], permutation_p=p_perm,
               permutation_null_delta_r2=dict(mean=float(np.mean(nulls)), q95=float(np.percentile(nulls, 95))),
               band_pass=bool(rG - rB >= 0.10 and lo > 0 and p_perm <= 0.05), headroom_ok=bool(rB <= 0.90),
               y_sd=float(y.std(ddof=1)), rmse_baseline=float(np.sqrt(((y - pB) ** 2).mean())), rmse_with_gates=float(np.sqrt(((y - pG) ** 2).mean())))
    # exploratory
    ex = {}
    for name, cols in dict(g1_only=B0 + ["g1"], g2_only=B0 + ["g2"], oracle_lnq=B0 + ["f_lnq"]).items():
        p, _ = loo(ok.select(cols).to_numpy(), y)
        ex[name + "_delta_r2"] = float(r2(y, p, base) - rB)
    strata = pl.read_csv(EXP / "results/cohort.csv").select("base", "crust", "stationary").rename({"base": "rule"})
    ex["rule_strata_in_evaluable"] = ok.join(strata, on="rule").group_by("crust", "stationary").len().to_dicts()
    ex["spearman_y_g1"] = float(spearmanr(y, ok["g1"]).statistic)
    ex["spearman_y_g2"] = float(spearmanr(y, ok["g2"]).statistic)
    rep["exploratory"] = ex
    rep["per_rule"] = ok.select("rule", "y_target", *B0, *GATES).with_columns(pl.Series("pred_B0", pB), pl.Series("pred_G", pG)).to_dicts()
    return rep


def main():
    import os
    smoke = os.environ.get("RG_SMOKE") == "1"  # code-path test on shuffled pilot rows; writes only under scratch/
    runs_path = EXP / ("scratch/smoke_runs.csv" if smoke else "results/confirm_runs.csv")
    runs = pl.read_csv(runs_path, schema_overrides={"ext_boundary": pl.Int64, "hole_boundary": pl.Int64})
    rules = pl.read_csv(EXP / "results/cohort.csv")["base"].to_list()
    S = 4 if smoke else json.loads((EXP / "results/seed_count.json").read_text())["S_pred"]
    out = dict(bands={str(b): analyse_band(runs, rules, b, S) for b in (0, 1)})
    gates = {}
    for b, r in out["bands"].items():
        gates[b] = dict(coverage=r["n_rules_evaluable"] >= 20, reliability=all(v["split_half_spearman"] >= 0.7 for v in r["reliability"].values()),
                        headroom=r.get("headroom_ok", False))
    all_gates = all(all(g.values()) for g in gates.values())
    passed = all(r.get("band_pass", False) for r in out["bands"].values())
    out["gates"] = gates
    out["g1_pass_both_bands"] = passed
    out["verdict"] = ("UNINFORMATIVE: at least one gate failed (" + ", ".join(f"band {b}: {[k for k, v in g.items() if not v]}" for b, g in gates.items() if not all(g.values())) + ")"
                      + ("; G1 criterion would have PASSED" if passed else "; G1 criterion would have FAILED")) if not all_gates else ("PASS" if passed else "FAIL (informative)")
    out["provenance"] = dict(git_commit=subprocess.check_output(["git", "rev-parse", "HEAD"], text=True, cwd=ROOT).strip(),
                             script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), lib_sha256=hashlib.sha256((Path(__file__).parent / "rg_lib.py").read_bytes()).hexdigest(),
                             input_sha256=hashlib.sha256(runs_path.read_bytes()).hexdigest(), lam=LAM, bootstrap=NBOOT, bootstrap_seed=BSEED, permutations=PERMS)
    (EXP / ("scratch/smoke_analysis.json" if smoke else "results/confirm_analysis.json")).write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps({k: v for k, v in out.items() if k != "bands"}, indent=1))
    for b, r in out["bands"].items():
        print(b, {k: r.get(k) for k in ("n_rules_evaluable", "r2_baseline", "r2_with_gates", "delta_r2", "delta_ci95", "permutation_p", "band_pass", "headroom_ok", "reliability")})


if __name__ == "__main__":
    main()
