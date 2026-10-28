# Research frontier: ideas and todo list

Written 2026-10-12 from reading everything in `notes/`. This is a list of
candidate investigations, not results. Each item names a falsifiable
prediction or a decisive experiment where one is obvious. Per AGENTS.md, write
the hypothesis note (with timestamp and predictions) before running anything.

Status key: **[queued]** hypotheses already written, measurement pending;
**[open]** stated in notes as unexplained; **[new]** suggested here.
Effort: S = hours, M = a day, L = multi-day or needs new code.

## A. The t^(1/3) mechanism (cube-root-hypothesis.md, open-questions-hypotheses.md)

The "well-mixed walker in a reflecting cup" story makes predictions P1-P5 and
Q1/Q2 predictions P1.1-P2.3. The notes record them as written but untested for
the ants (calibration only covers the rotor).

1. **Run the pending predictions.** [queued, M] Measure c(t), kappa(t), beta,
   and check P5: `a = (1 + gamma_c + gamma_kappa) / (2 - beta)` rule by rule.
   Decisive test: does P5 predict the outliers (alpha 0.19 to 0.6)? If not,
   the mechanism is wrong or incomplete.
2. **Persistent-walk MSD test (P1.3).** [queued, S] Interior MSD/lag should be
   `(1 - a)/(1 + a)` with `a = (2q-1)^2`. Cheap; falsifies "well-mixed" fast.
3. **Why c ~ 0.44, and why does it vary?** [queued, M] Test P2.1 (c depends
   on rule[1], rule[2] far more than later letters) with a regression over the
   census; build the local edge model (P2.3). Note the random walk also gives
   c = 0.44 (calibration.md), so c is not diagnostic by itself; the
   explanation must say why the rotor gives 0.50 and ants 0.44.
4. **Is the exponent exactly 1/3 for every chaotic rule?** [open, M] Part C
   says most between-rule spread is per-run noise (ICC 6-33%), but a small real
   residue (sd 0.004-0.014) remains. Distinguish "different exponents" from
   "different convergence rates" by fitting `A = a t^(2/3) (1 + b t^-delta)`
   per rule over longer windows (2^30+ steps, few rules, many seeds).
5. **Limit shape.** [new, M] The rotor has a deterministic limit shape
   (Bou-Rabee & Peres). Do chaotic ants? Measure shape (isotropy, radial
   profile of the visited-time density, contour radius vs heading symmetry)
   across seeds; check whether the coefficient `S/N^(2/3)` converges with CV
   falling as it does for the rotor (4.07 to 5.69, still rising).
6. **The rotor as an exact reduction.** [new, L] Can a chaotic ant be mapped
   to a rotor-like walker with a time-dependent, colour-dependent effective
   rotation? A coupling or an observable that matches step-for-step on the
   interior (visits mod n vs rotor visits mod 4) would turn the heuristic into
   a theorem sketch.
7. **Boundary-width exponent.** [new, M] Kapri & Dhar's boundary exponent
   (0.136) drifts down (0.19 to 0.132) for the rotor. Measure the same for
   ants; is the ant boundary width a different universality class?
8. **Edge exponent 0.52.** [open, S] Calibration shows it is a finite-time
   effect for both rotor and ants. Quantify its approach to 0.5 and confirm
   with the longest runs; remove it from any remaining claims.

## B. Hard vs easy tethering and the knockout map

9. **Run the knockout map.** [queued, M] The protocol, controls, hot-spot
   definition and falsifiers are fixed in `knockout-map-hypotheses.md`
   (coarse 5x5 tiles, 100-draw random-swap null, route-density partial
   Spearman). Do it first: it is fully specified and discriminates between
   "diffuse chaotic hold" and "localised return paths".
10. **Refinement down to 1x1 cells.** [queued, M] Slide windows inside hot
    tiles; find the minimal set of cells. If the hold reduces to a short
    closed cycle or a few cells, extract and describe it as an object.
