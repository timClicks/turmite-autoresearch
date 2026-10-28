# h1-lacunarity-decomposition

Migrated legacy investigation (2026-10-14). Its files used to sit in the flat `data/` directory (and `calib/`, `occ/`, `snaps/`, `dumps*`, `knock*` where listed) with the label prefix below; `experiments/_migration/map.tsv` gives the exact old -> new path of every file. This stub was generated from file names and script docstrings. It is **not** the original write-up: the question, timestamped hypotheses, commands and results are in `notes/` (mainly `notes/frontier-results.md`, `notes/frontier-status.md`, `notes/research-frontier*.md`; search for the label), and the producing command is usually in the script docstring or a `run_*.sh` here.

Old labels / prefixes: h1, run

## Scripts

- `scripts/h1_decomp.py`: dependencies = ["polars", "numpy", "scipy"]
- `scripts/h1_lacunarity.py`: H1 (research-frontier-2026-10-13-pm.md): is the rule-specific part of the area exponent carried by drift of the filling fraction eta = A/(W_x W_y)?
- `scripts/run_1e10.sh`: Item 17: push the length<=10 primitive rules still unresolved at 1e9 to 1e10 steps (lean ant, grid 32768).
- `scripts/run_1e11.sh`: B5 (frontier 2026-10-13): first 240 rules (in the fixed-seed shuffled chunk order of run_1e10.sh)
- `scripts/run_1e11b.sh`: B5 extension (2026-10-13): the remaining survivors of the 1e10 run (list positions 241..), same protocol as run_1e11.sh, chunks 20.. .

## Results

1 entries in `results/` (0 are `.log`/`.done` markers); csv/json/txt outputs, `*_stats.txt` hold the summaries quoted in the notes.
