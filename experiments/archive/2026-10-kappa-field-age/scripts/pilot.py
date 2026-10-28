"""Register/run/audit a feasibility pilot; never fits ant outcome associations.

Same launcher is kept in each experiment so every write stays in its own scope.
Run --prepare before --run. Source/config changes require a fresh run name.
"""
from pathlib import Path
import argparse
import csv
import hashlib
import json
import os
import subprocess
import time
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[4]
EXP = Path(__file__).resolve().parents[1]
AGE = EXP.name.endswith("field-age")
EXAMPLE = "kappa_field_age_sampler" if AGE else "kappa_tail_budget_sampler"

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def write_new(p, obj):
    body = json.dumps(obj, indent=2, sort_keys=True) + "\n"
    if p.exists():
        assert p.read_text() == body, f"refuse to replace {p}"
    else:
        p.write_text(body)

def cohort():
    if not AGE:
        p = ROOT / "experiments/archive/2026-10-fixed-area-cycles/results/cohort_rules.txt"
        return p.read_text().split(), {str(p.relative_to(ROOT)): digest(p)}, {}
    p = ROOT / "experiments/archive/2026-10-kappa-rule-space/results/rules_pool.csv"
    rows = list(csv.DictReader(p.open()))
    # Match strata EXACTLY on length and three-letter prefix; lexicographic
    # round-robin through supported blocks, without any new ant outcome.
    blocks = {}
    for r in rows:
        key = (len(r["base"]), r["base"][:3])
        group = int(abs(float(r["g_k"])) >= .05)
        blocks.setdefault(key, [[], []])[group].append(r["base"])
    pairs = []
    for key, groups in sorted(blocks.items()):
        pairs.append(list(zip(*[sorted(g) for g in groups])))
    selected = []
    for i in range(max(map(len, pairs))):
        for block in pairs:
            if i < len(block): selected.append(block[i])
    assert len(selected) >= 2, f"instrument profile lacks support: {len(selected)} matched pairs"
    selected = selected[:24]
    strata = {r: label for pair in selected for r, label in zip(pair, ["stationary", "drifting"])}
    return sorted(strata), {str(p.relative_to(ROOT)): digest(p)}, strata

def prepare(name, profile):
    rules, inputs, strata = cohort()
    seeds = list(range(2026101511 if AGE else 2026101501, 2026101515 if AGE else 2026101505))
    if profile:
        # One matched pair per first two supported blocks for age, four
        # evenly spaced lexicographic cohort rules for tail. Cost only.
        if AGE:
            rules = [r for label in ["stationary", "drifting"] for r in sorted(strata) if strata[r] == label][:0] + [
                sorted(r for r in strata if strata[r] == label)[i] for i in [0, 12] for label in ["stationary", "drifting"]]
        else:
            rules = [rules[i] for i in [0, 11, 22, 33]]
    sources = ["src/field_age.rs", "src/fixed_area.rs", "src/walkers.rs", "src/rule.rs", "src/lib.rs", "Cargo.lock",
               "examples/kappa_tail_budget_sampler.rs", "examples/kappa_field_age_sampler.rs", str(Path(__file__).relative_to(ROOT))]
    cfg = dict(scope="feasibility only; no association, model selection or confirmatory verdict", rules=rules,
               strata={r: strata[r] for r in rules if r in strata}, seeds=seeds,
               control_seeds=[2026101541, 2026101542],
               cap=2**27, grid=4096, bands=[[32768, 34816], [131072,139264]],
               control_cap=2**22, control_bands=[[1024,1088],[4096,4352]],
               threads=4, example=EXAMPLE, pilot_excluded_from_confirmation=True, original_48_rule_cohort_gate="FAILED: only 22 exact matched pairs in existing pool",
               sources={s:digest(ROOT/s) for s in sources}, inputs=inputs,
               definition="depth 0..4 to any visited boundary; departure visits; phase=(initial+visits)%n; cycles=visits//n",
               checkpoint="per completed trajectory only; mid-trajectory state checkpoints NOT implemented; confirmation blocked",
               gates={"accounting":"B+I=steps; fragments conserve labels; hazards sum=steps", "escape":0,
                      "budget":"max pilot t <= cap/4 required before confirmation at this cap",
                      "unresolved_fraction":.05, "coverage":"all pilot specs reported; no exclusions"})
    config_hash = hashlib.sha256(json.dumps(cfg, sort_keys=True).encode()).hexdigest()
    manifest = dict(config=cfg, config_hash=config_hash, git_commit=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip(),
                    recorded_utc=datetime.now(timezone.utc).isoformat(),
                    commands={"prepare":f"uv run {Path(__file__).relative_to(ROOT)} --prepare --name {name}" + (" --profile" if profile else ""),
                              "run":f"uv run {Path(__file__).relative_to(ROOT)} --run --name {name}"},
                    environment={"rustc":subprocess.check_output(["rustc","--version"],text=True).strip(),
                                 "uv":subprocess.check_output(["uv","--version"],text=True).strip()})
    path=EXP/"results"/f"{name}.manifest.json"
    assert not path.exists(), f"already prepared: {path}"
    write_new(path,manifest)
    print(path.relative_to(ROOT), config_hash)

