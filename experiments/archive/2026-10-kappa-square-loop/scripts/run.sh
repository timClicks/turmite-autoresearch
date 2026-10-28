#!/usr/bin/env bash
# usage (repo root, in WSL): bash experiments/archive/2026-10-kappa-square-loop/scripts/run.sh [cohort|mutants]
# cohort: the 300 fresh rules x seeds 601..608 of ../2026-10-kappa-leadrun-fresh (2400 runs, 2^27 steps, board 8192)
# mutants: the 3336 mutant specs of the same folder (for C3). Output dumps/loops_<what>.csv (gitignored, bulk).
set -euo pipefail
what=${1:-cohort}
E=experiments/archive/2026-10-kappa-square-loop
P=experiments/archive/2026-10-kappa-leadrun-fresh/results
case $what in cohort) specs=$P/specs.txt;; mutants) specs=$P/mutant_specs.txt;; *) echo bad arg; exit 2;; esac
mkdir -p $E/dumps
[ -f $E/dumps/loops_$what.done ] && { echo already done; exit 0; }
cargo build --release --example kappa_square_loop_sampler
echo "git $(git rev-parse --short HEAD) $(date -Iseconds) cmd: kappa_square_loop_sampler 27 8192 20 < $specs" > $E/results/run_$what.log
./target/release/examples/kappa_square_loop_sampler 27 8192 20 < $specs > $E/dumps/loops_$what.csv 2>> $E/results/run_$what.log
echo "finished $(date -Iseconds)" >> $E/results/run_$what.log
sha256sum target/release/examples/kappa_square_loop_sampler $E/dumps/loops_$what.csv >> $E/results/run_$what.log
touch $E/dumps/loops_$what.done
