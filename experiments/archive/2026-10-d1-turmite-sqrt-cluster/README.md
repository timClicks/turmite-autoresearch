# d1-turmite-sqrt-cluster

Migrated legacy investigation (2026-10-14). Its files used to sit in the flat `data/` directory (and `calib/`, `occ/`, `snaps/`, `dumps*`, `knock*` where listed) with the label prefix below; `experiments/_migration/map.tsv` gives the exact old -> new path of every file. This stub was generated from file names and script docstrings. It is **not** the original write-up: the question, timestamped hypotheses, commands and results are in `notes/` (mainly `notes/frontier-results.md`, `notes/frontier-status.md`, `notes/research-frontier*.md`; search for the label), and the producing command is usually in the script docstring or a `run_*.sh` here.

Old labels / prefixes: d1, d1b, run

## Scripts

- `scripts/d1_tables.py`: D1: table features of the sqrt(t) turmite cluster vs the cube-root-like cluster. Design and decision rule: notes/frontier-2026-10-13-results.md.
- `scripts/d1b_specs.py`: dependencies = ["numpy"]
- `scripts/d1b_stats.py`: D1b: 2-state 3-colour random tables: classes, 'state 0 never leaves state 0' enrichment, single-feature AUCs, area/extent^2. Design/prediction: notes/frontier-2
- `scripts/run_d1b.sh`

## Results

8 entries in `results/` (3 are `.log`/`.done` markers); csv/json/txt outputs, `*_stats.txt` hold the summaries quoted in the notes.
