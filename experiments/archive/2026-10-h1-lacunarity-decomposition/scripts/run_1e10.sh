#!/bin/bash
# Item 17: push the length<=10 primitive rules still unresolved at 1e9 to 1e10 steps (lean ant, grid 32768).
# Rules are shuffled with a fixed seed so any prefix of the chunks is an unbiased sample.
# Chunked and resumable: experiments/archive/2026-10-highways-unresolved-rules-1e10-1e11/results/h1e10/chunk_NN.{txt,csv,done}.
# usage (WSL): RAYON_NUM_THREADS=3 CARGO_TARGET_DIR=~/turmite-target-frontier bash experiments/archive/2026-10-h1-lacunarity-decomposition/scripts/run_1e10.sh
cd /mnt/f/Code/turmite
cargo build --release --bin sweep_lean 2>/dev/null
if [ ! -f experiments/archive/2026-10-highways-unresolved-rules-1e10-1e11/results/h1e10/chunk_00.txt ]; then
  awk -F, 'NR>1 && $3=="budget"{print $1}' experiments/archive/2026-10-census-sweeps/results/sweep_1B.csv | python3 -c "
import sys, random
def root(s):
    n=len(s)
    for p in range(1,n):
        if n%p==0 and s[:p]*(n//p)==s: return s[:p]
    return s
rs=[l.strip() for l in sys.stdin if l.strip()]
rs=[r for r in rs if root(r)==r]
random.Random(20261013).shuffle(rs)
for i in range(0,len(rs),12):
    open('experiments/archive/2026-10-highways-unresolved-rules-1e10-1e11/results/h1e10/chunk_%02d.txt'%(i//12),'w').write('\n'.join(rs[i:i+12])+'\n')
print(len(rs),'rules',file=sys.stderr)
"
fi
for f in experiments/archive/2026-10-highways-unresolved-rules-1e10-1e11/results/h1e10/chunk_*.txt; do
  b=${f%.txt}
  [ -f $b.done ] && continue
  $CARGO_TARGET_DIR/release/sweep_lean - - 10000000000 32768 < $f > $b.csv 2> $b.log && touch $b.done
done
