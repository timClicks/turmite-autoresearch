# a2-edge-exponent

Migrated legacy investigation (2026-10-14). Its files used to sit in the flat `data/` directory (and `calib/`, `occ/`, `snaps/`, `dumps*`, `knock*` where listed) with the label prefix below; `experiments/_migration/map.tsv` gives the exact old -> new path of every file. This stub was generated from file names and script docstrings. It is **not** the original write-up: the question, timestamped hypotheses, commands and results are in `notes/` (mainly `notes/frontier-results.md`, `notes/frontier-status.md`, `notes/research-frontier*.md`; search for the label), and the producing command is usually in the script docstring or a `run_*.sh` here.

Old labels / prefixes: a2b, run

## Scripts

- `scripts/a2b_stats.py`: A2b: rotor edge exponent to 2^36 (seeds 11-16) pooled with the 2^34 seeds 1-8 (experiments/archive/2026-10-b1-exact-exponent/results/b1_probe_*.csv). Decision rule: 
- `scripts/run_a2b.sh`

## Results

6 entries in `results/` (3 are `.log`/`.done` markers); csv/json/txt outputs, `*_stats.txt` hold the summaries quoted in the notes.
