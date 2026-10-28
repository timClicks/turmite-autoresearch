# Is a chaotic edge a broken crawler? The crawler's cost per birth as a ceiling for the c law

Registered 2026-10-25 23:30 (+13:00), base commit `56aac50`. **No registered measurement has been run** when this file
is first committed. Everything I looked at beforehand is listed under "Seen before registering".
Author: Kea (AI research agent, Claude). Open questions: the unexplained c-law coefficients (`a ~ 1.36`, `b ~ 0.70`) and
"why letters 5-8 matter" (`experiments/archive/2026-10-kappa-chiral-edge`, C4; `experiments/archive/2026-10-c-law-mechanism`,
closing entry), and Q20/Q15 (`notes/open-questions-hypotheses.md`).

## Question

The square-ring crawler (`experiments/archive/2026-10-square-ring-fillers`, lemma proved for all k >= 1) is an exact,
ordered solution for a growing straight edge. Every cell it creates costs `2(k+1)` steps. The chaotic rules obey an
empirical edge law, `1/c = 1.363 + 0.696 m`, where `c` = births / boundary steps and `m` is the opening same-letter run
(the lead). The law transfers to fresh rules and to a flat band with an i.i.d. interior, and it does **not** depend on
the interior's colours (c-law-mechanism Stage 2c: all-zero, young-only and old-only interiors change c by 0.3%). So `c`
is set by an edge layer that the ant builds for itself. The crawler is one such layer, built perfectly. Does the
crawler's exact accounting say anything about the chaotic one?

## The crawler's edge accounting (derived from the lemma; checked numerically in P0)

Use the edge tracer's definitions (`src/edge_trace.rs`). A *boundary read* starts on a visited cell with an unvisited
4-neighbour, and a *birth* is a step onto a never-visited cell. `r_j` = boundary reads at colour `j` per birth, so
`1/c = sum_j r_j`.

The crawler's period has `8(k+1)` steps and 4 births: a chain of three (plaquette P, three fresh cells and one shared
cell) and a chain of one (plaquette Q, one fresh cell and three shared cells). Each fresh cell is read at counts
`0..k-1` while its plaquette is circled, then at `k` (the L that ejects the ant), all while it still has an unvisited
neighbour. Its later reads `k+1..2k+1` happen as a *shared* cell of the next pass's plaquettes. By then the next row
has been born, so all of these reads but one in four are interior. Hence

    r_j = 1 (0 <= j <= k),   r_(k+1) = 1/4,   r_j = 0 (j >= k+2),   1/c_crawler = k + 5/4,

with birth chains of length 1 and 3, half each, and none of length 2. A blank-board tracer run at 2^22 steps showed
exactly this profile for `R^5 L R^6` and `R^7 L R^8` (see "Seen before registering").

Set this against the chaotic law at `m = k`:

    crawler: 1/c = 1.25 + 1.00 m          chaotic: 1/c = 1.363 + 0.696 m

The intercepts agree within 0.11. The slope is the naive "2x2 loop" slope `b = 1`, which C3 of the chiral-edge
experiment rejected for chaotic rules (that picture also had `a = 0`; the crawler shows that `b = 1` comes with
`a = 5/4`, not 0). So, read through the crawler, **a chaotic edge spends 30% fewer boundary reads per lead step than a
perfect crawler**, and its intercept is the crawler's.

## Hypothesis H-crawl (registered)

A chaotic edge is a fragmented crawler. Fresh plaquettes are circled as in the crawler, at a cost of one boundary read
per birth per circulation. A circulation breaks when a non-fresh (shared) cell of the plaquette reads a letter other
than `s_0`. In the crawler, the shared cells are young edge cells at counts `m+1..2m+1`, and the rule supplies `s_0` at
exactly those counts: the membership predicate `Pi(m)` (`T(v) = R` for `v` in `[0, 2m+2]` except `T(m) = L`; the
corner reads `2m+2`). The 30% shortfall is the circulation lost to unsupported shared cells. The crawler,
`1/c = m + 5/4`, is the ceiling that full support reaches.

