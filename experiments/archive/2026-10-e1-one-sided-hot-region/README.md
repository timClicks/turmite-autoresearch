# e1-one-sided-hot-region

Migrated legacy investigation (2026-10-14). Its files used to sit in the flat `data/` directory (and `calib/`, `occ/`, `snaps/`, `dumps*`, `knock*` where listed) with the label prefix below; `experiments/_migration/map.tsv` gives the exact old -> new path of every file. This stub was generated from file names and script docstrings. It is **not** the original write-up: the question, timestamped hypotheses, commands and results are in `notes/` (mainly `notes/frontier-results.md`, `notes/frontier-status.md`, `notes/research-frontier*.md`; search for the label), and the producing command is usually in the script docstring or a `run_*.sh` here.

Old labels / prefixes: dumps, e1, e1c, knock, run

## Scripts

- `scripts/e1_map.py`: E1: knockout coarse map on an arbitrary grid file (same protocol as knockout.py coarse: every 5x5 tile with >= 5 visited cells,
- `scripts/e1_rot_alignment.py`: E1 follow-up: why does the rotated-field coarse map show only 2 hot tiles (original: 11) although the rotated hot tiles have the same mean loss?
- `scripts/e1_rot_check.py`: E1 covariance check: the 11 hot 5x5 tiles of RRRRRLLLLLL (top-left (x,y)) become, in the field rotated 90 degrees clockwise ((x,y)->(-y,x)), the 5x5 tiles with 
- `scripts/e1_stats.py`: E1: TSAW (examples/tsaw.rs; experiments/archive/2026-10-e1-one-sided-hot-region/results/e1_tsaw.csv, tsaw 26 16384 < experiments/archive/2026-10-e1-one-sided-hot-region/r
- `scripts/e1c_stats.py`: E1c: Rayleigh test on lobe bearings across the tethered ages of RRRRRLLLLLL. Rule: notes/frontier-2026-10-13-results.md.
- `scripts/run_e1.sh`: E1: knockout map at other ages and with the field rotated 90 degrees (RRRRRLLLLLL). usage (WSL): RAYON_NUM_THREADS=1 bash experiments/2026-10-13-e1-one-sided-ho
- `scripts/run_e1c.sh`

## Results

11 entries in `results/` (5 are `.log`/`.done` markers); csv/json/txt outputs, `*_stats.txt` hold the summaries quoted in the notes.

## Bulk output (gitignored)

- `dumps_e1/`
- `knock_e1/`
