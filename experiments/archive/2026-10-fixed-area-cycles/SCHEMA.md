# Draft output contract (version 0; freeze before production)

The following is the historical proposed contract. The implemented contract is
documented at the end; README's dated registration and config.frozen.json fix
the actual estimands and parameters.

Use CSV for small keyed tables and JSON for manifests. Bulk episode rows belong
in ignored `dumps/`; reproducible small summaries belong in `results/`.
Integers for all times/counts; explicit nulls for undefined estimates; no NaN
silently converted to zero. Fields below are a contract to implement, not files
that already contain observations.

## Run manifest — results/<run_id>.json

schema_version, run_id, stage (pilot/production/control), command, commit,
dirty flag, source hashes, config hash, input hashes, walker spec, seed,
patch radius, grid size, area bands, step cap, RNG/algorithm version,
output hashes, status, completed targets, stop reason. Separate timestamp/runtime
telemetry from deterministic scientific payload. Never record secrets.

## Run status — results/run_status.csv

One row per attempted spec, including failed starts and unattained bands:
run_id, walker, rule (nullable for controls), seed, stage, steps_completed,
area_final, status (complete/budget/escaped/error), stop_reason.
Key: (stage, walker, rule, seed, config_hash); config_hash must be retained.

## Band summary — results/bands.csv

run_id, band_id, target_lo, target_hi, reached_lo, reached_hi,
t_start, t_end, area_start, area_end, perimeter_start, perimeter_end,
steps, new_cells, boundary_steps, interior_steps, sum_PA,
PA_end, PA_time, f_boundary, kappa_end, kappa_time, c,
width_start, height_start, width_end, height_end, rg2_end,
n_complete_B, n_complete_I, n_complete_cycles,
clipped_B_steps, clipped_I_steps, complete_I_steps,
L999_completed, mean_I_completed, mean_B_completed,
tail_threshold_steps, tail_complete_steps, tail_incomplete_lower_bound_steps,
quantile_gate_passed, censoring_gate_passed, status.
Key: (run_id, band_id). Define quantile interpolation before computing it.

Conservation: B+I=steps; new_cells=area_end-area_start; complete and clipped
episode contributions partition B/I without overlap. sum_PA is a floating
sum over departure states, reduced in fixed order (or a specified deterministic
accumulator). Closed bands have actual target endpoints; partial ones retain
their actual final states. Unreached bands have null times/counts, not zero runs.

## Episode intersections — dumps/episodes/<run_id>.csv

run_id, episode_id, label (B/I), band_id, observed_episode_start,
observed_episode_end, true_start_observed, true_end_observed,
overlap_start, overlap_end, overlap_steps, full_duration_if_known,
left_clipped_by_band, right_clipped_by_band, terminated_by_budget_or_escape.
Intervals use departure step indices [start,end). Unknown true duration is
null; observed duration is a lower bound. Record an episode crossing several
bands with a stable episode_id and distinct intersections. Duration distributions
must state their band attribution rule and deduplicate full episodes.

## Cycles — dumps/cycles/<run_id>.csv

run_id, cycle_id, B_episode_id, I_episode_id, cycle_start, cycle_end,
D, T, full_cycle_observed, contained_band_id (nullable).
Incomplete cycles do not enter complete-cycle means; their fragments still
enter exact finite-window accounting through the episode table.

## Analysis — results/analysis.json and results/rule_summary.csv

Store analysis command, commit/source/config/input hashes, seeds, cohort and
inclusion flow, train/test rules, bootstrap recipe, estimands, thresholds,
all prespecified verdicts and deviations. Include seed counts and between-seed
sd per rule/band. Publish no tail or kappa precision claim without its gate
counts, missingness and censoring report. Notebook consumes these small tables,
never raw episodes or checkpoints.

## Checkpoints and resume

Checkpoint must retain walker/colour state, ever-visited geometry, heading,
time, RNG state where applicable, open episode/cycle, active band counters,
next target and config/source identities. Verify resumed output byte agreement
against uninterrupted runs before trusting resumability. Atomic `.done` marker
only after payloads and hashes are durable; crash/error/partial target is
recorded explicitly and never treated as full target completion.

## Implemented contract / audit (2026-10-15 continuation)

The sampler writes per-spec `dumps/prod{16,8}/RULE_SEED.bands.csv`,
`.status.csv`, `.idur0.u32`, `.idur1.u32`, and a parameter-stamped `.done`.
The Rust example's HEADER defines the CSV names. Duration files are little-endian
u32 complete-contained I durations in completion order. Log2 bins and cycle
counts/time sums are aggregates; individual episode/cycle tables proposed above
are not emitted. Atomic payload renames precede the marker.

Resume is per finished trajectory, not a saved walker checkpoint: interrupted
trajectories are rerun from their seed. Existing markers check parameters only,
not source or payload hashes; do not resume a changed implementation into an
existing run directory. The continuation did not change sampler source. Audit
hashes describe the files checked after production, not a retrospective proof
of the original build environment.

`scripts/audit.py` requires all 44 x 64 specs at both widths, validates marker
parameters, endpoints, duration counts/sums, histogram totals and B/I partitions,
and writes `results/production.sha256`, `audit.json` and `run_status.csv`.
`analyse.py` verifies those hashes before loading data and writes `analysis.json`,
`analysis.txt`, `rule_summary.csv`. Its overall verdicts require coverage,
quantile, censoring and reliability gates as well as numerical thresholds.
Per-band `success` fields describe the numerical test threshold; use the overall
gate-aware fields for conclusions. Full all-production thread determinism is not
established by the 44-rule, seed-1001 replay in `determinism.json`.
