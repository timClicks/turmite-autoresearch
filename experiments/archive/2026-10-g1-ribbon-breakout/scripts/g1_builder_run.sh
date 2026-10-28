#!/usr/bin/env bash
# Recreate the archived blank-board dumps; each completed pair is skipped.
set -euo pipefail
cd "$(dirname "$0")/../../../.."
export UV_PROJECT_ENVIRONMENT="$HOME/.venvs/turmite" UV_LINK_MODE=copy
exp=experiments/archive/2026-10-g1-ribbon-breakout
mkdir -p "$exp/dumps"
cargo build --release --example g1_ribbon_breakout_builder_dump
target="${CARGO_TARGET_DIR:-target}"
for t in 12800000000 12900000000; do
    prefix="$exp/dumps/g1_$t"
    if [[ ! -f "$prefix.done" ]]; then
        "$target/release/examples/g1_ribbon_breakout_builder_dump" RLRLLL "$t" 400000 "$prefix" 32768 800 > "$exp/results/g1_dump_$t.log" 2>&1
        touch "$prefix.done"
    fi
done
uv run "$exp/scripts/g1_wake_extract.py" "$exp/dumps"
