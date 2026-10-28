#!/bin/bash
cd /mnt/f/Code/turmite
cut -d, -f1 experiments/archive/2026-10-patched-starts/results/patched.csv | tail -n +2 | sed 's/@.*//' | sort -u > experiments/archive/2026-10-b2-between-rule-variance/results/b2b_rules.txt
(for r in $(cat experiments/archive/2026-10-b2-between-rule-variance/results/b2b_rules.txt); do for s in 1 2 3 4 5 6 7 8; do echo sbg:$r:$s:0.02; done; done) > experiments/archive/2026-10-b2-between-rule-variance/results/b2b_walkers.txt
~/turmite-target-frontier5/release/probe 27 16384 < experiments/archive/2026-10-b2-between-rule-variance/results/b2b_walkers.txt > experiments/archive/2026-10-b2-between-rule-variance/results/b2b_probe.csv 2> experiments/archive/2026-10-b2-between-rule-variance/results/b2b_probe.log && touch experiments/archive/2026-10-b2-between-rule-variance/results/b2b.done
