# Manuscript build

## October follow-up revision (2026-10-20)

Follows the blog assessment in commit `0e7d251`; scientific evidence is pinned
at `0de4d38de7c468583bc8c8aba4dc6ed54edada10`. No simulations, estimators or
scientific fits were changed. The abstract, key results, definitions, transport
discussion, edge-entry results, evidence table and conclusion now incorporate:

- the growth-adjusted uniform reference for window-normalized kappa, with the
  uniform-resampling calibration and walker-specific comparisons;
- the opening-run c law, both fresh-rule validation scores (including the
  broader-validation failure), flat-band ablations and failed mechanism targets;
- the registered no-direct-effect construction for the area-conditioned lead
  association, survivor selection and the still-unexplained shortening mutation;
- the failed same-turn square-loop test, surgery closed unrun, and the
  uninformative growth-clock support failure, with distinct verdicts.

The original census, exponents, numerical inputs and figure assets are retained.
`recent_findings_numbers.py` extracts the new numbers from committed summaries
into `recent_findings.json`, with input hashes. It does not invoke the original
analysis producer: that producer can omit Stage 4c when ignored dumps are absent.
Audits 44--48 preserve commands, seeds, windows, deviations and provenance limits.
The supplementary census gains `opening_run` and `c_lead_pred` (65 columns);
the prediction is explicitly labelled as fitted, with extrapolation outside the
stationary calibration class. A rounding correction to the blog's analytical
uniform reference (1.1101) is included with the paper revision.

Reproduce from the repository root in WSL, after setting
`export UV_PROJECT_ENVIRONMENT=$HOME/.venvs/turmite UV_LINK_MODE=copy`:

```bash
uv run research-outputs/scholarly-articles/cube-root-growth/recent_findings_numbers.py --check
uv run research-outputs/data-papers/rule-census/build_rule_census.py --check
uv run research-outputs/data-papers/walker-reference/build_walker_reference.py --check
typst compile --root . research-outputs/scholarly-articles/cube-root-growth/main.typ research-outputs/scholarly-articles/cube-root-growth/main.pdf
typst compile --root . --format png --ppi 55 research-outputs/scholarly-articles/cube-root-growth/main.typ 'tmp/paper-update/page-{p}.png'
cargo test --release > tmp/paper-update/release-tests.log 2>&1
```

Create `tmp/paper-update` first. To regenerate the extracted JSON rather than
check it, omit `--check`; this refreshes its recorded base commit. No dependency
declarations changed. Tools: Typst 0.15.1, uv 0.5.15, cargo 1.98.1. The release
suite passed (existing compiler warnings remain); both supplementary guards and
the extraction guard passed. The blog's production build and local-link check
passed (102 HTML pages). The 45-page PDF compiled without diagnostics, all pages
were visually reviewed in contact sheets, and the opening, new results and audit
pages were checked individually. No blank pages, clipping or overlap was found.
Final PDF SHA-256: `d1d68a9a7278e992121aaddc1fd637f9d48ddd4d0c6b25fa001adaf4f5d271ba`.
`revision_verification.json` records source/output hashes and validation scope;
temporary renders and logs are in `tmp/paper-update/` (ignored).

## Keep the census dataset current

`../../data-papers/rule-census/rule_census.csv` (moved from `supplementary/` on
2026-10-28; see `../../data-papers/README.md`) is the paper's per-rule supplementary
dataset (all 4083 swept rules, 65 columns; data dictionary in its README). It is a
join of committed result files, so it goes stale silently. Rebuild it and commit
the result in the same change whenever you touch anything it reads:

```bash
uv run research-outputs/data-papers/rule-census/build_rule_census.py
```

Rebuild when you: change the census classification, windows or fits
(`census.py`, `analyse_probe.py`); rerun or extend a sweep, the 10^9 follow-up or
highway confirmation; re-fit the `c` model; or change any census count quoted in
`main.typ` / `numbers.json`. After rebuilding, check that `rule_census.build.json`
still matches the paper (3512 census rules, 3055 analysed; blob median width
exponent 0.3326) and that the diff is what you expected. If you add a per-rule
quantity to the paper, add it as a column in the build script and the dictionary
rather than leaving it only in a figure script. The CSV is regenerated, never
hand-edited.

