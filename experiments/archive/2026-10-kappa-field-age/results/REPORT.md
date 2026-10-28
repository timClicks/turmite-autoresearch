# Instrument feasibility results

This report supersedes the scaffold's NOT RUN status. Scientific confirmation has **not** run.

Frozen pilot: 44 rules x 4 starts, three area bands; cap 2^30, grid 4096, four workers. Base commit `b3a0f762ac2230b5df92188206a4d3a1081897be`; dirty source hashes and seed identities are in [manifest](pilot-v2.manifest.json).

| Band start | Completed / requested | Unresolved interior time | Minimum completed entry episodes |
|---|---:|---:|---:|
| 32768 | 176 / 176 | 0 | 1018 |
| 131072 | 176 / 176 | 0 | 4085 |
| 524288 | 168 / 176 | 0 | 0 |

No-escape gate: **True**. All-complete gate: **False**. Quarter-cap reserve gate: **False** (max final step 1,073,741,824). Ant batch wall time 757.9 s; measured whole-process peak RSS 514.2 MiB (four concurrent jobs).

## Instrument validation

Four reference/property tests check discovery times, exact departure counts, nonzero patch phase offsets, visited-boundary rim census, offline fragment accounting, follow-up past band edges, right censoring, and rotor/random-walk paths. Full release tests passed; see the tail-budget results/instrument-release-tests.log.

Sampled thread replay: **True**, 8 specs and 48 files, one versus six workers at the two profile bands. Finished-trajectory resume preserves bytes. Full all-seed replay and mid-trajectory state checkpoints are **not** validated.

Existing pool support before matching: 169 stationary and 23 drifting rules. The latter is below the required 24 even without matching; exact length/prefix matching retains 22 pairs. See cohort_audit.json.

## Coverage by pre-existing stratum

| Stratum | Area 32768 | Area 131072 | Area 524288 |
|---|---:|---:|---:|
| stationary | 88 / 88 | 88 / 88 | 88 / 88 |
| drifting | 88 / 88 | 88 / 88 | 80 / 88 |

Synthetic exogenous-age chain (N=400,000, seed 2026101581): known return-hazard contrast 0.24, estimated 0.239944; after within-stratum label permutation 0.002478. Both four-standard-error calibration checks pass. This calibrates transition-frequency estimation, not a kappa model or a physical ageing intervention.

**Original cohort feasibility gate failed:** FAILED: only 22 exact matched pairs in existing pool. The pilot uses the 44 supported rules (22 exact length/prefix-matched pairs). This does not silently replace the planned 48-rule confirmation cohort.

## Noncomplete trajectories

These remain in every coverage denominator; missing-band features are null, not zero effects.

- `RLLLLLLRRRRR@2026101511`: budget, final step 1073741824, visited cells 408316.
- `RLLLLLLRRRRR@2026101512`: budget, final step 1073741824, visited cells 397468.
- `RLLLLLLRRRRR@2026101513`: budget, final step 1073741824, visited cells 392092.
- `RLLLLLLRRRRR@2026101514`: budget, final step 1073741824, visited cells 403732.
- `RLLLLRRLLRRR@2026101511`: budget, final step 1073741824, visited cells 498388.
- `RLLLLRRLLRRR@2026101512`: budget, final step 1073741824, visited cells 503496.
- `RLLLLRRLLRRR@2026101513`: budget, final step 1073741824, visited cells 492960.
- `RLLLLRRLLRRR@2026101514`: budget, final step 1073741824, visited cells 500324.

## Split-seed feature reliability (descriptive)

Spearman correlation across rules between first two and last two pilot seeds, restricted to rules with all four starts attaining the band and the feature observed. Contributing rule counts are shown in parentheses. No bootstrap inference is made; coverage denominators retain every requested start. The CSV includes every seed and between-seed dispersion is in the summary JSON.

| Feature | Area 32768 | Area 131072 | Area 524288 |
|---|---:|---:|---:|
| immature | 0.916 (44) | 0.847 (44) | 0.860 (42) |
| median_log_age | 0.413 (44) | 0.321 (44) | 0.718 (42) |
| cycle_variance | 0.910 (44) | 0.869 (44) | 0.846 (42) |

## Meaning and remaining work

These results establish observation/accounting feasibility at the measured scales and describe repeatability. They do not test T1/T2 or A1/A2/A3, compare tail or age features with kappa, establish causal mechanisms, or calibrate a survival-family fit or drift forecast.

Confirmation remains unregistered and unlaunched. Before confirmation: implement and byte-test mid-trajectory state checkpoints; calibrate/freeze the survival family and predictor loss; freeze grouped rule folds and seed roles; resolve the failed age cohort support gate explicitly; choose seed counts using pilot feature reliability. Retain the original thresholds and report deviations prospectively. No successful scientific prediction is claimed.

## Reproduce

Use WSL from the repo root with `export UV_PROJECT_ENVIRONMENT=$HOME/.venvs/turmite UV_LINK_MODE=copy`. Source-hash guards reject changes to registered inputs; retain old manifests and use a new run label for changed sources.

```bash
cargo build --release --example kappa_tail_budget_sampler --example kappa_field_age_sampler --example kappa_tail_budget_calibrate
uv run experiments/archive/2026-10-kappa-field-age/scripts/calibrate.py
uv run experiments/archive/2026-10-kappa-field-age/scripts/run.py --name pilot-v2
uv run experiments/archive/2026-10-kappa-field-age/scripts/summarize.py
uv run experiments/archive/2026-10-kappa-field-age/scripts/verify.py
uv run experiments/archive/2026-10-kappa-field-age/scripts/report.py
cargo test --release
```

The pilot itself is frozen prospectively in pilot-v2.manifest.json. Its exact preparation command is recorded there. pilot-v1 was rejected before simulation because an unrelated module export changed src/lib.rs; its manifest and failure log are retained.
