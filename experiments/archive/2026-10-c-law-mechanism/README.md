# Mechanism of the c law: why 1/c = 1.36 + 0.70 lead, and what it implies for kappa

Continues `experiments/archive/2026-10-kappa-chiral-edge` (kappa chiral-edge hypothesis refuted; the opening same-letter
run "lead" sets c, the fraction of boundary steps that open a new cell). Base commit `f0b96b7`. Notation: rule letters
`s_0 s_1 ...`; colour `k` turns by `s_k`; lead `m` = length of the opening run of equal letters; a *boundary step* is a
step that starts on a visited cell with >= 1 unvisited 4-neighbour (as in `src/probe.rs`, which includes the rims of inner
holes); a *birth* is a step onto a never-visited cell; c = births / boundary steps.

## Stage 1 (registered 2026-10-19 18:50 (+13:00), before any aggregate of `edgestats_sample.csv`)

### Seen before registering (disclosure)
One row group of `experiments/archive/2026-10-edge-statistics/results/edgestats_sample.csv` (rule RRRLRRLLLLR: colours 1, 2 turn R like
colour 0 and have ~2000 edge steps with ~5 births each; colour 3, the first L, has 1310 edge steps and 1296 births), the old
`c_letters.txt` / `c_model.py` (pooled chirality model), and the previous experiment's c-law numbers. Nothing aggregated.

### Hypothesis (mechanism)
Fresh ground at a growing edge is circled by the ant on cells that are still young. While the cell colour is in
`0..m-1` the turn is `s_0` (the *circulating* reads), the ant keeps going round a loop whose outside is fresh and enters
nothing; the first read of the opposite letter (colour `m`) sends it into the fresh ground (a birth). Boundary-step
bookkeeping: `1/c = sum_k r_k` with `r_k` = boundary steps that start on colour-`k` cells per birth (an identity, used as an
instrument check only). The claim is about the **shape of r_k**: `r_0 ~ 1`; `r_k` flat at a plateau `rho` for the
circulating colours `1..m-1`, with `rho` equal to the lead slope `b`; so the lead's linear cost is the per-read cost
of circulating reads, not a shift of the post-lead tail. `a` (1.36) then collects `r_0`, the killing read and the tail.
Linearity of 1/c in lead out to lead 8 (known from the previous experiment) is a **constraint** any model must meet, not a
prediction: a geometric-survival model `r_k ~ phi^k` would saturate and is already excluded.

### Data and frozen choices
- Profile data: `experiments/archive/2026-10-edge-statistics/results/edgestats_sample.csv` (300 rules; per rule and colour: edge
  steps, new cells, ahead/left/right fresh; last octave of a blank-board run; the producing `examples/edgestats.rs` is in
  the repo, the K used is **not recorded**, see G0). Rules joined to `probe_summary.csv` (census) by string.
- Sets for the profile claims: sample rules with `cls == blob`, `c > 0`, `|g_k| < 0.05` ("stationary blob", as in `c_law.py`),
  lead from the rule string (uncapped here; capped at 6 where a regression is stated).
- Forward model scoring is frozen to `c_law.py`: census = stationary blob rows of `probe_summary.csv` (n = 2185), random half split
  `np.random.default_rng(20261019).permutation` (A fit, B score), and the 176 fresh rules of
  `experiments/archive/2026-10-kappa-leadrun-fresh/results/fresh_rules.csv` (kept & stationary, lengths 13-14) for out-of-sample.
  Baselines to beat: lead-only ln c held-out R^2 0.842 (split B), lead law fresh R^2 0.877, `c_model.py` pooled chirality
  (about 0.66 in its own held-out set), prefix-8 lookup 0.950 (an overparameterised ceiling, not a model).

### Predictions
**G0 calibration (instrument gate).** For sample rules also in the census, Pearson r(c_edge, c_census) >= 0.95 and median
|relative difference| <= 0.06, where `c_edge = sum new_cells / sum edge_steps` per rule. If it fails the sample's numbers
are reported as offset and nothing is concluded from them; the profile is then re-measured with the Stage 2 tracer.
- **D1 (where births happen).** Rules with `2 <= m < n`: median over rules of the fraction of births at colours `1..m-1`
  is <= 0.05, and the fraction at colours `{0, m}` is >= 0.70. ~65% (one rule seen).
