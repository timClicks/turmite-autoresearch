# item21-slow-outliers

Migrated legacy investigation (2026-10-14). Its files used to sit in the flat `data/` directory (and `calib/`, `occ/`, `snaps/`, `dumps*`, `knock*` where listed) with the label prefix below; `experiments/_migration/map.tsv` gives the exact old -> new path of every file. This stub was generated from file names and script docstrings. It is **not** the original write-up: the question, timestamped hypotheses, commands and results are in `notes/` (mainly `notes/frontier-results.md`, `notes/frontier-status.md`, `notes/research-frontier*.md`; search for the label), and the producing command is usually in the script docstring or a `run_*.sh` here.

Old labels / prefixes: item21

## Scripts

- `scripts/item21_select.py`: Item 21: pick the extreme exponent outliers among blob rules (alpha_w > 0.40 or < 0.27) plus 30 random core
- `scripts/item21_stats.py`: Item 21: re-measurement of exponent outliers. Input experiments/archive/2026-10-item21-slow-outliers/results/item21_probe.csv (probe 27 < experiments/2026-10-13-item

## Results

7 entries in `results/` (2 are `.log`/`.done` markers); csv/json/txt outputs, `*_stats.txt` hold the summaries quoted in the notes.
