#!/bin/sh
# Stage 2 tracer runs (README). Fresh CARGO_TARGET_DIR, build status checked, commit and binary sha256 logged.
# usage (repo root): sh experiments/archive/2026-10-crawler-cost-chaotic-edge/scripts/run_stage2.sh
set -eu
E=experiments/archive/2026-10-crawler-cost-chaotic-edge
R=$E/results
TD=${CARGO_TARGET_DIR_FRESH:-$(mktemp -d)}
CARGO_TARGET_DIR=$TD cargo build --release --locked --example c_law_mechanism_trace
B=$TD/release/examples/c_law_mechanism_trace
{
  echo "commit $(git rev-parse HEAD)"
  echo "dirty files (src/ examples/): $(git status --porcelain -- src examples | wc -l)"
  echo "binary sha256 $(sha256sum "$B" | cut -d' ' -f1)"
  echo "rustc $(rustc --version)"
} > "$R/run_stage2.log"
if [ ! -f "$R/trace_s2.jsonl.done" ]; then
  echo "$(date -u +%FT%TZ) start trace_s2.jsonl: blank 24 4096" >> "$R/run_stage2.log"
  "$B" blank 24 4096 < "$E/results/lists/s2_specs.txt" > "$R/trace_s2.jsonl.tmp"
  mv "$R/trace_s2.jsonl.tmp" "$R/trace_s2.jsonl"
  touch "$R/trace_s2.jsonl.done"
  echo "$(date -u +%FT%TZ) done sha256 $(sha256sum "$R/trace_s2.jsonl" | cut -d' ' -f1)" >> "$R/run_stage2.log"
fi
