"""Extract published precision from the W3c result files; no simulations or refits.

uv run research-outputs/cube-root-growth-paper/kappa_prediction_numbers.py
"""
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
E = ROOT / "experiments/archive/2026-10-kappa-rule-space/results"
stats = (E / "w3c_stats.txt").read_text()
cross = (E / "w3c_cross.txt").read_text()


def groups(pattern, text, convert=float):
    match = re.search(pattern, text, re.M)
    if match is None:
        raise ValueError(f"missing result: {pattern}")
    return [convert(x) for x in match.groups()]


stationary = stats.split("[stationary]", 1)[1].split("[all]", 1)[0]
gain, lo, hi, combined, area = groups(
    r"prefix-8 size-controlled gain: ([+\-\d.]+), bootstrap 95% CI ([+\-\d.]+)\.\.([+\-\d.]+).*?with prefix ([+\-\d.]+) vs alone ([+\-\d.]+)", stationary)
n = groups(r"fresh rules (\d+)", stationary, int)[0]
prefix = groups(r"prefix<=8: strict held-out R\^2 ([+\-\d.]+)", stationary)[0]
gain6 = groups(r"prefix-6 size-controlled gain: ([+\-\d.]+)", stationary)[0]
cross_gains = {}
for train, test, value in re.findall(
        r"^train=(\w+)\s+test=(\w+).*?p=8 gain ([+\-\d.]+)", cross, re.M):
    cross_gains[f"{train}_{test}"] = float(value)
assert len(cross_gains) == 4
files = [E / "w3c_stats.txt", E / "w3c_cross.txt", Path(__file__)]
result = dict(n=n, prefix_r2=prefix, gain=gain, ci=[lo, hi],
              combined_r2=combined, area_r2=area, gain6=gain6, cross=cross_gains,
              provenance=dict(command="uv run research-outputs/cube-root-growth-paper/kappa_prediction_numbers.py",
                              commit=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
                              input_sha256={str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}))
(OUT / "kappa_prediction.json").write_text(json.dumps(result, indent=2) + "\n")
