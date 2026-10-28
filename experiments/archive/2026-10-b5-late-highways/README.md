# b5-late-highways

Migrated legacy investigation (2026-10-14). Its files used to sit in the flat `data/` directory (and `calib/`, `occ/`, `snaps/`, `dumps*`, `knock*` where listed) with the label prefix below; `experiments/_migration/map.tsv` gives the exact old -> new path of every file. This stub was generated from file names and script docstrings. It is **not** the original write-up: the question, timestamped hypotheses, commands and results are in `notes/` (mainly `notes/frontier-results.md`, `notes/frontier-status.md`, `notes/research-frontier*.md`; search for the label), and the producing command is usually in the script docstring or a `run_*.sh` here.

Old labels / prefixes: b5

## Scripts

- `scripts/b5_restart6.sh`: Restart the B5 driver with 6 rayon threads (12 rules per chunk = exactly 2 rounds of 6) at the next chunk boundary. Safe: chunks are resumable.
- `scripts/b5_stats.py`: B5: highway onsets in (1e10, 1e11] for a 240-rule unbiased sample of the rules still unresolved at 1e10 (experiments/2026-10-13-highways-unresolved-rules-1e10-1

## Results

2 entries in `results/` (1 are `.log`/`.done` markers); csv/json/txt outputs, `*_stats.txt` hold the summaries quoted in the notes.
