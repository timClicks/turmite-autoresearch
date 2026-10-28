"""Freeze full-cohort feasibility pilot AFTER the separate cost profile.
No scientific outcome model or confirmation is authorized by this manifest.
"""
from pathlib import Path
import json
import hashlib
import subprocess
from datetime import datetime, timezone
import pilot
EXP=Path(__file__).resolve().parents[1]
ROOT=Path(__file__).resolve().parents[4]
m=json.loads((EXP/"results/profile-v1.manifest.json").read_text())
audit=json.loads((EXP/"results/profile-v1.audit.json").read_text())
assert audit["batches"]["ants"]["completed"]==16
rules,inputs,strata=pilot.cohort()
cfg=m["config"].copy()
cfg.update(rules=rules,strata=strata,inputs=inputs,cap=2**30,
           bands=[[32768,34816],[131072,139264],[524288,557056]],
           profile_cost_seconds=audit["batches"]["ants"]["elapsed_seconds"],
           resource_budget="4 workers, 4096 board; <=2 GiB aggregate expected; <=30 minutes per experiment, check logs and stop if exceeded",
           decision="Extend to third candidate band to measure attainment/censoring and cost; no ant association or model selection. Original field-age 48-rule support gate remains failed when applicable.")
cfg["sources"]=dict(cfg["sources"])
cfg["sources"]={s:hashlib.sha256((ROOT/s).read_bytes()).hexdigest() for s in cfg["sources"]}
cfg["sources"][str(Path(__file__).relative_to(ROOT))]=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
cfg["sources"]["examples/kappa_tail_budget_calibrate.rs"]=hashlib.sha256((ROOT/"examples/kappa_tail_budget_calibrate.rs").read_bytes()).hexdigest()
cfg["calibration_sha256"]=hashlib.sha256((EXP/"results/calibration.json").read_bytes()).hexdigest()
m.update(config=cfg,config_hash=hashlib.sha256(json.dumps(cfg,sort_keys=True).encode()).hexdigest(),
         git_commit=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip(),
         recorded_utc=datetime.now(timezone.utc).isoformat(),
         commands={"prepare":f"uv run {Path(__file__).relative_to(ROOT)}", "run":f"uv run {Path(__file__).with_name('pilot.py').relative_to(ROOT)} --run --name pilot-v2"})
pilot.write_new(EXP/"results/pilot-v2.manifest.json",m)
print(f"Frozen {len(rules)} rules x {len(cfg['seeds'])} seeds, three bands; {m['config_hash']}")
