#!/bin/sh
# usage (repo root): sh experiments/2026-10-26-wall-vs-memory/scripts/run_stage2.sh
# Builds probe into a fresh target dir (stale-build trap, AGENTS.md), records provenance,
# runs every spec in results/stage2_specs.txt once. Skips the run if results/stage2.done exists.
set -eu
D=experiments/2026-10-26-wall-vs-memory/results
if [ -e "$D/stage2.done" ]; then echo "already done: $D/stage2.done"; exit 0; fi
T=$(mktemp -d)
CARGO_TARGET_DIR="$T" cargo build --release --locked --bin probe
{
  echo "commit $(git rev-parse HEAD)"
  echo "dirty $(git status --porcelain --untracked-files=no | wc -l) tracked files"
  echo "rustc $(rustc --version)"
  echo "probe_sha256 $(sha256sum "$T/release/probe" | cut -d' ' -f1)"
  echo "specs_sha256 $(sha256sum "$D/stage2_specs.txt" | cut -d' ' -f1)"
  echo "command probe 31 16384 < $D/stage2_specs.txt"
  echo "RAYON_NUM_THREADS ${RAYON_NUM_THREADS:-unset}"
  echo "start $(date -u +%Y-%m-%dT%H:%M:%SZ)"
} > "$D/stage2_provenance.txt"
"$T/release/probe" 27 16384 < "$D/stage2_specs.txt" > "$D/stage2_probe.csv" 2> "$D/stage2_probe.log"
echo "end $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$D/stage2_provenance.txt"
echo "stage2_probe.csv_sha256 $(sha256sum "$D/stage2_probe.csv" | cut -d' ' -f1)" >> "$D/stage2_provenance.txt"
touch "$D/stage2.done"
rm -rf "$T"
