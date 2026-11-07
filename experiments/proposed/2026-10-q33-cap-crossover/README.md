# Q33: does an active fresh-run cap set a growth crossover?

## Status, question and registration

**Proposed; no registered calibration, excluded-pilot or confirmation runs.** A small Python fallback is available for technical checks; see [PYTHON.md](PYTHON.md). Prepared 2026-10-29 UTC against `8904956fbb5a0e3bce676a39e92f4543f3774c5f`. This commit registers the design and gates below. It does not certify an implemented instrument or authorize skipping those gates. Move to active with the migration helper when calibration starts. Confirmation requires a separate freeze commit containing actual input lists, executable commands, hashes and passed gate reports.

Question: when a cap actually changes fresh penetration, does increasing it move the crossover to compact growth in proportion to its size? This follows Q33 and wall-vs-memory Stages 3–3c; those stages did not meet all their registered thresholds. We separate three claims: bounded fresh runs preserve compactness absent crystallisation; the active spatial penetration scale sets crossover width; and its late exponent equals 2/3. Primary H-scale support rests on P1/P3/P4/P5 (claims 1 and 2). P2 separately scores the third claim's late band [0.59, 0.71] and the W∝m crossover and must not be folded into the primary pair. Q38 (crystallisation mechanism) and Q39 (why about 0.70) remain deferred.

Read [DESIGN.md](DESIGN.md) for derivation and the failed-manipulation audit, [IMPLEMENTATION.md](IMPLEMENTATION.md) for production requirements, and [NOTEBOOK.md](NOTEBOOK.md) for the append-only record. The shareable notebook contains narrative only; there are no empirical outputs.

## Intervention: hold persistence fixed, vary only the cap

On fresh departures use S (straight) with probability 127/128, R with probability 1/256, L with probability 1/256. At the m-th consecutive fresh departure override this with U (reversal). On every revisited departure use the underlying rule and advance its colour normally. S and U are interventions; the underlying rules remain the census L/R rules. Use one SplitMix64 draw per step, including forced/deterministic steps. With u=high32(draw), turn S unless (u & 127)==0; on that event bit 7 chooses R or L. This gives exact dyadic probabilities and avoids categorical-rounding ambiguity.

The turn distribution is identical at every m. The core comparison is each capped walker against its uncapped counterpart with the same rule and random stream. This avoids changing the natural persistence scale along with the cap.

Let fresh mean never previously **departed**, matching FreshSetWalker. Keep ever-departed bits separately from cyclic colour. At each step:
1. Inspect current cell; if fresh set r=r+1, otherwise r=0.
2. Fresh: if finite cap and r>=m turn U, otherwise use the draw above. Revisited: use Rule[colour].
3. Mark departed; increment colour modulo rule length; move.
4. Update arrival and departure observables at their documented times.

An entered fresh run has a departed predecessor: U returns to it, so the bound is m. The origin has no such predecessor and its first run can have m+1 fresh departures. Record this run separately; do not plant a virtual visited cell or include it in penetration-scale estimates. Cap=1 and colour-zero revisits need explicit oracle tests.

## Conditions, cohorts and fixed budget

Main: m=1,2,4,8,16,32,64,128, plus uncapped persistent-fresh policy, plus original ant: **10 arms x 200 rules = 2000 blank starts**, all initially north. The original ant is a census bridge, not an independent cap-dose arm. Retire the old RLU-cap / own-colour-zero factorial as the main manipulation for the reasons in DESIGN.md; its identities belong in unit tests.

Sampling frame: pin the CSV used to define the 2630 blob rules, check 2630 unique strings and its SHA-256. Sample from the whole frame, without the core exponent or burstiness filter. Sort by SHA-256 of UTF-8 `Q33-20261029-cohort:` plus rule (ties by rule); first eight are the excluded pilot and next 200 confirmation. This hash ranking is the fixed pseudorandom draw. Record overlap with previously studied rules rather than excluding them: the estimand is the full blob census, and the fixed intervention and held-out pilot/confirmation split protect the present test. Pin actual lists and inclusion/exclusion reasons before any pilot.

