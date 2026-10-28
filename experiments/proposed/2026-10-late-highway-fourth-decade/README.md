# Q19: is the late-highway yield per decade flat? A fourth decade, (1e11, 1e12]

Registered 2026-10-25, base `df07dfe`, branch `ccr-9a56d193-javkym`. Status: **REGISTERED; design and power analysis done, no 1e12 run started.**

## Question and registered prediction

Q19 (`notes/open-questions-hypotheses.md`): the corrected genuine late-highway yields among survivors are 12/854 = 1.41% in
(1e8, 1e9], 16/807 = 1.98% in (1e9, 1e10] and 12/732 = 1.64% in (1e10, 1e11]
(`experiments/archive/2026-10-late-highway-board-check/`). Is the per-decade yield constant ("chaotic" is a transient for a fixed fraction
of rules per decade, without end), or slowly falling?

* **H-flat (my prior, ~55%):** per-decade yield p = 40/2393 = 1.67% (pooled), so a random m of the 702 survivors at 1e11 should
  contain 0.0167 m highways with onset in (1e11, 1e12].
* **H-fall:** yield falls by a factor f per decade, f in {0.7, 0.5, 0.3}, so p = 1.17%, 0.83%, 0.50%.
* **Genuine** means the `late-highway-board-check` criteria: not a board filler (escape footprint < 0.99 of the board side in both
  directions), and the same period, drift and onset on a second, larger board.
* **Decision rule (frozen now):** exact one-sided binomial test of the observed count X in the run sample of size m against
  H-flat with p = 0.0167, alpha = 0.05 (reject flat if X <= cut(m)). Report X/m with an exact (Clopper-Pearson) 95% interval
  regardless. Not rejecting is **not** support for flat; say "inconclusive at this power".
* **Power (`scripts/power.py`, arithmetic only):** the test is weak.

| m run | E[X] if flat | cut | power vs x0.7 | vs x0.5 | vs x0.3 | core-hours (2 / 1.5 / 1 e8 steps/s) |
|---|---|---|---|---|---|---|
| 48 | 0.8 | none | 0.00 | 0.00 | 0.00 | 67 / 89 / 133 |
| 100 | 1.7 | none | 0.00 | 0.00 | 0.00 | 139 / 185 / 278 |
| 200 | 3.3 | 0 | 0.09 | 0.19 | 0.37 | 278 / 370 / 556 |
| 350 | 5.9 | 1 | 0.08 | 0.21 | 0.48 | 486 / 648 / 972 |
| 702 | 11.7 | 5 | 0.17 | 0.47 | 0.86 | 975 / 1,300 / 1,950 |

  **Consequence, stated before spending compute:** even the full 702 at 1e12 has under 50% power against a halving per decade;
  only a collapse (x0.3 or worse) is likely to be seen. Partial samples can only estimate the yield (wide interval), not test it.
  The honest deliverable of any feasible stage is an interval for p, to be pooled with the three earlier decades in a
  log-linear trend fit (slope of log yield per decade with its interval), not a flat/falling verdict.
* **Further registered predictions (measurement checks, not hypotheses):**
  T1: tiled `sweep_lean` is byte-identical to dense on the first rules of the sample (met on 2 rules at 3e9, below).
  T2: throughput at 3e9 steps is 1.5-2.2e8 steps/s/core with 4 parallel workers and peak RSS < 100 MiB each (met: 179-188 Msteps/s, 11-16 MiB).
  T3 (open): throughput at 1e12 stays >= 1.0e8 steps/s/core and the footprint on a 65536 board stays below 0.99 of the side for
  the non-filler survivors (the 1e11 widths are 5.5k-12k cells; cube-root growth predicts 1.2-2.6x more at 1e12, i.e. under 31k).

## Pruning-index preflight

* Index revision: `df07dfe58faa93579d1b27a2436c4f0f7c0141db`. Commands: `git rev-parse HEAD`; `rg --files notes/pruning-index/entries`;
  `rg -n -i -e highway -e late -e yield -e unresolved -e decade notes/pruning-index/entries`.
* Candidates: the only entry is `NR-20261022-additive-laws-order-blind`; it matches "highway/late" words only in unrelated
  context (additive conservation laws, objective: order-sensitive invariants). No match for late-highway yield. A no-match is a
  recorded outcome, not evidence of novelty.
* Scope: all 702 survivors of the 1e11 sweep, unchanged rule family, blank background, plain ant, objective = yield of new highways.
* Decision: **run** (no signature covers it). Compute/stopping budget: see "Stages"; a null at partial power does not warrant a dead-end signature.

