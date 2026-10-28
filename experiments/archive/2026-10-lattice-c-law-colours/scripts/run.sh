#!/usr/bin/env bash
# usage (WSL, repo root): bash experiments/archive/2026-10-lattice-c-law-colours/scripts/run.sh
# Builds into a fresh target dir (stale-build trap, AGENTS.md), logs the binary sha256, traces the 960 frozen ants of the
# parent experiment (2^27 steps, 8192 board, last octave).
set -euo pipefail
cd "$(dirname "$0")/../../../.."
E=experiments/archive/2026-10-lattice-c-law-colours
export CARGO_TARGET_DIR=$HOME/turmite-target-lcc-$(git rev-parse --short HEAD)
cargo build --release --example lattice_c_law_colours
T=$CARGO_TARGET_DIR/release/examples/lattice_c_law_colours
{ echo "commit $(git rev-parse HEAD) (dirty: $(git status --porcelain src examples | wc -l) files)"; sha256sum $T; } > $E/results/run.log
[ -f $E/results/traces.done ] && exit 0
/usr/bin/time -f "traces wall %e s" $T 27 8192 < experiments/archive/2026-10-lattice-c-law/results/lists/ants.txt > $E/results/traces.jsonl 2>> $E/results/run.log
touch $E/results/traces.done
