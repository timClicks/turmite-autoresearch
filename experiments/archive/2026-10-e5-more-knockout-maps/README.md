# e5-more-knockout-maps

Migrated legacy investigation (2026-10-14). Its files used to sit in the flat `data/` directory (and `calib/`, `occ/`, `snaps/`, `dumps*`, `knock*` where listed) with the label prefix below; `experiments/_migration/map.tsv` gives the exact old -> new path of every file. This stub was generated from file names and script docstrings. It is **not** the original write-up: the question, timestamped hypotheses, commands and results are in `notes/` (mainly `notes/frontier-results.md`, `notes/frontier-status.md`, `notes/research-frontier*.md`; search for the label), and the producing command is usually in the script docstring or a `run_*.sh` here.

Old labels / prefixes: dumps, e5, knock, run

## Scripts

- `scripts/e5_map.py`: E5: knockout coarse map (E1 script plus a tile-origin offset env OFFX/OFFY) (same protocol as knockout.py coarse: every 5x5 tile with >= 5 visited cells,
- `scripts/e5_select.py`: E5 rule selection: tethered rules (all rules of experiments/archive/2026-10-tether-rules/results/tether_screen.csv) from spread clusters (2% gap, as spread_clusters.
- `scripts/e5_stats.py`: E5: knockout maps on more tethered rules and a shifted tile origin. Inputs experiments/archive/2026-10-e5-more-knockout-maps/knock_e5/*/{base.csv,coarse.csv} (+ the 
- `scripts/run_e5.sh`: E5: knockout maps on 6 more tethered rules (experiments/archive/2026-10-e5-more-knockout-maps/results/e5_rules.txt, 2^24 dumps) + RRRRRLLLLLL with the tile origin sh

## Results

4 entries in `results/` (2 are `.log`/`.done` markers); csv/json/txt outputs, `*_stats.txt` hold the summaries quoted in the notes.

## Bulk output (gitignored)

- `dumps_e5/`
- `knock_e5/`
