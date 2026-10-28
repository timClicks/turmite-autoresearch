"""Extract committed October follow-up summaries; do not rerun fits or simulations.

Run under uv from the repository root. Input hashes pin the evidence; --check
compares scientific content and hashes without changing the recorded base commit.
"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).with_name("recent_findings.json")
FILES = {
    "c_law": "experiments/archive/2026-10-kappa-chiral-edge/results/c_law.json",
    "edge": "experiments/archive/2026-10-c-law-mechanism/results/stage2_analysis.json",
    "interior": "experiments/archive/2026-10-c-law-mechanism/results/stage2c_analysis.json",
    "conditioning": "experiments/archive/2026-10-c-law-mechanism/results/stage4_analysis.json",
    "uniform": "experiments/archive/2026-10-kappa-uniform-baseline/results/analysis.txt",
    "spread": "experiments/archive/2026-10-kappa-uniform-baseline/results/census_spread.txt",
    "walkers": "experiments/archive/2026-10-kappa-walker-reference/results/analysis.txt",
    "noisy": "experiments/archive/2026-10-kappa-walker-reference/results/analysis_nrotor.txt",
}


def build():
    data = {k: json.loads((ROOT / FILES[k]).read_text())
            for k in ("c_law", "edge", "interior", "conditioning")}
    # Only publish fields used by the manuscript; omitted chain summaries contain
    # undefined estimates represented as NaN in the original scientific record.
    data["edge"] = {k: data["edge"][k] for k in ("L1", "V", "S", "K4_census")}
    data["provenance"] = {
        "command": "uv run research-outputs/scholarly-articles/cube-root-growth/recent_findings_numbers.py",
        "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "sha256": {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest()
                   for p in [*FILES.values(), str(Path(__file__).relative_to(ROOT))]},
        "scope": "Extraction only. Text-source values are cited in Audits 44 and 48; no new measurements.",
    }
    return data


if __name__ == "__main__":
    result = build()
    if "--check" in sys.argv:
        saved = json.loads(OUT.read_text())
        result["provenance"]["git_commit"] = saved["provenance"]["git_commit"]
        if saved != result:
            raise SystemExit("Recent-findings extraction is stale")
        print("Recent-findings values and input hashes match")
    else:
        OUT.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
