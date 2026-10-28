# kappa and the chiral edge layer: does the opening run act on fresh ground?

Registered 2026-10-19 08:45 (+13:00), base commit `3f23de3`, **before any analysis of necklace-matched data**.
Stage 1 (below) is analysis-only on `probe_summary.csv`, which has been seen before (K1 ICC, W3 prefix work), but the
within-necklace lead regression has never been run. It is therefore a registered test on seen data (not blind),
and the lead effect itself is known from the cross-section, so only the within-necklace design is new.

## Hypothesis (mechanism)

Fresh ground reads colour 0, 1, 2, ... in order, and edge cells are young. With rule `R^m L ...` a cell turns the
ant the same way on its first m visits. An ant circling on young cells makes a closed 4-step loop (turn, turn, turn,
turn), re-reading those same cells, so it dwells around a newly opened patch for roughly 4m steps instead of
leaving. Picture: bulk is old and near-uniformly coloured (diffusive); the rim is a thin chiral layer whose strength
is the opening same-letter run, like skipping orbits in a magnetic field that acts only at a wall, or the surface
accumulation of persistent (active-Brownian) walkers whose persistence is set at the wall.

Why test this rather than the plans in `notes/kappa-mechanisms-2026-10-15.md`: it is the mechanistic reading of the
only kappa predictor that has survived fresh data (leading run: L1, L3, A1, M3) and it explains the one unexplained
asymmetry (extending the lead cuts A22) through c, since loop steps are boundary steps that open no new cell:
dA/dt = c kappa P/A with c falling as kappa rises.

## Stage 1: within-necklace test (no new runs)

Cyclic rotations of one rule have identical composition and cyclic sequence, and differ only in which colour the
blank ground reads first (K1: ICC of ln kappa across rotations is only 0.199, so ~80% of variance is within
necklace). If the opening run acts on fresh ground, then within a necklace ln kappa should follow each rotation's own
lead. A composition or bulk-cycle explanation predicts no within-necklace slope.

Data: `experiments/archive/2026-10-probe-growth-census/results/probe_summary.csv`, blob class, kappa > 0 (as K1); stationary
subset |g_k| < 0.05 as a sensitivity. lead = length of the opening same-letter run, capped at 6 as in the
leading-run experiment; trail = the closing same-letter run (capped at 6), the control: it is a property of the
same string with the same composition but not read first by fresh ground. Necklaces with >= 2 members of differing
lead. Demean ln kappa, ln c, lead, trail within necklace; pooled within-necklace OLS slope; CIs by bootstrap over
necklaces (2000, seed 20261019).

- **N1** slope of ln kappa on lead (within necklace) > 0, bootstrap CI above 0, and >= 0.08 per step
  (cross-section 0.15-0.2; allowing for dilution by the cap and by rotations that fall outside the blob class). ~70%.
- **N2** slope of ln c on lead < 0 with CI below 0 (loops are boundary steps that open no cells). ~55%.
- **N3** control: |slope of ln kappa on trail| < 0.5 x slope on lead, and its CI includes 0 or is smaller in
  magnitude than the lead CI's lower bound. ~65%.
- **N4** within-necklace R^2 of the lead term >= 0.05 for ln kappa. ~60%.
- **N5** (descriptive, no threshold) repeat on stationary rules only, and with lead uncapped.

Decision rule. N1 fails => the lead effect is not a fresh-ground effect at fixed cyclic content in the census
(composition/bulk-cycle or area-proxy reading wins) and Stage 2 is not run. N1 holds and N3 holds => proceed to
Stage 2. N2 failing while N1 holds means the c-mediated story (loops as non-opening boundary steps) is wrong even
if lead matters, to be reported as such.

## Stage 2 (proposed, not yet registered)

Background dose-response with the rule fixed, `sbg:RULE:SEED:DENSITY`, then a micro-observable (fraction of
boundary steps inside same-turn runs of length >= 4, dwell per new cell). Registered separately after Stage 1.

## Commands (WSL, repo root)

```bash
uv run experiments/archive/2026-10-kappa-chiral-edge/scripts/necklace_lead.py   # results/necklace_lead.{txt,json}
```

## Stage 1 results (run 2026-10-19 ~08:55, commit 3f23de3, seed 20261019, 2000 necklace bootstraps)

