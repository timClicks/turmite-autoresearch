# NR-20261028-wall-vs-memory-bounded-random-fresh-compact: for the 106 tested core-class rules, randomising the fresh-ground turn among {R, U} or {L, U} (bounded fresh runs) does not make growth porous; "randomness on fresh ground by itself destroys the compact regime" (H-random) failed

- Schema: 1
- ID: NR-20261028-wall-vs-memory-bounded-random-fresh-compact
- Registered: 2026-10-28T20:00+13:00
- Author: Claude (AI research agent)
- Initial status: active
- Evidence class: empirical. One registered test (Stage 3c) on two pinned cohorts, finite windows. Not a proof; nothing beyond the tested specs is excluded.
- Objective and search keywords: decide whether a random fresh-ground turn breaks the ant's compact growth by itself (H-random) or only when it makes fresh runs unbounded (H-bound). Observables: area exponent a, perimeter exponent beta, compact/porous class. Keywords: fresh ground, first departure, random fresh turn, bounded fresh run, reversal, U-turn, FreshSetWalker, fs:, H-random, H-bound, wall, porous, compact, cube root.
- Claim and permitted pruning decision: Claim: H-random predicted f = compact / non-escape <= 0.50 for the bounded sets; observed `fs:RULE:RU:SEED` 47/48 (cohort A) and 86/100 (cohort B), `fs:RULE:LU:SEED` 42/48 (A); 1 porous run in 196. Permitted: defer an exact repeat of these 196 specs with the same instrument as a test of H-random. Not permitted: concluding that bounded random fresh turns leave the exponent unchanged (they raise early a by about +0.056 in cohort B), or anything about other rules, sets, backgrounds, horizons or observables. The registered H-bound reading was itself unresolved (thresholds missed), so this entry does not establish H-bound.

## Topological dead-end signature

- Model and update semantics: one walker on Z^2, board 16384 x 16384 (run stops within 2 cells of the edge). `FreshSetWalker` (`src/walkers.rs`): the ant `RULE` (turn by rule[colour], colour -> colour + 1 mod n), except that on a cell never departed from the turn is `SET[(high32 * |SET|) >> 32]` of the step's SplitMix64 draw (seeded by SEED, one draw per step); R = +1, L = -1, U = +2 quarter turns. With SET = RL it equals `HybridWalker` at EV = 0, EF = 1 (F1) step for step.
- Rule-space vertices and adjacency: vertices are (rule, SET, seed). No adjacency is claimed.
- Membership predicate: a spec belongs if and only if it is one of the 196 lines of `experiments/active/2026-10-wall-vs-memory/results/stage3c_specs.txt` with SET in {RU, LU}: `fs:RULE:RU:SEED` and `fs:RULE:LU:SEED` for RULE in `results/rules.txt` (6 rules) and SEED 2026102601..2026102608, and `fs:RULE:RU:2026102801` for RULE in `results/stage3b_rules.txt` (100 rules).
- Canonicalization/equivalences: none.
- Invariants: not used.
- Scope: blank background, start at the centre heading north, the stated seeds.
- Observable and instrument: `bin/probe` (`probe 27 16384`) octave windows; per run a = slope of ln area vs ln t and beta = slope of ln perimeter vs ln area over k = 12..22 (k = log2 of the window end), classes as Stage 1 plus escape, stalled and filler (all registered before the run). Scorer `scripts/analyse_stage3c.py`. Binary sha256 a0615a0514150ab73d25727eb691b0fdcddee86af2459def45098d751aea87bc (rustc 1.97.0), commit `3d13c181482dbcab0575e8b5c4da58dfcb2aaf06`.
- Horizon and windows: 2^27 steps; early window k = 12..22 complete for every member run (no escapes).
- Exclusions: other sets (in particular RL and RLU, which are unbounded), deterministic policies, other rules or rule classes, patched or random backgrounds, other boards and horizons, other observables (kappa, c, late-window exponents).

