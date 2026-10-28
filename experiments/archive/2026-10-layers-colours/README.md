# layers-colours

Migrated legacy investigation (2026-10-14). Its files used to sit in the flat `data/` directory (and `calib/`, `occ/`, `snaps/`, `dumps*`, `knock*` where listed) with the label prefix below; `experiments/_migration/map.tsv` gives the exact old -> new path of every file. This stub was generated from file names and script docstrings. It is **not** the original write-up: the question, timestamped hypotheses, commands and results are in `notes/` (mainly `notes/frontier-results.md`, `notes/frontier-status.md`, `notes/research-frontier*.md`; search for the label), and the producing command is usually in the script docstring or a `run_*.sh` here.

Old labels / prefixes: layers

## Scripts

- `scripts/layers_census_c.py`: EXPLORATORY: how common is the 'crust' class? Proxy: census edge-entry probability c (probe_summary.csv), since all
- `scripts/layers_classes.py`: EXPLORATORY (added after seeing Arm A): do the 24 ants (12 extreme + 12 typical kappa) split into a 'crust' class
- `scripts/layers_select.py`: Arm A selection (notes/kappa-experiment-design.md): six lowest and six highest rule-mean kappa among rules with >= 6
- `scripts/layers_stats.py`: Arm A statistics. Input experiments/archive/2026-10-layers-colours/results/layers.csv (examples/layers.rs 26 8192 < experiments/archive/2026-10-layers-colours/results/lay
- `scripts/layers_stats_typical.py`: Arm A statistics. Input experiments/archive/2026-10-layers-colours/results/layers_typical.csv (examples/layers.rs 26 8192 < experiments/archive/2026-10-layers-colours/res

## Results

9 entries in `results/` (1 are `.log`/`.done` markers); csv/json/txt outputs, `*_stats.txt` hold the summaries quoted in the notes.
