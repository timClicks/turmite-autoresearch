# spread-home

Migrated legacy investigation (2026-10-14). Its files used to sit in the flat `data/` directory (and `calib/`, `occ/`, `snaps/`, `dumps*`, `knock*` where listed) with the label prefix below; `experiments/_migration/map.tsv` gives the exact old -> new path of every file. This stub was generated from file names and script docstrings. It is **not** the original write-up: the question, timestamped hypotheses, commands and results are in `notes/` (mainly `notes/frontier-results.md`, `notes/frontier-status.md`, `notes/research-frontier*.md`; search for the label), and the producing command is usually in the script docstring or a `run_*.sh` here.

Old labels / prefixes: spread

## Scripts

- `scripts/spread_clusters.py`: Review follow-up: the 560 tethered (log-class) rules share a few discrete spread values. Cluster spread_real (relative gap 2%) and describe the clusters.
- `scripts/spread_dups.py`: Review check: do different tethered rules share exactly equal spreads (a sign of shared orbits)?  Input experiments/archive/2026-10-tether-rules/results/tether_scree
- `scripts/spread_groups.py`: What labels the discrete home types?  Within-group spread of spread_real for groupings of the 556 tethered rules by simple rule invariants.

## Results

6 entries in `results/` (0 are `.log`/`.done` markers); csv/json/txt outputs, `*_stats.txt` hold the summaries quoted in the notes.