## Evidence and limits

- Preregistered criterion: `experiments/active/2026-10-wall-vs-memory/README.md`, "Stage 3c", registered at `9fbcbf2f` (19:30 NZDT 2026-10-28) before code or runs; scorer committed at `3d13c181` before the run.
- Evidence revision: `df2e5bb1908e052a0e7ac3cd93d3fa2e2a9b233b`.
- Inputs/results (SHA-256, under `experiments/active/2026-10-wall-vs-memory/results/`): `rules.txt` a4fcff15f30dc97e2b7c9b574a77a2d3438d1a3a504e7ba5d534a9607f352591; `stage3b_rules.txt` 8ab1ca28dba8800c0df059af77e52034e243736388732e39c33b0e62763a8427; `stage3c_specs.txt` 375d3e2dfaa59afa02e950b0ba0e9aa316f413141d1f9b0232ab23c24e07c951; `stage3c_probe.csv` 29fa44d89c86c457df50d9c0648f26f98914e4aed8f0d46ccececeb50ce77562; `stage3c_runs.csv` 51092c3ad0c9b16267254d016d8ca41390e40c4e7f9346e102ac61aed2b185d0; `stage3c_analysis.txt` b378606bd36e345c689a7b53177a59a12e3a2190d6a1e9f29bb3fa83524ccae8.
- Recipe: `uv run --frozen python experiments/active/2026-10-wall-vs-memory/scripts/select_stage3c.py`; `RAYON_NUM_THREADS=3 sh experiments/active/2026-10-wall-vs-memory/scripts/run_stage3c.sh`; `uv run --frozen python experiments/active/2026-10-wall-vs-memory/scripts/analyse_stage3c.py`.
- Proof or measured result: cohort A (6 rules x 8 seeds): RU f 0.979 [0.891, 0.996], LU 0.875 [0.753, 0.941], porous 0 of 96; cohort B (100 rules x 1 seed): RU f 0.860 [0.779, 0.915], porous 1 of 100 (Wilson 95%). Non-compact members are intermediate near the compact edge (early a 0.77-0.86). Unbounded control RLU (not a member): compact 2 of 148, porous 73 of 148.
- Controls and oracle checks: T0' (`cargo test --release --locked --test fresh_set`: independent sparse reference; RL = F1; the fresh-run bound of at most 4 cells, 5 from the origin, for RU/LU on every simulated step; long runs for RLU) passed; T3 (six `fs:RULE:RL` probe rows equal F1's committed rows field for field) passed.
- Confounds: finite windows; cohort A has 6 independent rules (seeds shared), cohort B one seed per rule; all rules from one class (core: cls blob, 0.30 < alpha_w < 0.37, not bursty), selected for compact growth under their own R turn; bounded randomness shifts the exponent (+0.056 early a in B), so "compact" is a class statement.
- Why the evidence covers the predicate: the membership is exactly the 196 tested specs and every one was fitted and classed.

## Reopening and cross-references

- Reopen if: a correction to `FreshSetWalker` or the probe changes these trajectories; longer horizons show members leaving the compact class; a different classification of the near-edge intermediates is justified by a calibrated criterion.
- Discriminating next test: a dose curve in the bound itself (fresh policies whose runs are bounded by m cells, m = 4..64) to see whether compactness fails at a size set by m and the territory, which H-bound predicts and H-random does not address. Not registered.
- Experiment / lab notebook / scientific note: `experiments/active/2026-10-wall-vs-memory/README.md` (Stages 3-3c), `NOTEBOOK.md`; `notes/cube-root-hypothesis.md`; `notes/open-questions-hypotheses.md`.
- Related signature IDs: `NR-20261026-wall-vs-memory-no-wall-porous` (F1, EF = 1 random R/L, unbounded fresh runs, porous). No conflict: that entry concerns an unbounded policy; this one, bounded random policies. Together they locate the effect in the bound, within the tested specs only.

## Amendments (append only)

None.
