#!/bin/sh
# usage (repo root): sh experiments/2026-10-26-wall-vs-memory/scripts/run.sh
# Builds probe into a fresh target dir (stale-build trap, AGENTS.md), records provenance,
# runs every spec in results/specs.txt once. Skips the run if results/run.done exists.
set -eu
D=experiments/2026-10-26-wall-vs-memory/results
if [ -e "$D/run.done" ]; then echo "already done: $D/run.done"; exit 0; fi
T=$(mktemp -d)
CARGO_TARGET_DIR="$T" cargo build --release --locked --bin probe
{
  echo "commit $(git rev-parse HEAD)"
  echo "dirty $(git status --porcelain --untracked-files=no | wc -l) tracked files"
  echo "rustc $(rustc --version)"
  echo "probe_sha256 $(sha256sum "$T/release/probe" | cut -d' ' -f1)"
  echo "specs_sha256 $(sha256sum "$D/specs.txt" | cut -d' ' -f1)"
  echo "command probe 27 16384 < $D/specs.txt"
  echo "RAYON_NUM_THREADS ${RAYON_NUM_THREADS:-unset}"
  echo "start $(date -u +%Y-%m-%dT%H:%M:%SZ)"
} > "$D/provenance.txt"
"$T/release/probe" 27 16384 < "$D/specs.txt" > "$D/probe.csv" 2> "$D/probe.log"
echo "end $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$D/provenance.txt"
echo "probe_csv_sha256 $(sha256sum "$D/probe.csv" | cut -d' ' -f1)" >> "$D/provenance.txt"
touch "$D/run.done"
rm -rf "$T"
