# a1-kappa

Migrated legacy investigation (2026-10-14). Its files used to sit in the flat `data/` directory (and `calib/`, `occ/`, `snaps/`, `dumps*`, `knock*` where listed) with the label prefix below; `experiments/_migration/map.tsv` gives the exact old -> new path of every file. This stub was generated from file names and script docstrings. It is **not** the original write-up: the question, timestamped hypotheses, commands and results are in `notes/` (mainly `notes/frontier-results.md`, `notes/frontier-status.md`, `notes/research-frontier*.md`; search for the label), and the producing command is usually in the script docstring or a `run_*.sh` here.

Old labels / prefixes: a1, a1b, a1c, a1d

## Scripts

- `scripts/a1_edge_q.py`: A1, exploratory (not pre-registered): does the edge-weighted turn probability q_edge = sum_c share_boundary(c) * [rule[c] == R] explain kappa across the 40 mixi
- `scripts/a1_kappa_proxy.py`: A1 proxy (NOT the half-plane model): how much of the across-rule variance of kappa is carried by the rule string alone?
- `scripts/a1b_icc.py`: A1b: ICC of kappa across rules with 12 patched seeds per rule. Design/decision: notes/frontier-2026-10-13-results.md. usage: uv run experiments/2026-10-13-a1-ka
- `scripts/a1c_predict.py`: A1c (exploratory, after A1b): predict the rule-mean kappa (core band, b2_probe + item21 + patched rules, >= 6 runs) from the rule string.
- `scripts/a1d_stats.py`: A1d: probe statistics of the memoryless persistent walker (pw:Q:SEED).

## Results

7 entries in `results/` (0 are `.log`/`.done` markers); csv/json/txt outputs, `*_stats.txt` hold the summaries quoted in the notes.