11. **Characterise the bound state.** [new, L] Treat the hard-rule home as an
    attractor of the (ant, field) dynamics. Is it a quasi-periodic orbit, a
    long but finite cycle, or a chaotic repeller? Compute the return map to
    the home, Lyapunov-style sensitivity (flip one cell, measure divergence
    time), and the escape-time distribution under single-cell perturbations.
12. **Formation, not just maintenance.** [new, M] Results show the home is not
    re-formed from degraded fields. When does it first form in a normal run?
    Record the time and the local configuration at which tethering sets in;
    is formation a rare event (waiting-time distribution) or a deterministic
    function of the early history?
13. **Age dependence.** [new, S] One territory per rule at one age (2^24) is a
    stated caveat. Repeat the dose-response at 2^20 and 2^28: does the
    required fraction of intact cells (90 to 97%) change with age?
14. **Long-range carrier test.** [new, M] The "return paths" idea is untested.
    Alternatives to test against it: global parity or conserved-quantity
    structure (e.g. a sum over cells of colour weighted by something), a
    specific cell-colour class on the path. Knock out by *class* (all cells of
    colour k visited by excursions) rather than by patch.
15. **How many rules are "hard"?** [new, L] Only two hard and three easy rules
    are known. Screen the whole chaotic census for shuffle-resistance of the
    tether (cheap: shuffle test only). Is hardness tied to rule features
    (length, R/L balance, structure of the suffix)?
16. **Graded home.** [open, M] Shuffled fields give a stationary spread between
    home (14) and cup (39-47). Model the spread as a function of the corrupted
    fraction; is there a sharp threshold (percolation-like) or smooth crossover?

## C. Census, classification and unresolved rules

17. **The 854 unresolved rules of length <= 10.** [open, M-L] See
    `experiments/archive/2026-10-census-sweeps/results/unresolved_le10.txt` (includes RLL, RLR, RLLL, RRLL, RLLR). Push each
    to 1e10+ steps with the fast ant; classify into: highway (late), chaotic,
    slow-growth, bounded. Any rule still unresolved at 1e11 deserves a
    hand-study. Record the largest known highway-onset time and its
    distribution (is it heavy-tailed?).
18. **Highway onset time distribution.** [new, M] From the existing sweeps,
    fit the onset-time distribution by rule length. If heavy-tailed, the
    "unresolved" fraction has a predictable decay, which estimates how many
    unresolved rules will eventually be highways.
19. **Highway period/offset catalogue.** [new, M] Collect period, displacement
    vector and angle across all highway rules. Which (period, displacement)
    pairs are realisable? Is there a constraint tying period to rule length?
20. **Chaotic-vs-highway boundary in rule space.** [new, L] Is chaos
    (cube-root growth) vs highway predicted by simple rule statistics (number
    of R vs L, longest run, symmetry)? Fit a classifier and look at
    misclassifications; they are the strange rules AGENTS.md says to chase.
21. **Slow-growth outliers (alpha 0.19 to 0.6).** [open, M] Which rules have
    non-1/3 exponents and are those real or noise (Part C suggests noise)?
    Re-measure the extreme ones with many seeds and patched starts.
22. **Tethered log-growing rules.** [open, M] Test H1': inward drift v with
    diffusion D, occupancy ~ exp(-r v / D), P1.5. Measure radial drift and
    compare D/v to the decay length. This links the tethered rules to the
    easy/hard split of section B.
23. **Rule equivalences.** [new, S] Confirm that symmetry reductions (cyclic
    rotation of colours, mirror, complement) are used consistently in the
    canonical forms, and check that no two canonical rules produce identical
    trajectories (a rule-identity bug would corrupt the census statistics).

## D. Extensions beyond the current model

24. **Other grids and turn sets.** [new, L] Add N/U turns (Turmite-like or
    4-turn alphabets), hex and triangular lattices (RL, LLRR on a hex grid are
    known). Does t^(1/3) hold on hex, and does the rotor analogue (Kapri &
    Dhar on other lattices) predict it?
