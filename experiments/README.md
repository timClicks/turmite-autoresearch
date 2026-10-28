# Experiments

Keep this README as a reference index: layout rules, the folder mapping and links. Scientific
content belongs in each experiment's own README and notebooks, or in `notes/`.

- [Experiment template](_template/README.md)
- [Exact additive modular invariant miner](archive/2026-10-invariant-mining/README.md)
- [Negative-result pruning index](../notes/pruning-index/README.md)
- [Dead-end signature template](_template/DEAD_END.md)

## Layout

```
experiments/
  proposed/YYYY-MM-slug/   registered or planned; nothing measured yet
  active/YYYY-MM-slug/     open work, or a maintained instrument other work depends on
  archive/YYYY-MM-slug/    concluded or paused; results stay citable and readable by other experiments
  _lib/  _template/  _migration/
```

- **The bucket is status; the slug is identity.** `YYYY-MM` is the month the work started and does not
  change when the folder moves. Slugs are unique across buckets. Blog pages are keyed by slug
  (`/experiments/<slug>/`), so a bucket move does not change a published URL.
- **Archive is not deprecation.** Archived experiments hold finished datasets that live work still reads
  (for example the census in `archive/2026-10-census-sweeps/`). Reopening one means moving it back to
  `active/`, with a new dated NOTEBOOK entry saying why.
- **New work** starts as a copy of `_template/` in `proposed/` (registration written, nothing run) or
  directly in `active/` once measurement begins.
- Scripts find the repository root with `Path(__file__).resolve().parents[4]` (script in
  `experiments/<bucket>/<slug>/scripts/`). Refer to another experiment by its repository path
  (`ROOT / "experiments/archive/2026-10-census-sweeps/results/..."`), not by a sibling path such as
  `HERE.parent / "..."`, so that a later bucket move can rewrite it.

## Moving an experiment between buckets

Write a one-row map and let the relocation script move the folder and rewrite references:

```sh
printf 'old_path\tnew_path\tbucket\treason\n' > experiments/_migration/YYYY-MM-DD-<slug>.tsv
printf 'experiments/active/2026-10-x\texperiments/archive/2026-10-x\tarchive\tconcluded: <why>\n' \
  >> experiments/_migration/YYYY-MM-DD-<slug>.tsv
uv run --frozen experiments/_migration/relocate.py experiments/_migration/YYYY-MM-DD-<slug>.tsv --dry-run
uv run --frozen experiments/_migration/relocate.py experiments/_migration/YYYY-MM-DD-<slug>.tsv
```

Then review the staged diff, run the checks below, add a NOTEBOOK entry in the moved experiment, and
update the tables here. Keep old maps: together they are the record of where every path used to be.

What the script rewrites, and what it deliberately leaves alone, is in its docstring
([`_migration/relocate.py`](_migration/relocate.py)). In short, it leaves alone links pinned to a
commit (`blob/<sha>/experiments/...`, which must keep the path that existed at that commit),
generated data under `results/` (Markdown reports aside), `.log`/`.csv`/`.sha256`/`.patch` files,
and saved notebook outputs. Those keep the old paths as a faithful record of the run; translate
them with the tables below.

**Other checkouts.** Pulling the move relocates tracked files, but gitignored `dumps*/`, `knock*/`,
`scratch/` and `synth/` stay behind in the old folders. Move them with

```sh
uv run --frozen experiments/_migration/relocate.py experiments/_migration/2026-10-28-buckets.tsv --local-only
```

which refuses to overwrite anything. Do this before running scripts that read `dumps/`.

## The 2026-10-28 reorganisation

All 129 experiments moved from `experiments/YYYY-MM-DD-slug/` to
`experiments/<bucket>/YYYY-MM-slug/` (7 active, 1 proposed,
121 archive). Dropping the day caused no slug collisions. Machine-readable map:
[`_migration/2026-10-28-buckets.tsv`](_migration/2026-10-28-buckets.tsv). The older flat-layout map
(`data/` and friends to `experiments/YYYY-MM-DD-slug/`) is [`_migration/map.tsv`](_migration/map.tsv);
chain the two to follow a pre-2026-10-14 path.

