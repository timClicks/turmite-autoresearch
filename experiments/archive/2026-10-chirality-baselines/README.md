# Does chirality predict more than letter groups?

## Registered 2026-10-15 23:17 NZDT, before scoring

Base commit: `b3a0f762ac2230b5df92188206a4d3a1081897be`, with existing
uncommitted work retained. This is a critique-driven reanalysis of an already
inspected scatter plot, not an independent prospective validation.

Question: how much does the existing chirality model add beyond coarse groups
defined by rule letters, on exactly its original held-out rules?

Prediction: the primary one-letter baseline explains most of the pooled
variation. Operationally, its held-out R² will be within 0.05 of chirality.
We also expect chirality to reduce squared error by less than 10% against
the three-letter baseline. Both predictions can fail; report all scores.

Fixed method, without selecting groups using measured or predicted c:

- Read `2026-10-probe-growth-census/results/c_model.csv`. Retain its
  non-bursty cohort, targets, predictions and `held_out` flag exactly.
- Primary baseline: calibration-target mean by `rule[1]` (the letter after
  the leading R). Secondary baseline: mean by `rule[1:4]`, falling back to
  the primary group mean, then the overall calibration mean, for absent groups.
  Short rules have their available suffix as a separate group.
- Fit means only on eligible non-held-out rows. Original chirality constants
  used the full 300-rule edge-statistics sample; report calibration-rule
  overlap and eligible counts explicitly, rather than claiming equal targets.
- Report original R² (held-out-mean denominator), strict R² (calibration-mean
  predictor denominator), SSE, RMSE, MAE, and paired SSE reduction of chirality
  versus each baseline, globally and within each predefined letter group.
  A within-group R² uses that held-out group's mean; it is a descriptive
  denominator, never a fitted prediction. Also report pooled within-group R²
  after centering both observations and predictions within held-out groups:
  this isolates discrimination from group-mean calibration error.
- Paired rule bootstrap: 4000 resamples, seed 20261046, stratified by the
  primary letter group, with fitted models fixed. Report percentile 95%
  intervals for SSE reduction and delta R². These quantify held-out rule
  variation conditional on the fitted models, not seed noise or training
  uncertainty. No ant trajectories or probe estimators change.
- Synthetic controls verify zero residual skill for group-constant predictions,
  perfect residual skill for a correct predictor, negative skill for a wrong
  predictor, and training-only means/fallbacks. Do not infer within-group
  prediction from the extremes in a scatter plot alone.

Inputs are committed source results; outputs belong only in this folder.
Save per-rule predictions, group statistics, a machine-readable summary with
input/script hashes and exact command, and an executed shareable notebook.

## Reproduction

From WSL at `/mnt/f/Code/turmite`, first set:

```bash
export UV_PROJECT_ENVIRONMENT=$HOME/.venvs/turmite UV_LINK_MODE=copy
uv run experiments/archive/2026-10-chirality-baselines/scripts/compare.py
uv run experiments/archive/2026-10-chirality-baselines/scripts/check_controls.py
uv run --with nbconvert --with ipykernel --with nbformat jupyter nbconvert --to notebook --execute --inplace experiments/archive/2026-10-chirality-baselines/notebook.ipynb
cargo test --release
```

## Results (2026-10-15 23:23 NZDT)

The original cohort and predictions reconstruct exactly (tolerance 1e-14).
All 300 calibration rules have eligible targets; 2,747 rules are held out.
Results are in `results/comparison.json`, per-group `groups.{csv,json}`, and
per-rule `held_out_predictions.csv`; source hashes and command are embedded.

| Prediction | Held-out R² | RMSE |
| --- | ---: | ---: |
| One-letter mean | 0.585589 | 0.081457 |
| Three-letter mean | 0.807648 | 0.055496 |
| Chirality | 0.660023 | 0.073780 |

Chirality reduces SSE by 17.96% [15.92, 20.08]% against the one-letter mean,
but has 76.75% [65.42, 88.93]% more SSE than the three-letter mean. Intervals
are the registered conditional paired rule bootstrap. Three-letter fallback
is needed for the short held-out rule `RLL`; no target-dependent selection.

Within the primary L/R groups (1,452/1,295 test rules; 173/127 training rules),
chirality R² is 0.189960/0.163770. Its pooled centered within-three-letter R²
is -0.00006245; the raw within-group R², retaining group-mean bias, is
-0.775530. Centered scores are descriptive, not predictions fitted on test data.
The first registered prediction fails (one-letter gap 0.07443 > 0.05).
The second holds (chirality underperforms the three-letter baseline).

The critique's R²=0.88 is not reproduced: the original files already record
R²=0.660 and correlation 0.869. Chirality has modest information within broad
groups; after conditioning on three letters there is essentially no residual
discrimination. These data do not establish a growth mechanism or seed robustness.
Rule-bootstrap intervals condition on fitted models and assume independent
rules despite related/repeated rule strings. No physical instrument or window
changed, so walker calibration was not rerun. Synthetic controls pass.

The executed `notebook.ipynb` reads the small versionable result files only;
new files await a user-requested commit. No dependencies were added.
The paper extracts results with
`uv run research-outputs/working-papers/cube-root-growth/chirality_baseline_numbers.py`.

Target definition: the existing `probe_summary.csv` uses final-window
`new_cells / boundary_steps` at k=26 (the octave from 2^25 to 2^26), as
defined in `experiments/_lib/analyse_probe.py`; exponent fits use k=20..26
but c here is the final-window value, not a fitted or pooled c. This
reanalysis inherits the saved calibration membership and blank-board targets;
it draws no new train/test split or initial conditions.

Verification: three synthetic control tests pass; `cargo test --release`
passes; the notebook executes three code cells cleanly; repeating all four
analysis outputs gives identical bytes. The paper compiles without
diagnostics; pages 1, 2, 20 and 21 were rendered and reviewed. Verification
hashes and exact command are in `results/verification.json`. To repeat:

```bash
uv run --with pymupdf experiments/archive/2026-10-chirality-baselines/scripts/verify_artifacts.py
```

PyMuPDF is a one-off verification dependency under uv, not a change to the
project dependency declarations. Rendered inspection pages stay in ignored
`scratch/`. The PDF workflow used bundled Node on Windows because WSL has
no `node`, and PyMuPDF because Poppler's `pdftotext` is unavailable in WSL.
