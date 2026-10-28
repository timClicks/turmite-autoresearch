#!/usr/bin/env bash
# Portable replay using the established CPU probe; no CUDA sources required.
set -euo pipefail
cd "$(dirname "$0")/../../../.."
export UV_PROJECT_ENVIRONMENT=$HOME/.venvs/turmite UV_LINK_MODE=copy
export CARGO_TARGET_DIR=${CARGO_TARGET_DIR:-$HOME/turmite-target}
E=experiments/archive/2026-10-kappa-growth-clock
mkdir -p "$E/dumps"
cargo build --release --bin probe
"$CARGO_TARGET_DIR/release/probe" 24 4096 < "$E/results/specs.txt" > "$E/dumps/cpu-replay.csv.partial" 2> "$E/results/cpu-replay.log"
mv "$E/dumps/cpu-replay.csv.partial" "$E/dumps/cpu-replay.csv"
# Compare with the frozen raw digest even if the GPU dump is absent.
actual=$(sha256sum "$E/dumps/cpu-replay.csv" | cut -d' ' -f1)
expected=$(cut -d' ' -f1 "$E/results/raw.sha256")
test "$actual" = "$expected"
echo 'Full CPU replay: all 256 specs byte-identical to frozen GPU CSV' > "$E/results/cpu-replay-check.txt"
