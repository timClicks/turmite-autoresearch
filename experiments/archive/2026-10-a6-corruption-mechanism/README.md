# a6-corruption-mechanism

Migrated legacy investigation (2026-10-14). Its files used to sit in the flat `data/` directory (and `calib/`, `occ/`, `snaps/`, `dumps*`, `knock*` where listed) with the label prefix below; `experiments/_migration/map.tsv` gives the exact old -> new path of every file. This stub was generated from file names and script docstrings. It is **not** the original write-up: the question, timestamped hypotheses, commands and results are in `notes/` (mainly `notes/frontier-results.md`, `notes/frontier-status.md`, `notes/research-frontier*.md`; search for the label), and the producing command is usually in the script docstring or a `run_*.sh` here.

Old labels / prefixes: a6, run

## Scripts

- `scripts/a6_jobs.py`: A6 mechanism: job list for knock `strat` jobs. Per rule: 60 draws x class {0,1} x occupancy quartile {0..3}, 25 cells each. Writes experiments/2026-10-12-knocko
- `scripts/a6_stats.py`: A6 mechanism: loss vs occupancy quartile for rare vs other cells. Decision rules: notes/frontier-2026-10-13-results.md. usage: uv run experiments/2026-10-13-a6-
- `scripts/run_a6.sh`: A6 mechanism test. usage (WSL): RAYON_NUM_THREADS=1 bash experiments/archive/2026-10-a6-corruption-mechanism/scripts/run_a6.sh

## Results

4 entries in `results/` (2 are `.log`/`.done` markers); csv/json/txt outputs, `*_stats.txt` hold the summaries quoted in the notes.
