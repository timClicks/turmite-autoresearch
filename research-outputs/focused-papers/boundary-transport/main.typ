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
  title: "The cost of the edge", short: "BOUNDARY TRANSPORT", issue: "02", accent: rgb("#a14d2b"),
  deck: [Rule dependence, prediction and unresolved transport in generalised Langton’s ants],
  abstract: [Growth requires reaching a boundary and entering fresh ground. We separate those events through an exact accounting identity, then ask which parts admit independent prediction. An opening-run law predicts edge-entry cost on fresh stationary rules, with weaker broader validation. Prefix models predict occupation within a restricted cohort, while a conditioning control reproduces an apparent opening-run association without a direct occupation effect. A growth-adjusted uniform reference sharpens the measured occupation deficit. Forecasts and failed mechanism tests constrain explanations without deriving a transport closure.],
  takeaway: [Predictive regularities for entry and occupation, a corrected occupation baseline, and controls that separate an accounting identity from a physical explanation.],
  hero: "/research-outputs/cube-root-growth-paper/fig/edge.pdf",
)

= Growth as a boundary-access problem <sec:introduction>

A slow-growing territory may be hard to escape from even when the walker readily enters fresh ground once it reaches the boundary. Separating these events makes rule dependence measurable. It also creates a danger: the resulting factorization is exact by construction and can look like an explanation before any transport law has been supplied.

This paper distinguishes accounting, held-out prediction and intervention. The earlier boundary-return picture of Meng and Cohen @meng1994 motivates the question, while the calibrated census in the companion paper supplies the finite-time growth context. Neither that census nor the identity below derives boundary occupation from the microscopic rule.

= Measurement and scope <sec:methods>

== Rules, cohort selection and measurement windows <sec:rules>

An ant reads colour $c$, turns by `rule[c]`, increments that colour modulo rule length and steps forward on the square lattice. Blank-board trajectories are deterministic. Swapping L and R reflects the trajectory, so the census retains rules beginning with R and excludes all-identical-letter rules. The sweep covers 4083 rules of length 2–12; highway detection and builder exclusions leave #N.census.rules census rules and #N.probe.analysed usable probe fits. The growth-census companion gives the complete classification and exclusions.

The probe records visited area $A$, boundary cardinality $P$ and discovery and boundary-step counts in octave windows $[2^k,2^(k+1))$. A boundary cell has at least one unvisited four-neighbour, including hole rims. Baseline fits use $k=20$–$26$; each follow-up states its own cohort, seeds and windows. Area scales as $A tilde t^a$, width as $t^alpha$ and boundary as $P tilde A^beta$. Stationary and prefix-prediction cohorts are selected subsets, not representatives of all rules. A rule-bootstrap interval describes the selected rule population rather than between-start uncertainty.

== Splitting growth into edge entry, occupation and geometry <sec:decomposition>

*Growth requires both reaching the edge and stepping beyond it.* The probability of entering fresh ground from an edge cell is $c$. The ratio $kappa$ measures the fraction of steps spent on edge cells divided by the edge's fraction of the territory at the window endpoint. Its uniform reference during growth is derived in @sec:uniform-reference. A walker can have a high entry probability but grow slowly if it rarely reaches the edge.

