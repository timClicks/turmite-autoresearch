"""Feasibility/reliability only. No tail/age versus kappa model is fit."""
from pathlib import Path
import csv
import hashlib
import json
import re
import numpy as np
from scipy.stats import spearmanr
ROOT=Path(__file__).resolve().parents[4]
EXP=Path(__file__).resolve().parents[1]
name="pilot-v2"
m=json.loads((EXP/f"results/{name}.manifest.json").read_text())
audit=json.loads((EXP/f"results/{name}.audit.json").read_text())
cfg=m["config"]
for batch in audit["batches"].values():
    for relative, expected in batch["payload_sha256"].items():
        assert hashlib.sha256((EXP/relative).read_bytes()).hexdigest()==expected, f"payload changed: {relative}"
def rows(p):return list(csv.DictReader(p.open()))
features=[]
for rule in cfg["rules"]:
    for seed in cfg["seeds"]:
        stem=f"{rule}_{seed}"
        dest=EXP/"dumps"/name/"ants"
        bandrows=rows(dest/f"{stem}.bands.csv")
        bins=rows(dest/f"{stem}.bins.csv")
        ages=rows(dest/f"{stem}.age.csv")
        for b in bandrows:
            k=int(b["band"])
            feature=dict(rule=rule,seed=seed,band=k,reached_hi=int(b["reached_hi"]),steps=int(b["steps"]),
                         unresolved_overlap=int(b["unresolved_overlap"]),I=int(b["I"]),B=int(b["B"]),
                         boundary_complete_n=int(b["b_complete"]),boundary_complete_steps=int(b["b_steps"]))
            selected=[r for r in bins if int(r["band"])==k and r["label"]=="I_intersect"]
            count=sum(int(r["entry_count"]) for r in selected)
            tsum=sum(int(r["entry_time_sum"]) for r in selected)
            feature.update(entry_complete_n=count,entry_full_duration_sum=tsum,entry_mean=tsum/count if count else None)
            for onset in [16,64,256]:
                tail=[r for r in selected if int(r["bin"])>=int(np.log2(onset))]
                tn=sum(int(r["entry_count"]) for r in tail)
                tt=sum(int(r["entry_time_sum"]) for r in tail)
                feature[f"tail_probability_{onset}"]=tn/count if count else None
                feature[f"tail_mean_{onset}"]=tt/tn if tn else None
            c=next((r for r in ages if int(r["band"])==k and int(r["target"])==cfg["bands"][k][0]),None)
            for f in ["immature","median_log_age","cycle_variance"]:feature[f]=float(c[f]) if c else None
            features.append(feature)
dest=EXP/"results/pilot_features.csv"
with dest.open("w",newline="") as f:
    wr=csv.DictWriter(f,fieldnames=list(features[0]));wr.writeheader();wr.writerows(features)
summary={"scope":"Feasibility and split-seed feature reliability only; NO scientific predictions evaluated", "bands":[],
         "analysis_source_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
         "audit_sha256":hashlib.sha256((EXP/f"results/{name}.audit.json").read_bytes()).hexdigest(),
         "source_manifest_sha256":hashlib.sha256((EXP/f"results/{name}.manifest.json").read_bytes()).hexdigest(),
         "input_sha256":hashlib.sha256(dest.read_bytes()).hexdigest(),
         "command":f"uv run {Path(__file__).relative_to(ROOT)}",
         "checkpoint_ready":False,"original_age_cohort_gate":cfg.get("original_48_rule_cohort_gate","not applicable"),
         "requested_rules":len(cfg["rules"]),"seeds_per_rule":len(cfg["seeds"]),"bootstrap": "none: descriptive pilot, no confidence interval or inference"}
for k in range(len(cfg["bands"])):
    fs=[f for f in features if f["band"]==k]
    reliability={};dispersions={}
    for label in ["entry_mean","tail_probability_64","tail_mean_64","immature","median_log_age","cycle_variance"]:
        halves=[[],[]]; sds=[]
        for rule in cfg["rules"]:
            rr=[f for f in fs if f["rule"]==rule and f["reached_hi"] and f[label] is not None]
            if len(rr)!=len(cfg["seeds"]):continue
            rr.sort(key=lambda f:f["seed"])
            for h in [0,1]:halves[h].append(np.mean([float(f[label]) for f in rr[h*2:h*2+2]]))
            sds.append(np.std([float(f[label]) for f in rr],ddof=1))
        rho=float(spearmanr(*halves).statistic) if len(halves[0])>2 else None
        if rho is not None and not np.isfinite(rho):rho=None
        reliability[label]={"spearman_two_seed_halves":rho,"rules":len(halves[0])}
        dispersions[label]={"median_between_seed_sd":float(np.median(sds)) if sds else None}
    unresolved=sum(f["unresolved_overlap"] for f in fs); total=sum(f["I"] for f in fs)
    summary["bands"].append(dict(band=k,lo=cfg["bands"][k][0],completed=sum(f["reached_hi"] for f in fs),requested=len(fs),
        unresolved_overlap=unresolved,unresolved_I_fraction=unresolved/total if total else None,
        min_completed_entry_episodes=min(f["entry_complete_n"] for f in fs),
        split_seed_reliability=reliability,between_seed_dispersion=dispersions))
    if cfg.get("strata"):
        summary["bands"][-1]["by_stratum"]={label:{"requested":sum(cfg["strata"][f["rule"]]==label for f in fs),
            "completed":sum(f["reached_hi"] for f in fs if cfg["strata"][f["rule"]]==label)} for label in sorted(set(cfg["strata"].values()))}
summary["run_gates"]={"all_complete":audit["batches"]["ants"]["completed"]==audit["batches"]["ants"]["requested"],
    "no_escape":audit["batches"]["ants"]["escaped"]==0,"quarter_cap_reserve":audit["batches"]["ants"]["max_t"]<=cfg["cap"]/4,
    "max_t":audit["batches"]["ants"]["max_t"],"elapsed_seconds":audit["batches"]["ants"]["elapsed_seconds"]}
log=(EXP/f"results/{name}.log").read_text()
summary["peak_process_rss_kib"]=[int(v) for v in re.findall(r"Maximum resident set size \(kbytes\): (\d+)",log)]
summary["scientific_verdict"]="NOT TESTED: no fitted/calibrated survival family, outcome seed roles, or frozen confirmatory regression; no causal conclusion"
summary["noncomplete_trajectories"]=[r for r in audit["batches"]["ants"]["runs"] if r["status"]["stop"]!="complete"]
if cfg.get("strata"):
    summary["cohort_audit"]=json.loads((EXP/"results/cohort_audit.json").read_text())
(EXP/"results/pilot_summary.json").write_text(json.dumps(summary,indent=2,sort_keys=True,allow_nan=False)+"\n")
print(json.dumps(summary,indent=2))
