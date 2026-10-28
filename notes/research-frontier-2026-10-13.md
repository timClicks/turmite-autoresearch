# Research frontier (2026-10-13)

Open questions, research problems and areas to investigate, drawn from `notes/summary-2026-10-13.md`, `research-outputs/scholarly-articles/cube-root-growth/main.typ`, `notes/frontier-status.md` and `notes/open-questions-hypotheses.md`. It follows the earlier `research-frontier.md` (items 1-32).

Nothing here has been measured. Every prediction below is a proposal written on 2026-10-13 *before* any test; per AGENTS.md, don't edit a prediction after seeing data, append what happened. Predictions are guesses to make the experiments discriminate, not results.

## A. Open questions from the results

### A1. Why does kappa take its value, and why does it drift in some rules?
kappa (edge occupancy relative to uniform spread) is about 0.9 for core rules, about half the rotor's 2.0, and has no explanation. It drifts in the outliers: toward 0 in the log-growers, upward in the 103 fast rules (gamma_kappa about +0.17).

- **Hypothesis:** kappa is set by the persistent-walk reflection at the edge. A walker with turn probability q = #R/n, reflected off blank ground, has an edge occupancy fixed by q and the colour mix of edge cells (mostly colours 1-2).
- **Test:** build the half-plane model from P2.3 of `open-questions-hypotheses.md` (straight edge, measured edge colour mix, uniform interior) and compute kappa per rule.
- **Prediction:** it explains more than 50% of the across-rule variance of kappa on held-out rules, with the same train/held-out split used for the c model (R^2 = 0.66). If it explains under 20%, the edge colour mix is not the controlling factor.
- **Drift:** for rules with |gamma_kappa| > 0.1, check whether the interior colour distribution (TV distance from uniform) is also drifting. This would link kappa drift to the "not well mixed" rules (35 of 40 are well mixed in the random sample; the 5 that aren't are the candidates).

### A2. Is the edge exponent exactly 1/2?
beta is about 0.52 for ants and rotor alike, with local slopes drifting toward 0.5 (0.51-0.53 at 2^26-2^28). The rotor's value is not proved.

- **Test:** extend the rotor local-slope series to 2^34 or beyond with a lean walker, and fit beta(t) = beta_inf + b * t^(-x).
- **Prediction:** beta_inf is within 0.005 of 0.5 for the rotor. If the fit instead prefers beta_inf of about 0.51 or more with x > 0, the cube root would have a roughness correction.
- **Ants:** repeat on the six long-run rules. Look for rule-to-rule differences in beta_inf (RLR was noted as not converged).

### A3. Why does the ant's visit density equal the rotor's cone?
Both give density 3t/A * (1 - r/R_eq) to a few percent. A derivation would also fix the 2/3 exponent.

- **Hypothesis:** the cone is the stationary profile of any walker whose only dynamics is a reflecting boundary moving at rate set by the local density at the edge. The shape would then follow from the free-boundary problem (quasi-static diffusion with a moving front), not from rotor specifics.
- **Test:** solve the radial free-boundary problem numerically with a flux-driven front and compare the profile.
- **Prediction:** it gives a linear-in-r profile with the same 3t/A prefactor. A different profile (for example Bessel-like) would kill the idea.
- **Control:** measure the profile for the random-background variant (radius exponent 0.47, item 26) and the sqrt(t) turmite cluster. The cone should fail there.

### A4. Why is the ants' boundary width wider than the rotor's?
Ants: 0.25-0.27 at 2^28. Rotor: 0.13-0.16 under the same estimator. Kapri and Dhar report about 0.13, and note the drift.

- **Test:** local-slope series for the ants out to 2^32 and beyond, to see if the slope falls the way the rotor's does (0.19 to 0.13 over 1e4 to 1e7 steps).
- **Prediction:** if the ants' slope is falling, it stays above the rotor's at matched t but trends down by at least 0.02 per decade. If it is flat within 0.01 over two decades, the classes differ.
- **Open:** a width that grows as t^0.26 against t^0.13 would mean the edge is roughly twice as rough at the same age. Check whether edge-width exponent correlates with kappa or with the rule's q.

### A5. Why only about 28 home types?
556 tethered rules share about 28 discrete home types (spread values equal to 0.3%, across different rules and territories).

- **Hypothesis:** the home type is labelled by a coarse invariant of the rule, such as the multiset of colours at which it turns R or L, or the position of the rare colours.
- **Test:** cluster the 556 rules by spread value, then look for a rule feature that is constant within each cluster and differs between them.
- **Prediction:** at least 80% of clusters are separable by a single feature, tested by a classifier on held-out clusters. Failing that, the types are a property of the dynamics, not of the rule string.
- **Question:** do rules that share a home type share the home configuration up to translation or symmetry, or only the statistics?

### A6. Why are rare colours the critical cells?
Rare colours (6, 8, 10 for one hard rule, 0, 6, 8 for the other) are critical in every tethered rule tested (swap ratio about 2, recolour about 1.3). Parity is not.

- **Open:** are they rare in the other 112 rules of the same class, as the open question asks? Count colour frequencies inside the home for all tethered rules.
- **Hypothesis:** rare colours are where the home's rewrites are least frequent, so a corrupted cell there is rarely overwritten back into agreement. Corruption of a frequent colour self-heals.
- **Prediction:** the loss from corrupting a cell falls with how often the ant visits it per unit time, after controlling for colour. If colour still matters at equal visit rate, rarity is not the mechanism.
- **Link:** the knockout map found hot tiles rich in rare-colour cells (partial rho 0.41-0.48), but also that 3 cells can reproduce the 3x3 effect. Find the minimal critical set by greedy cell selection, with the earlier null as a control.

### A7. Is RRLLLLLLR truly non-self-averaging?
The CV of A/t^(2/3) rises with t, and alpha_w is 0.38 +/- 0.07. Every other rule's CV falls (9 of 11).

- **Test:** 200 or more seeds (random 5x5 patches) to 2^30. Look at the distribution of A/t^(2/3), not just its CV.
- **Prediction:** if it is non-self-averaging, the distribution develops multiple modes (several "phases") and the CV keeps rising. If it is slow convergence, the CV peaks and then falls.
- **Next:** search the census for other rules with rising CV, using the short-run proxy (CV slope over 2^20-2^26).

## B. Caveats turned into research problems

### B1. Exponents come from 7-octave windows
- **Problem:** the rotor calibration quantifies the finite-window bias but can't show the ants share it. The 11-rule, 24-seed run to 2^30 found 6 rules matching the rotor and 5 not.
- **Plan:** push 20 representative rules to 2^34 or beyond with the lean ant (2.1x faster), with the window slid in 2-octave steps.
- **Prediction:** local exponents converge toward 1/3 monotonically for the 6 matching rules. For the other 5, either they converge to a different value (a true rule-dependent exponent) or the gap closes at a rate consistent with a correction t^(-x).
- **Decision rule:** declare "exactly 1/3" only if the extrapolated value is within 0.005 for at least 15 of 20 rules.

### B2. Each rule has one trajectory
- **Problem:** a rule is a single deterministic orbit from a blank board, so the between-rule bootstrap is a statement about this set of rules.
- **Plan:** use the 5x5 patched-start ensemble for a larger rule sample (currently 40 rules x 12 runs), and a different ensemble (random sparse backgrounds at low density) as a robustness check.
- **Prediction:** the ICC for alpha stays low (about 0.07), so rule-to-rule differences in the exponent remain small compared with run-to-run noise.

### B3. Rule length is capped at 12
- **Problem:** rules of length above 12 are the majority of rules. Both the census and the c model stop there.
- **Plan:** sample random rules of length 14, 16, 20 and 24 (fixed seed, uniform over rules starting with R), run to 2^27, and apply the probe.
- **Prediction (written now, before the run):** median width exponent stays within 0.01 of 0.333, the fraction of log-growers keeps its length-12 value to within 5 points, and the c model keeps R^2 above 0.4.
- **What would break it:** a trend of the log-growing fraction with n, or of the exponent with n, would show that the cube-root regime is a short-rule property.

### B4. 153 rules weren't fitted, and the fast tail is under-represented
- **Problem:** these ran off the probe grid before 2^26 steps or had a window with no new cells. The fastest growers are the likely ones to leave the grid.
- **Plan:** rerun them on a larger grid, or with a hash-based sparse board, and fit them.
- **Prediction:** they have a higher median alpha than the analysed blob rules, with a heavier fast tail (gamma_kappa > 0). If they match the analysed rules, the missing-data worry is small.
- **Also:** report how the census median and the fast fraction (103 of 2,622 now) change when they are added.

### B5. Highway classification is finite-time
- **Problem:** 304 builders were identified by finite simulation. In the 807 unresolved rules run to 10^10, 38 (4.7%) became highways in (10^9, 10^10]. The pre-registered 1% was falsified. **[Corrected 2026-10-21: 22 of the 38 (1e9,1e10] and 4+ of the 16 (1e10,1e11] "highways" are board artefacts; genuine yields 1.98% and 0.68-1.64% (1.64% if the 7 pending rechecks confirm); see `experiments/archive/2026-10-late-highway-board-check/README.md`.]**
- **Plan:** extend the 10^10 run to 10^11 or 10^12 for the surviving rules, using the lean ant.
- **Prediction:** the onset rate per decade stays about flat (slope +0.015 +/- 0.026), so about 4% of survivors escape each decade. A falling rate would support a finite set of late highways.
- **Implication:** if the rate stays flat, the "chaotic" census contains rules that will eventually build highways, and every exponent in it is a transient. This is the most dangerous caveat for the headline result.
- **Related:** the onset clusters (28 of 38 in shared-prefix groups, roughly 10 independent events) suggest onsets are correlated through the rule's prefix. Test whether shared prefix predicts shared onset time order.

## C. Mechanism and theory

### C1. Derive the cube root for a reversible ant
Bou-Rabee and Peres prove a convex limit shape for the rotor, but d/(d+1) is only a lower bound and no proof route exists for reversible ants. Open: a heuristic that gives A ~ t^(2/3) without assuming constant c and kappa. The aim is a quantitative claim, for example kappa = f(q), that can be checked against A1.

### C2. Rotor with non-uniform initial arrows
The paper's own suggested next step. Vary the initial arrow distribution in a controlled way (bias toward one direction, or a fraction of fixed arrows).
- **Prediction:** kappa changes in a controlled way while c stays near 0.5. The exponent stays at 1/3 as long as the bias is bounded. This directly tests whether kappa is a free parameter of the cube root.

### C3. Why is c flat?
c is flat in time for 99.7% of blob rules, and the letter model explains 66% of its variance. The remaining question is why it is time-independent while the edge colour mix is set by the ant's own history. Check if the edge-cell colour distribution is itself stationary.
- **Prediction:** edge colour shares are constant to within 5% over three octaves. A drifting share with constant c would mean a cancellation.

## D. Extensions

- **D1. Other universality tests:** the turmite sqrt(t) cluster (1,560 of 65,536 tables) is an exact different class. What distinguishes it? Is it ballistic-diffusive, with a different boundary dynamics?
- **D2. Higher dimensions:** the 3D rotor is transient, so it can't calibrate the 3D ant (extent 0.245, volume 0.788). Find another 3D calibration walker, or go to 2^32 in 3D to test 1/4 and 3/4 more tightly.
- **D3. Noise crossover:** the class changes somewhere between eps = 0.1 and 0.6. Locate the transition and see if it is sharp.
- **D4. Many ants:** A_m(t) ~ A_1(mt) holds within 0.87-1.23. Look for the m-dependence of the deviation and whether it is systematic.
- **D5. Web demo:** add the A1 half-plane prediction of kappa next to the live measurement for any rule the user picks.

## E. Open items from the knockout map (`notes/knockout-map-results.md`)

Two hard rules (RRRRRLLLLLL, RLLLLRRRRLR), one territory each at age 2^24, shuffling 5x5 patches (3 permutations per tile) against a null of 100 random 25-cell swaps. Established there: 3.5% of tiles are reproducible hot spots (null 0.7%), the worst 5x5 windows remove 20-30% of the tether (fresh permutations confirm 0.09-0.15), and the sensitive region is a disc of radius about 15-20 around the tether centre. The return-route idea (P3) was not supported (partial rho 0.13 and 0.03, intervals contain 0), and a contiguous patch hurt no more than scattered cells (P4, unpredicted). The three follow-ups the note lists are the first three items below.

### E1. Why is RRRRRLLLLLL's hot region one-sided?
Its 11 hot tiles all lie north of the tether centre (octant counts 0,0,0,2,2,2,4,1), while RLLLLRRRRLR's 17 form a rough disc.
- **Hypothesis:** the lobe is set by where this particular field built up, not by a fixed direction in the rule's geometry.
- **Test:** repeat the map on the 2^26 grids in `experiments/archive/2026-10-tether-rules/dumps_f/` and on other ages (2^22, 2^25).
- **Prediction:** if the lobe is tied to the field, it moves or grows with age and keeps its offset from the tether centre. If it is tied to the rule's geometry, it keeps a fixed compass direction. Also rotate the field by 90 degrees and rerun: a rule-fixed lobe should not rotate with it.

### E2. Is the sensitive disc set by the tether radius or the excursion scale?
- **Test:** redo the loss map with near_home measured at radius 6 and 15 instead of 10.
- **Prediction:** if the disc tracks the tether radius, its radius scales with the measuring radius. If it tracks the excursion scale (42% of excursion steps fall in r = 10-15 from the start), it stays at about 15-20 whatever the measuring radius.

### E3. A route definition that breaks the occupancy collinearity
rho(route, occupancy) is 0.88/0.92, so the partial correlation has little power. The null for P3 is therefore not strong evidence against return paths.
- **Test:** define routes as the last exit-to-return path of each excursion, or cells on the shortest homeward legs, rather than all steps beyond r = 10.
- **Prediction:** if return paths matter, partial rho for the new definition exceeds 0.15 on both rules. If it stays near 0 with a definition that has far lower collinearity (say below 0.6), the return-path idea can be dropped.

### E4. Why does a contiguous patch not hurt more than scattered cells?
Full-tile mean loss is 0.0060 against 0.0093 for 25-cell swaps at similar dose. The note says it has no tested reason, and the hottest windows are the exception.
- **Hypothesis:** damage is per critical cell, so scattering hits more of the sparse critical set than a block does. The block only hurts where it lands on the clustered hot places.
- **Test:** compare loss with the number of rare-colour cells changed (links to A6), for both patches and swaps.
- **Prediction:** loss is a function of the count of critical cells changed, the same for patches and swaps. If patch and swap curves stay apart at equal critical count, contiguity matters.

### E5. Knockouts across more rules and territories
Only two rules and one territory each. The note's null is the only noise estimate, and the coarse grid origin and tile offset were not varied.
- **Plan:** run the map on 5-10 more tethered rules, covering several of the 28 home types (A5), and vary the tile offset.
- **Prediction:** hot-tile fraction is 2-6% in every rule and the worst 5x5 windows remove 15-30%. A rule with no hot spots would imply a different kind of hold. Check whether rules sharing a home type share the hot-spot pattern.

### E6. Does the map connect to the formation question?
Frontier item 12 found no detectable formation event, and the map shows the home is graded and spread over a disc. Combine them: knock out the hot windows at earlier ages (2^18-2^22) and ask when a window first becomes critical.
- **Prediction:** the critical set grows with the cup, so the corrupted *fraction* needed stays constant (item 13), but the hot windows' positions are fixed early. If the hot windows appear late, the home forms by accretion on a prior core.

## Suggested priority

1. **B5** (highway rate to 10^11 or more): decides whether the census is a transient.
2. **B3** (rule length 14-24): extends the headline claim to the majority of rules.
3. **B1** (2^34 runs): decides "exactly 1/3" for the ants.
4. **A1, A3:** the two best chances at a mechanism with numbers behind it.
5. **A5, A6, A7:** the strange findings; cheap and well-posed.
6. **E1-E3:** the knockout note's own follow-ups. E1 and E2 are cheap reruns of existing code (`examples/knock.rs`); E3 needs a new route definition.

---
Outcomes (appended 2026-10-13; the predictions above are unchanged): see `notes/frontier-2026-10-13-results.md` for the status of every item, the protocols written before each run, the commands and data files.