Main seed for rule = first eight bytes, big-endian, of SHA-256(`Q33-20261029-main:` + rule); share stream across arms, use a distinct stream for every rule. The sample unit is a rule; paired conditions and repeated windows are not independent replicates. Hash ranking is deterministic selection, not a source of fresh independent randomness.

Each main run has fixed maximum N=2^31 steps. Total maximum 4.295e12 steps. No outcome-triggered extensions. Hard operational stop: 24 hours of production machine time for the batch, excluding calibration and compilation. Checkpoint on stop; report incomplete runs and do not score missing windows. Pilot throughput must predict completion within this budget; otherwise register a smaller or resourced design *before confirmation*, without inspecting confirmation data.

Walker controls: rotor, memoryless persistent R/L walk, fresh RU walker, and this new persistent-fresh walker with unbiased memoryless R/L revisits. Run each at eight seeds 202610293301..08 up to 2^28. The last control isolates interior colour memory; it is not assumed to be porous. Ordinary ant identity checks are deterministic, not eight statistical replicates.

Excluded pilot: the eight held-out rules, same ten arms, N<=2^24; 80 trajectories, <=1.343e9 steps. Used for correctness, throughput, cap exposure, regime coverage and detector audit. All pilot exponents are labelled excluded exploratory measurements. No pilot rows enter confirmation estimates. Do not tune thresholds to make pilot outcomes pass.

## Gates and ordering

**G0 source/preflight:** full pruning audit at pinned revision, exact sample lists and seeds, implementation and independent oracle committed; fresh bits survive colour wraps, negative coordinates, tile edges, save/load. Gate failure stops the study before scientific interpretation.

**G1 calibration:** production versus sparse oracle step by step; dense versus tiled on small trajectories; exact deterministic and uncapped identities; original ants reproduce stored probes. Verify bound m outside origin for every tested step and equivalent results across thread counts. Use planted geometry to verify area, width, hull and boundary counters. Calibrate local fits on known synthetic exponents before ant readings.

**G2 manipulation:** an independent premarked flat half-plane with north-facing entries, one new blank half-plane per trial, tests penetration without any interior rule. For each m use 4096 trials, seeds 202610293400+i, stop at first departure from a visited cell; keep completed and right-censored observations. Require zero bound violations and at least 30% reaching the cap for m>=2. Analytically at least (127/128)^(m-1)>=e^-1 of trials follow the straight branch and reach it; binomial variability is tiny at this count. Use a sparse oracle; maximum 4096 x sum(m+1) steps is small. Measure duration-weighted spatial depth ell_m there; require OLS slope of log ell_m on log m in [0.8,1.2] for m=8..128. This is a manipulation check, not an ant result.

**G3 excluded pilot:** for each m>=8, in at least four of the eight pilot rules require >=100 non-origin cap interventions after 2^12. For each of m=16,32,64,128 require both W/m<=1 and W/m>=8 in at least four non-crystallised pilot trajectories. Failure means exposure or horizon is inadequate: do not assert a full crossover test, and revise/register before confirmation. The pilot may show that long straight runs crystallise; that is a possible design failure, not permission to drop such rules.

**G4 excursion calibration:** reuse the time-weighted Rev3 instrument (instrument a8a93b1; passing calibration 9e3621dce52922a139a74bb23b2346a3d10061fb), reproduce its frozen synthetic D/S separation and walker gates with its own censoring treatment. Do not use the retired number-weighted Score, and do not treat its old failures as exclusions of time weighting. Excursion shape is a secondary mediator; it cannot establish growth collapse by itself.

**G5 confirmation freeze:** publish passed gate reports, detector implementation/version and false-positive/false-negative audit, full command lines, machine details, source/binary/input hashes, locked dependencies, and fixed spec list. If anything material changes after pilot, append an amendment stating what was seen. Only then run confirmation. No empirical result is registered retroactively.

