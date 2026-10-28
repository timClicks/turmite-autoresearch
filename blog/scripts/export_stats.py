"""Export a small, auditable browser dataset from committed probe results.

Run from the repository root with: uv run --frozen blog/scripts/export_stats.py
No simulation or scientific result files are modified.
"""
import csv
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
SOURCE = "experiments/archive/2026-10-kappa-walker-reference/results/probe_nrotor.csv"
ANALYSIS = "experiments/archive/2026-10-kappa-walker-reference/results/analysis_nrotor.txt"


def export():
    revision = subprocess.check_output(
        ["git", "log", "-1", "--format=%H", "--", SOURCE, ANALYSIS], cwd=ROOT, text=True
    ).strip()
    inputs = {}
    for name in (SOURCE, ANALYSIS):
        raw = (ROOT / name).read_bytes()
        pinned = subprocess.check_output(["git", "show", f"{revision}:{name}"], cwd=ROOT)
        if raw != pinned:
            raise ValueError(f"Commit source changes before exporting: {name}")
        inputs[name] = hashlib.sha256(raw).hexdigest()
    runs = {}
    with (ROOT / SOURCE).open(newline="") as stream:
        for row in csv.DictReader(stream):
            _, eps, seed = row["rule"].split(":")
            run = runs.setdefault(row["rule"], {
                "eps": float(eps), "seed": int(seed), "escaped": False, "windows": []
            })
            # escaped labels the whole run, including valid windows before escape.
            run["escaped"] |= row["escaped"] == "true"
            run["windows"].append([int(row[k]) for k in
                                   ("k", "t", "area", "perimeter", "boundary_steps")])
    data = {
        "kind": "noisy-rotor", "revision": revision, "inputs": inputs,
        "command": "uv run --frozen blog/scripts/export_stats.py",
        "columns": ["k", "t", "area", "perimeter", "boundary_steps"],
        "runs": [dict(run, windows=sorted(run["windows"])) for _, run in sorted(runs.items())],
    }
    output = ROOT / "blog/_data/noisy_rotor.json"
    output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(data, separators=(",", ":")) + "\n", encoding="utf-8")
    print(f"Exported {len(runs)} runs to {output.relative_to(ROOT)}")


if __name__ == "__main__":
    export()
