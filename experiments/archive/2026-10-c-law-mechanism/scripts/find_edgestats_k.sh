#!/bin/bash
# Recover the unrecorded K of edgestats_sample.csv: run examples/edgestats for the first sample rule at several K and print colour-0/1/3 rows.
cd /mnt/f/Code/turmite/.claude/worktrees/paper-figure-proposals
cargo build --release --example edgestats 2>&1 | tail -1
grep -m3 '^RRRLRRLLLLR,[013],' experiments/archive/2026-10-edge-statistics/results/edgestats_sample.csv | sed 's/^/SAMPLE  /'
for K in 20 21 22 23 24 25 26; do
  ./target/release/examples/edgestats $K RRRLRRLLLLR | awk -F, -v k=$K '$2==0||$2==1||$2==3 {print "K=" k "  " $0}'
done