- **D2 (flat plateau).** Rules with lead `m >= 4`: the median over rules of `max_k r_k / min_k r_k` over `k = 1..m-1` is <= 1.35,
  the pooled mean of `r_k` over those rules and `k` lies in [0.55, 0.85], and is within 0.10 of the census b (0.696). ~55%.
- **D3 (decomposition of the slope).** Over stationary blob sample rules, regress `Lpart = sum_{k<m} r_k` and
  `Tpart = sum_{k>=m} r_k` separately on `min(m, 6)`: slope of Lpart in [0.55, 0.85] and |slope of Tpart| <= 0.15, i.e. at least
  80% of b is carried by the lead reads themselves. ~60%.
- **D4 (killing read).** Rules `2 <= m < n`: median of births/edge_steps at colour `m` >= 0.85. ~65% (one rule seen: 0.99).
- **D5 (colour-0 read).** Median over rules of births/edge_steps at colour 0 lies in [0.45, 0.55] (random-heading value 1/2). ~65% (one rule seen: 0.51).

**Forward model K3 (3 parameters + letters up to 12).** `1/c = e + rho * sum_{k=1}^{min(n-1,12)} prod_{j=1}^{k-1} phi_j`, with
`phi_j = 1` if `s_j == s_0` (circulating) and `phi_j = psi` otherwise (a killing read thins the surviving cells).
(e, rho) by OLS and psi by grid in [0, 1] (step 0.01) on half A; ln-c R^2 scored on half B; then refit on the full census and
score c on the 176 fresh rules.
- **K3-1** held-out R^2 of ln c on B >= 0.90 and >= lead-only (0.842) + 0.04. ~40%.
- **K3-2** fresh R^2 (c) >= 0.90 (lead law 0.877). ~35%.
- **K3-3** fitted `psi < 0.7`. ~60%.
A pass means a few-parameter survival kernel carries most of the information of the 8-letter prefix lookup; a fail
(especially K3-1) means the tail depends on the letters in a way a run/kill kernel does not capture and is reported as such.

### Commands (WSL, repo root)
```bash
uv run experiments/archive/2026-10-c-law-mechanism/scripts/stage1_profile.py   # G0, D1-D5 -> results/stage1_profile.{txt,json}
uv run experiments/archive/2026-10-c-law-mechanism/scripts/stage1_k3.py        # K3 -> results/stage1_k3.{txt,json}
```

## Stage 1 results (run 2026-10-19 ~19:05-19:25, commit f0b96b7 + uncommitted scripts; `results/stage1_profile.{txt,json}`, `stage1_k3.{txt,json}`, post hoc `stage1_explore.txt`)

G0 **PASS**: 259 sample rules in the census, corr(c_edge, c_census) 0.988, median |relative difference| 0.0041. (The K of the sample run is still not recorded.)
Stationary blob sample: 207 rules (leads 1:120, 2:39, 3:29, 4:12, 5:3, 6:3, 10:1; n for D2 is only 19 and for lead >= 5 is 7).

| pred | outcome |
|---|---|
| D1 births at circulating colours <= 5%, at {0,m} >= 70% | **FAILED**: circulating share median 0.142; {0,m} share 0.790 passes |
| D2 flat plateau | **FAILED** (all three needed): max/min median 1.371 (> 1.35), pooled mean 0.798 (in range), 0.102 from b (> 0.10) |
| D3 Lpart slope in [0.55, 0.85], \|Tpart slope\| <= 0.15 | **FAILED narrowly**: Lpart 0.864 [0.79, 0.99], Tpart -0.151 [-0.19, -0.12]; total 1/c = 1.348 + 0.713 m |
| D4 births/edge at colour m >= 0.85 | **FAILED**: median 0.516 (the one rule seen, 0.99, was unrepresentative) |
| D5 colour-0 birth probability in [0.45, 0.55] | **HELD**: median 0.530, IQR [0.513, 0.564] |
| K3-1 held-out R^2(ln c) >= 0.90 and +0.04 | **FAILED**: 0.875 (lead-only 0.842) |
| K3-2 fresh R^2(c) >= 0.90 | **HELD**: 0.913 (lead law 0.877), median rel err 0.031 |
| K3-3 psi < 0.7 | **HELD**: psi 0.16, e 1.12, rho 0.69 |

What the data show (post hoc `stage1_explore.txt`, n = 120/39/29/12 rules for leads 1-4): births equal toward-side-fresh exactly; about 52% of births
are colour-0 reads (immediate continuations of a birth), independent of lead; the killing read (colour m) carries 29-36% of births with
birth probability ~0.55; circulating reads at colours 1..m-1 carry the rest of the lead cost and their share r_k *decays* (~0.88 per read) with r_1 rising with m
(0.72, 0.85, 0.895, 0.889). The registered picture "flat plateau of circulating reads whose height equals b" is wrong in detail.

