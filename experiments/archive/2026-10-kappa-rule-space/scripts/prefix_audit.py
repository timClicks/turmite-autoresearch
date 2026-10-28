# /// script
# dependencies = ["numpy", "polars", "scipy"]
# ///
"""Frozen prefix-8 robustness audit; see README prefix audit addendum."""
from pathlib import Path
import hashlib
import json
import subprocess
import numpy as np
import polars as pl
from kcommon import census, per_rule, rule_means, EXP, ROOT

SEED = 20261015


def lookup(train, y, test, exclude_self=False):
    groups = {}
    for rule, v in zip(train, y):
        for p in range(1, 9):
            groups.setdefault((p, rule[:p]), []).append(float(v))
    result, support = [], []
    for i, rule in enumerate(test):
        value, depth = float(y.mean()), 0
        for p in range(8, 0, -1):
            g = list(groups.get((p, rule[:p]), []))
            if exclude_self and g:
                g.remove(float(y[i]))
            if len(g) >= 3:
                value, depth = float(np.mean(g)), p
                break
        if depth == 0 and exclude_self:
            value = float((y.sum() - y[i]) / (len(y) - 1))
        result.append(value)
        support.append(depth)
    return np.array(result), np.array(support)


def basis(train, test, flexible):
    knots = np.quantile(train, [.1, .25, .5, .75, .9]) if flexible else []
    def build(a):
        return np.column_stack([a] + [np.maximum(a - k, 0) for k in knots])
    x, z = build(train), build(test)
    mean, sd = x.mean(0), x.std(0)
    assert np.all(sd > 0)
    return (x - mean) / sd, (z - mean) / sd


def predict(x, y, z):
    return np.c_[np.ones(len(z)), z] @ np.linalg.lstsq(
        np.c_[np.ones(len(x)), x], y, rcond=None)[0]


