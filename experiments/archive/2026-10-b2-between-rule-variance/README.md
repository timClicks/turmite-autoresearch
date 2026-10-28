# b2-between-rule-variance

Migrated legacy investigation (2026-10-14). Its files used to sit in the flat `data/` directory (and `calib/`, `occ/`, `snaps/`, `dumps*`, `knock*` where listed) with the label prefix below; `experiments/_migration/map.tsv` gives the exact old -> new path of every file. This stub was generated from file names and script docstrings. It is **not** the original write-up: the question, timestamped hypotheses, commands and results are in `notes/` (mainly `notes/frontier-results.md`, `notes/frontier-status.md`, `notes/research-frontier*.md`; search for the label), and the producing command is usually in the script docstring or a `run_*.sh` here.

Old labels / prefixes: b2, b2b, run

## Scripts

- `scripts/b2_anova.py`: Within-rule vs between-rule scatter of fitted exponents.
- `scripts/b2_sample.py`: B2: 100 random non-bursty blob rules (numpy seed 20261013), disjoint from the 40 rules of experiments/archive/2026-10-patched-starts/results/patched.csv, 12 patched 
- `scripts/b2b_anova.py`: Within-rule vs between-rule scatter of fitted exponents.
- `scripts/run_b2b.sh`

## Results

14 entries in `results/` (5 are `.log`/`.done` markers); csv/json/txt outputs, `*_stats.txt` hold the summaries quoted in the notes.