`results/necklace_lead.{txt,json}`. All blob: 536 necklaces / 2358 rules. Stationary: 474 / 1891.

| pred | outcome |
|---|---|
| N1 slope ln kappa on lead >= 0.08, CI > 0 | **FAILED**: all blob -0.007 [-0.037, 0.017]; stationary +0.044 [0.027, 0.060] (~1/4 of the cross-sectional 0.15-0.2, still below 0.08) |
| N2 slope ln c on lead < 0 | **HELD, much stronger than expected**: -0.243 [-0.249, -0.237], within-necklace R^2 0.83 (stationary -0.228, R^2 0.86) |
| N3 trail control | moot (N1 failed); trail slope on ln kappa +0.013 [-0.013, 0.039] all, +0.022 stationary |
| N4 R^2 >= 0.05 for ln kappa | **FAILED**: 0.000 (all), 0.026 (stationary) |

Per the decision rule Stage 2 (sbg dose-response) is NOT run. Reading: at fixed cyclic content the fresh-ground
opening run barely moves kappa; it moves **c** (births per boundary step) almost deterministically. The edge-layer
loop picture is right about c and wrong about kappa. The cross-sectional lead-kappa association therefore must come
mostly from between-necklace content correlated with lead.

## Stage 1b (registered 2026-10-19 09:05, before running; census data again)

Hypothesis: that content is the longest cyclic same-letter run M (max over the necklace, cyclic, = max over rotations
of lead), a bulk-cycle property: a run of M same-turn colours makes any cell, at any age, loop for M reads.
Stationary blob rules, capped at 6 for both.
- **M1** R^2 of ln kappa on M exceeds R^2 on lead (OLS, same rules), and M's R^2 >= 0.05.
- **M2** with both in one regression the lead coefficient falls to < 50% of its lead-only value, M's coefficient > 0.
- **M3** necklace-level: necklace mean ln kappa on M, slope > 0 with necklace-bootstrap CI above 0.
(Confound I know of: M, rule length and ln A(22) are all correlated; no area control in this stage, so a positive
result is "kappa follows cyclic run content", not a clean causal claim.) Script `scripts/cyclic_run.py`.

## Stage 1b result (run 2026-10-19 ~09:10; `results/cyclic_run.txt`, stationary blob, 2185 rules, 625 necklaces)

M1 **FAILED** (R^2 M 0.033 < 0.05; and census-wide ln kappa on lead has R^2 0.001, slope +0.010: the lead-kappa
association exists only after conditioning on ln A(22), see leading-run experiment). M2 **FAILED** (lead coefficient
rises, ratio 4.28, when M is added). M3 **FAILED**, wrong sign (necklace-level slope -0.071 [-0.088, -0.053]).
Cyclic-run content does not explain it. Descriptive `results/c_by_lead.txt` (post hoc, seen before registering
Stage 3): c is nearly a function of lead: mean c 0.487, 0.374, 0.297, 0.242, 0.208, 0.181 for lead 1..6, sd within
lead 0.07 (lead 1) falling to 0.015, and 1/c grows ~linearly (2.09, 2.69, 3.38, 4.15, 4.83, 5.57).
Back-of-envelope: with total d ln kappa/d lead ~ 0, b ~ +0.15 at fixed area, d ln A22/d lead ~ -0.3 (M-series) implies
d ln kappa/d ln A ~ +0.5 (partly definitional, kappa = B A / P): the lead effect on kappa is a conditional-on-area
effect that cancels against lead's effect on growth via c. Unverified.

## Stage 3: lead sets the edge birth rate c (registered 2026-10-19 09:25, before computing anything on fresh rules)

