# e2-sensitive-disc

Migrated legacy investigation (2026-10-14). Its files used to sit in the flat `data/` directory (and `calib/`, `occ/`, `snaps/`, `dumps*`, `knock*` where listed) with the label prefix below; `experiments/_migration/map.tsv` gives the exact old -> new path of every file. This stub was generated from file names and script docstrings. It is **not** the original write-up: the question, timestamped hypotheses, commands and results are in `notes/` (mainly `notes/frontier-results.md`, `notes/frontier-status.md`, `notes/research-frontier*.md`; search for the label), and the producing command is usually in the script docstring or a `run_*.sh` here.

Old labels / prefixes: e2, e2b, run

## Scripts

- `scripts/e2_stats.py`: E1: TSAW (examples/tsaw.rs; experiments/archive/2026-10-e2-sensitive-disc/results/e2_tsaw.csv, tsaw 26 16384 < experiments/archive/2026-10-e1-one-sided-hot-region/results
- `scripts/e2b_stats.py`: E2b: sensitive-disc radius vs near_home radius R (4,6,10,15,22) with an all-tile weighted estimator and the hot-tile estimator. Decision: notes/frontier-2026-10
- `scripts/run_e2.sh`: E2: knockout coarse map with the near_home radius at 6 and 15 (stored job lists). usage (WSL): RAYON_NUM_THREADS=1 bash experiments/archive/2026-10-e2-sensitive-disc
- `scripts/run_e2b.sh`

## Results

8 entries in `results/` (4 are `.log`/`.done` markers); csv/json/txt outputs, `*_stats.txt` hold the summaries quoted in the notes.
