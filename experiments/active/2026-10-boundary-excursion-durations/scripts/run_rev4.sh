#!/usr/bin/env bash
# Revision 4 calibration (depth–duration readout). Registered 2026-10-29 17:58 NZDT (e066256).
# Usage: from repo root, after
#   cargo build --release --locked --example boundary_excursions --example boundary_excursions_depth_synth
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../../../.." && pwd)"
EXP="$ROOT/experiments/active/2026-10-boundary-excursion-durations"
RES="$EXP/results"
BIN="${BIN:-$ROOT/target/release/examples/boundary_excursions}"
SYN="${SYN:-$ROOT/target/release/examples/boundary_excursions_depth_synth}"
MAX_LOG2="${MAX_LOG2:-24}"
GRID="${GRID:-8192}"
export RAYON_NUM_THREADS="${RAYON_NUM_THREADS:-4}"
export UV_PROJECT_ENVIRONMENT="${UV_PROJECT_ENVIRONMENT:-$HOME/.venvs/turmite}" UV_LINK_MODE=copy

echo "bin=$BIN sha256=$(sha256sum "$BIN" | awk '{print $1}')"
echo "synth=$SYN sha256=$(sha256sum "$SYN" | awk '{print $1}')"
echo "max_log2=$MAX_LOG2 grid=$GRID threads=$RAYON_NUM_THREADS"
echo "git=$(git -C "$ROOT" rev-parse HEAD)"

# G1 synthetic gate first (stop if it fails).
mkdir -p "$EXP/scratch"
"$SYN" 2026102981 20 > "$EXP/scratch/rev4_synth_dhist.csv"
echo "synth csv sha256=$(sha256sum "$EXP/scratch/rev4_synth_dhist.csv" | awk '{print $1}')"
uv run --frozen python "$EXP/scripts/synth_rev4.py" "$EXP/scratch/rev4_synth_dhist.csv"
grep -q '^G1: PASS' "$RES/rev4_synth.txt" || { echo "G1 failed: stop before walkers" >&2; exit 2; }

start=$(date +%s)
"$BIN" "$MAX_LOG2" "$GRID" --check --hist "$RES/rev4_calib_hist.csv" --fhist "$RES/rev4_calib_fhist.csv" \
  --dhist "$RES/rev4_calib_dhist.csv" \
  < "$RES/rev4_calib_specs.txt" > "$RES/rev4_calib_windows.csv" 2>"$RES/rev4_calib_run.log"
echo "rev4 calib wall seconds: $(( $(date +%s) - start ))"
echo "windows: $(wc -l < "$RES/rev4_calib_windows.csv") dhist rows: $(wc -l < "$RES/rev4_calib_dhist.csv")"
uv run --frozen python "$EXP/scripts/analyse_rev4.py"
