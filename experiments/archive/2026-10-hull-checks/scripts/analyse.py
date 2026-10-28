"""Analyse saved profiles only; never run walkers from analysis/notebooks."""
import argparse
import csv
import json
import subprocess
from pathlib import Path

import numpy as np
from checks import ROOT, EXP, BANDS, coefficients, measure, persistence, digest, calibration


def analyse(pilot=False):
    calibration()  # Interpretation is blocked if the estimator oracle fails.
    folder = EXP / "results" / ("pilot" if pilot else "full")
    manifest = json.loads((folder / "manifest.json").read_text())
    rows, omitted, inputs = [], [], {}
    expected_files = {s.replace(":", "_").replace("@", "_") + ".csv" for s in manifest["specs"]}
    for path in sorted(folder.glob("*.csv")):
        if path.name not in expected_files:
            continue
        marker = path.with_suffix(".done")
        if not marker.exists() or marker.read_text().strip() != digest(path):
            raise ValueError(f"Incomplete/corrupt output: {path}")
        inputs[path.name] = digest(path)
        lines = path.read_text().splitlines()
        omitted.extend(line for line in lines if line.startswith("#"))
        for row in csv.DictReader(line for line in lines if not line.startswith("#")):
            if int(row["empty"]):
                omitted.append(f"{row['spec']} k={row['k']}: {row['empty']} empty bins")
                continue
            r = np.array([float(v) for v in row["profile"].split(";")])
            assert len(r) == 512 and np.all(np.isfinite(r)) and np.all(r > 0)
            rows.append(dict(spec=row["spec"], k=int(row["k"]), cohort=("rotor" if row["spec"].startswith("rotor:") else
                             "legacy" if row["spec"].split("@")[0] in manifest["legacy"] else "sampled"),
                             wout=float(row["Wout"]), coeff=coefficients(r), **measure(r)))
    by_spec = {}
    for row in rows:
        by_spec.setdefault(row["spec"], {})[row["k"]] = row
    for row in rows:
        prev = by_spec[row["spec"]].get(row["k"] - 1)
        for name in ("shape", "local"):
            lo, hi = BANDS[name]
            row[name + "_persistence"] = persistence(prev["coeff"][lo:hi+1], row["coeff"][lo:hi+1]) if prev else None
    rotors = {s: list(rs.values()) for s, rs in by_spec.items() if s.startswith("rotor:")}
    matches = []
    for row in rows:
        if row["cohort"] == "rotor":
            continue
        controls = []
        for s in sorted(rotors):
            nearest = min(rotors[s], key=lambda r: (abs(np.log(r["radius"] / row["radius"])), r["k"]))
            if abs(np.log(nearest["radius"] / row["radius"])) <= np.log(1.1):
                controls.append(nearest)
        matched = dict(spec=row["spec"], k=row["k"], cohort=row["cohort"], controls=len(controls),
                       rotor_checkpoints=[[r["spec"], r["k"]] for r in controls])
        for name in ("shape", "local"):
            denom = np.median([r[name] for r in controls]) if controls else 0
            matched[name + "_ratio"] = float(row[name] / denom) if len(controls) >= 8 and denom > 0 else None
        matches.append(matched)
    rng = np.random.default_rng(20261015)
    summaries = []
    for cohort in ("legacy", "sampled"):
        for k in sorted({r["k"] for r in rows}):
            group = [r for r in matches if r["cohort"] == cohort and r["k"] == k]
            if not group:
                continue
            # Invalid/escaped profiles count against coverage, rather than vanishing
            # from the denominator and making a damaged cohort look well matched.
            expected = sum(not s.startswith("rotor:") and
                           ((s.split("@")[0] in manifest["legacy"]) == (cohort == "legacy"))
                           for s in manifest["specs"])
            item = dict(cohort=cohort, k=k, rows=expected, valid_rows=len(group), matched=sum(r["controls"] >= 8 for r in group))
            for name in ("shape", "local"):
                per_rule = {}
                for r in group:
                    if r[name + "_ratio"] is not None:
                        per_rule.setdefault(r["spec"].split("@")[0], []).append(r[name + "_ratio"])
                meds = np.array([np.median(v) for _, v in sorted(per_rule.items())])
                boot = np.median(rng.choice(meds, (2000, len(meds)), replace=True), axis=1) if len(meds) else []
                item[name] = {"rules": len(meds), "median": float(np.median(meds)) if len(meds) else None,
                              "rule_sd": float(meds.std(ddof=1)) if len(meds) > 1 else None,
                              "ci95": np.quantile(boot, [.025, .975]).tolist() if len(meds) else None,
                              "per_rule": {s: {"median": float(np.median(v)), "seeds": len(v),
                                                "seed_sd": float(np.std(v, ddof=1)) if len(v) > 1 else None}
                                           for s, v in sorted(per_rule.items())}}
            summaries.append(item)
    persistence_summary = {}
    for cohort in ("legacy", "sampled", "rotor"):
        persistence_summary[cohort] = {}
        for name in ("shape", "local"):
            per_rule = {}
            for spec, rs in sorted(by_spec.items()):
                values = [r[name + "_persistence"] for k, r in sorted(rs.items())
                          if r["cohort"] == cohort and 27 <= k <= 30 and r[name + "_persistence"] is not None]
                if values:
                    key = spec.split("@")[0] if cohort != "rotor" else spec
                    per_rule.setdefault(key, []).append(float(np.median(values)))
            values = [np.median(v) for v in per_rule.values()]
            persistence_summary[cohort][name] = float(np.median(values)) if values else None
    slopes = []
    for spec, rs in sorted(by_spec.items()):
        data = [r for k, r in sorted(rs.items()) if 26 <= k <= 30 and r["length"] is not None]
        if len(data) == 5:
            slopes.append({"spec": spec, "length_radius_slope": float(np.polyfit(np.log([r["radius"] for r in data]),
                                                                                 np.log([r["length"] for r in data]), 1)[0])})
    verdicts = {}
    for cohort in ("legacy", "sampled"):
        late = [s for s in summaries if s["cohort"] == cohort and s["k"] in (28, 29, 30)]
        raw_late = [r for r in rows if r["cohort"] in (cohort, "rotor") and r["k"] in (28,29,30)]
        resolution_fraction = float(np.mean([r["coarse_local_ratio"] is not None and abs(r["coarse_local_ratio"] - 1) <= .2 for r in raw_late])) if raw_late else None
        matching_ok = len(late) == 3 and all(s["matched"] / s["rows"] >= .8 for s in late)
        sample_ok = cohort == "legacy" or (len(late) == 3 and all(s["local"]["rules"] >= 8 for s in late))
        shape_ok = len(late) == 3 and all(s["local"]["median"] is not None and s["local"]["median"] <= 1.25 and
            s["shape"]["median"] >= 2 and np.mean([v["median"] <= 1.25 and s["shape"]["per_rule"][r]["median"] >= 2
                for r, v in s["local"]["per_rule"].items()]) >= .8 for s in late)
        ps = persistence_summary[cohort]
        persistent = ps["shape"] is not None and ps["local"] is not None and ps["shape"] >= .7 and ps["shape"] - ps["local"] >= .2
        local_ok = len(late) == 3 and all(s["local"]["median"] is not None and s["local"]["median"] >= 1.5 and
            s["local"]["ci95"][0] > 1 and np.mean([v["median"] >= 1.5 for v in s["local"]["per_rule"].values()]) >= .8 for s in late)
        gates = matching_ok and sample_ok and resolution_fraction is not None and resolution_fraction >= .9
        verdicts[cohort] = dict(matching_ok=matching_ok, sample_ok=sample_ok, resolution_fraction=resolution_fraction,
                               shape_thresholds=shape_ok, persistence=persistent, local_thresholds=local_ok,
                               decision="pilot only" if pilot else "H-shape" if gates and shape_ok and persistent else
                               "H-local" if gates and local_ok else "mixed/unresolved")
    clean_rows = [{k: v for k, v in row.items() if k != "coeff"} for row in rows]
    result = dict(pilot=pilot, commit=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
                  seed=20261015, script_sha256=digest(Path(__file__)), estimator_sha256=digest(EXP / "scripts/checks.py"),
                  manifest_sha256=digest(folder / "manifest.json"), inputs=inputs,
                  missing_files=sorted(expected_files - inputs.keys()), exclusions=omitted,
                  profiles=clean_rows, matched=matches, summaries=summaries, persistence=persistence_summary,
                  length_slopes=slopes, verdicts=verdicts)
    if result["missing_files"]:
        for v in verdicts.values():
            v["decision"] = "incomplete run"
    path = folder / "analysis.json"
    path.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    print(json.dumps({"profiles": len(rows), "exclusions": len(omitted), "missing_files": result["missing_files"], "verdicts": verdicts}, indent=2))


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--pilot", action="store_true")
    analyse(p.parse_args().pilot)
