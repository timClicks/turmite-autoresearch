# w2

Migrated legacy investigation (2026-10-14). Its files used to sit in the flat `data/` directory (and `calib/`, `occ/`, `snaps/`, `dumps*`, `knock*` where listed) with the label prefix below; `experiments/_migration/map.tsv` gives the exact old -> new path of every file. This stub was generated from file names and script docstrings. It is **not** the original write-up: the question, timestamped hypotheses, commands and results are in `notes/` (mainly `notes/frontier-results.md`, `notes/frontier-status.md`, `notes/research-frontier*.md`; search for the label), and the producing command is usually in the script docstring or a `run_*.sh` here.

Old labels / prefixes: w2

## Scripts

- `scripts/w2_select.py`: W2 selection: 10 sqrt-class and 10 chaotic-class 2x2 turmite tables, seed 20261013, from the 2^20 screen.
- `scripts/w2_stats.py`: W2: visit-density profile of 2x2 turmites at 2^28 vs the uniform-occupancy formula (1/(1-a))(1-(r/R)^(2(1-a)/a)) with the run's own a (k=22..28)

## Results

5 entries in `results/` (2 are `.log`/`.done` markers); csv/json/txt outputs, `*_stats.txt` hold the summaries quoted in the notes.
