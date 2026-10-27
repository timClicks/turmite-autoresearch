#!/usr/bin/env bash
# Calibration: mf / rotor / rw seeds from results/calib_specs.txt.
# Usage: from repo root, after `cargo build --example boundary_excursions --release --locked`.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
EXP="$ROOT/experiments/2026-10-27-boundary-excursion-durations"
RES="$EXP/results"
BIN="${BIN:-$ROOT/target/release/examples/boundary_excursions}"
MAX_LOG2="${MAX_LOG2:-24}"
GRID="${GRID:-8192}"
export RAYON_NUM_THREADS="${RAYON_NUM_THREADS:-4}"
export PATH="${HOME}/.cargo/bin:${PATH}"

mkdir -p "$RES"
echo "bin=$BIN sha256=$(sha256sum "$BIN" | awk '{print $1}')"
echo "max_log2=$MAX_LOG2 grid=$GRID threads=$RAYON_NUM_THREADS"
echo "git=$(git -C "$ROOT" rev-parse HEAD)"

# C0 on a tiny non-cohort smoke before the long run
printf 'rw:7\nrotor:7\n' | "$BIN" 12 256 --check --hist "$RES/c0_smoke_hist.csv" > "$RES/c0_smoke_windows.csv"
echo "C0 smoke (check) OK"
set +e
printf 'rw:7\n' | "$BIN" 12 256 --check --mutant > /dev/null 2>"$RES/c0_mutant.stderr"
ec=$?
set -e
if [[ $ec -eq 0 ]]; then
  echo "C0 mutant FAILED to panic" >&2
  exit 1
fi
echo "C0 mutant panicked as required (exit $ec)"

"$BIN" "$MAX_LOG2" "$GRID" --check --hist "$RES/calib_hist.csv" \
  < "$RES/calib_specs.txt" > "$RES/calib_windows.csv" 2>"$RES/calib_run.log"
echo "calibration windows: $(wc -l < "$RES/calib_windows.csv")"
echo "calibration hist rows: $(wc -l < "$RES/calib_hist.csv")"