Per window of $S$ steps (the window's step count; $d A slash d t$ below means $Delta A slash S$ over octave windows) let $B$ be the number of steps that start on a boundary cell and $Delta A$ the number that enter new ground. Boundary membership is evaluated at each step; $P$ and $A$ in the normalization are measured at the window endpoint. For $B>0$, define

$ c = (Delta A) / B, quad kappa = (B slash S) / (P slash A), quad (d A) / (d t) = c dot kappa dot P / A. $ <eq:rate>

The last equality is an _identity_ given these definitions. Measuring its agreement cannot validate a physical mechanism. In particular, $kappa$ is an observed occupation ratio, not a closure that predicts how the walker reaches its boundary. Its endpoint normalization also need not equal an average of instantaneous occupation ratios.

Conditionally, if $A tilde t^a$ with $a>0$, $c$ and $kappa$ scale as $t^(gamma_c)$ and $t^(gamma_kappa)$, and $P tilde A^beta$, matching powers gives

$ a = (1 + gamma_c + gamma_kappa) / (2 - beta), quad alpha approx a / 2. $ <eq:a>

@eq:a is also algebra under these scaling assumptions, so agreement between the measured $a$ and @eq:a (median error #f(N.identity.median_abs_err_blob) over blob rules) checks the fits for consistency only. Fixed-ratio octave increments have the same time power as a derivative for a positive power law, but independently fitted slopes need not satisfy this relation exactly; logarithmic growth is outside this power-law derivation. The approximation $alpha approx a/2$ additionally requires area to scale as the square of the measured linear size.

*The physical hypothesis is stationarity, not factorization.* If $gamma_c = gamma_kappa = 0$ and $beta = 1/2$, @eq:a gives $a = 2/3$. These conditions can fail, but measuring them on the same trajectory describes a growth regime rather than explaining why it occurs. Uniform occupation would supply the stronger closure $kappa=1$ for a fixed territory; approximate interior colour uniformity does not supply that closure. We do not derive either the stationary regime or its rule-specific occupation from the microscopic rule.

Geometry contributes to the growth prefactor too. In a continuous stationary approximation, writing $P=G sqrt(A)$ gives $A(t) approx [A(t_0)^(3/2)+(3/2)c kappa G(t-t_0)]^(2/3)$. Thus a prefactor prediction needs independent values for $c$, $kappa$ and the geometric amplitude $G$, as well as their persistence. Same-window collapse using measured factors supplies none of these independently; finite octave budgets require the discrete expression in @sec:forecast.

#figure(
  image("../../cube-root-growth-paper/fig/edge.pdf", width: 100%),
  caption: [The quantities in @eq:rate on a real territory (`RLL`, $2^16$ steps). Grey: cells visited so far, area $A$. Black: the _edge_, visited cells with at least one never-visited neighbour, size $P$. Only a step taken from an edge cell can enter new ground; $c$ is the fraction of edge steps that do, and $kappa$ compares the share of time the ant spends on the edge with the share of the territory that is edge. The right panel zooms on the boxed stretch of coastline.],
) <fig:edge>

== Deterministic simulation and reproducibility records <sec:reproducibility>

All simulation is deterministic and seeded: rules start from a blank board, so a rule has one trajectory; seeds enter in stochastic walkers and patched-start controls. The fast simulator is tested step for step against a reference implementation. Census summaries, prefix-prediction summaries and forecast errors are read from saved analysis outputs; some follow-up values are transcribed from their recorded summaries. Bootstrap intervals use fixed seeds. Exact producers, recipes and registration records are collected in the #link("../../cube-root-growth-paper/supplementary/reproducibility-audit.pdf")[supplementary reproducibility audit].

= Edge transport: predictions and mechanism tests <sec:factors>

== Stationary factors and the rotor comparison

Over all #N.probe.blob blob rules, the medians (and quartile ranges) of the factors are $c = #f(N.mf_blob.c.at(1), d: 2)$ #iqr(N.mf_blob.c), $kappa = #f(N.mf_blob.kappa.at(1), d: 2)$ #iqr(N.mf_blob.kappa) and $beta = #f(N.mf_blob.beta.at(1), d: 3)$ #iqr(N.mf_blob.beta, d: 3), with territory fill (area over bounding box) #f(N.mf_blob.fill.at(1), d: 2) #iqr(N.mf_blob.fill). Restricting to the #N.probe.core rules in the band $0.30 < alpha < 0.37$ (the "core", used in earlier drafts for comparison with the rotor) moves these medians by at most 0.01: $c$ #f(N.mf_core.c.at(1), d: 2), $kappa$ #f(N.mf_core.kappa.at(1), d: 2), $beta$ #f(N.mf_core.beta.at(1), d: 3).

The drift exponents are small, but the 0.05 threshold is loose: through @eq:a a drift of 0.05 shifts $a$ by about 0.033 and $alpha$ by about 0.017, as much as the rule-to-rule differences we are trying to explain. These fractions therefore say that $c$ and $kappa$ drift by less than the effect size of interest, not that they are exactly constant, and only the six $2^32$ runs probe much smaller drifts. $|gamma_c| < 0.05$ for #pct(N.identity.frac_blob_gc_small) and $|gamma_kappa| < 0.05$ for #pct(N.identity.frac_blob_gk_small) of all #N.probe.blob blob rules (the fractions are computed on the whole class, because "core" is itself defined by a width exponent near 1/3 and would make small drifts nearly automatic).

@fig:ck shows the long runs: both factors plateau from $2^17$ to $2^32$ for six rules. These observations characterize the measured cube-root regime; the predictions P1–P4 were written down before the analysis (#link("../../cube-root-growth-paper/supplementary/reproducibility-audit.pdf")[Audit 9]) and specify its proposed stationary factors. P4 predicted $beta$ close to $1/2$, and the measured $beta$ is #f(N.mf_core.beta.at(1), d: 3) (core median), equal to the rotor's #f(N.calib_A.rotor.beta.median, d: 3) in the same window (#link("../../cube-root-growth-paper/main.pdf")[the synthesis calibration table]). The original registration's P5 treated reconstruction of the exponent as a mechanism test; that criterion was not independent and is not used as evidence here. Calibration assesses estimator bias, not the validity of a transport closure.

The headline medians are for the whole blob class; the core band is selected on the outcome and appears only as a sensitivity check.

#figure(
  image("../../cube-root-growth-paper/fig/ck_time.pdf", width: 100%),
  caption: [Edge-entry probability $c$ and edge-occupancy ratio $kappa$ against $log_2 t$ for six rules run to $2^32$. Both are flat after $2^20$; $kappa$ fluctuates by roughly ten percent from octave to octave.],
) <fig:ck>

For the rotor the same decomposition gives $c = #f(N.rotor_ck.c.at(0), d: 2)$ and $kappa = #f(N.rotor_ck.kappa.at(0), d: 1)$; a random walk gives $c = #f(N.rw_ck.c.at(0), d: 2)$. So $c$ alone does not discriminate (the random walk's $c$ is close to the ants'), and the ants' $kappa$ (about #f(N.mf_blob.kappa.at(1), d: 1)) is about half the rotor's.

The cube root does not require the same $c$ and $kappa$ as the rotor; it requires that they be constant and that the edge scale as $A^(1/2)$. The typical ant's edge occupation is below the growth-adjusted uniform reference (@sec:uniform-reference); we have no explanation of its level.

== Uniform occupation on a growing territory <sec:uniform-reference>

The endpoint normalization in @eq:rate matters when interpreting occupation. For an instantaneously uniform walker, the expected boundary share is $P(t)/A(t)$. If $A tilde t^a$ and $P tilde A^beta$ throughout an octave, its measured reference is

$ kappa_("unif")(a,beta) = 2 integral_(1/2)^1 x^(-a(1-beta)) d x. $ <eq:uniform-reference>

At $a=2/3$, $beta=1/2$, this is $3(1-2^(-2/3)) approx 1.110$, rather than 1. A control that resamples uniformly from visited cells before each move gives $kappa=1.118 plus.minus 0.009$ over eight seeds, against 1.107 using its measured $a=0.677 plus.minus 0.005$ and $beta=0.520 plus.minus 0.007$ (between-seed sd; #link("../../cube-root-growth-paper/supplementary/reproducibility-audit.pdf")[Audit 44]). This calibrates the reference, not the ants' transport mechanism. The continuous prefactor formula above uses instantaneous coefficients; a window-normalized $kappa$ cannot be substituted as an instantaneous value without this averaging correction.

Across 2,185 stationary census blobs ($|gamma_kappa|<0.05$), $kappa/kappa_("unif")$ has median 0.814, interquartile range 0.664--0.957 and 5th--95th percentiles 0.443--1.332. About 20% are at least 1. The ratio uses each rule's own fitted $a,beta$ and its final measured occupation window, $k=26$, ending at $2^26$ steps; the exponent fits use $k=20 ... 26$. The supplementary census table includes these per-rule references. This is a distribution of single blank-board runs, not replicated rule means.

Matched-instrument walker controls (#link("../../cube-root-growth-paper/supplementary/reproducibility-audit.pdf")[Audit 48]) give ratios 1.24--1.32 for random and persistent walks, and $1.799 plus.minus 0.033$ for the rotor over $k=20 ... 26$ (eight seeds per setting; between-seed sd). Memoryless walkers have $beta approx 0.9$, so their uniform reference is about 1.02--1.03, not the 1.16 obtained by assuming a smooth boundary. Their fits use earlier windows $k=12 ... 22$; the rotor ratio is $1.686 plus.minus 0.035$ over that earlier range. These comparisons establish a finite-window contrast, not a matched-growth or asymptotic separation: the memoryless ratios lie inside the upper part of the ant distribution, and walker seed means differ from single-run ant values.

A further nine-level noisy-rotor scan (eight seeds per level) rejects monotone interpolation: the window-mean ratio rises to $2.59 plus.minus 0.09$ at noise 0.01 before falling to $1.26 plus.minus 0.03$ at noise 1. Small-noise rows drift, and escapes prevent the registered late-window comparison at most noise levels; the reported comparison uses $k=12 ... 22$, with two levels retaining seven of eight runs. The reference comparison does not explain the transient or the ant deficit. It does not apply to every memory model: the earlier reinforced-walk pilot has low, declining occupation in a different regime (#link("../../cube-root-growth-paper/main.pdf")[the synthesis stochastic-memory comparison]).

== Reproducible differences in edge occupation

The relative time spent on the edge varies between rules more reproducibly than the width exponent does. We quantify that reproducibility with intraclass correlations, as in the #link("../growth-census/main.pdf")[growth-census seed-variability analysis].

*Occupation is more rule-specific than the width exponent.* Replicated starts show _moderately reproducible_ differences (#link("../../cube-root-growth-paper/supplementary/reproducibility-audit.pdf")[Audit 10]; the within-rule sd is nearly as large as the between-rule sd): 99 random rules, each run from 12 random $5 times 5$ patches, have a between-rule sd of $kappa$ of 0.44 against a within-rule sd of 0.37 in the core band (ICC 0.58; 0.63 for $log kappa$; 58 further core rules give 0.50 and 0.63). The width exponent on this design (#link("../../cube-root-growth-paper/supplementary/reproducibility-audit.pdf")[Audit 11]) has ICC 0.12 (0.065 in the #link("../growth-census/main.pdf")[growth-census seed-variability analysis], a different set of rules and starts), so $kappa$ is much more rule-specific than the measured width exponent.
== Longer prefixes predict occupation in fresh stationary rules <sec:prefix>

*The first eight letters carry information that simple letter summaries miss.* The test transfers a prefix lookup from census rules to fresh, longer rules. Its predictive success is restricted to rules selected for a measured stationary regime; it is not a mechanism for $kappa$.

A follow-up registered an eight-letter prefix lookup before sampling 300 primitive rules of lengths 13 and 14, excluding the earlier exploratory sample (W3c; #link("../../cube-root-growth-paper/supplementary/reproducibility-audit.pdf")[Audit 12]). Each rule had eight patched starts, seeds 501–508, run to $2^27$ on an $8192^2$ board. Of 2400 runs, 414 escaped; 176 rules retained at least six core-band runs ($0.25 < alpha < 0.42$, $kappa > 0$), and #KP.n also met the stationary criterion $|"median" gamma_kappa| < 0.05$. Training used stationary census rules of length $<=12$ only; fresh rules and their outcomes were not added to the lookup.

The lookup predicts mean $ln kappa$ from census rules sharing the first eight letters, falling back to shorter prefixes with at least three training rules, or to the training mean. Prefix alone gives strict held-out $R^2 = #f(KP.prefix_r2)$, where the reference prediction is the training mean.

Adding the lookup to a regression on $ln A(2^22)$ raises $R^2$ from #f(KP.area_r2) to #f(KP.combined_r2): gain #f(KP.gain), rule-bootstrap 95% interval [#f(KP.ci.at(0)), #f(KP.ci.at(1))] (2000 resamples, seed 20261045). This passes the registered gain threshold of 0.15 with a positive lower bound. The six-letter gain, #f(KP.gain6), is below the same threshold, limiting transfer at that prefix length.

The size-controlled model uses measured early area, so its score is not prediction from the rule string alone; the prefix-only score is, conditional on the measured regime filter.

#figure(
  image("../../cube-root-growth-paper/fig/prefix_lookup.pdf", width: 100%),
  caption: [Measured against predicted $ln kappa$ on the fresh rules (leave-one-out prefix lookup, linear $ln A(2^22)$ term; scores recomputed from the audit-12 prediction file, not refitted). (a) Stationary cohort, area term only. (b) Stationary cohort, area plus eight-letter prefix lookup. (c) All retained rules, the same model: the gain largely disappears when the stationarity restriction is removed, so the lookup is a conditional predictor (dashed line: identity). Training-set and cohort definitions are in the text.],
) <fig:prefix>

@fig:prefix shows the cohort restriction directly: the improvement from (a) to (b) is visible as a tighter band about the identity, and (c) shows it largely absent for all retained rules.

The predictive gain is specific to the stationary cohort. An exploratory crossed comparison (#link("../../cube-root-growth-paper/supplementary/reproducibility-audit.pdf")[Audit 12], not registered) gives a prefix-8 gain of #f(KP.cross.all_stationary) when training on all retained census rules and testing on the same stationary fresh rules, against #f(KP.cross.stationary_stationary) with stationary training. Training and testing on all retained rules gives #f(KP.cross.all_all) (interval includes zero). Stationary training with all retained test rules gives #f(KP.cross.stationary_all), with an interval including zero. The prefix lookup is therefore a *conditional transport predictor*: among rules meeting the finite-window stationarity criterion ($|gamma_kappa| < 0.05$), the leading letter sequence carries predictive information about $kappa$ ($R^2 = #f(KP.prefix_r2)$). It does not predict whether a rule will be stationary; that requires simulation. This score measures prediction error relative to the training-mean baseline in the selected cohort; it does not identify a causal fraction of occupation variance attributable to the early instructions.

The current conclusion is that a prefix lookup carries predictive information about finite-window $kappa$ in the stationary cohort, including information beyond this particular area regression. It is not a derivation of $kappa$, a demonstration of a size-independent effect, or an unrestricted predictor for the census. Core-band and stationarity filters use measured dynamics, the bootstrap holds the training set fixed, and prefix families intentionally overlap between training and test. This tests transfer within prefix families to longer rules, not prediction of unseen families.

*Transfer remains a separate question.* The score above is within the selected stationary-rule setting. Subsequent registered six-letter-family hold-outs failed to beat their training-mean baseline (`experiments/archive/2026-10-kappa-prefix-family-holdout/`; status summarized in `notes/ACTIVE.md`, 2026-10-20). Thus prefix prediction must not be described as transfer to unseen families. This later qualification changes the interpretation of the existing score, not its value; the original model and family hold-out use different splits.

=== Conditioning on area can induce an opening-run association

Later decoding identified the opening same-letter run as a compact predictor of area-residualised occupation. This association requires a further control: early area depends on both edge entry $c$ and occupation $kappa$, while the opening run strongly predicts $c$ (@sec:c-law). Conditioning on their shared outcome can induce an opening-run association with $kappa$ even without a direct effect. Such a shared outcome is often called a collider.

A registered check on #RF.conditioning.at("4a").n fresh stationary rules (#link("../../cube-root-growth-paper/supplementary/reproducibility-audit.pdf")[Audit 46]) finds a conditional coefficient of #f(RF.conditioning.at("4a").obs_lead) per added opening turn in $ln kappa$ given $ln A(2^22)$. A permutation model with no direct lead effect reproduces it: mean #f(RF.conditioning.at("4a").null_lead_mean), central 95% interval [#f(RF.conditioning.at("4a").null_lead_ci.at(0)), #f(RF.conditioning.at("4a").null_lead_ci.at(1))]. Adding $ln c$ leaves coefficient #f(RF.conditioning.at("4a").with_c.lead), rule-bootstrap 95% interval [#f(RF.conditioning.at("4a").with_c.ci.at(0)), #f(RF.conditioning.at("4a").with_c.ci.at(1))]. The no-direct-effect model fits $ln A(2^22)$ using $ln c$, $ln kappa$ and a retained residual; it is a diagnostic construction, not an independently established causal graph.

Lead-preserving early-letter flips give mean change in $ln kappa$ of #f(RF.conditioning.at("4c").mean_d), interval [#f(RF.conditioning.at("4c").ci.at(0)), #f(RF.conditioning.at("4c").ci.at(1))], over #RF.conditioning.at("4c").n_pairs retained pairs (bootstrap clustered by base rule; retention #pct(RF.conditioning.at("4c").retention)). The earlier shortening mutation still has a total occupation change of about $-0.198$; this is not explained away by area conditioning. A post-hoc split by flip direction is confounded with the mutation arms. No direct opening-run effect on $kappa$ is established, and neither is its absence: the interval is from one selected cohort and one occupation window. All resampling here uses seed 20261019 and 2,000 draws.

The tested same-turn square-loop explanation also fails its registered prevalence and mediation criteria (#link("../../cube-root-growth-paper/supplementary/reproducibility-audit.pdf")[Audit 47]); its decisive interior-loop adjustment retains about 96% of the area-conditioned lead coefficient. This excludes the tested loop summary, not loops of other shapes or earlier transients. Gated loop surgery was closed unrun. A separate growth-clock audit retained only 7 of the required 12 complete families, so it fitted no primary effects. These outcomes do not strengthen the prefix score into a causal result. Direction-balanced interventions, a second cohort and prospective regime selection remain needed.

== Early transport budgets forecast later growth <sec:forecast>

A same-window identity cannot test persistence. We therefore specified a forecast on existing replicated runs before computing its errors (#link("../../cube-root-growth-paper/supplementary/reproducibility-audit.pdf")[Audit 17]). Write $g=P/sqrt(A)$; formally @eq:rate gives $(d (A^(3/2)))/(d t)=(3/2)c kappa g$. For an octave ending at $t$, with duration $S=t/2$, the exact discrete budget is

$ Q = (A^(3/2) - (A-Delta A)^(3/2)) / S. $ <eq:budget>

The endpoint product $(3/2)c kappa g=(3/2)(Delta A/S)sqrt(A)$ is a right-end approximation, typically #f(TF.ants.rule_medians.endpoint_over_exact, d: 3) times the exact budget in this cohort. We forecast with @eq:budget. Each trajectory's mean budget over windows ending at $2^20$, $2^21$ and $2^22$ predicts its increments in $A^(3/2)$ over the next four octaves, ending at $2^23$–$2^26$, without updating from those outcomes.

A competing model extrapolates a log–log drift fitted to the same three early budgets. The rule-independent baseline is the median early rule-mean budget after excluding the target rule and all its seeds.

There are #TF.ants.runs complete trajectories across #TF.ants.rules rules, with approximately 12 patched starts per rule; #TF.ants.excluded.len() trajectories are excluded by the completeness, nonescape or positive-growth criteria. We apply no outcome exponent filter. For each trajectory, error is the median absolute relative increment error over four forecast windows; the summary is the median of equal-weight rule means.

*Early budgets improve the typical forecast.* Constant budgets give #f(100 * TF.ants.rule_medians.constant, d: 1)% error against #f(100 * TF.ants.rule_medians.baseline, d: 1)% for the baseline and #f(100 * TF.ants.rule_medians.drift, d: 1)% for the drift fit. The reduction is #f(100 * TF.ants.reduction, d: 1)% (rule-bootstrap 95% interval #f(100 * TF.ants.reduction_ci.at(0), d: 1)–#f(100 * TF.ants.reduction_ci.at(1), d: 1)%; 2000 resamples, seed 20261013), passing the stated 30% prediction. Integrating all four forecast increments from the observed area at $2^22$ gives final-area error #f(100 * TF.ants.rule_medians.constant_final, d: 1)% against #f(100 * TF.ants.rule_medians.baseline_final, d: 1)% for the baseline.

Calibration separates persistence from a universal forecasting advantage. The same estimator on #TF.rotor.runs rotor seeds, with matched windows, gives #f(100 * TF.rotor.rule_medians.constant, d: 1)% error against #f(100 * TF.rotor.rule_medians.baseline, d: 1)% for the other-seed baseline.

On #TF.random_walk.runs random-walk seeds (training $k=17$–$19$, forecast $k=20$–$23$), errors are #f(100 * TF.random_walk.rule_medians.constant, d: 1)% and #f(100 * TF.random_walk.rule_medians.baseline, d: 1)%; drift extrapolation still misses by #f(100 * TF.random_walk.rule_medians.drift, d: 1)%. Synthetic $A=C t^(2/3)$ and $A=C t$ recover their known constant and square-root budgets respectively.

Near-stalls bound the forecast's reliability despite its typical accuracy. RMS within-rule seed sd of relative increment errors is #f(TF.ants.rms_seed_sd.constant, d: 2) for constant budgets, #f(TF.ants.rms_seed_sd.drift, d: 2) for drift and #f(TF.ants.rms_seed_sd.baseline, d: 2) for the baseline; these are ratios, not percentages. One retained trajectory (`RLLRRRLLRLRR@108`) has constant-budget error about 6506 times the observed increment. Near-stalls make relative errors enormous, so the robust improvement does not imply uniformly reliable predictions. Escaped or incomplete trajectories are excluded, and this test cannot forecast their breakouts.

An exploratory check, specified after the primary result, uses the median early budget of the other seeds of the same rule and gives #f(100 * TF.ants.rule_medians.other_seeds, d: 1)% error, slightly better than each trajectory's own early budget. This supports persistent rule-level growth budgets in the measured windows; it neither identifies the spatial-memory mechanism nor proves asymptotic scaling. Exact recipes, input hashes and all trajectory errors are recorded in the appendix (#link("../../cube-root-growth-paper/supplementary/reproducibility-audit.pdf")[Audit 18]).

*This forecast tests persistence of growth, not the separate transport factors.* @eq:budget uses only area endpoints. Its success therefore cannot show that measuring $c$ and $kappa$ adds predictive information beyond early area history, or validate their physical interpretation. An independent factor model would have to predict boundary access on held-out trajectories without using their measured boundary occupation or future growth, then improve growth forecasts against an area-history baseline. No such mechanistic closure is established here.

== Mechanism tests: local transport, board memory and boundary trapping <sec:mechanisms>

The tests bound what can set boundary occupation by separating three proposed sources: local transport statistics, stochastic spatial memory, and near-boundary geometry. @tab:exclusion collects the resulting constraints. Local summaries leave substantial rule dependence unresolved; the tested forms of stochastic memory do not reproduce growth and occupation together; and similar edge dwell times coexist with widely differing occupation. These constraints apply to the specified models and finite windows. They do not exhaust all stochastic models or establish that deterministic arrow updates are mathematically necessary. A successful mechanism must explain the joint growth and occupation regime, as well as its rule dependence.

#figure(
  table(columns: (1.05fr, 1.15fr, 1.25fr, 1.4fr, 1.35fr), inset: 5pt,
    table.header([Candidate class], [Hypothesis], [Operational test], [Finding], [Constraint]),
    [1. Local / Markovian], [Local turn bias or short strings determine $kappa$.], [Held-out linear/ridge fits; edge-colour predictors.], [$R^2=0.003$ for simple strings; edge predictors $R^2=-0.05$.], [These local summaries do not predict occupation; longer prefixes can.],
    [1. Memoryless transport], [Independent persistent turns reproduce the ant regime.], [Matched probe; five turn rates, six seeds each.], [$a=0.94$–$0.96$; $kappa=1.3$–$1.45$.], [Rejects this independent-turn closure of board dynamics.],
    [2. Stochastic board memory], [Site cookies or edge reinforcement suffice.], [Eight seeds per setting; growth and occupation measured together.], [Directional cookies escape; random cookies are diffusive; reinforcement has falling $kappa$.], [Memory alone is insufficient in these settings.],
    [2. Arrow randomisation], [Noise smoothly interpolates rotor occupation to a memoryless limit.], [Six noise levels, eight seeds each; 38 fitted runs.], [$a$ rises; $kappa$ first rises to 3.6–6.7 while $c$ stays 0.498.], [Phase disruption changes transport without changing edge-entry bias.],
    [3. Boundary trapping], [Edge dwell or crust depth determines $kappa$.], [Layer profiles on 24 rules; 26 matched pairs.], [Similar dwell with widely varying $kappa$; depth ordering 13/26.], [Local trapping summaries do not determine occupation.],
    [3. Excursion geometry], [Return angles and scaled displacement explain $kappa$.], [Size controls; held-out forecasts; disjoint-seed matching.], [Simple associations are size-confounded; a cutoff association remains.], [No established geometric mechanism; cutoff dynamics remain open.],
    [3. Excursion duration budget], [A tail of long interior returns sets the boundary share $B slash S$ beyond boundary residence and geometry.], [Registered 44-rule, 1408-trajectory test; rule-held-out PRESS gain, three area bands.], [T1 fails (band 0 gain #f(TB.t1_band0.gain, d: 2), lower bound #f(TB.t1_band0.lo95, d: 2)); T2 passes (#f(TB.t2.identity.median_rel_err, d: 2)) but persistence is better (#f(TB.t2.persistence.median_rel_err, d: 2)).], [Not supported at these scales; selected cohort only.],
  ),
  caption: [Exclusion matrix for candidate mechanisms. Findings constrain the tested closures rather than entire mathematical classes. Designs, windows, uncertainty and qualifications are given below and in the linked audits.],
) <tab:exclusion>

=== Local features and independent turns leave occupation unexplained

*Simple letter features.* (#link("../../cube-root-growth-paper/supplementary/reproducibility-audit.pdf")[Audit 10]): a linear regression on string features (turn probability $q$, $n$, run count, letters 1--6), fitted on a random half of the #N.probe.blob non-bursty blob rules and scored on the other half, has held-out $R^2$ = 0.003 for $kappa$ and 0.002 for its drift $gamma_kappa$, against 0.78 for $c$ with the same features and split (a different, simpler model than the chirality model in @sec:mixing, which reaches #f(N.followup.c_model.r2, d: 2) on a larger held-out set); Spearman($kappa$, $q$) = 0.08. On 192 rules with at least six core-band runs, leave-one-rule-out $R^2$ for the rule-mean $log kappa$ is $-0.06$ to $-0.04$ for ridge on letter-by-position, about 0 for ridge on 2- and 3-letter substring counts, and 0.04 for a prefix-5 neighbour mean. These scores constrain the tested low-order summaries, while leaving nonlinear information in longer prefixes available.
*Edge-colour statistics.* (#link("../../cube-root-growth-paper/supplementary/reproducibility-audit.pdf")[Audit 10]): on 40 random core rules the edge-weighted turn probability correlates with $c$ at Spearman $-0.84$ (a positive control that the instrument can see rule dependence) but with $kappa$ at only $-0.27$, and leave-one-out $R^2$ of $kappa$ on it and the edge-colour distance from uniform is $-0.05$.

*Independent-turn control.* The transport closure is tested directly by a memoryless walker that turns right with probability $Q$ and left otherwise, independent of the board, driven through the same probe (#link("../../cube-root-growth-paper/supplementary/reproducibility-audit.pdf")[Audit 10]; $Q in {0.25, 0.4, 0.5, 0.6, 0.75}$, six seeds each, $2^26$ steps on a $32768^2$ board; predictions written beforehand in #link("../../cube-root-growth-paper/supplementary/reproducibility-audit.pdf")[Audit 19], A1d). Its $kappa$ is roughly constant at 1.3 to 1.45 (within $plus.minus 5%$ across $Q$ from 0.25 to 0.6), but its area exponent is 0.94 to 0.96, not $2/3$.

So independent persistent turns reproduce roughly uniform occupancy but neither the cube root nor the ants' $kappa$ (about 0.9) nor the rotor's (about 2.0). This rejects the independent-turn mechanism; it motivates testing board memory without establishing that memory alone is sufficient, or excluding every memoryless mechanism.

=== Stochastic memory controls constrain particular models

Independent-turn, site-cookie and edge-reinforced controls did not reproduce the joint ant growth and occupation regime in the tested parameter ranges. These are failures of the tested constructions, not an exclusion of stochastic explanations. Full parameter grids and oracle records remain in the synthesis manuscript and its reproducibility audit (Audits 19–27). The controls motivate a return-time account but do not establish one.

=== Shallow trapping does not account for occupation differences

Layer profiles bound explanations based on shallow trapping (#link("../../cube-root-growth-paper/supplementary/reproducibility-audit.pdf")[Audit 22]; prior predictions in #link("../../cube-root-growth-paper/supplementary/reproducibility-audit.pdf")[Audit 23]). Layer $d$ is Manhattan distance to never-visited ground minus one; $rho(d)$ is visits per cell relative to the territory mean, with $rho(0)=kappa$. In 24 selected blank-board ant rules (12 extreme and 12 near $kappa=0.9$; #link("../../cube-root-growth-paper/supplementary/reproducibility-audit.pdf")[Audit 24]), 15 have depleted layers 2–4 ($rho=0.01$–$0.6$). In 13 of those, $c=0.61$–$0.66$ and edge-phase dwell is 1.5–1.6 visits per cell, despite a crust-class $kappa$ range of 0.13–18. Boundary occupation thus varies widely among rules with similar local edge kinetics.

The other nine have deeper occupation within 30% of uniform and $kappa=0.82$–$0.96$, a range narrowed by selection.

#figure(
  image("../../cube-root-growth-paper/fig/layers.pdf", width: 60%),
  caption: [Layer profiles $rho(d)$ for the 24 selected blank-board ant rules (15 with a crust, 9 without; thin lines), the rotor (mean of 12 seeds) and a persistent walk (mean of 5 runs), windows $k >= 22$, recomputed from the committed layer counts. Layer 0 is the edge, so $rho(0) = kappa$; the right-hand point pools all depths $>= 5$. Crust rules are depleted at depths 2–4 and span $kappa$ from 0.13 to 18 (the text above; the plotted values are window means); the non-crust rules, the rotor and the persistent walk stay close to 1 beyond the edge layer. The crust label comes from the exploratory split described in the text.],
) <fig:layers>

The class split is exploratory. Depletion extends beyond layers 0–1, and dwell–occupation correlations are negative (Spearman $rho=-0.26$ in the extreme cohort, $-0.59$ in the typical cohort), constraining both the registered first-two-layer explanation and the proposed positive dwell association.

The matched comparison further limits crust depth as an ordering variable (#link("../../cube-root-growth-paper/supplementary/reproducibility-audit.pdf")[Audit 25]): among 26 pairs matched on length, R count and edge-entry probability within 0.02, with rule-mean $kappa$ differing by at least 0.5, the lower-$kappa$ rule has the deeper crust in only 13 pairs, below the registered 18. Blank-board occupation preserves 25 of the 26 patched-start pair orderings. The reproducible occupation differences therefore require information beyond these local dwell and shallow-depletion summaries. Interior return dynamics are a candidate source of that information; the local tests alone do not establish their role.

=== Interior-return associations and their size confounds

Excursion tomography bounds which measured return summaries can account for $kappa$ beyond territory size (#link("../../cube-root-growth-paper/supplementary/reproducibility-audit.pdf")[Audit 13]; analysis and provenance in #link("../../cube-root-growth-paper/supplementary/reproducibility-audit.pdf")[Audit 14]). Apparent associations involving return displacement divided by territory radius and return angle were largely attributable to territory size. Early excursion features supplied no held-out predictive gain for later $log kappa$ beyond an area baseline, limiting these summaries as independent transport predictors. Extreme completed-excursion duration relative to territory radius remains associated with $kappa$, but the ratio retains a size confound, its binned quantile has coarse resolution, and window-crossing excursions are censored. The rotor control was outside its registered tolerance and final-window random-walk controls were unavailable, limiting the strength of the exclusion. These measurements narrow the candidate explanations without establishing a mechanism; matched-area comparisons or interventions are needed.

A subsequent registered analysis assigned area matching, $kappa$ and the excursion cutoff to three disjoint seed groups, rotating their roles (#link("../../cube-root-growth-paper/supplementary/reproducibility-audit.pdf")[Audit 15]). Across 44 previously selected rules, the rule-bootstrap intervals for pairwise concordance excluded chance at both measured windows. This weakens shared-trajectory area selection as a sufficient explanation.

A registered tail-budget test then asked whether the mean duration of interior returns predicts the boundary share beyond boundary residence and edge geometry (#link("../../cube-root-growth-paper/supplementary/reproducibility-audit.pdf")[Audit 43]; #TB.n_rules selected rules, 32 fresh starts each, three area bands). With the empirical binned mean duration as the estimator, the leave-one-rule-out gain was #f(TB.t1_band0.gain, d: 2) at the smallest band but its rule-bootstrap lower bound was #f(TB.t1_band0.lo95, d: 2), so the registered criterion failed; at the second band the gain was #f(TB.t1_band1.gain, d: 2) with lower bound #f(TB.t1_band1.lo95, d: 2). Extrapolating to the largest band met the registered error threshold (median relative error #f(TB.t2.identity.median_rel_err, d: 2) against 0.20), but a model-free log-linear extrapolation of the outcome seeds did better (#f(TB.t2.persistence.median_rel_err, d: 2)) and a 99.9th-percentile summary did worse (#f(TB.t2.q999.median_rel_err, d: 2)). The pass therefore does not support the tail. A Shapley decomposition of the model change between bands attributes #pct(TB.decomp_tail_share) of the change to the tail terms, but this follows largely from the identity (the mean duration far exceeds boundary residence) and is a model counterfactual, not causal evidence. The analysis scripts were written after the run with their choices fixed beforehand, the prediction without a perimeter-to-area rescaling is our choice, and the survival-family fit was not frozen. This is one selected cohort and no census-wide claim follows.

It is an association on existing simulations, not fresh-rule prediction: matching noisy area still leaves size uncertainty, escapes are excluded, and the two windows reuse trajectories. The earlier matched-area comparison did not meet its registered noise-floor gate (#link("../../cube-root-growth-paper/supplementary/reproducibility-audit.pdf")[Audit 16]), so it remains insufficiently resolved for the deferred transplant. The later concordance neither changes that gate outcome nor establishes a causal cutoff mechanism.

Together these constraints require an explanation beyond the tested local reflection, generic-memory and shallow-trapping closures. They focus attention on the evolving board state and interior returns, while leaving both the longer-prefix prediction and the residual cutoff association to be explained.


== Growth outliers accompany drifting edge occupation

*Slower and faster growth track how often the ant reaches the edge.* The entry probability is comparatively stable; the relative time spent at the boundary changes.

#N.probe.log rules grow logarithmically ($alpha$ median #f(N.cube.log.alpha.at(1))), with $kappa$ median #f(N.cube.log.kappa.at(1), d: 4) and $gamma_kappa = #f(N.cube.log.g_k.at(1), d: 2)$: the ant rarely visits the edge and the occupancy of the edge decays, consistent with an ant confined near its origin.

#N.probe.fast blob rules have $alpha > 0.37$ with $gamma_kappa$ median #f(N.cube.fast.g_k.at(1), d: 2) (edge occupation rises). Across blob rules the correlation of $alpha$ with $gamma_kappa$ is #f(N.identity.corr_alpha_gk, d: 2), with $gamma_c$ #f(N.identity.corr_alpha_gc, d: 2) and with $beta$ #f(N.identity.corr_alpha_beta, d: 2) (@fig:dev).

These deviations locate the limit of the stationary-factor description: the outlying growth exponents accompany drifting edge occupation, the departure specified in advance ("$kappa$ drifting strongly with $t$"). Through @eq:a this identifies which measured factor carries the deviation; the physical origin of its drift remains open.

#figure(
  image("../../cube-root-growth-paper/fig/deviations.pdf", width: 100%),
  caption: [Left: width exponent against the drift exponent of $kappa$; shared observables enter both axes. Right: area exponent against its reconstruction from @eq:a; the agreement is by construction up to fit error (see text). Neither panel tests a mechanism.],
) <fig:dev>

= Predicting edge entry and testing interior mixing <sec:mixing>

== Rule letters predict edge-entry probability

=== The opening same-letter run predicts edge-entry cost <sec:c-law>

Let $m$ be the length of the opening run of equal letters (1 for `RLL`, 2 for `RRLL`). On #RF.c_law.n_census stationary census blobs, the empirical fit is

$ 1/c approx #f(RF.c_law.C1.a) + #f(RF.c_law.C1.b) min(m,8). $ <eq:c-lead>

This is a fitted law, not a microscopic derivation. With the census coefficients frozen, it predicts $c$ on #RF.c_law.n_fresh fresh stationary primitive rules of lengths 13--14 with $R^2=#f(RF.c_law.C1.r2)$ and median absolute relative error #pct(RF.c_law.C1.median_rel_err). The fresh refit has slope #f(RF.c_law.C2.fresh_b), rule-bootstrap 95% interval [#f(RF.c_law.C2.ci_b.at(0)), #f(RF.c_law.C2.ci_b.at(1))] (2,000 resamples, seed 20261019; #link("../../cube-root-growth-paper/supplementary/reproducibility-audit.pdf")[Audit 45]). The fresh sample has eight patched starts per rule, seeds 601--608, with core-band and stationarity selection. On a separate blank-board tracer validation, #RF.edge.V.n of 600 candidates of lengths 11--16 survive a frozen growth filter; $R^2=#f(RF.edge.V.lead.r2)$ and median relative error #pct(RF.edge.V.lead.median_rel). This misses the registered $R^2 >= 0.80$ threshold. The cohorts differ in background, window and selection; both scores bound transfer of the law.

The tracer validation measures the last octave through $2^24$ steps on a $4096^2$ board, retaining unescaped runs with at least 200 births and area ratio 1.3--1.9 across that octave. Its instrument agrees with the census to median relative error 0.0026 on 207 stationary sample rules; rotor and random-walk calibration pass, with the latter requiring a shorter run because of board escapes (#link("../../cube-root-growth-paper/supplementary/reproducibility-audit.pdf")[Audit 46]).

A flat-band test preserves the relation under substantial changes to the initial interior. For #RF.edge.S.n selected rules, fresh rows occupy half a $256 times 1024$ torus beside previsited uniform-colour ground: the fitted slope is #f(RF.edge.S.band_slope), intercept #f(RF.edge.S.band_intercept), and squared correlation of $c$ with the blank-board census is #f(RF.edge.S.corr2). Replacing the interior with all-zero, young-only or old-only colours gives median absolute relative changes #f(100 * RF.interior.Z.median_rel, d: 1)%, #f(100 * RF.interior.Y.median_rel, d: 1)% and #f(100 * RF.interior.H.median_rel, d: 1)% (respectively #RF.interior.Z.n, #RF.interior.Y.n and #RF.interior.H.n retained rules). The initially registered $2^30$-step band run exhausted the fresh rows before measurement. The replacement selects the first tested endpoint with at least half the band consumed, rejects over 90% consumption or fewer than 5,000 births, and was frozen before comparing $c$. These are tests of robustness to initial interior colours within a selected finite-time regime, not proof that the evolved bulk is irrelevant.

Among circulating-colour boundary reads with a prior read, #f(100 * RF.edge.L1.frac_lag4, d: 1)% return after exactly four steps (#RF.edge.L1.n_rules rules with $m>=3$, about 1.90 million reads). This supports a local recirculation contribution. The proposed flat read-cost plateau and high birth probability at the first opposite turn fail, however. Three- and five-parameter return kernels give broader-validation $R^2=#f(RF.edge.V.K3.r2)$ and #f(RF.edge.V.K4.r2); the latter misses its registered 0.90 target. Sparse-background tests also reduce the lead slope as fresh cells become less common, but high-density escapes void the originally registered full-density comparison. The evidence narrows the explanation towards fresh-ground dynamics while leaving the constants and residual letter dependence unresolved.

=== Chirality and letter-group baselines

*Young edge colours encounter fresh ground more often on the left.* For edge steps on colours 1 to 3, the share with fresh ground on the left exceeds that on the right in #N.followup.chiral.left_more of #N.followup.chiral.rules calibration rules (medians #f(N.followup.chiral.left_med, d: 2) against #f(N.followup.chiral.right_med, d: 2)). This handedness, or chirality, means that a rule turning L on a young colour enters new ground more often.

Across rules $c$ ranges from about 0.1 to 0.67. A chirality model uses the rule letters and this measured asymmetry to predict $c$. It is retained as a historical baseline alongside the opening-run law. The 0.78 quoted in @sec:factors comes from a plain linear regression on string features, with different features, sample and split; these $R^2$ values are not directly comparable.

Constants (the share of edge steps by colour and the left/right fresh-ground rates) are fitted on a 300-rule sample and applied to the others without refitting.

On #N.followup.c_model.n held-out rules the model attains $R^2 = #f(N.followup.c_model.r2, d: 2)$ (correlation #f(N.followup.c_model.corr, d: 2); median absolute error #f(N.followup.c_model.mae_med, d: 2)); grouping rules by their first letter after the leading R explains #f(N.followup.r2_letters.r1, d: 2) of the variance of $c$, by the next three letters jointly #f(N.followup.r2_letters.r123, d: 2), and by the sixth letter alone (rules of length at least 8) #f(N.followup.r2_letters.r6, d: 3).

The model was a post-hoc fit to these data, though evaluated on rules outside its calibration sample; we have not tested it on rules of length above 12.

*Comparison with letter-group baselines.* A critique-driven reanalysis retains all #CB.n_test held-out rules and fits group means only on the same #CB.n_train calibration rules. The primary baseline groups by the letter after the leading R; the secondary baseline groups by the next three letters jointly, with a training-only fallback for absent groups. The groups and scoring procedure were fixed before this comparison, after the original scatter plot had been inspected.

#figure(
  table(
    columns: (2fr, 1fr, 1fr),
    table.header([Prediction], [Held-out $R^2$], [RMSE]),
    [One-letter group mean], [#f(CB.overall.letter1.r2)], [#f(CB.overall.letter1.rmse)],
    [Three-letter group mean], [#f(CB.overall.letters123.r2)], [#f(CB.overall.letters123.rmse)],
    [Chirality model], [#f(CB.overall.chirality.r2)], [#f(CB.overall.chirality.rmse)],
  ),
  caption: [Predictions of $c$ on exactly the original held-out rules. Group means use calibration targets only. $R^2$ uses the held-out-mean denominator, matching the original model score; using the training-mean predictor as reference gives #f(CB.overall.letter1.strict_r2), #f(CB.overall.letters123.strict_r2) and #f(CB.overall.chirality.strict_r2), respectively.],
) <tab:c-baselines>

Chirality reduces squared error by #f(100 * CB.comparisons.letter1.sse_reduction, d: 1)% against the one-letter baseline (95% interval #f(100 * CB.comparisons.letter1.sse_reduction_ci.at(0), d: 1)--#f(100 * CB.comparisons.letter1.sse_reduction_ci.at(1), d: 1)%). It has #f(-100 * CB.comparisons.letters123.sse_reduction, d: 1)% _more_ squared error than the three-letter baseline (interval #f(-100 * CB.comparisons.letters123.sse_reduction_ci.at(1), d: 1)--#f(-100 * CB.comparisons.letters123.sse_reduction_ci.at(0), d: 1)%). These are paired rule-bootstrap intervals with #CB.bootstrap_resamples draws, seed #CB.seed, stratified by the primary groups and conditional on the fitted models; related rules and initial-seed variability limit their interpretation.

Within the broad L and R groups, chirality still has $R^2 = #f(CB.primary_groups.L.r2)$ and #f(CB.primary_groups.R.r2), with #CB.primary_groups.L.n and #CB.primary_groups.R.n held-out rules. It therefore has some discrimination beyond one-letter grouping. After subtracting each three-letter group's held-out mean from both observations and predictions, however, its pooled within-group $R^2$ is approximately zero (#f(CB.grouping.letters123.centered_within_r2.chirality, d: 5)); the corresponding raw within-group score, which also penalises group-mean errors, is #f(CB.grouping.letters123.raw_within_r2.chirality). Thus the three-letter lookup is the stronger predictor, and the chirality model supplies essentially no additional residual discrimination within those groups. This observational comparison does not explain the growth exponent. Reproduction and per-group scores are recorded in #link("../../cube-root-growth-paper/supplementary/reproducibility-audit.pdf")[Audit 42].

#figure(
  image("../../cube-root-growth-paper/fig/cmodel.pdf", width: 55%),
  caption: [Held-out edge-entry probability: model against measurement. Predictions concentrate near 0.33 and 0.53 (rules with predicted $c approx 0.53$ have measured $c$ from about 0.25 to 0.67). The letter-group comparison in @tab:c-baselines quantifies the limitation: modest skill remains within one-letter groups, but essentially none after centering within three-letter groups.],
) <fig:cm>

== Interior colour uniformity and transport tests <par:mixing>

A candidate interior approximation treats the ant's turns as those of a persistent random walk with turning probability $q = \#R slash n$. This does not specify occupation of the evolving territory or its boundary. The sample is the #N.mix_sample.listed rules in #link("../../cube-root-growth-paper/supplementary/reproducibility-audit.pdf")[Audit 26], of which #N.mixing.typ_n are blob rules with $0.30 < alpha < 0.37$; the procedure used to choose the list was not recorded, so it should be read as a convenience sample.

We therefore repeated the test on #N.mixing_random.n rules drawn uniformly at random (fixed seed) from the core class, with predictions written beforehand (#link("../../cube-root-growth-paper/supplementary/reproducibility-audit.pdf")[Audit 27]): #N.mixing_random.uni_n of #N.mixing_random.n have near-uniform interior colours (our prediction of 60–85% was exceeded), their MSD-slope ratio has median #f(N.mixing_random.uni_ratio.at(1), d: 2) (range #f(N.mixing_random.uni_ratio.at(0), d: 2) to #f(N.mixing_random.uni_ratio.at(2), d: 2)), and the remaining #N.mixing_random.non_n have median ratio #f(N.mixing_random.non_ratio_med, d: 2).

The convenience-sample numbers follow. For the #N.mixing.typ_n typical rules we tested (a) colour uniformity (total-variation distance of interior colours from uniform), (b) turn correlations, and (c) the slope of mean-square displacement against lag, which for independent turns is $(1 - a')/(1 + a')$ with $a' = (2q-1)^2$.

For #N.mixing.uni_n rules with near-uniform interior colours (TV $<$ 0.05) the measured slope is within [#f(N.mixing.uni_ratio.at(0), d: 2), #f(N.mixing.uni_ratio.at(2), d: 2)] of the prediction (median #f(N.mixing.uni_ratio.at(1), d: 2)), the displacement exponent is #f(N.mixing.uni_expo.at(1), d: 2), and the lag-1 turn correlation is #f(N.mixing.uni_corr1.at(1), d: 3) at the median.

For the other #N.mixing.non_n rules, whose interior colours are far from uniform, the MSD slope is off by a factor of #f(N.mixing.non_ratio.at(1), d: 2) at the median (correlation between the ratio and the colour deviation across the sample: #f(N.mixing.corr_ratio_tv, d: 2)).

Time to mix across the territory is a fraction #f(N.mixing.mix.at(1), d: 3) (median) of the growth time.

For #pct(N.mixing.uni_n / N.mixing.typ_n) of the sampled rules, these particular interior statistics are compatible with the persistent-walk approximation. They do not establish a random-environment description of the full dynamics, uniform spatial occupation, or stationarity of $kappa$. Boundary occupation and its drift must be measured separately; @fig:ck reports those measurements for six rules.

= Prediction has advanced further than explanation

Opening rule letters predict part of entry cost and, within a selected stationary cohort, occupation. The broader-validation failure and the conditioning control limit the reach of those statements. The corrected uniform reference identifies an occupation deficit but does not explain why it occurs.

The tested local, stochastic-memory and shallow-trapping constructions do not close the transport problem. A useful next account must predict occupation on independent starts and previously unseen rule families, preserve the window convention, and survive interventions that change the proposed transport structure. Such a closure remains prospective; no unrun first-passage test is evidence for it.

= Evidence, provenance and draft status

This is an editorial split of existing research, not a new measurement. Exact commands, seed schedules, windows, exclusions and registration limits remain in the #link("../../cube-root-growth-paper/supplementary/reproducibility-audit.pdf")[shared reproducibility audit]. The companion manuscripts reuse evidence and should not be treated as independent replication. Source snapshot and numerical-input hashes are recorded beside this draft in `provenance.json`.

*Availability.* Repository archive URL and DOI remain to be supplied before submission. The simulator, committed result summaries, supplementary rule census and walker-reference table live in the accompanying repository.

*Authorship and assistance.* T.S. McNamara directs the research. Existing code, analyses and prose were developed with AI assistance as described in the synthesis; Codex assisted this editorial split and typesetting. Author review, funding and competing-interest statements must be finalized before submission.

#pagebreak(weak: true)
#bibliography("../../cube-root-growth-paper/refs.bib", style: "ieee")


