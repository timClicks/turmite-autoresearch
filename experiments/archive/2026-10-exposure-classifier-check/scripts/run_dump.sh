#!/bin/sh
# Build the truth-table harness into a fresh target dir (stale-build trap, AGENTS.md), log hashes, dump.
# Run from the repository root: sh experiments/archive/2026-10-exposure-classifier-check/scripts/run_dump.sh
set -eu
EXP=experiments/archive/2026-10-exposure-classifier-check
T=${CARGO_TARGET_DIR_FRESH:-$(mktemp -d)}
CARGO_TARGET_DIR=$T cargo build --release --locked --example exposure_classifier_check_dump
BIN=$T/release/examples/exposure_classifier_check_dump
{
  echo "date_utc $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "commit $(git rev-parse HEAD)"
  echo "dirty_src_examples $(git status --porcelain -- src examples | wc -l)"
  echo "rustc $(rustc --version)"
  echo "binary_sha256 $(sha256sum "$BIN" | cut -d' ' -f1)"
  echo "instrument_sha256 $(sha256sum examples/kappa_exposure_classes.rs | cut -d' ' -f1)"
  echo "harness_main_sha256 $(sha256sum examples/exposure_classifier_check_dump/main.rs | cut -d' ' -f1)"
  echo "harness_body_sha256 $(sha256sum examples/exposure_classifier_check_dump/instrument_body.rs | cut -d' ' -f1)"
  echo "command $BIN $EXP/results"
} > $EXP/results/dump.log
"$BIN" $EXP/results
for f in table.csv walks.csv paths.csv; do echo "$f $(sha256sum $EXP/results/$f | cut -d' ' -f1)"; done >> $EXP/results/dump.log
cat $EXP/results/dump.log