Guards (all call the same script):
- `build_rule_census.py --check` rebuilds in memory and exits 1 if the committed
  CSV or summary JSON differ, or if the table disagrees with `numbers.json`
  (census/builder/log/blob/analysed counts, blob median width exponent).
- `rebuild_figures.py` regenerates the table first and aborts if it disagrees with
  `numbers.json`; the table and builder are in its provenance hashes.
- `.githooks/pre-commit` runs `--check` when a staged file is one of the table's
  inputs. It is opt-in, once per clone: `git config core.hooksPath .githooks`
  (bypass a WIP commit with `--no-verify`).

## Accounting-identity criticism (2026-10-16)

Replaced the subtitle “a calibrated mean-field decomposition” with
“calibrated growth and boundary transport”. The methods now distinguish exact
window accounting, conditional power-law algebra and the missing dynamical
closure. Same-run reconstruction and prefactor collapse are diagnostic only;
the geometric amplitude also enters the prefactor. The forecast budget uses
area endpoints alone and tests persistence, not independent predictive value
of the separate factors. Interior colour/short-lag tests do not establish
uniform spatial occupation or stationary boundary access. The restricted
prefix score is predictive, not a causal share of variance.

The conclusion retains the growth census, predictive results and negative
controls while stating that the mechanism remains unresolved. Original
predictions and numerical inputs were retained. An interpretation correction
was appended to `notes/cube-root-hypothesis.md`; reviewer-response wording and
requirements for a substantive mechanism test are in
`notes/accounting-identity-response-2026-10-16.md`. This is an editorial audit
of existing evidence, not a new experiment. Prior working changes were kept;
no commit was made.

Reproduce in WSL from the repository root with
`export UV_PROJECT_ENVIRONMENT=$HOME/.venvs/turmite UV_LINK_MODE=copy`:

```bash
typst compile --root . research-outputs/scholarly-articles/cube-root-growth/main.typ research-outputs/scholarly-articles/cube-root-growth/main.pdf
cargo test --release
```

Typst compiled without diagnostics. The 39-page PDF's title, accounting,
prefix, forecast and limitations/conclusion pages (1, 8, 14, 15, 28) were
rendered and visually checked. PDF SHA-256:
`64920b08ca86eedb82537a48fd316146170874c27692b72517990e11b50f1dc4`.
Build, rendered-page inspection and release-test logs are in
`tmp/accounting-review/`. The full `cargo test --release` suite passed
(exit 0; compiler warnings remain). `git diff --check` passes for this edit.

## Chirality baseline comparison (2026-10-15)

Added a training-only comparison on the original 300 calibration and 2,747
held-out rules. Three-letter group means achieve R²=0.807648, compared with
0.585589 for one letter and 0.660023 for chirality. Chirality reduces SSE
by 17.96% against one-letter grouping but has 76.75% more SSE than the
three-letter lookup. Within broad L/R groups its R² is 0.189960/0.163770;
after centering within three-letter groups, pooled residual R² is about zero.
Paired rule-bootstrap intervals condition on the fitted models and do not
measure initial-seed or training uncertainty. The critique's quoted R²=0.88
does not match the existing files (R²=0.660, correlation 0.869).

The abstract, key results, comparison table, figure caption, evidence table
and Audit 42 now state this limitation. New paper numbers are extracted by
`chirality_baseline_numbers.py` from
`experiments/archive/2026-10-chirality-baselines/results/`, without editing legacy
results. Full registration, commands and caveats are in that experiment's
README and `notes/chirality-baselines-2026-10-15.md`.

Rebuild from WSL with the standard environment exports:

```bash
uv run experiments/archive/2026-10-chirality-baselines/scripts/compare.py
uv run research-outputs/scholarly-articles/cube-root-growth/chirality_baseline_numbers.py
typst compile --root . research-outputs/scholarly-articles/cube-root-growth/main.typ research-outputs/scholarly-articles/cube-root-growth/main.pdf
uv run --with pymupdf experiments/archive/2026-10-chirality-baselines/scripts/verify_artifacts.py
```

