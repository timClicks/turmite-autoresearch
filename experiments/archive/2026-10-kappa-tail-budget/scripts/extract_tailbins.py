"""Compact the entry-conditioned log2 duration bins of pilot-v2 into results/pilot_tailbins.csv.
ONLY bins.csv label I_intersect entry_count / entry_time_sum are read (no B, I or B/S).
Payload hashes are checked against the frozen audit.  uv run scripts/extract_tailbins.py
"""
from pathlib import Path
import csv, hashlib, json
ROOT = Path(__file__).resolve().parents[4]
EXP = Path(__file__).resolve().parents[1]
m = json.loads((EXP / "results/pilot-v2.manifest.json").read_text())["config"]
audit = json.loads((EXP / "results/pilot-v2.audit.json").read_text())
for rel, h in audit["batches"]["ants"]["payload_sha256"].items():
    if rel.endswith(".bins.csv"):
        assert hashlib.sha256((EXP / rel).read_bytes()).hexdigest() == h, rel
rows = []
for rule in m["rules"]:
    for seed in m["seeds"]:
        for r in csv.DictReader((EXP / f"dumps/pilot-v2/ants/{rule}_{seed}.bins.csv").open()):
            if r["label"] == "I_intersect" and int(r["entry_count"]) > 0:
                rows.append((rule, seed, int(r["band"]), int(r["bin"]), int(r["entry_count"]), int(r["entry_time_sum"])))
dest = EXP / "results/pilot_tailbins.csv"
with dest.open("w", newline="") as f:
    w = csv.writer(f); w.writerow(["rule", "seed", "band", "bin", "entry_count", "entry_time_sum"]); w.writerows(rows)
print(len(rows), "rows;", hashlib.sha256(dest.read_bytes()).hexdigest())
