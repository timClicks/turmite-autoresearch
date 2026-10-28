"""Extract the chirality baseline comparison without changing legacy results.

uv run research-outputs/working-papers/cube-root-growth/chirality_baseline_numbers.py
"""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "experiments/archive/2026-10-chirality-baselines/results"
result = json.loads((SOURCE / "comparison.json").read_text())
groups = json.loads((SOURCE / "groups.json").read_text())
output = {"n_train": result["n_train_targets"], "n_test": result["n_test"],
          "seed": result["seed"], "bootstrap_resamples": result["bootstrap_resamples"],
          "overall": result["overall"], "comparisons": result["comparisons"],
          "grouping": result["grouping"],
          "primary_groups": {row["group"]: row for row in groups
                             if row["grouping"] == "letter1" and row["model"] == "chirality"},
          "provenance": {"command": "uv run research-outputs/working-papers/cube-root-growth/chirality_baseline_numbers.py",
                         "input_sha256": {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                                          for p in [SOURCE / "comparison.json", SOURCE / "groups.json", Path(__file__)]}}}
Path(__file__).with_name("chirality_baselines.json").write_text(json.dumps(output, indent=2) + "\n")
