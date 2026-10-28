# Execution plan — shared requirements

The experiment-specific hypotheses and candidate sample sizes are in README.md.
This is a scaffold, not a frozen registration. No scientific outputs exist.

## 1. Inspect and calibrate

Read the mechanism note, linked prior failures, current source, and AGENTS.md.
Audit available committed summaries before deciding what needs new simulation.
Existing data may motivate a design but are not fresh confirmation. No analysis
of historical results is authorized by the mere presence of this scaffold.
Implement the smallest reference instrument and test deterministic fixtures,
then compare any optimized implementation step for step. Calibrate on synthetic
known-answer processes and rotor/random-walk controls before trusting ant fits.

## 2. Freeze a prospective run

Pilot seeds: candidate namespace 2026101501..2026101504. Confirmation seeds:
candidate namespace starting 2026101601, with the count specified in README.
These values are proposed, NOT verified unused. Audit earlier manifests;
freeze explicit seed lists and distinct role assignments before launch. Split
by seed identity, never result rank. Bootstrap seed: proposed 2026101599.
Use a deterministic documented mapping from seeds to initialized patch contents.

Append a dated registration with full git commit, dirty source hashes, cohort
selection code/input hashes, complete rules, seed lists, area bands, board and
step caps, censoring, feature definitions, folds, bootstrap, estimator and gates.
Resolve every draft choice, including tie breaks and nonattainment. Estimate
cost from a separate pilot and record a compute budget. Do not tune predictions
using confirmation outcomes. Planned thresholds are not measured facts.

## 3. Run reproducibly

All Python/Rust runs use WSL from /mnt/f/Code/turmite:

```bash
export UV_PROJECT_ENVIRONMENT=$HOME/.venvs/turmite UV_LINK_MODE=copy
cargo test --release
```

Use uv for Python and polars rather than pandas. No dependency additions are
needed for this scaffold. Future runners use release mode, at most six workers,
and background long jobs with logs in this experiment's results/. Record exact
commands after the actual CLI exists; no imaginary sampler commands are given.
Scripts resolve ROOT = Path(__file__).resolve().parents[3] and write only here.

Each completed rule/seed output gets an atomic .done marker with config/source
hashes. Checkpoints include walker, visited region, RNG and open instrument
state. Changed configs cannot reuse markers. Verify uninterrupted/resumed byte
agreement and one-versus-six-thread output agreement. Record verification scope.
Bulk traces stay in dumps/; compact aggregates and manifests in results/.

## 4. Judge and report

Run the acceptance gates before scientific tests. Report missing runs,
nonattainment, board escapes and regime switches, with seed counts and sd.
Bootstrap at the independent rule/base level, preserving paired windows and
mutations. Separate registered tests from exploratory sensitivity analyses.
A failed instrument gate is uninformative; a reliable null rejects the stated
prediction at those scales. No resampling episodes as independent rules.

Update README, append-only NOTEBOOK and notebook together. The notebook reads
only explicitly listed, committed results and never launches simulation. Include
full input hashes and provenance. Update the cross-cutting mechanism note with
links and failures as well as successes. Commit only when asked.
