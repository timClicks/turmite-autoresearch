"""Known-answer instrument calibrations; outputs stay in this experiment."""
from pathlib import Path
import csv
import hashlib
import json
import subprocess
import numpy as np
ROOT=Path(__file__).resolve().parents[4]
EXP=Path(__file__).resolve().parents[1]
out=EXP/"results/calibration_renewal.csv"
with out.open("w") as f:
    subprocess.run([str(ROOT/"target/release/examples/kappa_tail_budget_calibrate")],stdout=f,check=True)
rows=list(csv.DictReader(out.open()))
report={"seed_range":[2026101561,2026101576],"cycles_per_seed":20000,"families":{},
        "input_sha256":hashlib.sha256(out.read_bytes()).hexdigest(),
        "source_sha256":hashlib.sha256((ROOT/"examples/kappa_tail_budget_calibrate.rs").read_bytes()).hexdigest(),
        "git_commit":subprocess.check_output(["git","rev-parse","HEAD"],text=True,cwd=ROOT).strip(),
        "command":f"uv run {Path(__file__).relative_to(ROOT)}",
        "scope":"Calibration of actual instrument mean/time-mass accounting; NOT calibration of a fitted survival family"}
for family in sorted(set(r["family"] for r in rows)):
    selected=[r for r in rows if r["family"]==family]
    means=np.array([float(r["measured_mean"]) for r in selected])
    occ=np.array([float(r["measured_occupation"]) for r in selected])
    known=float(selected[0]["known_mean"])
    bias=float(means.mean()-known)
    se=float(means.std(ddof=1)/np.sqrt(len(means)))
    report["families"][family]={"mean":float(means.mean()),"known":known,"bias":bias,
        "between_seed_sd":float(means.std(ddof=1)),"mean_bias_within_4se":bool(abs(bias)<4*se),
        "occupation_mean":float(occ.mean()),"known_occupation":float(selected[0]["known_occupation"]),
        "occupation_between_seed_sd":float(occ.std(ddof=1))}
assert all(r["mean_bias_within_4se"] for r in report["families"].values())
(EXP/"results/calibration.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
print(json.dumps(report,indent=2))