This makes two kinds of prediction that the lead law alone does not:

1. **Crawler limit.** Chaotic rules that satisfy `Pi(m)` have the crawler's full local turn table, but they do not
   settle into a ring. There are 40 such stationary census blobs with `m >= 2`, and all 40 are "other" in the
   square-ring P6 classification to about 1.3e8 steps. Their edge should be crawler-like, with `1/c` near
   `m + 5/4`, above the lead law.
2. **A lead-dependent letter window.** Letters at positions `p` in `[m+1, 2m+1]` (the shared-cell window) should
   matter more for `c` than letters at `p >= 2m+3`, and the window should move outward as `m` grows. This is a
   candidate mechanism for C4's "information keeps accumulating with each early letter", with a horizon that depends
   on `m`.

## Competing explanations

- **H-young.** Circulation is supported by shared cells that are themselves young (colour `< m`), so letters after
  the lead hardly matter for circulation. `Pi` membership is then irrelevant: Pi-blobs sit on the lead law, and
  single-letter flips show no lead-dependent window.
- **K3-generic** (c-law-mechanism Stage 1). The influence of a letter decays smoothly with its position through a
  fitted survival kernel that does not depend on `m` beyond the lead. This predicts no step at `2m+1` and no outward
  movement with `m`.
- **Composition.** `Pi(m)` rules carry many `s_0` letters, so any "more R letters means more circulation" effect would
  mimic prediction 1. P1b controls for this by matching composition. The flip design (P2) changes composition by
  exactly one letter in every arm.

## Seen before registering (disclosure)

- The whole record of the c-law experiments (chiral-edge, c-law-mechanism, c-law-renewal, both lattice c-law
  experiments), the square-ring fillers README and results, and the P6 classification of the 40 Pi-blobs (class labels
  only).
- **Exploratory tracer runs** (2026-10-25 ~23:00; `c_law_mechanism_trace blank 22 2048`, minimal rules
  `R^k L R^(k+1)`, k = 1..8; output not kept): `1/c` = 2.320, 3.175, 4.089, 5.149, 6.241, 7.061, 8.231, 8.972. For
  k = 5 and 7 (ring fillers), the r-profile was exactly the crawler's. For the others (not fillers), chain-2 events made
  up about 10-30% of chains. **Three of the 40 P1 rules (`RRLRRR`, `RRRLRRRR`, `RRRRLRRRRR`) were in this run.** Their
  tracer `1/c` lies at about 0.8-0.9 of the way from the lead law to `m + 5/4`. This is why I give P1 high odds. P1 is
  also scored without these three rules. I have not looked at the census `c` of any P1 rule, or at any tracer output
  for the other 37.
- Cohort counts by lead and `Pi` membership (rule strings only, no outcome).

## Predictions (registered before any run; my honest odds)

**P0 calibration (exact).**
- **P0a.** An independent Python simulation of the crawler configuration `C_k` on a strip (k = 1..8, 64 periods) gives
  exactly `r_j = 1` (j <= k), `r_(k+1) = 1/4`, 0 otherwise, `1/c = k + 5/4`, and chains {1: 1/2, 3: 1/2}. ~90%.
- **P0b.** The edge tracer on the 25 census board fillers (blank, 2^27 steps, board 8192, window [2^26, 2^27], the
  square-ring P2 setting, where all 25 are in the ring regime) gives `|1/c - (k + 5/4)| <= 0.05` and a chain-2 share
  `<= 0.02` for every rule. ~80%. A failure here would mean the instrument and the derivation disagree, and P1-P3 would
  be read with that caveat.

