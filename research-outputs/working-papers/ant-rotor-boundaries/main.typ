// Census numbers come from numbers.json; forecasts load their reproducible analysis output.
#let N = json("../../scholarly-articles/cube-root-growth/numbers.json")
#let KP = json("../../scholarly-articles/cube-root-growth/kappa_prediction.json")
#let TB = json("../../scholarly-articles/cube-root-growth/tail_budget.json")
#let CB = json("../../scholarly-articles/cube-root-growth/chirality_baselines.json")
#let RF = json("../../scholarly-articles/cube-root-growth/recent_findings.json")
#let TF = json("../../../experiments/archive/2026-10-transport-forecast/results/transport_forecast.json").cohorts
#let f(x, d: 3) = str(calc.round(x, digits: d))
#let pct(x) = str(calc.round(100 * x, digits: 0)) + "%"
#let iqr(v, d: 2) = "[" + f(v.at(0), d: d) + ", " + f(v.at(2), d: d) + "]"


#import "../editorial.typ": editorial
#show: editorial.with(
  title: "A shared bulk, a different edge", short: "ANTS & ROTORS", issue: "03", accent: rgb("#4c5587"),
  deck: [Visit profiles and surface growth in deterministic expanding territories],
  abstract: [Can two walkers share a bulk growth regime while organizing their boundaries differently? Selected ant and rotor ensembles have closely agreeing accumulated radial visit profiles, yet their measured surface-width growth differs. The difference persists in radius-based fits and after separating the outer coastline from interior holes. A conditional cone-profile calculation explains why bulk agreement alone is weak evidence for a common mechanism; controls outside the cube-root regime expose limits of its assumptions. These are finite-window comparisons in selected cohorts, not evidence for an interface universality class.],
  takeaway: [A measured bulk-profile agreement together with a persistent finite-window boundary-growth gap. Existing checks exclude several simple measurement explanations while leaving the dynamical origin unresolved.],
  hero: "/research-outputs/scholarly-articles/cube-root-growth/fig/hero.pdf",
)

= When the interior agrees and the boundary does not <sec:introduction>

An accumulated occupation field records where a walker has spent its past. Surface width records the shape of the frontier it leaves behind. Agreement in the first observable need not imply agreement in the second. Generalised Langton’s ants and the rotor walker make this distinction concrete.

The rotor provides a known growth benchmark @bourabee2026 and an established profile and width comparison @kapri2009. The present contribution is narrower than a shared-universality claim: selected ensembles agree in their bulk profiles but differ at their boundaries over the observed windows. This developing study keeps the distinction between measured trajectory slopes, spatial correlations and asymptotic exponents explicit.

= Walkers, observables and comparison scope <sec:methods>

An ant reads colour $c$, turns by letter `rule[c]`, increments the colour modulo rule length and steps forward on the square lattice. Classic Langton’s ant is `RL`. Blank-board ant trajectories are deterministic; patched-start controls and random initial rotor arrows use the seeds recorded in the shared audit. The fast ant is tested against the reference simulator.

Area $A$ counts all visited cells. The boundary $P$ counts visited cells with at least one never-visited four-neighbour, including hole rims. Equivalent radius is $R_("eq")=sqrt(A/pi)$; surface width is the standard deviation of boundary-site radius about the visited-set centroid. Boundary occupation $kappa$ is the fraction of window steps starting on boundary cells divided by the endpoint fraction $P/A$. Its normalization depends on growth within the window, so levels cannot be interpreted as fixed-domain occupation ratios.

The following analyses use different recorded cohorts and horizons. Counts, fitting windows and exclusions accompany each comparison; they must not be pooled as independent confirmations of a single universal exponent. The census companion provides the larger rule population, while this paper concentrates on the measured profile and width cohorts.

= Bulk profiles

== Ant and rotor visits accumulate in the same cone

