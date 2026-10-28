# alpha-gap: is the log/blob cut at alpha = 0.15 objective?

Registered 2026-10-15 23:32 +13:00, before any code was written (reviewer response, complaint 2).

## Question
The paper calls a rule log-growing if its census width exponent alpha < 0.15, "chosen by eye from the
gap in the exponent histogram". Is there an objective gap, and does the blob median depend on the cut?

## Registered tests and predictions (census.csv, probe_summary.csv only)
1. Hartigan dip test on the raw alpha distribution. Prediction: p < 0.05.
2. Cut sensitivity at 0.05, 0.10, 0.15, 0.20, 0.25: N, median blob alpha_w, IQR.
   Prediction: median changes by < 0.001 for any cut in [0.10, 0.25].
3. Two-component Gaussian mixture on raw alpha. Prediction: low component mean < 0.12.
4. Histogram with the cut marked.

## Command
`uv run experiments/archive/2026-10-alpha-gap/scripts/gap_robustness.py` (seed 20261015; adds `diptest`, `scikit-learn` to pyproject).
Outputs: `results/gap_robustness.json`, `results/alpha_gap.pdf|png`.

## Results (appended after the run; predictions above are unchanged)
Population: 3512 census rules; 3208 non-builders (571 log, 2637 blob). Builder alpha is on a different regime and is excluded from the
distribution tests (the dip test on all 3512 gives the same answer).

| Prediction | Outcome |
|---|---|
| Dip p < 0.05 | **Met**, dip = 0.047, p < 0.001 (n = 3208). Weak evidence: it only rejects unimodality, and a long left tail would do that. |
| Median moves < 0.001 for cuts in [0.10, 0.25] | **Not met.** Medians 0.3312 (cut 0.10), 0.3326 (0.15), 0.3328 (0.20), 0.3329 (0.25): spread 0.0017, max deviation from the 0.15 cut 0.0014 (all from the 0.10 cut). For cuts 0.15–0.25 the spread is 0.0003. At cut 0.05 the median is 0.3293. |
| GMM low mean < 0.12 | **Met**: components at 0.094 (sd 0.031, weight 0.19) and 0.334 (sd 0.025, weight 0.81). |

Unregistered but important: the histogram does **not** show an empty gap at 0.15. The log-growers' density falls off across 0.10–0.17
(20, 29, 20, 8 rules per 0.01 bin at 0.12–0.16; 16 rules in [0.145, 0.155)), and the true trough is at **0.17–0.26** (0 to 4 rules per bin),
above the cut. So 0.15 sits on the flank of the log-grower peak, not inside a gap; 0.2 would be a more defensible midpoint of the empty
region. The conclusion that matters (median 0.333 insensitive to the cut) holds to within 0.0003 for any cut in the trough region.
