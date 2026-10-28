#!/usr/bin/env bash
# Excluded development pilot. Do NOT run reserved_confirmation_specs.txt.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../../../.." && pwd)"
EXP="$ROOT/experiments/active/2026-10-boundary-excursion-durations"
RES="$EXP/results"
BIN="${BIN:-$ROOT/target/release/examples/boundary_excursions}"
MAX_LOG2="${MAX_LOG2:-24}"
GRID="${GRID:-8192}"
export RAYON_NUM_THREADS="${RAYON_NUM_THREADS:-4}"
export PATH="${HOME}/.cargo/bin:${PATH}"

echo "bin=$BIN sha256=$(sha256sum "$BIN" | awk '{print $1}')"
echo "git=$(git -C "$ROOT" rev-parse HEAD)"
"$BIN" "$MAX_LOG2" "$GRID" --check --hist "$RES/pilot_hist.csv" \
  < "$RES/pilot_specs.txt" > "$RES/pilot_windows.csv" 2>"$RES/pilot_run.log"
echo "pilot windows: $(wc -l < "$RES/pilot_windows.csv")"
echo "pilot hist rows: $(wc -l < "$RES/pilot_hist.csv")"
