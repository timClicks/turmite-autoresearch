# Proposed output contract

No data are present. Final column definitions and units must be frozen with
registration. All rows keyed by experiment/run, rule, start seed, arm and band.

- `results/manifest.json`: exact command, UTC and NZDT timestamp, git commit,
  dirty source hashes, config hash, input hashes, explicit rule/seed list,
  initial-patch convention, seed roles, folds, estimator, software versions.
- `results/runs.csv`: rule, base_rule (when paired), arm, seed, band, area_start,
  area_end, steps, B, I, P_end, A_end, mean_P_over_A, kappa_endpoint,
  kappa_time_normalized, attained, escaped, censored_steps, completion_status.
  Define both normalizations explicitly; never mix them in a model or figure.
- `results/features.csv`: rule/seed/arm/band, named feature, value, units,
  cell_or_step_weighting, normalization, sample_count, censor_lower, censor_upper.
  Tail: duration-bin counts/time sums and boundary/interior means. Prefix:
  colour/depth exposure, launch/return counts, first divergent turn. Gates:
  directed crossings, moving-map reclassifications, concentration, edit exposure.
  Age: census age/visits/cycles, separate exposure-weighted features and hazards.
  Only the experiment's relevant feature family is needed; no arbitrary search.
- `results/predictions.csv`: held-out rule/base, band, target seed role, model,
  fold, observed and predicted target, baseline prediction, coverage status.
- `results/analysis.json`: calibration, coverage and reliability gates;
  per-prediction estimates, seed sd, bootstrap intervals, exact verdicts,
  exclusions, limitations, exploratory labels, and hashes of every input.
- `dumps/`: optional episodes, spatial crossing maps, snapshots and checkpoints.
  No raw dumps in the notebook or cross-experiment imports.

Counts B+I must equal steps. Include incomplete episode fragments, not just
completed cycles. Unattained targets produce explicit status rows; never zeros
masquerading as measurements. A `.done` marker means verified output completion,
not scientific success. Keep bounded summaries small enough to commit.
