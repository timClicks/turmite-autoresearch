"""Resumable excluded pilot and walker accounting controls. Never opens main outcomes."""
from __future__ import annotations
import argparse
import csv
import gzip
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import time

ROOT = Path(__file__).resolve().parents[4]
EXP = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", choices=["build", "controls", "pilot"], required=True)
    args = parser.parse_args()
    results = EXP / "results" / "pilot_v1"
    results.mkdir(parents=True, exist_ok=True)
    build_file = results / "build.json"
    if args.stage == "build":
        if build_file.exists():
            raise RuntimeError("build already recorded; reuse it or register a versioned rebuild")
        target = Path(tempfile.mkdtemp(prefix="turmite-renewal-", dir=Path.home()))
        env = {**os.environ, "CARGO_TARGET_DIR": str(target), "CARGO_BUILD_JOBS": "2"}
        with (results / "build.log").open("w") as log:
            subprocess.run(["cargo", "build", "--release", "--example", "c_law_renewal_trace"], cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT, check=True)
        binary = target / "release/examples/c_law_renewal_trace"
        sources = [ROOT / "src/edge_renewal.rs", ROOT / "src/edge_trace.rs", ROOT / "src/walkers.rs", ROOT / "src/rule.rs", ROOT / "src/lib.rs", ROOT / "examples/c_law_renewal_trace.rs", ROOT / "Cargo.toml", ROOT / "Cargo.lock", Path(__file__)]
        record = {"command": "uv run --frozen experiments/active/2026-10-c-law-renewal/scripts/run_pilot.py --stage build",
            "git_revision": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
            "binary": str(binary), "binary_sha256": sha(binary),
            "sources_sha256": {str(p.relative_to(ROOT)): sha(p) for p in sources},
            "rustc": subprocess.check_output(["rustc", "--version"], text=True).strip(),
            "build_exit_status": 0, "fresh_target": str(target)}
        build_file.write_text(json.dumps(record, indent=2) + "\n")
        print("Built fresh instrument", binary, flush=True)
        return
    build = json.loads(build_file.read_text())
    binary = Path(build["binary"])
    assert sha(binary) == build["binary_sha256"]
    for name, expected in build["sources_sha256"].items():
        assert sha(ROOT / name) == expected, f"source changed since build: {name}"

    def run(name, argv, mode="summary"):
        path = results / (name + ".json")
        marker = results / (name + ".done")
        recipe = {"argv": argv + [mode], "binary_sha256": build["binary_sha256"], "build_manifest_sha256": sha(build_file), "driver_sha256": sha(Path(__file__))}
        if marker.exists():
            old = json.loads(path.read_text())
            assert old["recipe"] == recipe and marker.read_text().strip() == sha(path)
            if mode == "counts":
                assert old["counts_sha256"] == sha(EXP / old["counts_file"])
            return old
        if path.exists():
            raise RuntimeError(f"unmarked result exists: {path}; inspect before reuse")
        t = time.monotonic()
        command = [str(binary), *map(str, argv), mode]
        if mode == "summary":
            completed = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=True)
            record = {"recipe": recipe, "summary": json.loads(completed.stdout)}
        else:
            # Bulk counts go in ignored dumps; a small support audit is committed separately.
            count_dir = EXP / "dumps" / "pilot_v1"
            count_dir.mkdir(parents=True, exist_ok=True)
            raw = count_dir / (name + ".csv")
            with raw.open("w") as out:
                completed = subprocess.run(command, cwd=ROOT, stdout=out, stderr=subprocess.PIPE, text=True, check=True)
            compressed = raw.with_suffix(".csv.gz")
            with compressed.open("wb") as out, gzip.GzipFile(filename="", mode="wb", fileobj=out, mtime=0) as zipped:
                zipped.write(raw.read_bytes())
            raw.unlink()
            record = {"recipe": recipe, "summary": json.loads(completed.stderr),
                "counts_file": str(compressed.relative_to(EXP)), "counts_sha256": sha(compressed)}
        record["seconds"] = time.monotonic() - t
        path.write_text(json.dumps(record, indent=2) + "\n")
        marker.write_text(sha(path) + "\n")
        print(name, "births", record["summary"]["births"], "seconds", round(record["seconds"], 3), flush=True)
        return record

    if args.stage == "controls":
        # No timing claim; the single-run driver has no parallel reduction.
        argv = ["band", "RRRLRLLRLRLLRL", "2026102021", "12", "32", "64", "32", "counts"]
        a = subprocess.check_output([str(binary), *argv], env={**os.environ, "RAYON_NUM_THREADS": "1"}, stderr=subprocess.DEVNULL)
        b = subprocess.check_output([str(binary), *argv], env={**os.environ, "RAYON_NUM_THREADS": "6"}, stderr=subprocess.DEVNULL)
        assert a == b
        (results / "thread_check.json").write_text(json.dumps({"argv": argv, "sha256_1_and_6": hashlib.sha256(a).hexdigest(), "identical": True}, indent=2) + "\n")
        for seed in range(2026102051, 2026102059):
            run(f"rotor-{seed}", ["blank", f"rotor:{seed}", "24", "4096"])
            run(f"rw-{seed}", ["blank", f"rw:{seed}", "20", "4096"])
        return

    with (EXP / "results/design/families.csv").open() as f:
        rows = [r for r in csv.DictReader(f) if r["split"] == "pilot"]
    choice = None
    for log2 in range(22, 27):
        good = {}
        for row in rows:
            good.setdefault(row["family"], True)
            for seed in row["interior_seeds"].split(";"):
                name = f"{row['family']}-{row['arm']}-{seed}-k{log2}"
                record = run(name, ["band", row["rule"], seed, str(log2), "256", "4096", "2048"])
                s = record["summary"]
                consumed = (s["area"] - 256 * 2048) / (256 * 2048)
                good[row["family"]] &= 0.1 <= consumed <= 0.8 and s["births"] >= 5000 and not s["escaped"]
        if sum(good.values()) >= 3:
            choice = log2
            break
    verdict = {"selected_log2": choice, "gate": "at least 3/4 complete pilot families, all arms/seeds 10-80% band consumed and >=5000 window births",
        "status": "horizon_selected" if choice is not None else "STOP_register_geometry_or_budget_revision",
        "design_sha256": sha(EXP / "results/design/families.csv"), "build_sha256": sha(build_file)}
    (results / "horizon.json").write_text(json.dumps(verdict, indent=2) + "\n")
    print(json.dumps(verdict), flush=True)
    if choice is not None:
        for row in rows:
            for seed in row["interior_seeds"].split(";"):
                name = f"{row['family']}-{row['arm']}-{seed}-k{choice}-counts"
                run(name, ["band", row["rule"], seed, str(choice), "256", "4096", "2048"], "counts")


if __name__ == "__main__":
    main()
