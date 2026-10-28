# kappa prefix decode: what does the 8-letter prefix encode?

Registered 2026-10-16 09:05 +13:00, base commit `269288e`, before any decoding
measurement. **Exploratory discovery on inspected data** (census and the 162
stationary pool rules were already used by `prefix_audit.py`); nothing here is
confirmation. Confirmation would need a fresh `w3c_sample.py` draw under a new
seed, excluding pool rules (not run).

## Question, and a correction to its framing

The prefix signal that survives scrutiny is the **stationary-cohort gain over a
spline in ln A(22)**: +0.20 held-out R^2 (CI 0.10-0.31, 162 rules;
`../2026-10-kappa-rule-space/results/prefix_audit.json`). It is *not* the 0.63 in
`x2_prefix_heldout.txt`; that is ln A(22) alone (prefix-6 + ln A gives 0.633, no
gain), and all-rules transfer is ~0 (+0.04, CI -0.02..0.10). So the target here is
the **residual of ln kappa after the ln A(22) spline, stationary rules only**.
Otherwise any feature that predicts growth speed would look like a decoded prefix.

Already tested and not repeated: fresh-cell long-excursion launch rate (P1 failed)
and exposure features over position (P2 failed its interval bar), in
`../2026-10-kappa-prefix-exposure`. Earlier evidence in
`../2026-10-kappa-rule-space` (W1, X1): prefix-sharing ICC of stationary ln kappa is
~0 for prefix <= 3 and jumps at 4 (0.14), 5 (0.32), 6 (0.46); Hamming-1 flips at
positions j >= 4 give r(ln kappa) = 0.38 but j <= 3 ~ 0.

## Candidate encodings (all compared to the prefix-8 lookup, the reference)

- **E0 additive**: ridge on R-indicators at positions 1..8 (plus length).
- **E1 interactions**: E0 plus all pairwise products of positions 1..8.
- **E2 summary**: leading-run length, R count in the first 8, number of L/R switches
  in the first 8 (3 numbers).
- **E3 edge-runs-its-own-prefix**: ln kappa residual of the *standalone* rule
  `canon(rule[:p])` looked up in the census (p = 4..7), no lookup fitting.
  Mechanism: fresh and recently invaded rim cells carry low colours, so near the
  boundary the ant mostly executes `rule[:p]`.
- **E4 shuffled-position control**: E0 and E1 with positions permuted at random
  per fit (should give ~0 gain; guards the pipeline).
- **Descriptive**: greedy depth-3 regression tree on the stationary residual over
  prefix letters, to show which positions split.

## Predictions (registered; thresholds are design choices)