**P1 crawler limit (census `c`, `probe_summary.csv`, seen-but-never-analysed data).** Cohort: the 40 stationary census
blobs (`cls == blob`, `c > 0`, `|g_k| < 0.05`) with `Pi(m)` and `m >= 2`. Write `LL(m) = 1.363 + 0.696 min(m, 8)` and
`phi = (1/c - LL(m)) / (m + 5/4 - LL(m))`, so 0 = on the lead law and 1 = on the crawler line.
- **P1a.** median `phi` >= 0.5 (all 40, and separately without the 3 seen rules). ~70%.
- **P1b.** Composition-matched controls are stationary blobs with the same `m`, the same `n` and the same number of
  `R`s that are not `Pi`. For each Pi rule I draw up to 3 controls (seed 20261025); if none exist, I relax `n` by ±1,
  then the R-count by ±1. The test: median `phi`(Pi) minus median `phi`(controls) >= 0.3, with a 95% bootstrap CI over
  Pi rules (2000 resamples, seed 20261025; controls resampled with their Pi rule) whose lower bound is above 0. ~65%.
- **P1c (ceiling).** At most 10% of the 40 have `1/c > m + 5/4 + 0.10`. ~50%. This is a bold claim: no fragmented edge
  spends more boundary reads per birth than a perfect crawler. Hole rims could break it.

**P2 window (new tracer runs, single-letter flips).** Parents: stationary census blobs with `n` in 10..12, not `Pi`,
30 per `m` in {1, 2, 3} (seed 20261025). Mutants: each parent with one letter flipped at every position `p` in
`[m+1, n-1]`. The lead and the canonical first letter are unchanged; non-primitive mutants are dropped. Tracer:
`blank 24 4096`, window [2^23, 2^24]. A run is kept if it does not escape, has births >= 200 and has
1.3 <= area/area_t0 <= 1.9 (the c-law V filter). Effect `e = |1/c_mut - 1/c_par| / (1/c_par)`. Position classes:
window `W = [m+1, 2m+1]`, corner `2m+2`, far `F = [2m+3, n-1]`.
- **N0 (noise gate).** Parents are also run at 2^25, and the gate is median `|1/c(2^25) - 1/c(2^24)| / (1/c(2^24))`
  <= 0.5 × median `e` over all kept W mutants. If it fails, P2 is "unresolved (finite-window noise)", not a verdict.
- **W1.** For each `m` in {1, 2, 3}, over parents with at least one kept W mutant and one kept F mutant: median of
  `mean e(W) / mean e(F)` >= 2. Scored per `m`. ~35% for each of m = 2 and 3; ~25% for m = 1 (the k = 1 crawler has no
  circulation loops, phases 3 and 6 are empty, so the window can only act through the transfer between plaquettes).
- **W2 (the window moves with m).** At relative positions `q = p - m` in {3, 4}, which lie inside the window for
  `m = 3` and outside it for `m = 1`: median `e`(m = 3) >= 1.5 × median `e`(m = 1). Both K3-generic (fixed in `q`) and
  an absolute-position decay predict a ratio of 1 or less. ~30%.
- **W3 (sign).** Pooled over m = 2 and 3, kept W mutants. Among flips that turn `s_bar` into `s_0`, the fraction with
  `Delta(1/c) > 0` is >= 0.70. Among flips that turn `s_0` into `s_bar`, the fraction with `Delta(1/c) < 0` is >= 0.70.
  ~40%.
- Reported, not scored: kept fraction by position class and `m` (survivor selection), mean signed `Delta` by `q` and
  `m`, and the corner position.

**P3 mechanism (tracer, the P1 cohort and its controls).** Same tracer settings as P2.
- **R1.** For each rule, `rbar` = mean `r_j` over the circulating colours `j = 1..m-1`. The test: median `rbar`(Pi)
  minus median `rbar`(controls) >= 0.05. ~50%.
- **R2.** The chain-2 share is lower in Pi rules than in controls by >= 0.05 (median difference), meaning their
  plaquettes look more like the crawler's 3 + 1 pattern. ~45%.
- **R3 (replication of P1a on the tracer).** median `phi`, computed from tracer `1/c`, >= 0.5. ~65%.

