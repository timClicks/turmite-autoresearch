# Lab notebook: Q33 active cap crossover

Append-only. New entries go last. No empirical walker data exist.

## 2026-10-29 UTC · base 8904956fbb5a0e3bce676a39e92f4543f3774c5f · intent

User requested a developed design pushed to proposed/. This proposal follows the homepage, First steps onto fresh ground (26 October), The wall is a bound, not a direction (28 October), wall-vs-memory Stages 3–3c, and the Rev3 time-weighted instrument's passing calibration. Earlier local-only feasibility notes are background, not runs of this intervention.

## 2026-10-29 UTC · same base · interpretation

The proposed random-RLU cap is exponentially unlikely to activate at large m; the own-colour-zero policy closes a square before large caps. Those identities do not test a width crossover. Fix a highly straight-biased fresh policy and vary only its cap, with a coupled uncapped control. The flat-plane all-straight branch derives an order-m penetration scale, but ant geometry may suppress it.

## 2026-10-29 UTC · same base · decision

Register gated calibration and a separately frozen confirmation plan. Preserve the old porous-band prediction as a separately scored conjecture; do not assume it transfers to straight-biased motion. No implementation, pilot or confirmation is run in this proposal. The proposed bucket is intentional.

## 2026-10-29 UTC · same base · decision

Pruning preflight: GitHub connector inspection of all seven entry scopes and amendments at the base revision; concepts fresh/cap/bounded/crossover/porous/compact/penetration/excursion. Relevant IDs NR-20261026-wall-vs-memory-no-wall-porous, NR-20261028-wall-vs-memory-bounded-random-fresh-compact, NR-20261027-reflecting-cup-d-calibrator and NR-20261028-excursion-score-compact-d-calibrators. Their exact old walker/Score predicates do not cover the new policy. Other three entries cover invariants, crawler mutants and exposure-class tests. Decision propose; no exclusions or empirical pruning signatures. Full local rg audit and actual specs remain pre-execution requirements.

## 2026-10-29 UTC · same base · assumption

Fixed-q persistent-fresh policy may have a useful non-ordered late regime. It may instead crystallise or lack early/late scale coverage. G2/G3 decide adequacy on excluded data; their failure stops confirmation under this design. Budget: eight-rule excluded pilot through 2^24, then only after a new freeze 200 rules x ten arms through 2^31 with a 24-hour production stop. No changes to Q38/Q39 or deferred programmes.


## 2026-10-29 UTC · proposal head feb6b96c622d0b38d46532eef2975e5f4c47348a · intent

User suggested Python simulation tools for machines without Rust. Add a reusable stdlib sparse simulator, experiment-local PEP 723 CLI and independent visit-count/vector-turn oracle tests. Preserve all registered predictions and gates; no registered calibration, pilot or confirmation is run.

## 2026-10-29 UTC · same parent · observation

Technical checks: `UV_CACHE_DIR=/tmp/q33-uv-cache uv run --offline --script experiments/proposed/2026-10-q33-cap-crossover/scripts/test_python_sim.py` passed all 14 tests under Python 3.12.14 and uv 0.12.23. Cases include RNG fixtures, small-rule/seeded oracle comparisons, colour-zero revisits, origin and cap bounds, incremental/rescan geometry, synthetic exponents, incomplete windows, checkpoint resume and CLI resource handling. CLI subprocess runs are disposable correctness fixtures, not growth evidence; no outputs are added to results/.

## 2026-10-29 UTC · same parent · decision

PEP 723 dependencies=[] avoids installing the heavy root analysis environment. New runs write only inside this experiment and never overwrite an existing run directory. Record source/output hashes and explicit resource statuses. Rust execution remains unavailable, so Rust/Python equivalence, production throughput, crystallisation detection, pre-entry depth and Rev3 boundary-excursion instrumentation are not claimed. The independent RLRLLL checker is unchanged. Proposal remains in proposed/.

## 2026-11-03 UTC · PR #33 parent e414f09cc6fe86dcacacb4ef1fe17c51973335ec · observation

