# Instrument feasibility results

This report supersedes the scaffold's NOT RUN status. Scientific confirmation has **not** run.

Frozen pilot: 44 rules x 4 starts, three area bands; cap 2^30, grid 4096, four workers. Base commit `b3a0f762ac2230b5df92188206a4d3a1081897be`; dirty source hashes and seed identities are in [manifest](pilot-v2.manifest.json).

| Band start | Completed / requested | Unresolved interior time | Minimum completed entry episodes |
|---|---:|---:|---:|
| 32768 | 176 / 176 | 0 | 1018 |
| 131072 | 176 / 176 | 0 | 4085 |
| 524288 | 176 / 176 | 0 | 16362 |

No-escape gate: **True**. All-complete gate: **True**. Quarter-cap reserve gate: **False** (max final step 831,505,321). Ant batch wall time 655.4 s; measured whole-process peak RSS 530.4 MiB (four concurrent jobs).

## Instrument validation

Four reference/property tests check discovery times, exact departure counts, nonzero patch phase offsets, visited-boundary rim census, offline fragment accounting, follow-up past band edges, right censoring, and rotor/random-walk paths. Full release tests passed; see the tail-budget results/instrument-release-tests.log.

Sampled thread replay: **True**, 8 specs and 48 files, one versus six workers at the two profile bands. Finished-trajectory resume preserves bytes. Full all-seed replay and mid-trajectory state checkpoints are **not** validated.

Known-answer renewal calibration uses 16 independent seeds per law, 20,000 cycles per seed. Mean interior durations (mean +/- between-seed sd; known mean):

- geometric: 4.011272 +/- 0.018268; known 4.000000; bias +0.011272.
- mixture: 11.448353 +/- 0.282892; known 11.500000; bias -0.051647.
- serial_mixture: 11.519500 +/- 0.447971; known 11.500000; bias +0.019500.

All three predeclared four-standard-error Monte Carlo checks pass. These calibrate the actual episode accountant, including a serially correlated mixture, not a fitted survival family.

## Split-seed feature reliability (descriptive)

Spearman correlation across rules between first two and last two pilot seeds, restricted to rules with all four starts attaining the band and the feature observed. Contributing rule counts are shown in parentheses. No bootstrap inference is made; coverage denominators retain every requested start. The CSV includes every seed and between-seed dispersion is in the summary JSON.

| Feature | Area 32768 | Area 131072 | Area 524288 |
|---|---:|---:|---:|
| entry_mean | 0.656 (44) | 0.635 (44) | 0.847 (44) |
| tail_probability_64 | 0.957 (44) | 0.962 (44) | 0.985 (44) |
| tail_mean_64 | 0.863 (42) | 0.828 (43) | 0.921 (43) |

## Meaning and remaining work

These results establish observation/accounting feasibility at the measured scales and describe repeatability. They do not test T1/T2 or A1/A2/A3, compare tail or age features with kappa, establish causal mechanisms, or calibrate a survival-family fit or drift forecast.

Confirmation remains unregistered and unlaunched. Before confirmation: implement and byte-test mid-trajectory state checkpoints; calibrate/freeze the survival family and predictor loss; freeze grouped rule folds and seed roles; resolve the failed age cohort support gate explicitly; choose seed counts using pilot feature reliability. Retain the original thresholds and report deviations prospectively. No successful scientific prediction is claimed.

## Reproduce

Use WSL from the repo root with `export UV_PROJECT_ENVIRONMENT=$HOME/.venvs/turmite UV_LINK_MODE=copy`. Source-hash guards reject changes to registered inputs; retain old manifests and use a new run label for changed sources.

```bash
cargo build --release --example kappa_tail_budget_sampler --example kappa_field_age_sampler --example kappa_tail_budget_calibrate
uv run experiments/archive/2026-10-kappa-tail-budget/scripts/calibrate.py
uv run experiments/archive/2026-10-kappa-tail-budget/scripts/run.py --name pilot-v2
uv run experiments/archive/2026-10-kappa-tail-budget/scripts/summarize.py
uv run experiments/archive/2026-10-kappa-tail-budget/scripts/verify.py
uv run experiments/archive/2026-10-kappa-tail-budget/scripts/report.py
cargo test --release
```

The pilot itself is frozen prospectively in pilot-v2.manifest.json. Its exact preparation command is recorded there. pilot-v1 was rejected before simulation because an unrelated module export changed src/lib.rs; its manifest and failure log are retained.
