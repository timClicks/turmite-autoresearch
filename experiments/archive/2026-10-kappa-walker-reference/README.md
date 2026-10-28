# kappa of the calibration walkers against their own uniform reference

Registered 2026-10-19 (+13), base commit 6de71f2 (dirty workspace from other
experiments; this folder is untracked and self-contained), **before any new run**.

## Question

`experiments/archive/2026-10-kappa-uniform-baseline` showed the probe's kappa for a walker that is
uniform on its territory at every instant is `kappa_unif(a, beta) = 2 * int_{1/2}^{1} x^(-a(1-beta)) dx`
(1.110 at a = 2/3, beta = 1/2), and restated the ant (median census kappa/kappa_unif = 0.81,
5-95% 0.44-1.33, IQR 0.66-0.96, n = 2185 stationary blob rules, single run each). The rotor
(kappa ~2.0) and memoryless walkers (1.3-1.45) were only compared against 1.11, which is
justified only for a ~ 2/3, beta ~ 1/2 (deviation entry 2026-10-16 01:00). Recompute their
ratios with **each walker's own measured (a, beta)**, then ask whether the ant location is ant-specific.

## Prior numbers (from EXISTING data, computed before the new runs)

`scripts/prior_ab.py` on `2026-10-a1-kappa/results/a1d_probe.csv` (pw, 6 seeds) and
`2026-10-calib-instrument-calibration/results/calib_rotor.csv` (rotor, 64 seeds), windows k = 12..22:

| walker | a | beta | kappa | kappa_unif(a,beta) | ratio |
|---|---|---|---|---|---|
| pw:0.25 | 0.891 | 0.882 | 1.254 | 1.033 | 1.21 |
| pw:0.5  | 0.913 | 0.907 | 1.358 | 1.027 | 1.32 |
| pw:0.75 | 0.930 | 0.931 | 1.287 | 1.020 | 1.26 |
| rotor   | 0.724 | 0.564 | 1.856 | 1.104 | 1.68 |

**Correction to the premise in the task/deviation entry.** "Memoryless walkers have a ~ 0.95 and a
reference near 1.16" used the beta = 1/2 column of the formula (a = 0.95 -> 1.159). Their territory
is porous and the perimeter (visited cells with an unvisited 4-neighbour, holes included) scales
as P ~ A^0.9, so a(1-beta) ~ 0.09 and the reference is **~1.02-1.03**, below 1.11, not above.
Recomputing therefore moves the memoryless ratios *up* (1.2-1.3 vs 1.2-1.3 against 1.11: unchanged
to within 0.1), not down.

## Predictions (registered)

New runs, fresh seeds, same probe: ratio_w = kappa_w / kappa_unif(a_w, beta_w), with a_w, beta_w
fitted per seed (log-log, windows k = 12..22) from the same run as kappa (kappa = mean over the
same windows of the per-window kappa, as in `scripts/analyse.py` of the baseline experiment).

1. Memoryless walkers (`pw:0.25`, `pw:0.5`, `pw:0.75`, `rw`): a in 0.88-0.96, beta in 0.86-0.95,
   kappa_unif in 1.01-1.05, ratio in 1.15-1.40 (rw has no prior run in this window; I expect it
   alongside pw:0.5). Between-seed sd of the ratio <= 0.1.
2. Rotor: a in 0.68-0.74, beta in 0.53-0.58, kappa_unif ~1.10, ratio 1.6-1.8 over k = 12..22. Over k = 20..26
   (the window the census uses), kappa ~2.0 and ratio ~1.8; the difference between the two windows
   is reported as the window bias.
3. Mean-field walker (anchor, already measured, not rerun): ratio 1.01 (1.118 / 1.107).
4. Location test. Ant median 0.81, IQR 0.66-0.96, 5-95% 0.44-1.33.
   - **Ant-specific location** is supported if every non-uniform walker's ratio is above the ant
     IQR (> 0.96) by more than 3 between-seed sd, and none lies in 0.66-0.96. I predict this: all
     walkers 1.2-1.8.
   - **Same ratio for all walkers** would be shown by walker ratios inside 0.66-0.96 (the ant IQR).
     I predict this does not happen.
   - **Not discriminating** if some walkers sit in 0.96-1.33. That is inside the ant 5-95% range
     (so "outside the ant range" is the wrong test for those), but above the median. I predict the
     memoryless walkers land here (1.2-1.3) and only the rotor is outside (> 1.33). If so: the
     verdict is that the ant is *lower than every walker tested* and that walkers do not
     discriminate within 0.96-1.33; it says nothing about mechanism.
   - Rule-level caveat: the ant ratios are single run, rule-dependent, noise inflated
     (ln-kappa reliability ~0.6). Only a walker-ratio far from the ant IQR carries weight.