gain = held-out R^2 gain over the area spline on the 162 pool rules, trained on the
census stationary rules (exactly the audit's training/test sets and metric); lookup
gain reference = the audit's (spline, crossfit5) gain, re-derived in this script.

- **D1** (additive fails): E0 recovers < 25% of the lookup gain. The earlier
  "simple features fail" result was on raw kappa; I expect it to hold on the residual.
- **D2** (information is interactive): E1 recovers >= 50% of the lookup gain, CI of
  the E1 gain above 0.
- **D3** (own-prefix mechanism): E3 gain CI above 0 for some p in 4..7, and the best
  p recovers >= 50% of the lookup gain. If E3 fails while E1 succeeds, the prefix
  acts as a code, not as the rule the edge actually runs.
- **D4** (control): E4 gain CI contains 0.
- **D5** (tree): the first split of the descriptive tree is at position >= 4.
  (Weak prediction from W1/X1.)

Failure of D2 and D3 together means the lookup's gain is a rule-specific memorisation
of sibling rules that no compact encoding captures at this sample size.

## Commands

```bash
wsl -e bash -lc "export UV_PROJECT_ENVIRONMENT=\$HOME/.venvs/turmite UV_LINK_MODE=copy && cd /mnt/f/Code/turmite && uv run experiments/archive/2026-10-kappa-prefix-decode/scripts/decode.py"
```

Outputs: `results/decode.txt`, `results/decode.json`.

## Results

Run 2026-10-16 (commit 269288e, dirty tree, seed 20261016, 2000 pool-rule bootstraps;
`results/decode.txt`, `decode.json`, `leadrun_table.txt`). Gain = held-out R^2 gain over
the ln A(22) spline on the 162 stationary pool rules, trained on 2183 stationary census rules.

| model | gain [95% CI] | vs lookup |
|---|---|---|
| prefix-8 lookup (reference) | +0.201 [0.103, 0.311] | 100% |
| E0 additive R-indicators, pos 1-8 | +0.301 [0.212, 0.409] | 150% |
| E1 + pairwise interactions | +0.365 [0.273, 0.479] | 182% |
| E2 three summaries (lead run, R count, switches) | +0.330 [0.238, 0.443] | 164% |
| E3 own-prefix census residual, p=4/5/6/7 | +0.045 / +0.086 / +0.121 / +0.138 | 22-69% |
| E4 target-shuffled controls | -0.007, -0.009 (sd 0.009, 0.015) | ~0 |
| *post hoc* A8 leading run length alone (1 number) | **+0.330 [0.242, 0.441]** | 165% |
| *post hoc* A5 letter 2 alone (RR vs RL) | +0.227 [0.159, 0.298] | 113% |
| *post hoc* A11 R count in first 4 | +0.249 | 124% |
| *post hoc* A7 letters 4-8 only / A12 letters 9+ | +0.065 [-0.005, 0.142] / +0.002 | 32% / 1% |
| *post hoc* A1 length, A3 R fraction of whole rule | -0.013 / +0.032 (CI includes 0) | - |

Mean residual of ln kappa (after the area spline) by leading-run length k (census | pool):
k=1 -0.110 | -0.123; 2 +0.043 | +0.054; 3 +0.135 | +0.132; 4 +0.239 | +0.221; 5 +0.340 |
+0.352; 6 +0.453 | +0.372; 7-8 +0.64..+0.72 (census only). Within-group sd ~0.17;
corr(lead, residual) = 0.62 census, 0.70 pool. Roughly **+0.1 in ln kappa per extra
leading same-letter step**, near-linear.

Verdicts on the registered predictions:
- **D1 FAILED** (expected additive to recover <25%; it recovers 150%).
- **D2 passed vacuously** (E1 182%, CI > 0) but interactions add little over E0 (+0.06) and
  nothing over the one-number leading run; the lookup tree is not hiding interactions.
- **D3 FAILED**: own-prefix residual recovers 22-69%, best p=7 (69%, CI > 0 but coverage
  of the census is only 43-60%, so partly missing-value filling). The strict ">= 50%"
  bar is met at p=6 and 7 but the feature is far worse than the leading run itself.
  Reading: the edge-runs-`rule[:p]` story is at most a coarse proxy of the leading run.
- **D4 passed** (shuffle controls ~0).
- **D5 FAILED**: first tree split is at position 2 (RR vs RL, SSE drop 31.6), not >= 4.

What this is and is not: the lookup is a *noisy encoding* of a one-parameter signal, so
the earlier statement "every simpler rule feature fails" is true for raw kappa and for
features that carry no early-letter order (length, R fraction: A1, A3, here ~0) but false for
the area-residualised target once the leading run is used. The signal sits almost entirely in
letters 1-4 (A11 124%, A7 32%, A12 ~0). Open and **not** shown: (i) lead run correlates -0.56
with ln A(22), so a single area snapshot plus spline may leave growth-history confounding (the
audit's standing caveat; the leading run could proxy early growth, not a transport property);
(ii) A-series is post hoc, selected on the same pool data it is scored on, so the headline
+0.33 is optimistic; it needs fresh rules; (iii) the non-stationary rules are excluded;
(iv) no mechanism: why a run of k identical turns should raise the share of time on the
boundary by ~10%/step is untested.

Mechanism candidate for the next, registered test (not tested here): a cell whose first k
colours all turn the same way sends the ant through k same-handed turns on each early visit,
so the rim is laid down as a coherent circulating (spiral) structure whose return kernel
depends on k; the cleanest intervention is to hold the rule fixed from letter k+1 on and vary
only the leading run (W6-style paired mutation at fixed area, with the early-colour exposure
measurement), predicting a monotone dose response of ln kappa in k with slope near +0.1.
Existing W6m found early-letter mutations sign-mixed in kappa, which this has to reconcile
(mutating letter 2 changes k only when it is the run boundary).
