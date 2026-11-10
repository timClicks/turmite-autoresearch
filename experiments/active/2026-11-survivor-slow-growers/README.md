# Do the 702 late survivors include slow or bounded growers, and do highways come from them?

Registered 2026-11-10 09:15 NZDT (+13:00), base `251100a2f99f81099954ebd147dea11ea173e337`, branch `agent/survivor-slow-growers`.
Status: **MEASURED** (P1, P2 held; P3 failed on 1 of 8). Registered with nothing measured beyond the exploratory look stated below; moved from `proposed/` to `active/` on 2026-11-11 once results existed.
Phase priority 2 (regime validation: censoring and selection bias in the late-highway hazard cohort). Answers the open item in
`notes/ACTIVE.md` ("whether the 702 include bounded rules (RLLLLLR is 42x42 at 1e11)") and feeds Q19.

## What I already looked at (exploratory, not a test)

Before registering I computed, for the 702 `stop=budget` rows of the 1e11 census
(`experiments/archive/2026-10-highways-unresolved-rules-1e10-1e11/results/h1e11/`), the side growth over the last decade,
`g11 = log10(side(1e11)/side(1e10))` with `side = max(width, height)`, using `h1e10/` for the 1e10 boxes. The distribution is
bimodal: 528 rules in the 0.25-0.35 bin (cube-root growth of the side predicts 1/3), 143 rules below 0.2 (50 at 0.00-0.05, many
with sides 30-150 cells), and a few above 0.4. The gap between ~0.15 and ~0.25 is nearly empty, so the class cut 0.2 is chosen from this
look. **Everything below uses data I have not yet looked at in relation to this class** (1e8 and 1e9 boxes; which rules became
genuine highways; new longer runs).

## Classes (frozen now)

`scripts/classes.py` (stdlib) -> `results/classes.csv`: `slow` if `g11 < 0.2`, else `growing`. Result: 143 slow, 559 growing.
sha256 `classes.csv` 40b5533e...5d84123f, `p3_sample.txt` dfe4c858...2c44dd.

## Hypotheses

* **H-slow (my prior ~75%):** the survivors are a mixture: a cube-root-growing majority and a distinct slow class (bounded or
  much slower than t^(1/3)) that stays slow. The slow class is not at risk of the late highways seen so far.
* **H-pause (competing):** "slow" is a transient pause of ordinary cube-root growers (a rule that sat still for a decade resumes),
  so classes do not persist across decades and highways arise from both classes in proportion.

## Registered predictions

Notation: `g10 = log10(side(1e10)/side(1e9))`, `g9 = log10(side(1e9)/side(1e8))`; 1e8 boxes from
`experiments/archive/2026-10-census-sweeps/results/sweep_v2.csv` (board as recorded in that census), 1e9 boxes from `sweep_1B.csv`, 1e10
from `h1e10/`.

* **P1 (persistence, both directions).** Among the 143 slow rules, >= 90% have `g10 < 0.2`; among the 559 growing rules, >= 90%
  have `g10 >= 0.2`. Fails if either fraction is below 90%. H-pause predicts both fractions near the overall class shares
  (about 20% / 80%), i.e. a failure.
* **P2 (where highways come from).** Of the genuine late highways with onset in (1e9,1e10] (16 rules) and (1e10,1e11] (12 rules),
  as listed in `experiments/archive/2026-10-late-highway-board-check/results/classify.txt` (status table), at most 1 of 28 was
  slow in the decade before its onset decade (`g9 < 0.2` for the first cohort, `g10 < 0.2` for the second). Under H-pause, with a
  slow share of about 0.2, the expected count is about 5.6 and P(X <= 1) is about 0.02. Fails if X >= 2.
* **P3 (do they stay put?).** The 8 slow rules in `results/p3_sample.txt` (first 8 of the slow class by sha256("survivor-slow:"+rule))
  are re-run from a blank board to 2e11 steps. Prediction: all 8 have `side(2e11)/side(1e11) <= 1.05` (cube root predicts 1.26),
  none escapes and none forms a highway. Fails if any ratio exceeds 1.05 or any rule escapes or forms a highway.
  Measurement check T1: the 2e11 run must reproduce nothing contradictory with the census (it cannot check 1e11 directly; recorded
  as a limitation, not a test).
* **Consequence, not a hypothesis:** if P1 and P2 hold, the at-risk pool for Q19 is the growing class, and the per-decade yields
  are recomputed on growing-only denominators (`results/yields_growing.txt`). The Q19 registered 1e12 prediction ("about 12 of
  702") becomes "about the same count among about 559", so its expected yield per rule rises by about 702/559 = 1.26x. No Q19
  decision rule is changed here; Q19 remains registered and un-run.

"Bounded" is not claimed by any of these tests: a ratio of 1.0 over one doubling is compatible with a rule growing as a log or a
very small power. The deliverable is "slow class persists and is not the source of late highways", or its failure.

## Pruning-index preflight

* Index revision `251100a2f99f81099954ebd147dea11ea173e337`. Commands: `ls notes/pruning-index/entries`;
  `rg -n -i -e bounded -e survivor -e slow -e at-risk -e hazard notes/pruning-index/entries`.
* Candidates: `NR-20261025-crawler-window-single-letter` (mentions survivor filtering, unrelated objective) and
  `NR-20261028-wall-vs-memory-bounded-random-fresh-compact` ("bounded" refers to fresh runs of a random walker). Neither covers
  the late-survivor cohort or highway hazard. No match is a recorded outcome, not evidence of novelty.
* Decision: **run**. Compute budget: P1, P2 are reads of committed CSVs; P3 is 8 rules x 2e11 steps, 4 at a time, about 40 min
  wall on 4 cores (1.8e8 steps/s/core measured by Q19 T2). Stop after P3 whatever it shows; any longer run (bounded check by exact
  recurrence, 1e12) needs its own registration.

## Reproduction

```bash
python3 experiments/active/2026-11-survivor-slow-growers/scripts/classes.py
cargo build --release --locked --bin sweep_lean
bash experiments/active/2026-11-survivor-slow-growers/scripts/p3_run.sh
uv run --frozen experiments/active/2026-11-survivor-slow-growers/scripts/analyse.py
```

## Results, uncertainty and limitations

* **P1 HOLD**, **P2 HOLD** (`results/analysis.txt`).
* **P3 FAIL** (`results/p3_analysis.txt`, `scripts/p3_eval.py`): 7 of 8 slow rules had `side(2e11)/side(1e11) <= 1.05`; RLRLRRRR
  reached 1.086 (140 -> 152). None escaped or formed a highway; all stayed far below the cube-root 1.26.
* Limitation: 8 rules over half a decade cannot tell bounded rules from very slow growth; the slow class is "slow", not "bounded".
  The second P3 batch's start time is unlogged (see NOTEBOOK).
