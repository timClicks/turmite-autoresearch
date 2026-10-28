# Proposed additional figures for the cube-root paper (2026-10-16)

Status: proposal only. Nothing here has been built. Data availability for each
item has **not** been checked; that is step one before building. Based on a read of
`research-outputs/working-papers/cube-root-growth/main.typ` and `fig/`.

## Existing coverage

16 figures: hero, timeline, gallery, mechanics, alpha_gap, census, edge,
growth_curves, timelapse, exponents, ck_time, memory_paths, memory_growth,
deviations, cmodel, rotor. They cluster in the setup and the cube-root evidence
(sections 2-4). The mechanism, prediction and edge-gap sections, where the prose
is densest, have little or no visual support.

Rules for any new figure (from `AGENTS.md`): built from committed
`experiments/*/results/` or `numbers.json`, not `dumps/`; recipe recorded; added
to `rebuild_figures.py`.

## Highest value: the prose asks the reader to take a claim on trust

1. **Walker map in the (area exponent a, kappa) plane.** The central negative
   result (no tested mechanism reproduces a ~ 2/3 with kappa ~ 0.9) currently
   lives in `tab:exclusion`, `tab:memory` and four paragraphs. One scatter: ant
   cloud; rotor (0.69, 2.0); random walk and independent-turn walkers near
   (0.95, 1.4); cookie and edge-reinforcement walkers; the regime box and
   kappa = 1 line. Overlay the eps-noise rotor path: kappa rises to 3.6-6.7 and
   falls while c stays 0.498. Sources: `tab:memory`, audits 10, 20, 21, 25.

2. **The edge gap: surface width W(t) vs t, ants vs rotor (log-log).** The
   tagline "same bulk, different edge" is supported only by the hero image;
   the measurement (0.22-0.25 ants vs 0.10-0.13 rotor, flat for k = 22-32) is
   only quoted. Two panels: W vs t with fitted slopes; local exponent vs k with
   the Kapri-Dhar ~0.13 marked. Optional inset: hole-rim share (4% ants vs 25%
   rotor). Sources: audits 34, 35 (A4/A4c).

3. **Layer profiles rho(d) for crust and non-crust rules.** "Crust",
   "depleted layers 2-4" and rho(0) = kappa are defined only in prose but used
   in two sections. Plot rho vs depth for one crust rule, one ordinary rule and
   the rotor. Shows why similar dwell coexists with kappa from 0.13 to 18.
   Sources: audits 22-24.

4. **`RLRLLL` column sweeper.** The most vivid result has no figure. Panels:
   steps-per-new-cell (or area) vs t showing the switch near 1.3e10; a crop of
   the boustrophedon wake with period-3 columns; predicted vs measured
   d|x|^2/dt (0.86, 0.84 vs 0.86, 0.83). **Snag:** dumps are gitignored and
   paper scripts should not read `dumps/`, so the wake crop needs a small
   committed extract or a recorded exception (as `memory_figures.py` has).
   Sources: audits 38-41.

## Strong explanatory value

5. **Prefix lookup: predicted vs measured ln kappa.** Headline claim quoted only
   as a score. Scatter coloured train/test, with the all-retained-rules case
   (interval includes zero) alongside, so the cohort restriction is visible.
   Source: audit 12 / W3c.

6. **Forecast errors.** Forecast vs observed increment for constant budget,
   baseline and drift; mark near-stall outliers (e.g. `RLLRRRLLRLRR@108`, ~6506x)
   and show rotor and random-walk controls. Source: audits 17, 18.

7. **Calibration as local slope vs window k.** `tab:calib` gives end values
   only. Rotor (known 1/3, 2/3), ants and random walk; shows where the +0.02
   area bias arises and why R_g is preferred. Source: calib experiments, audit 6.

8. **Replicate-start reproducibility.** Rule-mean kappa vs rule-mean alpha with
   between-start error bars across 12 random patches per rule. Shows kappa
   separates rules (ICC ~0.58) while alpha largely does not (~0.12); the premise
   of the kappa-centred paper is currently two sentences of ICCs. Sources:
   audits 10, 11.

## Worth considering

9. **Cone derivation.** rho(r) = (t/((1-a)A))(1 - (r/R)^(2(1-a)/a)) for several
   a, with the eps = 0.001 rotor and turmite profiles overlaid. Shows where the
   formula fails; `fig:rotor` only shows where it works. Sources: audits 19, 29,
   32, 33.
10. **Interior mixing.** Measured MSD slope vs persistent-walk prediction,
    coloured by colour-uniformity TV. Shows where the approximation holds.
    Sources: audits 26, 27.
11. **Identity in action.** Per-rule c, kappa, P/A reconstructing dA/dt.
    Overlaps `fig:dev` right panel; only worthwhile if that figure is split.

## Skip

- More census or exponent-distribution plots (already well covered).
- Another phase-diagram beyond `fig:census`.
- A tail-budget figure (mostly null result; `tab:exclusion` suffices).

## Suggested order

Build 1-4 first (their absence most weakens the argument), then 5 and 7 (cheap if
the CSV/JSON already exists in `experiments/*/results/` and `numbers.json`).

## Implementation update, 2026-10-16

Item 1 is implemented as `fig/late_switch.pdf`, linked from the RLRLLL
subsection. Its script reads compact results recovered from the proposal
worktree; details, checks and reproduction commands are in
`experiments/archive/2026-10-g1-ribbon-breakout/README.md`. Other proposals remain open.

Status 2026-10-17 (from the proposal branch, merged 2026-10-19): items 1-3 and 5 were not built there; see `notes/handover-paper-figures-2026-10-17.md`.

Status 2026-10-20: item 5 built as `fig/prefix_lookup.pdf` (`prefix_figure.py`, reads `experiments/archive/2026-10-kappa-rule-space/results/prefix_audit_predictions.csv`; LOO encoding, linear area; R^2 recomputed 0.497 -> 0.736 stationary, 0.363 -> 0.393 all-retained; numbers in `fig/prefix_numbers.json`), inserted at `fig:prefix` in `sec:prefix`, registered in `rebuild_figures.py` (full rebuild not run). Item 2 built the same day as `fig/edge_gap.pdf` (`edge_gap_figure.py`; pooled A4+A4c shape CSVs, 36 ant runs and 14 rotor seeds to 2^34; mean local exponent over k>=22: ants 0.243, rotor 0.129, `fig/edge_gap_numbers.json`), `fig:edge-gap` in the surface-width section; the hole-rim inset was not built. Item 3 built as `fig/layers.pdf` (`layers_figure.py`; rho(d) recomputed from `layers*.csv` with the `layers_stats.py` formula, k>=22; 15 crust / 9 non-crust ants, 12 rotors, 5 persistent walks; `fig/layers_numbers.json`), `fig:layers` in the shallow-trapping subsection. Item 1 built as `fig/walker_map.pdf` (`walker_map_figure.py`; ants from `probe_summary.csv` k=20-26, memory pilot `summary.json` window 16..20, noisy rotor from `armb_probe.csv` via `per_rule`, medians reproduce `armb_stats.txt`; `fig/walker_map_numbers.json`), `fig:walker-map` after `tab:memory`. Windows differ across sources (stated in the caption); the regime box was not drawn. Proposals 1-5 are now all built; 6-8 and below were not attempted. `rebuild_figures.py` lists all new scripts and inputs but the full rebuild was not run, so the new figures were produced by running each script directly.
