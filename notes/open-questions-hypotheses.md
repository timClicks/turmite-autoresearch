# Open questions: hypotheses before measuring

Written 2026-10-10 10:30 NZDT. Data in hand: probe_summary.csv (c, kappa, ...
per rule). No new measurements yet.

## Q1. Why is the ant well mixed inside its territory?

H1. Inside, the ant is a random walker in a random environment. Each interior
cell has been visited many times, so its colour (visits mod n) is close to
uniformly distributed and nearly independent of its neighbours'. The ant then
turns R with probability q = (number of R in the rule) / n on each step,
independently of earlier turns. That is a persistent random walk, and a
reflecting wall plus a symmetric walk gives a uniform stationary density.

Predictions:
- P1.1 Interior colours are close to uniform over 0..n-1, with weak
  neighbour correlation.
- P1.2 The fraction of R turns the ant actually makes is close to #R/n.
- P1.3 Turns are nearly uncorrelated, and the mean squared displacement grows
  linearly with lag, with slope (1 - a) / (1 + a), where a = (2q - 1)^2.
  (Derivation: each turn multiplies the velocity by +i or -i; the average
  factor is i(2q - 1), so velocities k steps apart correlate as
  Re[(i(2q-1))^k], which vanishes for odd k and is (-a)^(k/2) for even k.
  Summing gives MSD / lag = 1 + 2 * sum_m (-a)^m = (1 - a) / (1 + a).)
- P1.4 Mixing time across the blob ~ R^2 / D, which is much less than the
  time to grow, ~ R^3. So the walker has time to spread out.

H1' (for tethered, log-growing rules). Something breaks the random environment
near home, for example a colour field that is not uniform, giving an inward
drift. If the drift v is constant and diffusion is D, occupancy falls off as
exp(-r v / D), which matches the exponential profile already seen.
- P1.5 Tethered rules have a measurable inward radial drift, and D / v matches
  the decay length of their occupancy profile.

## Q2. Why is c about 0.44, and why does it vary?

H2. Edge cells are young: most have been visited once or twice, so their
colour is 1 or 2. On an edge cell the ant's turn is therefore set mostly by
rule[1] (and rule[2]), not by a random colour. If the low colours turn the same
way as colour 0 (R), the ant tends to curl back inside, so c is low. If they
turn the opposite way (L), the ant zig-zags outward, so c is high.

Predictions:
- P2.1 Among all rules, c depends strongly on rule[1] and rule[2], much more
  than on later letters.
- P2.2 Edge cells' colours are concentrated on 1 and 2.
- P2.3 A local model (an ant on a straight edge, cells beyond it blank, edge
  cells with the measured colour mix, interior colours uniform) predicts c per
  rule better than the random-heading estimate (fresh neighbours / 4).

## Added 2026-10-13 from the frontier work (see notes/frontier-results.md)

- Q3. Why do 556 tethered rules share only ~28 discrete home types (spread values equal to 0.3% across different rules and territories)? What invariant of the rule labels them?
- Q4. Why are the rare colours (6, 8, 10 / 0, 6, 8) the critical cells of the hard rules' homes, and are they rare in the other 112 rules of the same class?
- Q5. Is RRLLLLLLR (CV of A/t^(2/3) rising with t, alpha_w 0.38 +- 0.07) truly non-self-averaging, and with how many 'phases'?
- Q6. Why does the ant's visit density equal the rotor's cone 3 t/A (1 - r/R_eq) to a few per cent? A derivation would also fix the 2/3 exponent.
- Q7. Why is the ants' boundary width exponent (0.25-0.27 at 2^28) above the rotor's (0.13-0.16 under the same estimator)?

## Added 2026-10-13 (later) from `notes/frontier-2026-10-13-results.md`

Answered or sharpened there: Q3 (no single rule feature labels the home types: A5), Q4 (rare colours are rare in 99.8% of tethered rules and 5% of blob rules, but the self-healing explanation is reversed: the most-visited cells hurt most: A6), Q5 (RRLLLLLLR: CV rises through 2^29, unimodal; rising CV occurs in ~5% of random rules, mostly RLLL-prefixed: A7), Q6 (cone follows from uniform occupancy + the exponent, and correctly fails on a random background: A3), Q7 (ants 0.24 vs rotor 0.13 still falling, ants trend inconclusive: A4).
New, unexplained:
- Q8. RLRLLL (an item-4 "core" rule) leaves a 32768 board at ~1.3e10 steps with no highway: an ~1e4-cell thin structure along the edge (bounding box 3,377 at 1e10, 18,175 at 1.3e10). What is it, and are the other "escaped without highway" cases (4.6% of the 10^10 survivors, 1.2% in (1e10, 1e11]) the same thing?
- Q9. The tether of RRRRRLLLLLL is intermittent in age: a fresh ant started from the 2^25 field at home heading north is not tethered (near_home 0.061) while 2^22, 2^24, 2^26 are (0.43, 0.47, 0.36). What state does the original ant carry that the field plus "home, north" does not?
- Q10. In the rotor with north-biased arrows (C2b/C2c) the territory width at 2^28 grows +25% at bias 0.15 and 2.6x at 0.25, while kappa and c change by < 10% and the width exponent not at all. Which factor of the identity dA/dt = c kappa P/A carries the amplitude, and why does the area exponent rise (0.715 to 0.787) while the width exponent does not (elongation untested)?
- Q11. Why is the area-exponent ICC across rules (0.34) so much larger than the width-exponent ICC (0.12) (B2)? Rule identity matters for area but little for width.
- Q12. The 3D ants' extent exponent is 0.234 and volume exponent 0.771 at 2^28-2^32, so volume/extent^3 is still rising as ~t^0.07: what is the 3D limit shape (D2)?
- Q13. Why does the corruption of the most-visited cells hurt most, with rare colours doubling the damage at equal visit quartile (A6)? How much of "visit rate" is just distance from home?
- Q14. Does contiguity reduce the damage per critical cell (patch ~0.65x the loss per rare cell of a swap, E4), or is that a location effect?
- Q15. The census "builders" (304) are mostly non-highway frame builders with steps per bounding-box cell ~2-6; are they one class, and does it match the sqrt(t) turmite cluster (D1)?
- Q16. The late-highway onset rate fell from 4.7% to 1.25% per decade at 1e10-1e11 (B5): is the set of late highways finite, and what is the distribution of onset times within a prefix family?

