# Do the 702 late survivors include slow or bounded growers, and do highways come from them?

Registered 2026-11-10 09:15 NZDT (+13:00), base `251100a2f99f81099954ebd147dea11ea173e337`, branch `agent/survivor-slow-growers`.
Status: **MEASURED** (P1, P2 held; P3 failed on 1 of 8). Registered with nothing measured beyond the exploratory look stated below; moved from `proposed/` to `active/` on 2026-11-11 once results existed.
Phase priority 2 (regime validation: censoring and selection bias in the late-highway hazard cohort). Answers the open item in
`notes/ACTIVE.md` ("whether the 702 include bounded rules (RLLLLLR is 42x42 at 1e11)") and feeds Q19.

## What I already looked at (exploratory, not a test)

Before registering I computed, for the 702 `stop=budget` rows of the 1e11 census
(`experiments/archive/2026-10-highways-unresolved-rules-1e10-1e11/results/h1e11/`), the side growth over the last decade,
`g11 = log10(side(1e11)/side(1e10))` with `side = max(width, height)`, using `h1e10/` for the 1e10 boxes. The distribution is
bimodal: 528 rules in the 0.25-0.35 bin (cube-root growth of the side predicts 1/3), 143 rules below 0.2 (50 at 0.00-0.05, many
with sides 30-150 cells), and a few above 0.4. The gap between ~0.15 and ~0.25 is nearly empty, so the class cut 0.2 is chosen from this
look. **Everything below uses data I have not yet looked at in relation to this class** (1e8 and 1e9 boxes; which rules became
genuine highways; new longer runs).

## Classes (frozen now)

`scripts/classes.py` (stdlib) -> `results/classes.csv`: `slow` if `g11 < 0.2`, else `growing`. Result: 143 slow, 559 growing.
sha256 `classes.csv` 40b5533e...5d84123f, `p3_sample.txt` dfe4c858...2c44dd.

## Hypotheses

* **H-slow (my prior ~75%):** the survivors are a mixture: a cube-root-growing majority and a distinct slow class (bounded or
  much slower than t^(1/3)) that stays slow. The slow class is not at risk of the late highways seen so far.
* **H-pause (competing):** "slow" is a transient pause of ordinary cube-root growers (a rule that sat still for a decade resumes),
  so classes do not persist across decades and highways arise from both classes in proportion.

## Registered predictions

Notation: `g10 = log10(side(1e10)/side(1e9))`, `g9 = log10(side(1e9)/side(1e8))`; 1e8 boxes from
`experiments/archive/2026-10-census-sweeps/results/sweep_v2.csv` (board as recorded in that census), 1e9 boxes from `sweep_1B.csv`, 1e10
from `h1e10/`.

* **P1 (persistence, both directions).** Among the 143 slow rules, >= 90% have `g10 < 0.2`; among the 559 growing rules, >= 90%
  have `g10 >= 0.2`. Fails if either fraction is below 90%. H-pause predicts both fractions near the overall class shares
  (about 20% / 80%), i.e. a failure.
* **P2 (where highways come from).** Of the genuine late highways with onset in (1e9,1e10] (16 rules) and (1e10,1e11] (12 rules),
  as listed in `experiments/archive/2026-10-late-highway-board-check/results/classify.txt` (status table), at most 1 of 28 was
  slow in the decade before its onset decade (`g9 < 0.2` for the first cohort, `g10 < 0.2` for the second). Under H-pause, with a
  slow share of about 0.2, the expected count is about 5.6 and P(X <= 1) is about 0.02. Fails if X >= 2.
* **P3 (do they stay put?).** The 8 slow rules in `results/p3_sample.txt` (first 8 of the slow class by sha256("survivor-slow:"+rule))
  are re-run from a blank board to 2e11 steps. Prediction: all 8 have `side(2e11)/side(1e11) <= 1.05` (cube root predicts 1.26),
  none escapes and none forms a highway. Fails if any ratio exceeds 1.05 or any rule escapes or forms a highway.
  Measurement check T1: the 2e11 run must reproduce nothing contradictory with the census (it cannot check 1e11 directly; recorded
  as a limitation, not a test).