## Observables and finite windows

Save checkpoints at 2^k, k=8..31, with width W, x/y spans, departed area A, centre-point convex-hull area H, lattice perimeter P, boundary occupation, boundary reads, births and cap-turn counts. Save extra growth-only samples at t=floor(2^(k+j/8)), j=1..7. In every octave [2^k,2^(k+1)] fit log A and log W on log t using its nine samples. Place the estimate at sqrt(W_start W_end). Endpoint ratios are a separately labelled sensitivity check. Duplicate times, zero births and incomplete windows get explicit missing/stall flags.

Define primary W=sqrt((xmax-xmin+1)(ymax-ymin+1)) on departed cells. Also log census width as a separately named compatibility column after inspecting its implementation; do not silently redefine a legacy statistic. A counts distinct departed cells. P counts visited/unvisited four-neighbour edges, with holes included. Boundary cells are departed cells with at least one never-departed four-neighbour. A boundary read is classified immediately before the current departure; fresh cells are not yet in that set. Incremental counters must agree with full rescans in check mode.

For each window record boundary time fraction f_B, c_cost=B/births, b_rate=births/B, and kappa as the time-average of I_boundary A/n_boundary on pre-departure states, omitting states with n_boundary=0. Output the existing probe's kappa separately if its definition differs. Undefined ratios stay undefined. This avoids the old c versus 1/c ambiguity. Add area/bounding-box occupancy, hull occupancy and P-versus-A slope to separate a dense filler from porous growth.

Log fresh-run number and duration-weighted histograms, maximum spatial depth from the pre-entry territory, displacement from entry, cap activation and completed/incomplete runs. Reconstruct entry-territory depth in an optional diagnostic pass on pilot snapshots, since measuring against the evolving territory gives a different observable. Use flat-plane ell_m as the pre-confirmation measured length; do not estimate a collapse-rescaling parameter on confirmation curves.

## Crystallisation and resource censoring

Detect translated periodic highways, square-ring/spiral crawlers and column sweepers separately from growth classes. Exact candidate validation uses heading/colour/read-cell traces and repeatable translated or expanding macro-transitions. Freeze period search ranges and persistence requirements with positive archived examples and chaotic negative controls before confirmation. Keep the separate Python RLRLLL checker independent; do not replace it with the production detector. A finite trace validates an observed ordered regime, not its permanence.

For a candidate onset t0, censor every intersecting/later growth window and retain earlier windows. A suspected but unverified candidate gets an uncertain label, not a confirmed crystallisation. Report fits both excluding and including uncertain candidates. Record detection time and last verified chaotic time to show onset uncertainty. Allocation/time/checkpoint failures are resource censoring; they are not highways or fillers. Do not discard a difficult rule because a detector or pool fails.

## Registered predictions and decision rules

**H-scale:** for active caps, late non-ordered growth becomes compact and the transition scale is proportional to m (or independently calibrated ell_m). **H-local:** short turning geometry/interior effects dominate, so an active cap does not give this crossover. **H-order:** much of the apparent effect is selection into ordered structures. All three may coexist.

P1, manipulation: G2 and G3 pass. Failure makes confirmation uninformative under this design, not a falsification of H-scale.

P2, original sharp Q33 prediction (secondary): an earlier local alpha_A in [0.86,0.91] precedes late [0.59,0.71], with crossover W proportional to m. We do **not** assume the early interval transfers to the straight-biased policy: it may be ballistic. Score this exact prediction separately and report failure rather than replacing its band after seeing controls.

P3, primary cap effect: on paired capped/uncapped runs define d=alpha_A(capped)-alpha_A(uncapped), evaluated at matched W by linear interpolation in log W only between consecutive complete uncensored windows. For m=16,32,64,128 at W/m in [8,16], predict a pooled rule-median d<=-0.10 with its rule-bootstrap 95% interval entirely below zero. Require >=50 paired rules per m; report the change in support across m. Failure with adequate support contradicts this quantitative prediction, not every possible bound model.