Release tests and three synthetic statistical controls pass; the shareable
notebook executed cleanly; analysis outputs reproduce byte-for-byte. The
38-page PDF compiled without diagnostics and pages 1, 2, 20 and 21 were
rendered and reviewed. Hashes are in the experiment's `results/verification.json`.
No project dependencies changed and no commit was made. Existing working-tree
changes were retained.

## Finding-led prose pass (2026-10-15)

Used the author-supplied podcast transcript as a guide to discoverability,
checking its framing against the current manuscript rather than treating it as
evidence. Rewrote the abstract and key results around concrete findings: the
eightfold time cost of doubling width under cube-root scaling, the bulk/edge
contrast with the rotor, drifting boundary occupation, the two transport
predictors, future-window forecasts, the limits of the tested memory models,
and the late column-sweeper transition. The introduction now states the question
and result before discussing the literature. Prior-work distinctions remain.

Added a plain-language explanation of edge entry versus edge occupation before
the decomposition, and a physical lead for the chirality result. Split dense
prefix, forecast, control, profile, surface-width and conclusion paragraphs at
changes of question or evidential role. Promoted the existing `RLRLLL` case from
the limitations bullet to its own results subsection; the limitations retain a
cross-reference. Author statements stay together in the PDF.

The body retains every pre-existing math span, numerical input reference and
audit link (multiset comparison against the session's starting source in
`tmp/prose-review/before.typ`). Measurements, numerical JSON inputs, figures,
estimators, dependencies and registration records were not changed. The cone
remains a conditional consistency check; temporal width slopes are not spatial
roughness exponents; prefix prediction retains its stationary-cohort and
within-family limits; a board escape is not a highway detection. The transcript's
"twice as rough" and universal cone language were not adopted.

Verification from the repository root in WSL:

```bash
export UV_PROJECT_ENVIRONMENT=$HOME/.venvs/turmite UV_LINK_MODE=copy
typst compile --root . research-outputs/scholarly-articles/cube-root-growth/main.typ research-outputs/scholarly-articles/cube-root-growth/main.pdf
typst compile --root . --format png --ppi 55 research-outputs/scholarly-articles/cube-root-growth/main.typ 'tmp/prose-review/page-{p}.png'
cargo test --release > tmp/prose-review/release-tests.log 2>&1
uv run tmp/prose-review/review.py > tmp/prose-review/editorial-check.log 2>&1
```

The last command is a local editorial comparison/contact-sheet helper, not an
analysis producer. Typst compiled without diagnostics; all 38 rendered pages
were reviewed in contact sheets, with individual checks of the findings page
and moved case study. Release tests passed (exit 0; existing warnings remain).
The manuscript passes `git diff --check`. PDF SHA-256:
`413c0c272ef46c48b8ee151643f4a03aba1d917fb90b8b1d6cf5a445f0575f1a`.
Existing working-tree edits were preserved. Base commit:
`b3a0f762ac2230b5df92188206a4d3a1081897be`. No commit was made.

## Heading and navigation pass (2026-10-15)

Replaced generic section titles with descriptions of the question, measurement
or evidential limit. Promoted the major paragraph topics to numbered subsections:
calibration uncertainty, seed variability, occupation reproducibility, prefix
prediction, future-window forecasts, growth outliers, mixing, visit profiles and
surface-width comparisons. The mechanism tests now identify the tested
explanations and their constraints; interior-return tests have their own
subheading. Existing reference labels are preserved. No measurements, numerical
inputs or scientific body claims were changed. Prior working-tree edits were
retained; no commit was made.

Verification (from the repository root in WSL with the environment exports below):

```bash
typst compile --root . research-outputs/scholarly-articles/cube-root-growth/main.typ research-outputs/scholarly-articles/cube-root-growth/main.pdf
typst compile --root . --format png --ppi 75 research-outputs/scholarly-articles/cube-root-growth/main.typ 'tmp/heading-review/final-{p}.png'
cargo test --release > tmp/heading-review/release-tests.log 2>&1
```

Typst compiled without diagnostics. The 36-page layout was reviewed in contact
sheets, then the shortened main headings were checked individually in the final
render. The release suite passed (exit 0); `git diff --check` passes for the edited
manuscript files. PDF SHA-256:
`f181c4dd2cd7bb27c10c6568cca4514baa0678a7e51e6d7ab6d212640e58eb18`.

## Bounding the dynamics: editorial pass (2026-10-15)

