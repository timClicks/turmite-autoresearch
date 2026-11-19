# Leak handedness on a cohort: does a forced-L base need more leak than forced R to lose compactness?

## Question and registered prediction

Registered 2026-11-12 09:05 (+1300) NZDT, base commit `251100a2f99f81099954ebd147dea11ea173e337`, **before any
run of the specs below and before the run or analysis scripts were written**.
*(Correction 2026-11-12 09:25: the minute above was written ahead of the clock; the registration commit `19e4aa0` is dated
08:58:54 +1300, and the run started at 08:59:16 +1300.)* Code that exists at registration:
`scripts/select_specs.py` (writes the specs from committed Stage 3b classes, no draw) and `scripts/calibrate.py`
(synthetic, no ant data). Implements Q42 in `notes/open-questions-hypotheses.md` (follow-up 2 of the leak titration).

**Known so far.** In the leak titration (`experiments/active/2026-10-leak-titration/`, six core rules) a leak EF on
fresh ground (the fresh turn is replaced by R or L with probability 1/2 each) takes the ant from compact to porous
gradually between EF 0.1 and 0.6. With a forced-L base turn on fresh ground instead of the ant's own R, two rules
(`RLRLLRRLRLR`, `RLRLLRRRRRRR`) that build highways under forced L at EF = 0 were already porous at EF = 0.1, and the
other rules rose more slowly than under base R (EF_50 0.4-0.7 against 0.3-0.5). Registered P4 (|EF_50^L - EF_50^R| <= 0.1)
failed on 1 of 3 scoreable rules. The README calls this "three rules, one base turn, no mechanism: a lead, not a finding".

**Question.** On a cohort large enough to settle it, (P1) does a forced-L base need more leak than a forced-R base to
lose compactness, and (P2) do rules that build an ordered escaping structure under forced L go porous at a small leak
when rules that stay compact under forced L do not?

Why it matters for priority 1 (boundary access): the record locates compactness in the bound on fresh runs
(`NR-20261028-wall-vs-memory-bounded-random-fresh-compact`). If the base turn's handedness relative to the rule's own
colour-0 turn changes how much leak the territory tolerates, then the bound is not the whole story: the match between
the fresh-ground turn and the interior turns matters for how the boundary is re-entered. If there is no lag, the leak
titration's P4 miss was a small-sample artefact and the bound account stands unamended on this point.

### Competing readings

- **H-match** (lead from the leak titration): with base L the fresh turn mismatches the colour-0 turn R the rule uses
  on revisits; leaked R turns then *agree* with revisits and do less damage than leaked L turns under base R. Predicts
  a positive lag (arm L less risen than arm R at the same EF).
- **H-bound-only**: only the distribution of fresh-run lengths matters, and it is identical in law for the two arms
  at the same EF (mirror image on fresh ground). Predicts no lag.
- **H-reversed**: a forced-L base is already further from the ant's own dynamics and breaks faster. Predicts a negative lag.

Priors before measuring: lag 45%, no lag 35%, reversed 10%, unresolved 10%.

## Design

**Cohort** (`results/cohorts.csv`, from the committed classes in
`experiments/active/2026-10-wall-vs-memory/results/stage3b_runs.csv`; no overlap with the six leak-titration rules):

- **C** (77 rules): compact under both forced R and forced L at EF = 0.
- **E** (9 rules): escape under forced L (all before 2^21 steps), compact under forced R.
- Excluded (14): 13 intermediate under forced L, 1 intermediate under forced R (listed with reasons in `cohorts.csv`).
  Intermediate bases cannot show a compact-to-porous loss cleanly.

