# patterns-fields

Migrated legacy investigation (2026-10-14). Its files used to sit in the flat `data/` directory (and `calib/`, `occ/`, `snaps/`, `dumps*`, `knock*` where listed) with the label prefix below; `experiments/_migration/map.tsv` gives the exact old -> new path of every file. This stub was generated from file names and script docstrings. It is **not** the original write-up: the question, timestamped hypotheses, commands and results are in `notes/` (mainly `notes/frontier-results.md`, `notes/frontier-status.md`, `notes/research-frontier*.md`; search for the label), and the producing command is usually in the script docstring or a `run_*.sh` here.

Old labels / prefixes: patterns

## Scripts

- `scripts/patterns.py`: Pattern-matched fields: does a hard tethered rule form a home?
- `scripts/patterns_analyse.py`: Check every synthetic field independently of the Rust code, and summarise.
- `scripts/patterns_chart.py`: Chart: how tightly a hard tethered ant is held, against how much of its

## Results

8 entries in `results/` (0 are `.log`/`.done` markers); csv/json/txt outputs, `*_stats.txt` hold the summaries quoted in the notes.