* **Consequence, not a hypothesis:** if P1 and P2 hold, the at-risk pool for Q19 is the growing class, and the per-decade yields
  are recomputed on growing-only denominators (`results/yields_growing.txt`). The Q19 registered 1e12 prediction ("about 12 of
  702") becomes "about the same count among about 559", so its expected yield per rule rises by about 702/559 = 1.26x. No Q19
  decision rule is changed here; Q19 remains registered and un-run.

"Bounded" is not claimed by any of these tests: a ratio of 1.0 over one doubling is compatible with a rule growing as a log or a
very small power. The deliverable is "slow class persists and is not the source of late highways", or its failure.

## Pruning-index preflight

* Index revision `251100a2f99f81099954ebd147dea11ea173e337`. Commands: `ls notes/pruning-index/entries`;
  `rg -n -i -e bounded -e survivor -e slow -e at-risk -e hazard notes/pruning-index/entries`.
* Candidates: `NR-20261025-crawler-window-single-letter` (mentions survivor filtering, unrelated objective) and
  `NR-20261028-wall-vs-memory-bounded-random-fresh-compact` ("bounded" refers to fresh runs of a random walker). Neither covers
  the late-survivor cohort or highway hazard. No match is a recorded outcome, not evidence of novelty.
* Decision: **run**. Compute budget: P1, P2 are reads of committed CSVs; P3 is 8 rules x 2e11 steps, 4 at a time, about 40 min
  wall on 4 cores (1.8e8 steps/s/core measured by Q19 T2). Stop after P3 whatever it shows; any longer run (bounded check by exact
  recurrence, 1e12) needs its own registration.

## Reproduction

```bash
uv run --frozen experiments/active/2026-11-survivor-slow-growers/scripts/classes.py
cargo build --release --locked --bin sweep_lean
bash experiments/active/2026-11-survivor-slow-growers/scripts/p3_run.sh
uv run --frozen experiments/active/2026-11-survivor-slow-growers/scripts/analyse.py
```

## Results, uncertainty and limitations

* **P1 HOLD**, **P2 HOLD** (`results/analysis.txt`).
* **P3 FAIL** (`results/p3_analysis.txt`, `scripts/p3_eval.py`): 7 of 8 slow rules had `side(2e11)/side(1e11) <= 1.05`; RLRLRRRR
  reached 1.086 (140 -> 152). None escaped or formed a highway; all stayed far below the cube-root 1.26.
* Limitation: 8 rules over half a decade cannot tell bounded rules from very slow growth; the slow class is "slow", not "bounded".
  The second P3 batch's start time is unlogged (see NOTEBOOK).
* Correction (2026-11-12, after review on PR #37): P2's zero is an upper bound, not a zero hazard. 0 genuine late highways in
  287 slow rule-decades (143 in (1e9,1e10], 144 in (1e10,1e11]) gives a 95% Poisson upper bound of about 3.0/287 = 1.0% per
  decade, roughly half the growing-class rate (2.4%, 2.0%). So the slow class has a lower hazard, consistent with zero, and
  "the at-risk pool is the growing class" is a modelling choice: Q19 should show yields on both the 702 and 559 denominators.
* Correction (2026-11-12): `results/yields_growing.txt` was never written; the growing-only yields are in `results/analysis.txt`
  ("Pools at decade start"). The committed `classes.csv` is LF, sha256 9d867159...827da8a6; the registered hash at line 21 is
  of a CRLF file, and `classes.py` now writes LF.
* Post hoc observation (2026-11-12, not evidence): all 8 P3 rules grew in every decade from 1e8 to 1e11 (for example RLLLR
  44, 54, 62, 70, then 72 at 2e11), and no slow rule's box shrank. The "bounded vs very slow" framing is weak; the per-decade
  increments look roughly constant, which suggests `side ~ a + b log10 t`. A registered log-versus-power test is the next step.

---

## Amendment A1: log versus power growth of the 143 slow rules (registered 2026-11-12 22:15 NZDT (+13:00), nothing fitted)

Append-only. Nothing above is edited. Registered on branch `agent/survivor-slow-growers` on top of `a729be7`, after Tim approved
the test in chat on 2026-11-12. This amendment is committed alone, and pushed, before any model is fitted to any box; the analysis
script is written only after that commit.

### Question

The 5% bound of P3 was registered as if the slow class were bounded. The post hoc look (README, "Post hoc observation"; NOTEBOOK
2026-11-12 18:25) suggested otherwise. What functional form does the box side of a slow survivor follow between 1e7 and 1e11 steps?

### What I have already looked at (so this is partly confirmatory, not a blind test)

I have read, for the 143 slow rules, the sides at 1e8, 1e9, 1e10, 1e11 only as the *aggregate* statements in the 2026-11-12 18:25
notebook entry (all 143 non-decreasing; 127 grew in all three decades; in 106 of those the largest per-decade increment is at most
twice the smallest) and, per decade, for the 8 P3 rules (including their 2e11 sides). I have **not** fitted any model to them.
The hypothesis H-log was suggested by that look, so a fit of H-log to the same four points is not independent evidence for it. The
two protections are: (i) a fixed comparison against H-power, whose pass/fail is not guaranteed by the look, and (ii) a genuinely
unseen out-of-sample point, the **1e7 box** of each rule in `sweep_2_10.csv` (all 143 have a `budget`, 1e7-step row), which I have
not read for these rules; predictions P4 are made from the 4-point fits.

### Data (committed, read only)

Per rule, `side = max(width, height)` at `t = 10^k`: k = 8 `sweep_v2.csv`, k = 9 `sweep_1B.csv`, k = 10 `h1e10/`, k = 11 `h1e11/`
(exactly as `scripts/analyse.py` reads them), and k = 7 from `experiments/archive/2026-10-census-sweeps/results/sweep_2_10.csv`. A rule is
used only if each of its rows has `stop = budget` and `steps = 10^k` exactly; otherwise it is dropped and listed (`n_used` is
reported with the 143). The rule set is the frozen `results/classes.csv` (`cls = slow`). Calendar and board settings of the older
census runs are as recorded there; a 1e7 box that disagrees with its own 1e8 box (smaller 1e8 side than 1e7 side) is reported as an
instrument anomaly, and the rule stays in.

### Hypotheses (about `y(t)` = box side, `x = log10 t`)

* **H-const (bounded, already saturated):** `y = c`. Not a straw man: it is the registered "bounded" reading of P3, in its
  sharpest form. Saturating-after-1e8 transients are the same hypothesis up to noise.
* **H-log:** `y = a + b x`, b free (one added box of `b` cells per decade, a doubling adds `0.30 b`).
* **H-power:** `y = C t^alpha`, with `0 <= alpha <= 1/3` (alpha = 1/3 is the cube-root law of the growing class; alpha = 0 is H-const).
  The fit parameterises `C` at `t = 1e11` and scans `alpha` on `numpy.linspace(0, 1/3, 334)`, with `C` solved exactly by weighted least squares.
* Control **H-cube** (alpha fixed at 1/3, `C` free): should be rejected for essentially every slow rule (their g11 < 0.2 by
  construction); a failure to reject says the noise model is far too wide.

My prior (written before fitting): ~35% H-log is the better class description (P3 below), ~40% the two cannot be told apart, ~15%
H-power, ~10% something else (both rejected, mixed class).

### Noise model and fit (fixed now)

`y_k` is an integer cell count; there is no repeat-seed noise (a rule is deterministic), so "noise" is the departure of a lumpy,
monotone staircase from a smooth law. I model it as independent Gaussian with `sigma_k = max(1, 0.03 y_k)` cells (about one cell for the
rounding of each box edge, and 3% for lumpiness), `y_k` the *observed* side. Weighted least squares, `chi2_m = sum_k ((y_k - f_m(x_k))/sigma_k)^2`.
Degrees of freedom on four points: const 3, log 2, power 2. `AIC_m = chi2_m + 2 k_m` with `k` = 1, 2, 2. The sigma scale is a guess;
the sensitivity runs use scale 0.5 and 2 (descriptive only, they do not change any verdict).

### Per-rule label (4 points, k = 8..11)

`D_i = chi2_power - chi2_log` (positive favours log; both have k = 2).
* `const` if `AIC_const <= min(AIC_log, AIC_power)`;
* else `log` if `D_i >= 4` (likelihood ratio about e^2 = 7.4), `power` if `D_i <= -4`, else `ambiguous`.

### Instrument calibration (synthetic, no real data; run by the script before it reads any box)

Seed 20261112. For `y8 in {30, 60, 120}` and noise as above (3000 draws each): truth log with `b = 0.1 y8` and `0.2 y8`; truth power with
`alpha in {0.03, 0.06, 0.10, 0.15}` (normalised at `t = 1e8`). Reported: label rates, mean `D`, and the backcast score below. I ran a
throw-away prototype of this *synthetic* calibration before writing this registration, in order to pick the thresholds. Its
findings, which are the honest statement of what four points can do: per rule, for `alpha <= 0.06` the label is
`ambiguous` in at least 99% of draws whatever the truth; only `alpha >= 0.10` is labelled `power` (about 40% at 0.10, 92% at 0.15); truth log is
labelled `log` in at most 2%. Mean `D` is about +0.05 to +0.6 under truth log, -0.02 to -0.4 for alpha = 0.03 to 0.06 and -3 for 0.10. So
**per rule the 4-point test cannot discriminate in the regime of interest (alpha about 0.05, which is what a slow class with
g about 0.05 per decade has), and the aggregate over 143 rules can only separate log from power if alpha is above about 0.04.** If the
data sit at alpha below that, the honest result is "indistinguishable", and I will say so.

### Gates

* **G1 (noise scale adequate):** the median over used rules of `min(chi2_log, chi2_power)` (4 points, 2 df, nominal median 1.39) lies in
  [0.3, 3.0]. If it does not, sigma is mis-scaled: P2 and P3 are reported as numbers but **not** as verdicts, and the sensitivity rows are
  read instead.
* **G2 (data):** at least 135 of the 143 rules have all five rows as defined. Otherwise the shortfall is the headline.

### Registered predictions (all on the used rules; thresholds fixed now)

* **P1 (bounded is refuted).** At least 80% of used rules have `chi2_const > 7.815` on four points (3 df, p < 0.05). Fails if fewer.
  This refutes "box side constant for 1e8-1e11" for most of the class; it says nothing about the 20% that may be bounded.
* **P2 (log is adequate).** At least 75% of used rules have `chi2_log <= 5.991` (2 df, p >= 0.05). Fails if fewer. (Gated by G1.)
* **P3 (aggregate log versus power).** Let `S = sum_i D_i` over used rules. Parametric bootstrap, seed 20261112, B = 2000 per
  arm, noise as above: arm LOG simulates each rule from its own fitted log curve, arm POWER from its own fitted power curve (x = 8..11, same
  `sigma` rule applied to the simulated values), refits both models, and records `S*`. Then
  `p_pow = P_POWER(S* >= S_obs)` and `p_log = P_LOG(S* <= S_obs)`.
  * **LOG favoured:** `p_pow < 0.05` and `p_log >= 0.05` (power rejected, log not). This is the predicted outcome.
  * **POWER favoured:** `p_log < 0.05` and `p_pow >= 0.05`.
  * **Both rejected:** both < 0.05 (neither curve family describes the class's curvature).
  * **Indistinguishable:** both >= 0.05. This is the outcome the calibration says is likely if alpha < 0.04.
  The prediction **P3 holds only if LOG is favoured**; every other outcome is a failure of P3 and is reported as such. (Gated by G1.)
* **P4 (out-of-sample backcast to 1e7; the only unseen data).** From each rule's 4-point log and power fits predict `y(1e7)`
  (`a + 7b` and `C 10^{alpha(7-11)}`); `e_log`, `e_pow` are absolute errors against the observed 1e7 side. Let `N_log` = number of rules with `e_log < e_pow`
  (exact ties dropped, `N_tie` reported) among `N` used. **P4 holds** if the two-sided exact binomial test (p = 1/2) gives p < 0.05
  and `N_log > N/2`. If `N_log < N/2` with p < 0.05, power wins the backcast (P4 fails, in the opposite direction); otherwise indistinguishable (P4 fails).
  The synthetic calibration gives `N_log/N` about 0.59 under truth log with `b = 0.1 y8` (borderline for this rule), 0.78 for `b = 0.2 y8`,
  and 0.28 under power alpha = 0.06: this test is sharper than P3. Also reported, not a verdict: mean signed backcast error of each model,
  and the fraction of rules whose observed 1e7 side is below the 1e8 side (instrument anomaly guard).
* **P5 (local-slope drift, descriptive; no verdict).** Per rule, the successive increments `d_k = y_{k+1} - y_k` (k = 7..10).
  Median over rules of `(d_10 + d_9)/(d_8 + d_7)` is reported: H-log predicts about 1, power with alpha ~ 0.05 predicts about 1.2 (a
  factor `10^{2 alpha}`), H-const predicts 0 or noise.

### Supplementary stage (descriptive; does not override P3)

Stage 2 refits the three models to all five points (k = 7..11), reports label counts and `S`, the median `alpha_hat`, and the fraction of rules
whose `alpha_hat` is at the 0 or 1/3 bound. For the 8 P3 rules only, the log and power fits from four points are used to predict the 2e11
side; residuals are reported. **The 8 sides at 2e11 were already known to me, so this is a consistency check, not a test.**

### Decision consequences (fixed now, so I cannot re-read them after the fact)

* P3 = LOG favoured and P4 holds: "slow survivor boxes grow roughly logarithmically over 1e7-1e11, not as a power": the wording of the
  slow class in the README, guide and atlas changes from "slow, maybe bounded" to "logarithmic-looking growth (the power alternative is
  disfavoured at the stated noise model)"; the 1.05 bound is recorded as inside the cell noise of that law. Still no claim for t -> infinity.
* Indistinguishable: the slow class stays "slow, bounded not tested and not established"; the log-versus-power question is left open and
  the next step is a longer run (not registered here).
* POWER favoured: report the `alpha_hat` distribution; its median is the headline and the P3 5% bound is judged by it.
* No change to P1, P2 (original), P3 (original), Q19 or the 702/559 denominators.

### Pruning-index preflight

Index revision `cc7a8858fbde77153c19b7c8b0c4634a2abd9b07`. Commands: `ls notes/pruning-index/entries`;
`rg -n -i -e logarithm -e log-growth -e saturat -e "slow growth" -e bounded notes/pruning-index/entries`. Matches:
`NR-20261028-wall-vs-memory-bounded-random-fresh-compact` ("bounded" refers to fresh-run policies of a random walker; unrelated
objective). No entry covers growth laws of slow survivors. No match is a recorded outcome, not evidence of novelty. Decision: **run** (reads committed data only; seconds).

### Reproduction (script to be added after this registration)

```bash
export UV_PROJECT_ENVIRONMENT=$HOME/.venvs/turmite UV_LINK_MODE=copy
uv run --frozen experiments/active/2026-11-survivor-slow-growers/scripts/growth_fit.py
```

Uses `numpy` (already in `pyproject.toml` and `uv.lock`), so no PEP 723 header and `uv.lock` is untouched. Writes `results/growth_fit.txt`
and `results/growth_fit.csv`.

### A1 results (2026-11-12, registration `b1014be`, script `e357179`, results `efeae5b`)

`results/growth_fit.txt` and `results/growth_fit.csv`, from `scripts/growth_fit.py`; two runs byte-identical. 143 of 143 rules used (G2 pass);
no 1e7 side exceeds its 1e8 side (136 smaller, 7 equal). G1 pass (median min chi2 0.485, nominal 1.39: the registered sigma is somewhat
too wide, i.e. the staircase is smoother than modelled).

* **P1 HOLD.** chi2_const > 7.815 in 143/143. The control H-cube (alpha = 1/3) is rejected in 143/143 (median chi2 1344). Constant sides are refuted for all 143 rules (over 1e8-1e11 at this noise model; this does not exclude a rule that is flat after a late transient).
* **P2 HOLD.** chi2_log <= 5.991 in 123/143 = 0.860. For comparison chi2_power <= 5.991 in 122/143: both fit about equally well rule by rule.
* **P3 HOLD (LOG favoured).** Per rule, 135 of 143 are `ambiguous`, 6 `log`, 2 `power`, 0 `const` (as the calibration said: per-rule 4-point
  labels barely discriminate). In aggregate `S = sum D = +71.8` (median `D` +0.24). Bootstrap arms: LOG `S*` mean +87.7 (5-95%: +56.9 to +118.9),
  POWER `S*` mean -91.8 (-123.5 to -59.7). `p_pow < 0.0005` (0 of 2000), `p_log = 0.194`. Power is rejected as the class description; log is not.
* **P4 HOLD.** Backcast to 1e7 (not read before): `e_log < e_pow` in 108 rules, `e_pow < e_log` in 35, no ties, exact binomial p = 7.4e-10. Mean signed error (observed - predicted): log
  -0.95 cells, power -8.3 cells (power predicts 1e7 sides too large); median absolute error 1.6 vs 3.3 cells; constant model 17.8.
* **P5 (descriptive).** Median (d9+d10)/(d7+d8) = 1.000 over 142 rules (log predicts 1, power alpha 0.05 predicts 1.26).
* **Fitted values.** Power alpha_hat (4 points) median 0.059 (quartiles 0.052-0.065; none at a bound): above the 0.04 below which the
  calibration said the aggregate cannot separate the two families. Log slope b median 8.7 cells per decade (11% of the 1e11 side per decade).
  Five points (descriptive): 29 `log`, 10 `power`, 104 `ambiguous`; `S` = +558; median alpha_hat 0.063; chi2_log <= 7.815 in 112/143, chi2_power in 101/143.
* **Sigma-scale sensitivity (descriptive, 4 points).** Scale 0.5: 34 log / 13 power / 96 ambiguous, `S` +287, P2 fraction 0.72; scale 2: 1 log / 0 power, `S` +17.9, P2 fraction 0.99. The sign of `S` does not change; at scale 2 the aggregate would
  be much weaker (the bootstrap was not rerun at other scales, so the P3 verdict is stated at the registered scale only).
* **2e11 consistency check (not a test; sides already known).** The 4-point log fit predicts 2e11 sides within 1.2-7.5 cells of the observed
  (RLRLRRRR: predicted 144.5, observed 152, the largest miss); the power fit overshoots more (RLRLRRRR 146.3). The log predictions give ratios to the
  1e11 side of 1.03-1.05 for all 8 (RRRLLRLL exactly 1.05), so the registered 5% bound sat on the edge of what a log law gives. In 6 of 8 rules both fits
  over-predict slightly (post hoc: the real curve may be a little flatter than log; the backcast bias of -0.95 cells points the same way).

**Verdict.** At the registered noise model, four decades of box sides of the 143 slow survivors are better described as `side ~ a + b log10 t` than as a power law: the power alternative
is rejected in aggregate (p < 0.0005) and loses the out-of-sample 1e7 backcast 108 to 35, while the log curve is not rejected in aggregate. Constant (bounded) boxes are
refuted for all 143 over this window. Rule by rule the two families are not separable (135/143 ambiguous), so no individual rule is certified as log.

**What this does not show.** (1) Nothing about t -> infinity: a log law and a power law with alpha below about 0.04 are not separable here, and a rule-by-rule label is `ambiguous` for 135 of 143. The power family is rejected in aggregate at the registered noise model, not rule by rule.
(2) The test is partly confirmatory: H-log came from a look at the same four decades; only the 1e7 backcast is out of sample, and it was read once.
(3) The sigma model (3% plus one cell) is a guess; G1 says it is somewhat wide, and a narrower sigma only strengthens the aggregate, while a wider one weakens it.
(4) Rules are not independent draws (many share sub-structure), so the bootstrap p-values treat 143 correlated rules as independent and are optimistic;
the sign test in P4 has the same issue. (5) No rule was tested for a transition to cube-root growth or a highway beyond 2e11.

**Consequences, as registered.** The slow class wording changes from "slow, maybe bounded" to "logarithmic-looking growth over 1e7-1e11 (power disfavoured at the stated noise model)"; the 1.05
bound of P3 is recorded as sitting inside the cell noise of that law. No change to P1, P2, P3 (original), Q19 or the 702/559 denominators.
