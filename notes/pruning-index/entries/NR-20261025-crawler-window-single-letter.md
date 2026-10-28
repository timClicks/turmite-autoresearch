# NR-20261025-crawler-window-single-letter: for 90 stationary census blobs (n 10..12, lead 1..3), single-letter flips show no lead-dependent "shared-cell window" [m+1, 2m+1] in the edge birth cost 1/c, and no consistent sign inside it

- Schema: 1
- ID: NR-20261025-crawler-window-single-letter
- Registered: 2026-10-25T23:35+13:00
- Author: Kea (AI research agent, Claude)
- Initial status: active
- Evidence class: empirical. Two registered tests (W2, W3) failed on one pinned cohort after the noise gate passed. This is not a proof, and nothing beyond the tested specs is excluded.
- Objective and search keywords: explain which rule letters beyond the lead set the edge birth rate c (births per boundary step; the c law `1/c = 1.363 + 0.696 m`). The mechanism tested is H-crawl's positional window: letters at positions `[m+1, 2m+1]`, where the square-ring crawler's shared cells must read `s_0`. It should matter most, move outward with the lead m, and raise `1/c` when a letter is set to `s_0`. Keywords: c law, birth rate, boundary steps per birth, lead, opening run, crawler, square-ring, shared cell, window, single-letter flip, mutant, letters 5-8, K3.
- Claim and permitted pruning decision: Claim: on the tested specs, (W2) the relative effect of a flip at q = p - m in {3, 4} is *smaller* for m = 3 (inside the window) than for m = 1 (outside it): median e 0.034 vs 0.062, ratio 0.55 (registered threshold >= 1.5). (W3) In-window flips `s_bar -> s_0` raised `1/c` in only 31% of 67 kept mutants (registered >= 70%); `s_0 -> s_bar` lowered it in only 44% of 63. Permitted: defer an exact repeat of single-letter flip tests of the window hypothesis on the same 90 parents, instrument, horizon and filter. Not permitted: excluding whole-table support effects (the same experiment's P1 shows they exist), multi-letter or gap-dose designs, other lengths, leads, backgrounds, the flat band, or longer horizons.

## Topological dead-end signature

- Model and update semantics: one ant on Z^2, blank board 4096 x 4096 (run ends on escape), colours 0..n-1. On colour c the ant turns by rule[c] (R = +1, L = -1 quarter turn), sets the colour to (c+1) mod n and steps (`src/edge_trace.rs`, `AntWalker`).
- Rule-space vertices and adjacency: the parents are the 90 rules in `experiments/archive/2026-10-crawler-cost-chaotic-edge/results/lists/p2_parents.txt`: 30 per lead m in {1, 2, 3}, drawn from stationary census blobs (`cls == blob`, `c > 0`, `|g_k| < 0.05`), n in 10..12, not Pi(m), by `scripts/make_lists.py` with numpy `default_rng(20261025)`. Edges: one letter flipped at position p in `[m+1, n-1]`, keeping the lead and primitivity (748 parent-mutant pairs, 664 distinct mutants, `lists/cohorts.csv`).
- Membership predicate: a pair belongs if and only if it is a row with role `p2_mutant` in `lists/cohorts.csv` (sha256 below).
- Canonicalization/equivalences: none. Mirror images and rotations are not covered.
- Invariants: not used.
- Scope: blank background, a single start, deterministic (no seeds).
- Observable and instrument: `1/c` = boundary_steps / births over the window (2^23, 2^24], from `examples/c_law_mechanism_trace.rs blank 24 4096` at commit `082fb7bb29463fb5cf1d6a19ad95a6137355302b`, binary sha256 e1bd80b819c3827bc54c25cd35ff7cb2df7411055d97be0ff802671a0919f780 (rustc 1.97.0). A pair is kept if neither run escapes, both have births >= 200 and both have 1.3 <= area/area_t0 <= 1.9. Effect `e = |1/c_mut - 1/c_par| / (1/c_par)`.
- Horizon and windows: 2^24 steps, last-octave window. Parents were also run to 2^25 for the noise gate only.
- Exclusions: whole-table support (P1: Pi rules sit at a median phi of 0.65, against 0.15 for controls). Multi-letter changes and gap-dose designs. W1 (near letters matter more than far letters) held and is not a dead end; it does not discriminate the window hypothesis from a smooth decay. Leads >= 4, lengths outside 10..12, the flat band, sparse backgrounds and other horizons are also not covered.

## Evidence and limits

- Preregistered criterion: `experiments/archive/2026-10-crawler-cost-chaotic-edge/README.md`, W2 and W3 (and the N0 gate), registered at `a387d27` before any list or run.
- Evidence revision: `b4798f8412fbe5bfbeedf0190156b7a53a61ab54`.
- Inputs/results (SHA-256, under `experiments/archive/2026-10-crawler-cost-chaotic-edge/results/`): `lists/p2_parents.txt` cf137fd6d62c91099f91e361e7fb8a2d79f16bd8dd0bc65dd8a39d3015417fb7; `lists/p2_mutants.txt` 63e00373aa60f9b6426843d1b56fe9f83b5566d047bcd6f477fd21985bce91f0; `lists/cohorts.csv` 3ee20861434037f8e71fd0a460a3c4a44c845f4333963b72a320701c645067f1; `trace_p2_parents_24.jsonl` bb7f6a19514d829aee6eeb7ae292e3d64af4589430e79e434bb91a09c4512b8e; `trace_p2_parents_25.jsonl` b2d4d03f2c28ad5a325a51fd6b6979b133647dca2f6e168076450da5e482ed81; `trace_p2_mutants.jsonl` a6e798ee8be1424662c7baf68c685d7ea59eae0818ba3235c918a1540e86d9b3; `p2_effects.csv` 3ffac26e2e68f9831dee1cbcef91bd937adaecb617babba13ce94d089aba7b1e; `analysis.txt` b0acac75143e446ca753f664a51cbb04a76e7fc40c60471f023cdedcb369da18; `analysis.json` b28e5154522faf21da0e587c0cb7c79dc9e1cd131d65be6d69256ce14322c33e; `run.log` 7a257a588e0276d26645005c378c04ba24a05e1dbfdbadd8784ad7fa8b6185e5.
- Recipe: `uv run --frozen scripts/make_lists.py`; `CARGO_TARGET_DIR_FRESH=$(mktemp -d) sh scripts/run.sh`; `uv run --frozen scripts/analyse.py` (all paths relative to the experiment folder).
- Proof or measured result: 748 pairs, of which 530 were kept. W1 scored 28, 25 and 25 parents (m = 1, 2, 3). W2 compared 40 (m = 3) and 43 (m = 1) kept mutants. W3 used 67 + 63 kept in-window mutants for m = 2 and 3. N0: the median relative drift of the parents' `1/c` from 2^24 to 2^25 is 0.0026, well under half the median in-window effect (0.070).
- Controls and oracle checks: the same instrument reproduces the crawler's exact `1/c = k + 5/4` to within 0.0021 on 25 census fillers (P0b), and the experiment's own strip simulation gives the exact rationals (P0a). The edge tracer has property tests against `probe_walker` and a naive reimplementation (`tests/edge_trace.rs`).
- Confounds: survivor filtering kept 62-75% of pairs depending on position class and m (table in `analysis.txt`). Flips that turn a rule into a highway or filler drop out. There is one start per rule, and between-start variance is not measured.
- Why the evidence covers the predicate: the membership is exactly the tested pairs, and the statistic is computed over the kept ones under the registered rule. Nothing is claimed for untested rules or conditions.

## Reopening and cross-references

- Reopen if: a gap-dose or multi-letter design shows that window letters act collectively (an all-or-nothing chain); the instrument or filter changes; other lengths, leads, backgrounds or horizons are used; or between-start variance turns out to be comparable to e.
- Discriminating next test: on the flat band (c-law-mechanism Stage 2 setting), rules with a complete crawler window except for 0, 1 or 2 gaps at controlled positions. This tests a product (chain) model against an additive one. Not scheduled.
- Experiment / lab notebook / scientific note: `experiments/archive/2026-10-crawler-cost-chaotic-edge/README.md`, `NOTEBOOK.md`, `notebook.ipynb`; `notes/open-questions-hypotheses.md`.
- Related signature IDs: none. `NR-20261025-kappa-exposure-classes-exposed-edge` concerns kappa by exposure class, not c or letter positions.

## Amendments (append only)

None.
