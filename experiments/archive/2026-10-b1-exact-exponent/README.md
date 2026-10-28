# b1-exact-exponent

Migrated legacy investigation (2026-10-14). Its files used to sit in the flat `data/` directory (and `calib/`, `occ/`, `snaps/`, `dumps*`, `knock*` where listed) with the label prefix below; `experiments/_migration/map.tsv` gives the exact old -> new path of every file. This stub was generated from file names and script docstrings. It is **not** the original write-up: the question, timestamped hypotheses, commands and results are in `notes/` (mainly `notes/frontier-results.md`, `notes/frontier-status.md`, `notes/research-frontier*.md`; search for the label), and the producing command is usually in the script docstring or a `run_*.sh` here.

Old labels / prefixes: b1, b1b, run

## Scripts

- `scripts/b1_select.py`: B1/A2/A4 rule set: the 6 rules already run to 2^32 (experiments/archive/2026-10-probe-growth-census/results/long.csv) + the 11 item-4 rules (13 distinct after overla
- `scripts/b1_stats.py`: B1 and A2: 20 ants + 8 rotors run to 2^34 (experiments/archive/2026-10-b1-exact-exponent/results/b1_probe_NN.csv). Design and decision rules: notes/frontier-2026-10-
- `scripts/b1b_stats.py`: B1b: patched-start ants to 2^34 (seeds 301-303), criterion vs the rotor (mean 0.6676, seed sd 0.0063): |mean a_inf - 0.6676| < 0.0145. Design: notes/frontier-20
- `scripts/run_b1.sh`: B1/A2: 20 ants + 8 rotors to 2^34. usage (WSL): RAYON_NUM_THREADS=3 bash experiments/archive/2026-10-b1-exact-exponent/scripts/run_b1.sh
- `scripts/run_b1b.sh`

## Results

46 entries in `results/` (22 are `.log`/`.done` markers); csv/json/txt outputs, `*_stats.txt` hold the summaries quoted in the notes.
