#!/usr/bin/env bash
# Self-test of analyse_rev5.py on committed Rev4 *walker* calibration data relabelled as fake ant specs
# (eden->RLLR, bal->RLLRL, rotor->RLLLRR, idla->RLLLLRLL). Beta medians must equal rev4_analysis.json.
# No ant data are read. Output goes to scratch/rev5_selftest/.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../../../.." && pwd)"
EXP="$ROOT/experiments/active/2026-10-boundary-excursion-durations"
RES="$EXP/results"
T="$EXP/scratch/rev5_selftest"
export UV_PROJECT_ENVIRONMENT="${UV_PROJECT_ENVIRONMENT:-$HOME/.venvs/turmite}" UV_LINK_MODE="${UV_LINK_MODE:-copy}"
mkdir -p "$T"
for x in windows fhist dhist; do
  sed -e 's/^eden:/RLLR@/' -e 's/^bal:/RLLRL@/' -e 's/^rotor:/RLLLRR@/' -e 's/^idla:/RLLLLRLL@/' \
    "$RES/rev4_calib_$x.csv" | grep -v -E '^(idlar|mf):' > "$T/rev5_pilot_$x.csv"
done
REV5_SELFTEST_DIR="$T" uv run --frozen python "$EXP/scripts/analyse_rev5.py" > /dev/null
uv run --frozen python - "$T/rev5_analysis.json" "$RES/rev4_analysis.json" <<'PY'
import json, sys
a = json.load(open(sys.argv[1]))["rules"]; b = json.load(open(sys.argv[2]))
for fake, kind in (("RLLR", "eden"), ("RLLRL", "bal"), ("RLLLRR", "rotor"), ("RLLLLRLL", "idla")):
    x, y = a[fake]["beta"], b[kind]
    assert abs(x["beta"] - y["beta"]) < 1e-12 and x["n_windows"] == y["n_windows"] and x["call"] == y["call"], (fake, x, y)
    print(f"selftest {kind} as {fake}: beta {x['beta']:.3f} n {x['n_windows']} call {x['call']} == rev4; "
          f"Score_tw {a[fake]['score_tw']['verdict']}; reading {a[fake]['reading']}")
print("selftest: PASS")
PY
