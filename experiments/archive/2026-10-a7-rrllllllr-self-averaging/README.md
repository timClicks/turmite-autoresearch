# a7-rrllllllr-self-averaging

Migrated legacy investigation (2026-10-14). Its files used to sit in the flat `data/` directory (and `calib/`, `occ/`, `snaps/`, `dumps*`, `knock*` where listed) with the label prefix below; `experiments/_migration/map.tsv` gives the exact old -> new path of every file. This stub was generated from file names and script docstrings. It is **not** the original write-up: the question, timestamped hypotheses, commands and results are in `notes/` (mainly `notes/frontier-results.md`, `notes/frontier-status.md`, `notes/research-frontier*.md`; search for the label), and the producing command is usually in the script docstring or a `run_*.sh` here.

Old labels / prefixes: a7, a7c, run

## Scripts

- `scripts/a7_census.py`: A7-next: which rules have a rising seed-to-seed CV of A/t^(2/3)? Design and prediction: notes/frontier-2026-10-13-results.md. usage: uv run experiments/2026-10-
- `scripts/a7_stats.py`: A7: is RRLLLLLLR@seed non-self-averaging? Input experiments/archive/2026-10-a7-rrllllllr-self-averaging/results/a7_probe.csv (200 seeds 25..224, probe to 2^30) plus,
- `scripts/a7c_stats.py`: A7c: RRLLLLLLR to 2^32, 64 new seeds. Rule: notes/frontier-2026-10-13-results.md.
- `scripts/run_a7c.sh`

## Results

12 entries in `results/` (5 are `.log`/`.done` markers); csv/json/txt outputs, `*_stats.txt` hold the summaries quoted in the notes.
