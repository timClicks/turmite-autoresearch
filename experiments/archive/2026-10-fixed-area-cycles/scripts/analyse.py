# /// script
# dependencies = ["polars", "numpy", "scipy"]
# ///
"""Frozen analysis (config.frozen.json / README 'Registration'). Run after run_production.sh.

usage: uv run experiments/archive/2026-10-fixed-area-cycles/scripts/analyse.py
reads dumps/prod16 (primary) and dumps/prod8 (sensitivity);
writes results/rule_summary.csv, results/analysis.json, results/analysis.txt.

Implementation notes (decided before looking at outcomes, see NOTEBOOK):
- Bootstrap for P2 resamples the per-rule leave-one-rule-out error terms (computed once on the 44 rules),
  never refits on bootstrap samples, so a duplicated rule cannot appear in its own training set.
- Spearman uses scipy.stats.spearmanr (average ranks for ties, which only arise in bootstrap resamples).
"""
import hashlib
import argparse
import csv
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import polars as pl
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[4]
EXP = Path(__file__).resolve().parents[1]
CFG = json.loads((EXP / "config.frozen.json").read_text())
GROUPS = {g: list(range(lo, hi + 1)) for g, (lo, hi) in CFG["seed_groups"].items()}
RULES = (EXP / CFG["cohort_file"]).read_text().split()
BANDS = (0, 1)
RNG_SEED, DRAWS = CFG["bootstrap"]["seed"], CFG["bootstrap"]["draws"]
CAP = CFG["step_cap"]


def nearest_rank(v, q):
    v = np.sort(v)
    return float(v[max(int(np.ceil(q * len(v))), 1) - 1])


def load(run):
    d = EXP / "dumps" / run
    frames, stat = [], []
    def records(path):
        # Thousands of two-row files otherwise pay a columnar-parser setup
        # cost apiece. Keep the same column types and order, then construct
        # the columnar frame once for the whole cohort.
        with path.open() as f:
            rows = list(csv.DictReader(f))
        return [{k: (None if v == "" else v if k == "spec" or "_bin_" in k or k == "stop"
                     else float(v) if k in ("sum_pa", "i_q50") else int(v))
                 for k, v in row.items()} for row in rows]
    for rule in RULES:
        for g, seeds in GROUPS.items():
            for s in seeds:
                name = f"{rule}_{s}"
                frames.extend({**row, "rule": rule, "seed": s, "group": g}
                              for row in records(d / f"{name}.bands.csv"))
                stat.extend(records(d / f"{name}.status.csv"))
    return pl.DataFrame(frames, infer_schema_length=None), pl.DataFrame(stat, infer_schema_length=None)