The time-averaged visit density, as a function of distance from the centroid in units of the territory radius $R_("eq") = sqrt(A slash pi)$ and of $t slash A$, is a cone, $n(r) = 3 (1 - r slash R_("eq")) t slash A$, for ants and rotor alike. Over the first ten of fifteen radial shells the ants' profile (#N.shape.ants.runs runs of 11 rules, $2^#N.shape.ants.kmax$ steps) and the rotor's (#N.shape.rotor.runs seeds, $2^#N.shape.rotor.kmax$ steps) differ by at most #pct(N.shape.max_rel_diff_ants_rotor_shells0_9), and the ant profile differs from the cone by at most #pct(N.shape.max_rel_diff_ants_cone_shells0_9)\; the across-rule relative sd at mid-radius is #pct(N.shape.ants.profile_rel_sd_shell6). This agreement bounds the bulk-profile differences despite the distinct microscopic updates, contrary to the registered prediction of differing profiles. It is not independent evidence for the cube root, because the cone is conditionally implied by the exponent together with approximately uniform instantaneous occupancy and compact circular growth with coherent discovery radii.

Suppose the walker is spread uniformly over the current territory, $n(r, t') = 1 slash A(t')$ for $r < R(t')$, and $A(t) prop t^a$. A cell at radius $r$ is inside from the time $t_r$ at which $R(t_r) = r$, so its accumulated visits are $rho(r) = integral_(t_r)^t d t' slash A(t') = (t slash ((1-a) A)) (1 - (r slash R)^(2(1-a) slash a))$. For $a = 2/3$ this is exactly $(3 t slash A)(1 - r slash R)$, and it integrates to $t$ over the disc. The cone is therefore the footprint of a uniformly mixing walker inside a disc growing as $t^(2/3)$; nothing specific to rotors or ants enters beyond these occupancy, geometry and discovery-time assumptions (#link("../../scholarly-articles/cube-root-growth/supplementary/reproducibility-audit.pdf")[Audit 19], A3). It also explains why ants and rotor agree although their $kappa$ differ (about 0.9 against 2.0): $kappa$ changes only a thin edge layer, not the bulk integral. The profile checks consistency with these joint assumptions; accumulated visits alone do not establish instantaneous uniform occupancy. Kapri and Dhar instead motivate the rotor cone by approximately equal subsequent local-time increments @kapri2009, so matching the cone does not distinguish the mechanisms.

With the measured rotor exponent $a = 0.687$ the formula gives a centre prefactor $1 slash (1-a) = 3.19$ rather than 3, against a measured 2.87 (#link("../../scholarly-articles/cube-root-growth/supplementary/reproducibility-audit.pdf")[Audit 29]) that the 0.075 $R_("eq")$ shell width lowers by roughly 3--4%, so the data do not separate $a = 2/3$ from 0.687 at better than about 5%.

*Controls limit the profile derivation.* The formula's predictions for other exponents were tested on walkers with $a != 2/3$ (#link("../../scholarly-articles/cube-root-growth/supplementary/reproducibility-audit.pdf")[Audit 19], W2, W3 and the checks after them; #link("../../scholarly-articles/cube-root-growth/supplementary/reproducibility-audit.pdf")[Audit 32], #link("../../scholarly-articles/cube-root-growth/supplementary/reproducibility-audit.pdf")[Audit 33]), with results that do not support the derivation beyond $a = 2/3$.

Rotors whose arrow is randomised with probability $epsilon = 0.001$ ($a = 0.75$–$0.78$, four seeds, territories round enough for a radial profile: anisotropy $<= 0.31$, fill 0.96) have a centre density of 1.9–2.1 against 3.5–3.8 from the formula, so the formula fails and the cone, at 3, is also off. For $epsilon >= 0.003$ and for a memoryless persistent walker the territories are elongated or holey (anisotropy up to 0.9, fill down to 0.3), so the premise fails first and the profile cannot test the formula.

Two chaotic 2-state turmites with a stable $a approx 0.74$ over six octaves (`tm:2:2:46382`, `7982`; single trajectories) keep a cone-like centre (2.8 and 3.1) below the formula's 3.5 and 3.2.

So the cone is not simply a consequence of "uniform occupancy and an exponent", and we cannot say that uniform occupancy needs $a = 2/3$; every walker we tried has $a >= 2/3$, and the exponents are finite-window values.

We had also meant to test the formula on the $a approx 1/2$ turmite cluster, but those tables grow as one-dimensional lines (anisotropy 1.00), and eight of the ten sampled are the same trajectory, so the cluster does not bear on the question.

The territories are round (median anisotropy #f(N.shape.ants.aniso, d: 3) at $2^28$, the rotor's #f(N.shape.rotor.aniso, d: 3) at $2^26$; fill #f(N.shape.ants.fill, d: 2)).

== Surface width grows faster in the examined ant cohorts

The surface width does _not_ match: its local exponent fitted over $k >= 18$ is #f(N.shape.ants.dW, d: 2) for ants and #f(N.shape.rotor.dW, d: 2) for the rotor (Kapri and Dhar: about 0.13), so these fits show a finite-window temporal-exponent gap, without matching physical radii. These single fits use a different window ($k >= 18$) from the matched-$k$ follow-up below, which is why the absolute values differ; the comparison that matters is the ratio.

A longer follow-up (#link("../../scholarly-articles/cube-root-growth/supplementary/reproducibility-audit.pdf")[Audit 34]; 36 ant runs and 14 rotor seeds to $2^34$) finds both exponents flat rather than falling, about 0.22–0.25 for ants and 0.10–0.13 for the rotor at every matched $k$ from 22 to 32, so the gap of roughly a factor two does not close in the accessible range; whether it closes asymptotically is undecided.

The gap is not an artefact of the extreme-$kappa$ rules with a "crust" (an almost unvisited shell between the active edge and the bulk, found in 15 of 24 rules examined; see the companion boundary-transport study): to $2^30$ the 9 ordinary-$kappa$ rules without a crust have local exponents 0.21–0.35 (median 0.27), all above 0.18, against 0.17–0.45 (mean 0.32) for the 15 crust rules (difference +0.04, Mann–Whitney $p = 0.054$; Spearman with $log kappa$ +0.40, $p = 0.056$; one trajectory per rule, W1). The wider edge occurs in both examined ant cohorts, with at most a mild additional effect in this high-$kappa$ sample; census-wide generality is not established.

#figure(
  image("../../scholarly-articles/cube-root-growth/fig/rotor.pdf", width: 100%),
  caption: [Left and middle: how often each cell was visited (log scale) in a single run of $2^22$ steps, for the rotor walker (one seed) and the ant `RLL`. Right: visits per cell, averaged in rings around the centre, against the cone $3(1 - r slash R)$. Both curves follow the cone; this figure is one run each and is an illustration, not the ensemble measurement quoted in the text.],
) <fig:rotor>

== The width gap survives radius and outer-hull checks

Refitting the same A4/A4c trajectories directly against $R=sqrt(A slash pi)$ gives $W_("surf") prop R^zeta$ with rotor $zeta=0.401$ (14 seeds, sd 0.073; bootstrap mean interval 0.366–0.437) and ant $zeta=0.714$ (36 runs across six rules, RMS within-rule seed sd 0.134; rule-bootstrap interval 0.664–0.761), over $k=22$–$32$. The rotor estimate lies above the registered $zeta in [0.30,0.37]$ band and is closer to $3/8$, implied by $W prop t^(1/8)$ and $R prop t^(1/3)$, than to $1/3$. Restricting to $k=26$–$32$ gives 0.389 and 0.685; the later A4c cohort alone over $k=26$–$34$ gives 0.395 and 0.637. The ant/rotor slope ratio therefore changes from 1.78 to 1.61.

Replacing $R$ with $R_g$ or the mean outer radius changes these means by less than 0.005. This confirms a finite-window gap but does not support an exact factor-two law.

#figure(
  image("../../scholarly-articles/cube-root-growth/fig/edge_gap.pdf", width: 100%),
  caption: [Surface width of ants and the rotor walker out to $t = 2^34$ (pooled A4 and A4c runs: 36 ant runs across six rules, 14 rotor seeds; checkpoints at $t = 2^k$). (a) $W_("surf")$ against $t$; line is the mean of $ln W$ over runs, band the 16–84% range over runs. (b) Local exponent between $k$ and $k+2$, mean $plus.minus$ standard error over runs (dashed: the Kapri–Dhar value of about 0.13, see text). The ants' exponent stays near 0.20–0.27 while the rotor's falls towards 0.10–0.13; the mean widths cross near $t approx 2^26$, below which the rotor is wider, so the figure shows a difference of exponent over this window, not of prefactor. Ant runs mix six rules, so the band is between-run, not between-seed.],
) <fig:edge-gap>

The surface cells here, as in the edge $P$ of the boundary definition in this paper, are all visited cells with a never-visited 4-neighbour, so they include the rims of interior holes and detached unvisited pockets, not only the outer hull; $W_("surf")$ is the standard deviation of their radius about the centroid (the same surface-site criterion as Kapri and Dhar, but they use origin-centred radii and the square root of an ensemble mean of per-cluster variances; we summarize per-run fitted slopes). Their v2 body gives $0.136 plus.minus 0.02$, while Fig. 8 gives $plus.minus 0.002$; we therefore quote only about 0.13 @kapri2009.

*Interior holes do not explain the gap.* A follow-up separates hole rims from the outer coastline (24 ant runs of the six rules above and 8 rotor seeds, to $2^30$; #link("../../scholarly-articles/cube-root-growth/supplementary/reproducibility-audit.pdf")[Audit 35], predictions registered before the run). Porosity does not explain the gap: the local exponent over $k >= 22$ is 0.239 for the ants' outer-hull width and 0.239 for all surface cells, against 0.135 and 0.130 for the rotor, and hole rims are 4% of the ants' surface cells but 25% of the rotor's.

The ants have a lower finite-resolution box-count slope (1.07 against 1.16) and steeper measured spectral decay than the rotor; these are not established asymptotic fractal dimensions.

The wavelength follow-up finds relatively greater low-mode excess, but its registered band decision is mixed and the high-band result is outside the predicted range. The temporal fall in normalized power includes $(W/R)^2$ and supplies no independent corroboration. Persistence of large-scale shape versus local fluctuating width remains unresolved (#link("../../scholarly-articles/cube-root-growth/supplementary/reproducibility-audit.pdf")[Audit 35]).

These are growth-trajectory slopes, not spatial roughness exponents; physical-distance height correlations, local widths, spectral scaling and phase persistence beyond the already removed modes 0–2 are needed, together with a justified growth clock, to test a KPZ or other interface universality class @kpz1986 @ramasco2000 (#link("../../scholarly-articles/cube-root-growth/supplementary/reproducibility-audit.pdf")[Audit 33]).

= A boundary difference, not yet a universality class

Bulk-profile agreement and a finite-window surface-growth gap coexist in the measured ant and rotor cohorts. Radius refits and outer-hull checks preserve the difference, but the slope ratio varies with fitting range. Neither an exact factor-two law nor census-wide boundary behaviour is established.

Accumulated profiles test joint assumptions about occupation, shape and discovery history; they cannot identify instantaneous mixing on their own. The decisive next work is physical-distance height correlations, local-width and spectral scaling, and separation of persistent large-scale shape from fluctuating boundary width. Those tests must precede any interface-class assignment. This draft is a focused account of an observed contrast and its remaining ambiguities.

= Evidence, provenance and draft status

This is an editorial split of existing research, not a new measurement. Exact commands, seed schedules, windows, exclusions and registration limits remain in the #link("../../scholarly-articles/cube-root-growth/supplementary/reproducibility-audit.pdf")[shared reproducibility audit]. The companion manuscripts reuse evidence and should not be treated as independent replication. Source snapshot and numerical-input hashes are recorded beside this draft in `provenance.json`.

*Availability.* Repository archive URL and DOI remain to be supplied before submission. The simulator, committed result summaries, #link("../../data-papers/rule-census/README.md")[supplementary rule census] and #link("../../data-papers/walker-reference/README.md")[walker-reference table] live in the accompanying repository.

*Authorship and assistance.* T.S. McNamara directs the research. Existing code, analyses and prose were developed with AI assistance as described in the synthesis; Codex assisted this editorial split and typesetting. Author review, funding and competing-interest statements must be finalized before submission.

#pagebreak(weak: true)
#bibliography("../../scholarly-articles/cube-root-growth/refs.bib", style: "ieee")

