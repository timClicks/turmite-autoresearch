# e4-patch-vs-swap

Migrated legacy investigation (2026-10-14). Its files used to sit in the flat `data/` directory (and `calib/`, `occ/`, `snaps/`, `dumps*`, `knock*` where listed) with the label prefix below; `experiments/_migration/map.tsv` gives the exact old -> new path of every file. This stub was generated from file names and script docstrings. It is **not** the original write-up: the question, timestamped hypotheses, commands and results are in `notes/` (mainly `notes/frontier-results.md`, `notes/frontier-status.md`, `notes/research-frontier*.md`; search for the label), and the producing command is usually in the script docstring or a `run_*.sh` here.

Old labels / prefixes: e4, run

## Scripts

- `scripts/e4_jobs.py`: E4 job lists. Per rule: (a) the stored coarse jobs (5x5 patch x3 permutations, blanks, 100 swaps of 25 cells) verbatim,
- `scripts/e4_stats.py`: E4: loss vs count of rare cells lost, patches vs swaps. Input experiments/archive/2026-10-knockout-maps/knock/RULE/e4.csv (+ coarse.csv for the determinism check).
- `scripts/run_e4.sh`: E4: knockout jobs with rare-colour accounting (RARE env). usage (WSL): RAYON_NUM_THREADS=1 bash experiments/archive/2026-10-e4-patch-vs-swap/scripts/run_e4.sh

## Results

3 entries in `results/` (2 are `.log`/`.done` markers); csv/json/txt outputs, `*_stats.txt` hold the summaries quoted in the notes.