def main():
    # Calibrate the flexible control on a known area-only response and a planted
    # additional signal, with independently drawn test points.
    random = np.random.default_rng(SEED + 2)
    ca, cb = random.uniform(-2, 2, 1000), random.uniform(-2, 2, 500)
    cx, cz = basis(ca, cb, True)
    beta = np.arange(1, cx.shape[1] + 1) / 10
    cy, cv = 2 + cx @ beta, 2 + cz @ beta
    assert np.max(np.abs(predict(cx, cy, cz) - cv)) < 1e-10
    signal, test_signal = random.normal(size=1000), random.normal(size=500)
    planted = predict(np.c_[cx, signal], cy + signal, np.c_[cz, test_signal])
    assert np.max(np.abs(planted - cv - test_signal)) < 1e-10
    # Own labels must not survive the leave-one-out path, even at fallback.
    assert np.allclose(lookup(["RR", "RL"], np.array([1., 3.]), ["RR", "RL"], True)[0], [3., 1.])
    raw_path = EXP / "dumps/w3c_probe.csv"
    raw = pl.read_csv(raw_path)
    runs = per_rule(raw).with_columns(base=pl.col("rule").str.split("@").list.first())
    runs = runs.join(raw.filter(pl.col("k") == 22).select("rule", lnA22=pl.col("area").log()), on="rule", how="left")
    fresh = rule_means(runs.filter(pl.col("alpha_w").is_between(.25, .42) & (pl.col("kappa") > 0)), 6)
    cen = census().filter((pl.col("kappa") > 0) & pl.col("lnA22").is_not_null()).sort("rule")
    inputs = [raw_path, ROOT / "experiments/archive/2026-10-probe-growth-census/results/probe_summary.csv",
              ROOT / "experiments/archive/2026-10-probe-growth-census/results/probe_all.csv",
              Path(__file__), Path(__file__).with_name("kcommon.py"), ROOT / "experiments/_lib/analyse_probe.py"]
    report = {"seed": SEED, "git": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
              "command": "uv run experiments/archive/2026-10-kappa-rule-space/scripts/prefix_audit.py",
              "sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},
              "calibration": "PASS: exact area-only spline and planted additional signal; LOO fallback excludes own label",
              "rows": []}
    predictions = []
    for cohort in ("stationary", "all"):
        tr = cen.filter(pl.col("g_k").abs() < .05) if cohort == "stationary" else cen
        te = fresh.filter(pl.col("g_k").abs() < .05) if cohort == "stationary" else fresh
        rules, tests = tr["rule"].to_list(), te["base"].to_list()
        assert not set(rules) & set(tests), "held-out rules overlap training"
        y, v = np.log(tr["kappa"].to_numpy()), te["lnk"].to_numpy()
        a, b = tr["lnA22"].to_numpy(), te["lnA22"].to_numpy()
        encoded, support = lookup(rules, y, tests)
        fold = np.empty(len(y), dtype=int)
        fold[np.random.default_rng(SEED).permutation(len(y))] = np.arange(len(y)) % 5
        cross = np.empty(len(y))
        for f in range(5):
            keep, hold = fold != f, fold == f
            cross[hold] = lookup([r for r, k in zip(rules, keep) if k], y[keep],
                                 [r for r, k in zip(rules, hold) if k])[0]
        for encoding, train_enc in (("loo", lookup(rules, y, rules, True)[0]), ("crossfit5", cross)):
            for flexible in (False, True):
                x, z = basis(a, b, flexible)
                baseline = predict(x, y, z)
                pred = predict(np.c_[x, train_enc], y, np.c_[z, encoded])
                den = (v - y.mean()) ** 2
                contribution = (v - baseline) ** 2 - (v - pred) ** 2
                gain = float(contribution.sum() / den.sum())
                indices = np.random.default_rng(SEED + 1).integers(0, len(v), (2000, len(v)))
                bs = contribution[indices].sum(1) / den[indices].sum(1)
                top = np.argsort(-contribution, kind="stable")[:5]
                keep = np.ones(len(v), bool); keep[top] = False
                row = dict(cohort=cohort, encoding=encoding, area="spline" if flexible else "linear",
                           n_train=len(y), n_test=len(v), baseline_r2=float(1 - ((v-baseline)**2).sum()/den.sum()),
                           model_r2=float(1 - ((v-pred)**2).sum()/den.sum()), gain=gain,
                           ci=np.quantile(bs, [.025, .975]).tolist(),
                           top5_share=float(contribution[top].sum()/contribution.sum()) if contribution.sum() > 0 else None,
                           without_top5=float(contribution[keep].sum()/den[keep].sum()),
                           top5_rules=[tests[i] for i in top], prefix8_share=float((support == 8).mean()),
                           area_outside_training=int(((b < a.min()) | (b > a.max())).sum()))
                report["rows"].append(row)
                for i, rule in enumerate(tests):
                    predictions.append(dict(cohort=cohort, encoding=encoding, area=row["area"], rule=rule,
                                            target=float(v[i]), lnA22=float(b[i]), prefix_depth=int(support[i]),
                                            baseline=float(baseline[i]), prediction=float(pred[i]), contribution=float(contribution[i])))
    primary = [r for r in report["rows"] if r["cohort"] == "stationary" and r["encoding"] == "crossfit5"]
    linear, spline = primary
    report["expectations"] = {"A1": linear["gain"] >= .15 and linear["ci"][0] > 0,
                              "A2": spline["gain"] >= .5 * linear["gain"] and spline["ci"][0] > 0}
    # Match CSV precision: BLAS reductions can differ below the last reported
    # decimal between processes, without a scientific difference.
    def stable(value):
        if isinstance(value, float):
            return round(value, 12)
        if isinstance(value, list):
            return [stable(v) for v in value]
        if isinstance(value, dict):
            return {k: stable(v) for k, v in value.items()}
        return value
    report["output_decimal_places"] = 12
    (EXP / "results/prefix_audit.json").write_text(json.dumps(stable(report), indent=2) + "\n")
    pl.DataFrame(predictions).write_csv(EXP / "results/prefix_audit_predictions.csv", float_precision=12)
    for row in report["rows"]:
        print(f"{row['cohort']:10s} {row['encoding']:9s} {row['area']:6s} n={row['n_test']} "
              f"R2={row['baseline_r2']:.3f}->{row['model_r2']:.3f} gain={row['gain']:.3f} "
              f"CI={row['ci']} top5={row['top5_share']} without5={row['without_top5']:.3f}")
    print(report["expectations"])


if __name__ == "__main__":
    main()
