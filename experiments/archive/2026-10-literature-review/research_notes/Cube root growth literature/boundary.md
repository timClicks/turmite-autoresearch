# Boundary measurements and interface scaling

## What is the closest boundary comparator?

### Takeaway
The boundary-width comparison is defensible as a finite-window comparison, with conventions stated. Kapri–Dhar do not establish a rotor universality class, and the present ant measurements do not establish one either.

### Cited Findings
- Kapri–Dhar, arXiv:0906.5506v2 (17 September 2009), PRE 80, 051118, DOI 10.1103/PhysRevE.80.051118, Sec. III.E, PDF p.5, Eq.10/Fig.8: surface means visited sites touching an unvisited neighbour, including hole rims. Their width is the square root of the ensemble mean of per-cluster radial variances, using distance from the origin. They use 10,000 clusters; Fig.8 spans approximately 10²–10⁷ steps. Body: δ=0.136±0.02; caption: ±0.002; derived radius exponent 0.40±0.06. These inconsistent errors must be disclosed. Their KPZ suggestion requires a time change making radius linear. — [Full text](https://arxiv.org/pdf/0906.5506v2).
- Papoyan, Poghosyan and Priezzhev, arXiv:1606.01756v2 (15 July 2016), DOI 10.1088/1742-5468/2016/07/073209, Sec.I pp.2–4 and Sec.IV pp.10–11, Eqs.4.1–4.6: a single clockwise rotor walker on a semi-infinite square-lattice cylinder, special boundary rotors and random bulk rotors, separates circumference from growth. Surface-height variance is sampled at excursion endpoints. They report circumferences 100,200,…,1000, at most 200 excursions, 10,000 samples; fitted α=0.51±0.03 and β=0.35±0.05. Their scaling formula uses endpoint step time t_n, whose mean grows as n². Do not identify excursion count and walker-step time. This is a closer finite-size boundary comparator than aggregation results. — [Full text](https://arxiv.org/pdf/1606.01756v2).
- Current local instrument uses radii about the visited centroid, not the origin; each run's slopes are then summarised across seeds/rules. — [shape source](../../../../../examples/shape.rs), [hull source](../../../../../examples/hull_width.rs), [manuscript](../../../../../research-outputs/working-papers/cube-root-growth/main.typ).

### Inferences
- Replace “Kapri and Dhar's definition” with “the same surface-site criterion, using centroid-centred radii here”; state the ensemble difference separately. A matched calculation of origin-centred sqrt(mean variance) would quantify the remaining convention effect.
- Their 0.40 radius-trajectory exponent is not a spatial roughness exponent; their own local-growth clock makes it a temporal growth exponent. A rotor fit closer to 3/8 than 1/3 cannot by itself discriminate interface classes.

### Gaps
- The published KD typeset error discrepancy was not resolved against an authoritative publisher full text; quote both v2 readings or omit the uncertainty when saying “about 0.13”.
- Cylinder paper is numerical evidence in a different geometry with special boundary conditions. Its time convention requires care before quantitative transfer to plane trajectories.

## Which interface observables are actually needed?

### Takeaway
Measure spatial correlations, their evolving correlation length, and persistent shape separately. A width fit along an expanding cluster mixes size and time.

### Cited Findings
- Kardar–Parisi–Zhang (1986), PRL 56,889–892, DOI 10.1103/PhysRevLett.56.889, p.889 Eq.1 and p.891: coarse-grained single-valued local growth with smoothing, slope-dependent growth and short-range stochastic forcing; for a one-dimensional interface α=1/2, z=3/2, β=1/3. Their discussion explicitly distinguishes strip saturation from the growing spherical geometry. — [Original paper scan](https://courses.physics.ucsd.edu/2020/Winter/physics116/KPZ%20Model.pdf).
- Ramasco, López and Rodríguez (2000), arXiv:cond-mat/0001111v1, PRL84,2199–2202, DOI 10.1103/PhysRevLett.84.2199: pp.1–2 Eqs.1–5 distinguish global width, local width, height differences and spectrum. A growing correlation length controls finite-size crossover; a growth exponent is α/z under ordinary Family–Vicsek scaling. Local and spectral exponents may differ from global scaling, so matching one slope is insufficient. — [Original preprint](https://arxiv.org/pdf/cond-mat/0001111v1).

### Inferences
- Minimal first experiment is already designed: finish the registered hull-checks full run, preserving its coverage, matched-radius and coarsening gates. Report physical separation ℓ≈RΔθ, absolute and normalised power, and phase persistence. Its fixed angular bands are useful diagnostics but cover physical wavelengths growing with radius; they do not independently hold a local physical scale fixed.
- Then measure unfiltered (or explicitly transfer-function-corrected) G(ℓ,t), local window widths and S(q,t) over a resolved range with lattice scale ≪ℓ≪R. The current mode-9–64 filtered structure function has a filter-imposed scale and plateau; its fitted correlation length is descriptive, not automatically the interface's intrinsic ξ.
- To compare with KPZ, specify and justify an effective growth clock, test ξ in physical distance versus that clock, and test local/global/spectral scaling jointly. Check persistent lattice anisotropy (especially mode 4), centroid motion, overhang/outermost-envelope bias and angular resolution. Finite-size saturation at independently controlled lateral size would be stronger evidence; cylinder results motivate this option, but a new ant geometry changes the model.
- Determinism is compatible with an effective stochastic description; locality and short-range effective correlations must be tested rather than assumed from visual texture.

### Gaps
- Family–Vicsek (1985), DOI 10.1088/0305-4470/18/2/005, J.Phys.A18 L75–L81: publisher DOI and discovered scan failed to open. Original full text not verified. Attribute the explicit formulas above to the verified Ramasco paper rather than pretending to have inspected FV equations.
- No reviewed argument establishes that ant coarse-grained noise, memory or growth clock meets KPZ assumptions.

## What should change in the boundary claims?

### Takeaway
Keep the measured gap, qualify its population and finite-window meaning, and update the stale statement that wavelength content is untested. Do not turn mixed band results into an accepted lobe hypothesis.

### Cited Findings
- Width-radius refit: 14 rotor seeds and 36 ant runs across six rules, k=22–32, means 0.401 and 0.714; later windows give 0.389/0.685 and 0.395/0.637. Radius choices change means by <0.005. — [refit JSON](../../../2026-10-w-width-radius-refit/results/width_radius_refit.json), [manuscript paragraph](../../../../../research-outputs/working-papers/cube-root-growth/main.typ).
- Hull split: 24 ant runs (six selected A4 rules, four seeds) and eight rotor runs through 2³⁰; outer/all temporal slopes ants 0.239/0.239, rotor 0.135/0.130; hole-rim shares 0.038/0.252. Band follow-up is registered mixed: low-mode excess decreases with wavenumber, but the high-band prediction fails. The normalised-power temporal drop contains (W/R)² and supplies no independent corroboration. — [registration, results and correction](../../../2026-10-hull-width/README.md).
- Hull-checks contains synthetic calibration and plumbing pilot only; full science run has not started. Pilot exclusions are not evidence for either shape hypothesis. — [current status](../../../2026-10-hull-checks/README.md).

### Inferences
Claim audit for main.typ (read 2026-10-15):

| Current claim | Decision / replacement |
|---|---|
| Intro: about twice as fast | Retain as approximate finite-window temporal-exponent comparison; do not imply exact factor-two law. |
| “at matched sizes 2²²–2³²” | These are step counts, not matched radii. Say “matched step-count checkpoints”; radius matching is pending. |
| Wider edge “generic to ants” (near line402) | Narrow to examined cohorts; selected six-rule and crust cohorts do not establish a census-wide property. |
| Wsurf is “Kapri and Dhar's definition” (near line409) | Same surface membership, different centring and ensemble aggregation; correct explicitly. |
| Outer hull “smoother at small scale” | Describe lower finite-resolution box-count slope and steeper measured spectral decay; avoid asserting an asymptotic fractal dimension. |
| Whether excess lies in lobes “untested” | Update: within-checkpoint low-mode excess observed, registered band decision mixed; persistence and local residual unresolved. |
| Height correlations and removal of shape modes needed | Retain, specifying mode0–2 already removed in angular spectra; persistent higher low modes remain. |

Suggested related-work wording: “Kapri and Dhar measured surface-site radial width for Eulerian walkers and suggested a KPZ comparison after changing the growth clock. Later cylinder simulations separated lateral size and time and found width scaling near KPZ values. Our ant trajectories show a larger finite-window width exponent than the rotor controls. Removing enclosed-hole rims preserves this gap in the six-rule cohort, while wavelength-resolved measurements show a relative excess toward low modes with mixed registered outcomes. These observations do not distinguish persistent shape from local interface fluctuations, and do not establish an interface universality class.” Cite KD and cylinder at the first two sentences; cite local experiment results at the remaining empirical sentences.

### Gaps
- No new simulations or numerical analyses were performed in this review. Existing values above are reported from the linked scientific record, not regenerated.
- Citation tracing found the cylinder comparator in one forward-search round. No claim of exhaustive interface literature coverage; original FV access remains open.
