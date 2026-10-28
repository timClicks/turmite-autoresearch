# Hull checks: persistent shape or local roughening?

Registered 2026-10-15 21:36 NZDT, base `da88e61` with a dirty working tree,
before new measurements. Requested by the user as “an experiment for Hull checks”.
This follows [the hull-width correction](../2026-10-hull-width/README.md)
and [research avenue 5](../../../notes/paper-gaps-research-avenues-2026-10-15.md).

## Question and hypotheses

Does the ants' wider coastline survive removal of persistent global shape and
comparison with rotors of the same radius? H-shape predicts that the gap is
mostly in persistent low modes; H-local predicts a residual excess at shorter
wavelengths. The decay of normalised power is not independent evidence: it
already contains W/R scaling. No universality-class claim follows from this test.

## Registered design

Instrument: `examples/hull_checks.rs`, a frozen copy of `hull_width.rs` with
full-precision 512-bin outermost-visited-cell profiles appended, every integer
k rather than every second k. This definition can miss overhangs; it is not
the same observable as surface-cell Wout. Keep both. Exterior remains 4-connected.

Full cohort: six original A4 rules, plus 12 rules selected from the frozen
`unresolved_le10.txt` pool by ascending SHA-256 of `20261015:RULE`, excluding
the six originals. This is a sample of unresolved rules, not certified chaotic
rules. No growth-based selection after inspection. Ant patch seeds 331–334;
rotor seeds 331–342. Ant checkpoints k=24..30, rotor k=24..32, grid 8192.
All profiles and escapes retained; no replacement of failed or escaping rules.
Profile validity requires all bins populated. Pilot uses RLR, RLRLRRRLLR and
rotor, seeds 331–332, k=16..20, grid 1024; it tests plumbing only.

Fixed definitions (r in cells, theta equally spaced): remove modes 0..2 for
the primary residual; split modes 3..8 (shape), 9..64 (local), and 65..256
(resolution diagnostic). Use correct single weighting of the Nyquist mode.
Report absolute band variance and variance/rbar² separately. Report
S(lag)=mean[(h(theta+lag)-h(theta))²] for h containing modes 9..64,
lags 1,2,4,8,16,32,64,128. Correlation length = first lag whose S reaches
the local variance (half the decorrelated plateau); report missing crossings.
Physical separation = 2*pi*rbar*lag/512. This angular-profile estimator is
calibrated on synthetic modes, not assumed to be an interface exponent.

For each ant checkpoint match each rotor seed to its nearest radius in log
space, requiring |log(Rrot/Rant)| <= log(1.10); ties choose smaller k.
At least 8 rotor seeds must match; otherwise mark unmatched, with no extrapolation.
Compare with the median of matched rotor seeds. Unit of inference: median over
seeds within a rule, then rules. Report rule spread and between-seed sd;
bootstrap rules (2000 draws, seed 20261015) for 95% intervals of median ratios.
Repeated checkpoints are not independent replicates. Temporal persistence is
the real complex inner product of band coefficients at consecutive k, divided
by their norms, in the centroid/laboratory angular frame; do not rotate to fit.
The same mode split on pairwise-max-coarsened 256-bin profiles checks resolution.

## Predictions and decision rules (do not rewrite)

1. Calibration: pure m=4 lies wholly in shape; pure m=32 wholly in local;
   Parseval and the exact sinusoidal structure function agree to 1e-10 relative
   tolerance. A Nyquist-only contour has the correct variance. Failure blocks
   biological/geometric interpretation. No finite-window rotor exponent is imposed.
2. H-shape: at k=28,29,30 the rule-median matched ratio of local variance is
   <=1.25, while the shape ratio is >=2.0; at least 80% of eligible rules agree.
3. H-shape persistence: median adjacent-k shape correlation is >=0.7 and
   exceeds local correlation by >=0.2 for ants over k=26..30.
4. H-local alternative: local ratio >=1.5 at k=28,29,30 with bootstrap lower
   bound >1, in at least 80% of eligible rules, and local-variance ratio changes
   by <=20% on coarsening. Otherwise the evidence is mixed/unresolved.
5. Radius matching: >=80% of ant rows at each late k have >=8 matched rotors.
   Resolution: local variance changes by <=20% in >=90% of valid late profiles.
   Either failure prevents choosing H-shape or H-local. Report original and
   sampled cohorts separately. Insufficient valid sampled rules (<8) also blocks
   a census-sample conclusion. Predictions 2 and 3 both required for H-shape.

Correlation lengths and their log-log slopes against radius over k=26..30 are
descriptive checks, per run, with between-seed spread; no fitted power law will
be labelled stable from this short window. Results cannot establish causation.

## Reproduction (WSL from repo root)

```bash
export UV_PROJECT_ENVIRONMENT=$HOME/.venvs/turmite UV_LINK_MODE=copy
export CARGO_TARGET_DIR=$HOME/turmite-target
cargo test --release
cargo test --release --example hull_checks
cargo build --release --example hull_checks
cargo build --release --example hull_width
uv run experiments/archive/2026-10-hull-checks/scripts/checks.py
uv run experiments/archive/2026-10-hull-checks/scripts/validate.py
uv run experiments/archive/2026-10-hull-checks/scripts/run.py --pilot
uv run experiments/archive/2026-10-hull-checks/scripts/analyse.py --pilot
# Full job (background; per-spec checkpoints and .done markers):
nohup uv run experiments/archive/2026-10-hull-checks/scripts/run.py > experiments/archive/2026-10-hull-checks/results/run.log 2>&1 &
uv run experiments/archive/2026-10-hull-checks/scripts/analyse.py
```

`run.py` records commands, seed/spec cohort, input/source hashes, git commit and
dirty status; validates resume hashes before skipping. Each completed spec is
atomic and checkpointed separately; an interrupted spec restarts from t=0.
No state-level restart within a spec. Full measurement outputs are small CSVs
under this experiment's results; no previous experiment results are overwritten.

## Status

Prepared and pilot-validated 2026-10-15. Full science run not started; the commands
above are ready. No scientific prediction has been evaluated by the pilot.

## Validation results (2026-10-15; registration unchanged)

- `scripts/checks.py` → `results/calibration.json`: all synthetic controls pass.
- `scripts/validate.py` → `results/validation.json`: nine matched legacy rows
  identical, and byte-identical exporter output under 1 versus 6 Rayon threads.
- `scripts/run.py --pilot` then `scripts/analyse.py --pilot` →
  `results/pilot/`: six complete runs, 30 checkpoint rows; 10 valid angular
  profiles and 20 explicitly excluded for empty bins. No files missing.
  Two rotor seeds cannot satisfy the eight-control matching requirement.
- Repeating `scripts/run.py --pilot` → `results/resume.log`: six skips with
  output SHA-256 checked before skipping. No results overwritten.
- `cargo test --release` → `results/release_tests.log`: passed. The new example's
  square-with-holes oracle passed separately (`cargo test --release --example hull_checks`).
- `notebook.ipynb` executed top to bottom with `uv run --with nbconvert --with
  ipykernel --with nbformat jupyter nbconvert --to notebook --execute --inplace
  experiments/archive/2026-10-hull-checks/notebook.ipynb` (`results/notebook.log`).

The sparse-bin exclusions in this early pilot motivate enforcing the registered
coverage gate, not interpolation. Full runs begin at k=24. Hashes and dirty-tree
state are in the pilot manifest; working outputs have not been committed.