## Design

- `rw`, `pw:0.25`, `pw:0.5`, `pw:0.75`: seeds 2026101901..08, `probe 23 16384` (board 16384, 2^23 steps;
  windows k = 12..22). Escaped windows are dropped and counted; seeds with any escape are reported.
- `rotor`: seeds 2026101901..08, `probe 27 8192`; fit over k = 12..22 and k = 20..26 separately.
- No estimator or fit change relative to the baseline experiment's `analyse.py` (same formulas). A
  secondary, descriptive-only estimate with per-window local (a_k, beta_k) from adjacent window ends
  is also reported, because a single power law is a poor description of porous walkers.

## Commands / results

Filled in as it runs (`NOTEBOOK.md`, `results/`).

## Results (2026-10-19, run at commit 34fbf45; workspace dirty with unrelated changes, no Rust changed)

Commands (WSL, repo root): `bash experiments/archive/2026-10-kappa-walker-reference/scripts/run.sh` (builds `probe`; specs in `results/specs_mem.txt`,
`results/specs_rotor.txt`; seeds 2026101901..08 for each of rw, pw:0.25, pw:0.5, pw:0.75, rotor; memoryless
`probe 23 16384`, rotor `probe 27 8192`; outputs `results/probe_mem.csv`, `results/probe_rotor.csv`),
then `uv run experiments/archive/2026-10-kappa-walker-reference/scripts/analyse.py` -> `results/analysis.txt`. 8 seeds per walker, no escaped windows.
Mean (between-seed sd); a, beta fitted per seed, then averaged.

| walker (windows) | a | beta | kappa | kappa_unif(a,beta) | ratio | vs ant (med 0.81, IQR 0.66-0.96, 5-95 0.44-1.33) |
|---|---|---|---|---|---|---|
| rw (12..22) | 0.920 (.028) | 0.917 (.041) | 1.307 (.030) | 1.024 | **1.28** (.04) | above IQR, inside 5-95 |
| pw:0.25 | 0.903 (.017) | 0.898 (.021) | 1.271 (.027) | 1.029 | **1.24** (.03) | same |
| pw:0.5 | 0.920 (.030) | 0.909 (.037) | 1.350 (.036) | 1.026 | **1.32** (.04) | same, at the 95% edge |
| pw:0.75 | 0.911 (.026) | 0.907 (.027) | 1.287 (.051) | 1.026 | **1.26** (.06) | same |
| rotor (12..22) | 0.730 (.020) | 0.575 (.030) | 1.858 (.039) | 1.102 | **1.69** (.04) | above ant 95% |
| rotor (20..26) | 0.685 (.006) | 0.530 (.026) | 1.989 (.034) | 1.106 | **1.80** (.03) | above ant 95% |
| mean-field (baseline expt) | 0.677 | 0.520 | 1.118 (.009) | 1.107 | 1.01 (.01) | anchor |

The local-exponent reference (per-window a_k, beta_k from adjacent window ends) agrees with the
power-law reference to <= 0.006 in every row (columns in `analysis.txt`).

### Against the registered predictions
1. Memoryless: a 0.90-0.92 (pred 0.88-0.96), beta 0.90-0.92 (0.86-0.95), kappa_unif 1.02-1.03 (1.01-1.05),
   ratio 1.24-1.32 (1.15-1.40), sd <= 0.06 (<= 0.1): **held**.
2. Rotor: a, beta, ratio inside the registered ranges in both windows (1.69 over 12..22, 1.80 over 20..26): **held**.
   Window bias of the ratio between the two windows is 0.11 (rotor a still relaxing towards 2/3).
3. Location test: every non-uniform walker is above the ant IQR (by 5-25 between-seed sd of the walker); none is in
   0.66-0.96. By the registered criterion the ant location is *lower than every walker tested*.
   As registered, the memoryless walkers fall in the not-discriminating band 0.96-1.33 (inside the ant 5-95%
   range; about 20% of ant rules are >= 1); only the rotor is outside the ant range.

### What this does and does not show
- The recomputed ratios: memoryless ~1.25-1.3 (not changed by the correction: their reference is 1.03, not 1.16, because
  beta ~0.9), rotor 1.7-1.8. The ant median 0.81 is not the value a generic walker gets; uniform-on-territory
  (mean-field) is 1.0, and no non-uniform walker tested sits below 1.
