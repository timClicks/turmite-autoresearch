#!/bin/bash
# Hull-width run (WSL). Resumable: skips finished halves. Needs: cargo build --release --example hull_width
cd /mnt/f/Code/turmite
D=experiments/archive/2026-10-hull-width/results
T=${CARGO_TARGET_DIR:-target}
export RAYON_NUM_THREADS=${RAYON_NUM_THREADS:-4}
for r in RLR RLRLRRRLLR RLLLRLLRRLR RLRLLRRLL RLRLRRRRLR RLLRLLRLRRRL; do for s in 221 222 223 224; do echo $r@$s; done; done > $D/hull_ants_specs.txt
for s in $(seq 221 228); do echo rotor:$s; done > $D/hull_rotor_specs.txt
git rev-parse HEAD > $D/hull.commit
for w in rotor ants; do
  [ -f $D/hull_$w.done ] && continue
  $T/release/examples/hull_width 30 8192 < $D/hull_${w}_specs.txt > $D/hull_$w.csv 2> $D/hull_$w.log && touch $D/hull_$w.done
done
touch $D/hull.done
# Cross-check for decision rule 1: `shape` Wsurf on the same ants/rotors to k=24 must equal Wall.
cargo build --release --example shape 2>&1 | tail -1
cat $D/hull_rotor_specs.txt $D/hull_ants_specs.txt | $T/release/examples/shape 24 8192 > $D/shape_check.csv 2> $D/shape_check.log