**Walker and specs** (`results/specs.txt`, 2708 lines, sha256 `41b1a9b4850aae41b7aff76429368ed24a14997e3d12c9250dbd92b382d17621`).
Both arms use `FreshSetWalker` (`fs:RULE:SET:SEED`) with a 20-slot SET (k = 10 EF minority letters, so the minority
probability is EF/2 exactly, as in the leak titration's arm L). Using one encoding for both arms removes the `hy:`
versus `fs:` encoding difference from the comparison. Seeds 2026111201..04 (new).

| cohort | arm | EF | runs |
|---|---|---|---|
| C | R and L | 0 (`ft:RULE:R`, `ft:RULE:L`, gates) | 154 |
| C | R and L | 0.1, 0.3, 0.5, 1.0 x 4 seeds | 2464 |
| E | R and L | 0 (gates) | 18 |
| E | R and L | 0.1 x 4 seeds | 72 |

**Instrument.** `probe 27 16384` (unchanged from wall-vs-memory and the leak titration). Per run: early a and beta
over k = 12..22, late a over k = 20..26; class by the Stage 1 `fit` and `classify`, `stalled` as Stage 3 and `filler`
as Stage 3c, copied unchanged from `experiments/active/2026-10-wall-vs-memory/scripts/analyse_stage3c.py`; escape as
the probe reports it.

**Compute budget.** About 2700 probe runs to 2^27 steps on 3 threads; the Stage 3b (300 runs, 3 min) and leak titration
(1068 runs, 14 min) rates give roughly 30-45 minutes. Stop rule: if the run has not finished within 2 hours, stop and record it.

### Statistics (frozen)

For a rule r in C: `a0_R,r`, `a0_L,r` = early a of the EF = 0 rows (deterministic). `a1_r` = mean early a over the 8 EF = 1
runs (4 per arm; same law). `abar_arm,r(EF)` = mean over seeds with a complete early fit.
`Delta_arm,r = a1_r - a0_arm,r`. Rise fraction `F_arm,r(EF) = (abar_arm,r(EF) - a0_arm,r) / Delta_arm,r`.
**Lag** `Lambda_r = mean over EF in {0.3, 0.5} of [F_R,r(EF) - F_L,r(EF)]` (positive = arm L has risen less).

A rule is **scoreable** if `Delta_R,r >= 0.10` and `Delta_L,r >= 0.10`, and at least 3 of 4 seeds have a complete early
fit in each arm at EF = 0.3, 0.5 and 1.0. Escapes at EF > 0 are counted and reported; they have no early fit.

**Calibration of the P1 rule** (`results/calibration.txt`, synthetic, 70 rules, 1000 draws, seed 20261112; per-seed sd
0.025 = the median within-rule sd in the committed leak-titration runs, and 0.04 as a stress value). True lag 0: "no lag"
95% (sd 0.025) / 70% (sd 0.04), false "lag" 0.0% / 0.3%, false "reversed" 2.4% / 2.6%. True lag +0.10: "lag" 100%.
True lag +0.05: "lag" about half the time, otherwise mostly unresolved. True lag -0.10: "reversed" 100%.

### Gates (scored before any prediction)

- **G1 (replication).** The 172 EF = 0 rows (`ft:RULE:R`, `ft:RULE:L`) are byte-identical to the committed Stage 3b
  `stage3b_probe.csv` rows with the same labels. If G1 fails nothing is scored.
- **G2 (shared law at EF = 1).** Over scoreable C rules, `d_r = abar_L,r(1) - abar_R,r(1)`: |mean d_r| <= 0.02 and
  |d_r| <= 0.06 for at least 90% of rules. If G2 fails, P1 is not scored (the shared endpoint is not shared).
- **Code oracle.** `cargo test --release --locked --test fresh_set` passes (independent sparse reference for `fs:`).

### Predictions

- **P1 (handedness lag, cohort C).** Median Lambda over scoreable rules with a rule-bootstrap 95% interval (10000
  resamples, seed 20261112, rules sorted before resampling). **Lag** if the interval's lower end > 0 and the median
  >= 0.05; **reversed** if the upper end < 0; **no lag** if the interval lies inside [-0.05, 0.05]; otherwise
  **unresolved**. Fewer than 30 scoreable rules: not scored.
- **P2 (ordered-L collapse).** Arm L at EF = 0.1: the fraction of runs classed porous is >= 0.50 in cohort E (36 runs)
  and <= 0.10 in cohort C (308 runs). Both halves must hold. Prior about 50%. Reported alongside: escapes in each cohort
  at EF = 0.1 (an escaping run is not porous), and arm R at EF = 0.1 for cohort E as the within-rule control.

Reading table: P1 lag supports H-match (the base-turn/colour-0 match changes leak tolerance); no lag supports H-bound-only
and turns the leak titration's P4 miss into a three-rule artefact; reversed contradicts the lead. P2 holding says the
forced-L highway collapse belongs to rules with ordered forced-L structures, not to forced-L bases generally; failing
on the E half says the six-rule observation does not generalise across escaping rules.

### What this cannot show

No asymptotic statement (finite window k = 12..22), nothing about rules outside this cohort, no mechanism for a lag
beyond the readings above, and no statement about EF_50 location (two EF points per arm, not a curve).

## Pruning-index preflight

- Index revision and search commands: `251100a2f99f81099954ebd147dea11ea173e337`; `rg --files notes/pruning-index/entries`
  (7 entries, all titles and predicates read); `rg -n -i -e "leak" -e "forced.?L" -e "fresh" -e "handed" -e "titration" notes/pruning-index/entries`.
- Candidate signature IDs: `NR-20261026-wall-vs-memory-no-wall-porous`, `NR-20261028-wall-vs-memory-bounded-random-fresh-compact`.
- Scope comparison: the first covers EF = 1 / EV = 0 on the six core rules only (not members: different rules; its
  "Not permitted" list names intermediate EF and forced L). The second covers `fs:RULE:RU` / `fs:RULE:LU` (bounded sets)
  on cohort A and B; this test uses R/L sets with a leak (unbounded fresh runs at EF > 0) on cohort B rules, so no spec
  is a member. The EF = 0 rows are deliberate replication gates of committed Stage 3b rows.
- Decision: run.
- Run spec and exclusions: `results/specs.txt`, `results/spec_roles.csv`, `results/cohorts.csv` (14 exclusions, each with its reason; no signature-based exclusion).
- Compute/stopping budget: above. A lag would warrant a mechanism test (fresh-run length versus revisit-turn agreement,
  Q41 Stage C); no lag closes Q42's handedness half.

## Reproduction

From the repository root (Linux; `UV_PROJECT_ENVIRONMENT=$HOME/.venvs/turmite UV_LINK_MODE=copy`, Rust from `~/.cargo`):

```sh
uv run --frozen python experiments/active/2026-11-leak-handedness-cohort/scripts/select_specs.py   # specs, roles, cohorts
uv run --frozen python experiments/active/2026-11-leak-handedness-cohort/scripts/calibrate.py      # results/calibration.txt
RAYON_NUM_THREADS=3 sh experiments/active/2026-11-leak-handedness-cohort/scripts/run.sh experiments/active/2026-11-leak-handedness-cohort/scratch/rerun  # fresh, gitignored dir; compare bytes
uv run --frozen python experiments/active/2026-11-leak-handedness-cohort/scripts/analyse.py        # runs.csv, rules.csv, analysis.txt
uv run --frozen python experiments/active/2026-11-leak-handedness-cohort/scripts/posthoc.py        # POST HOC, results/posthoc.txt
cargo test --release --locked --test fresh_set                                                     # code oracle
```

The run (`results/provenance.txt`): commit `19e4aa0` (registration; `run.sh` was not yet committed, it is `add989a`), rustc 1.99.1,
probe sha256 `3f5416b7...`, 2708 specs on 3 threads, 2026-11-12 08:59-09:20 NZDT (21.5 min), `probe.csv` sha256 `e09b8ea6...`.
The folder was registered in `proposed/` and moved to `active/` after the run (`experiments/_migration/2026-11-12-leak-handedness-cohort.tsv`),
so the command recorded in `provenance.txt` names the old path. `analyse.py` gives byte-identical output on re-run and under `PYTHONHASHSEED=7`.

## Results, uncertainty and limitations

Scored output: `results/analysis.txt` (per run `results/runs.csv`, per rule `results/rules.csv`).

**Gates.** G1 PASS: all 172 EF = 0 rows are identical to the committed Stage 3b rows (built with rustc 1.97.0; this run 1.99.1).
G2 PASS: at EF = 1 the two arms agree, mean d = -0.0015 and |d| <= 0.06 in 77/77 rules. Code oracle: `fresh_set` 4/4 passed.
All 77 cohort-C rules were scoreable.

**P1 (handedness lag): UNRESOLVED.** Median Lambda = +0.023, rule-bootstrap 95% [-0.158, +0.186], n = 77; Lambda > 0 in 41/77.
Descriptive: median rise fraction at EF 0.3 is 0.35 (arm R) against 0.30 (arm L); at EF 0.5, 0.64 against 0.63.
So the cohort shows no consistent lag in either direction, but the interval is far too wide for the registered "no lag" verdict
(the calibration expected a half-width near 0.02).

Why the interval is wide is the main finding, and it was not anticipated by the calibration. The calibration assumed every rule
shares one lag with a rule-level spread of 0.05. In the data the spread of Lambda across rules is **sd 0.38** (quartiles -0.29 / +0.30;
|Lambda| > 0.4 in 24 of 77 rules), while seed noise on one rule's Lambda is only about 0.06-0.07 (`results/posthoc.txt`: split-half across seeds, r = 0.93-0.96;
*2026-11-16: this replaces a median-Delta back-of-envelope figure of ~0.05, see Review fixes below*). The handedness of
the base turn changes leak tolerance strongly **rule by rule**, in both directions, and the effects cancel in the median.
This is a defect of the registered design (a cohort-median test cannot see a rule-dependent sign), stated here rather than repaired.

