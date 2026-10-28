"""Frozen read-bit/write-bit pilot scoring; no fits or held-out claims."""
from __future__ import annotations
import csv
import json
import math
from pathlib import Path
import subprocess
import numpy as np
from run_memory import sha, write_new
from analyse_memory import finite, log_error

ROOT = Path(__file__).resolve().parents[4]
EXP = Path(__file__).resolve().parents[1]
RUNS = EXP / "results/information_v1"


def main():
    config_path = EXP / "information_design.json"
    cfg = json.loads(config_path.read_text())
    replay = json.loads((RUNS / "replay.json").read_text())
    assert replay["all_old_fields_exact"] and replay["thread_bytes_identical"]
    assert json.loads((RUNS / "complete.json").read_text())["treatment_runs"]==24
    inputs = [config_path,RUNS / "replay.json",RUNS / "complete.json",RUNS / "build.json",ROOT / cfg["rules_source"]]
    with (ROOT / cfg["rules_source"]).open() as f:
        bases = [r for r in csv.DictReader(f) if r["split"]=="pilot" and r["arm"]=="base"]
    records = {}
    for base in bases:
        for seed in base["interior_seeds"].split(";"):
            for mode in cfg["modes"]:
                path = RUNS / f"{base['family']}-{seed}-{mode.replace(':','-')}.json"
                assert path.with_suffix(".done").read_text().strip()==sha(path)
                record = json.loads(path.read_text())
                assert record["recipe"]["config_sha256"]==sha(config_path)
                records[(base["family"],seed,mode)] = record["summary"]
                inputs.append(path)
    rows=[]
    spreads={}
    for base in bases:
        for seed in base["interior_seeds"].split(";"):
            ref = records[(base["family"],seed,"full")]
            for mode in cfg["modes"][1:]:
                model=records[(base["family"],seed,mode)]
                reasons=[]
                if not ref["window_complete"]: reasons.append("reference_incomplete")
                if ref["births"]<cfg["min_reference_births"]: reasons.append("reference_births_below_500")
                if not model["window_complete"]: reasons.append("treatment_incomplete")
                if ref["escaped"] or model["escaped"]: reasons.append("escaped")
                eligible=not reasons
                c_ref=ref["births"]/ref["boundary_reads"] if ref["boundary_reads"] else None
                c_model=model["births"]/model["boundary_reads"] if model["boundary_reads"] else None
                error=log_error(c_model,c_ref) if eligible else None
                if eligible and model["births"]:
                    budget=np.asarray(model["lag"])/model["births"]-np.asarray(ref["lag"])/ref["births"]
                    budget_error=float(np.abs(budget).max())
                else:
                    budget=None
                    budget_error=math.inf if eligible else None
                row={"family":base["family"],"rule":base["rule"],"lead":int(base["lead"]),"seed":seed,"mode":mode,
                    "eligible":eligible,"exclusion_reasons":reasons,"reference_c":c_ref,"model_c":c_model,
                    "abs_log_error":finite(error) if error is not None else None,"error_infinite":bool(eligible and not math.isfinite(error)),
                    "max_budget_error":finite(budget_error) if budget_error is not None else None,
                    "budget_error_infinite":bool(eligible and not math.isfinite(budget_error)),
                    "signed_budget_delta_first_lag4_short_long":list(map(float,budget)) if budget is not None else None,
                    "boundary_phase_changed_fraction":model["boundary_changes"]/model["boundary_reads"] if model["boundary_reads"] else None,
                    "boundary_reset_fraction":model["boundary_resets"]/model["boundary_reads"] if model["boundary_reads"] else None,
                    "boundary_turn_changes":model["boundary_turn_changes"],"boundary_next_turn_changes":model["boundary_next_turn_changes"],
                    "boundary_ambiguous_resets":model["boundary_ambiguous_resets"],"physical_steps":model["steps"],
                    "window_complete":model["window_complete"],"births":model["births"],"boundary_reads":model["boundary_reads"]}
                rows.append(row)
        for mode in cfg["modes"]:
            samples=[records[(base["family"],seed,mode)] for seed in base["interior_seeds"].split(";")]
            rates=[s["births"]/s["boundary_reads"] for s in samples if s["boundary_reads"]]
            spreads[f"{base['family']}:{mode}"]={"c_by_seed":rates,"mean":float(np.mean(rates)) if rates else None,
                "between_seed_sd":float(np.std(rates,ddof=1)) if len(rates)>1 else None,
                "partial_windows":sum(not s["window_complete"] for s in samples)}
    tests={}
    for mode in ["turn:4","next:4","word2:4"]:
        pairs=[r for r in rows if r["mode"]==mode and r["eligible"]]
        err=[math.inf if r["error_infinite"] else r["abs_log_error"] for r in pairs]
        budget=[math.inf if r["budget_error_infinite"] else r["max_budget_error"] for r in pairs]
        median=float(np.median(err)) if err else math.inf
        maximum=max(err,default=math.inf)
        med_budget=float(np.median(budget)) if budget else math.inf
        sensitive=[r for r in pairs if r["rule"]==cfg["sensitive_rule"]]
        sensitive_cost=max((math.inf if r["error_infinite"] else r["abs_log_error"] for r in sensitive),default=math.inf)
        sensitive_budget=max((math.inf if r["budget_error_infinite"] else r["max_budget_error"] for r in sensitive),default=math.inf)
        enough=len(pairs)>=cfg["min_eligible_pairs"]
        i1="UNINFORMATIVE" if not enough else ("HELD" if median<=cfg["median_abs_log_limit"] and maximum<=cfg["max_abs_log_limit"] else "FAILED")
        i2="UNINFORMATIVE" if not enough or len(sensitive)!=2 else ("HELD" if med_budget<=cfg["median_budget_error_limit"] and sensitive_cost<=cfg["sensitive_max_abs_log_limit"] and sensitive_budget<=cfg["sensitive_max_budget_error_limit"] else "FAILED")
        exposed=[r for r in pairs if r["boundary_phase_changed_fraction"]>=cfg["min_changed_boundary_fraction"]]
        exposed_sensitive=[r for r in exposed if r["rule"]==cfg["sensitive_rule"]]
        i3="HELD" if len(exposed)>=cfg["min_exposed_pairs"] and len(exposed_sensitive)==2 else "UNINFORMATIVE"
        candidate="REJECTED_ON_PILOT" if "FAILED" in [i1,i2] else ("SUPPORTED_ON_PILOT_ONLY" if i1==i2==i3=="HELD" else "UNINFORMATIVE")
        tests[mode]={"eligible_pairs":len(pairs),"median_abs_log_error":finite(median),"max_abs_log_error":finite(maximum),
            "cost_has_infinite_error":any(not math.isfinite(e) for e in err),"median_max_budget_error":finite(med_budget),
            "sensitive_eligible_pairs":len(sensitive),"sensitive_max_abs_log_error":finite(sensitive_cost),"sensitive_max_budget_error":finite(sensitive_budget),
            "exposed_pairs":len(exposed),"exposed_sensitive_pairs":len(exposed_sensitive),"I1":i1,"I2":i2,"I3":i3,"candidate":candidate}
    report={"scope":"explanatory excluded pilot; sensitive rule selected from earlier results; no main validation",
        "command":"uv run --frozen experiments/active/2026-10-c-law-renewal/scripts/analyse_information.py",
        "git_revision":subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip(),"script_sha256":sha(Path(__file__)),
        "config":cfg,"tests":tests,"pairs":rows,"rule_seed_spread":spreads,"inputs_sha256":{str(p.relative_to(ROOT)):sha(p) for p in inputs}}
    write_new(EXP / "results/information_report.json",report)
    print(json.dumps(tests,indent=2,allow_nan=False),flush=True)


if __name__=="__main__": main()
