"""Training-only letter baselines on the original chirality holdout; see ../README.md."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import polars as pl

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "experiments/archive/2026-10-probe-growth-census/results"
EDGE = ROOT / "experiments/archive/2026-10-edge-statistics/results/edgestats_sample.csv"
SEED, BOOTSTRAPS = 20261046, 4000


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def group(rule, depth):
    return rule[1:1 + depth]


def fit_baseline(rules, y, depth):
    """Only the explicitly supplied training targets can enter these means."""
    means = {}
    for key in sorted({group(r, depth) for r in rules}):
        means[key] = float(np.mean([v for r, v in zip(rules, y) if group(r, depth) == key]))
    return means


def predict_baseline(rules, means, primary, global_mean, depth):
    return np.array([means.get(group(r, depth), primary.get(group(r, 1), global_mean)) for r in rules])


def ratio_score(sse, denominator):
    return float(1 - sse / denominator) if denominator > 0 else None


def metrics(y, pred, train_mean):
    err = pred - y
    sse = float(err @ err)
    return {"n": len(y), "sse": sse, "rmse": float(np.sqrt(np.mean(err**2))),
            "mae": float(np.mean(np.abs(err))), "median_ae": float(np.median(np.abs(err))),
            "r2": ratio_score(sse, float(np.sum((y - y.mean())**2))),
            "strict_r2": ratio_score(sse, float(np.sum((y - train_mean)**2))),
            "mean_error": float(err.mean())}


def centered_r2(y, pred, labels):
    """Descriptive residual skill; test means are used only for centering scores."""
    yc, pc = y.copy(), pred.copy()
    for label in sorted(set(labels)):
        mask = labels == label
        yc[mask] -= y[mask].mean()
        pc[mask] -= pred[mask].mean()
    return ratio_score(float(np.sum((yc - pc)**2)), float(yc @ yc))


def comparison(y, model, baseline, strata, rng):
    base_error, model_error = (y - baseline)**2, (y - model)**2
    reduction = ratio_score(float(model_error.sum()), float(base_error.sum()))
    sst = float(np.sum((y - y.mean())**2))
    delta = float((base_error.sum() - model_error.sum()) / sst) if sst > 0 else None
    indices = [np.flatnonzero(strata == label) for label in sorted(set(strata))]
    reductions, deltas = [], []
    for _ in range(BOOTSTRAPS):
        idx = np.concatenate([rng.choice(i, len(i), replace=True) for i in indices])
        b, m = float(base_error[idx].sum()), float(model_error[idx].sum())
        den = float(np.sum((y[idx] - y[idx].mean())**2))
        if b > 0:
            reductions.append(1 - m / b)
        if den > 0:
            deltas.append((b - m) / den)
    return {"sse_reduction": reduction,
            "sse_reduction_ci": np.percentile(reductions, [2.5, 97.5]).tolist() if reductions else None,
            "delta_r2": delta,
            "delta_r2_ci": np.percentile(deltas, [2.5, 97.5]).tolist() if deltas else None}


def reconstruct_chirality(cal, rules):
    g = cal.with_columns(kk=pl.min_horizontal(pl.col("colour"), pl.lit(6))).group_by("kk").agg(
        steps=pl.col("edge_steps").sum(), new=pl.col("new_cells").sum(),
        left=pl.col("left_fresh").sum(), right=pl.col("right_fresh").sum()).sort("kk")
    share = (g["steps"] / g["steps"].sum()).to_numpy()
    left = (g["left"] / g["steps"]).to_numpy()
    right = (g["right"] / g["steps"]).to_numpy()
    p0 = g["new"][0] / g["steps"][0]
    predictions = []
    for rule in rules:
        num, den = share[0] * p0, share[0]
        for k in range(1, min(7, len(rule))):
            fl = float(rule[k] == "L") if k < 6 else rule[6:].count("L") / len(rule[6:])
            num += share[k] * (fl * left[k] + (1 - fl) * right[k])
            den += share[k]
        predictions.append(num / den)
    return np.array(predictions)


def main():
    data = pl.read_csv(SOURCE / "c_model.csv").sort("rule")
    probe = pl.read_csv(SOURCE / "probe_summary.csv").filter(~pl.col("bursty")).sort("rule")
    cal = pl.read_csv(EDGE)
    rules = data["rule"].to_list()
    assert len(set(rules)) == len(rules)
    assert rules == probe["rule"].to_list(), "Original non-bursty cohort changed"
    np.testing.assert_array_equal(data["c"].to_numpy(), probe["c"].to_numpy())
    cal_rules = set(cal["rule"].to_list())
    np.testing.assert_array_equal(data["held_out"].to_numpy(), [r not in cal_rules for r in rules])
    np.testing.assert_allclose(data["c_pred"].to_numpy(), reconstruct_chirality(cal, rules), rtol=0, atol=1e-14)
    assert all(r.startswith("R") and 2 <= len(r) <= 12 for r in rules)
    train, test = data.filter(~pl.col("held_out")), data.filter(pl.col("held_out"))
    tr, te = train["rule"].to_list(), test["rule"].to_list()
    ty, y = train["c"].to_numpy(), test["c"].to_numpy()
    train_mean = float(ty.mean())
    primary = fit_baseline(tr, ty, 1)
    secondary = fit_baseline(tr, ty, 3)
    predictions = {"constant": np.full(len(y), train_mean),
                   "letter1": predict_baseline(te, primary, primary, train_mean, 1),
                   "letters123": predict_baseline(te, secondary, primary, train_mean, 3),
                   "chirality": test["c_pred"].to_numpy()}
    assert all(np.isfinite(p).all() for p in predictions.values())
    rng = np.random.default_rng(SEED)
    labels1 = np.array([group(r, 1) for r in te])
    summary = {"seed": SEED, "bootstrap_resamples": BOOTSTRAPS,
               "uncertainty": "Paired rule bootstrap stratified by rule[1]; fitted models fixed; no seed/training uncertainty",
               "n_calibration_edge": len(cal_rules), "n_train_targets": train.height, "n_test": test.height,
               "excluded_calibration_rules": sorted(cal_rules - set(tr)),
               "training_mean": train_mean, "training_group_means": {"letter1": primary, "letters123": secondary},
               "secondary_fallback_test_rules": [r for r in te if group(r, 3) not in secondary],
               "overall": {name: metrics(y, p, train_mean) for name, p in predictions.items()},
               "comparisons": {name: comparison(y, predictions["chirality"], predictions[name], labels1, rng)
                               for name in ("letter1", "letters123")}}
    group_rows = []
    summary["grouping"] = {}
    for depth, name in [(1, "letter1"), (3, "letters123")]:
        labels = np.array([group(r, depth) for r in te])
        residual_sst = sum(float(np.sum((y[labels == k] - y[labels == k].mean())**2)) for k in sorted(set(labels)))
        summary["grouping"][name] = {
            "between_group_variance_fraction": float(1 - residual_sst / np.sum((y - y.mean())**2)),
            "centered_within_r2": {model: centered_r2(y, p, labels) for model, p in predictions.items()},
            "raw_within_r2": {model: ratio_score(float(np.sum((y - p)**2)), residual_sst) for model, p in predictions.items()}}
        for label in sorted(set(labels)):
            mask = labels == label
            training_n = sum(group(r, depth) == label for r in tr)
            for model, pred in predictions.items():
                row = {"grouping": name, "group": label, "model": model, "n_train_group": training_n,
                       "observed_mean": float(y[mask].mean()), "observed_sd": float(y[mask].std(ddof=1)) if mask.sum() > 1 else None,
                       "observed_min": float(y[mask].min()), "observed_max": float(y[mask].max()),
                       **metrics(y[mask], pred[mask], train_mean)}
                # Within each fixed subgroup, bootstrap its rules as paired observations.
                row.update({"vs_baseline_" + k: v for k, v in comparison(
                    y[mask], pred[mask], predictions[name][mask], labels1[mask], rng).items()})
                group_rows.append(row)
    inputs = [SOURCE / "c_model.csv", SOURCE / "probe_summary.csv", EDGE,
              ROOT / "experiments/archive/2026-10-probe-growth-census/scripts/c_model.py", ROOT / "uv.lock",
              Path(__file__)]
    summary["provenance"] = {"git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
                             "working_tree": "Uncommitted changes present; exact input/script hashes below",
                             "command": "uv run experiments/archive/2026-10-chirality-baselines/scripts/compare.py",
                             "python": sys.version, "numpy": np.__version__, "polars": pl.__version__,
                             "inputs_sha256": {p.relative_to(ROOT).as_posix(): sha(p) for p in inputs}}
    summary["registered_predictions"] = {
        "letter1_within_005_r2": abs(summary["overall"]["letter1"]["r2"] - summary["overall"]["chirality"]["r2"]) <= .05,
        "chirality_sse_gain_vs_letters123_below_010": summary["comparisons"]["letters123"]["sse_reduction"] < .10}
    out = HERE / "results"
    out.mkdir(exist_ok=True)
    (out / "comparison.json").write_text(json.dumps(summary, indent=2, allow_nan=False) + "\n")
    pl.DataFrame({"rule": te, "c": y, "group1": labels1, "group123": [group(r, 3) for r in te],
                  **predictions}).write_csv(out / "held_out_predictions.csv")
    # CI arrays live in JSON because CSV columns should be scalars.
    (out / "groups.json").write_text(json.dumps(group_rows, indent=2, allow_nan=False) + "\n")
    pl.DataFrame([{k: v for k, v in row.items() if not k.endswith("_ci")} for row in group_rows]).write_csv(out / "groups.csv")
    print(json.dumps({k: summary[k] for k in ["n_calibration_edge", "n_train_targets", "n_test", "overall", "comparisons", "grouping", "registered_predictions"]}, indent=2))


if __name__ == "__main__":
    main()
