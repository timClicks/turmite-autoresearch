# d2-three-dimensions

Migrated legacy investigation (2026-10-14). Its files used to sit in the flat `data/` directory (and `calib/`, `occ/`, `snaps/`, `dumps*`, `knock*` where listed) with the label prefix below; `experiments/_migration/map.tsv` gives the exact old -> new path of every file. This stub was generated from file names and script docstrings. It is **not** the original write-up: the question, timestamped hypotheses, commands and results are in `notes/` (mainly `notes/frontier-results.md`, `notes/frontier-status.md`, `notes/research-frontier*.md`; search for the label), and the producing command is usually in the script docstring or a `run_*.sh` here.

Old labels / prefixes: d2, d2c, run

## Scripts

- `scripts/d2_stats.py`: D2: 3D ants to 2^32. Input experiments/archive/2026-10-d2-three-dimensions/results/d2_cube.csv (spec,k,area=volume,extent; k=-1 marks leaving the box). Design/decisi
- `scripts/d2c_stats.py`: D2: 3D ants to 2^32. Input experiments/archive/2026-10-d2-three-dimensions/results/d2c_cube.csv (spec,k,area=volume,extent; k=-1 marks leaving the box). Design/decis
- `scripts/run_d2.sh`: D2: 3D ants to 2^32 in a 768^3 box. usage (WSL): CARGO_TARGET_DIR=~/turmite-target-frontier2 RAYON_NUM_THREADS=2 bash experiments/archive/2026-10-d2-three-dimensions
- `scripts/run_d2c.sh`

## Results

11 entries in `results/` (6 are `.log`/`.done` markers); csv/json/txt outputs, `*_stats.txt` hold the summaries quoted in the notes.
