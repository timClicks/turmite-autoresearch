"""Small byte-for-byte CLI checks; writes only to the explicit scratch directory."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


# sweep_lean is documented as byte-identical to sweep, and its tiled backend as byte-identical to dense, whatever
# the tile geometry. The stress settings use tiles small and caches tight enough that the 256-cell batch evicts
# constantly (a 2^6 tile on this grid would never evict, so agreement would be vacuous); the stats JSON proves it.
TILED_CONFIGS = {
    "tiled-default": {"TURMITE_GRID": "tiled"},
    "tiled-t2c2-packed": {"TURMITE_GRID": "tiled", "TURMITE_TILE_LOG2": "2", "TURMITE_CACHE_TILES": "2", "TURMITE_INACTIVE": "packed"},
    "tiled-t3c4-raw": {"TURMITE_GRID": "tiled", "TURMITE_TILE_LOG2": "3", "TURMITE_CACHE_TILES": "4", "TURMITE_INACTIVE": "raw"},
    "tiled-t3c4-lz4": {"TURMITE_GRID": "tiled", "TURMITE_TILE_LOG2": "3", "TURMITE_CACHE_TILES": "4", "TURMITE_INACTIVE": "lz4"},
}
# Counter that must be positive in the stats JSON for the stress configurations to have exercised their code path.
MUST_EXERCISE = {"tiled-t2c2-packed": "packed_stores", "tiled-t3c4-raw": "raw_stores", "tiled-t3c4-lz4": "compressed_stores"}


def csv_problems(name, data):
    """Reasons a sweep CSV cannot support a meaningful equality check (empty, or no highway/budget rows)."""
    rows = [line.split(",") for line in data.decode().splitlines()[1:]]
    out = []
    if len(rows) < 2:
        out.append(f"{name}: no data rows")
    if not any(r[2] == "budget" for r in rows):
        out.append(f"{name}: no budget-stopped rows")
    if not any(r[4] and r[7] for r in rows):
        out.append(f"{name}: no row with a highway period and onset")
    return out


def compare_lean(root, target, out, recipe, sweep_bytes):
    """sweep_lean vs sweep (oracle path), across thread counts and storage backends. Returns failure strings."""
    failed = []
    binary = target / "release" / "sweep_lean"
    args = ["2", "6", "32768", "256"]

    def run(label, threads, extra_env):
        stats = out / f"lean-{label}-{threads}.stats.json"
        env = {**os.environ, "RAYON_NUM_THREADS": str(threads), **extra_env}
        if extra_env.get("TURMITE_GRID") == "tiled":
            env["TURMITE_GRID_STATS"] = str(stats)
        result = subprocess.run([str(binary), *args], text=True, capture_output=True, cwd=root, env=env, check=True)
        path = out / f"lean-{label}-{threads}.csv"
        path.write_bytes(result.stdout.encode())
        recipe["runs"].append({"command": [str(binary), *args], "env": {**extra_env, "RAYON_NUM_THREADS": str(threads)},
                               "binary_sha256": sha256(binary), "output": path.name, "output_sha256": sha256(path)})
        return path.read_bytes(), stats

    dense = {}
    for threads in (1, 3):
        dense[threads], _ = run("dense", threads, {})
    failed += csv_problems("sweep_lean dense", dense[1])
    if dense[1] != dense[3]:
        failed.append("sweep_lean dense: output differs between 1 and 3 threads")
    if dense[1] != sweep_bytes:
        failed.append("sweep_lean dense: output differs from sweep")
    for label, env in TILED_CONFIGS.items():
        for threads in (1, 3):
            data, stats = run(label, threads, env)
            if data != dense[1]:
                failed.append(f"sweep_lean {label}: output differs from dense at {threads} thread(s)")
        counter = MUST_EXERCISE.get(label)
        per_rule = json.loads(stats.read_text())["per_rule"]
        if counter and (sum(r["evictions"] for r in per_rule) == 0 or sum(r[counter] for r in per_rule) == 0):
            failed.append(f"sweep_lean {label}: stress configuration did not exercise {counter}; agreement would be vacuous")
    return failed


def self_test(sweep_bytes):
    """Planted faults: the vacuity guards must flag degenerate CSVs, otherwise a pass means nothing."""
    assert not csv_problems("control", sweep_bytes), "control batch should be non-vacuous"
    assert csv_problems("control", b"rule,n,stop,steps,period,dx,dy,onset,width,height,tail_period\n"), "empty CSV not flagged"
    assert csv_problems("control", b"\n".join(l for l in sweep_bytes.split(b"\n") if b",budget," not in l)), "no-budget CSV not flagged"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=True)
    target = Path(os.environ.get("CARGO_TARGET_DIR", root / "target"))
    if not target.is_absolute():
        target = root / target
    cases = [
        ("sweep", ["2", "6", "32768", "256"], None),
        ("probe", ["14", "256"], "RL\nRLR\nLLRR\nRLR@1\nRLR@2\nrotor:1\nrotor:2\nrw:1\nrw:2\n"),
    ]
    recipe = {
        "commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip(),
        "build": "cargo build --release --locked --bin sweep --bin probe",
        "rustc": subprocess.check_output(["rustc", "--version"], text=True).strip(),
        "cargo_lock_sha256": sha256(root / "Cargo.lock"),
        "script_sha256": sha256(Path(__file__)),
        "runs": [],
    }
    failed = []
    for name, flags, stdin in cases:
        binary = target / "release" / name
        outputs = []
        for threads in (1, 3):
            command = [str(binary), *flags]
            result = subprocess.run(command, input=stdin, text=True, capture_output=True,
                                    cwd=root, env={**os.environ, "RAYON_NUM_THREADS": str(threads)}, check=True)
            path = out / f"{name}-{threads}.csv"
            path.write_bytes(result.stdout.encode())
            (out / f"{name}-{threads}.log").write_text(result.stderr)
            # Prevent vacuous agreement if the CLI emits only a header.
            if len(result.stdout.splitlines()) < 2:
                failed.append(f"{name}: no data rows")
            outputs.append(path.read_bytes())
            recipe["runs"].append({"command": command, "stdin": stdin,
                                   "RAYON_NUM_THREADS": threads, "binary_sha256": sha256(binary),
                                   "output": path.name, "output_sha256": sha256(path)})
        if outputs[0] != outputs[1]:
            failed.append(f"{name}: output differs between 1 and 3 threads")
    sweep_bytes = (out / "sweep-1.csv").read_bytes()
    self_test(sweep_bytes)
    failed += compare_lean(root, target, out, recipe, sweep_bytes)
    recipe["failures"] = failed
    (out / "recipe.json").write_text(json.dumps(recipe, indent=2) + "\n")
    if failed:
        raise SystemExit("; ".join(failed))
    print("PASS: sweep and seeded probe CSVs match at 1 and 3 Rayon threads; sweep_lean (dense, tiled) matches sweep")


if __name__ == "__main__":
    main()