See `notes/research-frontier-2026-10-13-pm.md` for the Phase 3 hypotheses, tests, and pre-registered predictions addressing Q8–Q16 and the open mechanisms of kappa.

## Added 2026-10-15: independent-area cutoff test

The cutoff–kappa lead survives assigning area matching, kappa and cutoff to
three disjoint seed groups: concordance 0.730 [0.605,0.842] at k=22 and
0.757 [0.617,0.881] at k=25, 44 rules, rule-bootstrap intervals (2000 draws,
seed 20261016). Registered thresholds held; synthetic controls passed. Recipe:
`uv run experiments/2026-10-15-independent-area/scripts/analyse.py`;
[registration, caveats and next test](../experiments/2026-10-15-independent-area/README.md),
[output with provenance](../experiments/2026-10-15-independent-area/results/analysis.json).
This rules out shared-trajectory area matching as a sufficient explanation;
it does not remove noisy-area confounding or establish causality. The earlier
noise-floor gate remains failed. Open: does cutoff predict kappa at truly
fixed area in new trajectories, and can an intervention separate cause from
two responses to the same field property?

Prospective follow-up avenues, recorded 2026-10-15:
[fixed-area sampling, cycle accounting and mutation-to-tail tests](cutoff-research-avenues-2026-10-15.md).
These are research proposals; detailed predictions and analysis choices must
be registered in experiment READMEs before new measurements.

## Q8 follow-up, 2026-10-15: registered archival comparison
[G1 README](../experiments/2026-10-13-g1-ribbon-breakout/README.md) and
[append-only notebook](../experiments/2026-10-13-g1-ribbon-breakout/NOTEBOOK.md)
record the test and failed transfer prediction. RLRLLL has efficient, elongated
new-cell window boxes in 281/298 complete breakout windows, versus 0/676 before
onset; median efficiency 4.022, transverse box 54 cells. The original <=12-cell
prediction fails. This does not establish a period or a surface-wave mechanism.
Across completed census chunks, 0/37 earlier and 0/3 later no-highway escapes
have global box aspect >=2, falsifying the >=75% transfer prediction. Global
boxes are insufficient to test local ribbon dynamics (recognised highways also
usually have nearly square global boxes). Later census coverage is 324/732,
not complete; RLRLLL's later chunk is unfinished. Local-window comparison of
RLLLLRRL, RLLLLRLRRL and RLLLRLRLLL remains the discriminating next test.
Reproduce: `uv run experiments/2026-10-13-g1-ribbon-breakout/scripts/compare_survivors.py`;
JSON and per-rule CSV in that experiment's results include input hashes.

## Appended 2026-10-15: open items left by the experiments closed that day (nothing here has been measured)

- **kappa at matched area (`experiments/2026-10-14-kappa-matched-area`).** A residual rule effect on the excursion cutoff at fixed area is not established: 2 of 3 registered noise-floor
  criteria failed. Open and unregistered: rule-level regression of ln_ratio on the kappa residual given ln A with rule random effects, split seeds, all 44 rules, no matching.
- **Prefix effect on kappa (`experiments/2026-10-kappa-rule-space`, W3c).** The size-controlled gain of the prefix-8 lookup replicated on stationary rules (+0.240, CI 0.148-0.347) but is ~0 in the all-rules
  cohort when trained on all census rules (+0.031 / +0.042 on stationary test rules); stationary-trained it is +0.240. Open: does the non-stationary census tail simply degrade the lookup (w3c_cross.txt, exploratory), or is the prefix effect specific to stationary dynamics? Not run: W5 (area-matched bulk fingerprint), an area-matched W6 mutation scan, the 200-base W6 (about 8 CPU-hours, needs a registered addendum).
- **Ants' wide edge (`experiments/2026-10-14-hull-width`).** The extra width carries 2-6x the long-wavelength power of the rotor, but the high-wavenumber deficit and a rotor-stability control failed. Open: real-space S(dtheta), band power versus k
  (needs a rerun that dumps r(theta) at k = 24..30), larger census-sampled rule set.
- **Crystal rules (`experiments/2026-10-crystal-rules`).** Ray motifs are not one rigid colour motif (P2 falsified); most ray length is an alternating-turn staircase (~2 steps/cell) over a background whose alternate cells carry opposite-turn colours (exploratory, sublattice picture not verified; unrelated to the 50-86 steps/cell colour-2 ground highway). Open and not run: ray transplant onto reset/shuffled
  background, ray-end knockouts, spinner isolation, exact periodicity of the ground highway, what ends a ray, why the sweep builds ground 2, why the opposite-turn two-sublattice background forms.

## Added 2026-10-15: crystal ground-phase intervention

