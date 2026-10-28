// Census numbers come from numbers.json; forecasts load their reproducible analysis output.
#let N = json("../../cube-root-growth-paper/numbers.json")
#let KP = json("../../cube-root-growth-paper/kappa_prediction.json")
#let TB = json("../../cube-root-growth-paper/tail_budget.json")
#let CB = json("../../cube-root-growth-paper/chirality_baselines.json")
#let RF = json("../../cube-root-growth-paper/recent_findings.json")
#let TF = json("../../../experiments/archive/2026-10-transport-forecast/results/transport_forecast.json").cohorts
#let f(x, d: 3) = str(calc.round(x, digits: d))
#let pct(x) = str(calc.round(100 * x, digits: 0)) + "%"
#let iqr(v, d: 2) = "[" + f(v.at(0), d: d) + ", " + f(v.at(2), d: d) + "]"


#import "../editorial.typ": editorial
#show: editorial.with(
  title: "Eight times the steps", short: "GROWTH & ITS LIMITS", issue: "01", accent: rgb("#24584d"),
  deck: [A calibrated census of cube-root growth in generalised Langton’s ants],
  abstract: [How fast do generalised Langton’s ants expand before a highway is detected? Across #N.probe.analysed analysed rules, the blob-class median width exponent is #f(N.alpha_w_blob.at(0)). Rotor calibration supports approximate cube-root growth to about $plus.minus 0.01$, rather than the precision suggested by a large census alone. Longer runs and replicated starts establish persistent finite-time rule differences while leaving their asymptotic interpretation open. A late transition to column sweeping demonstrates why a long blob transient cannot establish permanence.],
  takeaway: [A common measured growth regime, a calibrated limit on exponent precision, and explicit counterexamples to treating finite-time classification as an asymptotic theorem.],
  hero: "/research-outputs/cube-root-growth-paper/fig/growth_curves.pdf",
)

= A common growth law, with a finite horizon <sec:introduction>

A territory whose width grows as $t^(1/3)$ needs eight times as many steps to double in size. Generalised Langton’s ants provide a large deterministic family in which to ask how often this slow regime appears, how much rule-to-rule variation survives replication, and when apparent stability fails.

The contribution here is empirical: a multicolour census with a known-answer calibration, explicit exclusions and longer follow-ups. Earlier work on flipping rotators measured growth in different initial media @meng1994 @mishra2016. The present blank-board multicolour census does not establish a new theorem or explain the microscopic origin of the exponent.

Boundary occupation is used below only as a diagnostic: $kappa$ is the window boundary-step fraction divided by the endpoint boundary fraction $P/A$. The companion transport paper defines and tests this decomposition. It is not needed to infer the census exponent.

= Census design and measurements <sec:methods>

== Rule census and finite-horizon classification <sec:rules>

#figure(
  image("../../cube-root-growth-paper/fig/mechanics.pdf", width: 100%),
  caption: [The first steps of two ants. The ant (black triangle) looks at the colour of the cell it stands on, turns left or right as the rule's letter for that colour says, changes the cell to the next colour (cyclically), and steps forward. `RL` has two colours, so a cell flips between blank and green; `RLL` has three (blank, green, orange).],
) <fig:mech>

A rule is a string $r in {L,R}^n$. The ant has a position, a heading and a grid of colours in $ZZ_n$, all initially 0. At each step it reads the colour $c$ under it, turns left or right by `r[c]`, increments the colour to $(c+1) mod n$, and moves one cell. Swapping every L and R gives the mirror-image ant, so we keep only rules starting with R, and drop the trivial rules in which every colour turns the same way.

