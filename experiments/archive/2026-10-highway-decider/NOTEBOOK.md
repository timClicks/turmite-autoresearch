# Lab notebook: translated-cycler decider for census highways

Append-only. Newest entry last. Never edit an old entry; correct it with a new one (`corrects: <timestamp>`).

### 2026-10-23 18:12 (+13:00) · 6e0840b · intent
Give the census highways a configuration-level persistence certificate (README). Informs whether proof-track item 2 has a census-wide decider and
whether any census label is an impostor.

### 2026-10-23 18:12 (+13:00) · 6e0840b · decision
Pruning preflight at `6e0840bb05a1aa261c13ee1a0019550c0e92aac0`: queries and result in the README; no applicable signature; run, within the stated budget.
Timestamps in this notebook are read from the clock (`date`), unlike some first entries of the sibling experiment (corrected there).

### 2026-10-23 18:27 +1300 · 354eab7 · observation
Full run (registered predictions D1-D5; controls and C5 run before the summary was read): 571 of 571 census highways certified (568 at K = 3); C4 0 pre-onset certificates; C1-C3 all rejected (50/50, 38/38, 50/50); C5 0 of 72,864 candidates in 100 non-highway rules; 0 oracle disagreements in 3,423 dumps. Details and caveats in the README; `results/summary.txt`.

### 2026-10-23 18:27 +1300 · 354eab7 · deviation
(1) The post-registration extras: 50 additional non-highway rules in C5 and the from-zero verification (408 rules, new binary). (2) I hand-replaced the driver's wrong TOTAL line in `results/verify_from_zero.txt` (case-sensitivity bug in my one-off driver); the 408 per-rule lines are unchanged. (3) 3 dumps at K = 300 missing (board edge), not failures.

### 2026-10-23 18:45 +1300 · 597689e · deviation
Builds of this experiment's examples (WSL, fresh target directories, recorded sha256 in results/) were made from a working tree in which other sessions were editing `src/lean.rs`, `src/lib.rs` (adds `pub mod tiled`), `src/bin/sweep_lean.rs` and `src/tiled.rs` at the same time (file times 18:23-18:43; uncommitted). The examples here use only `Rule`, `DIRS` and `reference::Ant`, whose files are unchanged in git; the oracle and the 408-rule from-zero check compare against `reference::Ant` and `fast::run` as built then. I did not rebuild from a clean checkout of a single commit for every run; the stage-1 binary record says `dirty=0` for `examples/` and `src/` at `6ecd317` (its build preceded those edits).
Shareable `notebook.ipynb` built by `scripts/build_notebook.py` and executed from committed results (uv, WSL).

### 2026-10-23 18:49 +1300 · 652e517 · deviation
corrects: the "18:12" timestamps in the first two entries and the README header (registration commit `220aac1` is 18:11:47) and the 18:27 observation time (commit `cd802ed` is 18:27:23, fine) — only the first two were wrong. The hand-replaced TOTAL line of `results/verify_from_zero.txt` was removed by regenerating the file with `scripts/verify_from_zero.py` (408 of 408 identical). Falsification-harness disclosure and pruning-index outcome added to the README.
