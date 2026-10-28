# calib-instrument-calibration

Migrated legacy investigation (2026-10-14). Its files used to sit in the flat `data/` directory (and `calib/`, `occ/`, `snaps/`, `dumps*`, `knock*` where listed) with the label prefix below; `experiments/_migration/map.tsv` gives the exact old -> new path of every file. This stub was generated from file names and script docstrings. It is **not** the original write-up: the question, timestamped hypotheses, commands and results are in `notes/` (mainly `notes/frontier-results.md`, `notes/frontier-status.md`, `notes/research-frontier*.md`; search for the label), and the producing command is usually in the script docstring or a `run_*.sh` here.

Old labels / prefixes: alt, calib, calibrate, checkpoints, contour, done, exactly4, long, short

## Scripts

- `scripts/calibrate.py`: Calibration part A: put rotor walkers (true range exponent 2/3, width 1/3,
- `scripts/contour_chunks.py`: Contour radius of nbar = 1 at N = 1e6, per chunk of seeds, with two
- `scripts/contour_verdict.py`: Combine the contour-radius runs (main generator and alternative generator)

## Results

17 entries in `results/` (0 are `.log`/`.done` markers); csv/json/txt outputs, `*_stats.txt` hold the summaries quoted in the notes.