def summarise(run):
    b, status = load(run)
    d = EXP / "dumps" / run
    b = b.with_columns(
        (pl.col("b_dep") / pl.col("steps")).alias("fB"),
        (pl.col("perim_end") / pl.col("area_end")).alias("pa_end"),
        (pl.col("sum_pa") / pl.col("steps")).alias("pa_time"),
    ).with_columns(
        (pl.col("fB") / pl.col("pa_time")).log().alias("lnk_time"),
        (pl.col("fB") / pl.col("pa_end")).log().alias("lnk_end"),
        pl.col("pa_time").log().alias("ln_pa_time"),
    )
    checks = dict(
        runs=status.height,
        not_complete=status.filter(pl.col("stop") != "complete").height,
        max_t_final=int(status["t_final"].max()),
        g_budget_ok=bool(status["t_final"].max() <= CAP // 4),
        unreached=b.filter(pl.col("reached_hi") == 0).height,
        fresh_from_interior=int(b["fresh_from_interior"].sum()),
        bi_ne_steps=b.filter(pl.col("b_dep") + pl.col("i_dep") != pl.col("steps")).height,
        b_partition_bad=b.filter(pl.col("b_complete_steps") + pl.col("b_clip_steps") != pl.col("b_dep")).height,
        i_partition_bad=b.filter(pl.col("i_complete_steps") + pl.col("i_clip_steps") != pl.col("i_dep")).height,
        max_i_clip_share=float((b["i_clip_steps"] / b["i_dep"]).max()),
        i_clip_frags_total=int(b["i_clip_frags"].sum()),
    )
    rows = []
    for rule in RULES:
        for band in BANDS:
            for g, seeds in GROUPS.items():
                s = b.filter((pl.col("rule") == rule) & (pl.col("band_id") == band) & (pl.col("group") == g))
                assert s.height == len(seeds)
                dur = np.concatenate([np.fromfile(d / f"{rule}_{sd}.idur{band}.u32", dtype="<u4") for sd in seeds])
                assert len(dur) == s["i_complete"].sum()
                rows.append(dict(
                    run=run, rule=rule, band=band, group=g, n_seeds=s.height, n_I=len(dur),
                    ln_q999=np.log(nearest_rank(dur, 0.999)) if len(dur) else None,
                    ln_q99=np.log(nearest_rank(dur, 0.99)) if len(dur) else None,
                    ln_max=float(np.log(dur.max())) if len(dur) else None,
                    lnk_time=s["lnk_time"].mean(), lnk_time_sd=s["lnk_time"].std(),
                    lnk_end=s["lnk_end"].mean(), ln_pa_time=s["ln_pa_time"].mean(),
                    ln_meanB=float(np.log(s["b_complete_steps"].sum() / s["b_complete"].sum())),
                    fB=s["fB"].mean(), steps=s["steps"].mean(),
                ))
    return pl.DataFrame(rows), checks


def wide(df, col, band):
    """44-vector per group for one column and band, in cohort order."""
    out = {}
    for g in GROUPS:
        s = df.filter((pl.col("band") == band) & (pl.col("group") == g)).sort("rule")
        assert s["rule"].to_list() == sorted(RULES)
        out[g] = s[col].to_numpy().astype(float)
    return out


def rho(x, y):
    return float(spearmanr(x, y).statistic)


def p1(df, band, kcol="lnk_time"):
    q, k = wide(df, "ln_q999", band), wide(df, kcol, band)
    pairs = [("A", "C"), ("B", "D")]
    stat = np.mean([rho(q[a], k[c]) for a, c in pairs])
    rng = np.random.default_rng(RNG_SEED)
    n = len(RULES)
    boots = []
    for _ in range(DRAWS):
        i = rng.integers(0, n, n)
        boots.append(np.mean([rho(q[a][i], k[c][i]) for a, c in pairs]))
    lo, hi = np.percentile(boots, [2.5, 97.5])
    return dict(statistic=float(stat), per_rotation={f"{a}->{c}": rho(q[a], k[c]) for a, c in pairs}, ci95=[float(lo), float(hi)],
                success=bool(stat <= -0.30 and hi < 0))


def loo_terms(X, y):
    """Per-rule squared LOO error of OLS with intercept, and squared error of the LOO training mean."""
    n = len(y)
    e, s = np.zeros(n), np.zeros(n)
    for i in range(n):
        m = np.arange(n) != i
        A = np.column_stack([np.ones(m.sum()), X[m]]) if X is not None else np.ones((m.sum(), 1))
        beta, *_ = np.linalg.lstsq(A, y[m], rcond=None)
        xi = np.concatenate([[1.0], X[i]]) if X is not None else np.array([1.0])
        e[i] = (y[i] - xi @ beta) ** 2
        s[i] = (y[i] - y[m].mean()) ** 2
    return e, s


def p2(df, band):
    rots = CFG["P2"]["rotations"]
    terms = []
    for r in rots:
        q = wide(df, "ln_q999", band)[r["tail"]]
        mb = wide(df, "ln_meanB", band)[r["baseline"]]
        pa = wide(df, "ln_pa_time", band)[r["baseline"]]
        y = wide(df, "lnk_time", band)[r["outcome"]]
        Xb = np.column_stack([mb, pa])
        Xf = np.column_stack([mb, pa, q])
        e0, s = loo_terms(Xb, y)
        e1, _ = loo_terms(Xf, y)
        terms.append((e0, e1, s))
    gain = lambda idx: np.mean([(t[0][idx].sum() - t[1][idx].sum()) / t[2][idx].sum() for t in terms])
    all_idx = np.arange(len(RULES))
    r2 = [(1 - t[0].sum() / t[2].sum(), 1 - t[1].sum() / t[2].sum()) for t in terms]
    rng = np.random.default_rng(RNG_SEED)
    boots = [gain(rng.integers(0, len(RULES), len(RULES))) for _ in range(DRAWS)]
    lo, hi = np.percentile(boots, [2.5, 97.5])
    g = float(gain(all_idx))
    return dict(gain=g, r2_cv_baseline_full_per_rotation=r2, ci95=[float(lo), float(hi)], success=bool(g >= 0.10 and lo > 0))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", choices=["prod16", "prod8"])
    args = parser.parse_args()
    tag = f".{args.run}" if args.run else ""
    audit_path = EXP / f"results/audit{tag}.json"
    audit = json.loads(audit_path.read_text())
    config_hash = hashlib.sha256((EXP / "config.frozen.json").read_bytes()).hexdigest()
    assert audit["config_sha256"] == config_hash
    manifest = EXP / f"results/production{tag}.sha256"
    assert hashlib.sha256(manifest.read_bytes()).hexdigest() == audit["payload_manifest_sha256"]
    for line in manifest.read_text().splitlines():
        digest, relative = line.split("  ", 1)
        assert hashlib.sha256((EXP / relative).read_bytes()).hexdigest() == digest, relative
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    res = dict(command="uv run experiments/archive/2026-10-fixed-area-cycles/scripts/analyse.py" + (" " + " ".join(sys.argv[1:]) if sys.argv[1:] else ""), commit=commit, dirty_workspace=True,
               config_sha256=config_hash, bootstrap=CFG["bootstrap"],
               audit_sha256=hashlib.sha256(audit_path.read_bytes()).hexdigest(),
               source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
               payload_manifest_sha256=audit["payload_manifest_sha256"])
    out = []
    summaries = {}
    for run in ("prod16", "prod8"):
        if args.run and run != args.run:
            continue
        df, checks = summarise(run)
        summaries[run] = df
        res[run] = dict(checks=checks)
        out.append(f"== {run}: {checks}")
        # gates
        gq = {band: int(df.filter(pl.col("band") == band)["n_I"].min()) for band in BANDS}
        res[run]["g_quantile_min_pooled_n"] = gq
        res[run]["g_quantile_ok"] = {b: gq[b] >= 10_000 for b in BANDS}
        out.append(f"   G-quantile min pooled complete-I per rule x band x group: {gq}  ok={res[run]['g_quantile_ok']}")
        for band in BANDS:
            rel_q = rho(wide(df, "ln_q999", band)["A"], wide(df, "ln_q999", band)["B"])
            rel_k = rho(wide(df, "lnk_time", band)["C"], wide(df, "lnk_time", band)["D"])
            rel_q2 = rho(wide(df, "ln_q999", band)["C"], wide(df, "ln_q999", band)["D"])
            res[run][f"band{band}"] = dict(rel_lnq999_AB=rel_q, rel_lnq999_CD=rel_q2, rel_lnk_CD=rel_k, g_reliab_ok=bool(rel_q >= 0.5 and rel_k >= 0.5))
            P1 = p1(df, band)
            P1e = p1(df, band, "lnk_end")
            P2 = p2(df, band)
            res[run][f"band{band}"].update(P1=P1, P1_kappa_end_sensitivity=P1e, P2=P2)
            # variance components of ln q999 and ln kappa across the 4 groups
            for col in ("ln_q999", "lnk_time"):
                m = np.column_stack([wide(df, col, band)[g] for g in GROUPS])
                within = float(np.mean(np.var(m, axis=1, ddof=1)))
                between = float(np.var(m.mean(axis=1), ddof=1))
                res[run][f"band{band}"][f"{col}_sd_between_rules_of_means"] = float(np.sqrt(between))
                res[run][f"band{band}"][f"{col}_mean_within_rule_group_sd"] = float(np.sqrt(within))
            out.append(f"   band{band}: reliab(ln q999 A~B)={rel_q:.3f} (C~D {rel_q2:.3f}), reliab(ln kappa C~D)={rel_k:.3f} -> G-reliab {'OK' if res[run][f'band{band}']['g_reliab_ok'] else 'FAIL'}")
            out.append(f"   band{band}: P1 stat={P1['statistic']:+.3f} {P1['per_rotation']} CI95={np.round(P1['ci95'], 3).tolist()} success={P1['success']}; kappa_end sens {P1e['statistic']:+.3f} CI={np.round(P1e['ci95'], 3).tolist()}")
            out.append(f"   band{band}: P2 gain={P2['gain']:+.3f} CI95={np.round(P2['ci95'], 3).tolist()} success={P2['success']} (baseline/full R2cv per rotation: {np.round(P2['r2_cv_baseline_full_per_rotation'], 3).tolist()})")
        testable = bool(all(res[run][f"band{b}"]["g_reliab_ok"] and res[run]["g_quantile_ok"][b] for b in BANDS)
                        and checks["g_budget_ok"] and checks["not_complete"] == 0
                        and audit["runs"][run]["max_censor_gate_ratio"] <= 0.10)
        res[run]["statistically_testable"] = testable
        res[run]["P1_overall_success"] = bool(testable and all(res[run][f"band{b}"]["P1"]["success"] for b in BANDS))
        res[run]["P2_overall_success"] = bool(testable and all(res[run][f"band{b}"]["P2"]["success"] for b in BANDS))
        out.append(f"   P1 both bands: {res[run]['P1_overall_success']}; P2 both bands: {res[run]['P2_overall_success']}; testable (G-reliab both bands): {all(res[run][f'band{b}']['g_reliab_ok'] for b in BANDS)}")
    pl.concat(summaries.values()).write_csv(EXP / "results" / f"rule_summary{tag}.csv")
    (EXP / "results" / f"analysis{tag}.json").write_text(json.dumps(res, indent=1, default=float))
    text = "\n".join(out) + "\n"
    (EXP / "results" / f"analysis{tag}.txt").write_text(text)
    print(text)


if __name__ == "__main__":
    main()
