"""Account for controls/horizon choice and audit excluded-pilot state support."""
from __future__ import annotations
from collections import Counter, defaultdict
import csv
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import numpy as np

ROOT = Path(__file__).resolve().parents[4]
EXP = Path(__file__).resolve().parents[1]
RUNS = EXP / "results/pilot_v1"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def projection(name, source):
    c, word, visited, patch, lag, chain = source
    if name == "S0":
        return c, word, visited
    if name == "S1":
        return c, word, visited, patch
    if name == "S2":
        return source
    # These are support diagnostics only, not chosen scientific models.
    bits = int(name[1])
    local_word = word & ((1 << bits) - 1)
    return local_word, patch


def main():
    inputs = [RUNS / "build.json", RUNS / "horizon.json", RUNS / "thread_check.json"]
    report = {"status": "excluded_pilot_only", "git_revision": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "command": "uv run --frozen experiments/active/2026-10-c-law-renewal/scripts/pilot_report.py",
        "script_sha256": sha(Path(__file__)), "controls": {}}
    for walker, bounds in [("rotor", (0.47, 0.52)), ("rw", (0.40, 0.48))]:
        records = []
        for p in sorted(RUNS.glob(f"{walker}-*.json")):
            assert p.with_suffix(".done").read_text().strip() == sha(p)
            inputs.append(p)
            records.append(json.loads(p.read_text())["summary"])
        ratios = [s["births"] / s["boundary_reads"] for s in records]
        mean = float(np.mean(ratios))
        report["controls"][walker] = {"n": len(ratios), "c_by_seed": ratios, "mean": mean,
            "between_seed_sd": float(np.std(ratios, ddof=1)), "escapes": sum(s["escaped"] for s in records),
            "passed": len(ratios) == 8 and bounds[0] <= mean <= bounds[1] and not any(s["escaped"] for s in records)}
    report["thread_check"] = json.loads(inputs[2].read_text())
    report["horizon"] = json.loads(inputs[1].read_text())
    report["state_support"] = {}
    count_files = sorted(RUNS.glob("*-counts.json"))
    if count_files:
        per_run = {}
        for p in count_files:
            inputs.append(p)
            record = json.loads(p.read_text())
            path = EXP / record["counts_file"]
            assert sha(path) == record["counts_sha256"]
            states = Counter()
            with gzip.open(path, "rt") as f:
                for row in csv.DictReader(f):
                    if row["kind"] == "state":
                        states[tuple(map(int, row["source"].split(":")))] += int(row["count"])
            assert sum(states.values()) == record["summary"]["boundary_reads"]
            per_run[p.stem] = states
        for model in ["S0", "S1", "S2", "C0", "C1", "C2", "C4", "C8"]:
            by_family = defaultdict(Counter)
            projected = {}
            for name, counts in per_run.items():
                family = name.split("-base-")[0].split("-early_swap-")[0].split("-late_swap-")[0]
                projected[name] = Counter()
                for source, count in counts.items():
                    projected[name][projection(model, source)] += count
                by_family[family].update(projected[name])
            details = []
            for name, counts in projected.items():
                family = name.split("-base-")[0].split("-early_swap-")[0].split("-late_swap-")[0]
                training_support = set().union(*(set(c) for f, c in by_family.items() if f != family))
                mass = sum(count for state, count in counts.items() if state not in training_support) / sum(counts.values())
                details.append({"run": name, "unseen_mass": mass, "states": len(counts)})
            report["state_support"][model] = {"max_unseen_mass": max(r["unseen_mass"] for r in details),
                "median_unseen_mass": float(np.median([r["unseen_mass"] for r in details])), "runs": details}
    report["inputs_sha256"] = {str(p.relative_to(ROOT)): sha(p) for p in inputs}
    report["scope"] = "instrument controls and feasibility only; no validation outcomes or mechanism verdict"
    path = EXP / "results/pilot_report.json"
    if path.exists():
        raise RuntimeError("refusing to replace existing report; version a new analysis")
    path.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
