"""Run a few seeded analysis scripts twice, under different PYTHONHASHSEED values, and require byte-identical output.

Guards against the hash-order bug found on 2026-10-28 (notes/reproducibility-audit-2026-10-28.md): polars
group_by()/unique() and Python sets of str iterate in per-process hash order, and where that order decides which
unit receives which seeded draw, results change between runs. Each script's stdout and the files it writes are
compared; tracked files are restored to their committed bytes after every run.

usage (repo root): uv run --frozen python .github/scripts/check_python_determinism.py
"""

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
# (script, files it writes). Chosen to be fast (seconds) and to cover polars group_by/unique feeding a seeded bootstrap.
CHECKS = [
    ("experiments/archive/2026-10-kappa-matched-area/scripts/matched_area.py",
     ["experiments/archive/2026-10-kappa-matched-area/results/matched_area.txt"]),
    ("experiments/archive/2026-10-hull-width/scripts/hull_stats.py",
     ["experiments/archive/2026-10-hull-width/results/hull_stats.txt"]),
    ("experiments/archive/2026-10-kappa-exposure-classes/scripts/explore.py",
     ["experiments/archive/2026-10-kappa-exposure-classes/results/explore.txt"]),
    ("experiments/archive/2026-10-kappa-prefix-additive/scripts/additive.py",
     ["experiments/archive/2026-10-kappa-prefix-additive/results/additive.txt",
      "experiments/archive/2026-10-kappa-prefix-additive/results/additive.json"]),
    ("experiments/active/2026-10-wall-vs-memory/scripts/analyse_stage3b.py",
     ["experiments/active/2026-10-wall-vs-memory/results/stage3b_runs.csv",
      "experiments/active/2026-10-wall-vs-memory/results/stage3b_analysis.txt"]),
    ("experiments/active/2026-10-wall-vs-memory/scripts/analyse_stage3c.py",
     ["experiments/active/2026-10-wall-vs-memory/results/stage3c_runs.csv",
      "experiments/active/2026-10-wall-vs-memory/results/stage3c_analysis.txt"]),
]


def run(script: str, outputs: list[str], hashseed: str) -> dict[str, bytes]:
    saved = {p: (ROOT / p).read_bytes() for p in outputs if (ROOT / p).exists()}
    try:
        env = {**os.environ, "PYTHONHASHSEED": hashseed}
        res = subprocess.run([sys.executable, script], cwd=ROOT, env=env, capture_output=True, check=True)
        got = {"<stdout>": res.stdout}
        got.update({p: (ROOT / p).read_bytes() for p in outputs})
        return got
    finally:
        for p, b in saved.items():
            (ROOT / p).write_bytes(b)


failed = []
for script, outputs in CHECKS:
    a, b = run(script, outputs, "1"), run(script, outputs, "2")
    bad = [k for k in a if a[k] != b[k]]
    print(f"{'DIFF' if bad else 'same'}  {script}" + (f"  ({', '.join(bad)})" if bad else ""))
    failed += [f"{script}: {k}" for k in bad]
if failed:
    sys.exit("hash-order dependence:\n  " + "\n  ".join(failed))
print(f"{len(CHECKS)} scripts byte-identical under PYTHONHASHSEED 1 and 2")