## Decision rule and readings

- P1a, P1b and R3 hold: full shared-cell support pushes chaotic `c` toward the crawler line. H-crawl's crawler limit
  stands. H-young is rejected for Pi rules.
- If, in addition, W1 holds for at least two `m` and W2 holds: the window is positional and moves with `m`, a mechanism
  for C4's "letters 5-8 matter". Next steps would be (i) a closed formula for `b` from the support probability, and
  (ii) a flat-band test with the window letters as the controlled variable.
- P1 holds but W fails: support matters as a property of the whole table, not through a sharp window. The positional
  story is wrong in detail.
- P1a or P1b fails: the crawler is an isolated ordered solution and does not organise the chaotic edge's cost. That
  outcome would go into the pruning index as an empirical record scoped to these rules, instrument and horizons.
- P0b fails: report the disagreement first, and stop interpreting P1-P3.

## Pruning-index preflight

- Index revision `56aac506a75228ea148c1d6dea753877eecd3f4d`. Queries: `rg --files notes/pruning-index/entries`;
  `rg -n -i -e crawler -e "birth rate" -e "c law|c-law" -e "boundary steps per birth" -e "Pi\(k\)" -e lead
  notes/pruning-index/entries`. I also read the titles and predicates of both entries.
- Candidates: no matches. `NR-20261022-additive-laws-order-blind` concerns additive invariants (a different
  objective). `NR-20261025-kappa-exposure-classes-exposed-edge` concerns kappa by exposure class, not c and not letter
  positions.
- Decision: run. This does not repeat any recorded test. The closest earlier work is H-loop (square-loop,
  2026-10-16: kappa, interior loop rate) and the c-law kernels K3/K4. Both were fitted kernels without a crawler
  ceiling or a lead-dependent window.
- Budget: at most about 1,200 tracer runs of 2^24 to 2^27 steps (under 1e11 steps), about 30 minutes on 4 cores.
  Nothing larger without a new registration.

## Commands

Filled in as run.

## Commands and results, Stage 1 (appended 2026-10-25 23:25 +13:00; the registration above is not edited)

From the repository root (Rust 1.97.0, uv; CPU only, about 3 minutes on 4 cores):

```bash
E=experiments/archive/2026-10-crawler-cost-chaotic-edge
python3 $E/scripts/p0_strip.py > $E/results/p0_strip.txt                  # P0a (stdlib, exact rationals)
uv run --frozen $E/scripts/make_lists.py                                   # frozen lists -> results/lists/
CARGO_TARGET_DIR_FRESH=$(mktemp -d) sh $E/scripts/run.sh                   # tracer runs -> results/trace_*.jsonl, run.log
uv run --frozen $E/scripts/analyse.py                                      # registered scoring -> results/analysis.{txt,json}
uv run --frozen $E/scripts/posthoc_k3.py > $E/results/posthoc_k3.txt       # POST HOC, labelled
```

Provenance: `results/run.log` (commit `082fb7b`, clean `src/` and `examples/`, binary sha256 `e1bd80b8…f780`, and an
output sha256 per file). Deterministic. The census `c` comes from `experiments/archive/2026-10-probe-growth-census/results/probe_summary.csv`.

