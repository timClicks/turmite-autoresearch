#!/bin/sh
# usage (repo root): sh experiments/active/2026-10-wall-vs-memory/scripts/run.sh [OUTDIR]
# OUTDIR (default: the committed results/) is where the CSV, log, provenance and .done marker go.
# The committed results/ already carries run.done, so the default call skips; to actually re-simulate
# pass a fresh directory (e.g. scratch/rerun) and compare with scripts/verify.py.
# Builds probe into a fresh target dir (stale-build trap, AGENTS.md), records provenance,
# runs every spec in results/specs.txt once. Skips only if OUTDIR/run.done exists.
set -eu
S=experiments/active/2026-10-wall-vs-memory/results   # specs are always the committed ones
D=${1:-$S}
mkdir -p "$D"
if [ -e "$D/run.done" ]; then echo "already done: $D/run.done (pass a fresh OUTDIR to re-simulate)"; exit 0; fi
T=$(mktemp -d)
CARGO_TARGET_DIR="$T" cargo build --release --locked --bin probe
{
  echo "commit $(git rev-parse HEAD)"
  echo "dirty $(git status --porcelain --untracked-files=no | wc -l) tracked files"
  echo "rustc $(rustc --version)"
  echo "probe_sha256 $(sha256sum "$T/release/probe" | cut -d' ' -f1)"
  echo "specs_sha256 $(sha256sum "$S/specs.txt" | cut -d' ' -f1)"
  echo "command probe 27 16384 < $S/specs.txt"
  echo "RAYON_NUM_THREADS ${RAYON_NUM_THREADS:-unset}"
  echo "start $(date -u +%Y-%m-%dT%H:%M:%SZ)"
} > "$D/provenance.txt"
"$T/release/probe" 27 16384 < "$S/specs.txt" > "$D/probe.csv" 2> "$D/probe.log"
echo "end $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$D/provenance.txt"
echo "probe_csv_sha256 $(sha256sum "$D/probe.csv" | cut -d' ' -f1)" >> "$D/provenance.txt"
touch "$D/run.done"
rm -rf "$T"
