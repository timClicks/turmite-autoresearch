# b3-long-rules

Migrated legacy investigation (2026-10-14). Its files used to sit in the flat `data/` directory (and `calib/`, `occ/`, `snaps/`, `dumps*`, `knock*` where listed) with the label prefix below; `experiments/_migration/map.tsv` gives the exact old -> new path of every file. This stub was generated from file names and script docstrings. It is **not** the original write-up: the question, timestamped hypotheses, commands and results are in `notes/` (mainly `notes/frontier-results.md`, `notes/frontier-status.md`, `notes/research-frontier*.md`; search for the label), and the producing command is usually in the script docstring or a `run_*.sh` here.

Old labels / prefixes: b3

## Scripts

- `scripts/b3_sample.py`: B3: random rules of length 10,12 (controls),14,16,20,24; 200 each; uniform over strings starting with R; seed 20261013.
- `scripts/b3_stats.py`: B3: rule-length extension. Input experiments/archive/2026-10-b3-long-rules/results/b3_probe.csv (probe to 2^27). Decision rule: notes/frontier-2026-10-13-results.md.

## Results

5 entries in `results/` (2 are `.log`/`.done` markers); csv/json/txt outputs, `*_stats.txt` hold the summaries quoted in the notes.
