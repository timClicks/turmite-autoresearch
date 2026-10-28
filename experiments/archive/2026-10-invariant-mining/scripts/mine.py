"""Build exact-law miner and save reproducible, non-overwriting analysis inputs."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import os

ROOT = Path(__file__).resolve().parents[4]
EXPERIMENT = Path(__file__).resolve().parents[1]


def run(args, **kwargs):
    return subprocess.check_output(args, cwd=ROOT, **kwargs)


def main():
    rules = sys.argv[1:]
    if not rules or any(not 2 <= len(r) <= 255 or set(r) - set("LR") for r in rules):
        raise SystemExit("usage: mine.py RULE [RULE ...]; uppercase L/R, lengths 2..255")
    results = EXPERIMENT / "results"
    if results.exists():
        raise SystemExit("results already exists; preserve it and choose a new investigation for another run")
    scratch = EXPERIMENT / "scratch"
    scratch.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(dir=scratch) as target:
        env = dict(os.environ, CARGO_TARGET_DIR=str(Path(target).resolve()))
        subprocess.run(["cargo", "build", "--release", "--locked", "--bin", "invariants"], cwd=ROOT, env=env, check=True)
        binary = Path(target) / "release" / ("invariants.exe" if os.name == "nt" else "invariants")
        data = run([str(binary.resolve()), *rules])
        sources = ["src/invariants.rs", "src/bin/invariants.rs", "src/rule.rs", "src/lib.rs", "Cargo.lock", "Cargo.toml", str(Path(__file__).resolve().relative_to(ROOT))]
        metadata = {
            "commit": run(["git", "rev-parse", "HEAD"], text=True).strip(),
            "command": ["uv", "run", "--frozen", str(Path(__file__).resolve().relative_to(ROOT)), *rules],
            "rules": rules, "moduli": [2, 4], "seed": None,
            # Colour relabelling c -> c+k commutes with increment. A spatial
            # reflection also swaps L/R. Initial fields must be relabelled too.
            "colour_shift_symmetries": {r: {
                "preserving": [k for k in range(len(r)) if all(r[(c+k) % len(r)] == r[c] for c in range(len(r)))],
                "with_reflection": [k for k in range(len(r)) if all(r[(c+k) % len(r)] != r[c] for c in range(len(r)))],
            } for r in rules},
            "binary_sha256": hashlib.sha256(binary.read_bytes()).hexdigest(),
            "source_sha256": {s: hashlib.sha256((ROOT / s).read_bytes()).hexdigest() for s in sources},
            "output_sha256": hashlib.sha256(data).hexdigest(),
            "rustc": run(["rustc", "--version"], text=True).strip(),
        }
    results.mkdir()
    (results / "invariants.csv").write_bytes(data)
    (results / "provenance.json").write_text(json.dumps(metadata, indent=2) + "\n")


if __name__ == "__main__":
    main()