P4, crossover: per run use the first downward alpha_A=0.78 crossing that is preceded by alpha_A>=0.85 and followed by two consecutive complete windows <=0.78. Interpolate linearly in log W at the crossing; require all participating windows uncontaminated by onset. No preceding high window means left-censored or absent crossover, not W_cross=0. No sustained crossing before stopping means right-censored. Require a common set of at least 50 rules with complete crossings at the same three or more m levels; specify the eligible subset without cherry-picking crossings (use all supported levels). Fit within-rule log W_cross=a_rule+p log m on complete paired crossings; predict p in [0.8,1.2]. Report its rule-bootstrap interval and interval overlap, plus the selection fraction. The censored table is primary context; complete-case p is conditional, never an unbiased population estimate by default.

P5, collapse score: use m=16,32,64,128 and x=W/m grid {0.5,1,2,4,8,16}. Interpolate per-run exponents as above, at most a factor-two gap in W. Require the same >=50 rules at every grid point and every m. Take per-m median curves and mean squared deviation from their across-m mean. Compare with the identical construction at unscaled W=m_ref*x, m_ref=32, using the intersection of rules supported by both constructions. Predict scaled/unscaled score<=0.75 with a paired rule-bootstrap 95% interval below 1. A zero denominator is undefined, not a successful collapse. Flat curves can collapse trivially: require a pooled decrease >=0.10 from x=1 to x=8. Curves versus W/ell_m are a prespecified secondary plot. No free horizontal shifts are fitted. Lack of matched support is inconclusive.

Call the joint H-scale prediction supported only if P1, P3, P4 and P5 meet their point criteria and P3/P5 uncertainty criteria; report every component separately. Otherwise label failed components or inconclusive coverage. This is finite-horizon support for this intervention, not a proof of asymptotic universality. The original porous-band prediction P2 can fail even if the broader active-scale test passes.

## Uncertainty, table and deliverables

Bootstrap whole rules jointly across m, 10,000 replicates, sorted input, seed 202610293399; deterministic reduction order. Resample seed-control trajectories separately; eight seeds are not eight independent rules. Report finite-frame selection and one stochastic realisation per rule as limits. Prefix-coincident trajectories remain sampled rules, but additionally show unique-trajectory counts.

Deliver alpha_A(W) and alpha_A(W/m) figures, compatibility alpha_W and occupancy plots, cap-exposure and ell_m diagnostics, and a table per m of compact, porous, intermediate, stalled, crystallised, uncertain and resource-incomplete outcomes. Compact/porous are descriptive final-three-complete-window classes: all three alpha_A in [0.59,0.71] / [0.86,0.91], respectively; no such triple means insufficient late support. Crystallised/uncertain/resource-incomplete take precedence at horizon, with pre-onset fits still shown. Give Wilson 95% intervals and numerator/200 for each outcome; separately show conditional fractions among growth-eligible trajectories. Do not force a three-way exhaustive table.

Ledger: distinguish measured cap exposure, measured growth/ordering, the fitted crossover association and the causal explanation. Show matched-rule and available-rule plots, censored fractions, finite-window drift, and every failed gate. Fresh-only versus every-colour-zero noise remains a separate registered, unrun follow-up. No new lattice, invariant or prefix programme is opened.

## Pruning-index preflight

At base revision above, inspected every entry's title, scope/predicate and amendments through the GitHub connector; local clone/rg was unavailable (proxy connection failure). Search concepts: fresh, cap, bounded, crossover, porous, compact, penetration, excursion. Relevant candidates:
- NR-20261026-wall-vs-memory-no-wall-porous: exact old hy:F1 specs; new S/R/L and finite-cap specs are outside membership.
- NR-20261028-wall-vs-memory-bounded-random-fresh-compact: exact old fs:RU/LU specs; not this intervention. Its interpretation explicitly does not establish H-bound.
- NR-20261028-excursion-score-compact-d-calibrators and NR-20261027-reflecting-cup-d-calibrator: retired number-weighted Score/calibrators; not time-weighted Rev3.
Other entries cover additive invariants, old single-letter crawler mutants, and old exposure-class specs; none licenses excluding new cap runs. Deliberate identity/calibration controls remain justified. Decision: **propose gated calibration, then separately freeze confirmation**. No empirical signature is added for an unrun experiment.

