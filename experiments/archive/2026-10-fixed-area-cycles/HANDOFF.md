# Fresh-agent handoff

## Continuation status (2026-10-15, session 3)

The original scaffold handoff below is historical. The sampler, oracle tests,
pilot, controls and frozen registration are implemented. Production uses
config.frozen.json; do not restart from the draft. See the final NOTEBOOK entries.
Scripts now include audit.py (all payloads and hashes), check_determinism.py
(one production seed per rule at both widths), analyse.py (frozen tests, requires
audit.json), and results_notebook.py (replaces the NOT RUN scaffold after analysis).
The current user has authorized continuing this experiment, including simulations.
Production and both analyses have now finished; README's final sections and
results/analysis.json are authoritative. The executed notebook and association
figure are ready. P1 primary fails, P2 secondary passes; both sensitivity tests
pass. Do not relaunch for a different estimator without a fresh registration.
Remaining validation limit: thread determinism was replayed for seed 1001 of
each rule, not all 64 seeds. P3's full determinism clause is therefore incomplete.

## First 15 minutes

1. Read repository AGENTS.md and `experiments/README.md`; inspect `git status`.
   The workspace already contains unrelated uncommitted investigations. Do not
   reset, clean, overwrite their results or commit without being asked.
2. Read README, PLAN, SCHEMA and config here, plus the linked excursion audit
   (especially its retraction). Prior typical-excursion and edge-dwell results
   were null; this test concerns fixed-area tail time budgets.
3. Run `scripts/preflight.py` under uv/WSL. It prints source/config hashes.
4. Inspect the existing code below. Decide between a shared instrument module
   with property tests and an experiment-prefixed example; avoid exposing
   existing private Region internals merely for convenience.

## Code map (verified when scaffolded)

- `src/probe.rs`: private Region incrementally tracks ever-visited area and
  boundary cells; classification occurs BEFORE each step; arriving fresh cell
  is marked visited AFTER the step. Region starts with the origin visited.
- `examples/excursions.rs`: existing FastRegion, episode accounting and
  octave-window statistics. Reuse ideas, not unchecked assumptions about
  quantiles, window assignment or unfinished episodes.
- `src/bin/probe.rs`: walker spec parsing and deterministic rayon collection.
  `RULE@SEED` uses `PatchedAnt::new(rule, seed, 2)` (5x5 colour patch).
  Initial nonzero colours are NOT automatically visited territory.
- `src/walkers.rs`: Walker, PatchedAnt, Rotor, RandomWalk.
- `src/reference.rs`, `tests/probe.rs`: independent reference paths and
  brute-force visited-set boundary oracle. New instrument needs its own
  property comparison, including area-hit times and clipped episodes.
- `experiments/_lib/analyse_probe.py`: legacy kappa is boundary fraction
  divided by END-window P/A, not time-average P/A. Keep both, label them.
- `../2026-10-t1-excursion-tomography/results/t1b_cutoff_seeds.csv`:
  candidate cohort rule names only; do not use old outcomes as new measurements.
- `../2026-10-independent-area/results/analysis.json`: previous test and
  hashes; prior analysis seed was 20261015, not a fresh simulation seed.

## Deliverables in order

- [ ] Finalize time/band/episode conventions in PLAN and SCHEMA; record decision.
- [ ] Implement deterministic sampler and obvious independent oracle.
- [ ] Property tests: paths, area/perimeter, hit times, B/I labels, fragments,
      complete cycles, budget/escape stops, exact integer conservation.
- [ ] Controls: rotor and random walk, narrow/wide bands, endpoint vs averaged
      P/A, completed-only vs clipped accounting. Record bias, not just pass/fail.
- [ ] Pilot runtime, memory, censoring, quantile event count and attainability.
      Freeze gate rules BEFORE pilot; do not inspect rule associations in pilot.
- [ ] Amend config, freeze cohort + primary analysis + thresholds + seed split,
      timestamp README registration. Record hashes. Never rewrite predictions.
- [ ] Implement launcher: per-spec atomic outputs, checkpoint/resume, logs,
      keyed deterministic output, bounded rayon concurrency (machine: 6 cores).
- [ ] Run production in background, logging inside this experiment; analyse
      only after instrument/coverage gates. Include every attempted run status.
- [ ] Generate small reproducible summaries; execute shareable notebook;
      update README, append NOTEBOOK, link conclusions in notes.

## Toolchain recipes

From PowerShell, use the following WSL pattern (environment must be set each time):

```powershell
wsl -e bash -lc 'export UV_PROJECT_ENVIRONMENT=$HOME/.venvs/turmite UV_LINK_MODE=copy; cd /mnt/f/Code/turmite; uv run experiments/archive/2026-10-fixed-area-cycles/scripts/preflight.py'
wsl -e bash -lc 'export UV_PROJECT_ENVIRONMENT=$HOME/.venvs/turmite UV_LINK_MODE=copy; cd /mnt/f/Code/turmite; cargo test --release'
```

Proposed Rust example name (NOT implemented): `fixed_area_cycles_sampler`.
Only after implementation, document its actual CLI; do not present hypothetical
arguments as a runnable recipe. Build and simulate with `--release`.

Notebook execution after results exist:
`uv run --with nbconvert --with ipykernel --with nbformat jupyter nbconvert --to notebook --execute --inplace experiments/archive/2026-10-fixed-area-cycles/notebook.ipynb`.

No subagents or delegation are required by this handoff. No measurements were
authorized to start by the scaffold itself; the current request is scaffolding.