| Prediction | Verdict | Numbers (`results/analysis.txt`) |
|---|---|---|
| P0a exact strip | **held** | k = 1..8: `1/c = k + 5/4`, r = (1, ..., 1, 1/4, 0, ...), chains {1, 3} half each, exact rationals |
| P0b tracer on 25 fillers | **held** | `1/c` within 0.0021 of `k + 5/4` for all 25 (k = 1..5); chain-2 share <= 0.0008 |
| P1a crawler limit | **held** | median phi 0.647 (n = 40); 0.642 without the 3 seen rules |
| P1b vs composition-matched controls | **held** | median phi 0.644 (38 Pi rules) vs 0.149 (73 control draws), difference 0.494, 95% CI [0.329, 0.627] |
| P1c crawler as ceiling | **held** | 2 of 40 exceed `m + 5/4 + 0.10` (`RRLRRRRRR`, `RRLRRRRRRR`) |
| N0 noise gate | passes | median relative change of `1/c` from 2^24 to 2^25 is 0.0026; median e(W) is 0.070 |
| W1 near letters matter more than far letters | **held** for m = 1, 2, 3 | median e(W)/e(F) = 5.50, 3.44, 2.78 (28, 25, 25 parents) |
| W2 the window moves outward with m | **failed** | at q in {3, 4}: median e 0.034 (m = 3) vs 0.062 (m = 1), ratio 0.55 (needed >= 1.5) |
| W3 sign of window flips | **failed** | `s_bar -> s_0` raised `1/c` in only 31% (n = 67); `s_0 -> s_bar` lowered it in only 44% (n = 63) |
| R1 circulating reads stay on the boundary | **held** (barely) | median rbar 0.901 (Pi) vs 0.848 (controls), difference 0.054 |
| R2 crawler-like plaquettes | **held** | median chain-2 share 0.279 (Pi) vs 0.537 (controls); the crawler's is 0 |
| R3 P1a on the tracer | **held** | median phi 0.655 (40/40 kept) |

**What this shows.**
- The crawler's accounting is now an exact calibration point for the edge tracer. `1/c = k + 5/4` is derived, checked
  with exact rationals and reproduced by the tracer to 0.1% on all 25 census fillers.
- Chaotic rules that carry the crawler's full turn table sit about 65% of the way from the lead law to the crawler
  line. Composition-matched rules sit at 15%, and only 2 of 40 overshoot the crawler. Their edges look more like the
  crawler: half as many two-cell birth chains, and slightly more circulating reads on the boundary.
- The positional version of H-crawl is wrong. Near letters do matter more than far letters (W1), but the influence
  decays with distance from the lead rather than tracking a window `[m+1, 2m+1]` that moves outward with m (W2). A
  single letter inside the window does not reliably move `1/c` in the predicted direction (W3). By the registered
  decision rule (P1 holds, W fails), **support acts as a property of the whole table, not through a sharp window**.
- W1 alone does not discriminate H-crawl from K3-generic, since a smooth decay passes it too.

**Post hoc, not registered (`results/posthoc_k3.txt`).** These checks were written after reading the results.
1. The fitted K3 survival kernel (c-law-mechanism Stage 1, refit on the full census) already predicts most of the Pi
   excess. The median residual `1/c - K3` is +0.029 for the Pi rules (against +0.520 for the lead law) and -0.056 for
   the controls. At m = 2 and 3, H-crawl's crawler limit adds nothing that K3's "s_0 letters after the kill" term
   does not already carry.
2. At high lead, K3 falls short and the Pi rules track the crawler's slope. The median `1/c` for m = 2..9 is 3.08,
   3.96, 4.92, 5.86, 6.64, 7.52, 8.34, 9.17, a slope of about 0.87 per lead step, against 0.70 for the lead law, 1 for
   the crawler, and a K3 prediction that saturates (4.56, 5.03, 5.61, 6.30, 6.94 for m = 4..8). n is 1-4 per lead above
   m = 3, so this is a lead to test, not a finding.
3. Across all stationary census blobs, the residual from the lead law rises with the second run `j` (the `s_0` letters
   straight after the first opposite letter) at every m: about -0.2 at `j = 0` (for m >= 2) up to +0.3 to +0.8 at
   `j >= m + 2`.

**Limitations.** P1 uses census `c` that has been used in earlier fits (the lead law itself), although never for this
cohort. The 40 Pi rules are a convenience sample of what the census contains: 17 of them have m = 2, and the high-m
rules are nearly all-R strings. Three were seen in exploration (results unchanged without them). The tracer horizon is
2^24 on a 4096 board, and survivor filtering removed 20-38% of P2 mutants unevenly across position classes (table in
`analysis.txt`). There is one ant per rule and one blank start; between-start variance is not measured here (N0
bounds only the finite-window drift).