## Design

* **Population:** the 702 `stop=budget` rows of `experiments/archive/2026-10-highways-unresolved-rules-1e10-1e11/results/h1e11/chunk_*.csv`
  -> `results/survivors_1e11.txt` (sha256 `4496fd16...b5f74c`). Note it is a 32768-board census: survivors are rules that neither
  escaped nor showed a highway by 1e11.
* **Sample:** nested prefixes of `results/sample_order.txt`, rules sorted by sha256("q19-fourth-decade:" + rule)
  (`scripts/order.py`; sha256 `70ca50da...cdd721f41`). Any prefix is a uniform random subsample, and stages can be pooled without re-drawing.
* **Instrument:** `sweep_lean` with `TURMITE_GRID=tiled` (sparse tiles, unlimited cache), 65536 board, 1e12 steps, one thread per
  rule, four rules at once, checkpoints every 5e9 (`scratch/ckpt`, gitignored). Tiled is required: a dense 65536 board is 4.3 GB
  per worker and 15 GB RAM would allow 3.
* **Runs restart from step 0** (the 1e11 chunks left no committed checkpoints), so the cost is the full 1e12 per rule: ~1.5 h per rule per core at 1.85e8 steps/s.
* **Confirmation of any hit:** re-run on a 131072 board (tiled) and compare period, drift and onset (the `confirm` criterion);
  classify escapes by footprint as in `late-highway-board-check/scripts/classify.py`.
* **Known blind spot:** a rule whose structure is a highway fed by something outside the 65536 board is still an escape, not a
  highway; rules with a >1e12 onset are censored. This measures the yield in one decade, not the tail.

## Stages (compute is the decision for the user, not for the agent)

| stage | rules (prefix) | wall on 4 cores | what it can say |
|---|---|---|---|
| A | 1-48 | ~18 h | throughput/footprint at 1e12 (T3), interval for p with E[X] = 0.8: essentially "how many to expect" |
| B | 49-200 | ~57 h | with A: m = 200, E[X] = 3.3, cut 0, power 0.19 vs x0.5 |
| C | 201-702 | ~190 h | full population, power 0.47 vs x0.5; a GPU is not usable (no batch instrument) |

## Reproduction

```bash
uv run --frozen experiments/proposed/2026-10-late-highway-fourth-decade/scripts/power.py
python3 experiments/proposed/2026-10-late-highway-fourth-decade/scripts/order.py
cargo build --release --locked --bin sweep_lean
bash experiments/proposed/2026-10-late-highway-fourth-decade/scripts/run_stage.sh FIRST LAST     # 1-based inclusive range of sample_order.txt
```
`run_stage.sh` is resumable: finished rules (`results/runs/RULE.csv`) are skipped and interrupted ones resume from `scratch/ckpt`.
Provenance (commit, binary sha256, start/end) is appended to `results/runs/stage.log`.

## Results

### Calibration at 3e9 steps (2026-10-25; commit `df07dfe`, binary sha256 `c9dee7ca...cc7e1`, rustc 1.97.0)
First four rules of `sample_order.txt` (RRRRLLLRL, RRRRLRLLRL, RLRLLLRRLR, RRLRLLLRL), tiled backend, 65536 board, four processes in parallel,
one thread each: 188 / 182 / 184 / 179 Msteps/s, peak RSS 11-16 MiB, all `budget` with widths 1.7k-2.7k (`results/throughput_check_3e9.csv`).
Dense output equals tiled byte for byte for the first two rules. n = 4: a throughput calibration only, no highway statistic.
Stage A-C results: **none yet.**

## Pruning-index outcome and next question

None yet. A null result here would be a well-controlled but under-powered observation (see table); it must not be recorded as a dead end.
Next questions this sets up: Q15/Q20/Q23 (what builds the late structures) and whether a cheaper observable than the full 1e12 run
(shared-prefix trajectory deduplication, or an onset-hazard model fitted to the 40 known onsets) can add power for free.

## Addendum 2026-10-25 (appended before any 1e12 run; the registration above is unchanged)

**Decision (user, 2026-10-25): do not spend the 1e12 compute; improve power from existing data first.** Two free levers, both measured:

1. *Shared and trapped trajectories.* 52 of the 702 survivors fall into 21 groups with identical (width, height) at 1e11 (at most 31 reruns
   saved, 4%, and only if the trajectories really are identical, unverified); only **3** survivors have an unchanged bounding box between 1e10 and
   1e11, and the 130 small-box survivors (<= 300 cells) still grow at the cube-root rate (median width ratio 1e11/1e10 = 2.13 against 2.15 predicted).
   So there is no trapped class to drop from the denominator, and trajectory sharing is worth about 4%. Negative result; not a dead-end signature
   (it is a cost observation, not a claim about dynamics). Command: inline Python in the session log; the counts are reproduced by `scripts/hazard_all_decades.py` inputs, not saved.
2. *Use the whole census, not three decades* (`scripts/hazard_all_decades.py` -> `results/hazard_all_decades.txt`, `results/hazard_by_decade.csv`;
   `scripts/trend.py` -> `results/trend.txt`). Population: the 1013 rules of length <= 10; a decade is the decade of the highway **onset**;
   at risk = no highway and no escape yet; the 26 board artefacts of `late-highway-board-check` are excluded.

| onset decade | 1e2 | 1e3 | 1e4 | 1e5 | 1e6 | 1e7 | 1e8 | 1e9 | 1e10 |
|---|---|---|---|---|---|---|---|---|---|
| at risk | 971 | 945 | 928 | 911 | 896 | 879 | 856 | 807 | 732 |
| highways | 26 | 17 | 17 | 15 | 17 | 23 | 11 | 16 | 12 |
| hazard % | 2.68 | 1.80 | 1.83 | 1.65 | 1.90 | 2.62 | 1.29 | 1.98 | 1.64 |

(1e1 decade: 42 of 1013 = 4.15%, a start-up transient.) Poisson-likelihood fit of hazard ~ p0 f^k (f = factor per decade; 1 is flat):
**k = 2..10: f = 0.97 [0.91, 1.03]; k = 3..10: 1.00 [0.92, 1.08]; k = 5..10: 0.98 [0.87, 1.11]; k = 8..10 (the three decades of the board check): 1.13 [0.76, 1.66];
k = 1..10: 0.92 [0.88, 0.97]** (the apparent decline is the 1e1 transient). The windows were chosen after seeing the table: **exploratory**.
The highway **count** per decade is also constant: 17, 17, 15, 17, 23, 11, 16, 12 for 1e3..1e10 (mean 16.0, variance 13 against Poisson 16).

**Interpretation (not tested).** Onset times of length <= 10 highways look log-uniform over eight decades: a scale-free process, not a thinning tail.
My earlier framing of Q19 ("a halving per decade fits") is already excluded by the census, because the board-check README used only the last three decades.
What remains open is whether the log-uniform onset persists beyond 1e11 and how it relates to Q17 (onset grows only 0.018 decades per cell of highway size).
Strong reasons for caution: (i) a finite pool (1013 rules, 28% depleted by 1e11) is a weak test of heterogeneity, because even a subpopulation with a fixed
chance of forming a highway would be depleted by only a fraction of itself in 10 decades, so a flat hazard does not prove the supply is infinite;
(ii) `sweep_v2`/`sweep_1B` boards were never put through the second-board confirm test; (iii) fit windows post hoc; (iv) length <= 10 only.

**Registered prediction for (1e11, 1e12] (written now; no 1e12 run exists).** Using the k = 3..10 fit (f = 1.00): hazard 1.8% per at-risk rule, so about **12 highways among
the 702 survivors** (Poisson 95% range 7-20, adding fit uncertainty ~6-21). A run of all 702 that found 5 or fewer would reject flat (`power.py` cut) and would
contradict this extrapolation. Incremental value of that run: it would move the 95% interval of f from [0.92, 1.08] to roughly [0.93, 1.07]: a small gain for ~1,000-2,000 core-hours,
so the stages above are **not recommended** unless the decade is wanted for its own sake (as an out-of-sample check, or to catalogue the highways, which would be new data). Stage runner and sample order stay in place.

Q19 status: **partly answered, exploratory**: flat to within about +-8% per decade (95%) over 1e2-1e11 on length <= 10; the 1e11-1e12 decade is a registered, un-run prediction.

*Appended 2026-10-25 (prefix-causal-horizon):* the 52 rules in 21 equal-box groups mentioned in point 1 above are **not** shared trajectories: all 42 pairs separate by step 45 (prefix lemma, `experiments/archive/2026-10-prefix-causal-horizon/`). The possible 4% saving is therefore zero; the equal boxes are a separate, unexplained coincidence (Q25).

