#!/bin/bash
# run_census.sh : from repo root (in WSL). Census of all R-prefixed rules, lengths 2..14, 2^24 steps, 4096 board.
set -e
R=experiments/archive/2026-10-rulepat
python3 $R/scripts/gen_rules.py 2 14 > $R/results/census_rules.txt
./target/release/examples/rulepat_scan 24 4096 < $R/results/census_rules.txt > $R/results/census_scan.csv
touch $R/results/census_scan.done