Before execution, repeat the documented full-index rg workflow on a real checkout and compare every actual spec with applicable predicates. Save the index revision and included/excluded manifests. This source review is not represented as a completed shell audit.

## Reproduction and current limits

A dependency-free Python sparse simulator, CLI, checkpoint format and independent-oracle tests are now available; commands and limits are in [PYTHON.md](PYTHON.md). Its technical tests do not establish the complete Q33 gates, detector performance or Rust/Python cross-execution equivalence. Production implementation targets and remaining acceptance checks are in IMPLEMENTATION.md. Use existing Rust/tiled census/probe infrastructure; CPU first, Metal only after equivalent instrument support and oracle checks. Run locked release builds and uv-managed analysis. There is no new dependency justified by this documentation proposal.

This supersedes the *design*, not the historical observations, of the local-only 2026-10-29 cap feasibility memo. That memo's analytic union bound motivated changing the intervention; its C arithmetic is not a run of this proposed walker and is not imported as empirical results. No confirmation has started, so this investigation belongs in proposed/.

## Amendment A1 (2026-11-05, before any calibration, pilot or confirmation run)

Registration hygiene in response to the 2026-10-31 review of PR #31. No walker data were seen; no prediction band, gate threshold or decision rule above is changed. Items 3 (P3 discrimination) and 6 (metric for depth D) of that review need a design choice and are **left open** here.

1. **Provenance of P2 and the retired factorial.** The 2026-10-29 cap feasibility memo is not in the repository or on the machine used for this amendment, so it cannot be audited. P2 is therefore to be read as **registered by this proposal** (registration commit `36e6fba`, 2026-10-29), not inherited from an earlier registration; Q33 in `notes/open-questions-hypotheses.md` is qualitative. Its bands come from committed results: porous early a 0.86-0.91 from wall-vs-memory Stage 1 (`experiments/active/2026-10-wall-vs-memory/README.md`, F1) and the deterministic late band 0.59-0.71 from the same stage as summarised in `notes/open-questions-hypotheses.md` (Q30/Q31 entry). "W_cross proportional to m" is new in this proposal. The "RLU-cap / own-colour-zero factorial" is described only in DESIGN.md section 1; there is no committed run of it to retire.
2. **Sample lists pinned.** `scripts/pin_samples.py` applies the rule above to the committed frame and writes `inputs/frame.sha256`, `inputs/specs_pilot.tsv` (8 rules) and `inputs/specs_confirm.tsv` (200 rules), each with its main seed. `--check` regenerates and compares. Overlap with previously studied cohorts is recorded in `inputs/overlap.tsv` (Amendment A2).
3. **Area convention (G1).** The stored `probe` counts cells on arrival, including the current cell; this instrument counts departed cells. The mapping to verify in G1 is A_probe(t) = A(t) + [current cell never departed], and x/y spans likewise include the current cell in `probe`. G1 compares A and spans exactly after this mapping.
4. **Sample schedule.** Sub-octave times are defined by the integer formula t = floor(2^(k + j/8)) = the integer 8th root of 2^(8k + j). `inputs/schedule.tsv` lists every time for k = 0..31; a test checks the Python schedule against it so a Rust port can reproduce the same integers.
5. **Origin exception.** Analytic claim registered before the test that checks it: for m >= 2 the origin's first run has at most m fresh departures, because the U at r = m reverses into the previous cell of the same run, which is already departed. Only m = 1 can give m + 1 (the U at the origin enters a fresh cell). Prediction for the test: origin run length <= m for every m in 2..16 and seeds 0..63 on rules RLL and RLLR; and some m = 1 trajectory has origin run length 2.
6. **Provenance.** CLI provenance records the git commit and a dirty flag (AGENTS.md rule 2).

