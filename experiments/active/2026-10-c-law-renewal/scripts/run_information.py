"""Fresh oracle build, exact baseline replays, then excluded turn-information pilot."""
from __future__ import annotations
import argparse
from concurrent.futures import ThreadPoolExecutor
import csv
import json
import os
from pathlib import Path
import subprocess
import tempfile
import time
from run_memory import sha, write_new

ROOT = Path(__file__).resolve().parents[4]
EXP = Path(__file__).resolve().parents[1]
OUT = EXP / "results/information_v1"
CONFIG = EXP / "information_design.json"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage",required=True,choices=["build","replay","pilot"])
    args = parser.parse_args()
    OUT.mkdir(parents=True,exist_ok=True)
    cfg = json.loads(CONFIG.read_text())
    if args.stage=="build":
        if (OUT / "build.json").exists(): raise RuntimeError("fresh build already recorded")
        target = Path(tempfile.mkdtemp(prefix="turmite-renewal-info-",dir=Path.home()))
        env = {**os.environ,"CARGO_TARGET_DIR":str(target),"CARGO_BUILD_JOBS":"2"}
        with (OUT / "oracle.log").open("x") as log:
            subprocess.run(["cargo","test","--release","--test","local_memory","--test","edge_renewal","--test","edge_trace"],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
        with (OUT / "build.log").open("x") as log:
            subprocess.run(["cargo","build","--release","--example","c_law_renewal_memory"],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
        binary = target / "release/examples/c_law_renewal_memory"
        names = ["src/local_memory.rs","src/edge_renewal.rs","src/edge_trace.rs","src/walkers.rs","src/rule.rs",
            "examples/c_law_renewal_memory.rs","tests/local_memory.rs","tests/edge_renewal.rs","tests/edge_trace.rs","Cargo.toml","Cargo.lock",
            str(CONFIG.relative_to(ROOT)),str(Path(__file__).resolve().relative_to(ROOT)),cfg["rules_source"],
            "experiments/active/2026-10-c-law-renewal/scripts/run_memory.py",
            "experiments/active/2026-10-c-law-renewal/scripts/analyse_information.py",
            "experiments/active/2026-10-c-law-renewal/scripts/analyse_memory.py",
            "experiments/active/2026-10-c-law-renewal/scripts/launch_information.py"]
        write_new(OUT / "build.json",{"command":"uv run --frozen experiments/active/2026-10-c-law-renewal/scripts/run_information.py --stage build",
            "git_revision":subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip(),
            "binary":str(binary),"binary_sha256":sha(binary),"fresh_target":str(target),
            "sources_sha256":{name:sha(ROOT / name) for name in names},"test_exit":0,"build_exit":0,
            "rustc":subprocess.check_output(["rustc","--version"],text=True).strip()})
        print("Information policies freshly built and oracle-tested",flush=True)
        return
    build_path = OUT / "build.json"
    build = json.loads(build_path.read_text())
    binary = Path(build["binary"])
    assert sha(binary)==build["binary_sha256"]
    for name,h in build["sources_sha256"].items(): assert sha(ROOT / name)==h, name
    tail = [str(cfg["warmup_reads"]),str(cfg["measure_reads"]),str(cfg["max_log2"])]
    with (ROOT / cfg["rules_source"]).open() as f:
        bases = [r for r in csv.DictReader(f) if r["split"]=="pilot" and r["arm"]=="base"]
    assert len(bases)==4

    def run(job):
        name,argv,baseline = job
        path = OUT / (name+".json")
        marker = path.with_suffix(".done")
        recipe = {"argv":argv,"binary_sha256":build["binary_sha256"],"build_sha256":sha(build_path),
            "config_sha256":sha(CONFIG),"driver_sha256":sha(Path(__file__)),
            "baseline_file":str(baseline.relative_to(ROOT)) if baseline else None,"baseline_sha256":sha(baseline) if baseline else None}
        if marker.exists():
            record = json.loads(path.read_text())
            assert marker.read_text().strip()==sha(path) and record["recipe"]==recipe
            return record["summary"]
        if path.exists(): raise RuntimeError(f"unmarked output: {path}; inspect before resuming")
        started = time.monotonic()
        result = subprocess.run([str(binary),*argv],cwd=ROOT,capture_output=True,text=True,check=True)
        s = json.loads(result.stdout)
        assert sum(s["lag"])==s["boundary_reads"]==sum(s["phase_reads"])
        assert s["births"]==sum(s["phase_births"])<=s["boundary_reads"]
        assert sum(s["boundary_reset_lag"])==s["boundary_resets"]
        if s["window_complete"]: assert s["boundary_reads"]==cfg["measure_reads"]
        if baseline:
            old = json.loads(baseline.read_text())["summary"]
            assert all(s[k]==v for k,v in old.items()), f"baseline changed: {name}"
        if argv[0]=="band":
            assert s["boundary_reset_lag"][:3]==[0,0,0]
            if argv[3] in ["turn:4","word2:4"]: assert s["boundary_turn_changes"]==0
            if argv[3]=="word2:4": assert s["boundary_next_turn_changes"]==0
            if argv[3]=="next:4": assert s["boundary_next_turn_changes"]==0
        write_new(path,{"recipe":recipe,"summary":s})
        marker.write_text(sha(path)+"\n")
        print(name,"complete",s["window_complete"],"births",s["births"],"changed",s["boundary_changes"],"seconds",round(time.monotonic()-started,3),flush=True)
        return s

    def band_jobs(modes):
        jobs=[]
        for base in bases:
            for seed in base["interior_seeds"].split(";"):
                for mode in modes:
                    name=f"{base['family']}-{seed}-{mode.replace(':','-')}"
                    argv=["band",base["rule"],seed,mode,str(cfg["interior_to_reset_seed"][seed]),*tail]
                    prior=EXP / "results/memory_v1" / (name+".json") if mode in ["full","uniform:4"] else None
                    jobs.append((name,argv,prior))
        return jobs

    if args.stage=="replay":
        controls=[(f"control-{walker}-{seed}",["control",walker,str(seed),*tail],EXP / f"results/memory_v1/control-{walker}-{seed}.json")
            for walker in ["rotor","rw"] for seed in cfg["control_seeds"]]
        with ThreadPoolExecutor(max_workers=2) as pool:
            list(pool.map(run,controls+band_jobs(["full","uniform:4"])))
        argv=["band","RRRRLLRRLLLLRR","2026102021","word2:4","2026102061","16","64","12"]
        one=subprocess.check_output([str(binary),*argv],env={**os.environ,"RAYON_NUM_THREADS":"1"})
        six=subprocess.check_output([str(binary),*argv],env={**os.environ,"RAYON_NUM_THREADS":"6"})
        assert one==six
        record={"controls":16,"ant_baselines":16,"all_old_fields_exact":True,"thread_bytes_identical":True,
            "thread_check_argv":argv,"build_sha256":sha(build_path),"config_sha256":sha(CONFIG)}
        if (OUT / "replay.json").exists(): assert json.loads((OUT / "replay.json").read_text())==record
        else: write_new(OUT / "replay.json",record)
        return
    assert json.loads((OUT / "replay.json").read_text())["all_old_fields_exact"]
    with ThreadPoolExecutor(max_workers=2) as pool:
        list(pool.map(run,band_jobs(["turn:4","next:4","word2:4"])))
    final={"treatment_runs":24,"baseline_runs":16,"all_markers_validated":True,"scope":"excluded pilot only",
        "config_sha256":sha(CONFIG),"build_sha256":sha(build_path)}
    if (OUT / "complete.json").exists(): assert json.loads((OUT / "complete.json").read_text())==final
    else: write_new(OUT / "complete.json",final)


if __name__=="__main__": main()
