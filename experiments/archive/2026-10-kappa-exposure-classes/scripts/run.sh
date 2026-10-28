#!/usr/bin/env bash
# Main run for 2026-10-kappa-exposure-classes. Resumable: skips if results/classes.done exists.
# Builds into a fresh target dir (stale-build trap, AGENTS.md), logs the binary sha256, and runs
# every spec in --check mode (each window compared with probe::probe_walker and a board scan).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../../../.." && pwd)"
EXP="$ROOT/experiments/archive/2026-10-kappa-exposure-classes"
RES="$EXP/results"
MAX_LOG2=${MAX_LOG2:-26}
GRID=${GRID:-8192}
[ -f "$RES/classes.done" ] && { echo "classes.done exists; nothing to do"; exit 0; }
export CARGO_TARGET_DIR="${CARGO_TARGET_DIR:-$HOME/turmite-target-exposure}"
cd "$ROOT"
cargo build --release --example kappa_exposure_classes
BIN="$CARGO_TARGET_DIR/release/examples/kappa_exposure_classes"
{
  echo "date_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "git=$(git rev-parse HEAD) dirty=$(git status --porcelain -- src examples Cargo.toml Cargo.lock | wc -l)"
  echo "binary_sha256=$(sha256sum "$BIN" | cut -d' ' -f1)"
  echo "specs_sha256=$(sha256sum "$RES/specs.txt" | cut -d' ' -f1)"
  echo "rustc=$(rustc --version)"
  echo "command=$BIN $MAX_LOG2 $GRID --check < results/specs.txt > results/classes.csv"
  echo "threads=${RAYON_NUM_THREADS:-default} nproc=$(nproc)"
} > "$RES/run.log"
start=$(date +%s)
"$BIN" "$MAX_LOG2" "$GRID" --check < "$RES/specs.txt" > "$RES/classes.csv.tmp" 2>> "$RES/run.log"
mv "$RES/classes.csv.tmp" "$RES/classes.csv"
echo "elapsed_s=$(( $(date +%s) - start ))" >> "$RES/run.log"
echo "classes_sha256=$(sha256sum "$RES/classes.csv" | cut -d' ' -f1)" >> "$RES/run.log"
touch "$RES/classes.done"
