"""Compare the exporter against the unchanged instrument and thread counts."""
import json
import os
import subprocess
from pathlib import Path

from checks import ROOT, EXP, digest

target = Path(os.environ.get("CARGO_TARGET_DIR", ROOT / "target")).expanduser() / "release/examples"
new = target / "hull_checks"
old = target / "hull_width"
specs = "RLR@331\nRLRLRRRLLR@332\nrotor:331\n"


def run(binary, args, threads):
    return subprocess.check_output([str(binary), *args], input=specs, text=True, cwd=ROOT,
                                   env={**os.environ, "RAYON_NUM_THREADS": str(threads)})


a = run(new, ["20", "1024", "16"], 1)
b = run(new, ["20", "1024", "16"], 6)
assert a == b, "Exporter depends on thread count"
baseline = run(old, ["20", "1024"], 1)
selected = []
for line in a.splitlines()[1:]:
    cols = line.split(",")
    if int(cols[2]) % 2 == 0:
        selected.append(",".join(cols[:15]))
assert selected == baseline.splitlines()[1:], "Frozen instrument differs from original"
result = dict(status="PASS", compared_rows=len(selected), thread_counts=[1, 6],
              specs=specs.splitlines(), command="uv run experiments/archive/2026-10-hull-checks/scripts/validate.py",
              commit=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
              source_sha256=digest(Path(__file__)), binaries={p.name: digest(p) for p in (new, old)})
(EXP / "results/validation.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
