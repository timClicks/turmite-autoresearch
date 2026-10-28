"""Audit existing stratum support without reading new ant outcomes."""
from pathlib import Path
import csv
import hashlib
import json
import subprocess
ROOT=Path(__file__).resolve().parents[4]
EXP=Path(__file__).resolve().parents[1]
p=ROOT/"experiments/archive/2026-10-kappa-rule-space/results/rules_pool.csv"
rows=list(csv.DictReader(p.open()))
groups={}
for r in rows:
    key=f"{len(r['base'])}:{r['base'][:3]}"
    label="stationary" if abs(float(r["g_k"]))<.05 else "drifting"
    groups.setdefault(key,{"stationary":[],"drifting":[]})[label].append(r["base"])
counts={label:sum(len(g[label]) for g in groups.values()) for label in ["stationary","drifting"]}
report=dict(threshold="stationary iff abs(existing pool median g_k)<0.05; drifting otherwise",
            counts=counts,required_per_stratum=24,unmatched_support_gate=all(n>=24 for n in counts.values()),
            exact_length_prefix3_pairs=sum(min(len(g["stationary"]),len(g["drifting"])) for g in groups.values()),
            blocks=groups,input_path=str(p.relative_to(ROOT)),input_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),
            source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            git_commit=subprocess.check_output(["git","rev-parse","HEAD"],text=True,cwd=ROOT).strip(),
            command=f"uv run {Path(__file__).relative_to(ROOT)}")
(EXP/"results/cohort_audit.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
print(json.dumps({k:report[k] for k in ["counts","required_per_stratum","unmatched_support_gate","exact_length_prefix3_pairs"]},indent=2))
