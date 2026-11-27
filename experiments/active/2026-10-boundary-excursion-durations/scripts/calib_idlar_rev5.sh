#!/usr/bin/env bash
# Rev5 review (2026-11-27) S1 follow-up, POST HOC: relabel the committed Rev4 walker calibration data with `idlar` (IDLA with
# restart-launched excursions dropped) in the RLLLLRLL slot instead of `idla` (eden->RLLR, bal->RLLRL, rotor->RLLLRR,
# idlar->RLLLLRLL), into scratch/rev5_selftest_idlar/, then run diag_rev5.py on it -> results/rev5_diag_calibrators_idlar.txt.
# No ant data are read; no reading changes. The eden/bal/rotor sections duplicate results/rev5_diag_calibrators.txt.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../../../.." && pwd)"
EXP="$ROOT/experiments/active/2026-10-boundary-excursion-durations"
RES="$EXP/results"
T="$EXP/scratch/rev5_selftest_idlar"
export UV_PROJECT_ENVIRONMENT="${UV_PROJECT_ENVIRONMENT:-$HOME/.venvs/turmite}" UV_LINK_MODE="${UV_LINK_MODE:-copy}"
mkdir -p "$T"
for x in windows fhist dhist; do
  sed -e 's/^eden:/RLLR@/' -e 's/^bal:/RLLRL@/' -e 's/^rotor:/RLLLRR@/' -e 's/^idlar:/RLLLLRLL@/' \
    "$RES/rev4_calib_$x.csv" | grep -v -E '^(idla|mf):' > "$T/rev5_pilot_$x.csv"
done
uv run --frozen python "$EXP/scripts/diag_rev5.py" --res "$T" --out "$RES/rev5_diag_calibrators_idlar.txt" \
  --note "CALIBRATORS relabelled: RLLR=eden RLLRL=bal RLLLRR=rotor RLLLLRLL=idlar (IDLA without restart-launched excursions)" > /dev/null
echo "wrote $RES/rev5_diag_calibrators_idlar.txt"
