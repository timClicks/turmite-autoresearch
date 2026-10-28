# Output contract (prospective, version 1)

All generated files live in this experiment. Compact summaries go in results/;
event streams and checkpoints go in scratch/ (ignored). Never hand-edit outputs.

- `manifest.json`: schema version; full git revision; dirty source hashes if
  applicable; executable sha256; fresh build directory; exact argv/environment;
  rule input hash; explicit rules/strata/families/folds; seeds and roles; board,
  caps, bands, milestone list; estimator encoding/version; bootstrap seed.
- `runs.csv`: rule, family, stratum, seed, role, band, stop reason, entry/exit
  step, area, perimeter, boundary/interior/total steps, sum_P_over_A,
  completed/left/right-fragment counts and times, unresolved in-band time,
  maximum follow-up, checkpoint hash, runtime and peak memory.
- `segments.parquet` (scratch): run key, episode ID, segment ID, entry/exit
  time, entry/exit milestone, physical versus geometry-induced crossing,
  evolving/frozen convention, state encoding, elapsed time, censor reason,
  in-band contribution, entry/exit A/P. Counts and time sums are both necessary.
- `kernels.json`: model/fold/training keys, state counts, Q, m, entry law,
  dwell model, unseen-state policy, nonabsorbing classes, unresolved bounds,
  depth-64 time share, predicted first-return mean and its uncertainty.
- `predictions.csv`: run/rule/fold key, model, target band, predicted B/S,
  observed B/S (outcome role only), geometry source, predicted/observed kappa,
  per-rule between-seed sd, coverage and explicit eligibility reason.
- `calibration.json`, `readiness.json`, `analysis.json`: bias/coverage controls,
  oracle/resume/thread checks, gates, per-prediction pass/fail/uninformative,
  family-bootstrap intervals, all baselines and deviations.

Sort outputs by rule, seed, band, episode, segment. Write atomically then create
hash-checked `.done` markers. Checkpoints include walker position/heading, colour
field, visited mask, depth state, RNG state where relevant, open episodes,
accumulators and manifest identity. A changed recipe must not resume old state.
