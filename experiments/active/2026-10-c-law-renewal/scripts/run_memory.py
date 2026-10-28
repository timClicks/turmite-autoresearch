"""Fresh build, calibration and resumable excluded finite-memory pilot."""
from __future__ import annotations
import argparse
from concurrent.futures import ThreadPoolExecutor
import csv
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import time
import numpy as np

ROOT = Path(__file__).resolve().parents[4]
EXP = Path(__file__).resolve().parents[1]
OUT = EXP / "results/memory_v1"
CONFIG = EXP / "memory_design.json"


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def write_new(p, value):
    data = json.dumps(value, indent=2, allow_nan=False) + "\n"
    if p.exists():
        raise RuntimeError(f"refusing to replace {p}")
    p.write_text(data)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", required=True, choices=["build", "controls", "pilot"])
    parser.add_argument("--workers", type=int, default=2, choices=[1,2])
    a = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    cfg = json.loads(CONFIG.read_text())
    source_paths = ["src/edge_renewal.rs", "src/local_memory.rs", "src/edge_trace.rs", "src/walkers.rs", "src/rule.rs",
        "examples/c_law_renewal_memory.rs", "tests/local_memory.rs", "tests/edge_renewal.rs", "tests/edge_trace.rs",
        "Cargo.toml", "Cargo.lock", str(CONFIG.relative_to(ROOT)), str(Path(__file__).resolve().relative_to(ROOT)), cfg["rules_source"]]
    if a.stage == "build":
        if (OUT / "build.json").exists():
            raise RuntimeError("fresh build already recorded; reuse it or register a new version")
        target = Path(tempfile.mkdtemp(prefix="turmite-renewal-memory-", dir=Path.home()))
        env = {**os.environ, "CARGO_TARGET_DIR": str(target), "CARGO_BUILD_JOBS": "2"}
        with (OUT / "oracle-tests.log").open("x") as log:
            subprocess.run(["cargo", "test", "--release", "--test", "local_memory", "--test", "edge_renewal", "--test", "edge_trace"], cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT, check=True)
        with (OUT / "build.log").open("x") as log:
            subprocess.run(["cargo", "build", "--release", "--example", "c_law_renewal_memory"], cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT, check=True)
        binary = target / "release/examples/c_law_renewal_memory"
        write_new(OUT / "build.json", {"command": "uv run --frozen experiments/active/2026-10-c-law-renewal/scripts/run_memory.py --stage build",
            "git_revision": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
            "binary": str(binary), "binary_sha256": sha(binary), "fresh_target": str(target),
            "source_sha256": {name: sha(ROOT / name) for name in source_paths},
            "rustc": subprocess.check_output(["rustc", "--version"], text=True).strip(), "test_exit": 0, "build_exit": 0})
        print("Fresh memory instrument built and oracle-tested", flush=True)
        return
    build_path = OUT / "build.json"
    build = json.loads(build_path.read_text())
    binary = Path(build["binary"])
    assert sha(binary) == build["binary_sha256"]
    for name, expected in build["source_sha256"].items():
        assert sha(ROOT / name) == expected, f"source changed: {name}"

    def run(job):
        name, argv = job
        path = OUT / (name + ".json")
        done = path.with_suffix(".done")
        recipe = {"argv": argv, "binary_sha256": build["binary_sha256"],
            "build_sha256": sha(build_path), "config_sha256": sha(CONFIG),
            "driver_sha256": sha(Path(__file__)), "rules_sha256": sha(ROOT / cfg["rules_source"])}
        if done.exists():
            record = json.loads(path.read_text())
            assert done.read_text().strip() == sha(path) and record["recipe"] == recipe
            return name, record["summary"]
        if path.exists():
            raise RuntimeError(f"unmarked result {path}; inspect before resuming")
        started = time.monotonic()
        completed = subprocess.run([str(binary), *argv], cwd=ROOT, capture_output=True, text=True, check=True)
        s = json.loads(completed.stdout)
        assert sum(s["lag"]) == s["boundary_reads"] == sum(s["phase_reads"])
        assert s["births"] == sum(s["phase_births"]) <= s["boundary_reads"]
        if s["window_complete"]:
            assert s["boundary_reads"] == cfg["measure_reads"]
        assert s["boundary_changes"] <= s["boundary_resets"] <= s["boundary_reads"]
        assert sum(s["boundary_reset_lag"]) == s["boundary_resets"]
        if argv[0]=="band" and argv[3] in ["uniform:4","uniform:8","zero:4"]:
            assert s["boundary_reset_lag"][:3] == [0,0,0], "radius >=4 cannot reset a <=16-step return"
        write_new(path, {"recipe": recipe, "summary": s})
        done.write_text(sha(path) + "\n")
        print(name, "complete", s["window_complete"], "reads", s["boundary_reads"], "births", s["births"], "seconds", round(time.monotonic()-started,3), flush=True)
        return name,s

    tail = [str(cfg["warmup_reads"]), str(cfg["measure_reads"]), str(cfg["max_log2"])]
    if a.stage == "controls":
        reports = {}
        prior_path = EXP / "results/pilot_report.json"
        prior_controls = json.loads(prior_path.read_text())["controls"]
        for walker, bounds in [("rotor",(0.47,0.52)),("rw",(0.40,0.48))]:
            jobs = [(f"control-{walker}-{seed}", ["control",walker,str(seed),*tail]) for seed in cfg["control_seeds"]]
            with ThreadPoolExecutor(max_workers=a.workers) as pool:
                rows = list(pool.map(run,jobs))
            rates = [s["births"] / s["boundary_reads"] for _,s in rows]
            reports[walker] = {"n":len(rows),"c_by_seed":rates,"mean":float(np.mean(rates)),"between_seed_sd":float(np.std(rates,ddof=1)),
                "difference_from_parent_fixed_time_mean":float(np.mean(rates)-prior_controls[walker]["mean"]),
                "passed": bool(all(s["window_complete"] and not s["escaped"] for _,s in rows) and bounds[0] <= np.mean(rates) <= bounds[1])}
        argv = ["band","RRRLRRRLLRRLRL","2026102021","uniform:4","2026102061","16","64","12"]
        one = subprocess.check_output([str(binary),*argv], env={**os.environ,"RAYON_NUM_THREADS":"1"})
        six = subprocess.check_output([str(binary),*argv], env={**os.environ,"RAYON_NUM_THREADS":"6"})
        assert one==six
        report = {"command":"uv run --frozen experiments/active/2026-10-c-law-renewal/scripts/run_memory.py --stage controls",
            "build_sha256":sha(build_path),"controls":reports,"thread_identical":True,"thread_check_argv":argv,
            "thread_check_sha256":hashlib.sha256(one).hexdigest(),"passed":all(r["passed"] for r in reports.values()),
            "prior_controls_sha256":sha(prior_path)}
        if not (OUT / "controls.json").exists():
            write_new(OUT / "controls.json",report)
        else:
            assert json.loads((OUT / "controls.json").read_text()) == report
        assert report["passed"], "clock calibration failed; no ant pilot"
        return
    assert json.loads((OUT / "controls.json").read_text())["passed"]
    with (ROOT / cfg["rules_source"]).open() as f:
        rows = [r for r in csv.DictReader(f) if r["split"]==cfg["split"] and r["arm"]==cfg["arms_filter"]]
    assert len(rows)==4
    jobs = []
    for row in rows:
        for seed in row["interior_seeds"].split(";"):
            for mode in cfg["modes"]:
                name = f"{row['family']}-{seed}-{mode.replace(':','-')}"
                argv = ["band",row["rule"],seed,mode,str(cfg["interior_to_reset_seed"][seed]),*tail]
                jobs.append((name,argv))
    with ThreadPoolExecutor(max_workers=a.workers) as pool:
        list(pool.map(run,jobs))
    finished = {"runs":len(jobs),"config_sha256":sha(CONFIG),"build_sha256":sha(build_path),
        "scope":"excluded pilot only; no main outcomes", "all_markers_validated":True}
    if (OUT / "pilot_complete.json").exists():
        assert json.loads((OUT / "pilot_complete.json").read_text()) == finished
    else:
        write_new(OUT / "pilot_complete.json", finished)


if __name__=="__main__":
    main()
