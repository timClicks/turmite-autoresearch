# Chirality versus letter-group prediction of c

## 2026-10-15 23:23 NZDT — critique-driven comparison

The [experiment registration and full recipe](../experiments/archive/2026-10-chirality-baselines/README.md)
fixes letter groups before scoring, after inspection of the original scatter.
Base commit `b3a0f762ac2230b5df92188206a4d3a1081897be`, with uncommitted work.
No new ant simulations or changes to probe fits/windows. Command:

```bash
export UV_PROJECT_ENVIRONMENT=$HOME/.venvs/turmite UV_LINK_MODE=copy
uv run experiments/archive/2026-10-chirality-baselines/scripts/compare.py
```

Sources, hashes, split validation and exact reconstruction of the original
chirality predictions are in [comparison.json](../experiments/archive/2026-10-chirality-baselines/results/comparison.json).
All 300 original calibration rules have non-bursty target values; all models
score exactly the same 2,747 held-out rules of length at most 12.

| Model | Held-out R² | RMSE |
| --- | ---: | ---: |
| Mean by letter after leading R | 0.585589 | 0.081457 |
| Mean by next three letters | 0.807648 | 0.055496 |
| Existing chirality model | 0.660023 | 0.073780 |

Relative to one-letter grouping, chirality reduces SSE by 17.96% (95% paired
rule-bootstrap interval 15.92–20.08%). Relative to three-letter grouping it
has 76.75% more SSE (65.42–88.93%). Intervals use 4,000 draws, seed 20261046,
stratified by primary group, holding fitted models fixed. These are rule-level
sampling intervals conditional on the original calibration; no between-seed
or training-sample uncertainty is measured. Related rules limit the
independent-unit assumption. No group selection was performed using held-out c.

Within primary L/R groups (1,452/1,295 held-out rules; 173/127 calibration
rules), chirality R² is 0.189960/0.163770: coarse one-letter grouping is not
the whole story. Centering observations and predictions within the three-letter
groups gives pooled residual R² = -0.00006245 for chirality. Its raw pooled
within-group score is -0.775530, including errors in group means. The two
statistics answer different questions; centering is descriptive and not a
fitted predictive model. Per-group counts, scores, errors and bootstrap
intervals: [groups.json](../experiments/archive/2026-10-chirality-baselines/results/groups.json).

The registered expectation of a one-letter R² within 0.05 of chirality failed
(gap 0.07443). The expectation of less than 10% chirality SSE reduction against
three-letter grouping held, with chirality actually worse. Synthetic controls
passed for perfect/zero/adverse residual skill, group shifts, training-only
means/fallbacks and paired bootstrap reproducibility. Existing physical walker
calibration was not repeated because the trajectory instruments did not change.

**Correction to the critique premise and the earlier chat response:** saved
predictions and existing `followup_stats.json`/paper `numbers.json` already
give R²=0.660 and correlation 0.869, not R²=0.88. No historical result was
overwritten to obtain this correction.

Interpretation: three-letter lookup is the stronger held-out predictor of c;
chirality has modest skill beyond one-letter grouping but essentially no
residual discrimination inside three-letter groups. This does not make c
meaningless: it is a conditional edge-entry probability. It also does not
make c a diagnostic of the cube-root exponent (see [calibration](calibration.md)).
An independent test holding out rule families and varying initial seeds remains
open; this reanalysis does not establish a transport mechanism.