**P2 (ordered-L collapse): FAIL.** Arm L at EF 0.1: cohort E porous 9/36 = 0.25 (needed >= 0.50; 3 further runs escaped), cohort C
porous 0/308 (needed <= 0.10, held). The E half failed. Within-rule control: arm R at EF 0.1 on cohort E gave 0 porous of 36.
The collapse is all-or-nothing by rule: three E rules (`RLLLRLLLL`, `RLLRLLLRLRL`, `RLLRLLLRRRL`) are porous or escaping in every
arm-L run (mean a 0.90-0.95) and compact in every arm-R run; the other six stay compact or intermediate (mean a 0.69-0.77).
So the six-rule observation (forced-L highway rules go straight to porous at a 10% leak) generalises to 3 of 9 forced-L escaping rules,
not to escaping rules as a class.

**Post hoc, not registered** (`scripts/posthoc.py`, written after P1 came out unresolved; one of several possible looks, uncorrected):
Lambda tracks rule composition. Spearman(Lambda, fraction of R letters) = +0.40 (p = 0.0003). Rules with fewer than 45% R have median
Lambda -0.21 (base R tolerates the leak better); rules with more than 55% R have +0.18 (base L tolerates it better). The extremes are
the prefixes: all 7 `RRRR...` rules have Lambda > 0 (median +0.54) and 12 of 14 `RLLL...` rules have Lambda < 0 (median -0.38). Read
literally, the leak does less damage when the forced fresh-ground turn is the *minority* turn of the rule's own table. That is a
pattern to test, not a finding: it was found by looking, composition and prefix are confounded, and the three P2 collapse rules
also start `RLL` (a forced-L base on an L-heavy rule), which fits the same reading.