## Amendment A2 (2026-11-05, before any calibration, pilot or confirmation run)

Continues A1 registration hygiene. No walker growth data; no prediction band, gate threshold or decision rule above is changed. Review items 3 (P3 discrimination) and 6 (depth D metric/reference) remain **open** and still need a design choice.

1. **Overlap record.** `inputs/overlap.tsv` lists every pinned pilot/confirm rule that also appears in a previously studied experiment cohort (wall-vs-memory Stages 3b/3c, crawler-cost cohorts, kappa exposure/return/rule-space pools, and related archives). The blob census frame itself is omitted: every Q33 rule is in it by construction. Counts at this commit: 5/8 pilot and 58/200 confirmation rules overlap at least one study (63 distinct rules, 74 rule-study rows). Inclusion is unchanged; the record is for interpretation only.
2. **Full local pruning-index rg audit.** On this checkout, `rg -il 'cap|fresh|crossover|penetration|persistent|bound|porous|compact|excursion' notes/pruning-index/entries/` matches six of seven entries (all except `NR-20261022-additive-laws-order-blind`). Membership predicates checked against the new S/R/L + finite-cap intervention:
   - `NR-20261026-wall-vs-memory-no-wall-porous`: exact old hy:F1 / randomised-fresh specs; outside membership.
   - `NR-20261028-wall-vs-memory-bounded-random-fresh-compact`: exact old fs:RU/LU (and related bounded) specs; not this intervention; does not establish H-bound.
   - `NR-20261027-reflecting-cup-d-calibrator` and `NR-20261028-excursion-score-compact-d-calibrators`: excursion Score/calibrator retirements; not growth-cap runs.
   - `NR-20261025-crawler-window-single-letter` and `NR-20261025-kappa-exposure-classes-exposed-edge`: fixed parent/mutant or patched-start cohorts; not this policy.
   - Additive-laws entry: invariant mining only; growth questions excluded by its own permit.
   Decision unchanged: **propose**; no empirical pruning signature licenses skipping gated calibration. Index revision: files as of commit `ec20c3a` (A1 head) plus this amendment.
3. **Memory budget (review item 10).** If the uncapped arm is nearly ballistic, A approaches t and at N=2^31 can reach ~2e9 departed cells, far beyond the 1 GiB process-wide tile pool in IMPLEMENTATION.md. Default until pilot data exist: run uncapped arms **sequentially**, fail loud on allocation failure, and log peak RSS per arm. After the excluded pilot, either confirm the sequential budget from measured A(t) or register a resized pool before confirmation. No A(t) prediction is claimed here (pilot not run).
4. **Claims wording (review item about "first two").** Opening paragraph now states that P2 separately scores the third claim; primary H-scale support is P1/P3/P4/P5.
5. **Draft blog link (review item 11).** `blog/_drafts/q33-a-cap-must-be-used.md` now points at a commit-pinned blob URL instead of the branch tree path.

## Amendment A3 (2026-11-06, before any calibration, pilot or confirmation run)

Registration hygiene in response to the 2026-11-05 review of PR #34. **No walker growth data; no change to any prediction band, gate threshold or decision rule.** Review items 3 (P3 discrimination of H-scale vs H-local) and 6 (metric/reference for depth D) remain **open** and still need a design choice by the user; this amendment does not decide them.

1. **`git_dirty` provenance.** A1 item 6 said the CLI records a dirty flag. The 2026-11-05 review found it was always true for real runs under `results/`, because status was sampled after the run wrote untracked outputs, and because untracked files were included. Fix (in `scripts/python_sim.py`): capture `git rev-parse HEAD` and a single `git status --porcelain --untracked-files=no` **before** `destination.mkdir`, and reuse those values in provenance. Tracked modifications still mark dirty; the run's own new output directory does not.