References in prose, code, CI, notebooks' cell sources, the blog and the paper were rewritten
mechanically in the same commit, including inside append-only `NOTEBOOK.md` files: path strings
only, no wording or results changed. Bucket assignments follow each README's status line and
`notes/ACTIVE.md` as of 2026-10-28; move a folder if its status is wrong.

### Active

| Old path | New path | Why here |
|---|---|---|
| `experiments/2026-10-16-gpu-ant-sweep` | [`experiments/active/2026-10-gpu-ant-sweep`](active/2026-10-gpu-ant-sweep/README.md) | maintained instrument: CUDA gpu_sweep guide and benchmarks (linked from AGENTS.md) |
| `experiments/2026-10-16-gpu-probe` | [`experiments/active/2026-10-gpu-probe`](active/2026-10-gpu-probe/README.md) | maintained instrument: gpu_probe; timing on an idle machine still pending |
| `experiments/2026-10-20-c-law-renewal` | [`experiments/active/2026-10-c-law-renewal`](active/2026-10-c-law-renewal/README.md) | open: next coupled-phase mechanism to be registered; main cohort unopened (notes/ACTIVE.md) |
| `experiments/2026-10-22-falsification-harness` | [`experiments/active/2026-10-falsification-harness`](active/2026-10-falsification-harness/README.md) | maintained instrument: GUIDE.md is required reading for classification claims |
| `experiments/2026-10-23-macos-gpu` | [`experiments/active/2026-10-macos-gpu`](active/2026-10-macos-gpu/README.md) | maintained instrument: wgpu/Metal sweeper guide (linked from AGENTS.md) |
| `experiments/2026-10-23-tiled-grid-backend` | [`experiments/active/2026-10-tiled-grid-backend`](active/2026-10-tiled-grid-backend/README.md) | maintained instrument: tiled backend DESIGN.md; optional follow-ups open |
| `experiments/2026-10-26-wall-vs-memory` | [`experiments/active/2026-10-wall-vs-memory`](active/2026-10-wall-vs-memory/README.md) | open: follow-ups F-a..F-d registered; Q30, Q31 |

### Proposed

| Old path | New path | Why here |
|---|---|---|
| `experiments/2026-10-25-late-highway-fourth-decade` | [`experiments/proposed/2026-10-late-highway-fourth-decade`](proposed/2026-10-late-highway-fourth-decade/README.md) | registered with power analysis; no 1e12 run started (deferred in notes/ACTIVE.md) |

### Archive

