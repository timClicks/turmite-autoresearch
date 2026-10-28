#!/bin/bash
# usage (WSL): bash experiments/archive/2026-10-boundary-return-map/scripts/run_pilot.sh
cd "$(dirname "$0")/.."
B=$HOME/turmite-target-brm/release/examples/boundary_return_map_sampler
echo "commit $(git rev-parse HEAD) binary $(sha256sum $B | cut -c1-16)"
$B scratch/pilot 1048576 4096 16 64 8 0,1,2,4,8,16,32,64,128 32768,131072 pilot_v1 2 < results/pilot_specs.txt
