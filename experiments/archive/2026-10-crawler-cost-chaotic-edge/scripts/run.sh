#!/bin/sh
# Tracer runs for P0b, P2 and P3 (README). Builds into a fresh CARGO_TARGET_DIR (stale-build trap), checks the
# build's exit status, logs commit and binary sha256. Deterministic; output bytes do not depend on RAYON_NUM_THREADS.
# Each output has a .done marker; a rerun skips finished outputs.
#
# usage (repo root): sh experiments/archive/2026-10-crawler-cost-chaotic-edge/scripts/run.sh
set -eu
E=experiments/archive/2026-10-crawler-cost-chaotic-edge
L=$E/results/lists
R=$E/results
TD=${CARGO_TARGET_DIR_FRESH:-$(mktemp -d)}
CARGO_TARGET_DIR=$TD cargo build --release --locked --example c_law_mechanism_trace
B=$TD/release/examples/c_law_mechanism_trace
{
  echo "commit $(git rev-parse HEAD)"
  echo "dirty files (src/ examples/): $(git status --porcelain -- src examples | wc -l)"
  echo "binary sha256 $(sha256sum "$B" | cut -d' ' -f1)"
  echo "rustc $(rustc --version)"
  echo "RAYON_NUM_THREADS=${RAYON_NUM_THREADS:-unset}"
} > "$R/run.log"

run() { # out args... < list
  out=$1; shift
  if [ -f "$R/$out.done" ]; then echo "skip $out"; return; fi
  echo "$(date -u +%FT%TZ) start $out: $*" >> "$R/run.log"
  "$B" "$@" > "$R/$out.tmp"
  mv "$R/$out.tmp" "$R/$out"
  touch "$R/$out.done"
  echo "$(date -u +%FT%TZ) done $out sha256 $(sha256sum "$R/$out" | cut -d' ' -f1)" >> "$R/run.log"
}

run trace_p0_fillers.jsonl blank 27 8192 < $L/p0_fillers.txt
run trace_p2_parents_24.jsonl blank 24 4096 < $L/p2_parents.txt
run trace_p2_parents_25.jsonl blank 25 4096 < $L/p2_parents.txt
run trace_p2_mutants.jsonl blank 24 4096 < $L/p2_mutants.txt
run trace_p3_pi.jsonl blank 24 4096 < $L/p3_pi.txt
run trace_p3_ctrl.jsonl blank 24 4096 < $L/p3_ctrl.txt
