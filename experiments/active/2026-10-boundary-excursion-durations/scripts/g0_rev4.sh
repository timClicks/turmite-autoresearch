#!/usr/bin/env bash
# Revision 4 G0 instrument gate (README "Revision 4 registration"). Needs BASE_BIN = boundary_excursions built at 8904956.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../../../.." && pwd)"
BIN="${BIN:-$ROOT/target/release/examples/boundary_excursions}"
BASE_BIN="${BASE_BIN:?build examples/boundary_excursions at 8904956 and set BASE_BIN}"
T="$(mktemp -d)"
S='rw:7\nrotor:7\ncup:1.0:7\neden:7\nidla:7\nidlar:7\nmf:7\n'
echo "bin sha256=$(sha256sum "$BIN" | awk '{print $1}') base sha256=$(sha256sum "$BASE_BIN" | awk '{print $1}')"
printf "$S" | "$BASE_BIN" 14 512 --hist "$T/h0" --fhist "$T/f0" > "$T/w0" 2>/dev/null
printf "$S" | "$BIN" 14 512 --check --hist "$T/h1" --fhist "$T/f1" --dhist "$T/d1" > "$T/w1" 2>/dev/null
echo "smoke --check --dhist: exit 0"
printf "$S" | "$BIN" 14 512 --hist "$T/h2" --fhist "$T/f2" > "$T/w2" 2>/dev/null
for x in w h f; do cmp "$T/${x}0" "$T/${x}1"; cmp "$T/${x}0" "$T/${x}2"; done
echo "windows, hist, fhist byte-identical to base (with and without --dhist)"
printf 'bal:7\n' | "$BIN" 14 512 --check --dhist /dev/null > /dev/null 2>/dev/null
echo "bal:7 --check (N = tau, births, budget): exit 0"
for m in "--mutant" "--fine-mutant" "--depth-mutant --dhist /dev/null"; do
  set +e
  # shellcheck disable=SC2086
  printf 'rw:7\neden:7\n' | "$BIN" 12 256 --check $m > /dev/null 2>"$T/err"
  ec=$?
  set -e
  if [[ $ec -eq 0 ]]; then echo "mutant $m FAILED to panic" >&2; exit 1; fi
  echo "mutant $m panicked (exit $ec): $(grep -m1 -A1 panicked "$T/err" | tail -1 | cut -c1-110)"
done
rm -rf "$T"