def readrows(path):
    return list(csv.DictReader(path.open()))

def run(name):
    path=EXP/"results"/f"{name}.manifest.json"
    manifest=json.loads(path.read_text()); cfg=manifest["config"]
    for s,h in cfg["sources"].items(): assert digest(ROOT/s)==h, f"source changed: {s}"
    for s,h in cfg["inputs"].items(): assert digest(ROOT/s)==h, f"input changed: {s}"
    binary=ROOT/"target/release/examples"/EXAMPLE
    batches=[("controls",[f"{w}:{s}" for w in ["rotor","rw"] for s in cfg["control_seeds"]], cfg["control_cap"],cfg["control_bands"]),
             ("ants",[f"{r}@{s}" for r in cfg["rules"] for s in cfg["seeds"]],cfg["cap"],cfg["bands"])]
    report={"manifest_sha256":digest(path), "batches":{}, "scientific_tests":"NOT RUN: feasibility only"}
    for label,specs,cap,bands in batches:
        dest=EXP/"dumps"/name/label
        command=[str(binary),str(dest),str(cap),str(cfg["grid"]),",".join(f"{l}-{h}" for l,h in bands),manifest["config_hash"],str(cfg["threads"])]
        start=time.monotonic()
        subprocess.run(["/usr/bin/time","-v",*command],input="\n".join(specs)+"\n",text=True,check=True,cwd=ROOT)
        elapsed=time.monotonic()-start
        runs=[]; payloads={}
        for spec in specs:
            stem=spec.replace(":","_").replace("@","_")
            for f in sorted(dest.glob(stem+".*")): payloads[str(f.relative_to(EXP))]=digest(f)
            status=readrows(dest/f"{stem}.status.csv")[0]
            rows=readrows(dest/f"{stem}.bands.csv")
            hs=readrows(dest/f"{stem}.hazards.csv")
            for row in rows:
                count=sum(int(h["departures"]) for h in hs if h["band"]==row["band"])
                assert count==int(row["steps"])
                assert int(row["B"])+int(row["I"])==count
                assert int(row["tail_overlap"])==int(row["I"])
            runs.append({"spec":spec,"status":status,"bands":[{k:r[k] for k in ["band","reached_lo","reached_hi","steps","I","i_clip","unresolved_overlap"]} for r in rows]})
        report["batches"][label]={"elapsed_seconds":elapsed,"runs":runs,"payload_sha256":payloads,
            "completed":sum(r["status"]["stop"]=="complete" for r in runs),"requested":len(specs),
            "max_t":max(int(r["status"]["t_final"]) for r in runs),
            "escaped":sum(r["status"]["stop"]=="escaped" for r in runs)}
        # Save compact, cell-weighted census rows for the shareable notebook.
        age_rows=[r for spec in specs for r in readrows(dest/f"{spec.replace(':','_').replace('@','_')}.age.csv")]
        p=EXP/"results"/f"{name}.{label}.census.csv"
        if age_rows:
            with p.open("w",newline="") as f:
                wr=csv.DictWriter(f,fieldnames=list(age_rows[0]));wr.writeheader();wr.writerows(age_rows)
    report["limitations"]=["Full cohort pilot only if requested manifest contains full cohort; profile subsets do not satisfy coverage gates.",
        "No mid-run checkpoints; no estimator fitted or calibrated for ant inference; no confirmation launched.",
        "Random-walk cycle count with n=4 is a bookkeeping control, not colour-cycle physics.",
        "Tail entry/return frequencies condition on moving boundary and are not causal age effects."]
    (EXP/"results"/f"{name}.audit.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print(json.dumps({k:{a:b[a] for a in ["completed","requested","max_t","escaped","elapsed_seconds"]} for k,b in report["batches"].items()},indent=2))

if __name__=="__main__":
    ap=argparse.ArgumentParser();ap.add_argument("--name",default="profile-v1");ap.add_argument("--profile",action="store_true");ap.add_argument("--prepare",action="store_true");ap.add_argument("--run",action="store_true")
    args=ap.parse_args();assert args.prepare != args.run
    if args.prepare:prepare(args.name,args.profile)
    else:run(args.name)

