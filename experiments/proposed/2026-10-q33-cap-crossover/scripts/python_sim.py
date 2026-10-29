# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Short-run CLI: uv run --script python_sim.py --help (no Rust/dependencies)."""
from __future__ import annotations

import argparse
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import platform
import sys
import time

ROOT = Path(__file__).resolve().parents[4]
EXPERIMENT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "experiments" / "_lib"))
from turmite_sim import CellLimit, Config, SparseWalker, VERSION, octave_fits, sample_steps


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rule", default=None)
    parser.add_argument("--policy", choices=["ant", "fresh-set", "persistent-fresh"])
    parser.add_argument("--fresh-set", default=None)
    parser.add_argument("--cap", type=int)
    parser.add_argument("--seed", type=int)
    parser.add_argument("--steps", type=int, default=65536, help="total absolute target, including resumed steps")
    parser.add_argument("--max-cells", type=int, default=1000000, help="stop before exceeding this departed-cell count")
    parser.add_argument("--suboctaves", action="store_true")
    parser.add_argument("--hull", action="store_true", help="exact cell-centre hull at samples (costs extra)")
    parser.add_argument("--resume", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True,
                        help="new directory within this experiment; existing directories are never overwritten")
    args = parser.parse_args(argv)
    if args.steps < 0 or args.max_cells < 1:
        parser.error("steps must be nonnegative and max-cells positive")
    destination = args.output_dir.resolve()
    if not destination.is_relative_to(EXPERIMENT):
        parser.error("output-dir must be inside " + str(EXPERIMENT))
    try:
        if args.resume:
            if any(v is not None for v in (args.rule, args.policy, args.cap, args.seed, args.fresh_set)):
                parser.error("resume restores config; do not also supply rule/policy/cap/seed/fresh-set")
            raw_checkpoint = args.resume.read_bytes()
            walker = SparseWalker.from_checkpoint(json.loads(raw_checkpoint))
        else:
            raw_checkpoint = None
            walker = SparseWalker(Config(rule=args.rule or "RLL", policy=args.policy or "ant",
                                         seed=args.seed if args.seed is not None else 0,
                                         cap=args.cap, fresh_set=args.fresh_set or "RLU"))
        if args.steps < walker.steps:
            parser.error("target precedes checkpoint clock")
        if len(walker.cells) > args.max_cells:
            parser.error("checkpoint already exceeds max-cells")
        destination.mkdir(parents=True, exist_ok=False)
    except (ValueError, OSError, KeyError, TypeError) as exc:
        parser.error(str(exc))
    initial = walker.steps
    samples = [walker.snapshot(hull=args.hull)]
    schedule = set(sample_steps(args.steps, initial, suboctaves=args.suboctaves))
    status = "complete"
    began = time.perf_counter()
    while walker.steps < args.steps:
        try:
            walker.step(args.max_cells)
        except CellLimit:
            status = "resource_incomplete"
            break
        if walker.steps in schedule:
            samples.append(walker.snapshot(hull=args.hull))
    if samples[-1]["steps"] != walker.steps:
        samples.append(walker.snapshot(hull=args.hull))
    elapsed = time.perf_counter() - began

    def write(name, data):
        (destination / name).write_text(json.dumps(data, indent=2, sort_keys=True, allow_nan=False) + "\n")

    write("samples.json", samples)
    write("octaves.json", octave_fits(samples, suboctaves=args.suboctaves))
    write("fresh_runs.json", walker.fresh_summary())
    write("checkpoint.json", walker.checkpoint())
    source_files = [Path(__file__).resolve(), ROOT / "experiments/_lib/turmite_sim.py"]
    metadata = {
        "format": VERSION, "purpose": "technical short run; not Q33 confirmation or excluded pilot",
        "status": status, "config": asdict(walker.config),
        "initial_step": initial, "target_step": args.steps, "final_step": walker.steps,
        "max_cells": args.max_cells, "suboctaves": args.suboctaves, "hull": args.hull,
        "command_argv": sys.argv, "python": platform.python_version(), "platform": platform.platform(),
        "source_sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in source_files},
        "resume_sha256": hashlib.sha256(raw_checkpoint).hexdigest() if raw_checkpoint is not None else None,
        "output_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(destination.glob("*.json"))},
        "elapsed_seconds": elapsed,
        "limits": ["no crystallisation detector", "no time-weighted excursion instrument",
                   "no pre-entry depth instrument", "no Rust cross-execution check yet"],
    }
    write("provenance.json", metadata)
    print(json.dumps({"status": status, "steps": walker.steps, "output_dir": str(destination)}))
    return 0 if status == "complete" else 2


if __name__ == "__main__":
    raise SystemExit(main())