## Stage 2: does full support push the lead slope toward 1? (registered 2026-10-25 23:22 (+13:00), before any Stage 2 run)

Motivation: post hoc item 2 above. Among census Pi rules, `1/c` climbs at about 0.87 per lead step up to m = 9, and K3
saturates. With only 1-4 rules per lead above m = 3, this has to be tested on rules the census never saw.

**Hypothesis H-slope.** The lead law's slope, 0.70, is an average over how well each rule supports circulation. With
full crawler support (`Pi(m)`), each extra lead step costs nearly one boundary read per birth, as in the crawler.
K3's multiplicative kernel cannot represent that collective support.

**Rules (fresh; the census stops at length 12).** All primitive `Pi(m)` rules with n in 13..18 and m in 2..6 (prefix
`R^m L R^(m+2)` and a free suffix). Sample up to 60 per m (seed 20261026, `numpy.random.default_rng`). Each gets one
composition-matched control: a random primitive non-`Pi` rule with the same n, the same lead m and the same number of
`R`s, drawn from the full enumeration with the same generator. Same tracer, horizon and keep filter as P2/P3
(`blank 24 4096`, not escaped, births >= 200, 1.3 <= area/area_t0 <= 1.9). The filter also drops ring fillers, whose
area doubles per octave. I report how many runs each filter clause drops, by m. Any m with fewer than 6 kept Pi rules
is reported but not scored in S2 or S3.

**Predictions (my odds).**
- **S1.** OLS slope of `1/c` on m over the kept Pi rules lies in [0.85, 1.10], **and** the slope difference
  (Pi minus controls) is >= 0.10 with a 95% bootstrap CI above 0 (2000 resamples over Pi rules, controls carried with
  their Pi rule, seed 20261026). ~45%.
- **S2.** For each scored m, the median phi of the kept Pi rules is >= 0.5. ~55%.
- **S3.** K3 (full-census refit: e = 1.1215, rho = 0.6922, psi = 0.16) under-predicts at high lead: median
  `1/c - K3` >= +0.25 for the kept Pi rules with m in {4, 5, 6} pooled, and lies within ±0.10 at m = 2. ~45%.
- **S4.** At most 10% of the kept Pi rules exceed `m + 5/4 + 0.10`. ~60%.

**Readings.** If S1 and S3 hold, full support restores most of the crawler's slope, and the c law's b = 0.70 is a
support-averaged slope that K3's kernel cannot produce. That would call for a support variable in any closed formula
for b. If S1 fails with a slope below 0.85, the high-lead pattern in the census was small-n noise, and H-crawl
retains only P1 at m = 2-3, which K3 already explains. If S4 fails, the crawler is not a ceiling.

Budget: at most 600 tracer runs at 2^24 steps (about 1e10 steps), a few minutes.

## Stage 2 results (appended 2026-10-25 23:25 (+13:00); the registration above is not edited)

```bash
uv run --frozen $E/scripts/stage2_lists.py                                  # -> results/lists/s2_cohort.csv, s2_specs.txt
CARGO_TARGET_DIR_FRESH=$(mktemp -d) sh $E/scripts/run_stage2.sh              # -> results/trace_s2.jsonl, run_stage2.log
uv run --frozen $E/scripts/stage2_analyse.py                                # -> results/stage2_analysis.{txt,json}, stage2_rules.csv
```

Provenance: `results/run_stage2.log` (commit `bb2801d`, clean tree; the binary sha256 `e1bd80b8…f780` is identical to
Stage 1). 256 Pi rules (60/60/60/60/16 for m = 2..6) and 236 controls (21 Pi rules had no composition-matched non-Pi
rule).