- It does not say why. The walkers are above 1 and the typical ant is below 1; the ant range reaches 1.33 and the
  memoryless walkers sit at its top edge, so 'inside the ant range' is a weak statement. Accounting plus a control.
- Caveats: memoryless fits use k = 12..22 (board limits; a ~0.92 is not asymptotic, the census uses later windows);
  the rotor shows the window effect is ~0.1 in the ratio. Ant ratios are single-run and rule-dependent; walker
  ratios are 8-seed means, so the comparison is walker mean vs ant distribution, not like with like.
  Window labelling: probe CSV k is the window end (t = 2^k), the baseline mean-field CSV labels by window start, so
  'k=12..22' there is ends 2^13..2^23; same estimator, different label (corrected in the notebook).
- Next: a walker with the ant's a ~ 2/3, beta ~ 1/2 but intermediate memory (noisy rotor `nrotor:EPS`, Arm B of A1) to
  see where between 1.8 and 1.0 the ratio crosses the ant median; that discriminates 'memory in the environment
  lowers kappa' from 'it is ant-specific', which is not tested here.

## Next steps (detailed; none of these has been run)

Status of the question: the ant median ratio (0.81) is below every non-uniform walker tested
(memoryless 1.24-1.32, rotor 1.7-1.8) and the mean-field walker is 1.0. What is open is where and
why the ratio moves between those walkers and the ants. Each step below is written so that its
prediction can be registered in this README (dated, before the run) and can fail.

### 0. Housekeeping this experiment still owes (do first, small)
- `notebook.ipynb` from `experiments/_template/` (required by AGENTS.md): question, the
  `kappa_unif` formula, provenance cell (commit, sha256 of `results/probe_*.csv` and the two scripts),
  the results table read from `results/analysis.txt`, caveats, next steps. It must run top to bottom
  from a clean kernel under `uv`, reading only committed `results/`. Jupyter is not yet in
  `pyproject.toml`; see `experiments/README.md` for the setup, and mention any `uv add` in the commit.
- Add a short pointer in `notes/open-questions-hypotheses.md` with the correction (memoryless reference
  is 1.03, not 1.16) and the ratio table. That file has uncommitted edits from other work: commit only
  the new hunk (`git add -p`) or ask first.
- Append a new entry to the `2026-10-kappa-uniform-baseline` NOTEBOOK saying its window labels are
  start-of-window while the probe CSV labels by window end. Its numbers are unaffected (own CSV, own
  estimator), but "k=12..22" differs by one octave between the two experiments.
- Find which window the census kappa actually is (`probe_summary.csv`,
  `experiments/archive/2026-10-probe-growth-census`: last octave? which k?) and state it here. The rotor's
  ratio moves by 0.11 between k=12..22 and k=20..26, so the window match matters for every comparison.

### 1. Close the window confound for the memoryless walkers
- Question: is the memoryless ratio window-dependent like the rotor's? At the census window would it be
  nearer 1.1 or nearer 1.4?
- Obstacle: reaching 2^27 steps needs R ~ 35 000 cells, a ~1.2 GB board per walker, which is
  borderline with 6 in parallel. Options, in order of preference: (a) a sparse/hash-set walker used only
  for this control, with a property test against `probe_walker` step-for-step on a small board
  (AGENTS.md rule 4); (b) 2^25 steps on a 16384 board, one walker at a time, windows k=20..24, with
  escapes reported (rms R ~ 5800, some will leave); (c) accept k <= 22 and say so.
- Run: `rw` and `pw:0.5`, 8 new seeds 2026102001..08.
- Prediction to register: ratio at k=20..24 within +-0.1 of the k=12..22 value (1.24-1.32). Falsified if
  the shift exceeds 0.15; the memoryless walkers could then drift into or out of the ant IQR and the
  "above every ant-typical value" statement must be revised.
- Cost: (b) is minutes; (a) is about a day.

### 2. Noisy rotor: locate the ratio between 1.8 and the ant's 0.8 (main discriminating experiment)
- Rationale: `NoisyRotor` (`nrotor:EPS:SEED`, `src/walkers.rs`) interpolates from the rotor (EPS=0,
  a ~ 2/3, beta ~ 1/2, ratio 1.8) to a memoryless walker that never turns back on its own board (EPS=1,
  a ~ 0.9, ratio ~ 1.25). It stays on the a ~ 2/3 branch for small EPS, so `kappa_unif` stays ~1.10 and the
  comparison with the ant is clean. Earlier Arm B work found kappa drifts with EPS (non-stationary; 3-4
  runs per EPS; `notes/frontier-2026-10-13-results.md`), so report the drift `g_k` as well as the level,
  and apply the census stationarity cut (|g_k| < 0.05) before comparing with the ant distribution.
