# Leak minority turn: does a forced fresh-ground turn tolerate leak better when it is the rule's minority turn?

## Question and registered prediction

Registered 2026-11-13 09:10 (+1300) NZDT, base commit `a2c9494940526ecb1cc0d9b9483046690b1af38c` (branch
`agent/leak-handedness-cohort`, PR #38, not yet merged; this branch is stacked on it), **before any ant run of the specs
below and before the run or analysis scripts were written.** Code that exists at registration: `scripts/select_specs.py`
(one seeded draw of rules, writes specs) and `scripts/calibrate.py` (synthetic; reads only the development cohort's committed
per-rule lags and the held-out rules' letter strings, no held-out outcome). Implements the Q42 follow-up named in the
leak-handedness README ("Pruning-index outcome and next question") and in `notes/open-questions-hypotheses.md`.

**Known so far (development data, PR #38).** On 77 core-class rules (cohort C, from the wall-vs-memory Stage 3b draw), the
per-rule handedness lag Lambda (positive = a forced-L base has risen less towards porous than a forced-R base at the same leak
EF 0.3/0.5) had median +0.02 but a between-rule sd of 0.38 against seed noise near 0.05. **Post hoc**, found by looking:
Spearman(Lambda, fraction of R letters) = +0.40; all 7 `RRRR...` rules had Lambda > 0 and 12 of 14 `RLLL...` rules had
Lambda < 0. Read literally, the leak does less damage when the forced fresh-ground turn is the rule's *minority* letter. One of
several looks, uncorrected, and composition is confounded with prefix.

**Question.** Does that relation hold on rules that played no part in finding it?

### Competing readings

- **H-minority**: the forced turn's agreement with the rule's own turn statistics sets how much leaked fresh ground the
  boundary absorbs; a forced turn that matches the rule's *majority* letter is more fragile under leak. Predicts a positive
  Spearman and sign agreement on new rules.
- **H-chance**: the development correlation was a forking-paths artefact; on new rules Lambda is unrelated to composition.
  Predicts Spearman near 0.
- **H-prefix-only**: only the leading letters matter (prefix runs set the first fresh-ground excursions); composition as a
  whole is a weak proxy. Predicts P3 holding with P1/P2 weak or unresolved.

Priors before measuring: P1 replicates 45%, fails 20%, unresolved 35%. P3 holds 40% (if scoreable).

## Design

**Cohort H** (`results/rules.txt`, 110 rules): drawn uniformly without replacement (numpy `default_rng(20261113)`) from the
census core class (as wall-vs-memory Stage 1/3b: `cls == blob`, 0.30 < alpha_w < 0.37, not bursty), sorted by rule, after
removing the six Stage 1 / leak-titration rules and the 100 Stage 3b rules (pool 2298). By composition: 30 rules with R fraction
< 0.45, 54 with > 0.55, 14 balanced; 9 start `RRRR`, 14 start `RLLL`.
**Eligibility** (frozen, decided by the classifier before any leak statistic is computed): compact under both `ft:RULE:R` and
`ft:RULE:L` at EF = 0, by the leak-handedness classifier copied unchanged. Ineligible rules are listed with their classes.

**Anchor cohort A** (6 rules, a second `default_rng(20261113)` draw from cohort C of PR #38): the identical 26 specs per rule
that PR #38 ran (EF 0, 0.3, 0.5, 1; seeds 2026111201..04). Gate G1.

**Walker and specs** (`results/specs.txt`, 3016 lines): as PR #38, `fs:RULE:SET:SEED` with a 20-slot SET (k = 10 EF minority
slots, minority probability EF/2), arms R and L; EF = 0 rows are `ft:RULE:R`, `ft:RULE:L`. Cohort H: EF 0.3, 0.5, 1.0 x 2 arms x
seeds 2026111301..04 (new), plus the two EF = 0 rows: 26 specs per rule, 2860. EF 0.1 is dropped (it does not enter Lambda).

**Instrument.** `probe 27 16384`, early a over k = 12..22; `fit`, `classify`, `stalled`, `filler` and the per-rule statistics
(Delta, rise fraction F, Lambda, scoreable) copied unchanged from `experiments/active/2026-11-leak-handedness-cohort/scripts/analyse.py`.

**Compute budget.** 3016 probe runs to 2^27 on 3 threads; PR #38 ran 2708 in 21.5 min, so about 25 min. Stop rule: if not
finished within 90 minutes, stop and record it. No extension without a new registration.

### Gates (scored before any prediction)

- **G1 (replication).** All 156 anchor rows are byte-identical (as parsed, field for field) to the PR #38 `probe.csv` rows with
  the same labels. If G1 fails nothing is scored.
- **G2 (shared law at EF = 1)**, over scoreable H rules, as PR #38: |mean d| <= 0.02 and |d| <= 0.06 in >= 90% of rules.
  If G2 fails, P1-P3 are not scored.
- **Code oracle.** `cargo test --release --locked --test fresh_set` passes.

### Predictions (on scoreable eligible H rules; fewer than 30: nothing scored)

R fraction fr = (#R letters) / (rule length).

- **P1 (primary).** Spearman rho(Lambda, fr), rule-bootstrap 95% interval (10000 resamples, numpy `default_rng(20261113)`,
  rules sorted before resampling). **Replicates** if the lower end > 0; **fails** if the upper end < 0.20; otherwise
  **unresolved**.
- **P2 (per-rule sign).** Among scoreable rules with fr != 1/2 and |Lambda| >= 0.10: the fraction with
  sign(Lambda) = sign(fr - 1/2), Wilson 95% interval. **Holds** if the lower end > 0.50; **fails** if the upper end < 0.60;
  otherwise unresolved.
- **P3 (prefix).** Scoreable `RRRR...` rules have Lambda > 0 in >= 75%, and scoreable `RLLL...` rules have Lambda < 0 in
  >= 75%. Both must hold. Scored only if each group has >= 5 scoreable rules; otherwise reported descriptively.

**Calibration** (`results/calibration.txt`, synthetic, seed 20261113, 1000 draws, 2000 resamples). Model: Lambda = b (fr - 1/2)
+ N(0, 0.350) + N(0, 0.05), fr resampled from cohort H's letter strings, b from the development cohort (b_dev = +1.224 per unit
fr; dev Spearman +0.404). False "replicates" when b = 0: 2.8% / 2.0% / 2.7% at n = 50 / 70 / 90; "replicates" when b = b_dev:
81% / 94% / 97%; at b_dev/2: 30-53% (mostly unresolved otherwise). False P2 "holds" at b = 0: 2-3%; P2 "holds" at b_dev: 69-90%.
Under the null, P1 "fails" only 29-47% of the time (the rest unresolved), so a null on this cohort will often read as
unresolved rather than as a clean failure; that is a stated limit of n, not a tuning target. The development cohort is not
reused as target data: cohort C rules are excluded from H.

Reading: P1 replicates supports H-minority as a description that transfers within the core class (still no mechanism). P1 fails
retires the composition reading for this class and window and leaves the rule-by-rule handedness effect unexplained. P3 holding
while P1 is not replicated supports H-prefix-only.

### What this cannot show

No mechanism (why the forced turn's agreement with the rule's letters matters); no asymptotic statement (finite window
k = 12..22, board 16384); nothing outside the core class; composition and prefix remain partly confounded.

## Pruning-index preflight

- Index revision and search commands: `a2c9494940526ecb1cc0d9b9483046690b1af38c`; `ls notes/pruning-index/entries` (7 entries,
  titles and predicates read for PR #38 at `251100a`; none added since); `rg -n -i -e "leak" -e "minority" -e "handed" -e "composition" notes/pruning-index/entries`.
- Candidate signature IDs: `NR-20261026-wall-vs-memory-no-wall-porous`, `NR-20261028-wall-vs-memory-bounded-random-fresh-compact`
  (scope read for PR #38); the "composition" hit is `NR-20261025-kappa-exposure-classes-exposed-edge`, about return classes, not turns.
- Scope comparison: no spec is a member (leak R/L sets at EF > 0 on new rules; the bounded-set entry covers `RU`/`LU`). Anchor rows
  are deliberate replication gates.
- Decision: run.
- Run spec and exclusions: `results/specs.txt`, `results/spec_roles.csv`, `results/rules.txt`; no signature-based exclusion.
- Compute/stopping budget: above. P1 replicating would warrant a mechanism test (does the lag follow the colour-0 vs majority
  letter when composition is fixed, e.g. letter permutations of one rule).

## Reproduction

From the repository root (Linux; `UV_PROJECT_ENVIRONMENT=$HOME/.venvs/turmite UV_LINK_MODE=copy`, Rust from `~/.cargo`):

```sh
uv run --frozen python experiments/active/2026-11-leak-minority-turn/scripts/select_specs.py   # rules, specs, roles
uv run --frozen python experiments/active/2026-11-leak-minority-turn/scripts/calibrate.py      # results/calibration.txt (~6 min)

RAYON_NUM_THREADS=3 sh experiments/active/2026-11-leak-minority-turn/scripts/run.sh scratch/rerun  # fresh dir; compare bytes
uv run --frozen python experiments/active/2026-11-leak-minority-turn/scripts/analyse.py        # runs.csv, rules.csv, analysis.txt
cargo test --release --locked --test fresh_set                                                    # code oracle
```

(`run.sh` and `analyse.py` were added in a second commit, after registration and before the run.)

## Results, uncertainty and limitations

Run 2026-11-13 09:11-09:35 NZDT (24 min, 3 threads), commit `5ee269f` (`results/provenance.txt`; probe sha256 `3f5416b7...`, the
same binary hash as PR #38; `probe.csv` sha256 `7bb92b3c...`). Results commit `eb7f41d`. The folder was registered in `proposed/` and moved to `active/` after the run
(`experiments/_migration/2026-11-13-leak-minority-turn.tsv`), so `provenance.txt` and the commits before the move name the old path. Scored output `results/analysis.txt`
(per run `results/runs.csv`, per rule `results/rules.csv`); `analyse.py` gives byte-identical output on re-run and under
`PYTHONHASHSEED=7`.

**Gates.** G1 PASS: all 156 anchor rows identical to PR #38's rows. G2 PASS: mean d +0.0031, |d| <= 0.06 in 81/81 rules.
Code oracle `fresh_set` 4/4. **Eligibility:** 84 of 110 H rules compact under both forced turns (26 ineligible: 15 escape
under forced L, 5 filler, 5 intermediate under L, 1 intermediate under R; listed in `analysis.txt`); 81 scoreable.

**P1 FAILS.** Spearman(Lambda, R fraction) = -0.114, rule-bootstrap 95% [-0.329, +0.108], n = 81. The development value was
+0.404; the held-out interval excludes it and excludes everything above +0.11. By composition band, median Lambda is -0.14
(fr < 0.45, n 19), -0.06 (balanced, n 21), -0.04 (fr > 0.55, n 41): no positive trend.

**P2 FAILS.** Sign agreement 29/62 = 0.47, Wilson 95% [0.35, 0.59] (upper end below 0.60).

**P3 FAILS** on its `RRRR` half: 4 of 6 `RRRR...` rules have Lambda > 0 (needed >= 75%). The `RLLL...` half held (8 of 9 have
Lambda < 0). Two small groups; the RLLL agreement alone is not evidence for a prefix rule and was not registered as a separate test.

Calibration context: with the development slope the rule would have said "fails" in 0% of synthetic draws, and with half of it in
about 1.5%. So this is a controlled failure of the composition reading on new rules, not a power problem.

**Post hoc, not registered** (`scripts/posthoc.py`, `results/posthoc.txt`, written after scoring): the rule-level spread itself
replicates. Lambda has sd 0.381 in H (0.383 in the development cohort), quartiles -0.36 / +0.23, |Lambda| > 0.4 in 27 of 81 rules,
against seed noise near 0.057 per rule. The median is -0.065 (37/81 positive), close to zero as before. So handedness of the forced
turn changes leak tolerance strongly rule by rule, in both directions, on new rules too; R/L composition does not say which way.

**Limitations.** Finite window (early a, k = 12..22), board 16384, 4 seeds per cell, two leak levels in Lambda, core class only.
"Fails" covers the composition-sign description and the two prefix groups as registered, not every function of the rule table.

## Pruning-index outcome and next question

Dead-end signature `NR-20261113-leak-handedness-composition-sign` (well-controlled negative result within the stated scope:
composition does not predict the sign of the handedness lag in the core class at this window). It does not exclude other
predictors of the sign, other classes, or longer horizons.

Next question (not registered): the per-rule effect is large and real but its sign is not set by composition. A predictor would have
to come from the dynamics rather than the letter count, e.g. whether forced-L at EF = 0 is closer to the rule's own geometry
(`a0_L` vs `a0_R`, or late-window behaviour), tested on these 81 + 77 rules with a fresh held-out draw. A cleaner mechanism test
fixes composition and permutes letters within one rule's table.
