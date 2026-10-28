# e6-hot-window-age

Migrated legacy investigation (2026-10-14). Its files used to sit in the flat `data/` directory (and `calib/`, `occ/`, `snaps/`, `dumps*`, `knock*` where listed) with the label prefix below; `experiments/_migration/map.tsv` gives the exact old -> new path of every file. This stub was generated from file names and script docstrings. It is **not** the original write-up: the question, timestamped hypotheses, commands and results are in `notes/` (mainly `notes/frontier-results.md`, `notes/frontier-status.md`, `notes/research-frontier*.md`; search for the label), and the producing command is usually in the script docstring or a `run_*.sh` here.

Old labels / prefixes: dumps, e6, run

## Scripts

- `scripts/e6_jobs.py`: E6 job lists: hot tiles of the 2^24 map (experiments/archive/2026-10-knockout-maps/knock/RULE/hot.csv) x fresh permutation seeds 11,12,13, plus 100 swaps (seeds 101.
- `scripts/e6_stats.py`: E6: fraction of the 2^24-hot tiles that are hot (fresh permutations) at earlier ages. Design: notes/frontier-2026-10-13-results.md. usage: uv run experiments/20
- `scripts/run_e6.sh`: E6: formation of the hot windows. usage (WSL): RAYON_NUM_THREADS=1 bash experiments/archive/2026-10-e6-hot-window-age/scripts/run_e6.sh

## Results

3 entries in `results/` (2 are `.log`/`.done` markers); csv/json/txt outputs, `*_stats.txt` hold the summaries quoted in the notes.

## Bulk output (gitignored)

- `dumps_e6/`