- Design: EPS in {0, 0.01, 0.02, 0.05, 0.1, 0.2, 0.4, 0.7, 1.0}, 8 seeds each, `probe 27 8192`, windows
  k=20..26 (census-matched) and k=12..22 (this experiment). 72 runs; rotor runs took about a minute each.
- Predictions to register: (i) ratio(EPS) is monotone non-increasing from 1.8 towards ~1.25. (ii) The ant
  median 0.81 is not reached at any EPS: the noisy rotor stays >= 1.0. (iii) a(EPS) stays <= 0.75 up to
  EPS ~ 0.1, i.e. the cube-root-like regime survives weak noise (consistent with D3).
- Reading the outcomes: if no EPS gets below 1, neither "remove environment memory" nor "add noise" lowers
  the ratio below 1, and the ant deficit must come from something a rotor cannot do (a deterministic,
  rule-written colour field). If some EPS crosses 0.81 at a ~ 2/3, a stochastic walker reproduces the ant
  median and "ant-specific" is refuted for the location.
- Log, do not hide: runs leaving the board, runs where kappa drifts, and any disagreement between EPS=1
  and `pw:0.5` (their ratios should agree; a mismatch is a code bug, not a finding).

### 3. Calibrate what a ratio means (accounting for the formula itself)
- The `kappa_unif` formula assumes uniform occupancy. Test it where the answer is known by construction:
  a mean-field variant that resamples only from the outer fraction f of the visited cells (by age or by
  distance from the centre), f = 1, 0.5, 0.25, 0.1. f = 1 reproduces the 1.01 already measured.
- Prediction: ratio rises monotonically as f falls, and reaches ~1.8 at some f in 0.1-0.4. This maps a
  ratio r to an effective sampled layer, so the ant's 0.81 reads as "samples a layer wider than uniform
  occupancy implies". It does not assert that the rotor or the ant does this; many occupancy profiles give
  the same ratio.
- Needs a new example named with the slug prefix (`examples/kappa_walker_reference_*.rs`) with the same
  brute-force recount assert as `kappa_uniform_baseline.rs`.

### 4. Ant side: reduce the noise of the ant distribution before comparing
- The ant ratios are single run (ln-kappa reliability ~0.6), so the 0.44-1.33 range is inflated and the
  comparison is walker mean vs ant distribution, which is not like with like.
- Use the 8 patched seeds per rule already held in `2026-10-t1-excursion-tomography` and
  `2026-10-patched-starts`; compute per-rule mean ratios with each rule's own (a, beta) and report the
  distribution of rule means. Prediction: the spread narrows (sd of ln ratio from 0.35 towards 0.25) and
  the median stays 0.8 +- 0.05. If the median moves above 0.96, "ant below every walker" was a single-run
  artefact.
- Split the ants by their own a. Rules with a near 0.9, if any, should be compared with the memoryless
  1.25, not with the a ~ 2/3 rotor. Pre-register the sign of the within-ant slope of ln ratio on a; the
  walkers are not monotone in a (rotor a 0.69 -> 1.8, memoryless a 0.92 -> 1.25, mean-field a 0.68 -> 1.0),
  so a within-ant slope would not be explained by a alone.

### 5. Stopping rules and what I will not claim
- No mechanism is inferred from the ratio alone, consistent with the failed entries in the kappa-mechanisms
  ledger (P1, return gates, cutoff-ratio mixed model, square-loop test).
- Stop after steps 0-2 if step 2 shows no EPS below 1. The finding then stands as "walker ratios >= 1 at all
  memory levels tested; ants below 1", and the next experiment belongs on the rule-space side (what in a
  deterministic rule-written colour field lowers the ratio), not in more walkers.
- If step 1 or 4 overturns "ant below every walker", append a correcting NOTEBOOK entry and add a dated
  addendum below the results verdict; do not edit the original text.

## Step 2 registration: noisy-rotor scan (2026-10-19 21:35 NZST, base commit f414649, **before the run**)

