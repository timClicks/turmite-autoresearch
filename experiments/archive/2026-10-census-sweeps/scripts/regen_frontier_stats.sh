#!/bin/bash
# Regenerates every analysis text output of the frontier work from the raw data files (deterministic; run twice and diff to check).
# usage (WSL): bash experiments/archive/2026-10-census-sweeps/scripts/regen_frontier_stats.sh OUTSUFFIX   (writes results/NAME.OUTSUFFIX instead of results/NAME.txt when OUTSUFFIX is given)
cd /mnt/f/Code/turmite
export UV_PROJECT_ENVIRONMENT=$HOME/.venvs/turmite UV_LINK_MODE=copy
ext=${1:-txt}
run() { out=$1; shift; d=$(dirname "$(dirname "$1")")/results; uv run "$@" 2>&1 | grep -v "Reading inline" > $d/$out.$ext; }  # output lands in the results/ of the script's experiment
run highway_stats experiments/archive/2026-10-highways-unresolved-rules-1e10-1e11/scripts/highway_stats.py
run edge_exponent experiments/archive/2026-10-edge-statistics/scripts/edge_exponent.py
run dose_stats experiments/archive/2026-10-dose-corruption-dose/scripts/dose_stats.py
run classko_stats experiments/archive/2026-10-knockout-maps/scripts/classko_stats.py
run recolour_stats experiments/archive/2026-10-recolour/scripts/recolour_stats.py
run flip_stats experiments/archive/2026-10-flip-damage/scripts/flip_stats.py
run formage_stats experiments/archive/2026-10-formage-age/scripts/formage_stats.py
run tether_screen experiments/archive/2026-10-tether-rules/scripts/tether_screen_stats.py
run spread_dups experiments/archive/2026-10-spread-home/scripts/spread_dups.py
run spread_clusters experiments/archive/2026-10-spread-home/scripts/spread_clusters.py
run spread_groups experiments/archive/2026-10-spread-home/scripts/spread_groups.py
run hot_rare experiments/archive/2026-10-hot-tiles/scripts/hot_rare.py
run hot_recolour_stats experiments/archive/2026-10-hot-tiles/scripts/hot_recolour_stats.py
run item21_stats experiments/archive/2026-10-item21-slow-outliers/scripts/item21_stats.py
run item4_stats experiments/archive/2026-10-item4-exponent-rotor-calibrated/scripts/item4_stats.py
run item4_rotor_stats experiments/archive/2026-10-item4-exponent-rotor-calibrated/scripts/item4_stats.py experiments/archive/2026-10-item4-exponent-rotor-calibrated/results/item4_rotor_probe.csv
run ext_stats experiments/archive/2026-10-ext-other-lattices-turmites-noise/scripts/ext_stats.py
run ext_hex experiments/archive/2026-10-ext-other-lattices-turmites-noise/scripts/ext_lattice_stats.py experiments/archive/2026-10-ext-other-lattices-turmites-noise/results/ext_hex.csv
run ext_cube experiments/archive/2026-10-ext-other-lattices-turmites-noise/scripts/ext_lattice_stats.py experiments/archive/2026-10-ext-other-lattices-turmites-noise/results/ext_cube.csv
run ext_tri experiments/archive/2026-10-ext-other-lattices-turmites-noise/scripts/ext_lattice_stats.py experiments/archive/2026-10-ext-other-lattices-turmites-noise/results/ext_tri.csv 16 24
run cube_fill experiments/archive/2026-10-probe-growth-census/scripts/cube_fill.py
run shape_stats experiments/archive/2026-10-shape-limit/scripts/shape_stats.py experiments/archive/2026-10-shape-limit/results/shape_rotor.csv experiments/archive/2026-10-shape-limit/results/shape_ants.csv
run c_letters experiments/archive/2026-10-probe-growth-census/scripts/c_letters.py
run mixing_calib experiments/archive/2026-10-mixing/scripts/mixing_calib.py
uv run research-outputs/scholarly-articles/cube-root-growth/seed_uncertainty.py 2>&1 | grep -v "Reading inline" > experiments/archive/2026-10-probe-growth-census/results/seed_uncertainty.$ext
run ext_cube_long experiments/archive/2026-10-ext-other-lattices-turmites-noise/scripts/ext_long_stats.py cube
run ext_tm_long experiments/archive/2026-10-ext-other-lattices-turmites-noise/scripts/ext_long_stats.py tm
run h1e10_stats experiments/archive/2026-10-highways-unresolved-rules-1e10-1e11/scripts/h1e10_stats.py
uv run experiments/archive/2026-10-cell1/scripts/cell1_stats.py 2>&1 | grep -v "Reading inline" > experiments/archive/2026-10-cell1/results/cell1_stats.$ext
