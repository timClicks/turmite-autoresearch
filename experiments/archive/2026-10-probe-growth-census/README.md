# probe-growth-census

Migrated legacy investigation (2026-10-14). Its files used to sit in the flat `data/` directory (and `calib/`, `occ/`, `snaps/`, `dumps*`, `knock*` where listed) with the label prefix below; `experiments/_migration/map.tsv` gives the exact old -> new path of every file. This stub was generated from file names and script docstrings. It is **not** the original write-up: the question, timestamped hypotheses, commands and results are in `notes/` (mainly `notes/frontier-results.md`, `notes/frontier-status.md`, `notes/research-frontier*.md`; search for the label), and the producing command is usually in the script docstring or a `run_*.sh` here.

Old labels / prefixes: c, cube, growth, iso, long, pilot, probe, seed, sq

## Scripts

- `scripts/c_letters.py`: Item 3 / P2.1: how much of the rule-to-rule variation of c is carried by letters 1,2 vs later ones?
- `scripts/c_model.py`: Predict c from a rule's letters using the edge's chirality.
- `scripts/cube_fill.py`: Item 28 follow-up: local volume/extent exponents for cubic ants and the rotor3 control, plus V/E^3.
- `scripts/cube_stats.py`: Every number the "Why a cube root" section quotes, computed from the probe
- `scripts/sq_baseline_window.py`: Baseline for item 24: the square-lattice ants' area exponent in the SAME window (k=16..24, area at t=2^k)

## Results

17 entries in `results/` (0 are `.log`/`.done` markers); csv/json/txt outputs, `*_stats.txt` hold the summaries quoted in the notes.
