#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../../../.."
export UV_PROJECT_ENVIRONMENT=$HOME/.venvs/turmite UV_LINK_MODE=copy
source experiments/active/2026-10-gpu-ant-sweep/scripts/env.sh
E=experiments/archive/2026-10-kappa-growth-clock
mkdir -p "$E/dumps" "$E/scratch" "$E/results"
if pgrep -af '/(gpu_probe|gpu_sweep|probe|sweep|sweep_lean)( |$)' > "$E/scratch/busy.txt"; then
    cat "$E/scratch/busy.txt"; exit 1
fi
recipe=$(sha256sum "$E/results/specs.txt" "$E/scripts/run.sh" src/probe.rs src/bin/probe.rs src/gpu/probe.rs src/gpu/probe.cu src/bin/gpu_probe.rs src/walkers.rs Cargo.lock | sha256sum | cut -d' ' -f1)
if test -f "$E/results/batch.done"; then
    test "$(cat "$E/results/batch.done")" = "$recipe"
    sha256sum -c "$E/results/raw.sha256"
    echo 'Verified completed batch; skipped'; exit 0
fi
cargo build --release --features cuda --bin gpu_probe --bin probe
cargo test --release > "$E/results/release-tests.log" 2>&1
cargo test --release --features cuda --test gpu_probe > "$E/results/gpu-tests.log" 2>&1
"$CARGO_TARGET_DIR/release/probe" 24 4096 < "$E/results/spot_specs.txt" > "$E/scratch/cpu.csv" 2> "$E/results/cpu-spot.log"
"$CARGO_TARGET_DIR/release/gpu_probe" 24 4096 --lanes 256 --pool-gb 4 < "$E/results/spot_specs.txt" > "$E/scratch/gpu.csv" 2> "$E/results/gpu-spot.log"
cmp "$E/scratch/cpu.csv" "$E/scratch/gpu.csv"
echo 'Four specs byte-identical: probe/gpu_probe 24 4096' > "$E/results/spot-check.txt"
git rev-parse HEAD > "$E/results/run-commit.txt"
git status --short > "$E/results/run-tree.txt"
sha256sum src/probe.rs src/bin/probe.rs src/gpu/probe.rs src/gpu/probe.cu src/bin/gpu_probe.rs src/walkers.rs Cargo.lock "$E/scripts/run.sh" "$E/results/specs.txt" > "$E/results/run-sources.sha256"
"$CARGO_TARGET_DIR/release/gpu_probe" 24 4096 --lanes 256 --pool-gb 4 --stats "$E/results/gpu.json" < "$E/results/specs.txt" > "$E/dumps/probe.csv.partial" 2> "$E/results/probe.log"
mv "$E/dumps/probe.csv.partial" "$E/dumps/probe.csv"
sha256sum "$E/dumps/probe.csv" > "$E/results/raw.sha256"
echo "$recipe" > "$E/results/batch.done"
