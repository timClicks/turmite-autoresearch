"""Verify the safe wrapper preserves the completed pilot's compact audit bytes."""
from pathlib import Path
import hashlib
import json
import subprocess
ROOT=Path(__file__).resolve().parents[4]
EXP=Path(__file__).resolve().parents[1]
names=["pilot-v2.audit.json","pilot-v2.manifest.json","pilot-v2.ants.census.csv","pilot-v2.controls.census.csv"]
def hashes():return {n:hashlib.sha256((EXP/"results"/n).read_bytes()).hexdigest() for n in names}
before=hashes()
subprocess.run(["uv","run",str(EXP/"scripts/run.py"),"--name","pilot-v2"],cwd=ROOT,check=True)
assert before==hashes()
report=dict(passed=True,compact_sha256=before,
            scope="Completed full-pilot raw payloads verified by run.py; original compact audits and census bytes preserved. Not a mid-trajectory checkpoint test.",
            source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            wrapper_sha256=hashlib.sha256((EXP/"scripts/run.py").read_bytes()).hexdigest(),
            command=f"uv run {Path(__file__).relative_to(ROOT)}")
(EXP/"results/resume_verification.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
print("Full completed-pilot resume audit preserved")
