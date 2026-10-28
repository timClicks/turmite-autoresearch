"""Run with uv; deterministic paired summaries of local_patch_RULE.csv."""
import csv
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
out = {}
for rule in ("RLLLLRRL", "LRRRRRLLR", "RLLLLLLLRRLRR"):
    path = root / "results" / f"local_patch_{rule}.csv"
    rows = list(csv.DictReader(path.open()))
    pairs = {}
    for row in rows:
        pairs.setdefault(row["t_start"], {})[row["background"]] = row
    def displacement(row):
        return min(abs(int(row["dx"])), abs(int(row["dy"])))
    wins = sum(displacement(p["2"]) > displacement(p["0"]) for p in pairs.values())
    out[rule] = dict(pairs=len(pairs), colour_2_wins=wins,
                     prediction_passed=len(pairs) == 12 and wins >= 9,
                     input_sha256=hashlib.sha256(path.read_bytes()).hexdigest())
target = root / "results" / "local_patch_summary.json"
target.write_text(json.dumps(out, indent=2) + "\n")
print(target.read_text())
