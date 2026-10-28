# arm-kappa-depletion-arms

Migrated legacy investigation (2026-10-14). Its files used to sit in the flat `data/` directory (and `calib/`, `occ/`, `snaps/`, `dumps*`, `knock*` where listed) with the label prefix below; `experiments/_migration/map.tsv` gives the exact old -> new path of every file. This stub was generated from file names and script docstrings. It is **not** the original write-up: the question, timestamped hypotheses, commands and results are in `notes/` (mainly `notes/frontier-results.md`, `notes/frontier-status.md`, `notes/research-frontier*.md`; search for the label), and the producing command is usually in the script docstring or a `run_*.sh` here.

Old labels / prefixes: armb, armc

## Scripts

- `scripts/armb_stats.py`: Arm B (notes/kappa-experiment-design.md): noisy rotor. Input experiments/archive/2026-10-arm-kappa-depletion-arms/results/armb_probe.csv
- `scripts/armc_pairs.py`: Arm C feasibility (notes/kappa-experiment-design.md): pairs of rules with equal n and equal number of R, rule-mean c within
- `scripts/armc_stats.py`: Arm C: sign test of 'lower-kappa member of a matched pair has the larger depletion D = mean_{d=2..4}(1 - rho(d))'.

## Results

7 entries in `results/` (0 are `.log`/`.done` markers); csv/json/txt outputs, `*_stats.txt` hold the summaries quoted in the notes.
