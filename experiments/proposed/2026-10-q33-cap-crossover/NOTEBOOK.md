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
