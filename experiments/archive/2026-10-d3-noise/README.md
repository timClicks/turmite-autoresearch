# d3-noise

Migrated legacy investigation (2026-10-14). Its files used to sit in the flat `data/` directory (and `calib/`, `occ/`, `snaps/`, `dumps*`, `knock*` where listed) with the label prefix below; `experiments/_migration/map.tsv` gives the exact old -> new path of every file. This stub was generated from file names and script docstrings. It is **not** the original write-up: the question, timestamped hypotheses, commands and results are in `notes/` (mainly `notes/frontier-results.md`, `notes/frontier-status.md`, `notes/research-frontier*.md`; search for the label), and the producing command is usually in the script docstring or a `run_*.sh` here.

Old labels / prefixes: d3, run

## Scripts

- `scripts/d3_stats.py`: D3: area exponent vs turn noise eps. Inputs experiments/archive/2026-10-d3-noise/results/d3_noise.csv (new eps), experiments/2026-10-13-ext-other-lattices-turmites-n
- `scripts/run_d3.sh`: D3: turn-noise crossover. usage (WSL): CARGO_TARGET_DIR=~/turmite-target-frontier2 bash experiments/archive/2026-10-d3-noise/scripts/run_d3.sh

## Results

4 entries in `results/` (2 are `.log`/`.done` markers); csv/json/txt outputs, `*_stats.txt` hold the summaries quoted in the notes.