25. **Multi-state turmites.** [new, L] The repo is named turmite. Add an
    internal state; test whether chaotic turmites still grow as t^(1/3), and
    whether the cup picture needs a second, state-dependent parameter.
26. **Randomised variants as controls.** [new, M] (a) Random initial
    background instead of blank (cf. Kapri & Dhar's i.i.d. rotors). (b) Ant
    with noise (turn error rate eps). Predict a crossover time `t*(eps)` after
    which growth changes class; tests whether the mechanism depends on
    determinism.
27. **Many ants.** [new, L] Two or more ants on the same grid: do they share a
    territory with t^(1/3) per ant, or interact destructively?
28. **Higher dimensions.** [new, L] A 3D ant (rotor-router analogue); the
    rotor walker's exponent in d dimensions is `t^(1/(d+1))` (known for the
    Eulerian cases); the cup picture predicts a d-dependent exponent for ants.
    Compare.

## E. Methods, theory and tooling

29. **Cross-check to literature.** [new, S] Write an explicit comparison to
    Bou-Rabee & Peres (2026) and Kapri & Dhar (2009): what in the ant data
    would a proof extend to, and what is left? Perhaps the strongest argument
    for a theorem: the rotor's interior is exactly "4-periodic"; ants have
    n-periodic cells.
30. **Heavier statistics.** [new, M] Report between-seed sd (not just
    fit s.e.) for all headline numbers in `research-outputs/working-papers/cube-root-growth/numbers.json`, and add a
    script that regenerates every number from data (`research-outputs/working-papers/cube-root-growth/compute_numbers.py`
    exists; make it fail loudly on missing inputs).
31. **Faster ant.** [new, M] Add a block or lookup-table optimisation (compress
    the interior using the visit-count-mod-n structure) and property-test it
    against `reference`. Needed for item 4 and item 17 at 1e10+ steps.
32. **Web demo of the cup picture.** [new, S] Overlay c, kappa, P/A, and the
    boundary cells on the existing `web/` simulator so the mechanism can be
    seen live.

## Suggested order

1. Items 9, 1, 2, 3 (all fully specified or cheap; they test the two main
   stories directly).
2. Items 4 and 8 (tighten what is claimed about exponents before building on it).
3. Items 10-14 (follow up whatever 9 finds).
4. Items 17-21 (grow the census and chase the strange rules).
5. Section D only after A and B settle; items 26 and 24 are the cheapest.

## Honest gaps in this list

- I read `notes/` and the file listing only. I did not open the code, the
  paper source, or the census CSVs, so item 23 is a check rather than a known
  bug, and the "854 unresolved" count is just the line count of
  `unresolved_le10.txt`.
- Item 28's `t^(1/(d+1))` for rotors in d dimensions is from memory, not
  verified against the literature; treat it as something to look up.
- Items in sections C and D are speculative and unprioritised by cost.

## Status update (2026-10-13)

Every item except 9 (knockout map, other agent) has been investigated; see `notes/frontier-status.md` (one line each) and
`notes/frontier-results.md` (hypotheses with timestamps, methods, results, corrections). Items 10 and 17 are partly
dependent on other work (10 on the knockout agent's `refine*` files; 17 on a long background run: `experiments/archive/2026-10-h1-lacunarity-decomposition/scripts/run_1e10.sh`).
Two corrections to this list: item 28's rotor exponent t^(1/(d+1)) is only a lower bound for d >= 3 (the 3D random rotor walk
is transient in our simulation), and item 23's 'rule identity' check found that repeats u^k are identical to u.

Update 2026-10-13 (later): items 10 and 17 are now done. 10: own single-cell scan (`examples/cell1.rs`, `experiments/archive/2026-10-cell1/results/cell1_stats.txt`); 17: all 807 rules to 1e10 (38 new highways).
