#!/bin/bash
# G5 (board independence): RLLLRLRLLL on the 32768 board, compared with the 65536 run up to the exit step of the smaller board.
# Supplementary negative controls (added after registration, labelled so): two census "blob" rules, 3e9 steps, 8192 board.
set -e
E=experiments/archive/2026-10-sweeper-generalisation
FL=$HOME/turmite-target-sg1/release/examples/sweeper_generalisation_frontlog
mkdir -p $E/scratch/g5_RLLLRLRLLL_32768 $E/scratch/neg_RLLLLRRLL $E/scratch/neg_RLRLLLLRRL
$FL RLLLRLRLLL 40000000000 32768 $E/scratch/g5_RLLLRLRLLL_32768 1000000 > $E/scratch/g5_RLLLRLRLLL_32768/fingerprint.txt 2> $E/scratch/g5_RLLLRLRLLL_32768/log.txt &
$FL RLLLLRRLL 3000000000 8192 $E/scratch/neg_RLLLLRRLL 1000000 > $E/scratch/neg_RLLLLRRLL/fingerprint.txt 2>&1 &
$FL RLRLLLLRRL 3000000000 8192 $E/scratch/neg_RLRLLLLRRL 1000000 > $E/scratch/neg_RLRLLLLRRL/fingerprint.txt 2>&1 &
wait
echo done > $E/results/g5_negctl.done
