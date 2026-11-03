# Derivation and design risks

## Why the original factorial cannot identify the proposed scale

For uniform fresh R/L/U, every U returns to the departed predecessor. To reach the m-th fresh departure requires avoiding U on the previous m-1 departures. Thus an N-step run has probability at most min(1,N(2/3)^(m-1)) of any non-origin cap activation. Self-intersections only reduce exposure. At N=2^31, m=128 and 200 trajectories this union bound is about 1.86e-11. The initial origin run has a separate negligible bound at large m. Integer-mapped categorical draws require their exact avoidance probability in place of 2/3.

For the own-colour-zero policy, every fresh turn is identical. Four quarter turns close a square, so m>=8 never activates, including the initial loop. Such arms are identity controls. Failure of their W/m plot to collapse says nothing about the causal effect of an active cap.

These are geometric/probability arguments preceding the new study, not ant measurements. A maximum permitted length is not automatically the characteristic length of the actual distribution.

## An active spatial scale without changing the base policy

Fix q=1/128, the probability of a quarter turn on a fresh departure; otherwise go straight. On the all-straight branch the first m-1 departures lie on a ray and the m-th departure reverses. On a flat fresh half-plane this branch has probability (1-q)^(m-1), bounded below by e^-1 for all tested m<=128. For an entered run let D be maximal distance from its first fresh cell. On this branch D=m-1, and always D<=m-1. Consequently

    (m-1) (1-q)^((m-1)/2) <= sqrt(E[D^2]) <= m-1.

This shows an RMS penetration scale proportional to m over the tested range *on the calibration geometry*. Duration weighting also preserves order-m scaling: the straight branch contributes order m^3 to E[r D^2], while E[r]<=m. The calibration must define its exact ell_m (sqrt(sum r D^2 / sum r)) and verify the implementation against this order-of-m argument. The origin trial is excluded.

Ant boundaries have bays, holes and near neighbours. A ray may hit old territory early, so the flat-plane result does not prove in-ant exposure or ell_m~m. That is why G3 records actual cap activations and why depth is measured against the pre-entry territory, not the territory after growth.

The key internal control holds q fixed across caps and against the uncapped arm. A family with q=1/m would change persistence and cap together and confound their effects. That alternative is not the primary design.

## Conditional crossover scaling

Assume the intervention has spatial scale ell_m proportional to m, and suppose a single-scale growth crossover exists:

    W(t,m) = ell_m F(t/t_cross(m)).

If the pre-crossover regime has W approximately C t^a with C independent of m, matching at W_cross=k ell_m gives t_cross proportional to ell_m^(1/a). A diffusive-width a about 0.46 gives about m^2.17; ballistic width a=1 gives about m. We cannot borrow a from the old random-R/L experiment: the new walker has highly persistent fresh motion. Measure a on excluded controls and report the conditional scaling; primary confirmation tests the spatial relation W_cross~m without choosing a time exponent after inspection.

A~W^2 requires compact geometry. It cannot convert alpha_A about 0.9 into alpha_W about 0.45 on a porous or anisotropic territory without independent evidence. Log both spans, hull and occupancy.

The compact-regime alpha_A band [0.59,0.71] and early porous band [0.86,0.91] are inherited quantitative conjectures, not consequences of the cap. They remain separately scored. This design may falsify those numbers while retaining a cap-dependent crossover.

## What could still go wrong

- Long straight fresh runs may manufacture highways, strips or sweepers. Count ordering, retain pre-onset data and do not explain it under Q38 here.
- The first uncapped run can make a large seed territory; origins are not interchangeable with later entries. Show early windows separately and exclude origin from mediator statistics.
- Actual boundary geometry can suppress long excursions even when the flat-plane manipulation works.
- Changing m changes the colour field deposited on fresh ground. Matched uncapped controls isolate the intervention, but cannot prove a mediation path through run length alone.
- The uncapped fixed-q arm also has a natural persistence scale near 128. Scaling collapse over caps below that scale is a test of this finite range, not an asymptotic universality statement.
- A flat exponent curve trivially collapses. Require a genuine downward change and compare to unscaled W with matched rule support.
- Ordered and resource-censored runs select the remaining cohort. Report denominators and support changes; a clean complete-case curve is insufficient by itself.
- One seed per rule leaves stochastic variability entangled with between-rule variability. The main estimand averages over sampled rules and their fixed assigned streams; controls provide eight-seed diagnostics, not a complete decomposition.
- Census blob membership was defined under original dynamics and finite horizons. No guarantee carries over to this intervention.

## Interpretation matrix

| Exposure/coverage | Growth result | Reading |
|---|---|---|
| Failed | Any | Inadequate manipulation or horizon; no mechanism conclusion |
| Passed | Compact late regime plus nontrivial collapse | Finite-window support for an active-cap scale, within this policy family |
| Passed | Porous late growth with W/m large and no ordering | Counterexample to this quantitative sufficiency prediction |
| Passed | Dominant crystallisation | Competing outcome; growth comparison loses support |
| Passed | Compact but no proportional crossover | Boundedness may matter, but the single-scale m model fails or is unresolved |
| Passed | No early porous band | Original numerical conjecture fails; inspect the prespecified broader cap-effect test |