2. **Overlap record is regeneratable and includes crystallisation-relevant cohorts.** A2 item 1 left `inputs/overlap.tsv` without a producing script and omitted cohorts that bear on H-order. Fix: commit `scripts/overlap.py` with an explicit `COHORTS` list (extractor per source file; exact rule membership only — no prose substring matches) and `ONSET_SOURCES` for known highway onsets. New cohorts relative to A2: unresolved-1e10 highways, late-highway board-check rechecks, B5 late highways, square-ring-fillers P6, highway-preconditions (+ control), c-law-mechanism sample and band. Columns now include `known_onset` and `onset_lt_2_31`. `--check` regenerates and compares; a unit test covers it. Counts at this amendment: see the NOTEBOOK entry / `overlap.py --summary`. Notable: confirmation rule `RRLRLRL` has onset 1880688044 < 2^31 (`onset_lt_2_31=yes`); `RRRLLLRRL` has onset ~4.79e10 (`no`). Inclusion of these rules in the Q33 sample is **unchanged**; the flag is for interpretation and for later crystallisation-detector positive-control design (not decided here).

3. **A1 item 5 timing correction.** A1 said the origin-exception analytic claim was "registered before the test that checks it". The prediction commit `7e9feb4` and the test-result commit `ec20c3a` are 42 s apart; the NOTEBOOK deviation at that time records a failed-then-fixed test run inside the same session. The claim is analytic and deterministic, so scientific risk is low, but commit order is **not** evidence of prior registration. Correction: the claim and its test were written in the same session; treat them as co-registered at A1, not as a blind prediction. The sharper A3 origin assertions below are registered in this amendment before the test change that enforces them.

4. **Claims-to-predictions mapping (opening paragraph).** A2 item 4 rewrote the opening to say P1/P3/P4/P5 carry claims 1 and 2. Quoted A2 wording: *"Primary H-scale support rests on P1/P3/P4/P5 (claims 1 and 2). P2 separately scores the third claim's late band [0.59, 0.71] and the W∝m crossover and must not be folded into the primary pair."* Correction: none of P1/P3/P4/P5 scores claim 1 (bounded runs preserve compactness / late α_A near 2/3). Compactness appears in P2's late band and in the descriptive outcome table only. Also, "W∝m" is shared content of P2 and P4 (P4 scores p in [0.8, 1.2]); the two are not independent support for that quantity. Restated mapping used from this amendment: claim 1 is assessed **descriptively** (outcome table) and secondarily via P2's late band; claim 2 (penetration scale sets crossover width) is scored by P3/P4/P5 with P1 as the manipulation gate; claim 3 (late exponent equals 2/3) is scored by P2's late band. P2 and P4 both speak to W∝m and must be reported as overlapping, not additive, evidence.

5. **Origin-exception test sharpening (registered before the test edit).** Analytic addendum: under the update order in this README, for every seed/rule in the A1 grid, the origin run length at m = 1 is exactly 2 (not merely ≤ 2), and for each m in 2..16 the maximum origin run length over that grid equals m (the bound is tight). The unit test now asserts these.

6. **Memory plan detail (review minor).** A2's sequential uncapped default avoids pool contention across arms; it does not make a single uncapped arm fit in 1 GiB. Until pilot A(t): keep the process-wide 1 GiB pool as the per-arm limit under the sequential schedule; estimate ~24–32 bytes per departed cell for the tiled backend as a planning figure (exact layout is an implementation detail to freeze with G0). A resource-censored uncapped partner drops that rule from P3/P5 paired support and can bias those scores toward slowly growing rules; report the resource-censor fraction alongside P3/P5 and do not impute missing partners.

7. **Pruning-index record.** Index files last changed on main at `cc7a885` (excursion Rev3 merge). At this amendment head (see NOTEBOOK for `git rev-parse HEAD`), the concept `rg -il` still matches six of seven entries as in A2. Literal rule-string query required by the index README: `rg -w -F -f <208 Q33 rules> notes/pruning-index/entries` → **0 matches**. Decision unchanged: **propose**.