## Stage 2 (registered 2026-10-19 18:41 (+13:00), before running the tracer on any list)

New instrument: `src/edge_trace.rs` (`trace`, `trace_blank`), driver `examples/c_law_mechanism_trace.rs`. Property tests `tests/edge_trace.rs` check the tracer against
(a) `probe_walker`'s last-octave window (births, boundary steps, fresh neighbours, area, perimeter: exact equality) for ants, `SparseBgAnt`, rotor, random walk and
(b) a naive HashMap re-implementation of every field (per-colour tallies, lag, N_b resolved/censored, chains) incl. a prefilled torus; a deliberate one-line mutation
(lag + 1) was caught by all five tests. The window is the last half of the run (the probe's last octave of 2^24 steps), board 4096 x 4096 for the blank mode.
Frozen lists (`scripts/make_lists.py` -> `results/lists/`): `sample.txt` (207 stationary blob edgestats rules), `calib.txt` (rotor seeds 1-32, rw seeds 1-32),
`valid_candidates.txt` (600 random primitive rules, n uniform in 11..16, seed 20261020, canonical s_0 = R, none in the census, edgestats or fresh sets),
`band.txt` (12 census stationary blob rules per lead 1..5, 10 <= n <= 14, seed 20261019).
Commands (WSL, repo root; `T=./target/release/examples/c_law_mechanism_trace`, build with `cargo build --release --example c_law_mechanism_trace`):
```bash
$T blank 24 4096 < results/lists/calib.txt           > results/trace_calib.jsonl
$T blank 24 4096 < results/lists/sample.txt          > results/trace_sample.jsonl
$T blank 24 4096 < results/lists/valid_candidates.txt > results/trace_valid_raw.jsonl
$T band 30 256 1024 512 20261019 < results/lists/band.txt > results/trace_band.jsonl
```
Validation filter, frozen: keep a candidate if not escaped, births >= 200 and 1.3 <= area/area_t0 <= 1.9 (blob-like growth; 2^(2/3) = 1.59). Band filter, frozen: keep a rule if births in the window >= 5000
and area at the end < 262144 - 2000 (band not exhausted; the initial prefilled area is 131072).

### Predictions (probabilities are my honest odds)
- **T0 calibration (instrument).** (a) rotor, 32 seeds: mean c in [0.47, 0.52], between-seed sd <= 0.03 (notes/calibration.md: 0.498). (b) random walk, 32 seeds: mean c in [0.40, 0.48] (notes: 0.44).
  (c) the 207 sample rules: median |c_trace / c_census - 1| <= 0.06, none escaped. ~75%, ~70%, ~85%.
- **L1 (loop picture).** Rules with m >= 3: pooled over boundary reads at colours 1..m-1 that have a prior read, the fraction with lag exactly 4 is >= 0.60. ~55%.
- **L2.** Rules with m >= 2: of boundary reads at colour m (with prior read), fraction with lag 4 >= 0.50. ~50%.
- **L3.** r_1^{(4)} := (colour-1 boundary reads with lag 4) / births. The excess of r_1 between leads >= 2 and lead 1 (means over rules) is carried >= 70% by lag-4 reads. ~50%.
- **C1 (chains are geometric).** Pooled over sample rules with m <= 4: q_L = P(chain >= L+1 | chain >= L): q_1 in [0.45, 0.58], |q_2 - q_1| <= 0.10 and |q_3 - q_1| <= 0.10. ~50%.
- **N1 (Little's law).** Per rule, E[N_b] (resolved + censored cells born in the window) vs 1/c: median |ratio - 1| <= 0.15, and the slope of mean E[N_b] on min(m, 6) within 0.15 of the slope of 1/c (0.713). ~55%.
- **K4 transition kernel** (defined now, parameters are fitted, not predicted): `1/c = e + sum_{k=1}^{min(n-1,12)} prod_{j=0}^{k-1} phi(t_j)`, where `t_j` is the pair (type s_j, type s_{j+1}) with type C if the letter equals s_0 else K;
  phi in {CC, CK, KC, KK} (5 free numbers). Fit by least squares on 1/c over the full census (for B scoring: on half A). Built after seeing the Stage 1 profile (so it is informed by it, not blind).
- **V validation (new rules, tracer c, filter above).** Compare, with census-fitted parameters, the lead law (1.363 + 0.696 min(m,8)), K3 and K4 on R^2(c) and median relative error.
  **V1** lead law R^2 >= 0.80 on V (~65%). **V2** K3 >= lead law + 0.02 (~55%). **V3** K4 >= 0.90 and >= K3 + 0.01 (~40%). **V4** K4: phi_CC in [0.80, 1.0] and phi_CK <= phi_CC - 0.10 (~50%).
  **K4-census** K4 fit on A, held-out R^2(ln c) on B >= 0.90 (~45%).
- **Flat band (torus 256 x 1024, fresh rows 0..511, interior i.i.d. uniform colours 0..n-1 pre-visited, 2^30 steps, window = second half).** Regress 1/c_band on min(m,5) over kept rules:
  **S1** slope in [0.55, 0.85] (~45%). **S2** intercept in [1.0, 1.7] (~45%). **S3** across kept rules R^2(c_band, c_census) >= 0.60 (~50%). **S4** median births/edge at colour 0 in [0.45, 0.58] (~60%).
  **S5** (direction) median c_band / c_census > 1: a flat front has no hole rims, which add boundary steps without births (~55%).
  Reading: S1-S3 hold => the law is a local flat-edge property independent of the ant-built bulk and of curvature; S1/S2 off but S3 holds => geometry shifts a and b but rank order is local;
  S3 fails => bulk memory of the ant-built field matters. No claim of an exact flat-edge solution is made; the band is a Monte-Carlo stand-in with a finite i.i.d. interior.

**Erratum on timestamps (added 18:42, +13:00).** The Stage 1 registration header says 18:50 and the NOTEBOOK entries from 18:34 on carry times I estimated rather than read from the clock;
the wall clock at 18:40 shows they run ahead of real time by up to ~1 h. The *order* of events is as written (Stage 1 registered before `edgestats_sample.csv` was aggregated; Stage 2 registered
before any tracer list was run). Real clock readings were: session start 18:30, Stage 2 registration 18:41. From here on times are read from `date`.

## Stage 3: sparse-background dose-response (registered 2026-10-19 18:45 (+13:00), before any `sbg` run; Stage 2 band run still in progress, no Stage 2 result seen yet)

Question: is the lead dependence of c a fresh-ground effect? `SparseBgAnt` (tested in `tests/sparse_bg.rs`, and traced exactly by `tests/edge_trace.rs`): each cell starts, with probability `d`,
in a uniform non-zero colour in 1..n-1, else blank. A born cell that starts at colour j reads the rule rotated by j, so at `d = 1` no cell is ever read at colour 0 on its first visit.
Design (frozen): the 60 band rules (`results/lists/band.txt`, 12 census stationary-blob rules per lead 1..5, 10 <= n <= 14); densities d in {0, 0.02, 0.05, 0.1, 0.2, 0.4, 0.7, 1.0};
background seeds 1..4 (d = 0: seed 1 only; `sbg:RULE:SEED:0` is the blank ant); `blank 24 4096` tracer, same window as Stage 2 (1920-ish runs, spec `sbg:RULE:SEED:DENS`).
A run is **kept** if not escaped, births >= 200 and 1.3 <= area/area_t0 <= 1.9 (as in V). c per (rule, d) = mean over kept seeds, needing >= 2 kept seeds (d = 0: 1).
**Primary cohort (survivor control):** rules kept at *every* density; secondary: all kept cells at each d. I report kept fraction by lead and d. Lead = min(lead, 5).
Per d: OLS of 1/c on lead gives a(d), b(d); bootstrap over rules (2000, seed 20261019).
**Parameter-free mixture prediction (locality):** 1/c_pred(R, d) = (1-d) (1/c)_census(R) + d mean_{j=1..n-1} (1/c)_census(rot_j R), rot_j R = R[j:] + R[:j] mirror-canonicalised (swap L/R if it starts with L);
census = blob rows with c > 0; rotations missing from the census are dropped and a rule needs >= half of its n-1 rotations to be predicted.
This is the prediction that a born cell's reads depend only on its own read sequence (neighbours' phases irrelevant).

### Predictions
- **B1** `b(1.0) / b(0) <= 0.25` in the primary cohort (lead stops mattering when no cell is read at colour 0). ~65%.
- **B2** b(d) is non-increasing along the grid within +0.07 per step. ~70%.
- **B3 (mixture)** over primary-cohort cells with d >= 0.1 and a prediction: R^2 of observed vs predicted 1/c >= 0.50 and median |relative error| of 1/c <= 0.20. ~40%.
- **B4 (floor)** the intercept a(d) stays in [1.0, 2.0] at every d: a birth's own first read is always a boundary read, so 1/c cannot fall toward 0 (the intercept does not "fall to zero" even if the slope does). ~80%.
- **B5 (selection, descriptive with threshold)** the kept fraction at d = 1 is lower for lead >= 4 than for lead <= 2 by >= 0.10. ~35%.
Reading: B1+B2 hold => the lead slope is a fresh-ground effect; B3 holding on top means the effect is local to each cell's own read sequence (a single-cell mechanism); B3 failing with B1 holding means the
slope is fresh-ground but neighbours' phases matter (loops are collective and break when mixed). B1 failing => the lead slope is not (only) a fresh-ground effect.
Commands (WSL, repo root): `bash experiments/archive/2026-10-c-law-mechanism/scripts/run_stage3.sh` then `uv run experiments/archive/2026-10-c-law-mechanism/scripts/stage3_analyse.py`.

### Deviation to Stage 2 flat band (added 18:50 (+13:00), before any band c(m) was computed; see NOTEBOOK)
The registered band run (2^30 steps, window = second half) consumed every band before the window opened (void; file kept as `results/trace_band_2e30_void.jsonl`), so S1-S5 were untested.
Replacement, frozen before reading any band c: run L = 24..29 (`scripts/run_band.sh` -> `results/trace_band_L{L}.jsonl`), per rule use the smallest L whose end-of-run band consumption
`(area - 131072)/131072` is >= 0.5; keep the rule if that consumption is <= 0.9 and births in the window >= 5000. Predictions S1-S5 and their thresholds are unchanged.
A pilot on three non-band sample rules (`scripts/band_pilot.sh`) was used only to see the consumption time scale (about 2^25-2^27, 3x between rules).
Also: T0b was run at 2^20 steps (the registered 2^24 escaped the 4096 board for all 32 random walks); C1 was registered as geometric chains and failed (chains have length <= 3).

## Stage 2 results (run 2026-10-19 18:41-18:50, commit f0b96b7 + uncommitted working tree; `results/stage2_analysis.{txt,json}`)

| pred | outcome |
|---|---|
| T0a rotor c in [0.47, 0.52], sd <= 0.03 | **HELD**: 0.4977, sd 0.0007 (32 seeds, 2^24, none escaped; notes: 0.498) |
| T0b random walk c in [0.40, 0.48] | **HELD** at the deviated configuration (2^20 steps): 0.4480, sd 0.0062; all 32 runs at the registered 2^24 escaped the 4096 board |
| T0c sample median \|c_trace/c_census - 1\| <= 0.06, no escapes | **HELD**: 0.0026, 0 escaped (207 rules) |
| L1 lag-4 fraction of circulating reads >= 0.60 | **HELD**: 0.784 (47 rules with m >= 3, 1.90M reads); other lags 8: 0.057, 12: 0.032; all lags even |
| L2 lag-4 fraction at colour m >= 0.50 | **FAILED**: 0.483 (744k reads) |
| L3 >= 70% of the r_1 excess (lead >= 2 vs 1) is lag-4 reads | **HELD**: r_1 0.723 vs 0.879, 93% lag-4 |
| C1 chains geometric | **FAILED**: q_1 0.779, q_2 0.455, q_3 0.000; no chain is longer than 3 (4.36M chains; P(len 1,2,3) = 0.22, 0.43, 0.35, mean 2.13) |
| N1 Little: median \|E[N_b]/(1/c) - 1\| <= 0.15 and slope within 0.15 | **HELD**: 0.016 (median ratio 0.984); slopes 0.700 vs 0.712 |
| K4-census held-out R^2(ln c) >= 0.90 | **FAILED**: 0.863 (K3 0.875, lead-only 0.842) |
| V1 lead law R^2 on V >= 0.80 | **FAILED**: 0.711 (n = 378 of 600; median rel err 0.066) |
| V2 K3 >= lead law + 0.02 | **HELD**: 0.785 (+0.074; median rel err 0.042) |
| V3 K4 >= 0.90 and >= K3 + 0.01 | **FAILED**: 0.800 |
| V4 phi_CC in [0.8, 1], phi_CK <= phi_CC - 0.1 | **FAILED**: phi = (CC 0.916, CK 1.2 [at the bound], KC 0.103, KK 0.072), e 0.574 |
| S1 band slope in [0.55, 0.85] | **HELD**: 0.678 |
| S2 band intercept in [1.0, 1.7] | **HELD**: 1.399 |
| S3 corr^2(c_band, c_census) >= 0.60 | **HELD**: 0.999 |
| S4 median colour-0 birth probability in [0.45, 0.58] | **HELD**: 0.522 |
| S5 median c_band/c_census > 1 | **FAILED**: 0.998 |
(Deviations: T0b configuration; the void 2^30 band run replaced by the frozen L-selection rule; see above and the NOTEBOOK.)

## Stage 2c: ablation of the band interior (registered 18:52 (+13:00), before running)
Result S3 (rule-by-rule agreement to 0.2%) is almost too clean, so it gets a control that can break it. Same 60 rules, the same per-rule L chosen in the main band run (frozen from `stage2_analyse.py`, printed in `stage2_analysis.txt`),
same torus, but the pre-visited interior colours are drawn differently (driver `band` mode with a 7th argument):
**Z** all interior cells colour 0; **Y** i.i.d. uniform over colours 1..m (m = the rule's lead; the young colours); **H** i.i.d. uniform over colours m..n-1 (old/killing side). The U (uniform 0..n-1) run is the main band run.
- **A1** median |c_Z / c_U - 1| <= 0.05. ~45%. **A2** same for Y. ~45%. **A3** same for H. ~45%.
- **A4** In every interior variant the fitted slope of 1/c on min(m,5) stays within [0.55, 0.85]. ~55%.
If A1-A3 all hold, the interior's colours are irrelevant and c is a property of the rule on fresh ground. If one fails, the entry cell's (old cell's) colour distribution enters c, which would be the route by which letters beyond the lead matter.
Kept rules: the same 60 (consumption in the window may differ with the interior; I report the consumption and births; a rule is dropped from a variant only if the band is >90% eaten or < 5000 births, as before).

### Stage 3 deviation (added 19:00 (+13:00), after seeing kept/escape fractions only; no c(d) computed yet)
At d >= 0.7 almost every run escapes the 4096 board in 2^24 steps (kept 0.00-0.08 at d = 0.7, 0.00-0.02 at d = 1.0; at d = 0.4 kept 0.40-0.75, lead 1 escaping 50%). The registered primary cohort (valid at every d) is empty and B1 is untestable as registered.
Replacements, frozen before any c(d) is computed: primary cohort = rules valid at every d <= 0.2; secondary = d = 0.4 survivors (selection-biased, reported separately).
**B1'** for d in {0.1, 0.2}: |b_obs(d) - b_mix(d)| <= 0.10, where b_mix is the slope of the mixture prediction on lead at that d. **B2'** b(d) non-increasing within +0.07 along d <= 0.2. **B3'** mixture R^2 >= 0.50 and median |rel err| <= 0.20 on cells d in {0.1, 0.2}.
**B4'** intercept in [1.0, 2.0] for d <= 0.2 (and, secondary, at 0.4). **B5** reported at d = 1.0 (as registered) and at d = 0.4.

## Stage 3 results (run 2026-10-19, commit b7b4758; `results/trace_sbg.jsonl`, `stage3_analysis.{txt,json}`)
Primary cohort: 60 rules, valid at every d up to 0.2. 1/c = a + b lead (b CI over rules): d=0: 1.397 + 0.677 [0.646, 0.711]; 0.02: 1.439 + 0.646; 0.05: 1.489 + 0.605; 0.1: 1.537 + 0.549 [0.513, 0.583]; 0.2: 1.619 + 0.450 [0.412, 0.485].
Secondary, d=0.4 survivors (46 rules): 1.331 + 0.689 at d=0 on the same rules; 1.729 + 0.287 [0.235, 0.341] at d=0.4. Mixture-predicted slopes (census rotations): 0.678, 0.665, 0.645, 0.613, 0.548.

| pred | outcome |
|---|---|
| B1 b(1.0)/b(0) <= 0.25 | **NOT TESTABLE**: at d >= 0.7 the ant leaves the board in 88-100% of runs (kept 0-8%); no blob regime to measure c in |
| B1' abs(b_obs - b_mix) <= 0.10 at d = 0.1, 0.2 | **HELD** (0.064, 0.098; the observed slope falls faster than the mixture, the second barely passes) |
| B2' b(d) non-increasing within +0.07, d <= 0.2 | **HELD**: 0.677, 0.646, 0.605, 0.549, 0.450 |
| B3' mixture R^2 >= 0.50 and median rel err <= 0.20 (d = 0.1, 0.2) | **HELD**: R^2 0.869, 0.067 (120 cells). Null "no density effect": 0.613, 0.102 |
| B4' intercept in [1.0, 2.0] | **HELD**: 1.40-1.73 (rises, does not fall) |
| B5 kept fraction lower for lead >= 4 by >= 0.10 | **FAILED** at d = 1.0 (0.00 vs 0.01) and at d = 0.4, where the sign is opposite (0.48 for lead <= 2 vs 0.68 for lead >= 4) |

## Stage 4: reconcile with kappa (registered 2026-10-19 19:03 (+13:00), before any Stage 4 computation)

Definitions. kappa = (boundary steps / steps) / (perimeter / area); growth identity dA/dt = c kappa P/A. So c (births per boundary step) and kappa (boundary occupancy) are different factors of the area growth rate, and
ln A22 depends on both: if A ~ (c kappa t)^g (g about 0.68 from A^(2-beta) ~ c kappa t with beta ~ 0.52), then ln A22 is a **collider** of (ln c, ln kappa). Lead moves ln c strongly (slope about -0.24 per step) and, in the census, does not move ln kappa
(marginal R^2 0.001). Conditioning on ln A22 then induces a positive lead effect on ln kappa of size about 0.24 g beta_(kappa|A) ~ 0.24 x 0.68 x 1.0 ~ +0.17 per step with no direct effect at all (observed +0.15). This is a
hypothesis, not a result: it is what I am about to test. What I have seen: the leading-run README numbers (pooled b = +0.158, c-coefficient 1.037, arm means E -0.062, S -0.198, C -0.006 with dA -0.292, +0.013, 0.000) and the first-experiment summary; I have not
computed anything below.

### 4a: collider check on the 176 fresh rules (existing data, no runs)
Data: `experiments/archive/2026-10-kappa-leadrun-fresh/results/fresh_rules.csv` (kept and stationary, n = 176). Y = lnk, Z = ln c, W = lnA22, X = min(lead, 6). Fit W = alpha + g_c Z + g_k Y + e. Permutation null (2000 draws, seed 20261019):
permute Y across rules, rebuild W* = alpha + g_c Z + g_k Y_perm + e (each rule keeps its residual), regress Y_perm on 1, X, W*. H0 built in: Y independent of X and Z; the only link of Y to the rest is through W.
- **Q1** the observed coefficient on X in OLS Y ~ 1 + X + W lies inside the null's central 95% interval and |mean(null) - observed| <= 0.05. ~50%.
- **Q2** the same for the coefficient on W: |mean(null) - observed| <= 0.25. ~50%.
- **Q3** adding Z: OLS Y ~ 1 + X + W + Z gives a coefficient on X with |b| <= 0.07 or a bootstrap CI (2000, over rules) containing 0. ~60%.
Q1 and Q3 both holding means the "lead raises kappa at fixed area" association is reproduced by conditioning on a collider with no direct effect; Q1 failing (null << observed) means a direct fixed-area effect is needed.

### 4b: growth identity on the Part B mutant pairs (no new kappa runs)
c for bases and Part B mutants is measured by the Stage 2 tracer on the blank board (2^24 steps, window = last octave; deterministic; rules in `results/lists/s4_trace_rules.txt`). With pairs from `experiments/archive/2026-10-kappa-leadrun-fresh/results/mutant_pairs.csv`
(kept and stationary, 257 pairs): d = d ln kappa, dA = d ln A22, dc = d ln c (tracer). Fit dA = g (dc + d) + noise through the origin on all pairs.
- **Q4** g in [0.5, 0.9], and the arm means of g (dc + d) are within 0.08 of the observed mean dA for each of E, S, C. ~50%.
This is an identity-level check that the E/S asymmetry in dA (unexplained in the leading-run write-up) comes from the c law: E lowers c by about 0.24 per added lead step while d is about 0, S raises c while d is negative.

### 4c: lead-preserving early flips (the P1 proposal, now registered)
Bases: the 157 stationary fresh rules with lead k in 1..5 (same as Part B). Mutants: flip the single letter at index k+1 (arm **P1**) and at index k+2 (arm **P2**), when that index < n - 1; the lead stays k. Dropped if not primitive or already seen.
Run with the unchanged pipeline: `probe 27 8192` on `RULE@SEED`, seeds 601..608, core band alpha_w in [0.25, 0.42], kappa > 0, >= 6 core runs, stationary |g_k| < 0.05 (same as Part B); paired with the base's existing row. d = ln kappa(mutant) - ln kappa(base), dA, and tracer dc.
Statistics: mean d with a **cluster bootstrap over bases** (a base contributes both its mutants; 2000, seed 20261019); area-adjusted residual r = d - beta_hat dA with beta_hat from the pooled regression d ~ 1 + dA.
- **P-1 (lead is the active factor)** |mean d| <= 0.08 and its 95% CI inside [-0.15, 0.15]. ~40%.
- **P-2 (early position/composition, not lead)** mean d <= -0.10 with the CI upper bound < -0.03 (the M3-like drop appears with the lead untouched). ~35%. (P-1 and P-2 are exclusive; ~25% is "neither".)
- **P-3** area-adjusted mean residual within +/-0.08 of 0. ~45%.
- **P-4** over P pairs, dA = g (dc + d) has g in [0.4, 1.0] and R^2 >= 0.5. ~50%.
- **P-5** retention (kept and stationary mutants / mutants) reported against Part B's 0.53-0.68; descriptive. Dropout is a limit on every claim here.
Reading: P-1 holding says an early flip that leaves the lead alone does nothing, so M3 (S arm) is a lead effect (but still one-sided: E showed none); P-2 holding says M3 was an early-letter effect that any early flip produces and the lead has no special role.
No causal claim beyond these two arms and these 157 bases; the intervention changes letters, not the "lead" in isolation, and I say so in the write-up either way.
Commands: `uv run experiments/archive/2026-10-c-law-mechanism/scripts/stage4_lists.py`, tracer on `s4_trace_rules.txt`, `bash experiments/archive/2026-10-c-law-mechanism/scripts/run_p1.sh` (probe), `uv run experiments/archive/2026-10-c-law-mechanism/scripts/stage4_analyse.py` (needs `dumps/p1_probe.done`; exits without writing if absent).

## Stage 4 results (run 2026-10-19; `results/stage4_analysis.{txt,json}`, `results/p1/`)
| pred | outcome |
|---|---|
| Q1 observed conditional lead coefficient inside the no-direct-effect null | **HELD**: observed +0.148, null mean +0.145 [+0.137, +0.153] (176 fresh rules) |
| Q2 area coefficient within 0.25 | **HELD**: +1.073 vs null +1.035 |
| Q3 adding ln c removes the lead coefficient | **HELD**: +0.014 [-0.045, +0.062]; growth fit ln A22 = 11.45 + 0.687 ln c + 0.807 ln kappa, residual sd 0.092 |
| Q4 growth identity on Part B pairs | **HELD**: g = 0.805; arm dA observed/predicted E -0.292/-0.318, S +0.013/+0.050, C 0.000/-0.004 (257 pairs) |
| P-1 abs(mean d) <= 0.08, CI in [-0.15, 0.15] | **HELD**: -0.007 [-0.078, +0.060] (177 pairs, cluster bootstrap over bases) |
| P-2 mean d <= -0.10 | **FAILED** |
| P-3 area-adjusted residual within 0.08 | **HELD**: +0.007 [-0.022, +0.034] |
| P-4 dA = g(dc + d), g in [0.4, 1.0], R^2 >= 0.5 | **HELD** (after a NaN fix, see NOTEBOOK): g 0.809, R^2 0.875 |
| P-5 retention | 0.65 (Part B: 0.53-0.68) |
Post hoc, not registered: split by flip direction, L>R d +0.153 (n 98), R>L d -0.207 (n 79), sd of d 0.43; S and E arms are direction-confounded.
Reading: the fixed-area "lead effect" on kappa is a conditioning artefact (4a) with no detectable direct effect (|b| below ~0.06 per step given ln c); lead-preserving early flips shift kappa by zero on average, but single flips move it by about 0.2 in a letter-direction-dependent way, which I cannot separate from lead in the S/E arms. No causal claim that lead sets kappa.

**Erratum (added after the gap review).** Stage 1 says the K of `edgestats_sample.csv` is "not recorded": it is K = 23 (window (2^22, 2^23]), recovered by `scripts/find_edgestats_k.sh`; the Stage 2 tracer window is 2^24. Real clock times and commits for all result files: `results/PROVENANCE.md`.
