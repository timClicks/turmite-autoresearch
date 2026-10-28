#!/usr/bin/env bash
# usage (WSL, repo root): bash experiments/archive/2026-10-lattice-c-law/scripts/run.sh
# Builds into a fresh target dir (stale-build trap, AGENTS.md), logs the binary sha256, runs controls then ants.
set -euo pipefail
cd "$(dirname "$0")/../../../.."
E=experiments/archive/2026-10-lattice-c-law
export CARGO_TARGET_DIR=$HOME/turmite-target-lattice-$(git rev-parse --short HEAD)
cargo build --release --example lattice_c_law_run
T=$CARGO_TARGET_DIR/release/examples/lattice_c_law_run
{ echo "commit $(git rev-parse HEAD) (dirty: $(git status --porcelain src examples | wc -l) files)"; sha256sum $T; } > $E/results/run.log
for part in controls ants; do
  [ -f $E/results/$part.done ] && continue
  /usr/bin/time -f "$part wall %e s" $T 12 27 8192 < $E/results/lists/$part.txt > $E/results/$part.csv 2>> $E/results/run.log
  touch $E/results/$part.done
done
