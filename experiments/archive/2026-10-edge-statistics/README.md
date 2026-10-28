# edge-statistics

Migrated legacy investigation (2026-10-14). Its files used to sit in the flat `data/` directory (and `calib/`, `occ/`, `snaps/`, `dumps*`, `knock*` where listed) with the label prefix below; `experiments/_migration/map.tsv` gives the exact old -> new path of every file. This stub was generated from file names and script docstrings. It is **not** the original write-up: the question, timestamped hypotheses, commands and results are in `notes/` (mainly `notes/frontier-results.md`, `notes/frontier-status.md`, `notes/research-frontier*.md`; search for the label), and the producing command is usually in the script docstring or a `run_*.sh` here.

Old labels / prefixes: edge, edgestats

## Scripts

- `scripts/edge_exponent.py`: Item 8: is the perimeter-vs-area exponent beta (finite-window 0.52) a finite-time effect that

## Results

6 entries in `results/` (0 are `.log`/`.done` markers); csv/json/txt outputs, `*_stats.txt` hold the summaries quoted in the notes.

## Addendum (2026-10-19)
`results/edgestats_sample.csv` was produced by `examples/edgestats.rs` with K = 23 (window (2^22, 2^23], 4096 board), recovered by matching one rule's rows exactly; see `experiments/archive/2026-10-c-law-mechanism/results/PROVENANCE.md`.
