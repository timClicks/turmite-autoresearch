# c2-arrow-bias

Migrated legacy investigation (2026-10-14). Its files used to sit in the flat `data/` directory (and `calib/`, `occ/`, `snaps/`, `dumps*`, `knock*` where listed) with the label prefix below; `experiments/_migration/map.tsv` gives the exact old -> new path of every file. This stub was generated from file names and script docstrings. It is **not** the original write-up: the question, timestamped hypotheses, commands and results are in `notes/` (mainly `notes/frontier-results.md`, `notes/frontier-status.md`, `notes/research-frontier*.md`; search for the label), and the producing command is usually in the script docstring or a `run_*.sh` here.

Old labels / prefixes: c2, c2b, c2c, escape, run

## Scripts

- `scripts/c2_escape.py`: C2 follow-up: all biased-arrow runs left the 8192 board, so per-run exponents over k=20..26 do not exist.
- `scripts/c2_stats.py`: C2: rotor with north-biased initial arrows. Input experiments/archive/2026-10-c2-arrow-bias/results/c2_probe.csv. Decision rule in notes/frontier-2026-10-13-results.
- `scripts/c2b_escape.py`: C2b: biased-arrow runs (small biases, grid 32768); original text: all biased-arrow runs left the 8192 board, so per-run exponents over k=20..26 do not exist.
- `scripts/c2b_stats.py`: C2: rotor with north-biased initial arrows. Input experiments/archive/2026-10-c2-arrow-bias/results/c2b_probe.csv. Decision rule in notes/frontier-2026-10-13-results
- `scripts/c2c_escape.py`: C2 follow-up: all biased-arrow runs left the 8192 board, so per-run exponents over k=20..26 do not exist.
- `scripts/run_c2.sh`: C2: biased-arrow rotor vs unbiased control. usage (WSL): RAYON_NUM_THREADS=1 bash experiments/archive/2026-10-c2-arrow-bias/scripts/run_c2.sh
- `scripts/run_c2b.sh`: C2b: small biases on a larger grid. usage (WSL): RAYON_NUM_THREADS=1 bash experiments/archive/2026-10-c2-arrow-bias/scripts/run_c2b.sh
- `scripts/run_c2c.sh`: C2c: bias 0.2, 0.25, 0.3 on a 32768 board. usage (WSL): RAYON_NUM_THREADS=3 bash experiments/archive/2026-10-c2-arrow-bias/scripts/run_c2c.sh

## Results

21 entries in `results/` (9 are `.log`/`.done` markers); csv/json/txt outputs, `*_stats.txt` hold the summaries quoted in the notes.
