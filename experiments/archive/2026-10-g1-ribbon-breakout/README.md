# g1-ribbon-breakout

Migrated legacy investigation (2026-10-14). Its files used to sit in the flat `data/` directory (and `calib/`, `occ/`, `snaps/`, `dumps*`, `knock*` where listed) with the label prefix below; `experiments/_migration/map.tsv` gives the exact old -> new path of every file. This stub was generated from file names and script docstrings. It is **not** the original write-up: the question, timestamped hypotheses, commands and results are in `notes/` (mainly `notes/frontier-results.md`, `notes/frontier-status.md`, `notes/research-frontier*.md`; search for the label), and the producing command is usually in the script docstring or a `run_*.sh` here.

Old labels / prefixes: g1

## Scripts

- `scripts/g1_breakout_stats.py`: dependencies = ["polars", "numpy"]
- `scripts/g1_stats.py`: G1 analysis of experiments/archive/2026-10-g1-ribbon-breakout/results/g1_ribbon.csv (made by examples/ribbon_trace.rs). Predictions: notes/research-frontier-2026-10-

## Results

3 entries in `results/` (1 are `.log`/`.done` markers); csv/json/txt outputs, `*_stats.txt` hold the summaries quoted in the notes.

## 2026-10-15 21:22 NZDT: survivor comparison registration
Base commit da88e61b690507526ba4e2a2c017d9c7941beb91; existing dirty work is unrelated.
Before computing the comparison: use every chunk CSV with a sibling .done in
h1e10 and h1e11, separately (not the historical 240-rule subset). Escape means
stop=escaped and empty period; no claim of infinite-time nonperiodicity.
All runs are deterministic blank-board starts, no random seed.

Structural signature S: in complete 1M-step G1 windows, steps/new cell <8 AND
axis-aligned new-cell box aspect >=20. Predict >=90% of the previously defined
breakout windows (steps/new cell <10) satisfy S; <=5% of preceding complete fine
windows satisfy S. Calibration: a synthetic 40-by-10000 slab at 4 steps/cell
passes; a square at the same efficiency and a thin slow slab fail.
This is a window-box signature, not a measurement of individual stroke width.

Transfer prediction T: >=75% of no-highway escapes in EACH completed census
have whole-history box aspect >=2. This deliberately weaker census proxy tests
whether elongated territory is shared; it cannot validate S in another rule.
Compare against escaped recognised highways and budget survivors. Report all
rules, dimensions and prior-decade expansion ratios where available. RLRLLL
is a budget survivor at 1e10, so its later escape belongs to the 1e11 cohort.
No new multi-billion-step simulations are needed for this archival comparison.

Recipe: uv run experiments/archive/2026-10-g1-ribbon-breakout/scripts/compare_survivors.py
under WSL with UV_PROJECT_ENVIRONMENT=$HOME/.venvs/turmite UV_LINK_MODE=copy.
Outputs: results/survivor_comparison.json and results/survivor_geometry.csv.
Input SHA-256 hashes and script hash are stored in the JSON. Re-run must give
identical bytes. Historical generator: examples/ribbon_trace.rs (command in
notes/research-frontier-2026-10-13-pm.md G1); census: src/bin/sweep_lean.rs,
blank board, grid 32768, budgets 1e10/1e11, original logs beside chunks.

## 2026-10-15 archival outcome
S held: 281/298 complete breakout windows (94.3%), 0/676 preceding windows.
Median efficiency 4.022 steps/new cell; median transverse window box 54 cells;
the old <=12 prediction still fails (0/298). Partial final window excluded.
T failed: 0/37 h1e10 and 0/3 h1e11 no-highway escapes have global aspect >=2.
The completed h1e11 cohort is 324, not the historical 240 or planned 732.
Its three no-highway escapes are RLLLLRRL, RLLLLRLRRL, RLLLRLRLLL;
max-extent expansion relative to 1e10 is 1.1691, 2.1892, 8.5065.
RLRLLL is in h1e10/chunk_29.csv (3377 x 3250), and in h1e11/chunk_27.txt
without a completed CSV row. Its later evidence is the G1 trace, not a completed
h1e11 census record. Full per-rule comparisons and input hashes are in outputs.

