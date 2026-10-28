#!/usr/bin/env bash
# Revision 2 calibration (eden / idla / idlar / mf / rotor). Registered 2026-10-28 15:50 NZDT.
# Usage: from repo root, after `cargo build --example boundary_excursions --release --locked`.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
RES="$ROOT/experiments/2026-10-27-boundary-excursion-durations/results"
BIN="${BIN:-$ROOT/target/release/examples/boundary_excursions}"
MAX_LOG2="${MAX_LOG2:-24}"
GRID="${GRID:-8192}"
export RAYON_NUM_THREADS="${RAYON_NUM_THREADS:-4}"

echo "bin=$BIN sha256=$(sha256sum "$BIN" | awk '{print $1}')"
echo "max_log2=$MAX_LOG2 grid=$GRID threads=$RAYON_NUM_THREADS"
echo "git=$(git -C "$ROOT" rev-parse HEAD)"

# C0 smoke on tiny non-cohort seeds
printf 'rw:7\nrotor:7\ncup:1.0:7\neden:7\nidla:7\nidlar:7\nmf:7\n' \
  | "$BIN" 14 512 --check --hist /dev/null > /dev/null
echo "C0 smoke (--check: probe match rw/rotor, cup:1≡rw, scan recount, birth invariants, idla≡idlar geometry) OK"
set +e
printf 'rw:7\n' | "$BIN" 12 256 --check --mutant > /dev/null 2>/dev/null
ec=$?
set -e
if [[ $ec -eq 0 ]]; then echo "C0 mutant FAILED to panic" >&2; exit 1; fi
echo "C0 mutant panicked as required (exit $ec)"

start=$(date +%s)
"$BIN" "$MAX_LOG2" "$GRID" --check --hist "$RES/rev2_calib_hist.csv" \
  < "$RES/rev2_calib_specs.txt" > "$RES/rev2_calib_windows.csv" 2>"$RES/rev2_calib_run.log"
echo "rev2 calib wall seconds: $(( $(date +%s) - start ))"
echo "windows: $(wc -l < "$RES/rev2_calib_windows.csv") hist rows: $(wc -l < "$RES/rev2_calib_hist.csv")"