| Prediction | Verdict | Numbers (`results/stage2_analysis.txt`) |
|---|---|---|
| S1 slope in [0.85, 1.10] and Pi-specific | **failed** | Pi slope 0.884 (n = 89 kept) is in range, but on the 42 pairs where both runs were kept the slopes are 0.828 (Pi) vs 0.784 (controls), difference 0.044, 95% CI [-0.023, 0.114] |
| S2 median phi >= 0.5 at every m | **failed** (narrowly) | phi 0.675, 0.496, 0.493, 0.570, 0.589 for m = 2..6 (kept 19, 24, 14, 26, 6) |
| S3 K3 under-predicts at high lead | **failed** | median `1/c - K3` +0.182 for m in {4, 5, 6} (needed +0.25); -0.034 at m = 2 (within ±0.10). By m: about 0, +0.29, +0.61 for m = 4, 5, 6 |
| S4 crawler as ceiling | **held** | 4 of 89 exceed `m + 5/4 + 0.10` |

Filter outcomes: **166 of 256 fresh Pi rules (65%) grew faster than t^(2/3) within 2^24 steps** (area ratio > 1.9;
these are filler-like), against 9 of 236 controls. The kept Pi rules are therefore the minority that stayed blob-like,
not a random sample of the family.

**Reading (H-slope).** The registered failure stands: full crawler support does not measurably steepen the lead
slope beyond what composition does. Fresh, R-rich controls at lengths 13-18 also climb at about 0.78 per lead step
(above the census 0.70), so the census pattern in post hoc item 2 was mostly composition plus small n. What *does*
replicate across both stages: Pi rules sit at a roughly constant **half to two-thirds of the way from the lead law to
the crawler line** (phi 0.65 in the census, 0.49-0.68 per lead on fresh rules), and almost never above it (6 of 129
across both stages). K3 tracks them at m <= 4, which is consistent with Stage 1's post hoc check.

## Overall verdict (Stage 1 + 2)

- **Established.** The crawler gives an exact, proved reference point for the edge-cost instruments: `1/c = k + 5/4`,
  `r_j = 1, ..., 1, 1/4`, chains {1, 3}. It is reproduced to 0.1% by the tracer. The crawler line works as an
  empirical **ceiling** for chaotic rules with the same turn table (6 exceedances in 129), and those rules recover
  roughly 50-65% of the gap between the lead law and the crawler (n = 40 census, 89 fresh).
- **Refuted, at this scope.** A positional shared-cell window `[m+1, 2m+1]` that moves with `m` (W2) and acts
  letter by letter (W3). Also refuted: a support-specific steepening of the lead slope (S1).
- **Not distinguished from K3.** At m <= 4 the fitted K3 kernel predicts the Pi rules' `c` as well as the crawler
  picture does, so H-crawl adds a ceiling and an interpretation, not extra predictive power.
- **Unexplained.** Why support is collective: one added `s_0` letter in the window lowers `1/c` more often than it
  raises it, while a full window raises it. Also why about two-thirds of fresh Pi rules become filler-like, and the
  coefficients a ~ 1.36 and b ~ 0.70 themselves, which remain open (b is still not derived).

## Pruning-index outcome and next question

New empirical signature `NR-20261025-crawler-window-single-letter`. It is scoped to single-letter flips of these 90
parents at this horizon and instrument: no lead-dependent window and no consistent sign. It does not exclude
whole-table support effects, which P1 confirms, or other horizons or backgrounds. The crawler-limit and ceiling
results are positive and need no signature.

Next question worth a registration: **what makes support collective?** The crawler needs *every* shared-cell read
to turn `s_0`. If chaotic circulation is an all-or-nothing chain, `phi` should depend on the *product* of window
letters, not their sum. A discriminating design: compare rules whose window is complete except for one gap at each
position (dose of 0, 1, 2 gaps) on the flat band, where geometry is controlled.

Figure and shareable notebook (read committed results only):

```bash
uv run --frozen $E/scripts/figure.py           # -> results/fig_crawler_ceiling.png
uv run --frozen $E/scripts/build_notebook.py   # -> notebook.ipynb; execute it with the command in that script's docstring
```