**Limitations.** Finite window (early a over k = 12..22, board 16384); 4 seeds; the two-point rise fraction is not an EF_50; the
cohort is the Stage 3b sample of core-class rules, so nothing transfers to other classes. Escapes at EF = 1 (62 of 616 runs) and
EF = 0.5 (2) have no early fit; every rule kept >= 3 of 4 fits where required.

## Review fixes (2026-11-16, PR #38 review; no new data, no new runs)

- **S1, write order (correction).** The registration line above says it came "before the run or analysis scripts were written",
  and the NOTEBOOK says "before writing `run.sh` or `analyse.py`". That is false as written: both scripts were **drafted before**
  the registration commit `19e4aa0` (08:58:54 +1300) and **committed after** it (`add989a`, 09:00:19 +1300), and `run.sh` was
  already executing at 08:59:16. Accurate statement: drafted before, committed after; not run on cohort data before registration.
  The statistics and thresholds were frozen in this README at `19e4aa0`, so the scoring is unaffected. The run's recorded
  commit `19e4aa0` does not contain the `run.sh` that ran, and `dirty 0 tracked files` could not see an untracked script, so
  nothing in `provenance.txt` ties `add989a`'s `run.sh` to the run. Future `run.sh` files record `sha256sum "$0"` and
  `git status --porcelain` including untracked files under the experiment folder (process fix in `notes/ACTIVE.md`).
