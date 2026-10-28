# e3-route-collinearity

Migrated legacy investigation (2026-10-14). Its files used to sit in the flat `data/` directory (and `calib/`, `occ/`, `snaps/`, `dumps*`, `knock*` where listed) with the label prefix below; `experiments/_migration/map.tsv` gives the exact old -> new path of every file. This stub was generated from file names and script docstrings. It is **not** the original write-up: the question, timestamped hypotheses, commands and results are in `notes/` (mainly `notes/frontier-results.md`, `notes/frontier-status.md`, `notes/research-frontier*.md`; search for the label), and the producing command is usually in the script docstring or a `run_*.sh` here.

Old labels / prefixes: e3, e3b, run

## Scripts

- `scripts/e3_stats.py`: E3: homeward-leg counts (ret.u32) vs knockout loss, controlling for occupancy, distance and dose. Decision rule: notes/frontier-2026-10-13-results.md.
- `scripts/e3b_jobs.py`: E3b job lists: strat2 jobs, 60 draws x class {0,1} x route quartile {0..3}, 25 cells each. Writes experiments/archive/2026-10-knockout-maps/knock/RULE/e3b.jobs.
- `scripts/e3b_stats.py`: E3b: loss for homeward-dominant vs outward-dominant excursion cells at equal route-count quartile. Decision rules: notes/frontier-2026-10-13-results.md. usage: 
- `scripts/run_e3b.sh`

## Results

4 entries in `results/` (2 are `.log`/`.done` markers); csv/json/txt outputs, `*_stats.txt` hold the summaries quoted in the notes.