Interpretation: the efficient narrow-window signature is descriptive evidence
for RLRLLL's phase switch, not an independently discovered mechanism. Global
aspect does not identify local ribbons: even recognised highways usually have
nearly square whole-history boxes at board escape. No shared local mechanism
has been established for the other survivors. Need local-window traces and
moving-frame recurrence tests, on larger boards, to distinguish parallel strokes
from periodic translation. No new simulations or causal claims.
Timestamp correction: registration's 21:22 was an estimated time; actual clock
was 21:19 after the first analysis. Tool order establishes registration before run.

## 2026-10-16: paper figure and recovered wake archive

Presentation work, base commit c9811f56911ff4e7fd8cfe5e76cd5d461968265b.
Recovered the original note and exporter from worktree-g1-builder-structure
(c82030e), and compact extracts/draft from worktree-paper-figure-proposals
(b7c55f9 plus its untracked files). The exporter is now
`examples/g1_ribbon_breakout_builder_dump.rs` (dynamics unchanged). Historical
paths in the recovered note refer to that old worktree; current commands follow.
Raw dumps are retained in this experiment's ignored `dumps/`. Their SHA-256
hashes match the recovered extract manifest. No new long ant run was needed.

From the repository root in WSL, after setting
`export UV_PROJECT_ENVIRONMENT=$HOME/.venvs/turmite UV_LINK_MODE=copy`:

```bash
# Long regeneration, if raw dumps are absent: run in the background.
nohup bash experiments/archive/2026-10-g1-ribbon-breakout/scripts/g1_builder_run.sh > experiments/archive/2026-10-g1-ribbon-breakout/results/g1_regenerate.log 2>&1 &
# Fast archival extraction (writes only this experiment's results):
uv run experiments/archive/2026-10-g1-ribbon-breakout/scripts/g1_wake_extract.py experiments/archive/2026-10-g1-ribbon-breakout/dumps
uv run research-outputs/working-papers/cube-root-growth/late_switch_figure.py
typst compile --root . research-outputs/working-papers/cube-root-growth/main.typ research-outputs/working-papers/cube-root-growth/main.pdf
# Optional PDF rendering/byte-repeat verification; pypdfium2 version is recorded:
uv run --with pypdfium2==5.14.0 experiments/archive/2026-10-g1-ribbon-breakout/scripts/verify_figure.py
```

Compact results are `g1_wake_extract.json`, `g1_wake_crop_*.csv`,
`g1_wake_shape_*.csv`, and `g1_sweep_trace_*.csv`. The paper script reads only
results, never raw dumps. Output PDF/PNG and `late_switch_numbers.json` live in
`research-outputs/working-papers/cube-root-growth/fig/`; that JSON hashes source and inputs.
No randomness: one blank-board RLRLLL trajectory, 32768 board; 400,000-step
windows at 12.8 and 12.9 billion steps. Wake snapshots are at each window's END;
trace sample 0 is the position after the first step of each window (an offset of
one step relative to the displayed elapsed-time origin, negligible here).

Reproduced comparisons: L=6400/8610, predicted d|x|²/dt=0.864883/0.835453,
measured 0.862245/0.832701. Use the original analysis's strict symmetric
+/-20,000,000-step window (39 samples), OLS slope of |x|, times 2|x(t0)|.
The draft used an alternative x² fit and an asymmetric endpoint inclusion;
we restored the original reported method. This is an archival consistency check,
not a changed scientific estimator or new evidence for a scaling law.
The wake figure uses the first 48 rows of the 36x80 extract, square cells,
unvisited white. Full extracted-wake lag-3 agreement is 0.994327/0.994538.
No between-seed uncertainty is estimable from this trajectory.

Validation: the compact CSVs regenerate byte-identically; raw hashes match.
`check_builder_dump.py` checks all sampled trajectory states and ALL wake bytes
against an independent obvious ant loop for all 28 rules of lengths 2--4,
2000 steps each; `results/builder_oracle_check.log` records success. Build the
exporter with `cargo build --release --example g1_ribbon_breakout_builder_dump`.
The full `cargo test --release` suite passed (`results/figure_release_tests.log`).
No instrument change; no new rotor calibration. The shareable notebook adds a
results-only figure section, executed via the command in
`scripts/update_figure_notebook.py`; execution log `results/figure_notebook.log`.
