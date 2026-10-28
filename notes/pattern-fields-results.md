# Pattern-matched fields: results

Run 2026-10-11. Hypotheses written beforehand: pattern-fields-hypotheses.md.
Code: src/synth.rs (annealer, property-tested against a full recount, two
mutations caught), examples/synth.rs, experiments/archive/2026-10-patterns-fields/scripts/patterns.py (driver),
experiments/archive/2026-10-patterns-fields/scripts/patterns_analyse.py (independent numpy checks and summary),
experiments/archive/2026-10-patterns-fields/scripts/patterns_chart.py. Data: experiments/archive/2026-10-patterns-fields/results/patterns_final.csv (315 fields),
patterns_anneal.csv, patterns_summary.json, patterns_cross_resid.json.
Chart: notes/pattern-fields.png.

Protocol as published: final field after 2^24 steps, fresh ant at home
heading north, 2^26 steps, outcomes over the last quarter. 3 seeds per field.
New outcome: spread = RMS distance from the block's mean position.

## Answer

No level of local detail up to 3x3 lets a hard rule form a home. Both hard
rules (RRRRRLLLLLL, RLLLLRRRRLR) stay untethered in every pair-, 2x2- and
3x3-matched field, from home and from four other drop points (48 extra runs,
best own-time 0.11). Both hypotheses were wrong: H1 (some local order level
works) and H2 (the radial gradient works).

| hard rule spread, cells | RRRRRLLLLLL | RLLLLRRRRLR |
|---|---|---|
| real field | 14.4 | 14.4 |
| shuffle | 39.3 | 46.6 |
| radial shuffle | 39.5 | 42.3 |
| pairs matched (99.9% of windows) | 38.1 | 39.4 |
| 2x2 matched (91%, 93%) | 37.4 | 39.8 |
| 3x3 matched (80%, 73%) | 30.9 | 37.3 |

The easy rules tether at every level, as expected.

## Three findings that change the picture

1. Untethered is not free. In a shuffled field the hard ant's spread is flat
   from 4M to 268M steps: it is held by the territory's blank edge and roams
   the whole cup instead of sitting in a home. Every degraded field gives a
   stationary spread between home (14) and cup (39-47). "Home" is graded,
   and the ant never rebuilds one from a degraded field.

2. 3x3 statistics can't be separated from the field itself here. 79% and
   71% of 3x3 windows are unique patterns, so matching them is a jigsaw, and
   annealing put 52% (RRRRRLLLLLL) of cells back exactly in place (baseline
   11%). For the small easy territories it rebuilt 93-97% of the original.

3. What holds the hard ant tracks exact cells, not local statistics. A field
   keeping a random 90% of cells in place (rest shuffled) matches the real
   field's 2x2 and 3x3 histograms worse than the 3x3-annealed field
   (3x3 match 0.55 vs 0.80; 0.50 vs 0.73), yet holds the ant far better
   (spread 22.6 vs 30.9; 22.3 vs 37.3, own 0.30-0.34 vs 0.07-0.09). Keeping
   the disc r <= 40 is the same: worse statistics, tighter hold.

## Dose-response (hard rules, both similar)

- Random cells kept in place: 25% and 50% do nothing, 75% a little
  (spread ~35), 90% tethers weakly (own ~0.3), 97% nearly fully.
- Central disc kept, outside shuffled: r <= 30 fails, r <= 40 tethers (own
  0.36-0.42), though the ant spends ~98% of its time inside r = 30.
- Outer rim kept, core shuffled: core r < 10 shuffled still tethers (0.37),
  r < 20 fails. Neither core nor rim alone carries the home.
- Blank disc (r <= 10 or 20) inside a shuffled field: no home. The ant runs
  exactly as from a blank board until it reaches the disc edge (width 31 by
  2^16 steps), then is lost.

## Interpretation (inference, not yet tested)

The hard home is a property of the specific configuration across nearly the
whole territory, at scales beyond 3 cells: corruption anywhere loosens it in
proportion to how much is corrupted, and one excursion into scrambled ground
undoes it. A natural candidate is long-range paths (return routes the ant has
written) rather than any local texture. That is consistent with "a bound
state between the ant and the cells it keeps rewriting", but says the bound
state is non-local and not re-formable from random ground, unlike the easy
rules'.

## Caveats

- 2x2 annealing plateaued at 91-93% of windows matched; the residual could in
  principle matter, but finding 3 argues against it.
- One territory per rule, at one age (2^24).
- "same place" for 3x3 fields counts restored cells, which are clustered;
  part of 3x3's modest gain over random-keep at equal share may be that.

## Obvious next step

A knockout map: shuffle one small patch (say 5x5) at a time across the real
territory and record the spread. That locates the cells the hold depends on
and tests the return-path idea directly (compare the map with where the
ant's homeward excursions travel).