- **S2, heterogeneity on a firmer footing.** `scripts/posthoc.py` now adds a reliability section (still post hoc, same committed
  data): Lambda recomputed from disjoint seed halves correlates across the 77 rules at r = 0.933 / 0.940 / 0.959 for the three
  splits, implying seed noise of 0.056-0.072 on full Lambda against a between-rule sd of 0.383. The unnormalised
  abar_L - abar_R (EF 0.3/0.5 mean) has between-rule sd 0.065 against split-half noise 0.013, so the spread is not an
  artefact of dividing by small Delta (Spearman(|Lambda|, min Delta) = -0.47, which is why the old median-Delta figure was
  too low). Composition survives regressing out a0_R - a0_L (R^2 0.045; residual Spearman with R fraction +0.42, p = 1.5e-4).
  The rule-dependent sign is therefore well above seed noise; the composition reading stays an untested post hoc pattern.
- **S3, size of `results/probe.csv` (6.3 MB).** Kept, deliberately: it is the raw input from which `analyse.py` derives every
  scored number, and gate G1 (and any re-simulation check) compares against it row by row. It can be regenerated from
  `results/specs.txt` in about 21 min on 3 threads, and its sha256 (`e09b8ea6...`) is pinned in `provenance.txt`. The same
  justification was used for the wall-vs-memory probe CSVs. If the owner prefers, it can move to a gitignored `dumps/` with
  `runs.csv` and the hash retained.
- **M1.** The re-simulation directory is now the experiment's own gitignored `scratch/rerun` (repository-root `scratch/` is not ignored).
- **M2.** `posthoc.py` no longer carries a PEP 723 header; all its dependencies are locked project dependencies, so it runs
  with `uv run --frozen python` and reproduces `results/posthoc.txt` offline.
- **M3.** G1's "byte-identical" (registration text, left unchanged) is checked by `analyse.py` as parsed polars frames
  (`DataFrame.equals`): read it as **identical field for field**, not raw bytes. The blog post now says so.
- **M4.** `analyse.py` locates the Stage 3b CSV from the repository root (`parents[4]` plus a repository path) instead of a
  sibling-relative path; re-running it gives byte-identical outputs.
- **M5 (what I'd do differently).** The calibration assumed a rule-level lag spread of 0.05, but the only prior data (three
  leak-titration rules, one P4 miss above 0.1 in EF_50) gave no basis for a value that small. The next registration should
  calibrate against a heterogeneous-sign alternative, not just against one shared lag with small spread.
- **M6.** The homepage card now names the condition in each sentence (compactness under forced turns at no leak did not depend
  on handedness; under a partial leak handedness matters rule by rule).
- **N1.** Commit `a2c9494` is an empty commit made only to re-trigger stuck CI; it is not a revision of the experiment record.
- **Open review questions.** Whether the three P2 collapse rules share a forced-L highway type, and whether a follow-up sign
  predictor is fixed from rules outside cohort B, are not answered here (the second is taken up by PR #39).

## Pruning-index outcome and next question

No dead-end signature. P1 is unresolved (not a controlled null), and the P2 failure is a failed generalisation of a descriptive
observation, not a disproved mechanism.

Next question (Q42 update in `notes/open-questions-hypotheses.md`; not registered): **does a forced fresh-ground turn tolerate
leak better when it is the rule's minority turn?** A registered test should fix the sign prediction per rule from its table
(e.g. sign of Lambda = sign of (#R - #L), or of the second-run letter), test it on rules outside cohort B, and use a per-rule
sign-agreement statistic rather than a cohort median. A mechanism would have to say why the forced turn's agreement with the
interior turn statistics sets how much leaked fresh ground the boundary can absorb; the fresh-run length distribution (Q41,
Stage C) is identical in law for the two arms, so a lag of either sign is evidence against the bound being the whole story.