8. **Review item numbering.** The draft-blog commit-pin was item 12 of the #31 review, not item 11. Item 11 (NOTEBOOK entries with time-of-day and own short hash) is addressed by this amendment's NOTEBOOK entries and by using exact NZDT timestamps below.

P3 discrimination and the D metric remain open for the user.

## Amendment A4 (2026-11-07, before any calibration, pilot or confirmation run)

Registration hygiene in response to the 2026-11-06 follow-up review of PR #34. **No walker growth data; no change to any prediction band, gate threshold or decision rule.** Review items 3 (P3 discrimination) and 6 (D metric) remain **open**.

1. **Census onset source missing from `ONSET_SOURCES`.** A3's overlap record flagged confirmation rule `RRLRLRL` as the sole in-horizon onset (`onset_lt_2_31_distinct=1`). The 2026-11-06 review found confirmation rule `RRRRRRRLR` has a confirmed census highway onset of **756,289,068** steps (< 2^31) in `experiments/archive/2026-10-census-sweeps/results/confirmed_1B.csv` (`confirmed=true`, period 452), and the same onset appears in column 5 of `highway-preconditions/results/highway_specs.txt`. A3 left both files out of `ONSET_SOURCES`, so `known_onset` / `onset_lt_2_31` for `RRRRRRRLR` stayed blank. Fix (registered before regenerating): add those two committed tables to `ONSET_SOURCES` in `scripts/overlap.py` (census rows only when `confirmed=true`; highway-preconditions via the existing whitespace table: rule, period, dx, dy, onset). Inclusion of the rule in the Q33 sample is **unchanged**; the flag is for interpretation and crystallisation-control design. Expected after regeneration: `onset_lt_2_31_distinct=2` (both `RRLRLRL` and `RRRRRRRLR`). Cohort membership lists are unchanged.

## Amendment A5 (2026-11-07, before any calibration, pilot or confirmation run)

Registration hygiene for the remaining mechanical items of the 2026-11-06 follow-up review of PR #34 after A4. **No walker growth data; no change to any prediction band, gate threshold or decision rule.** Review items 3 (P3 discrimination) and 6 (D metric) remain **open**.

1. **`overlap.py` rewrite gate.** A3's default path rewrote a differing committed `inputs/overlap.tsv` without being asked. Fix: write only when the file is absent, or when `--write` is passed; otherwise print `DIFFERS` and exit 1. `--check` still compares only. Docstring updated to match.

2. **`git_dirty` and untracked helpers.** A3 sampled status before writes with `--untracked-files=no`, which also hid an untracked helper or input the run imports. Fix: keep untracked files in the check (`--untracked-files=normal`) and still sample **before** `destination.mkdir`, so this run's new output directory is not yet present. Tracked modifications and pre-existing untracked paths mark dirty; the run's own new directory does not.

3. **Per-cell memory figure source.** A3 attributed "~24–32 bytes per departed cell" to the tiled backend. That figure does not come from `tiled-grid-backend/DESIGN.md` (about **1 B per resident/packed cell**, lines 44–51). Correction in IMPLEMENTATION.md Amendment A5: use ~1 B/cell for the tiled Rust backend (so 1 GiB holds order 1e9 cells; ballistic uncapped arms still resource-censor before 2^31), and treat ~24–32 B/cell only as a planning guess for the Python `dict` sparse simulator until measured. Exact layouts freeze at G0.

4. **A3 item 5 origin assertions are observations, not registered predictions.** The sharper m=1 "== 2" and m≥2 "max == m" statements were written in the same commit as the test that asserts them (`21b3b22`), and the facts were already reported in the 2026-11-05 review. Call them **observations the test now asserts**, not blind registered predictions (same correction class as A3 item 3 for A1). The test remains; the epistemic label changes.

P3 discrimination and the D metric remain open for the user.
