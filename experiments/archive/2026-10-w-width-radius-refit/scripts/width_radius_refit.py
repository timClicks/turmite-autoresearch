"""Registered Wsurf versus radius refit; uv run experiments/archive/2026-10-w-width-radius-refit/scripts/width_radius_refit.py.

Design: notes/walker-comparisons-2026-10-13.md. No simulation or new estimator
of boundary width; inputs are unchanged A4/A4c shape checkpoints.
"""
import csv
import hashlib
import json
from pathlib import Path
import subprocess

import numpy as np

SEED = 20261013
FILES = {family: [f"experiments/archive/2026-10-a4-boundary-width/results/{cohort}_shape_{family}.csv" for cohort in ("a4", "a4c")]
         for family in ("rotor", "ants")}


def slope(x, y):
    return float(np.polyfit(np.log(x), np.log(y), 1)[0])


def load(paths):
    runs = {}
    for path in paths:
        with open(path) as f:
            for row in csv.DictReader(line for line in f if line.startswith(("kind,", "cp,"))):
                spec, k = row["spec"], int(row["k"])
                assert k not in runs.setdefault(spec, {}), (spec, k)
                runs[spec][k] = {key: float(row[key]) for key in ("A", "rg2", "rbar", "Wsurf")}
    return runs


def fit(runs, lo, hi):
    out, excluded = [], []
    ks = list(range(lo, hi + 1, 2))
    for spec in sorted(runs):
        g = runs[spec]
        if not all(k in g and all(v > 0 and np.isfinite(v) for v in g[k].values()) for k in ks):
            excluded.append(spec)
            continue
        t = np.exp2(ks)
        w = np.array([g[k]["Wsurf"] for k in ks])
        radii = {"Req": np.sqrt([g[k]["A"] / np.pi for k in ks]),
                 "Rg": np.sqrt([g[k]["rg2"] for k in ks]),
                 "rbar": np.array([g[k]["rbar"] for k in ks])}
        row = {"spec": spec, "cluster": spec.split("@")[0], "beta_t": slope(t, w)}
        for name, r in radii.items():
            row[name] = slope(r, w)
            row[f"alpha_{name}"] = slope(t, r)
        out.append(row)
    return out, excluded


def summary(rows, family, radius):
    clusters = sorted({r["cluster"] for r in rows})
    means = np.array([np.mean([r[radius] for r in rows if r["cluster"] == c]) for c in clusters])
    rng = np.random.default_rng(SEED)
    bs = np.mean(means[rng.integers(0, len(means), (2000, len(means)))], axis=1)
    vals = np.array([r[radius] for r in rows])
    # Ant uncertainty is across rule means; pooled seed sd mixes rule and seed variation.
    within = [np.std([r[radius] for r in rows if r["cluster"] == c], ddof=1)
              for c in clusters if sum(r["cluster"] == c for r in rows) > 1]
    return {"runs": len(rows), "clusters": len(clusters), "mean": float(means.mean()),
            "pooled_run_sd": float(vals.std(ddof=1)),
            "cluster_sd": float(means.std(ddof=1)),
            "rms_within_rule_sd": float(np.sqrt(np.mean(np.square(within)))) if within else None,
            "mean_ci95": np.quantile(bs, [.025, .975]).tolist(),
            "mean_beta_t": float(np.mean([r["beta_t"] for r in rows])),
            "mean_alpha_t": float(np.mean([r[f"alpha_{radius}"] for r in rows]))}


def main():
    t = np.exp2(np.arange(22, 33, 2))
    r = t ** (1 / 3)
    assert abs(slope(r, r ** (1 / 3)) - 1 / 3) < 1e-12
    assert abs(slope(r, t ** (1 / 8)) - 3 / 8) < 1e-12
    result = {"command": "uv run experiments/archive/2026-10-w-width-radius-refit/scripts/width_radius_refit.py", "base_commit": subprocess.check_output(
        ["git", "rev-parse", "HEAD"], text=True).strip(), "bootstrap_seed": SEED,
        "input_sha256": {p: hashlib.sha256(Path(p).read_bytes()).hexdigest() for ps in FILES.values() for p in ps},
        "synthetic_calibration": "passed", "analyses": {}}
    for label, lo, hi, late_only in (("primary", 22, 32, False), ("late", 26, 32, False),
                                     ("a4c_late", 26, 34, True)):
        entry = {}
        for family, paths in FILES.items():
            rows, excluded = fit(load(paths[1:] if late_only else paths), lo, hi)
            assert rows, (label, family)
            entry[family] = {"excluded": excluded, "fits": rows,
                             "summary": {r: summary(rows, family, r) for r in ("Req", "Rg", "rbar")}}
        a, b = (entry[f]["summary"]["Req"]["mean"] for f in ("ants", "rotor"))
        entry["Req_ratio"] = a / b
        entry["prediction_bands"] = {"rotor": .30 <= b <= .37, "ants": .60 <= a <= .80,
                                      "ratio": 1.7 <= a / b <= 2.3}
        result["analyses"][label] = entry
        print(label, f"k={lo}..{hi}")
        for family in FILES:
            for radius, s in entry[family]["summary"].items():
                print(f"  {family} {radius}: {s}")
            print("  excluded:", entry[family]["excluded"])
        print("  ratio", a / b, "bands", entry["prediction_bands"])
    Path("experiments/archive/2026-10-w-width-radius-refit/results/width_radius_refit.json").write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    main()
