# b4-unfitted-rules

Migrated legacy investigation (2026-10-14). Its files used to sit in the flat `data/` directory (and `calib/`, `occ/`, `snaps/`, `dumps*`, `knock*` where listed) with the label prefix below; `experiments/_migration/map.tsv` gives the exact old -> new path of every file. This stub was generated from file names and script docstrings. It is **not** the original write-up: the question, timestamped hypotheses, commands and results are in `notes/` (mainly `notes/frontier-results.md`, `notes/frontier-status.md`, `notes/research-frontier*.md`; search for the label), and the producing command is usually in the script docstring or a `run_*.sh` here.

Old labels / prefixes: b4

## Scripts

- `scripts/b4_builders.py`: B4 (review follow-up): what are the 304 census 'builders'? census.py labels builder = did not reach 2^27 inside the growth grid OR steps/(w*h) < 20.
- `scripts/b4_stats.py`: B4: why were 153 rules unfitted? Compare probe_all.csv (8192 board) with the 32768 rerun experiments/archive/2026-10-b4-unfitted-rules/results/b4_probe.csv.

## Results

6 entries in `results/` (2 are `.log`/`.done` markers); csv/json/txt outputs, `*_stats.txt` hold the summaries quoted in the notes.
