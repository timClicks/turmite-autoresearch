"""Fresh release build, controls, fixed pilot and byte-level thread replication."""
import hashlib
import json
import os
import platform
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parents[1]
RESULTS = HERE / "results"
SCRATCH = HERE / "scratch"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(command, log, env):
    with log.open("w") as stream:
        subprocess.run(command, cwd=ROOT, env=env, stdout=stream, stderr=subprocess.STDOUT, check=True)


def main():
    RESULTS.mkdir(exist_ok=True)
    SCRATCH.mkdir(exist_ok=True)
    revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    inputs = [ROOT / "examples/hidden_phase_return.rs", ROOT / "Cargo.lock", Path(__file__).resolve(), HERE / "scripts/analyze.py"]
    source_hashes = {str(p.relative_to(ROOT)): sha(p) for p in inputs}
    marker = RESULTS / "run.done.json"
    if marker.exists():
        saved = json.loads(marker.read_text())
        assert saved["source_hashes"] == source_hashes, "sources changed: use a separate experiment; do not overwrite results"
        for name, digest in saved["output_hashes"].items():
            assert sha(RESULTS / name) == digest
        print("Existing run verified; no measurements overwritten.")
        return
    assert not list(RESULTS.glob("*.csv")), "partial data exists; inspect it before a rerun"
    build = SCRATCH / f"build-{time.time_ns()}"
    env = dict(os.environ, CARGO_TARGET_DIR=str(build), PROPTEST_RNG_SEED="20261019")
    tests = ["cargo", "test", "--release", "--locked", "--example", "hidden_phase_return"]
    compile_cmd = ["cargo", "build", "--release", "--locked", "--example", "hidden_phase_return"]
    run(tests, RESULTS / "controls.log", env)
    run(compile_cmd, RESULTS / "build.log", env)
    binary = build / "release/examples/hidden_phase_return"
    command = [str(binary), str(RESULTS), "3"]
    start = time.monotonic()
    run(command, RESULTS / "pilot.log", env)
    elapsed = time.monotonic() - start
    # Full pilot replication, not a small surrogate: each CSV must be identical.
    repeat = SCRATCH / "one-thread"
    run([str(binary), str(repeat), "1"], RESULTS / "determinism.log", env)
    files = sorted(RESULTS.glob("*.csv"))
    assert len(files) == 24
    for path in files:
        assert path.read_bytes() == (repeat / path.name).read_bytes(), path.name
    provenance = dict(revision=revision, source_hashes=source_hashes,
        rustc=subprocess.check_output(["rustc", "--version"], text=True).strip(),
        platform=platform.platform(), architecture=platform.machine(),
        binary_sha256=sha(binary), command=command, controls=tests, build=compile_cmd,
        elapsed_seconds=elapsed, thread_replication="all 24 CSV files identical at 1 and 3 threads",
        output_hashes={p.name: sha(p) for p in files})
    marker.write_text(json.dumps(provenance, indent=2) + "\n")
    print(f"Pilot and full thread replication finished: {len(files)} CSV files.")


if __name__ == "__main__":
    main()
