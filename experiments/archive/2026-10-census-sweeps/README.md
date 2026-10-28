# census-sweeps

Migrated legacy investigation (2026-10-14). Its files used to sit in the flat `data/` directory (and `calib/`, `occ/`, `snaps/`, `dumps*`, `knock*` where listed) with the label prefix below; `experiments/_migration/map.tsv` gives the exact old -> new path of every file. This stub was generated from file names and script docstrings. It is **not** the original write-up: the question, timestamped hypotheses, commands and results are in `notes/` (mainly `notes/frontier-results.md`, `notes/frontier-status.md`, `notes/research-frontier*.md`; search for the label), and the producing command is usually in the script docstring or a `run_*.sh` here.

Old labels / prefixes: 1B, census, confirmed, equiv, non, regen, sweep, unresolved, v2

## Scripts

- `scripts/census.py`
- `scripts/equiv_census.py`: Frontier item 23: how many census rules are exact repeats u^k of a shorter
- `scripts/regen_frontier_stats.sh`: Regenerates every analysis text output of the frontier work from the raw data files (deterministic; run twice and diff to check).

## Results

13 entries in `results/` (1 are `.log`/`.done` markers); csv/json/txt outputs, `*_stats.txt` hold the summaries quoted in the notes.
