#!/usr/bin/env bash
# usage (WSL, repo root): bash experiments/archive/2026-10-lattice-c-law/scripts/run_moore.sh
# Follow-up B. Fresh target dir, binary sha256 logged, controls then ants; resumable via *.done.
set -euo pipefail
cd "$(dirname "$0")/../../../.."
E=experiments/archive/2026-10-lattice-c-law
export CARGO_TARGET_DIR=$HOME/turmite-target-lattice-moore-$(git rev-parse --short HEAD)
cargo build --release --example lattice_c_law_run
T=$CARGO_TARGET_DIR/release/examples/lattice_c_law_run
{ echo "commit $(git rev-parse HEAD)"; sha256sum $T; } > $E/results/run_moore.log
for part in controls ants; do
  [ -f $E/results/moore_$part.done ] && continue
  /usr/bin/time -f "$part wall %e s" $T 12 27 8192 < $E/results/lists/moore_$part.txt > $E/results/moore_$part.csv 2>> $E/results/run_moore.log
  touch $E/results/moore_$part.done
done