Reframed the working manuscript's negative tests as constraints on candidate
mechanisms. Section 5.1 now leads with the limits of local summaries, tested
stochastic memory and shallow trapping. The boundary-layer comparison emphasizes
the coexistence of similar dwell times and widely different occupation; arrow
randomisation separates occupation from edge-entry bias. Related framing in the
key results, introduction, forecast discussion, profile/width comparisons,
evidence table and conclusion is consistent with this approach.

Registered bands, gate outcomes, exploratory labels, control limitations and
audit links remain explicit. These are finite-window constraints on the tested
models, not proof by exhaustion of all mechanisms. Interior returns remain a
candidate explanation, not a causal conclusion established by the local tests.
No numerical inputs, measurements, estimators, dependencies or registration
records were changed. Prior working-tree edits were retained; base commit
`b3a0f762ac2230b5df92188206a4d3a1081897be`. No commit was made.

Verification from the repository root in WSL, with the environment exports below:

```bash
typst compile --root . research-outputs/scholarly-articles/cube-root-growth/main.typ research-outputs/scholarly-articles/cube-root-growth/main.pdf
typst compile --root . --format png --ppi 75 research-outputs/scholarly-articles/cube-root-growth/main.typ 'tmp/bounding-review/page-{p}.png'
cargo test --release > tmp/bounding-release-tests.log 2>&1
```

Typst compiled without diagnostics (`tmp/bounding-review/build.log`). All 36
pages were rendered and reviewed in contact sheets, with individual checks of
the mechanism matrix, boundary-layer discussion and evidence table. The release
suite passed (exit 0), and the manuscript passes `git diff --check`.
PDF SHA-256:
`4cedf05bfab075d0b9fc5aeb918486be1a7112c6ca8f289ab4bb0e4707ac76f7`.

## Reproducibility appendix editorial pass (2026-10-15)

Local paths and note filenames have been moved from the reading text, captions
and evidence table into `audit.typ`, included by `main.typ`. The dedicated
“Reproducibility & Preregistration Audit Table” preserves 41 records with exact
locations, analysis scripts, available seed declarations, hypothesis titles and
Git timestamps. Main-text links identify the corresponding audit entries.
The audit distinguishes author-recorded registration times, exploratory tests,
earliest available path commits (often migration commits), uncommitted records
and missing referenced files. It does not treat a Git timestamp as proof of
preregistration. W3c sampling/patch seeds and Arm B seeds were checked directly
against the sampler and saved specifications. No scientific measurements,
generated numerical inputs or dependencies were changed by this pass.

Rebuild with the existing Typst command below; the appendix is manuscript source,
not generated measurement data. Verification: Typst compiled without diagnostics,
all referenced audit IDs resolve, no inline repository paths remain in reading
text, the 36-page PDF was rendered, and appendix layouts were visually checked.
`cargo test --release` passed; the local verification log is
`tmp/provenance-edit/release-tests.log`. Existing working-tree edits were retained;
no commit was made.

From the repo root (WSL; see AGENTS.md for the env):

    export UV_PROJECT_ENVIRONMENT=$HOME/.venvs/turmite UV_LINK_MODE=copy
    uv run research-outputs/scholarly-articles/cube-root-growth/compute_numbers.py   # data/* -> research-outputs/scholarly-articles/cube-root-growth/numbers.json (bootstrap seed 20261012)
    uv run research-outputs/scholarly-articles/cube-root-growth/figures.py           # -> research-outputs/scholarly-articles/cube-root-growth/fig/*.pdf
    typst compile --root . research-outputs/scholarly-articles/cube-root-growth/main.typ research-outputs/scholarly-articles/cube-root-growth/main.pdf

