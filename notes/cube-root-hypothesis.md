# Why do chaotic ants grow as t^(1/3)?

Written 2026-10-10 07:45 NZDT, before any measurement beyond the census
(median width exponent 0.332 across 2,637 chaotic rules, stable from 2^16 to
2^27 steps and across rule lengths 3 to 12).

## Mechanism (the "well-mixed walker in a reflecting cup")

1. Blank cells repel. Every canonical rule turns R on colour 0, so an ant that
   steps onto fresh ground curls back on itself within a few steps. The
   unvisited plane acts as a wall the ant can only chip at.
2. Inside the visited region the ant's motion is irregular enough that, over
   times short compared with t, it is spread roughly evenly over the A visited
   cells.
3. So the fraction of time it spends on a boundary cell (a visited cell with an
   unvisited neighbour) is about P/A, where P is the number of boundary cells.
4. Each step taken from a boundary cell enters fresh ground with some roughly
   constant probability c.
5. The region is compact with a reasonably smooth edge, so P ~ A^(1/2).

Then dA/dt = c * kappa * P/A ~ A^(-1/2), so A ~ t^(2/3) and width ~ t^(1/3).

Compare: if the edge were fractal (P ~ A), growth would be t^(1/2). If the ant
had to return to the origin between growth events, as in internal DLA, it
would be t^(1/4).

## Predictions

- P1. Area A ~ t^(2/3), and the region stays compact: A / width^2 settles to
  a constant.
- P2. c = (new cells) / (steps starting on a boundary cell) is roughly constant
  in time for each rule.
- P3. kappa = (fraction of steps on the boundary) / (P/A) is roughly constant in
  time, and of order 1.
- P4. P ~ A^beta with beta close to 1/2.
- P5. More generally, with time exponents gamma_c and gamma_kappa for c and
  kappa, A ~ t^a with a = (1 + gamma_c + gamma_kappa) / (2 - beta). This should
  predict the measured exponent rule by rule, including the outliers
  (alpha from 0.19 to 0.6) whose growth is not a cube root. If the outliers'
  exponents are NOT explained by beta and gamma, the mechanism is wrong or
  incomplete.

## What would kill it

- kappa drifting strongly with t (the walker is not well mixed; e.g. it stays
  near the edge, or deep inside).
- c drifting with t while beta = 1/2 (a cube root by coincidence).
- The formula in P5 failing to predict alpha for the outliers.

## Interpretation correction — 2026-10-16 00:18 NZDT

Base commit `997c9b2da6efa526fc6c5a57104d103e1345e916`, dirty workspace.
The original predictions above are retained as registered. P5 is conditional
scaling algebra applied to quantities sharing the same growth data. Agreement
is a fit-consistency check, not independent validation of a mechanism; failure
could reflect finite-window fits or failure of the assumed power laws. It
should not have been offered as a stand-alone mechanism falsification test.
P2–P4 describe the proposed stationary regime but do not explain why it occurs.
Interior colour uniformity does not imply uniform spatial occupation or stable
boundary access. The revised paper states that the physical closure remains
missing; calibration concerns estimator bias. See the
[response audit](accounting-identity-response-2026-10-16.md) for evidence limits
and what independent prediction and intervention would need to establish.

## Manuscript interpretation update — 2026-10-20

Evidence revision `0de4d38de7c468583bc8c8aba4dc6ed54edada10`; editorial work
follows blog commit `0e7d251`. No new simulations or fits are introduced.
The probe's window-normalized uniform reference is about 1.11 in the cube-root
regime, verified by the uniform-resampling control; the stationary census
median ratio to each rule's own reference is 0.814. This corrects the reference
used to interpret P3, without changing its registered statement above.

The opening-run law for edge entry, `1/c = 1.363 + 0.696 min(m,8)`, transfers
to fresh stationary rules (R² 0.877) but misses its broader-validation target
(0.711 versus 0.80). Flat-band initial-interior ablations support a local
fresh-ground contribution; failed profile and kernel predictions leave the
constants unexplained. The registered no-direct-effect construction reproduces
the area-conditioned opening-run association with occupation. This limits a
mechanistic reading of prediction beyond early area; it does not remove the
prefix prediction, prove no direct effect, or explain the shortening mutation.

Records, commands, seeds and caveats:
[c law](../experiments/archive/2026-10-kappa-chiral-edge/README.md),
[mechanism and conditioning](../experiments/archive/2026-10-c-law-mechanism/README.md),
[uniform control](../experiments/archive/2026-10-kappa-uniform-baseline/README.md),
[walker controls](../experiments/archive/2026-10-kappa-walker-reference/README.md).
The square-loop null, unrun surgery and growth-clock support failure retain
their distinct verdicts. The headline census and growth exponent are unchanged;
neither stationarity nor cube-root growth is derived from the microscopic rule.

## Update 2026-10-26: the "blank cells repel" ingredient tested directly

Evidence revision `3040a0b86f69489a999e3881b8d4ff89886a0ac8`
([wall-vs-memory](../experiments/active/2026-10-wall-vs-memory/README.md)). The two
ingredients of the mechanism above (step 1, repulsion by blank cells; step 2,
mixing inside) were separated by turn noise applied only on fresh or only on
revisited cells. Removing step 1 while keeping the ant's memory made all six
tested rules porous (a ~ 0.86-0.91): randomising the turn on first departure
disrupts compact growth there (it also breaks first-visit chirality, so this
does not isolate reflection; forced L is untested). Keeping step 1 with a
memoryless interior gave a = 0.73 at k = 24..30 (0.717 at k = 27..31; rotor
0.68), a finite-window separation whose asymptote is unresolved, so step 2 in
its memoryless form is not shown sufficient. The original predictions above
are unchanged; this is new evidence on which ingredient carries the exponent,
not a derivation.
