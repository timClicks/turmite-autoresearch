# NR-20261113-leak-handedness-composition-sign: in core-class ants, the rule's R/L composition does not predict the sign of the leak handedness lag

- Schema: 1
- ID: NR-20261113-leak-handedness-composition-sign
- Registered: 2026-11-13T09:45+13:00
- Author: Turmite Research Agent (AI research agent)
- Initial status: active
- Evidence class: empirical. One registered held-out test (81 scoreable rules, 4 seeds per cell) over a finite window. Not a proof.
- Objective and search keywords: find a rule-table description that predicts which forced fresh-ground turn (R or L) tolerates a partial random leak better, per rule. Keywords: leak, handedness, forced turn, fresh ground, minority turn, composition, R fraction, prefix, RRRR, RLLL, Lambda, Q42.
- Claim and permitted pruning decision:
  - **Claim:** on 81 new core-class rules compact under both forced turns, Spearman(Lambda, R fraction) = -0.114, rule-bootstrap 95% [-0.329, +0.108]; per-rule sign agreement with sign(fr - 1/2) 29/62, Wilson [0.35, 0.59]; `RRRR` prefix 4/6 with Lambda > 0. The development correlation (+0.404, post hoc, PR #38) did not replicate.
  - **Permitted:** do not re-test "the forced turn tolerates leak better when it is the rule's minority letter" (by R fraction or by the `RRRR`/`RLLL` prefix groups) on core-class rules at this window.
  - **Not permitted:** concluding that handedness does not matter (the per-rule lag is large and replicates: sd 0.38 against seed noise ~0.06); excluding other predictors of its sign (other table features, dynamics-based predictors such as a0_L vs a0_R); excluding other classes, windows, boards or horizons.

## Topological dead-end signature

- Model and update semantics: square-lattice turmites with rule string RULE (colour i turns RULE[i]), driven through `FreshSetWalker` (`fs:RULE:SET:SEED`): on a never-departed cell the turn is drawn from a 20-slot SET (base letter in 20 - k slots, the other letter in k = 10 EF slots); elsewhere the rule's own turn.
- Rule-space vertices and adjacency: rule strings of the census core class (`cls == blob`, 0.30 < alpha_w < 0.37, not bursty), length 8-12, all R on colour 0; no adjacency used.
- Membership predicate: a test whose predictor of sign(Lambda_r) is a monotone function of the R fraction of RULE, or membership in the `RRRR`/`RLLL` prefix groups, scored on core-class rules compact under `ft:RULE:R` and `ft:RULE:L` at EF = 0, with Lambda as defined in `experiments/active/2026-11-leak-handedness-cohort/README.md` (EF 0.3, 0.5; early a over k = 12..22).
- Canonicalization/equivalences: none.
- Invariants: not used.
- Scope: `probe 27 16384`, seeds 2026111301..04, cohort drawn with `default_rng(20261113)` from the core class minus the 106 rules used before.
- Observable and instrument: per-rule lag Lambda = mean over EF 0.3, 0.5 of rise fraction F_R - F_L, with a shared EF = 1 level (gate G2).
- Horizon and windows: 2^27 steps; early window k = 12..22.
- Exclusions: other classes, other windows and horizons, EF other than 0.3/0.5, other predictors of sign.

## Evidence and limits

- Preregistered criterion: `experiments/active/2026-11-leak-minority-turn/README.md` at `fc60f7b` (P1-P3, gates, calibration), scripts at `5ee269f`, both before the run.
- Evidence revision: `eb7f41d93a7baf89d8501a059ea21b6ff6e4b838`
- Inputs/results (SHA-256): see `results/provenance.txt` (`probe.csv` 7bb92b3c698e65797fc55fdd6eba43906573c4c7252a8723cddbedf2d4d9dcad); `results/analysis.txt`, `rules.csv`, `runs.csv` regenerate byte-identically.
- Recipe: `scripts/select_specs.py`, `scripts/run.sh`, `scripts/analyse.py` (README Reproduction).
- Proof or measured result: as in the claim; 2860 held-out runs plus 156 anchor runs.
- Controls and oracle checks: G1 (156 anchor rows byte-identical to PR #38), G2 (same law at EF = 1, mean d +0.003), `cargo test --release --locked --test fresh_set` 4/4. Synthetic calibration: under the development slope the rule says "fails" in 0% of draws, at half the slope ~1.5%.
- Confounds: composition and prefix are partly confounded; two leak levels per arm; 4 seeds.
- Why the evidence covers the predicate: the registered predictors are exactly the members, scored on a fresh uniform draw from the class.

## Reopening and cross-references

- Reopen if: a scoring or classification error is found, or the test is run in another class, window or horizon (new ID in that case).
- Discriminating next test: a dynamics-based sign predictor registered on the 77 + 81 rules and scored on a fresh draw, or a letter-permutation test at fixed composition.
- Experiment / lab notebook / scientific note: `experiments/active/2026-11-leak-minority-turn/` README and NOTEBOOK 2026-11-13; `notes/open-questions-hypotheses.md` Q42.
- Related signature IDs: `NR-20261028-wall-vs-memory-bounded-random-fresh-compact` (bounded fresh runs; different specs).

## Amendments (append only)
