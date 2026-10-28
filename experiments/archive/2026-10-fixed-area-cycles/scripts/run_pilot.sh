#!/usr/bin/env bash
# Pilot (registered in README before it ran). Run from the repo root in WSL.
set -euo pipefail
export CARGO_TARGET_DIR=${CARGO_TARGET_DIR:-$HOME/turmite-target}
E=experiments/archive/2026-10-fixed-area-cycles
cargo build --release --example fixed_area_cycles_sampler 2>/dev/null
BIN=$CARGO_TARGET_DIR/release/examples/fixed_area_cycles_sampler
specs=$(mktemp)
{ while read -r r; do for s in 701 702 703 704; do echo "$r@$s"; done; done < $E/results/cohort_rules.txt
  for s in 701 702 703 704; do echo "rotor:$s"; echo "rw:$s"; done; } > $specs
run() { # name threads bands
  rm -rf $E/dumps/$1; /usr/bin/time -f "%e s wall, %M KB max RSS (whole process)" \
    env RAYON_NUM_THREADS=$2 $BIN $E/dumps/$1 268435456 8192 $3 < $specs 2> $E/dumps/$1.stderr || true
  tail -1 $E/dumps/$1.stderr
}
run pilot16 4 32768-34816,131072-139264
run pilot16_t1 1 32768-34816,131072-139264
run pilot8 4 32768-36864,131072-147456
diff -rq $E/dumps/pilot16 $E/dumps/pilot16_t1 && echo "DETERMINISM: 1-thread and 4-thread outputs identical"
