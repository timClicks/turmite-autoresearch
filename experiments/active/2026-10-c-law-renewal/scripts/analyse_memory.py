"""Score only the preregistered excluded finite-memory pilot comparisons."""
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


def finite(x):
    return float(x) if math.isfinite(x) else None


def log_error(model, reference):
    return abs(math.log(model / reference)) if model > 0 else math.inf


def main():
    config_path = EXP / "memory_design.json"
    cfg = json.loads(config_path.read_text())
    controls_path = RUNS / "controls.json"
    assert json.loads(controls_path.read_text())["passed"], "clock controls failed"
    assert json.loads((RUNS / "pilot_complete.json").read_text())["runs"] == 56
    inputs = [config_path, controls_path, RUNS / "build.json", RUNS / "pilot_complete.json", ROOT / cfg["rules_source"]]
    build = json.loads((RUNS / "build.json").read_text())
    with (ROOT / cfg["rules_source"]).open() as f:
        bases = [r for r in csv.DictReader(f) if r["split"] == "pilot" and r["arm"] == "base"]
    records = {}
    for base in bases:
        for seed in base["interior_seeds"].split(";"):
            for mode in cfg["modes"]:
                name = f"{base['family']}-{seed}-{mode.replace(':','-')}"
                p = RUNS / (name + ".json")
                record = json.loads(p.read_text())
                assert p.with_suffix(".done").read_text().strip() == sha(p)
                assert record["recipe"]["binary_sha256"] == build["binary_sha256"]
                assert record["recipe"]["config_sha256"] == sha(config_path)
                s = record["summary"]
                assert sum(s["lag"]) == s["boundary_reads"]
                if s["window_complete"]:
                    assert s["boundary_reads"] == cfg["measure_reads"]
                records[(base["family"],seed,mode)] = s
                inputs.append(p)
    comparisons = []
    rule_spread = {}
    for base in bases:
        for seed in base["interior_seeds"].split(";"):
            ref = records[(base["family"],seed,"full")]
            ref_ok = ref["window_complete"] and not ref["escaped"] and ref["births"] >= cfg["min_reference_births"]
            ref_c = ref["births"] / ref["boundary_reads"] if ref["boundary_reads"] else None
            for mode in cfg["modes"]:
                if mode=="full":
                    continue
                s = records[(base["family"],seed,mode)]
                reasons = []
                if not ref["window_complete"]: reasons.append("reference_window_incomplete")
                if ref["births"] < cfg["min_reference_births"]: reasons.append("reference_births_below_500")
                if ref["escaped"]: reasons.append("reference_escaped")
                if not s["window_complete"]: reasons.append("model_window_incomplete")
                if s["escaped"]: reasons.append("model_escaped")
                eligible = ref_ok and s["window_complete"] and not s["escaped"]
                model_c = s["births"] / s["boundary_reads"] if s["boundary_reads"] else None
                err = log_error(model_c,ref_c) if eligible else None
                if eligible and s["births"]:
                    budget = np.abs(np.asarray(s["lag"])/s["births"] - np.asarray(ref["lag"])/ref["births"])
                    max_budget = float(budget.max())
                    budget_values = list(map(float,budget))
                else:
                    max_budget = math.inf if eligible else None
                    budget_values = None
                row = {"family":base["family"],"lead":int(base["lead"]),"rule":base["rule"],"seed":seed,"mode":mode,
                    "eligible":bool(eligible),"exclusion_reasons":reasons,
                    "reference_c":ref_c,"model_c":model_c,"reference_births":ref["births"],"model_births":s["births"],
                    "reference_window_complete":ref["window_complete"],"model_window_complete":s["window_complete"],
                    "abs_log_error": finite(err) if err is not None else None,"error_infinite":bool(eligible and not math.isfinite(err)),
                    "budget_errors_first_lag4_short_long":budget_values,"max_budget_error":finite(max_budget) if max_budget is not None else None,
                    "budget_error_infinite":bool(eligible and not math.isfinite(max_budget)),
                    "boundary_reset_fraction":s["boundary_resets"]/s["boundary_reads"] if s["boundary_reads"] else None,
                    "boundary_changed_fraction":s["boundary_changes"]/s["boundary_reads"] if s["boundary_reads"] else None,
                    "resets_total":s["resets_total"],"physical_steps":s["steps"],"reference_physical_steps":ref["steps"]}
                comparisons.append(row)
        for mode in cfg["modes"]:
            rates = []
            for seed in base["interior_seeds"].split(";"):
                s = records[(base["family"],seed,mode)]
                if s["boundary_reads"]:
                    rates.append(s["births"]/s["boundary_reads"])
            rule_spread[f"{base['family']}:{mode}"] = {"n_seeds_with_reads":len(rates),"c_by_seed":rates,
                "mean_c":float(np.mean(rates)) if rates else None,"between_seed_sd":float(np.std(rates,ddof=1)) if len(rates)>1 else None,
                "includes_partial_windows":any(not records[(base['family'],seed,mode)]["window_complete"] for seed in base["interior_seeds"].split(";"))}
    tests = {}
    for mode in ["uniform:4","uniform:8"]:
        rows = [r for r in comparisons if r["mode"]==mode and r["eligible"]]
        errors = [math.inf if r["error_infinite"] else r["abs_log_error"] for r in rows]
        budgets = [math.inf if r["budget_error_infinite"] else r["max_budget_error"] for r in rows]
        enough = len(rows)>=cfg["min_eligible_pairs"]
        median = float(np.median(errors)) if errors else math.inf
        maximum = max(errors,default=math.inf)
        median_budget = float(np.median(budgets)) if budgets else math.inf
        tests[mode] = {"eligible_pairs":len(rows),"required":cfg["min_eligible_pairs"],
            "median_abs_log_error":finite(median),"median_error_infinite":not math.isfinite(median),
            "max_abs_log_error":finite(maximum),"max_error_infinite":not math.isfinite(maximum),
            "median_max_budget_error":finite(median_budget),"median_budget_infinite":not math.isfinite(median_budget),
            "M1":"UNINFORMATIVE" if not enough else ("HELD" if median<=cfg["M1_median_abs_log"] and maximum<=cfg["M1_max_abs_log"] else "FAILED"),
            "M2":"UNINFORMATIVE" if not enough else ("HELD" if median_budget<=cfg["M2_median_max_budget_error"] else "FAILED")}
    policy_rows = []
    policy_status = []
    for base in bases:
        for seed in base["interior_seeds"].split(";"):
            ref = records[(base["family"],seed,"full")]
            u = records[(base["family"],seed,"uniform:4")]
            z = records[(base["family"],seed,"zero:4")]
            valid = ref["window_complete"] and ref["births"]>=cfg["min_reference_births"] and u["window_complete"] and z["window_complete"] and not any(s["escaped"] for s in [ref,u,z])
            policy_status.append({"family":base["family"],"seed":seed,"windows_and_reference_eligible":bool(valid),
                "both_model_birth_counts_zero":bool(u["births"]==0 and z["births"]==0),"defined_comparison":bool(valid and (u["births"] or z["births"]))})
            if valid and (u["births"] or z["births"]):
                error = abs(math.log(z["births"]/u["births"])) if u["births"] and z["births"] else math.inf
                policy_rows.append({"family":base["family"],"seed":seed,"abs_log_error":finite(error),"infinite":not math.isfinite(error)})
    policy_errors = [math.inf if r["infinite"] else r["abs_log_error"] for r in policy_rows]
    policy_median = float(np.median(policy_errors)) if policy_errors else math.inf
    policy = {"eligible_defined_pairs":len(policy_rows),"median_abs_log_error":finite(policy_median),"median_infinite":not math.isfinite(policy_median),
        "M3":"UNINFORMATIVE" if len(policy_rows)<cfg["min_eligible_pairs"] else ("HELD" if policy_median<=cfg["M3_median_abs_log"] else "FAILED"),"pairs":policy_rows,
        "note":"both-zero policy comparisons are undefined, not passes","status_all_pairs":policy_status}
    report = {"scope":"excluded finite-memory pilot; original P1-P4 and main cohort untested",
        "command":"uv run --frozen experiments/active/2026-10-c-law-renewal/scripts/analyse_memory.py",
        "git_revision":subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip(),
        "script_sha256":sha(Path(__file__)),"config":cfg,"tests":tests,"policy":policy,"comparisons":comparisons,"rule_seed_spread":rule_spread,
        "exposure_caveat":"a match with negligible phase changes is a weak locality challenge; report reset exposure, never infer sufficiency from an unexposed arm",
        "inputs_sha256":{str(p.relative_to(ROOT)):sha(p) for p in inputs}}
    output = EXP / "results/memory_report.json"
    if output.exists():
        raise RuntimeError("refusing to replace prior report; version a new analysis")
    output.write_text(json.dumps(report,indent=2,allow_nan=False)+"\n")
    print(json.dumps({"tests":tests,"policy":policy},indent=2,allow_nan=False),flush=True)


if __name__=="__main__":
    main()
