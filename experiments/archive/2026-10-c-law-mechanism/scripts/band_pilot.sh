#!/bin/bash
# Pilot (not part of any registered analysis): how fast does the torus band get consumed? Three sample rules NOT in band.txt.
# prints births / boundary steps / area_t0 / area per window for log2 = 24..28. Used only to pick the band window.
cd /mnt/f/Code/turmite/.claude/worktrees/paper-figure-proposals
T=./target/release/examples/c_law_mechanism_trace
for L in 24 25 26 27 28; do
  printf 'RRRLLRLLRL\nRRLLRLLLRLL\nRLLRRRLRLR\n' | $T band $L 256 1024 512 20261019 | sed -E 's/.*"spec":"([A-Z]+)","log2":([0-9]+),"births":([0-9]+),"boundary_steps":([0-9]+),"fresh_nbrs":[0-9]+,"area":([0-9]+),"area_t0":([0-9]+).*/\1 log2=\2 births=\3 S=\4 area_t0=\6 area=\5/'
done