Validation of the cap-counter regression test (PR #33) and the review's follow-ups. The Oracle in `scripts/test_python_sim.py` now counts `cap_turns` / `cap_turns_nonorigin` itself in the branch that sets `turn = "U"`, so expected counts no longer come from a restated cap rule in the test body; the stepwise oracle test compares both counters for every case it covers; the counter test now spans seeds 7 and 1729 and caps None, 1, 4, 16, 32 (cap None must give zero interventions; every finite cap must exercise both origin and non-origin classes). Seeds 7 and 1729 are not reserved seeds. Suite: still 15 tests (the counter test was strengthened in place, the earlier 14-test entry stands for its head), all OK under Python 3.13.5 and uv 0.13.6 with `uv run --offline --script experiments/proposed/2026-10-q33-cap-crossover/scripts/test_python_sim.py`.

Mutation check, each mutant applied in turn to `experiments/_lib/turmite_sim.py` and reverted (file restored from a copy, `git status` clean for that file afterwards): `cap_turns_nonorigin += 1` FAILED (17 failures); non-origin increment deleted FAILED (17); `+= self.origin_run` (inverted) FAILED (17); `cap_turns += 1` deleted FAILED (17 failures, 1 error); `run_length > cap` (off by one) FAILED (18). An earlier automated review on e414f09 recorded the same mutants surviving the PR #31 base suite (first three) and being killed by e414f09. No scientific measurement, prediction, gate or reserved seed is touched; nothing is added to results/.

## 2026-11-04 20:03 UTC · base 21c9092 · intent

Daily progress session. Address the mechanical "should fix" items of the 2026-10-31 PR #31 review in a stacked PR, without changing any prediction band or gate: pin sample lists from the committed frame, state the probe area mapping, register an integer sub-octave schedule, add git provenance, and answer the reviewer's origin-exception question with a stated prediction (README Amendment A1, item 5) before running its test. P3 discrimination and the D metric need a design decision and are left open. No walker growth data will be produced.

## 2026-11-04 20:04 UTC · parent 7e9feb4 · observation

`uv run --offline --script experiments/proposed/2026-10-q33-cap-crossover/scripts/test_python_sim.py`: 17/17 OK (uv-managed Python, Linux box). New tests: (a) origin-run bound, Amendment A1 item 5: prediction **held**: origin run <= m for all m in 2..16, seeds 0..63, rules RLL and RLLR; m = 1 reached length 2 in at least one trajectory. So the m + 1 exception is only reachable at m = 1, and tests of it should target m = 1. (b) Sub-octave schedule equals the integer 8th-root table `inputs/schedule.tsv` for every time up to 2^31; the floating-point formula agreed with the exact integers for all k < 32, j < 8. (c) `pin_samples.py --check` regenerates the committed lists. The excluded-pilot list matches, in order, the eight rules the 2026-10-31 reviewer derived independently; confirmation lengths are 3 (1 rule) and 7-12 (199 rules), also as the reviewer reported. Frame sha256 `c76c7927…32cb5d`, 3055 rows, 2630 blob, 2630 unique.

## 2026-11-04 20:04 UTC · same parent · deviation

The first run of test (b) failed because the test compared against table entries above 2^31 (k = 31, j >= 1); a test bug, not a schedule mismatch. Fixed by restricting the table to times <= 2^31, then 17/17 passed. CLI provenance now records `git_commit` and `git_dirty`; checked on a disposable 4096-step run whose output was deleted.

## 2026-11-04 20:04 UTC · same parent · decision

Open, needing a design choice by the user or the proposal's author: review item 3 (P3 may not discriminate H-scale from H-local; reviewer suggests a registered uncapped-arm alpha_A expectation and/or a between-cap contrast at fixed W/m) and item 6 (metric and reference point for depth D). Also still owed before G0: overlap record with previously studied rules, a full local pruning-index rg audit, items 10-12 of the review. No walker growth data were produced.

## 2026-11-05 ~13:50 NZDT · parent ec20c3a · intent

Periodic proactive session. Complete G0 hygiene still owed after A1: overlap record, full local pruning-index rg audit, and the remaining mechanical review items that need no design choice (memory budget plan, "first two" wording, draft blog commit-pinned URL). Items 3 and 6 stay open. No walker growth data.

## 2026-11-05 ~13:50 NZDT · same parent · observation

Local `rg -il` over `notes/pruning-index/entries/` with concepts cap|fresh|crossover|penetration|persistent|bound|porous|compact|excursion matched six of seven entries; additive-laws missed (invariant scope only). Each matched membership predicate was read; none covers the new S/R/L + finite-cap policy. Overlap script against curated study cohorts (not the blob census): 5/8 pilot and 58/200 confirm rules appear in at least one prior study; written to `inputs/overlap.tsv` (74 data rows).

## 2026-11-05 ~13:50 NZDT · same parent · decision

Record as Amendment A2. Default uncapped memory plan is sequential + fail-loud until pilot A(t) exists. Do not invent P3 or D-metric choices. Still open before a scientific run: items 3 and 6, and G0 instrument/oracle completeness beyond this hygiene.

## 2026-11-06 09:10 NZDT · parent 9dabfd9 · intent

Daily progress run. Address the mechanical "should fix" items of the 2026-11-05 PR #34 review as Amendment A3, without changing any prediction band or gate and without deciding open items 3 (P3 discrimination) or 6 (D metric). Fix git_dirty sampling, commit regeneratable overlap.py with crystallisation-relevant cohorts and onset columns, correct A1 item-5 timing wording and the claims-to-predictions mapping, sharpen the origin-run assertions (registered in A3 before the test edit), and record the literal pruning rule-string query.

## 2026-11-06 09:11 NZDT · parent 21b3b22 · observation

`uv run --offline --script experiments/proposed/2026-10-q33-cap-crossover/scripts/test_python_sim.py`: **18/18 OK** (uv-managed Python, Linux box). Includes sharpened origin-run assertions (A3 item 5 **held**: m=1 always 2; max origin run == m for each m in 2..16 over the A1 grid) and `overlap.py --check`. Overlap summary:
```
rows=115 pilot_distinct=5/8 confirm_distinct=78/200 distinct=83 onset_lt_2_31_distinct=1
overlap.tsv: OK
```
`git_dirty` check: disposable 4096-step persistent-fresh runs with `--output-dir` under `results/` and under `scratch/` on a clean tracked tree both recorded `git_dirty: false`; outputs deleted afterwards. Literal pruning rule-string query `rg -w -F -f <208 Q33 rules> notes/pruning-index/entries` → 0 matches. Index files last changed at `cc7a885`.

## 2026-11-06 09:11 NZDT · same parent · decision

Record checks as Amendment A3 fulfilment on PR #34. Leave P3 discrimination and D metric for the user. Do not start G0, pilot or confirmation. No walker growth data.

## 2026-11-07 15:08 NZDT · parent 1128767 · intent

Periodic proactive session. Address the remaining mechanical "should fix" from the 2026-11-06 follow-up review of PR #34 as Amendment A4: add the census `confirmed_1B.csv` and highway-preconditions `highway_specs.txt` onset tables to `ONSET_SOURCES` so confirmation rule `RRRRRRRLR` (onset 756289068 < 2^31) is flagged. No prediction/gate changes; items 3 and 6 stay open for the user. No walker growth data.

## 2026-11-07 15:08 NZDT · parent 4842f0b · observation

`uv run --offline --script experiments/proposed/2026-10-q33-cap-crossover/scripts/test_python_sim.py`: **18/18 OK**. `overlap.py --check --summary`:
```
rows=115 pilot_distinct=5/8 confirm_distinct=78/200 distinct=83 onset_lt_2_31_distinct=2
overlap.tsv: OK
```
`RRRRRRRLR` now has `known_onset=756289068` and `onset_lt_2_31=yes` on its highway-preconditions overlap row (earliest onset from census `confirmed_1B.csv` and `highway_specs.txt`, both 756289068). `RRLRLRL` remains the other in-horizon onset. Cohort membership row counts unchanged (115). Inclusion unchanged.

## 2026-11-07 15:08 NZDT · same parent · decision

Record as Amendment A4 fulfilment on PR #34. Leave P3 discrimination and D metric for the user. Do not start G0, pilot or confirmation. No walker growth data.

## 2026-11-07 19:00 NZDT · parent 8a74ef2 · intent

Periodic proactive session. Finish the remaining mechanical "should fix" items from the 2026-11-06 follow-up review of PR #34 as Amendment A5: require `--write` to rewrite `overlap.tsv`, keep untracked files in the `git_dirty` check (still sampled before mkdir), correct the 24–32 B/cell attribution (tiled DESIGN ≈1 B/cell; Python dict is the larger guess), and relabel A3 item-5 origin sharpening as observation-not-prediction. No prediction/gate changes; items 3 and 6 stay open. No walker growth data.

## 2026-11-07 19:01 NZDT · parent 1c9d04f · observation

`uv run --offline --script experiments/proposed/2026-10-q33-cap-crossover/scripts/test_python_sim.py`: **18/18 OK**. `overlap.py --check --summary`: rows=115, onset_lt_2_31_distinct=2, overlap.tsv OK. Manual gate: differing committed file without `--write` exits 1 with "refuse rewrite"; with `--write` rewrites. Disposable 4096-step persistent-fresh run under `scratch/` on a tree with only the A5 script edits staged recorded `git_dirty: true` as expected (tracked modifications); outputs deleted. No walker growth data.

## 2026-11-07 19:00 NZDT · parent 8a74ef2 · decision

Record as Amendment A5 on PR #34 once the suite and `overlap.py --check` pass. Leave P3 discrimination and D metric for the user. Do not start G0, pilot or confirmation.

## 2026-11-08 11:27 NZDT · parent 8010f19 · deviation

The 2026-11-07 follow-up review of PR #34 found that the A5 checks commit (`8010f19`) rewrote a NOTEBOOK entry already committed in the A5 registration (`1c9d04f`). Original placeholder text at that entry (quoted, not restored): "Checks pending in the same session after the A5 registration commit." AGENTS.md requires corrections as new entries; this deviation records the edit. Pattern going forward: commit only `intent` (and `decision` if needed) with the registration, then append the observation after the check. The A5 `decision` entry timed 19:00 NZDT also sat after the 19:01 observation; leave historical order as committed.

## 2026-11-08 11:27 NZDT · parent 8010f19 · intent

Periodic proactive session. Address the remaining mechanical "should fix" items from the 2026-11-07 follow-up review of PR #34 as Amendment A6: (1) this deviation entry for the A5 NOTEBOOK rewrite; (2) correct tiled and Python memory planning figures (tiled = tiles_touched × bytes_per_tile; Python dict measured ~162 B/cell); (3) exclude this experiment's `results/` and `scratch/` from `git_dirty` so chunked `--resume` under `results/` stays informative; plus minors: assert `RRRRRRRLR` / `onset_lt_2_31_distinct=2` in the unit test, make `overlap.py --check` and `--write` mutually exclusive, refresh the PR title/body through A6. No prediction/gate changes; items 3 and 6 stay open for the user. No walker growth data.

## 2026-11-08 11:27 NZDT · parent 8010f19 · decision

Record as Amendment A6 on PR #34 once the suite and overlap check pass. Leave P3 discrimination and D metric for the user. Do not start G0, pilot or confirmation. Do not resolve `notes/ACTIVE.md` three-way conflicts here.

## 2026-11-08 11:28 NZDT · parent d76c1e1 · observation

`uv run --offline --script experiments/proposed/2026-10-q33-cap-crossover/scripts/test_python_sim.py`: **18/18 OK**. `overlap.py --check --summary`: rows=115, onset_lt_2_31_distinct=2, overlap.tsv OK. `--check --write` now errors as mutually exclusive. `tracemalloc` on CPython 3.13.5: 161.9 B/cell at 10^6 (coords outside small-int cache). Pathspec exclude verified: untracked under `results/` invisible with `:!…/results` / `:!…/scratch`; untracked helper under `scripts/` still visible. No walker growth data.

## 2026-11-09 20:38 NZDT · parent 00647e3 · intent

Periodic proactive session. Address the remaining mechanical "should fix" and minor items from the 2026-11-08 follow-up review of PR #34 (head `00647e3`) as Amendment A7: (1) restate the tiled memory model with the resident/inactive split and trail, and state that the "1 GiB pool" is a planning assumption the tiled backend does not enforce; (2) pin the exact pruning-index revision that A3 left as "see NOTEBOOK"; (3) commit the `tracemalloc` dict-cell measure as `scripts/measure_dict_cell_bytes.py` under `uv run --offline --script`, and note the Python dict simulator is not a candidate for uncapped arms at N=2^31; (4) fix `git_dirty` so pathspec excludes do not hide tracked modifications under `results/`/`scratch/` (two status calls); (5) keep registration and checks as separate commits with distinct timestamps. No prediction/gate changes; items 3 and 6 stay open for the user. No walker growth data. Do not resolve `notes/ACTIVE.md` conflicts.

## 2026-11-09 20:38 NZDT · parent 00647e3 · decision

Record as Amendment A7 on PR #34 once the suite and overlap check pass. Leave P3 discrimination and D metric for the user. Do not start G0, pilot or confirmation. Do not resolve `notes/ACTIVE.md` three-way conflicts here. Leave the reviewer's open questions on in-horizon crystallisation pairing and census `sweep_*.csv` COHORTS membership for a design answer.

## 2026-11-09 20:41 NZDT · parent c9f6ca6 · observation

`uv run --offline --script experiments/proposed/2026-10-q33-cap-crossover/scripts/test_python_sim.py`: **19/19 OK** (includes new `test_git_dirty_resume_chain_stays_clean`). `overlap.py --check --summary`: rows=115, onset_lt_2_31_distinct=2, overlap.tsv OK. `measure_dict_cell_bytes.py` under uv (CPython 3.12.15 from project venv): 172.4 B/cell at 10^5, **161.8 B/cell at 10^6**. Pruning re-confirm at A7 registration head `c9f6ca6`: index entries tip still `cc7a885`; concept `rg -il` matches 6/7; literal `rg -w -F -f <208 Q33 rules>` → 0 matches; decision remains **propose**. Two-call `git_dirty` pathspec check: clean tree → false; untracked under `results/` → false; untracked helper under `scripts/` → true. No walker growth data. No Rust changes (cargo test not re-run).

## 2026-11-19 08:46 NZDT · parent d3224b8 · intent

Daily progress session. ACTIVE (weekly review 2026-11-13) lists, as the next unblocked item, the #31 provenance re-pin and a `git_dirty` test that can fail. Register as Amendment A8 before touching code. No new experiment: other lines wait on owner decisions.

## 2026-11-19 08:46 NZDT · parent d3224b8 · deviation

The 2026-11-09 rebase-merge of #34 rewrote all 14 A1–A7 commits. Every `parent` hash in the entries above from 2026-11-04 onwards names the pre-rebase commit. The old→new map is in README Amendment A8 item 1; patches are identical for every pair (`git patch-id --stable`), so the registration-before-check order those entries record is unchanged. Entries are not edited.

## 2026-11-19 08:46 NZDT · parent d3224b8 · decision

Work on branch `agent/q33-a8-provenance-repin` stacked on #31 (base `exp/q33-cap-crossover-proposal`) so #31's own head is not moved without review. Do not start G0, pilot or confirmation. Leave design items 3 and 6, merge method, and ACTIVE conflicts to the owner.

## 2026-11-19 08:47 NZDT · parent af8c72b · observation

A8 checks (registration `af8c72b` pushed first). `git_dirty(root, rel)` factored out of `main` in `scripts/python_sim.py`; returns None unless both status calls succeed. New `test_git_dirty_helper_on_throwaway_repo` builds a `git init` repo in a temp dir: clean → false; untracked `results/c1` and `scratch/c1` → false; tracked `results/x.csv` edit → true; untracked `scripts/helper.py` → true; non-repo → None; tracked call failing → None. Suite with edits uncommitted: 20 run, OK, 1 skipped (the dirty-tree resume test). Mutants applied in place one at a time, then restored: M3 (drop results/scratch exclusion) → FAILED; M4 (`tracked = ""`) → FAILED; M5 (A7 `and` rule) → FAILED. Blog draft link re-pinned `4f8d018` → `3509395`. SHA pairing checked with `git patch-id --stable` (14/14 equal). No walker growth data; no Rust changes.

## 2026-11-20 08:52 NZDT · parent bb4e49c · intent

Daily progress session. The 2026-11-19 review of #41 suggests changes (one should-fix, four minors). Register as Amendment A9 and push it alone before editing code, so the registration has an externally visible CI run ahead of the checks. No new experiment: other lines wait on owner decisions.

## 2026-11-20 08:52 NZDT · parent bb4e49c · deviation

A8 says it was committed before its checks were run. The record contradicts that for the patch-id check and probably for the code/test run (NOTEBOOK 2026-11-19 08:47 says "edits uncommitted"). Erratum in README A9 item 2; A8 and earlier entries are not edited.

## 2026-11-20 08:47 NZDT · parent 9856908 · observation

A9 checks. Registration `2649c89` (committer time 2026-11-20 08:46:32 NZDT) was pushed alone; its CI runs on PR #41 (e.g. Simulator checks 44601840956, Small reproducibility checks 44601841265) were created 08:46:46 NZDT, before any code edit. Correction: the two 2026-11-20 entries above are headed 08:52 by hand; they were committed at 08:46 (commit `2649c89`). Code commit `9856908`: `_git(args, root=ROOT)`, `git_dirty` uses it; the throwaway-repo test is hermetic (GIT_CONFIG_GLOBAL=/dev/null, GIT_CONFIG_NOSYSTEM=1, GIT_CEILING_DIRECTORIES, gpgsign off, hooksPath=/dev/null, skipTest without git) and the half-checked case is a `subTest` over both status calls. Suite: 20 run, OK, 1 skipped (dirty-tree resume test; this checkout is dirty with the NOTEBOOK edit). Mutants applied one at a time to `scripts/python_sim.py`, then `git checkout`: M3 → FAILED; M4 → FAILED; M5 → FAILED; M6 (`if tracked is None:`) → FAILED; M6′ (`if untracked is None:`) → FAILED; M7 (`--untracked-files=no` on call 2) → FAILED; restored → OK. Hostile environment (TMPDIR inside a git work tree, global config with `commit.gpgsign=true` and a bad `core.hooksPath`): A9 test OK; the A8 test (`2649c89` scripts) ERRORS. Environment: Linux, Python 3.13.5, git 2.47.3, uv 0.13.7. No walker growth data; no Rust changes.
