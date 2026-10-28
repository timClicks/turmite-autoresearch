# Lab notebook: chirality versus letter-group baselines

### 2026-10-15 23:17 (+13:00) · b3a0f76 · intent

The user requested a direct training-only baseline comparison and within-group
scores in response to the paper critique. Register groups and predictions in
README.md before scoring; retain the original holdout and existing model.

### 2026-10-15 23:17 (+13:00) · b3a0f76 · assumption

The saved c_model.csv is the original model cohort and split. Verify against
probe_summary.csv and the 300-rule edgestats_sample.csv, and reconstruct the
chirality predictions independently before trusting its scores. Reusing this
inspected dataset limits the evidential status of this reanalysis.

### 2026-10-15 23:20 (+13:00) · b3a0f76 · observation

`uv run scripts/check_controls.py` (with the experiment path prefix) passed
three synthetic tests. `uv run experiments/archive/2026-10-chirality-baselines/scripts/compare.py`
produced `results/comparison.json`, `groups.{csv,json}` and
`held_out_predictions.csv`: all 300 calibration rules have eligible targets;
2,747 held-out rules reconstruct exactly. R²: one letter 0.58559, three
letters 0.80765, chirality 0.66002. The first registered prediction fails;
the second holds. Original predictions match reconstruction to 1e-14.

### 2026-10-15 23:20 (+13:00) · b3a0f76 · surprise

The critique's R²=0.88 is not present in the saved predictions or current
paper numbers. Both existing followup_stats.json and numbers.json already
give R²=0.660, correlation 0.869. The primary-agent response repeated the
critique's number without verifying it. Correct the premise explicitly.

### 2026-10-15 23:20 (+13:00) · b3a0f76 · interpretation

Chirality is not wholly uninformative within broad letter groups: their
within-group R² is 0.190 (L) and 0.164 (R). It nonetheless underperforms
the three-letter lookup and has essentially no pooled centered residual
skill within three-letter groups. Group-mean error and discrimination
must be kept distinct. These are observational comparisons of existing
targets; they do not establish the mechanism of growth.

### 2026-10-15 23:27 (+13:00) · b3a0f76 · observation

Regeneration by `scripts/verify_artifacts.py` (full uv command in README)
reproduces all four result files byte-for-byte; hashes in
`results/verification.json`. The three synthetic tests pass, the shareable
notebook executed three code cells without errors, and `cargo test --release`
passes (`results/release-tests.log`). The paper compiles without diagnostics;
the 38-page PDF's changed opening/comparison pages (1, 2, 20, 21) were rendered
for visual review. Recipe and PDF hash are in the verification record.

### 2026-10-15 23:27 (+13:00) · b3a0f76 · deviation

WSL has no Node or Poppler pdftotext. Used bundled Windows Node for the PDF
workflow initialization and a one-off `uv run --with pymupdf` renderer for
visual verification. No project dependencies changed. Physical calibration
was not repeated because no trajectory instrument/estimator/window changed;
synthetic statistical controls were run instead, as registered.

### 2026-10-15 23:27 (+13:00) · b3a0f76 · decision

Complete: scripts, machine-readable results, lab/shareable notebooks,
scientific note and manuscript comparison agree. Updated the abstract,
key-results summary, evidence table and figure caption to acknowledge the
stronger three-letter baseline. Retained all pre-existing work and made no
commit. Future work: independent rule-family holdout and initial-seed
replication; conditional rule-bootstrap intervals do not settle those questions.

### 2026-10-15 23:38 (+13:00) · 3d00123 · intent

The user requested a commit. The shared manuscript and its README/PDF contain
many unrelated uncommitted edits. Stage only this comparison against HEAD,
retaining the existing working versions. The committed source uses a provenance
footnote in place of Audit 42 because the expanded audit appendix is unrelated
uncommitted work. The staged manuscript compiles independently to 25 pages;
its source/PDF hashes and reviewed pages are in `results/staged-paper.json`.
The earlier 38-page PDF verification remains the record of the shared working
manuscript at analysis time, rather than the isolated commit's PDF.