The registered local colour-2 reset failed its strong staircase-disruption/termination predictions in all three crystal rules (16 paired states each). Reset to blank advanced geometric termination in 3/16, 6/16, 8/16 states, while mean full-window alternating-turn fractions increased; phase advance to 3 never advanced termination. Colours 2 and 3 specify the same turn, limiting that control to revisit effects. See [protocol, commands and caveats](../experiments/2026-10-crystal-rules/README.md#s2-phase-reset-results--2026-10-15-2123-1300) and [generated summary](../experiments/2026-10-crystal-rules/results/phase_summary.txt). Open: are ray ends caused by specific encountered defects rather than the abundant ground phase? A targeted endpoint intervention with explicit exposure measurement remains unrun.

## Research priorities for the paper, 2026-10-15

[Paper-gap research avenues](paper-gaps-research-avenues-2026-10-15.md) records
prospective fixed-area prefix tests, complete boundary/interior time accounting,
paired mutation challenges, crystal edit-exposure and endpoint tests, edge-profile
mode persistence, and stronger forecast baselines. These are proposals, not
preregistrations or new measurements. The first priority combines fixed-area
sampling with episode accounting to distinguish prediction from mechanism.

### Kappa prefix robustness follow-up (2026-10-15 22:40 +13:00)
The [prefix audit](../experiments/2026-10-kappa-rule-space/README.md#prefix-audit-addendum) retains the W3c stationary lead: five-fold lookup encoding plus a five-knot nonlinear ln A(22) control gives +0.201 held-out R2 gain [0.103,0.311] on 162 rules, seed 20261015 and 2000 rule bootstraps. Removing five largest positive contributors leaves +0.150. All-rules gain +0.041 [-0.018,0.103] remains weak. This is an audit of inspected data, not fresh confirmation or a mechanism; one area snapshot may leave growth-history confounding. Reproduce with uv run experiments/2026-10-kappa-rule-space/scripts/prefix_audit.py; input/source hashes in results/prefix_audit.json. Next discrimination: matched-area mutation intervention with early-colour exposure measurements.

## Kappa mechanism plans — 2026-10-15, prospective

[Mechanism brainstorming](kappa-mechanisms-2026-10-15.md) separates four live
possibilities: excursion survival mass, prefix-dependent fresh-cell return
kernels, sparse directional return gates, and field maturation. Each now has
an experiment scaffold with draft predictions, controls and a handoff. Start
with tail-budget and age observations; gate interventions depend on reliable
predictive evidence. These are plans only, not new results or registrations;
all earlier failed predictions retain their verdicts.

### Tail budget / field age instrument pilots — 2026-10-15 23:38 +13:00

See the [mechanism continuation](kappa-mechanisms-2026-10-15.md#instrumentpilot-continuation--2026-10-15-2338-1300)
and the [tail](../experiments/2026-10-15-kappa-tail-budget/results/REPORT.md) /
[age](../experiments/2026-10-15-kappa-field-age/results/REPORT.md) reports.
Both observation-only instruments now pass reference and synthetic accounting
checks. All primary bands were reached; two drifting rules miss the largest
age band. Reserve and original age cohort support gates fail. Median log age
has weak small-band seed-half precision. No T1/T2/A1/A2/A3 scientific prediction
has been tested; neither mechanism is established or retired. Next: calibrate
and freeze actual estimators and role/fold manifests, add state checkpoints,
and resolve cohort/precision/cap choices without dropping inconvenient rules.

- **kappa uniform reference (2026-10-16, `experiments/2026-10-16-kappa-uniform-baseline`).** The probe's kappa for a uniform-by-construction walker is ~1.11, not 1 (window-mean B/S over end-of-window P/A). Paper line "kappa < 1 below uniform" should be restated relative to 1.11. Still open: why the ants sit near 0.81× this reference (rotor and memoryless ratios need their own a, β); no mechanism established.
- **kappa walker references (2026-10-19, `experiments/2026-10-19-kappa-walker-reference`).** Each walker against its own `kappa_unif(a, beta)`: memoryless (rw, pw:q) a ~0.92, beta ~0.91, reference 1.02-1.03 (not 1.16; beta is ~0.9, not 1/2), ratio 1.24-1.32; rotor ratio 1.69 (k=12..22) / 1.80 (20..26); mean-field 1.01; noisy rotor (EPS 0..1, 8 seeds, k=12..22) 1.69, **2.59 at EPS 0.01**, then 2.41/2.11/1.84/1.62/1.42/1.31/1.26. No walker is below 1.26 versus ant median 0.81 (single run, IQR 0.66-0.96). Registered (i) monotone and (iii) a <= 0.75 up to EPS 0.1 FAILED (a is 0.87 at EPS 0.01; EPS<=0.05 runs drift). Window caveat: census kappa is the last window k=26; noisy walkers escape 8192 boards before 2^26. Open: why ants are low (no walker reproduces it); memoryless at census-matched windows not run. Reproduce: `scripts/run.sh`, `scripts/run_nrotor.sh`, `scripts/analyse*.py`.

- **kappa residual vs cutoff ratio, rule-level mixed model (2026-10-16, `experiments/2026-10-15-kappa-cutoff-mixed-effects`).** Registered random-intercept REML (own implementation, calibrated on synthetic data and a label-shuffle control), all 44 rules, kappa/ln A from even seeds and ln_ratio from odd seeds, seed 20261016. The registered hypothesis FAILED: standardised effect -0.275 (k=22) and -0.194 (k=25) vs the registered <= -0.30; permutation p 0.020 / 0.096; held-out dR2 +0.118 / +0.073 but bootstrap fraction positive 0.875 / 0.866; pooled-k slope ~0. The sign is negative everywhere, but the matched-pair 76-82% overstated it. ln_ratio is heavy-tailed (a minority of rules has seed sd 2-4 in ln_ratio) and the Gaussian model is misspecified. Post hoc (unregistered) the 27-29 rules with stable cutoffs meet every threshold (Std -0.43 / -0.39); that needs a registered replication (k=23, 24) before it counts. No T2 on this basis. Reproduce: `uv run experiments/2026-10-15-kappa-cutoff-mixed-effects/scripts/{calibrate,fit,posthoc}.py`.

### Kappa prefix-exposure confirmation — 2026-10-16 (`experiments/2026-10-15-kappa-prefix-exposure`)
Registered and run (10752 specs, 24 bases x 7 arms x 64 seeds; 10 informative validation bases). The early-letter effect on B/S at fixed area replicates on fresh mutants (P3: ratio of median |d ln B/S| early/late 9.0, CI 1.27-27.6) and is sign-mixed in kappa (P5: 47% positive, mean -0.11 vs median |shift| 0.33), as W6m found. The fresh-cell long-excursion launch rate does NOT carry it out of sample: P1 FAILED (held-out R2 0.105 vs 0.20, CI -0.21..0.32). P2 (exposure features over position) FAILED on its interval bar: delta R2 +0.215, CI [-0.002, 0.281]. Open: is the exposure gain real (needs more bases), and why do early mutants fail to reach the band more often (valid 0.82 vs 0.73-0.93)? Details and caveats in the experiment README.

- **kappa prefix decoded to a leading run (2026-10-16, `experiments/2026-10-16-kappa-prefix-decode`, exploratory, post hoc).** On the ln A(22)-spline residual, stationary rules, the prefix-8 lookup (+0.20 held-out) is beaten by one number, the length of the opening same-letter run (+0.33 [0.24,0.44]); residual rises ~+0.1 ln kappa per leading step in census and pool alike; letters 9+ and rule length/R-fraction carry nothing. Registered D1 (additive fails) and D5 (tree splits late) FAILED; own-prefix-rule hypothesis recovers only 22-69%. Caveats: lead run vs ln A(22) corr -0.56 (growth-history confound possible), A-series chosen on scored data. Next: registered fresh-rule test and fixed-area leading-run mutation dose-response.

### Kappa return gates, Stage 1 — 2026-10-16 (`experiments/2026-10-15-kappa-return-gates`)
Registered and run: incremental rim/interior depth instrument (oracle-tested), 24 rules x (64 predictor + 32 target) seeds, bands A = 32768 and 131072. Adding two gate features (crossing-location concentration g1, exit-heading return spread g2) to a 4-feature depth-profile baseline did NOT improve held-out-seed boundary occupation: DeltaR2 -0.039 [-0.118, +0.006] and -0.0004 [-0.033, +0.031] (criterion +0.10, plus bootstrap and permutation). Verdict UNINFORMATIVE, not a clean rejection: the baseline (which excludes boundary occupancy itself) already has held-out R2 0.88 / 0.95, so band 1 has no headroom, and g2 fails split-seed reliability at band 0 (0.56). Open: which independent, pre-window quantity can explain what the depth-profile ratios (essentially the time budget) reproduce? Gates are neither supported nor retired; G2 (matched gate/non-gate edits) is unrun and should not be launched on this evidence. Edge case reported: 3 predictor runs with 2-6 events gave a NaN null (sensitivity: same conclusion).

### Kappa leading-run effect: fresh test and mutants — 2026-10-16 (`experiments/2026-10-16-kappa-leadrun-fresh`) — **read with the 2026-10-19 reconciliation at the end of this file: the fixed-area lead slope is reproduced by a collider model with no direct effect**
- Replicated out of sample on 176 fresh, lead-stratified stationary rules (13-14 letters): held-out R^2 gain +0.65 [0.50, 0.83] over a ln A22 spline; slope +0.152/step [0.130, 0.174] (census fit +0.195); same slope within ln A tertiles and by rule length; a refit-on-shuffle null gives ~0 (max +0.06). The slope is concave in lead (leads 1-3 +0.235, 1-4 +0.197), and retention falls at lead 6 (0.40 kept), so lead >= 5 is selection-exposed.
- Mutants (257 pairs): shortening the lead lowers ln kappa by 0.20 at unchanged area; control flips at index >= 8 do nothing; extending the lead lowers ln kappa only -0.06 (not significant) because it also lowers ln A22 by 0.29 and ln kappa follows ln A22 with coefficient ~1. Registered M1 and M2 failed as stated; the regression slope on lead (+0.158) matches the cross-section.
- Open: ln A22 is a post-treatment mediator, so "at fixed area" estimates are not clean causal effects; is kappa nearly redundant with early area (coefficient ~1)? Does the letter at index k, rather than run length, carry the effect? Needs flips that leave early area unchanged or a kappa defined on late windows only.

### Growth-clock audit: fresh constant-composition families — 2026-10-16

[Registration and results](../experiments/2026-10-16-kappa-growth-clock/README.md):
64 fresh 14-letter rules, 16 suffix families x leads 1..4, four fresh patch seeds
202610160701..202610160704, probe 24 4096. The early-versus-current-area test is
**UNINFORMATIVE**: only 7/16 complete families at k=21,22,23 versus the registered
12-family gate. There were 45/256 eventual board escapes; qualifying rules by
lead were 16/9/15/13. P1/P2 were not fitted or scored. No mechanism verdict follows;
the growth-history question remains open. A follow-up must diagnose censoring on
this same cohort rather than replacing missing families. Release/GPU tests,
four byte-identical CPU/GPU spot checks and synthetic regression calibration pass.
Reproduce with the experiment's scripts/{sample.py,run.sh,analyse.py}; per-seed
status and source/input hashes are published in its results/.

### Kappa square-loop test (H-loop) — 2026-10-16 (`experiments/2026-10-16-kappa-square-loop`): FAILED, dead at this scale (premise questioned by the 2026-10-19 reconciliation at the end of this file)
Registered mechanism: a longer opening same-letter run raises kappa because the ant circles in 2x2 loops on young frontier cells. Instrument (loop counters on the probe stepping loop; identity to `probe_walker`, path-reference, exact PersistentWalk fractions, 1-vs-6 threads) then one run of the parent's 300 rules x seeds 601..608 (176 stationary) plus the 3336 parent mutants. **P2 failed**: the total loop-step fraction (16-26% of all steps, nearly seed-independent, ICC 1.0) is not monotone in lead and the within-ln A22-tertile Spearman is +0.50/+0.40/+0.17 (< 0.5 needed). **P3 failed** on the frozen interior-only mediator (b1/b0 = 0.96 [0.91, 1.00], leads 1-4: 0.98; needed <= 0.5); C1 failed with the wrong sign for lead-colour laps (1.13); P4 failed (loops are not concentrated on the boundary: median ratio 0.78, needed >= 2); C3 failed (Spearman 0.22 on 154 pairs, unpowered). Lead-colour laps rise monotonically with lead but are at most 1.6% of steps at lead 6. Only a boundary-based mediator removes part of the lead coefficient (0.73), and that one is nearly B/S by construction (accounting). Caveats: this is the cohort where the lead effect was found (mediation is legitimate, not a replication); loops of other shapes (period 6/8) and loops earlier in the run were not tested. The lead effect remains unexplained; the surgery experiment was not started.

- **kappa/kappa_unif target is a distribution (2026-10-18, `experiments/2026-10-16-kappa-uniform-baseline/results/census_spread.txt`).** Over 2185 stationary blob rules (single run each) kappa/kappa_unif has median 0.81, geomean 0.79, 5-95% range 0.44-1.33; 20% of rules are >= 1. The reference is rule-independent (1.105, sd ln 0.004). So "why 0.81x" is two questions: the location of this distribution and its spread (sd ln 0.35, partly single-run noise). Do not treat 0.81 as a constant to derive.
  *Update 2026-10-20 (post hoc synthesis, `experiments/2026-10-20-kappa-spread-budget/`):* of the single-run variance of ln kappa, about 0.15 is start-to-start noise (ICC 0.851), 0.47-0.54 is predicted by the first eight letters (held-out prefix-8 R^2 0.55-0.63 times the ICC), and 0.31-0.38 is rule-determined but unexplained. Rough to about +-0.1; three cohorts; no uncertainty propagated. The location (about 0.8 x kappa_unif) is not addressed.
  *Registered follow-up 2026-10-20 (`experiments/2026-10-20-kappa-spread-features/`, F1-F4 all held):* held-out R^2 of ln kappa on 162 fresh stationary rules is +0.62 for the first-8-letter lookup, -0.11 for the last 8 letters and +0.08 for composition; composition adds +0.008 to the prefix. The predictable part is specific to the start of the string. Which prefix feature matters, and the unexplained third, remain open.
  *Registered follow-up 2026-10-20 (`experiments/2026-10-20-kappa-prefix-runs/`, H1-H3 failed, H4 held):* run-structure keys of the opening give held-out R^2 -0.004 (lead alone), +0.25 (first two runs), +0.34 (three), +0.48 (four), against +0.62 for the 8-letter prefix. The lead has no unconditional predictive power on the fresh rules, consistent with the 2026-10-19 reconciliation (the lead association is at fixed area and reproduced by the area collider); the prefix signal is distributed over the opening. Caveat: run keys and letter-prefix keys differ in granularity and no group-count control was run.
  *Registered follow-up 2026-10-20 (`experiments/2026-10-20-kappa-prefix-ablation/`, A3 failed):* ablating letter j of the 8-letter lookup costs held-out R^2 of 0.00 (j=1), 0.23, 0.26, 0.35, 0.40, 0.29, 0.22, 0.07 (j=8) from 0.624; a permutation control with fixed group count agrees. The information is spread over roughly letters 2-7 and not front-loaded. The lookup is a conjunctive key, so this does not separate main effects from interactions.
  *Registered follow-up 2026-10-20 (`experiments/2026-10-20-kappa-prefix-additive/`, B2 failed):* held-out R^2 is +0.11 for an additive letter-by-position ridge model, +0.35 with all pairwise products, +0.62 for the 8-letter lookup. The signal needs higher-order interactions among letters 2-8, or equivalently family membership; the design cannot separate those (prefix families overlap between train and test; ridge penalty untuned).
  *Registered follow-up 2026-10-20 (`experiments/2026-10-20-kappa-prefix-family-holdout/`, D2 and D3 failed):* holding out whole 6-letter prefix families (43 families, 8-fold CV on 2185 census rules), pooled out-of-fold R^2 against the training mean is -0.16 for the 8-letter lookup (0.59 under random CV), -0.69 for the pairwise ridge (0.30) and -0.16 for the additive ridge (0.11). The prefix signal is family membership (rules sharing an opening behave alike), not a letter-level rule that transfers to unseen families; consistent with the paper's caveat. Caveats: few, uneven families; held-out family means differ from the training mean.

### Leading-run kappa effect: fresh rules and single-flip mutants — 2026-10-16/18 (`experiments/2026-10-16-kappa-leadrun-fresh`) — **see the 2026-10-19 reconciliation at the end of this file**
Part A (300 fresh lead-stratified rules, 176 stationary): the opening same-letter run predicts ln kappa out of sample and at fixed ln A(22) (L1 gain +0.651 [0.498, 0.828]; shuffled-label null ~0; slope ~0.15 per lead step, concave in lead). Survivor selection is a caveat (stationary share 0.68 at lead 1 vs 0.38 at lead 6).
Part B (417 single-flip mutants of 157 bases, 257 kept-and-stationary pairs, run 2026-10-18 after the 2026-10-16 launch died at 600/3336): M3 HELD (shortening the lead: d ln kappa -0.198 [-0.290, -0.110], area unchanged). M1 and M2 FAILED as registered (extend arm -0.062 [-0.152, +0.025]; extend minus late-flip control -0.056 [-0.159, +0.040]) because lengthening the lead also cuts ln A22 by ~0.29, which cancels the kappa change. Per the README's criterion, causality is NOT established; an earlier "causal at matched area" write-up was withdrawn (bd8c489). Caveats: ln kappa contains ln A, retention differs by arm (extend 0.53), pooled CIs ignore shared bases, no arm flips an early letter without changing the lead. Open: why lengthening the lead shrinks the pattern but shortening it does not; next test (proposed, not registered) is an early flip that leaves the lead unchanged, area-adjusted. Reproduce: `uv run experiments/2026-10-16-kappa-leadrun-fresh/scripts/analyse_mutants.py`.

### Kappa chiral-edge hypothesis refuted; lead sets c — 2026-10-19 (`experiments/2026-10-19-kappa-chiral-edge`)
Registered hypothesis: the opening same-letter run acts on fresh ground (young edge cells) as a chiral edge layer and raises kappa. Stage 1, within-necklace (cyclic rotations, composition fixed; census, 536 necklaces / 2358 blob rules): slope of ln kappa on lead -0.007 [-0.037, 0.017] (stationary +0.044 [0.027, 0.060]); N1 and N4 FAILED. The cyclic-maximum-run alternative also failed (wrong sign); census-wide ln kappa on lead has R^2 0.001, so the cross-sectional "lead effect" exists only conditional on ln A(22). What does hold: within a necklace the opening run sets c, the births per boundary step, almost deterministically (ln c slope -0.243, R^2 0.83). Stage 3 (registered): 1/c = 1.363 + 0.696 lead fitted on 2185 census rules predicts 176 fresh rules at R^2 0.877, median relative error 4.1% (C1, C2, C3 held; naive 2x2-loop picture a = 0, b = 1 rejected; C4 failed: prefix lookups keep gaining out to 8 letters). Mechanism of a ~ 1.36, b ~ 0.70 unexplained. Open: reconcile with the leading-run M3 (conditional-on-area effect); sbg dose-response of the c law (unregistered, not run). Reproduce: `uv run experiments/2026-10-19-kappa-chiral-edge/scripts/{necklace_lead,cyclic_run,c_by_lead,c_law,c_explore}.py`.

### Mechanism of the c law; kappa's fixed-area "lead effect" is a collider artefact — 2026-10-19 (`experiments/2026-10-19-c-law-mechanism`)
Held (registered): c is a property of the rule on fresh ground. A flat torus band with an i.i.d. interior reproduces census c rule by rule (60 rules, corr^2 0.999, median ratio 0.998, 1/c = 1.399 + 0.678 lead); an all-zero, young-only or old-only interior changes it by ~0.3%. The tracer (`src/edge_trace.rs`, exact vs `probe_walker` and a brute force) gives rotor c 0.4977 (notes 0.498) and random walk 0.448. Little's law: 1/c = mean boundary reads per born cell (holds to 1.6%); 78% of circulating reads return after exactly 4 steps (2x2 loops); runs of consecutive births never exceed 3. Sparse background (`SparseBgAnt`, 60 rules): the lead slope falls 0.68 -> 0.45 by density 0.2 (0.29 among survivors at 0.4), a parameter-free single-cell rotation mixture predicts it (R^2 0.87); above density ~0.7 the ant leaves the board, so the d = 1 test was impossible. Kappa: with ln A22 determined by c and kappa (ln A22 = 11.45 + 0.687 ln c + 0.807 ln kappa, resid sd 0.09), conditioning on ln A22 reproduces the "+0.15 per lead step at fixed area" with no direct effect (null +0.145 vs observed +0.148) and it vanishes given ln c (+0.014 [-0.045, 0.062]); the E/S area asymmetry of the leading-run mutants follows from the c law (g = 0.81). Lead-preserving early flips: mean d -0.007 [-0.078, 0.060] (177 pairs).
Failed (registered): flat-plateau picture of circulating reads (D1-D4), geometric birth chains (C1), the 5-parameter transition kernel K4 (validation R^2 0.80 vs 0.90), band c > blob c (S5), B5; B1 untestable. A 3-parameter survival kernel K3 beats the lead law out of sample (0.785 vs 0.711 on 378 new rules; fresh 0.913 vs 0.877) but not the 8-letter lookup.
Still open: a = 1.4 and b = 0.68 are not derived (lead candidate: loop-formation probability x 4 steps per revolution / births per chain, decomposition 55% lag-4 returns, 13% other short, 32% long/first); why letters 5-8 matter; whether kappa has any lead-specific effect (single early flips move it by about +/-0.2 with sign set by letter direction, post hoc; S and E arms are direction-confounded). Reproduce: `experiments/2026-10-19-c-law-mechanism/README.md`.

### Reconciliation: what the c-law result does to the lead-effect notes above — 2026-10-19 (appended at merge; nothing above was rewritten)
The sections "kappa prefix decoded to a leading run", "Kappa leading-run effect" (both versions), "Kappa square-loop test" and the loop-surgery scaffold all treat the association between the opening same-letter run (lead) and ln kappa **at fixed ln A22** (+0.15 per step) as a candidate effect to explain. `experiments/2026-10-19-c-law-mechanism` (Stage 4, registered 19:03 before computation) tests the alternative that it is conditioning on a collider: ln A22 = 11.45 + 0.687 ln c + 0.807 ln kappa (residual sd 0.092 on the 176 fresh rules), lead moves ln c (-0.20/step) and not ln kappa (-0.022/step marginal), so conditioning on ln A22 forces ln kappa upward with lead.
- **Held, registered:** Q1 (observed +0.148 vs null with no direct effect +0.145 [0.137, 0.153]), Q2, Q3 (adding ln c: lead coefficient +0.014 [-0.045, +0.062]), Q4 (Part B dA = g(dc + d), g = 0.805, arm means within 0.04), P-1 (lead-preserving early flips: mean d -0.007 [-0.078, +0.060], 177 pairs). P-2 failed. I re-ran 4a/4b from the committed inputs at merge time and reproduced these numbers exactly (4c was not re-run: its probe dumps are not in the tree).
- **Consequence for the notes above:** the fixed-area lead slope is not evidence of a direct lead effect on kappa; it is reproduced by a model with none. What remains of "lead matters" is lead -> c (the c law, 1/c = 1.36 + 0.70 lead, mechanism still partly open). The M3 drop (S arm, -0.198) is **unexplained**: it is a total effect, not conditioned on area, and the post-hoc flip-direction split (L>R +0.15, R>L -0.21) cannot be separated from lead in the S/E arms.
- **H-loop and loop-surgery:** both were designed to explain the fixed-area lead effect. The square-loop failure (P2) stands as measured; its premise is now itself in doubt, which strengthens the decision not to run surgery. A mediator test for a collider-induced association was never going to find a mechanism.
- **Not established by the c-law work:** that lead has *no* direct effect (bound |b| below about 0.06 per step given ln c, one cohort, survivor selection, kappa measured at one window); the flip-direction dependence; the origin of a = 1.4 and b = 0.68.
- **Before citing the lead effect anywhere (paper, blog, new experiments):** cite it as a *predictive* association conditional on area, not a causal or mechanistic one. The paper's prefix-lookup claim (main.typ, "conditional transport predictor") is worded as prediction and is not contradicted; any sentence that says lead *raises* kappa is not supported. Read `experiments/2026-10-19-c-law-mechanism/README.md` Stage 4 first.

### Prospective local renewal scaffold — 2026-10-20

[Local renewal experiment](../experiments/2026-10-20-c-law-renewal/README.md):
selected follow-up for the unexplained c-law coefficients and letters 5–8.
Proposes a local boundary-event reward model, challenged by composition- and
lead-preserving swaps, held-out families, return-budget predictions and a
history-augmented alternative. Design generation is available; ordered-event
instrumentation and scientific analysis are not implemented. Calibration and
an excluded pilot must precede a dated model freeze and main measurement.
Draft predictions only; no new scientific evidence or claim about kappa.

#### Local renewal instrument and pilot — 2026-10-20 00:52 (+13:00)

The [recorder and pilot](../experiments/2026-10-20-c-law-renewal/README.md)
now exist (evidence revision `e81f2385199b7e005df883bf0e3627b113740cd4`).
Ordered states match a sparse path oracle and aggregate tracer. Rotor/rw
controls pass (8 seeds each, c means 0.497504/0.446602, between-seed sd
0.000467/0.008122, no escapes); synthetic stationary-reward solver calibration
passes, but the ant backoff model is not implemented or calibrated.
The excluded pilot's common-horizon gate fails: 0/4 complete families at
every k=22..26, only 2/24 individual runs usable at k=26. No main outcomes
opened and no P1–P4 verdict. Reproduce with `scripts/run_pilot_all.sh`,
`scripts/pilot_diagnose.py`; per-run hashes, commands, seeds and failures in
that experiment's `results/`. A registered support diagnostic on the same
excluded pilots is pending; it cannot rescue the failed sampling gate.
The exact immediate birth predicate is already local (turn plus fresh mask).
The open mechanism is the distribution of local states; a pooled kernel must
respect target-rule-compatible successors rather than borrow target counts.

#### Rich-state lookup lacks pilot transfer support — 2026-10-20 00:59 (+13:00)

Registered diagnostic complete, evidence revision
`0fa4db2807247a2214fbcd433876d6062ba83e37`, same 24 excluded runs and k=26.
Counts-mode summaries reproduce the original runs exactly; flow and reward
checks pass. S0/S1/S2 all have 100% unseen read mass in every held-out pilot
family run. Eight turns plus patch, omitting source colour, still has median
94.44% unseen mass; current turn plus patch has median 2.26%, maximum 7.46%.
This establishes a feasibility problem for the proposed lookup in this
pilot, not a rejection of all local mechanisms or a main-cohort score.
Reproduce: experiment `scripts/support_probe.py`; compact evidence and hashes
in `results/support_report.json` and `results/pilot_support/`. The failed
common-horizon gate stands. Main P1–P4 remain untested. Next proposal:
compositional target-rule updates with learned missing patch/return conditions,
requiring its own calibration, sampling revision and frozen predictions.

#### Finite short-phase memory is insufficient with a uniform exterior — 2026-10-20 01:34 (+13:00)

Registration/code `c826721c2591201c45efeca9900abac5f8f4f841`; outcomes and
recipes `a878d5e9acc3411fa0a3b745d66a8e3a552e6ee8`,
[experiment](../experiments/2026-10-20-c-law-renewal/README.md). Four excluded
base rules, two seeds, full plus five uniform cache radii and r=4 zero reset.
New prospective clock: 2048 warmup + 8192 measured boundary reads, cap 2^28.
Window/path/cache oracles and full release tests pass; rotor/rw clock controls
pass with means 0.500748/0.462433 (8-seed sd 0.003133/0.006132), but rw is
0.015830 above its earlier fixed-time mean, so finite-window bias remains.

Exact deduction: a quarter-turn return of k steps has maximum coordinate
excursion <=k/4. Radius-r phase eviction therefore requires lag >=4(r+1).
r=4 preserves every <=16-step source phase. Nevertheless both uniform r=4
and r=8 FAIL registered M1/M2 (8/8 eligible pairs): median |ln c ratio|
0.012054/0.012623 but maximum 0.298926/0.276185; median largest budget errors
0.248662/0.200881 (limit .20, latter narrowly fails). Zero reset caps in 6/8;
M3 has only two defined comparisons and is UNINFORMATIVE, not a prior test pass.

In RRRRLLRRLLLLRR, r=4 c is 31–35% higher in both seeds (24–26% fewer reads
per birth). Exploratory decomposition loses 1.63/1.59 long reads per birth
and gains 0.51/0.47 lag-4 reads, net -0.95/-1.05. Lead-2 changes nearly cancel
in total c. Thus retaining direct short-phase clocks does not preserve their
frequencies or the full cost. This is a failure of the uniform-exterior
closure, not a universal locality theorem. Main outcomes remain unopened.
Commands: `scripts/launch_memory.py`, `analyse_memory.py`, `diagnose_memory.py`;
JSON evidence, all cases/caps and figure are in that experiment's results.
Next proposal: retain only the old turn bit at forgotten cells, then compare
two-turn information, to separate directional field memory from distant phase
timing. This proposal is unimplemented and needs fresh registered tests.

### Lattice c law: slope falls with loop length; the kappa deficit is not square-specific — 2026-10-20 (`experiments/2026-10-20-lattice-c-law`)
Registered (README, before any lattice c): A b ~ loop length, B b lattice-independent, C b ~ 4/z, as vectors over (triangular, hex R-lead, hex r-lead). 960 ants (48 per lead 1..5 per stratum, primitive rules of length 10-14) and 120 controls, 2^27 steps, board 8192, generic octave probe `src/lattice_probe.rs` (oracle tests: square equals `probe.rs`, hex/triangular equal a HashMap version; mean-field gate G4 passes at 0.994/1.005/1.004). **A, B and C are all disproven as stated.** Registered fits: b = 0.696 square (census 0.70), **0.355 triangular** [0.340, 0.371], 0.876 hex R-lead [0.78, 0.98]; the hex r-lead OLS is wrecked by one rule with 1/c = 390 (the frozen decision rule returns "undecided"; L1, L2, K4 failed). Post hoc (unregistered), per-lead medians give hex r-lead b ~ 0.27, so b is 0.86, 0.70, 0.34, 0.28 for loop lengths 3 (hex R), 4 (square), 6 (triangular), 6 (hex r): it **falls** with loop length. Intercept 1.3 on square and triangular, ~2.4-2.8 on hex. Kappa: ant median kappa/kappa_unif is 0.77 square, 0.74 triangular, 0.86 hex (random walks 1.28-1.44), so the deficit is not a square-lattice artefact. K3 held (no lead slope of ln kappa beyond 0.08). Open: why b falls with loop length (the Little's-law derivation b = l_b / N_b leaves N_b's scaling free; the data say N_b grows faster than l_b), the hex letter-type effect, more loop lengths, whether the intercept tracks coordination. Reproduce: `experiments/2026-10-20-lattice-c-law/README.md`.

#### Native boundary clock rejects the excursion-duration rescue — 2026-10-20 07:35 (+13:00)

[Renewal audit](../experiments/2026-10-20-c-law-renewal/README.md), registered
3521b6c037168657e26b21bb0b6bdc254eed8faf, implementation
b1bcbbc4844a221abb02a36778664ae23a53ccaf: all 40 pilot summaries replay
exactly; sparse native-lag oracle, synthetic time-stretch/order checks and full
release tests pass. Same four excluded rules x two seeds, 2048+8192 boundary
reads; no main outcomes. All compressed policies FAIL native budget N1 and
complete-wait/adjacent-wait N2. Both-bit sensitive-rule waiting TV .143930/.145131,
serial TV .289429/.281639, versus full-ant seed distances .044029/.041941.
So physical excursion stretching alone cannot explain the earlier failed
physical-budget tests. Close c still conceals a different boundary birth process.
No universal locality rejection, fitted coefficients or asymptotic claim.
Reproduce: experiment scripts/run_native.py and analyse_native.py; exact counts,
source/binary hashes and cases in results/native_v1/, results/native_report.json.
Next proposal is one coupled phase edit preserving two turns, to separate delayed
future-clock release from accumulated geometry changes under repeated resets.
It needs its own registration/oracle; no such causal branch test has run.

## Added 2026-10-21: highway preconditions (causal seeds)

`experiments/2026-10-21-highway-preconditions/`: in all 406 independent census highway onsets (<= 1e9) the future's
dependence on the grid collapses, within about one period of onset, to a fragment of the highway itself plus a few cells
(median 3) at the territory edge. Seeds are not shared across unrelated rules. Open, unregistered so far:
- Q17. Why does onset time grow with highway size (self-overlap, period, slowness), at only ~0.018 decades per cell?
  A random colour search would cost ~log10(n) decades per cell. What in the chaotic phase pre-builds highway fragments?
- Q18. Are the "+3" non-highway cells of the pre-onset seed a trigger (knock-out kills the launch) or incidental?