| Old path | New path | Why here |
|---|---|---|
| `experiments/2026-10-12-knockout-maps` | [`experiments/archive/2026-10-knockout-maps`](archive/2026-10-knockout-maps/README.md) | concluded or paused; results remain citable |
| `experiments/2026-10-13-a1-kappa` | [`experiments/archive/2026-10-a1-kappa`](archive/2026-10-a1-kappa/README.md) | concluded or paused; results remain citable |
| `experiments/2026-10-13-a2-edge-exponent` | [`experiments/archive/2026-10-a2-edge-exponent`](archive/2026-10-a2-edge-exponent/README.md) | concluded or paused; results remain citable |
| `experiments/2026-10-13-a3-background-cone-control` | [`experiments/archive/2026-10-a3-background-cone-control`](archive/2026-10-a3-background-cone-control/README.md) | concluded or paused; results remain citable |
| `experiments/2026-10-13-a4-boundary-width` | [`experiments/archive/2026-10-a4-boundary-width`](archive/2026-10-a4-boundary-width/README.md) | concluded or paused; results remain citable |
| `experiments/2026-10-13-a5-home-types` | [`experiments/archive/2026-10-a5-home-types`](archive/2026-10-a5-home-types/README.md) | concluded or paused; results remain citable |
| `experiments/2026-10-13-a6-corruption-mechanism` | [`experiments/archive/2026-10-a6-corruption-mechanism`](archive/2026-10-a6-corruption-mechanism/README.md) | concluded or paused; results remain citable |
| `experiments/2026-10-13-a7-rrllllllr-self-averaging` | [`experiments/archive/2026-10-a7-rrllllllr-self-averaging`](archive/2026-10-a7-rrllllllr-self-averaging/README.md) | concluded or paused; results remain citable |
| `experiments/2026-10-13-arm-kappa-depletion-arms` | [`experiments/archive/2026-10-arm-kappa-depletion-arms`](archive/2026-10-arm-kappa-depletion-arms/README.md) | concluded or paused; results remain citable |
| `experiments/2026-10-13-b1-exact-exponent` | [`experiments/archive/2026-10-b1-exact-exponent`](archive/2026-10-b1-exact-exponent/README.md) | concluded or paused; results remain citable |
| `experiments/2026-10-13-b2-between-rule-variance` | [`experiments/archive/2026-10-b2-between-rule-variance`](archive/2026-10-b2-between-rule-variance/README.md) | concluded or paused; results remain citable |
| `experiments/2026-10-13-b3-long-rules` | [`experiments/archive/2026-10-b3-long-rules`](archive/2026-10-b3-long-rules/README.md) | concluded or paused; results remain citable |
| `experiments/2026-10-13-b4-unfitted-rules` | [`experiments/archive/2026-10-b4-unfitted-rules`](archive/2026-10-b4-unfitted-rules/README.md) | concluded or paused; results remain citable |
| `experiments/2026-10-13-b5-late-highways` | [`experiments/archive/2026-10-b5-late-highways`](archive/2026-10-b5-late-highways/README.md) | concluded or paused; results remain citable |
| `experiments/2026-10-13-c2-arrow-bias` | [`experiments/archive/2026-10-c2-arrow-bias`](archive/2026-10-c2-arrow-bias/README.md) | concluded or paused; results remain citable |
| `experiments/2026-10-13-c3-edge-colour-shares` | [`experiments/archive/2026-10-c3-edge-colour-shares`](archive/2026-10-c3-edge-colour-shares/README.md) | concluded or paused; results remain citable |
| `experiments/2026-10-13-calib-instrument-calibration` | [`experiments/archive/2026-10-calib-instrument-calibration`](archive/2026-10-calib-instrument-calibration/README.md) | concluded or paused; results remain citable |
| `experiments/2026-10-13-cell1` | [`experiments/archive/2026-10-cell1`](archive/2026-10-cell1/README.md) | concluded or paused; results remain citable |
| `experiments/2026-10-13-census-sweeps` | [`experiments/archive/2026-10-census-sweeps`](archive/2026-10-census-sweeps/README.md) | concluded or paused; results remain citable |
| `experiments/2026-10-13-colourstats` | [`experiments/archive/2026-10-colourstats`](archive/2026-10-colourstats/README.md) | concluded or paused; results remain citable |
| `experiments/2026-10-13-d1-turmite-sqrt-cluster` | [`experiments/archive/2026-10-d1-turmite-sqrt-cluster`](archive/2026-10-d1-turmite-sqrt-cluster/README.md) | concluded or paused; results remain citable |
| `experiments/2026-10-13-d2-three-dimensions` | [`experiments/archive/2026-10-d2-three-dimensions`](archive/2026-10-d2-three-dimensions/README.md) | concluded or paused; results remain citable |
| `experiments/2026-10-13-d3-noise` | [`experiments/archive/2026-10-d3-noise`](archive/2026-10-d3-noise/README.md) | concluded or paused; results remain citable |
| `experiments/2026-10-13-d4-many-ants` | [`experiments/archive/2026-10-d4-many-ants`](archive/2026-10-d4-many-ants/README.md) | concluded or paused; results remain citable |
| `experiments/2026-10-13-dose-corruption-dose` | [`experiments/archive/2026-10-dose-corruption-dose`](archive/2026-10-dose-corruption-dose/README.md) | concluded or paused; results remain citable |
| `experiments/2026-10-13-e1-one-sided-hot-region` | [`experiments/archive/2026-10-e1-one-sided-hot-region`](archive/2026-10-e1-one-sided-hot-region/README.md) | concluded or paused; results remain citable |
| `experiments/2026-10-13-e2-sensitive-disc` | [`experiments/archive/2026-10-e2-sensitive-disc`](archive/2026-10-e2-sensitive-disc/README.md) | concluded or paused; results remain citable |
| `experiments/2026-10-13-e3-route-collinearity` | [`experiments/archive/2026-10-e3-route-collinearity`](archive/2026-10-e3-route-collinearity/README.md) | concluded or paused; results remain citable |
| `experiments/2026-10-13-e4-patch-vs-swap` | [`experiments/archive/2026-10-e4-patch-vs-swap`](archive/2026-10-e4-patch-vs-swap/README.md) | concluded or paused; results remain citable |
| `experiments/2026-10-13-e5-more-knockout-maps` | [`experiments/archive/2026-10-e5-more-knockout-maps`](archive/2026-10-e5-more-knockout-maps/README.md) | concluded or paused; results remain citable |
| `experiments/2026-10-13-e6-hot-window-age` | [`experiments/archive/2026-10-e6-hot-window-age`](archive/2026-10-e6-hot-window-age/README.md) | concluded or paused; results remain citable |
| `experiments/2026-10-13-edge-statistics` | [`experiments/archive/2026-10-edge-statistics`](archive/2026-10-edge-statistics/README.md) | concluded or paused; results remain citable |
| `experiments/2026-10-13-ext-other-lattices-turmites-noise` | [`experiments/archive/2026-10-ext-other-lattices-turmites-noise`](archive/2026-10-ext-other-lattices-turmites-noise/README.md) | concluded or paused; results remain citable |
| `experiments/2026-10-13-flip-damage` | [`experiments/archive/2026-10-flip-damage`](archive/2026-10-flip-damage/README.md) | concluded or paused; results remain citable |
| `experiments/2026-10-13-formage-age` | [`experiments/archive/2026-10-formage-age`](archive/2026-10-formage-age/README.md) | concluded or paused; results remain citable |
| `experiments/2026-10-13-frontier-code-patch` | [`experiments/archive/2026-10-frontier-code-patch`](archive/2026-10-frontier-code-patch/README.md) | concluded or paused; results remain citable |
| `experiments/2026-10-13-g1-ribbon-breakout` | [`experiments/archive/2026-10-g1-ribbon-breakout`](archive/2026-10-g1-ribbon-breakout/README.md) | concluded or paused; results remain citable |
| `experiments/2026-10-13-h1-lacunarity-decomposition` | [`experiments/archive/2026-10-h1-lacunarity-decomposition`](archive/2026-10-h1-lacunarity-decomposition/README.md) | concluded or paused; results remain citable |
| `experiments/2026-10-13-h3-scaling-collapse` | [`experiments/archive/2026-10-h3-scaling-collapse`](archive/2026-10-h3-scaling-collapse/README.md) | concluded or paused; results remain citable |
| `experiments/2026-10-13-highways-unresolved-rules-1e10-1e11` | [`experiments/archive/2026-10-highways-unresolved-rules-1e10-1e11`](archive/2026-10-highways-unresolved-rules-1e10-1e11/README.md) | concluded or paused; results remain citable |
| `experiments/2026-10-13-hot-tiles` | [`experiments/archive/2026-10-hot-tiles`](archive/2026-10-hot-tiles/README.md) | concluded or paused; results remain citable |
| `experiments/2026-10-13-item21-slow-outliers` | [`experiments/archive/2026-10-item21-slow-outliers`](archive/2026-10-item21-slow-outliers/README.md) | concluded or paused; results remain citable |
| `experiments/2026-10-13-item4-exponent-rotor-calibrated` | [`experiments/archive/2026-10-item4-exponent-rotor-calibrated`](archive/2026-10-item4-exponent-rotor-calibrated/README.md) | concluded or paused; results remain citable |
| `experiments/2026-10-13-j4-tethered-gyration` | [`experiments/archive/2026-10-j4-tethered-gyration`](archive/2026-10-j4-tethered-gyration/README.md) | concluded or paused; results remain citable |
| `experiments/2026-10-13-k1-necklace-icc` | [`experiments/archive/2026-10-k1-necklace-icc`](archive/2026-10-k1-necklace-icc/README.md) | concluded or paused; results remain citable |
| `experiments/2026-10-13-layers-colours` | [`experiments/archive/2026-10-layers-colours`](archive/2026-10-layers-colours/README.md) | concluded or paused; results remain citable |
| `experiments/2026-10-13-log-growers` | [`experiments/archive/2026-10-log-growers`](archive/2026-10-log-growers/README.md) | concluded or paused; results remain citable |
| `experiments/2026-10-13-memory-walkers` | [`experiments/archive/2026-10-memory-walkers`](archive/2026-10-memory-walkers/README.md) | concluded or paused; results remain citable |
| `experiments/2026-10-13-misc-instruments` | [`experiments/archive/2026-10-misc-instruments`](archive/2026-10-misc-instruments/README.md) | concluded or paused; results remain citable |
| `experiments/2026-10-13-mixing` | [`experiments/archive/2026-10-mixing`](archive/2026-10-mixing/README.md) | concluded or paused; results remain citable |
| `experiments/2026-10-13-occupancy-pages` | [`experiments/archive/2026-10-occupancy-pages`](archive/2026-10-occupancy-pages/README.md) | concluded or paused; results remain citable |
| `experiments/2026-10-13-patched-starts` | [`experiments/archive/2026-10-patched-starts`](archive/2026-10-patched-starts/README.md) | concluded or paused; results remain citable |
| `experiments/2026-10-13-patterns-fields` | [`experiments/archive/2026-10-patterns-fields`](archive/2026-10-patterns-fields/README.md) | concluded or paused; results remain citable |
| `experiments/2026-10-13-probe-growth-census` | [`experiments/archive/2026-10-probe-growth-census`](archive/2026-10-probe-growth-census/README.md) | concluded or paused; results remain citable |
| `experiments/2026-10-13-r1-width-vs-radius` | [`experiments/archive/2026-10-r1-width-vs-radius`](archive/2026-10-r1-width-vs-radius/README.md) | concluded or paused; results remain citable |
| `experiments/2026-10-13-recolour` | [`experiments/archive/2026-10-recolour`](archive/2026-10-recolour/README.md) | concluded or paused; results remain citable |
| `experiments/2026-10-13-shape-limit` | [`experiments/archive/2026-10-shape-limit`](archive/2026-10-shape-limit/README.md) | concluded or paused; results remain citable |
| `experiments/2026-10-13-snapshots` | [`experiments/archive/2026-10-snapshots`](archive/2026-10-snapshots/README.md) | concluded or paused; results remain citable |
| `experiments/2026-10-13-spread-home` | [`experiments/archive/2026-10-spread-home`](archive/2026-10-spread-home/README.md) | concluded or paused; results remain citable |
| `experiments/2026-10-13-tether-rules` | [`experiments/archive/2026-10-tether-rules`](archive/2026-10-tether-rules/README.md) | concluded or paused; results remain citable |
| `experiments/2026-10-13-transport-forecast` | [`experiments/archive/2026-10-transport-forecast`](archive/2026-10-transport-forecast/README.md) | concluded or paused; results remain citable |
| `experiments/2026-10-13-w-width-radius-refit` | [`experiments/archive/2026-10-w-width-radius-refit`](archive/2026-10-w-width-radius-refit/README.md) | concluded or paused; results remain citable |
| `experiments/2026-10-13-w1` | [`experiments/archive/2026-10-w1`](archive/2026-10-w1/README.md) | concluded or paused; results remain citable |
| `experiments/2026-10-13-w2` | [`experiments/archive/2026-10-w2`](archive/2026-10-w2/README.md) | concluded or paused; results remain citable |
| `experiments/2026-10-13-w3` | [`experiments/archive/2026-10-w3`](archive/2026-10-w3/README.md) | concluded or paused; results remain citable |
| `experiments/2026-10-13-w4-edge-exponent-2e36` | [`experiments/archive/2026-10-w4-edge-exponent-2e36`](archive/2026-10-w4-edge-exponent-2e36/README.md) | concluded or paused; results remain citable |
| `experiments/2026-10-14-hull-width` | [`experiments/archive/2026-10-hull-width`](archive/2026-10-hull-width/README.md) | concluded or paused; results remain citable |
| `experiments/2026-10-14-kappa-matched-area` | [`experiments/archive/2026-10-kappa-matched-area`](archive/2026-10-kappa-matched-area/README.md) | concluded or paused; results remain citable |
| `experiments/2026-10-14-rulepat` | [`experiments/archive/2026-10-rulepat`](archive/2026-10-rulepat/README.md) | concluded or paused; results remain citable |
| `experiments/2026-10-14-t1-excursion-tomography` | [`experiments/archive/2026-10-t1-excursion-tomography`](archive/2026-10-t1-excursion-tomography/README.md) | concluded or paused; results remain citable |
| `experiments/2026-10-15-alpha-gap` | [`experiments/archive/2026-10-alpha-gap`](archive/2026-10-alpha-gap/README.md) | concluded or paused; results remain citable |
| `experiments/2026-10-15-chirality-baselines` | [`experiments/archive/2026-10-chirality-baselines`](archive/2026-10-chirality-baselines/README.md) | concluded or paused; results remain citable |
| `experiments/2026-10-15-fixed-area-cycles` | [`experiments/archive/2026-10-fixed-area-cycles`](archive/2026-10-fixed-area-cycles/README.md) | concluded or paused; results remain citable |
| `experiments/2026-10-15-hull-checks` | [`experiments/archive/2026-10-hull-checks`](archive/2026-10-hull-checks/README.md) | concluded or paused; results remain citable |
| `experiments/2026-10-15-independent-area` | [`experiments/archive/2026-10-independent-area`](archive/2026-10-independent-area/README.md) | concluded or paused; results remain citable |
| `experiments/2026-10-15-kappa-cutoff-mixed-effects` | [`experiments/archive/2026-10-kappa-cutoff-mixed-effects`](archive/2026-10-kappa-cutoff-mixed-effects/README.md) | concluded or paused; results remain citable |
| `experiments/2026-10-15-kappa-field-age` | [`experiments/archive/2026-10-kappa-field-age`](archive/2026-10-kappa-field-age/README.md) | concluded or paused; results remain citable |
| `experiments/2026-10-15-kappa-prefix-exposure` | [`experiments/archive/2026-10-kappa-prefix-exposure`](archive/2026-10-kappa-prefix-exposure/README.md) | concluded or paused; results remain citable |
| `experiments/2026-10-15-kappa-return-gates` | [`experiments/archive/2026-10-kappa-return-gates`](archive/2026-10-kappa-return-gates/README.md) | concluded or paused; results remain citable |
| `experiments/2026-10-15-kappa-tail-budget` | [`experiments/archive/2026-10-kappa-tail-budget`](archive/2026-10-kappa-tail-budget/README.md) | concluded or paused; results remain citable |
| `experiments/2026-10-15-literature-review` | [`experiments/archive/2026-10-literature-review`](archive/2026-10-literature-review/README.md) | concluded or paused; results remain citable |
| `experiments/2026-10-16-kappa-growth-clock` | [`experiments/archive/2026-10-kappa-growth-clock`](archive/2026-10-kappa-growth-clock/README.md) | concluded or paused; results remain citable |
| `experiments/2026-10-16-kappa-leadrun-fresh` | [`experiments/archive/2026-10-kappa-leadrun-fresh`](archive/2026-10-kappa-leadrun-fresh/README.md) | concluded or paused; results remain citable |
| `experiments/2026-10-16-kappa-loop-surgery` | [`experiments/archive/2026-10-kappa-loop-surgery`](archive/2026-10-kappa-loop-surgery/README.md) | concluded or paused; results remain citable |
| `experiments/2026-10-16-kappa-prefix-decode` | [`experiments/archive/2026-10-kappa-prefix-decode`](archive/2026-10-kappa-prefix-decode/README.md) | concluded or paused; results remain citable |
| `experiments/2026-10-16-kappa-square-loop` | [`experiments/archive/2026-10-kappa-square-loop`](archive/2026-10-kappa-square-loop/README.md) | concluded or paused; results remain citable |
| `experiments/2026-10-16-kappa-uniform-baseline` | [`experiments/archive/2026-10-kappa-uniform-baseline`](archive/2026-10-kappa-uniform-baseline/README.md) | concluded or paused; results remain citable |
| `experiments/2026-10-19-c-law-mechanism` | [`experiments/archive/2026-10-c-law-mechanism`](archive/2026-10-c-law-mechanism/README.md) | concluded or paused; results remain citable |
| `experiments/2026-10-19-kappa-chiral-edge` | [`experiments/archive/2026-10-kappa-chiral-edge`](archive/2026-10-kappa-chiral-edge/README.md) | concluded or paused; results remain citable |
| `experiments/2026-10-19-kappa-walker-reference` | [`experiments/archive/2026-10-kappa-walker-reference`](archive/2026-10-kappa-walker-reference/README.md) | concluded or paused; results remain citable |
| `experiments/2026-10-20-kappa-exposure-classes` | [`experiments/archive/2026-10-kappa-exposure-classes`](archive/2026-10-kappa-exposure-classes/README.md) | concluded or paused; results remain citable |
| `experiments/2026-10-20-kappa-first-passage` | [`experiments/archive/2026-10-kappa-first-passage`](archive/2026-10-kappa-first-passage/README.md) | concluded or paused; results remain citable |
| `experiments/2026-10-20-kappa-prefix-ablation` | [`experiments/archive/2026-10-kappa-prefix-ablation`](archive/2026-10-kappa-prefix-ablation/README.md) | concluded or paused; results remain citable |
| `experiments/2026-10-20-kappa-prefix-additive` | [`experiments/archive/2026-10-kappa-prefix-additive`](archive/2026-10-kappa-prefix-additive/README.md) | concluded or paused; results remain citable |
| `experiments/2026-10-20-kappa-prefix-family-holdout` | [`experiments/archive/2026-10-kappa-prefix-family-holdout`](archive/2026-10-kappa-prefix-family-holdout/README.md) | concluded or paused; results remain citable |
| `experiments/2026-10-20-kappa-prefix-runs` | [`experiments/archive/2026-10-kappa-prefix-runs`](archive/2026-10-kappa-prefix-runs/README.md) | concluded or paused; results remain citable |
| `experiments/2026-10-20-kappa-spread-budget` | [`experiments/archive/2026-10-kappa-spread-budget`](archive/2026-10-kappa-spread-budget/README.md) | concluded or paused; results remain citable |
| `experiments/2026-10-20-kappa-spread-features` | [`experiments/archive/2026-10-kappa-spread-features`](archive/2026-10-kappa-spread-features/README.md) | concluded or paused; results remain citable |
| `experiments/2026-10-20-lattice-c-law` | [`experiments/archive/2026-10-lattice-c-law`](archive/2026-10-lattice-c-law/README.md) | concluded or paused; results remain citable |
| `experiments/2026-10-20-lattice-c-law-colours` | [`experiments/archive/2026-10-lattice-c-law-colours`](archive/2026-10-lattice-c-law-colours/README.md) | concluded or paused; results remain citable |
| `experiments/2026-10-20-rlrlll-macro-transition` | [`experiments/archive/2026-10-rlrlll-macro-transition`](archive/2026-10-rlrlll-macro-transition/README.md) | concluded or paused; results remain citable |
| `experiments/2026-10-21-boundary-return-map` | [`experiments/archive/2026-10-boundary-return-map`](archive/2026-10-boundary-return-map/README.md) | concluded or paused; results remain citable |
| `experiments/2026-10-21-highway-preconditions` | [`experiments/archive/2026-10-highway-preconditions`](archive/2026-10-highway-preconditions/README.md) | concluded or paused; results remain citable |
| `experiments/2026-10-21-late-highway-board-check` | [`experiments/archive/2026-10-late-highway-board-check`](archive/2026-10-late-highway-board-check/README.md) | concluded or paused; results remain citable |
| `experiments/2026-10-21-rlrlll-portrait` | [`experiments/archive/2026-10-rlrlll-portrait`](archive/2026-10-rlrlll-portrait/README.md) | concluded or paused; results remain citable |
| `experiments/2026-10-22-falsify-adaptive-search` | [`experiments/archive/2026-10-falsify-adaptive-search`](archive/2026-10-falsify-adaptive-search/README.md) | concluded or paused; results remain citable |
| `experiments/2026-10-22-invariant-mining` | [`experiments/archive/2026-10-invariant-mining`](archive/2026-10-invariant-mining/README.md) | concluded or paused; results remain citable |
| `experiments/2026-10-22-invariant-mining-snf` | [`experiments/archive/2026-10-invariant-mining-snf`](archive/2026-10-invariant-mining-snf/README.md) | concluded or paused; results remain citable |
| `experiments/2026-10-22-single-cell-gates` | [`experiments/archive/2026-10-single-cell-gates`](archive/2026-10-single-cell-gates/README.md) | concluded or paused; results remain citable |
| `experiments/2026-10-23-evidence-ledger` | [`experiments/archive/2026-10-evidence-ledger`](archive/2026-10-evidence-ledger/README.md) | concluded or paused; results remain citable |
| `experiments/2026-10-23-hidden-phase-return` | [`experiments/archive/2026-10-hidden-phase-return`](archive/2026-10-hidden-phase-return/README.md) | concluded or paused; results remain citable |
| `experiments/2026-10-23-highway-decider` | [`experiments/archive/2026-10-highway-decider`](archive/2026-10-highway-decider/README.md) | concluded or paused; results remain citable |
| `experiments/2026-10-23-sweeper-generalisation` | [`experiments/archive/2026-10-sweeper-generalisation`](archive/2026-10-sweeper-generalisation/README.md) | concluded or paused; results remain citable |
| `experiments/2026-10-24-lean-tiled-ci-identity` | [`experiments/archive/2026-10-lean-tiled-ci-identity`](archive/2026-10-lean-tiled-ci-identity/README.md) | concluded or paused; results remain citable |
| `experiments/2026-10-25-crawler-cost-chaotic-edge` | [`experiments/archive/2026-10-crawler-cost-chaotic-edge`](archive/2026-10-crawler-cost-chaotic-edge/README.md) | concluded or paused; results remain citable |
| `experiments/2026-10-25-exposure-classifier-check` | [`experiments/archive/2026-10-exposure-classifier-check`](archive/2026-10-exposure-classifier-check/README.md) | concluded or paused; results remain citable |
| `experiments/2026-10-25-prefix-causal-horizon` | [`experiments/archive/2026-10-prefix-causal-horizon`](archive/2026-10-prefix-causal-horizon/README.md) | concluded or paused; results remain citable |
| `experiments/2026-10-25-rotation-boxes` | [`experiments/archive/2026-10-rotation-boxes`](archive/2026-10-rotation-boxes/README.md) | concluded or paused; results remain citable |
| `experiments/2026-10-25-square-ring-fillers` | [`experiments/archive/2026-10-square-ring-fillers`](archive/2026-10-square-ring-fillers/README.md) | concluded or paused; results remain citable |
| `experiments/2026-10-crystal-rules` | [`experiments/archive/2026-10-crystal-rules`](archive/2026-10-crystal-rules/README.md) | concluded or paused; results remain citable |
| `experiments/2026-10-kappa-rule-space` | [`experiments/archive/2026-10-kappa-rule-space`](archive/2026-10-kappa-rule-space/README.md) | concluded or paused; results remain citable |
