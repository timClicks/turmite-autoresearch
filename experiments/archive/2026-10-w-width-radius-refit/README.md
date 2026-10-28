# w-width-radius-refit

Migrated legacy investigation (2026-10-14). Its files used to sit in the flat `data/` directory (and `calib/`, `occ/`, `snaps/`, `dumps*`, `knock*` where listed) with the label prefix below; `experiments/_migration/map.tsv` gives the exact old -> new path of every file. This stub was generated from file names and script docstrings. It is **not** the original write-up: the question, timestamped hypotheses, commands and results are in `notes/` (mainly `notes/frontier-results.md`, `notes/frontier-status.md`, `notes/research-frontier*.md`; search for the label), and the producing command is usually in the script docstring or a `run_*.sh` here.

Old labels / prefixes: w, width

## Scripts

- `scripts/w_checks.py`: Checks on W2/W3 (added after review): (1) local area exponent drift for W2 chaotic turmites, k=22..24 vs 26..28; (2) aniso/fill at last checkpoint for W3 runs;
- `scripts/width_radius_refit.py`: Registered Wsurf versus radius refit; uv run experiments/archive/2026-10-w-width-radius-refit/scripts/width_radius_refit.py.

## Results

5 entries in `results/` (1 are `.log`/`.done` markers); csv/json/txt outputs, `*_stats.txt` hold the summaries quoted in the notes.
