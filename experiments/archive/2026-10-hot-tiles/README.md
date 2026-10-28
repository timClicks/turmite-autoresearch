# hot-tiles

Migrated legacy investigation (2026-10-14). Its files used to sit in the flat `data/` directory (and `calib/`, `occ/`, `snaps/`, `dumps*`, `knock*` where listed) with the label prefix below; `experiments/_migration/map.tsv` gives the exact old -> new path of every file. This stub was generated from file names and script docstrings. It is **not** the original write-up: the question, timestamped hypotheses, commands and results are in `notes/` (mainly `notes/frontier-results.md`, `notes/frontier-status.md`, `notes/research-frontier*.md`; search for the label), and the producing command is usually in the script docstring or a `run_*.sh` here.

Old labels / prefixes: hot, rare

## Scripts

- `scripts/hot_lists.py`: Item 10 complement: cell lists inside the knockout agent's hot 5x5 tiles (read-only use of experiments/archive/2026-10-knockout-maps/knock/RULE/hot.csv, experiments/
- `scripts/hot_rare.py`: Cross-check for items 9/10/14 (read-only on experiments/archive/2026-10-knockout-maps/knock/ and experiments/archive/2026-10-knockout-maps/dumps/): are the knockout map's
- `scripts/hot_recolour_stats.py`: Item 10 complement: recolouring only the rare-colour cells inside the knockout hot tiles vs the same number of other cells in the same tiles.
- `scripts/rare_class_test.py`: Open question Q4 / item 14 generalisation: are the rarest colours of other rules also critical?

## Results

7 entries in `results/` (0 are `.log`/`.done` markers); csv/json/txt outputs, `*_stats.txt` hold the summaries quoted in the notes.
