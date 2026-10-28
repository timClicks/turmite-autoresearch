#!/usr/bin/env bash
# Full scan: build into a fresh target dir, log binary sha256, commit, command. Run from the repo root.
set -euo pipefail
E=experiments/archive/2026-10-highway-preconditions
# A fresh target dir per run (AGENTS.md stale-build trap); the published run used one that was new at the time.
export CARGO_TARGET_DIR=${CARGO_TARGET_DIR:-$(mktemp -d "$HOME/turmite-target-hp.XXXXXX")}
cargo build --release --example highway_preconditions_scan
B=$CARGO_TARGET_DIR/release/examples/highway_preconditions_scan
{
  echo "commit $(git rev-parse HEAD)$(git diff --quiet -- src examples || echo ' (dirty)')"
  echo "binary_sha256 $(sha256sum $B | cut -d' ' -f1)"
  echo "threads ${RAYON_NUM_THREADS:-all} ($(nproc) cores)"
  echo "cmd $B highway $E/results/highway_specs.txt $E/results"
  echo "cmd $B control $E/results/control_specs.txt $E/results"
  echo "start $(date -Is)"
} > $E/results/run.log
{ time $B highway $E/results/highway_specs.txt $E/results ; } 2>> $E/results/run.log
{ time $B control $E/results/control_specs.txt $E/results ; } 2>> $E/results/run.log
echo "end $(date -Is)" >> $E/results/run.log
sha256sum $E/results/*.csv $E/results/*.tsv >> $E/results/run.log
