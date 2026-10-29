# Python tools without Rust

The dependency-free sparse simulator is in `experiments/_lib/turmite_sim.py`;
the Q33 CLI and independent-oracle checks are in `scripts/`. Their PEP 723
metadata lets uv run them without installing the repository's analysis stack.
Python 3.12 or newer and uv are sufficient. No Rust, NumPy, compiler or GPU is
needed. No dependency lockfile is necessary because these scripts have no
third-party dependencies. The root `uv.lock` is unchanged.

Run from the repository root:

```sh
uv run --offline --script experiments/proposed/2026-10-q33-cap-crossover/scripts/test_python_sim.py

uv run --offline --script experiments/proposed/2026-10-q33-cap-crossover/scripts/python_sim.py \
  --rule RLL --policy ant --steps 65536 --suboctaves --hull \
  --output-dir experiments/proposed/2026-10-q33-cap-crossover/scratch/python-ant

uv run --offline --script experiments/proposed/2026-10-q33-cap-crossover/scripts/python_sim.py \
  --rule RLL --policy persistent-fresh --cap 32 --seed 20261029 --steps 65536 \
  --suboctaves \
  --output-dir experiments/proposed/2026-10-q33-cap-crossover/scratch/python-cap32
```

Offline mode requires an installed compatible Python; omit `--offline` if uv
must download one. If the default cache directory is read-only, set
`UV_CACHE_DIR` to a writable local directory for these commands. The scripts
do not modify global Python installations or run `uv sync` for heavy analysis
dependencies.

Policies:

| Policy | Fresh departure | Revisit |
|---|---|---|
| `ant` | rule's colour-zero turn | rule[colour] |
| `fresh-set --fresh-set RLU` | uniform categorical R/L/U, same multiply-high mapping as Rust | rule[colour] |
| `persistent-fresh --cap M` | fixed straight-biased Q33 policy; reversal on the M-th fresh departure | rule[colour] |
| `persistent-fresh` without cap | same straight-biased policy, uncapped | rule[colour] |

The RNG draws once per step, including ant and cap-forced steps. Directions
are north/east/south/west with north at negative y, as in Rust. A dictionary
entry retains departure history even when its colour wraps to zero. The cap
origin exception is explicit. Use `--seed` for reproducibility; the simulator
does not interpret these arbitrary small runs as census sampling or as the
registered excluded pilot.

## Outputs and continuation

Each run needs a new output directory inside this experiment. Existing files
are never overwritten. Outputs are:

- `samples.json`: geometry and cumulative boundary/cap counters at powers of
  two, plus sub-octave samples if requested and the actual final state.
- `octaves.json`: complete local-window fits and boundary ratios. Without
  `--suboctaves` these are explicitly endpoint log ratios. With it they use
  the registered nine-point OLS schedule at sufficiently large clocks (very
  early integer times deduplicate). Partial windows are not fitted.
- `fresh_runs.json`: completed non-origin run counts and duration weights,
  the initial run separately, and the unfinished run with a censor flag.
- `checkpoint.json`: versioned, full sparse state including RNG and run
  accounting; can be reloaded without changing the future trajectory.
- `provenance.json`: configuration, actual argv, Python/platform, source and
  output hashes, starting/target/actual steps, resource status and timing.
  Timing/platform/path fields intentionally differ between environments;
  trajectory outputs are deterministic for the same configuration.

Resume with the total desired clock, rather than additional steps:

```sh
uv run --offline --script experiments/proposed/2026-10-q33-cap-crossover/scripts/python_sim.py \
  --resume experiments/proposed/2026-10-q33-cap-crossover/scratch/python-cap32/checkpoint.json \
  --steps 131072 --suboctaves \
  --output-dir experiments/proposed/2026-10-q33-cap-crossover/scratch/python-cap32-next
```

The checkpoint restores rule, policy, cap and seed; do not also specify them.
Resumed output contains only the continuation segment. It includes the
checkpoint state as its first sample; windows spanning a previous segment
need explicitly merged sample tables and are not silently inferred.

`--max-cells` defaults to one million departed cells. It checks before a birth
and leaves the state unchanged on failure. A resource stop writes a resumable
checkpoint, reports `resource_incomplete` and exits with code 2. Successful
completion exits 0. A new higher limit can be supplied when resuming. This is
a cell-count budget, not a precise RAM allocator. Checkpoints are written at
normal completion or this resource stop; abrupt interruption is not crash-safe
checkpointing. Hull computation is optional because sorting all departed
cells at every saved sample costs extra.

## Validation and scientific scope

The 14-test stdlib suite checks independent visit-count/vector-turn oracle
agreement across all small rules and several seeded policies, known SplitMix
vectors, exact sampling thresholds, colour-zero revisits, fresh bounds and
the origin exception, full-rescan geometry, hull degeneracies, synthetic
growth exponents, incomplete windows, checkpoint continuation and CLI resource
behaviour. It passed under uv/Python 3.12.14 in this environment.

Rust source semantics were inspected, but no cross-language execution check
has been performed here. The Python oracle is written independently from the
incremental simulator; it is not a substitute for a future Rust/Python trace
comparison. No speed advantage or production-scale throughput is claimed.
Use small explicit budgets first; Python can be adequate for many diagnostic
tasks, and the decision to use Rust should follow measured requirements.

This implementation measures departed area, bounding-box width, exact lattice
perimeter, boundary occupation and optional cell-centre hull, using the named
Q33 definitions. It is not declared byte-identical to the existing probe's
CSV schema or normalisation. Fresh-run duration weighting is **not** the Rev3
time-weighted *boundary-excursion* instrument. There is no crystallisation
detector, pre-entry depth instrument, rotor/control panel or complete Q33
gate/scoring pipeline yet. Runs cannot be treated as confirmation or used to
claim calibrated growth classes until those pieces and gates are completed.

The separate RLRLLL checker is untouched. Generated diagnostic outputs stay
in scratch/ and are not committed as scientific evidence. No registered
Q33 calibration, excluded pilot or confirmation has run, so the proposal
remains in proposed/.