Typst is installed via `cargo install --locked typst-cli`. Numbers in main.typ are generated, with the exceptions below;
inputs are the data files listed in the scripts, produced by the commands in notes/. Most numbers come from numbers.json; the sweep tallies (4083, 578, 3505+7, 304 builders), the 24-seed item4 and 12-patch item21 designs, the a4c edge exponents (0.22-0.25, 0.10-0.13) and the 300-rule c-model sample are typed by hand from the cited data/*.txt files and should be moved into compute_numbers.py.
Exception: numbers quoted from the text outputs `experiments/archive/2026-10-a1-kappa/results/a1b_icc.txt`, `a1_kappa_proxy.txt`, `a1c_predict.txt`, `a1_edge_q.txt`,
`edge_exponent.txt`, `shape_stats.txt`, `b4_stats.txt`, `b5_stats.txt` are typed in main.typ with the file named beside them (the 2026-10-13 PM numbers h1, h3, g1 are instead parsed from `experiments/archive/2026-10-h1-lacunarity-decomposition/results/h1_lacunarity.txt`, `h3_collapse.txt`, `g1_stats.txt`, `g1_ribbon.log` by compute_numbers.py).
Data files were produced from an uncommitted working tree (no commit hash available yet).

Transport forecasts: `uv run experiments/archive/2026-10-transport-forecast/scripts/transport_forecast.py > experiments/archive/2026-10-transport-forecast/results/transport_forecast.log`.
The manuscript loads `experiments/archive/2026-10-transport-forecast/results/transport_forecast.json` directly; `--root .` permits
that repository-relative input. Registration, controls, exclusions and verification
are in `notes/transport-forecast-2026-10-13.md`; input hashes and seed are in the JSON.

Illustrative figures (`fig/gallery.pdf`, `fig/growth_curves.pdf`): `uv run research-outputs/scholarly-articles/cube-root-growth/gallery.py`. The ant grids come from
`examples/snapshot.rs` (commands in the script's docstring; 64 MB each, not committed). Growth curves use
`experiments/archive/2026-10-probe-growth-census/results/probe_all.csv` and `experiments/archive/2026-10-calib-instrument-calibration/results/calib_rotor.csv` (rotor seed `rotor:0`).

Explanatory figures (`fig/{mechanics,timeline,edge,timelapse,census,rotor}.pdf`): `uv run research-outputs/scholarly-articles/cube-root-growth/textbook_figs.py` (~40 s).
Needs `$GAL/RLL_k{14,17,20,23}.bin` from `examples/snapshot.rs` (commands in the script docstring); the rest is simulated
in the script (reference ant, rotor with numpy seed 1) or read from `experiments/archive/2026-10-census-sweeps/results/sweep_v2.csv` and `experiments/archive/2026-10-census-sweeps/results/census.csv`.

All figure scripts (`figures.py`, `gallery.py`, `textbook_figs.py`) import `research-outputs/scholarly-articles/cube-root-growth/style.py` for the palette and conventions (colour meanings are documented at its top); change colours there, not in the scripts.

Memory-walker comparison figures: after building the probe and completing
`uv run experiments/archive/2026-10-memory-walkers/scripts/memory_walkers_pilot.py $HOME/turmite-target-memory/release/probe`,
run `cargo run --release --example memory_paths -- 301 16 > experiments/archive/2026-10-memory-walkers/dumps/memory_paths.csv`
and `uv run research-outputs/scholarly-articles/cube-root-growth/memory_figures.py`. The dump is gitignored; source and input
hashes are in `research-outputs/scholarly-articles/cube-root-growth/fig/memory_recipe.json`. The new typed pilot table and
width-radius prose use `experiments/archive/2026-10-memory-walkers/results/memory_walkers_pilot/summary.json` and
`experiments/archive/2026-10-w-width-radius-refit/results/width_radius_refit.json`; regenerate the latter with
`uv run experiments/archive/2026-10-w-width-radius-refit/scripts/width_radius_refit.py`. Predictions and results are preserved in
`notes/walker-comparisons-2026-10-13.md`.

## Typesetting design (2026-10-13)

The manuscript uses Libertinus Serif for reading text, the title and headings,
DejaVu Sans for captions and page furniture, and DejaVu Sans Mono for rule strings.
Typst bundles the mathematical font; the other families must be available to
`typst fonts` (all are installed in the current WSL environment). The ink,
near-black accent and warm-grey caption colours are defined at the top of `main.typ`.
The title and abstract form an opening page; key results begin the next page.
References start on a fresh page to avoid a trailing isolated entry.

Rebuild: `typst compile --root . research-outputs/scholarly-articles/cube-root-growth/main.typ research-outputs/scholarly-articles/cube-root-growth/main.pdf`.
Visual QA: `typst compile --root . --format png --ppi 100 research-outputs/scholarly-articles/cube-root-growth/main.typ 'tmp/paper-design/page-{p}.png'`.
This changes presentation only; generated numbers and figure inputs are unchanged.

## Figure design and title-page image (2026-10-14)

`uv run research-outputs/scholarly-articles/cube-root-growth/rebuild_figures.py` regenerates all figure assets and the manuscript
from existing inputs. It writes `fig/rebuild.log` and `fig/rebuild_recipe.json`
with the git commit, source/input hashes, seeds and output hashes. Use the WSL
environment exports above. Snapshot inputs still come from `$GAL` (default
`~/gal`); no measurements or sweeps are rerun by this command.

Figures use thin neutral axes, sparse outward ticks, no grid or enclosing box,
outline histograms rather than overlapping fills, and direct endpoint labels
for the six-rule transport and growth comparisons. Short leaders connect labels
to their true endpoints when label spacing changes. Dense ensemble comparisons
retain a shared legend. Scientific colour meanings are unchanged. Vector PDFs
embed TrueType fonts; matching PNGs are generated for inspection, and PDF dates
are omitted for reproducible output.

`textbook_figs.py` also creates `fig/hero.pdf`: ant RLL and rotor occupation fields
at `2^22` steps (blank-board ant; rotor initial-arrow seed 1), normalized by `t/A`,
with a shared greyscale from 0 to 4, clipping higher values. Each territory is
fitted to its panel, so physical sizes should not be compared. This illustration
introduces the bulk/edge comparison; the measured edge exponents remain in the
body of the paper. It is not a new measurement or an estimator change.

## Kappa prediction update (2026-10-15)

The abstract, key results, introduction, factor discussion, evidence table,
length limitation and conclusion now distinguish failed simple-feature models
from W3c's prefix-8 lookup on fresh stationary rules of lengths 13–14.
Prefix-only strict held-out R² is 0.633; adding prefix to early area raises
R² from 0.497 to 0.737 (gain 0.240, rule-bootstrap interval 0.148–0.347).
The six-letter gain fails its registered threshold. The exploratory crossed
comparison is labelled as such: pooled training degrades the gain even on
stationary test rules. This is within-prefix-family transfer under measured
regime filters, not an unrestricted rule-string predictor or mechanism.
The excursion discussion also records the independent-seed-role association
without reversing the earlier failed noise-floor gate.

New numbers are extracted, not hand-edited, from small existing results:

```bash
export UV_PROJECT_ENVIRONMENT=$HOME/.venvs/turmite UV_LINK_MODE=copy
cd /mnt/f/Code/turmite
uv run research-outputs/scholarly-articles/cube-root-growth/kappa_prediction_numbers.py
typst compile --root . research-outputs/scholarly-articles/cube-root-growth/main.typ research-outputs/scholarly-articles/cube-root-growth/main.pdf
```

`kappa_prediction.json` includes the commit and SHA-256 of its producing script
and W3c stats/cross-check inputs. No fits or simulations were rerun and no
dependencies were changed. The PDF was rebuilt; the evidence table now uses
bounded column proportions so long evidence paths do not squeeze the status
column. Research proposals, separate from findings and preregistrations, are in
`notes/paper-gaps-research-avenues-2026-10-15.md`.

Verification: the κ extraction reran byte-identically (JSON SHA-256
94fb4290e9945d90f5867a275311cc88d7c38ddee99623e2bd6bba33f5e280fa).
Typst compiled without diagnostics (`kappa_build.log`); updated abstract,
key results, prefix discussion, evidence table and conclusion pages were
rendered and visually checked. Final PDF: 24 pages, SHA-256
871ec5da0ff063837540e7679f01a05fa82b0437acb28e2c2a03da1b1d4a89b2.
`rebuild_figures.py` now refreshes the extracted κ JSON before building and
includes its producer/input files in the rebuild provenance. This editorial
update introduces no simulator changes; the release suite passed during the
preceding phase-reset work. No commit was made.

## Typography and figure panels (2026-10-15)

Presentation pass on the existing working manuscript (base commit
`da88e61b690507526ba4e2a2c017d9c7941beb91`; prior manuscript edits preserved).
Body text remains Libertinus Serif, now 11.25 pt with 0.68 em leading and
1.3 em paragraph spacing, without first-line indents. Paragraph spacing exceeds
leading deliberately so paragraph boundaries are visible. Lato replaces
DejaVu Sans for headings, captions and page furniture; monospace is unchanged.
Section headings are bold sans serif, with explicit spacing. The opening page
has its own tighter title/abstract settings rather than inheriting body spacing.

Figures and numbered tables sit in pale neutral panels with 11 pt inset,
a 0.45 pt border and 3 pt corners. Captions are left aligned, 9 pt, dark ink.
The title-page illustration uses the same panel treatment. Existing figure
assets, scientific colour meanings, prose, inputs and numerical results are
unchanged. Evidence-table rows stay together and its column headings repeat
on continuation pages. The resulting manuscript is 25 pages (previously 24).

Reproduce from the repository root in WSL:

```bash
export UV_PROJECT_ENVIRONMENT=$HOME/.venvs/turmite UV_LINK_MODE=copy
typst compile --root . research-outputs/scholarly-articles/cube-root-growth/main.typ research-outputs/scholarly-articles/cube-root-growth/main.pdf
typst compile --root . --format png --ppi 75 research-outputs/scholarly-articles/cube-root-growth/main.typ 'tmp/typography-review/page-{p}.png'
cargo test --release > tmp/typography-release-tests.log 2>&1
```

Typst compiled without diagnostics. All pages were rendered and reviewed in
contact sheets, with larger checks of the opening page, representative figure
and equation pages, and the two-page evidence table. No figure regeneration,
simulations, estimator changes or dependency changes were required.
The full `cargo test --release` suite passed (exit 0; existing compiler
warnings remain). Final PDF SHA-256:
`4031968ec8618790236cf8f9d7830a9ebb6cd73f1c545f7b3ff0d9fb095f1c92`.
No commit was made.

## Literature positioning update (2026-10-15)

The literature review in `experiments/archive/2026-10-literature-review/` removes the broad absence-of-prior-growth claim. User-supplied Meng–Cohen1994 full text directly measures area and boundary growth in periodic binary media and supplies a boundary-access mechanism anticipating the scaling argument. The manuscript distinguishes uniform multicolour census coverage and separately measured c/kappa from this prior work. It also corrects cone assumptions, rotor theorem scope, finite-horizon highway language, boundary estimator conventions, matched-step wording and selected-cohort scope. Wavelength outcomes remain mixed and no interface class is assigned.

Rebuild with the existing Typst command above; final compile had no diagnostics. The resulting27-page PDF and selected changed pages were rendered/checked; exact hashes are in `experiments/archive/2026-10-literature-review/results/verification.json`. The review notebook executed cleanly. No figures or measurements were regenerated, no dependency declarations changed, no simulator/estimator change required Rust tests, and no commit was made. Coverage and source-ambiguity limitations are explicit in the report.

## Audit moved to supplementary material (2026-10-20)

The reproducibility and preregistration audit is now a separate ten-page
`supplementary/reproducibility-audit.pdf`. The main paper is 37 pages.
All 48 audit entries, their numbers and provenance caveats are retained in
`audit.typ`, included by the standalone supplementary source. Main-text audit
links open the companion PDF; locate entries by their unchanged audit numbers.
Keep the `supplementary/` directory beside `main.pdf` when distributing the files
so relative PDF links work (viewer support varies).

Rebuild both from the repository root in WSL:

```bash
export UV_PROJECT_ENVIRONMENT=$HOME/.venvs/turmite UV_LINK_MODE=copy
typst compile --root . research-outputs/scholarly-articles/cube-root-growth/main.typ research-outputs/scholarly-articles/cube-root-growth/main.pdf
typst compile --root . research-outputs/scholarly-articles/cube-root-growth/supplementary/reproducibility-audit.typ research-outputs/scholarly-articles/cube-root-growth/supplementary/reproducibility-audit.pdf
```

`rebuild_figures.py` also builds and hashes both PDFs. Both standalone builds
completed without diagnostics. The supplement's opening and final pages and the
main paper's final bibliography page were rendered and visually checked.
This is an editorial relocation; no data, figures, fits or simulations changed.`cargo test --release` passed (exit 0; existing warnings remain).
