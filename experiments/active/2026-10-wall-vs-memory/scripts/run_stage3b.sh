#!/bin/sh
# usage (repo root): sh experiments/active/2026-10-wall-vs-memory/scripts/run_stage3b.sh [OUTDIR]
# OUTDIR (default: the committed results/) is where the CSV, log, provenance and .done marker go.
# The committed results/ already carries stage3b.done, so the default call skips; to actually re-simulate
# pass a fresh directory (e.g. scratch/rerun) and compare with scripts/verify.py.
# Builds probe into a fresh target dir (stale-build trap, AGENTS.md), records provenance,
# runs every spec in results/stage3b_specs.txt once. Skips only if OUTDIR/stage3b.done exists.
set -eu
S=experiments/active/2026-10-wall-vs-memory/results   # specs are always the committed ones
D=${1:-$S}
mkdir -p "$D"
if [ -e "$D/stage3b.done" ]; then echo "already done: $D/stage3b.done (pass a fresh OUTDIR to re-simulate)"; exit 0; fi
T=$(mktemp -d)
CARGO_TARGET_DIR="$T" cargo build --release --locked --bin probe
{
  echo "commit $(git rev-parse HEAD)"
  echo "dirty $(git status --porcelain --untracked-files=no | wc -l) tracked files"
  echo "rustc $(rustc --version)"
  echo "probe_sha256 $(sha256sum "$T/release/probe" | cut -d' ' -f1)"
  echo "specs_sha256 $(sha256sum "$S/stage3b_specs.txt" | cut -d' ' -f1)"
  echo "command probe 27 16384 < $S/stage3b_specs.txt"
  echo "RAYON_NUM_THREADS ${RAYON_NUM_THREADS:-unset}"
  echo "start $(date -u +%Y-%m-%dT%H:%M:%SZ)"
} > "$D/stage3b_provenance.txt"
"$T/release/probe" 27 16384 < "$S/stage3b_specs.txt" > "$D/stage3b_probe.csv" 2> "$D/stage3b_probe.log"
echo "end $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$D/stage3b_provenance.txt"
echo "stage3b_probe.csv_sha256 $(sha256sum "$D/stage3b_probe.csv" | cut -d' ' -f1)" >> "$D/stage3b_provenance.txt"
touch "$D/stage3b.done"
rm -rf "$T"
