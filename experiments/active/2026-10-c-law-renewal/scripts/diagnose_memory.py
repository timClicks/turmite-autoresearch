"""Exploratory signed budget/phase decomposition and fixed-time clock audit."""
from __future__ import annotations
import csv
import hashlib
import json
import math
from pathlib import Path
import subprocess
import numpy as np

ROOT = Path(__file__).resolve().parents[4]
EXP = Path(__file__).resolve().parents[1]
RUNS = EXP / "results/memory_v1"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    assert (RUNS / "session.exit").read_text().strip()=="0"
    inputs = [EXP / "memory_design.json",EXP / "results/memory_report.json"]
    cfg = json.loads(inputs[0].read_text())
    with (ROOT / cfg["rules_source"]).open() as f:
        bases = [r for r in csv.DictReader(f) if r["split"]=="pilot" and r["arm"]=="base"]
    rows = []
    clock_rows = []
    for base in bases:
        for seed in base["interior_seeds"].split(";"):
            prefix = f"{base['family']}-{seed}"
            reference = RUNS / (prefix+"-full.json")
            inputs.append(reference)
            ref = json.loads(reference.read_text())["summary"]
            fixed_path = EXP / f"results/pilot_v1/{base['family']}-base-{seed}-k26.json"
            fixed = json.loads(fixed_path.read_text())["summary"]
            inputs.append(fixed_path)
            c_ref = ref["births"]/ref["boundary_reads"]
            c_fixed = fixed["births"]/fixed["boundary_reads"]
            clock_rows.append({"family":base["family"],"seed":seed,"event_clock_c":c_ref,"fixed_time_c":c_fixed,
                "ln_event_over_fixed":math.log(c_ref/c_fixed),"event_clock_end_step":ref["steps"],"fixed_time_end_step":fixed["steps"]})
            for mode in cfg["modes"]:
                if mode=="full": continue
                path = RUNS / (prefix+"-"+mode.replace(":","-")+".json")
                inputs.append(path)
                s = json.loads(path.read_text())["summary"]
                if not s["window_complete"] or not s["births"]: continue
                budget = np.asarray(s["lag"])/s["births"] - np.asarray(ref["lag"])/ref["births"]
                phase = np.asarray(s["phase_reads"])/s["births"] - np.asarray(ref["phase_reads"])/ref["births"]
                delta_cost = s["boundary_reads"]/s["births"] - ref["boundary_reads"]/ref["births"]
                assert abs(sum(budget)-delta_cost)<1e-10 and abs(sum(phase)-delta_cost)<1e-10
                rows.append({"family":base["family"],"rule":base["rule"],"lead":int(base["lead"]),"seed":seed,"mode":mode,
                    "ln_c_model_over_full":math.log((s["births"]/s["boundary_reads"])/c_ref),"delta_reads_per_birth":delta_cost,
                    "signed_budget_delta_first_lag4_short_long":list(map(float,budget)),"signed_phase_read_cost_delta":list(map(float,phase)),
                    "full_budget":list(map(float,np.asarray(ref["lag"])/ref["births"])),"model_budget":list(map(float,np.asarray(s["lag"])/s["births"])),
                    "boundary_reset_fraction":s["boundary_resets"]/s["boundary_reads"],"boundary_changed_fraction":s["boundary_changes"]/s["boundary_reads"],
                    "boundary_reset_lag":s["boundary_reset_lag"]})
    report = {"scope":"exploratory after failed M1/M2; no new confirmatory claim",
        "command":"uv run --frozen experiments/active/2026-10-c-law-renewal/scripts/diagnose_memory.py",
        "git_revision":subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip(),"script_sha256":sha(Path(__file__)),
        "decomposition":rows,"clock_audit":clock_rows,"inputs_sha256":{str(p.relative_to(ROOT)):sha(p) for p in inputs}}
    path = EXP / "results/memory_diagnostics.json"
    if path.exists(): raise RuntimeError("refusing prior diagnostic overwrite")
    path.write_text(json.dumps(report,indent=2,allow_nan=False)+"\n")
    for row in rows:
        if row["mode"] in ["uniform:4","uniform:8"]:
            print(row["family"],row["seed"],row["mode"],"d cost",round(row["delta_reads_per_birth"],4),"budget",[round(x,4) for x in row["signed_budget_delta_first_lag4_short_long"]],"reset",round(row["boundary_reset_fraction"],4))
    print("clock ln ratios",[round(r["ln_event_over_fixed"],4) for r in clock_rows])


if __name__=="__main__": main()