Reframed hypothesis: at the growing edge the ant reads young cells; the opening run m is the number of consecutive
same-turn reads, so it sets the number of boundary steps per birth, 1/c ~ a + b m. The naive 2x2-loop picture
predicts a = 0, b = 1 (each new 2x2 block costs 4m steps for 4 births); the census table already shows b ~ 0.7, so
that naive picture is stated here as expected to FAIL in b, and kept as a reference.
Fit on census only (stationary blob, `probe_summary.csv`, `1/c = a + b min(lead,8)`, OLS on 1/c), then predict fresh rules
(`2026-10-kappa-leadrun-fresh/results/fresh_rules.csv`, kept & stationary, lengths 13-14, never used in the fit,
c measured by the same probe, 8 seeds averaged, so noisier than census):
- **C1** out-of-sample R^2 of predicted vs observed c >= 0.75 and median |relative error| <= 0.08. ~75%.
- **C2** fresh refit slope b (OLS, bootstrap CI over rules, 2000, seed 20261019) contains census b. ~65%.
- **C3** naive-loop test: census b outside [0.85, 1.15] (i.e. naive picture rejected). ~85%.
- **C4** residual structure: after lead, the next letters matter. Census, random half split (seed 20261019): lookup on first 4 letters, fitted on
  half A, scored on half B, held-out R^2 for ln c >= 0.92 (lead-only ~0.84), and a prefix-6 lookup adds <= +0.02 beyond prefix-4. ~55%.
Script `scripts/c_law.py`.

## Stage 3 results (run 2026-10-19 ~09:35, commit 3f23de3, seed 20261019; `results/c_law.{txt,json}`)

Census fit (stationary blob, n = 2185): **1/c = 1.363 + 0.696 lead**. Fresh (kept + stationary, n = 176, lengths 13-14, not used in the fit):

| pred | outcome |
|---|---|
| C1 R^2 >= 0.75, median rel err <= 0.08 | **HELD**: R^2 0.877, median |rel err| 0.041. Per-lead means track within 0.02 (0.504/0.371/0.300/0.247/0.208/0.186 observed vs 0.486/0.363/0.290/0.241/0.206/0.181 predicted) |
| C2 fresh b CI contains census b | **HELD**: fresh 1/c = 1.335 + 0.683 lead, b CI [0.658, 0.707] vs 0.696 |
| C3 census b outside [0.85, 1.15] | **HELD** (b = 0.696): the naive 2x2-loop picture (a = 0, b = 1) is rejected |
| C4 prefix-4 lookup R^2 >= 0.92 and prefix-6 adds <= 0.02 | **FAILED**: held-out R^2 of ln c is 0.842 lead-only, 0.845 / 0.887 / 0.924 / 0.950 for prefix 4 / 5 / 6 / 8 lookups. Information keeps accumulating with each early letter; no sharp cutoff at 4 |

Exploratory, unregistered (`scripts/c_explore.py`, `results/c_explore.txt`): a linear model of 1/c on pairwise alignments
s_0 s_j of the first K letters is worse than the single lead (fresh R^2 0.81 vs 0.877), with weights decaying as
0.64, 0.36, 0.24, 0.09, 0.02: the run structure (a chained product) matters, not pairwise alignment.

## Status and verdict (2026-10-19)

- The registered **kappa** hypothesis (the opening run, as a fresh-ground chiral edge layer, raises kappa) is **refuted** at the census scale: within a necklace at fixed cyclic content the lead slope is ~0 (all blob) or 0.044 (stationary, a quarter of the cross-section); the cyclic-maximum-run alternative also fails (wrong sign).
- Reinterpretation the data support: the opening run **sets the birth rate c almost deterministically** (1/c = 1.36 + 0.70 lead, out-of-sample R^2 0.88). Because dA/dt = c kappa P/A, a higher lead slows growth without, on average, changing kappa. The earlier "lead effect on kappa" is a conditional-on-ln A(22) effect (census-wide kappa vs lead R^2 = 0.001). Whether it is residual structure from conditioning on a variable that lead itself drives (here via c) or a genuine fixed-area effect is NOT decided; the M3 result of the leading-run experiment (shortening the lead lowers ln kappa at unchanged area) still stands.
- Unexplained: why b ~ 0.70 and a ~ 1.36 (not 1 and 0), why c keeps gaining from letters 4-8, and the fact that kappa >~ 1 for lead >= 6 (small n: 22, 6, 4).
- Not done: Stage 2 sparse-background dose-response (gated on N1, which failed). It would still be the cleanest way to ask whether c's lead dependence really is a fresh-ground effect: prediction would be b falling toward 0 as background density rises. Not registered.

## Follow-up (added 2026-10-19, after the close of this experiment)
The open items above (mechanism of a ~ 1.36 and b ~ 0.70, the unregistered sbg dose-response, and whether the kappa shift at fixed ln A22 is real) were taken up in
`experiments/archive/2026-10-c-law-mechanism` (own registrations, results and notebook). Nothing registered or reported here is changed by it.
