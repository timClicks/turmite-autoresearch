"""Resume a pilot while preserving the original completed timing audit.
The frozen low-level runner is intentionally unchanged. It handles partial
trajectory batches; this wrapper verifies/reuses an already completed audit.
"""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
ROOT=Path(__file__).resolve().parents[4]
EXP=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser();ap.add_argument("--name",default="pilot-v2")
args=ap.parse_args()
manifest=EXP/"results"/f"{args.name}.manifest.json"
m=json.loads(manifest.read_text())
for relative,expected in m["config"]["sources"].items():
    assert hashlib.sha256((ROOT/relative).read_bytes()).hexdigest()==expected,f"source changed: {relative}; retain results and register a new run"
audit=EXP/"results"/f"{args.name}.audit.json"
if audit.exists():
    a=json.loads(audit.read_text())
    assert a["manifest_sha256"]==hashlib.sha256(manifest.read_bytes()).hexdigest()
    for label,b in a["batches"].items():
        for relative,expected in b["payload_sha256"].items():
            assert hashlib.sha256((EXP/relative).read_bytes()).hexdigest()==expected,f"saved payload changed: {relative}"
        assert (EXP/"results"/f"{args.name}.{label}.census.csv").is_file()
    print("Verified completed pilot; original outputs and timing audit preserved:",args.name)
else:
    subprocess.run(["uv","run",str(EXP/"scripts/pilot.py"),"--run","--name",args.name],cwd=ROOT,check=True)