A sweep of all such rules of length 2–12 (4083 rules) ran each on a blank $8192^2$ grid for up to $10^8$ steps with a highway detector (#link("../../cube-root-growth-paper/supplementary/reproducibility-audit.pdf")[Audit 1]); 578 escaped or were detected as highway builders (including classic `RL`). The census studied here is the remaining #N.census.rules rules of length #N.census.n_min–#N.census.n_max (3505 that ran the full budget plus 7 that escaped late).

Each census rule was then run to $2^27$ steps (#link("../../cube-root-growth-paper/supplementary/reproducibility-audit.pdf")[Audit 2], #link("../../cube-root-growth-paper/supplementary/reproducibility-audit.pdf")[Audit 1]). A rule is called a _builder_ (#N.census.builders rules) if it did not complete $2^27$ steps inside the grid or its steps per bounding-box cell at $10^8$ steps were below 20; builders are excluded.

Most are not highway builders: the recognised highways were already removed above, only 5 of the 304 have a recorded candidate highway period (#link("../../cube-root-growth-paper/supplementary/reproducibility-audit.pdf")[Audit 1]) (none confirmed), 289 stay in the grid and fill it slowly (about 2--6 steps per box cell, frame-like structures) and 10 left the grid (#link("../../cube-root-growth-paper/supplementary/reproducibility-audit.pdf")[Audit 3]). We did not check that the 289 form one class.

The census therefore partitions every rule of length 2--12 into four empirical phases, defined operationally by the $10^8$-step detector, the builder criterion above and the width-exponent cut below.

#figure(
  table(
    columns: 3,
    align: (left, right, right),
    [*Phase*], [*Rules*], [*% of census (#N.census.rules)*],
    [Highway / ballistic (detected, removed before the census)], [578], [n/a],
    [Frame builders], [#N.census.builders], [#pct(N.census.builders / N.census.rules)],
    [Log-growing (localised)], [#N.census.log], [#pct(N.census.log / N.census.rules)],
    [Compact blobs], [#N.census.blob], [#pct(N.census.blob / N.census.rules)],
  ),
  caption: [Complete partition of the sweep. The highway rules were removed by the sweep; the other three phases partition the #N.census.rules census rules.],
) <tab:phases>

That about three quarters of the non-highway rules fall into a single macroscopic phase is itself a result. The question of the paper is how growth varies within that phase, so the headline statistics below are for the whole blob class, not for a subset selected on its exponent.

A rule is _log-growing_ (#N.census.log rules) if the fitted width exponent from $t=2^21$ to $2^27$ is below 0.15, and otherwise _blob_ (#N.census.blob rules). The exponent distribution is bimodal (Hartigan dip #f(N.alpha_gap.dip, d: 3) on #N.alpha_gap.dip_n non-builder rules, $p < 0.001$; a two-component Gaussian mixture has means #f(N.alpha_gap.gmm_means.at(0), d: 2) and #f(N.alpha_gap.gmm_means.at(1), d: 2) with weights #pct(N.alpha_gap.gmm_weights.at(0)) and #pct(N.alpha_gap.gmm_weights.at(1)); @fig:alphagap). The dip test only rejects unimodality. The cut at 0.15 was set by eye and is _not_ in an empty gap: the log-growers' density tails off across 0.10--0.17 (#N.alpha_gap.n_per_bin_015 rules within 0.005 of the cut) and the trough is at 0.17--0.26, where bins hold at most four rules. The cut was fixed before the sensitivity analysis, which was registered afterwards (experiment `2026-10-alpha-gap`), and it matters little: the blob median width exponent is #f(N.alpha_gap.cuts.at("0.1"), d: 4), #f(N.alpha_gap.cuts.at("0.15"), d: 4), #f(N.alpha_gap.cuts.at("0.2"), d: 4) and #f(N.alpha_gap.cuts.at("0.25"), d: 4) for cuts at 0.10, 0.15, 0.20 and 0.25 (spread #f(N.alpha_gap.at("spread_0.15_0.25"), d: 4) for cuts from 0.15 to 0.25; #f(N.alpha_gap.at("spread_0.10_0.25"), d: 4) when 0.10 is included, which exceeds the 0.001 we predicted in advance; a cut at 0.05 gives #f(N.alpha_gap.cuts.at("0.05"), d: 4)).

#figure(
  image("../../cube-root-growth-paper/fig/alpha_gap.pdf", width: 90%),
  caption: [Census width exponent for the non-builder rules; the line marks the log/blob cut at 0.15. There is a density trough, but at 0.17--0.26 rather than at the cut.],
) <fig:alphagap>

#figure(
  image("../../cube-root-growth-paper/fig/census.pdf", width: 80%),
  caption: [Outcome of every rule in the sweep (4083 rules of length 2–12; the single length-2 rule is `RL` and is not shown), by rule length. Highway builders are a third to two fifths of the length-3 and length-4 rules and about one in seven from length 6 on. "Frame" builders (mostly rules that fill a frame slowly, a few that leave the grid) are a small slice. The two top classes, blob and log-growing, are the subject of this paper.],
) <fig:census>

== Growth observables, fitting windows and exclusions <sec:runs>

The probe (`src/probe.rs`) tracks the _visited_ set (every cell the ant has ever stood on), its area $A$, its _boundary_ $P$ (visited cells with at least one unvisited 4-neighbour), and, in octave windows $[2^k, 2^(k+1))$, the number of steps that start on a boundary cell and the number of steps that enter a never-visited cell. It also gives the bounding box, the radius of gyration $R_g$ of the visited set, and the ant's own spread. For each rule we fit log–log slopes over windows $k = 20 ... 26$:

- width exponent $alpha$ (bounding-box side against $t$) and $R_g$ exponent $alpha_g$;
- area exponent $a$ ($A tilde t^a$; $a$ is always the area exponent and $alpha$ always the width exponent, with $a approx 2 alpha$);
- boundary exponent $beta$ ($P tilde A^beta$).

#N.probe.analysed rules were analysed; #N.probe.unanalysed of the #(N.census.blob + N.census.log) growing rules had no usable window set (a window contained no new cells) and were not fitted. All analysed rules are kept in the statistics below. #N.probe.bursty of them have a single-window area jump `max_jump` $>=$ #f(N.bursty_rule.flagged_min_jump, d: 2) (no unflagged rule exceeds #f(N.bursty_rule.unflagged_max_jump, d: 2)); they are flagged in the data but not removed, and are all blob-class rules with a median width exponent of 0.42. Dropping them instead would move the blob median from #f(N.alpha_w_blob.at(0), d: 4) by less than 0.0001.

The unfitted rules are #pct(N.probe.unanalysed / (N.census.blob + N.census.log)) of growing rules, and they are not fast growers: rerun on a $32768^2$ grid, none left the grid, all reached $2^26$ steps, and their median area there is 1936 against 316162 for the fitted blob rules, so they are stalled or tethered (#link("../../cube-root-growth-paper/supplementary/reproducibility-audit.pdf")[Audit 3]). If fast growers are missing from the census it is for another reason; the only candidates are the 10 grid-escapers among the builders (0.3% of the census).

The census contains #N.repeats.n rules that are exact repeats of a shorter rule ($u^k$, which behave identically to $u$); we keep them, since removing them moves the blob median width exponent only from #f(N.repeats.blob_median_alpha_w_all, d: 4) to #f(N.repeats.blob_median_alpha_w_primitive, d: 4).

= Calibrating finite-window bias on the rotor walker <sec:calibration>

An exponent fitted over seven octaves from $2^20$ to $2^26$ is not the asymptotic exponent. We therefore ran the identical pipeline on #N.calib_A.rotor.alpha_w.n rotor-walker seeds (random initial arrows, $2^27$ steps), whose width exponent is $1/3$ and area exponent $2/3$ @bourabee2026, and on 16 random walks as a negative control.

#figure(
  table(
    columns: (auto, auto, auto, auto, auto),
    align: (left, right, right, right, right),
    stroke: (x: none), inset: 4pt,
    [], [width exp. $alpha$], [$R_g$ exp. $alpha_g$], [area exp. $a$], [edge exp. $beta$],
    [truth (rotor)], [1/3], [1/3], [2/3], [--],
    [rotor, median], [#f(N.calib_A.rotor.alpha_w.median)], [#f(N.calib_A.rotor.alpha_rg.median)], [#f(N.calib_A.rotor.a.median)], [#f(N.calib_A.rotor.beta.median)],
    [rotor, between-seed sd], [#f(N.calib_A.rotor.alpha_w.sd)], [#f(N.calib_A.rotor.alpha_rg.sd)], [#f(N.calib_A.rotor.a.sd)], [#f(N.calib_A.rotor.beta.sd)],
    [ants (core), median], [#f(N.calib_A.ants_core.alpha_w.median)], [#f(N.calib_A.ants_core.alpha_rg.median)], [#f(N.calib_A.ants_core.a.median)], [#f(N.calib_A.ants_core.beta.median)],
    [ants (core), between-rule sd], [#f(N.calib_A.ants_core.alpha_w.sd)], [#f(N.calib_A.ants_core.alpha_rg.sd)], [#f(N.calib_A.ants_core.a.sd)], [#f(N.calib_A.ants_core.beta.sd)],
    [random walk, median], [#f(N.calib_A.random_walk.alpha_w.median)], [#f(N.calib_A.random_walk.alpha_rg.median)], [#f(N.calib_A.random_walk.a.median)], [#f(N.calib_A.random_walk.beta.median)],
  ),
  caption: [Same pipeline on three systems. The rotor has known exponents; the random walk is a negative control (area exponent near 1, boundary exponent near 1). The "ants (core)" rows are selected on $0.30 < alpha < 0.37$, which truncates their sd: it understates the between-rule spread and flatters the comparison with the rotor's sd. @fig:exp, over all blob rules, is the fair comparison.],
) <tab:calib>

Findings.

- (i) The pipeline recovers the rotor: the radius-of-gyration exponent is #f(N.calib_A.rotor.alpha_rg.median) (sd #f(N.calib_A.rotor.alpha_rg.sd)) against the true 0.333, the width exponent is slightly low (#f(N.calib_A.rotor.alpha_w.median)) and noisier, and the area exponent overshoots by #f(N.calib_A.rotor.a.median - 2/3, d: 2). We therefore treat the finite-window bias of $a$ as $+0.02$ and prefer the $R_g$ estimator, which is the least noisy.
- (ii) The random walk is clearly separated (area exponent #f(N.calib_A.random_walk.a.median, d: 2)).
- (iii) The ants' $R_g$ exponent #f(N.calib_A.ants_core.alpha_rg.median) and area exponent #f(N.calib_A.ants_core.a.median, d: 2) sit within the rotor's bias and sd.
- (iv) The boundary exponent of both is about #f(N.calib_A.rotor.beta.median, d: 3) (rotor) and #f(N.calib_A.ants_core.beta.median, d: 3) (ants), not 1/2; it is a finite-window effect shared with the rotor and not evidence of a rough edge.

To check the pipeline further we reproduced the published rotor measurements of Kapri and Dhar @kapri2009 from #N.calib_B.seeds_long seeds (radius exponent local slopes #N.calib_B.nu_local.map(x => str(x)).join(", "), tending to $1/3$; boundary-width exponent local slopes falling from #N.calib_B.delta_local.first() to #N.calib_B.delta_local.last(), against their reported value $alpha slash 3 approx 0.13$).

A reservation: for the rotor, the true limit exponent is known, but only by proof for the radius; our statements about its $beta$ and $c$ are measurements, not theorems.

= Census evidence for cube-root growth <sec:census-results>

#figure(
  image("../../cube-root-growth-paper/fig/growth_curves.pdf", width: 100%),
  caption: [How the territory grows with the number of steps $t$ (log scales, so a power law is a straight line). Three ant rules (blue and purple) and the rotor walker (red) climb parallel to the dashed guide lines, slope $1/3$ for the width and $2/3$ for the visited area; doubling the width takes about eight times as many steps. The log-growing rule `RRLRLR`#sym.dots.h`LLL` (teal) falls away, and the random walk (grey), the negative control, grows much faster, with width $tilde t^(1/2)$.],
) <fig:growth>

#figure(
  image("../../cube-root-growth-paper/fig/timelapse.pdf", width: 100%),
  caption: [One rule (`RLL`) at four times, each panel rescaled to the same size. Eight times as many steps buys a territory only twice as wide ($8^(1/3) = 2$), and the shape stays the same round blob: it looks self-similar, and the roundness statistics of the companion ant–rotor study (anisotropy 0.05--0.07) agree, but we did not test scaling beyond that.],
) <fig:timelapse>

#figure(
  image("../../cube-root-growth-paper/fig/exponents.pdf", width: 100%),
  caption: [Fitted exponents of #N.probe.blob blob-class ant rules and #N.calib_A.rotor.alpha_w.n rotor seeds. Dashed line: $1/3$. The ants' distribution is wider than the rotor's: sd ratio #f(N.calib_A.sd_ratio_alpha_w, d: 1) (width), #f(N.calib_A.sd_ratio_alpha_rg, d: 1) ($R_g$).],
) <fig:exp>

== Growth exponents and calibration uncertainty

Over the #N.probe.blob blob rules the median width exponent is #f(N.alpha_w_blob.at(0)) (rule bootstrap 95% interval #f(N.alpha_w_blob.at(1)) to #f(N.alpha_w_blob.at(2))), the $R_g$ exponent #f(N.alpha_rg_core.at(0)), and the area exponent #f(N.a_core.at(0)) in the core.

The interquartile range of the width exponent is #iqr(N.iqr_alpha_w_blob). The bootstrap resamples _rules_; it does not include the finite-window bias, which @tab:calib puts at about $+0.02$ for $a$ and negative for $alpha$.

Against the rotor in the same window the differences (ants minus rotor, medians over all blob rules) are #f(N.bias.alpha_w.ant_minus_rotor, d: 3) for the width exponent, #f(N.bias.alpha_rg.ant_minus_rotor, d: 3) for the $R_g$ exponent and #f(N.bias.a.ant_minus_rotor, d: 3) for the area exponent.

Subtracting the rotor's own bias from the ants' medians gives #f(N.bias.alpha_w.ant_corrected, d: 3) (width), #f(N.bias.alpha_rg.ant_corrected, d: 3) ($R_g$) and #f(N.bias.a.ant_corrected, d: 3) (area), against $1/3$, $1/3$ and $2/3$. The corrections point in different directions, so the data are consistent with $1/3$ at roughly the $plus.minus 0.01$ level, not "equal to $1/3$ to three digits"; the correction assumes the ants share the rotor's finite-window bias, which we cannot check.

== Variation with rule length and longer run times

The median is flat in $n$: Spearman $rho$ between $alpha$ and $n$ is #f(N.spearman_alpha_n) over blob rules, and per-length medians for $n = 7 ... 12$ lie within about 0.01 of one another (table in #link("../../cube-root-growth-paper/supplementary/reproducibility-audit.pdf")[Audit 6], `by_n`). The spread between rules does not shrink with $n$ in our sample, so we do not claim a rule-length trend or its absence at larger $n$.

*Long runs.* Six typical rules were run to $2^32$ steps; their width exponents fitted from $2^17$ are between #f(N.cube.long_alpha.at(0)) and #f(N.cube.long_alpha.at(1)), and neither factor in the decomposition drifts (#link("../../cube-root-growth-paper/main.pdf")[the synthesis transport-factor figure]).

== Seed variability and reproducible rule differences <par:noise>

The between-rule scatter is mostly run-to-run: re-running #N.calib_C.rules rules from #N.calib_C.runs random $5 times 5$ starting patches gives within-rule sd #f(N.calib_C.alpha_w.sd_within) for $alpha$ and a between-rule true sd of only #f(N.calib_C.alpha_w.sd_between_true) (intraclass correlation #f(N.calib_C.alpha_w.icc, d: 2)).

Genuine rule-to-rule differences in $alpha$ are small; for $R_g$ and $a$ they are detectable (ICC #f(N.calib_C.alpha_rg.icc, d: 2), #f(N.calib_C.a.icc, d: 2)). We cannot say whether they reflect different exponents or different rates of convergence.

Where the rule-specific part of $a$ sits can be partly located (#link("../../cube-root-growth-paper/supplementary/reproducibility-audit.pdf")[Audit 7], #link("../../cube-root-growth-paper/supplementary/reproducibility-audit.pdf")[Audit 8]; the 99 random rules of the ICC above, window $k = 20$–$26$). The area is the product of the two box sides and a filling fraction, so $a = alpha_x + alpha_y + gamma_eta$ exactly, with $gamma_eta$ the log-slope of $A slash (W_x W_y)$. The rule-to-rule variance of $a$ is carried #pct(N.h1.share_ax) by $alpha_x$, #pct(N.h1.share_ay) by $alpha_y$ and #pct(N.h1.share_geta) by $gamma_eta$ (covariances of rule means, which include run noise); the two sides rise or fall together (correlation #f(N.h1.corr_axay, d: 1)), while $gamma_eta$ has ICC #f(N.h1.icc_geta, d: 2), like the sides taken singly (#f(N.h1.icc_ay, d: 2) and #f(N.h1.icc_ax, d: 2); $a$ itself #f(N.h1.icc_a, d: 2)). The territories consolidate slowly ($gamma_eta = +$#f(N.h1.mean_geta, d: 3), positive for #pct(N.h1.frac_geta_pos) of rules), but rules do not differ in $a$ mainly because they consolidate at different rates. We have not explained why the sides co-vary by rule.

= Persistence and exceptions

== Longer ensembles do not resolve a universal exponent <par:universality>

Eleven rules (stratified by length 3–12) were run from #(N.item4.runs_kept) random $5 times 5$ starting patches, 24 seeds each, to $2^30$ steps. The local area exponent, averaged over seeds and over the last six three-octave windows, has mean #f(N.item4.ant_last6_mean, d: 3) across rules (sd #f(N.item4.ant_last6_sd, d: 3), range #f(N.item4.ant_range.at(0), d: 3) to #f(N.item4.ant_range.at(1), d: 3)).

The same estimator applied to 24 rotor seeds, whose exponent is proved to be $2/3$, gives #f(N.item4.rotor_last6, d: 3): even the rotor sits $0.01$ above $2/3$ at $2^30$ by this estimator. #N.item4.within_0006_of_rotor of the #N.item4.rules rules are within 0.006 of the rotor; the others are up to 0.02 above it or 0.017 below it by amounts many standard errors wide.

One rule (`RRLLLLLLR`) does not self-average: its seed-to-seed spread rises with time. So the data are compatible with a common exponent $2/3$ with slow, rule-dependent convergence, but they cannot distinguish that from rule-dependent exponents within about 0.02.

== Replicated starts preserve extreme growth exponents

We re-ran the #N.item21.high_n fastest and #N.item21.low_n slowest blob rules from 12 random patches each. If their exponents had been run-to-run noise they would regress to the middle. They mostly do not: only #pct(N.item21.high_regress) of the fast rules fall below 0.37 and #pct(N.item21.low_regress) of the slow rules rise above 0.30; the Spearman correlation between census and re-measured exponent is #f(N.item21.spearman_census, d: 2), and the re-measured exponent correlates with $gamma_kappa$ at #f(N.item21.spearman_gk, d: 2). So the outliers are real properties of the rules over $2^20$–$2^27$ steps, with edge occupation drifting; whether they are different asymptotes or very slow transients is untestable at this length (the #link(<par:universality>)[exponent comparison] shows even typical rules differ by about 0.02 at $2^30$).

The replication bounds the noise interpretation to typical rules, narrowing our earlier statement about between-rule scatter: there it is (within-rule sd 0.016 against a between-rule sd of 0.004), but the tails are not.

== A blob becomes a column sweeper after billions of steps <sec:late-switch>

*A long blob-like transient can end in a different growth regime.* In one blank-board trajectory, `RLRLLL` ran as a blob until step $#f(N.g1.onset_t / 1e10, d: 4) times 10^10$ and then switched within a few $10^6$-step windows to a steady builder at #f(N.g1.steady_steps_per_new, d: 2) steps per newly visited cell (all #N.g1.steady_windows later windows), and left a $32768^2$ board at $#f(N.g1.exit_step / 1e10, d: 4) times 10^10$ (#link("../../cube-root-growth-paper/supplementary/reproducibility-audit.pdf")[Audit 38], #link("../../cube-root-growth-paper/supplementary/reproducibility-audit.pdf")[Audit 39]; one blank-board trajectory, trigger unknown).

*The new regime sweeps columns back and forth.* Two $4 times 10^5$-step trajectory dumps at $1.28 times 10^10$ and $1.29 times 10^10$ (#link("../../cube-root-growth-paper/supplementary/reproducibility-audit.pdf")[Audit 40], #link("../../cube-root-growth-paper/supplementary/reproducibility-audit.pdf")[Audit 39]; #link("../../cube-root-growth-paper/supplementary/reproducibility-audit.pdf")[Audit 41]) show that this builder is a boustrophedon column sweeper rather than a perimeter crawl: it makes a slow traverse of the full height $L$ (6,400 rows at the first dump and 8,610 at the second) at about 10 steps per row, a fast return at about 2 steps per row, and adds three columns per round trip, and the wake is strongly periodic in $x$ with period 3 (column agreement 0.99, dominated by colours 3, 4, 5).

Three columns of $L$ cells per $approx 12 L$ steps is 4 steps per new cell, and $d x slash d t = -1 slash (4 L)$ with the measured $L approx 0.67 |x| - 960$ predicts $d|x|^2 slash d t = 0.86$ and 0.84 at the two dumps against 0.86 and 0.83 measured, so $|x|$ grows as $t^(1 slash 2)$ in this phase.

The two values of $L$ come from the same single trajectory, so this is a consistency check on the sweep picture, not a test of the $L tilde |x|$ law; why the pattern has period 3 and what triggers the switch are unexplained. Three further board escapes without a recognised highway in the $10^11$ sample may be of this kind but were not traced.

#figure(
  image("../../cube-root-growth-paper/fig/late_switch.pdf", width: 100%),
  caption: [*A late switch to a period-3 column sweeper (`RLRLLL`).* (a) Steps per newly visited cell fall abruptly near $t=1.2677 times 10^10$ to about 4. Each dot is one window: $10^8$ steps through $1.2 times 10^10$, then $10^6$ steps (the final window is partial); upper ticks mark windows with no discoveries. (b) An actual $36 times 48$-cell crop of the wake at $t=1.28004 times 10^10$, with square cells and unvisited ground white. Lag-3 column agreement over the full extracted wake is 0.994. The adjacent trajectory covers $4 times 10^5$ steps starting at $1.28 times 10^10$, sampled every 100 steps, and shows slow traverses and fast returns. (c) The sweep model predicts $d |x|^2 slash d t = |x| slash (2 L)$: 0.86 and 0.84 against 0.86 and 0.83 measured. Measurement uses the local slope of $|x|$ in strict $plus.minus 2 times 10^7$-step windows (39 samples each), multiplied by $2|x|$ at the dump time. These are two checks on one deterministic blank-board trajectory; no between-seed uncertainty is available, and this post-hoc agreement does not explain the switch.],
) <fig:late-switch>

= What survives the calibration

The evidence supports a widespread finite-time cube-root regime in measured blob rules. The census size makes the median stable but cannot remove estimator bias, correlated rule structure or slow convergence. Replicated starts preserve extreme rules, and the late column-sweeper transition makes the finite-horizon qualification essential.

A universal asymptotic exponent remains undecided. The next decisive evidence would be registered longer follow-ups that separate rule-dependent corrections from persistent exponent differences, with the same known-answer calibration and explicit treatment of stalled and escaped runs. Boundary-transport mechanisms and ant–rotor surface comparisons are developed in the companion drafts.

= Evidence, provenance and draft status

This is an editorial split of existing research, not a new measurement. Exact commands, seed schedules, windows, exclusions and registration limits remain in the #link("../../cube-root-growth-paper/supplementary/reproducibility-audit.pdf")[shared reproducibility audit]. The companion manuscripts reuse evidence and should not be treated as independent replication. Source snapshot and numerical-input hashes are recorded beside this draft in `provenance.json`.

*Availability.* Repository archive URL and DOI remain to be supplied before submission. The simulator, committed result summaries, supplementary rule census and walker-reference table live in the accompanying repository.

*Authorship and assistance.* T.S. McNamara directs the research. Existing code, analyses and prose were developed with AI assistance as described in the synthesis; Codex assisted this editorial split and typesetting. Author review, funding and competing-interest statements must be finalized before submission.

#pagebreak(weak: true)
#bibliography("../../cube-root-growth-paper/refs.bib", style: "ieee")