Executes "Next steps" item 2 above as written; nothing in the design changes. Specs `results/specs_nrotor.txt`:
`nrotor:EPS:SEED`, EPS in {0, 0.01, 0.02, 0.05, 0.1, 0.2, 0.4, 0.7, 1.0}, seeds 2026102001..08 (72 runs),
`probe 27 8192`, script `scripts/run_nrotor.sh`, analysis `scripts/analyse_nrotor.py` (same estimators as `analyse.py`;
windows k = 12..22 and k = 20..26; ratio per seed with the seed's own a, beta).
Drift definition (fixed now): `g` = least-squares slope of ln(kappa_k) on k over the window set (per octave);
stationary if |g| < 0.05 (the census cut). Runs with any escaped window are dropped from means and counted.

Predictions (i)-(iii) are those in item 2, plus numbers I commit to now:
- (i) mean ratio (k=20..26) is monotone non-increasing in EPS within 1 between-seed sd; EPS=0: 1.7-1.9; EPS=1.0: 1.15-1.40.
- (ii) no EPS has mean ratio < 1.0 at k=20..26. Falsified if any EPS mean is < 0.96 with a <= 0.75.
- (iii) a(EPS) <= 0.75 for EPS <= 0.1 (k=20..26).
- (iv) EPS=1.0 agrees with `pw:0.5` (1.32 +- 0.1 at k=12..22). A mismatch > 0.15 is a code bug to be chased, not a finding.
- (v) the EPS=0 run reproduces the plain rotor (ratio 1.69 +- 0.1 at k=12..22).

## Step 2 results: noisy-rotor scan (2026-10-19, run at f414649; sha256 in `results/probe_bin_nrotor.sha256`)

Commands: `bash $E/scripts/run_nrotor.sh` then `uv run $E/scripts/analyse_nrotor.py` -> `results/analysis_nrotor.txt`.
72 runs, 8 seeds per EPS. Mean (between-seed sd), a/beta fitted per seed.

**Deviation from the registration.** The probe's `escaped` column is a run-level flag repeated on every row; an escaping run
simply ends, and its complete windows before that are valid. My first analysis dropped every run with the flag, which left
nothing for EPS >= 0.02. Fixed to keep complete windows (no data touched). Noisy walkers have a ~ 0.9 and leave the 8192 board
at 2^23-2^26 steps (EPS=0 never escapes), so the registered census-matched window k=20..26 exists only for EPS=0 (8/8) and
EPS=0.01 (6/8; 2/8 at 0.02). **Windows k=12..22 (and k=12..20 for all runs) are the comparison.** This is a window deviation
decided after seeing the escapes, not before.

| EPS | a (12..22) | beta | kappa | kunif | ratio (12..22) | drift g | stationary | ratio (12..20) |
|---|---|---|---|---|---|---|---|---|
| 0 | 0.734 (.016) | 0.588 | 1.852 | 1.099 | **1.69** (.02) | 0.018 | 8/8 | 1.66 |
| 0.01 | 0.871 (.022) | 0.708 | 2.800 | 1.082 | **2.59** (.09) | 0.099 | 0/8 | 2.29 |
| 0.02 | 0.905 (.033) | 0.782 | 2.557 | 1.063 | **2.41** (.17) | 0.079 | 0/8 | 2.21 |
| 0.05 | 0.935 (.015) | 0.859 | 2.196 | 1.042 | **2.11** (.15) | 0.053 | 4/8 | 2.00 |
| 0.10 | 0.931 (.024) | 0.878 | 1.900 | 1.035 | **1.84** (.09) | 0.038 | 7/8 | 1.77 |
| 0.20 | 0.936 (.011) | 0.902 | 1.663 | 1.029 | **1.62** (.05) | 0.024 | 7/7 usable | 1.56 |
| 0.40 | 0.922 (.016) | 0.898 | 1.465 | 1.029 | **1.42** (.05) | 0.018 | 7/7 usable | 1.41 |
| 0.70 | 0.933 (.017) | 0.920 | 1.339 | 1.023 | **1.31** (.03) | 0.008 | 8/8 | 1.30 |
| 1.00 | 0.931 (.028) | 0.924 | 1.290 | 1.022 | **1.26** (.03) | 0.010 | 8/8 | 1.26 |

(EPS=0.2, 0.4 have 7 of 8 runs complete through k=22.) At k=20..26: EPS=0 ratio 1.79 (.03); EPS=0.01 (n=6) 4.6 with g=0.095, a=0.92.

### Against the registered predictions
- (i) monotone non-increasing from 1.8 to ~1.25: **falsified.** Ratio *rises* to 2.4-2.6 at EPS 0.01-0.02, then falls monotonically to 1.26 for EPS >= 0.02. Endpoints held (EPS=0 1.69, EPS=1 1.26).
- (ii) no EPS below 1.0: **held** (minimum 1.26). Neither removing environment memory nor adding noise gets near the ant median 0.81 or even 1.
- (iii) a <= 0.75 for EPS <= 0.1: **falsified.** a is already 0.87 at EPS=0.01 (0.92 at k=20..26). The cube-root-like regime does not survive even 1% noise over these windows; this is not consistent with D3 as I stated it.
- (iv) EPS=1 vs pw:0.5: 1.26 vs 1.32, difference 0.06, within the 0.15 bar: **held** (the walkers differ in turn rule, so exact equality was not expected).
- (v) EPS=0 reproduces the rotor: 1.69 vs 1.69: **held.**

### What this does and does not show
- Observation: for 0.01 <= EPS <= 0.05 kappa/kappa_unif is above the rotor's, and these runs are not stationary (g 0.05-0.10 per octave, 0/8 at EPS 0.01-0.02), so the level there is a transient between two regimes, not a fixed point. The drift is positive: kappa is still rising, so the 12..22 value understates where it is heading (k=20..26 gives 4.6 at EPS=0.01).
- Interpretation (unverified): a small amount of noise breaks the rotor's compact-blob structure fast (a 0.69 -> 0.87) while the territory keeps a memory-like rough edge, which inflates boundary revisits; I have not tested this and do not claim a mechanism.
- The ratio never goes below 1 at any EPS. Per the pre-registered stopping rule (item 5) the finding stands as "walker ratios >= 1 at all memory levels tested; ants below 1", and the next experiment belongs on the rule-space side. Steps 1, 3, 4 (memoryless window control, f-layer calibration, ant-side noise reduction) are not run.
- Caveats: windows are k <= 22 for everything but EPS=0 (a ~ 0.9 is not asymptotic); 8 seeds; non-stationary rows (EPS <= 0.05) are not comparable with the stationary ant distribution; the board limit made the registered census window unavailable.

## Close-out (2026-10-19, commit 8b290d8 + this one)

Housekeeping owed in "Next steps" item 0 is done; steps 1, 3 and 4 are **not run** (stopping rule, item 5).
- `notebook.ipynb` written and executed top to bottom from a clean kernel under `uv` (`uv run --with jupyter --with nbconvert --with ipykernel jupyter nbconvert --to notebook --execute --inplace notebook.ipynb`; Jupyter is still not in `pyproject.toml`). It reads only committed `results/`, recomputes both tables, and agrees with the tables above. While building it I caught that the spec strings are `nrotor:1.0:` (not `1`); fixed in the notebook, no data affected.
- **Census window (answers the open item):** `experiments/_lib/analyse_probe.py` fits a, beta, g_c, g_k over k = 20..26 but takes `kappa` from the **last window only (k = 26, t in (2^25, 2^26])**, not a window mean. The walker tables here use the mean over k = 12..22 (k = 20..26 for the rotor). For the rotor the last-window and 20..26-mean ratios agree (1.800 vs 1.799), but for the non-stationary noisy rotors the last window of the available range is far above the mean (EPS 0.01: 4.15 vs 2.59), and for the memoryless walkers (last available window k = 22, not 26) it is -0.01 to +0.08 from the mean (rw 1.355 vs 1.277, pw:0.5 1.304 vs 1.316). So the memoryless-walker comparison with the ants is not window-matched, as flagged above, and the rotor one is.
- Tests: `cargo test --release` (no Rust changed; result in NOTEBOOK).
- Pointers added: `notes/open-questions-hypotheses.md` (kappa reference bullet), a correction entry in `2026-10-kappa-uniform-baseline/NOTEBOOK.md` (window labelling), blog homepage card and `blog/_posts/2026-10-19-the-ant-below-every-walker.md`.

**Verdict.** Registered predictions 1-3 (memoryless, rotor, location) held. In the noisy-rotor scan (i) and (iii) failed; (ii), (iv), (v) held. Every walker tested, including every EPS of the noisy rotor, has ratio >= 1.26; the ant median is 0.81. The ant deficit is therefore not a generic property of walkers with matched exponents. Unexplained: why the ants are low; why a leaves the 2/3 branch at EPS = 0.01; why the ratio overshoots the rotor at small EPS (non-stationary).
