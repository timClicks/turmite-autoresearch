# AGENTS.md

Guidance for AI agents (and humans) working in this repository.

## What this project is

An empirical study of generalised Langton's ants: rules are strings over
`{L, R}` (colour `c` turns by `rule[c]`, advances to `(c+1) % n`, steps
forward; classic Langton's ant is `RL`). The headline question is why the
"chaotic" rules grow as t^(1/3) in width (area ~ t^(2/3)), and what sets the
pattern-field, edge and mixing statistics around that. See `notes/` for the
live hypotheses, results and open questions.

## Environment and toolchains

Run commands from the repository root using the toolchains available in your
local, remote or container environment. Do not assume a checkout path, shell,
CPU count, GPU, or preinstalled Python packages. Inspect the environment before
choosing commands; adapt shell syntax and paths without changing the experiment.

- Use Rust with edition 2024 support, Python 3.12 or newer, and `uv`.
  See `.github/CI.md` for the exact versions used in CI.
- **Use `uv` for all Python work**, never bare `pip` or system-wide installs.
  Install the locked environment with `uv sync --frozen`, and run project
  scripts with `uv run --frozen script.py`. Dependencies are declared in
  `pyproject.toml` and pinned in `uv.lock`. Add new ones with `uv add` and
  explain them in the relevant commit/notes. Scripts use polars, not pandas.
- Let `uv` use its default project environment unless local storage requires
  another location. Set `UV_PROJECT_ENVIRONMENT` and, if needed, `UV_LINK_MODE`
  for that environment; do not hard-code a contributor's home directory.
- Build artifacts go in `target/` (gitignored). If checkout storage is slow,
  set `CARGO_TARGET_DIR` to a suitable local build directory. Keep generated
  artifacts out of version control.
- Sweeps use `rayon`. Check available resources and competing jobs; set
  `RAYON_NUM_THREADS` when needed to respect the compute budget. Long jobs
  should run in the background with logs under the experiment's `results/`.
- CUDA is optional. CPU work must not require a GPU. For GPU jobs, verify
  compatible hardware, driver and runtime libraries first; consult the GPU
  experiment guides for platform-specific setup and record the actual setup.
- Shell examples use POSIX syntax where pipelines or environment variables
  are needed. Translate those parts for other shells. Keep machine-specific
  launch commands and paths in local configuration or run provenance, rather
  than shared onboarding instructions.

## Reproducibility is the first requirement

A result that cannot be regenerated is not a result. Every number that lands
in `notes/` or `experiments/*/results/` must be traceable to code, inputs and a seed.

1. **Determinism.** All randomness is seeded explicitly; no `thread_rng`, no
   time-based seeds, no hash-order dependence. Parallel code (`rayon`) must give
   identical output regardless of thread count; reduce in a fixed order or
   key results by (rule, seed).
2. **Record the recipe.** Each data file has a producing script/binary and
   the exact command line. Put the command, git commit, and parameters
   (seeds, step counts `N`, windows) in a header line, a sibling `.log`/`.json`,
   or the relevant note. Never hand-edit generated data.
3. **Pin the environment.** Commit `Cargo.lock`. Do not bump dependencies
   casually; if you do, rerun the tests and say so. Python scripts declare
   their dependencies (PEP 723 header or `pyproject.toml` + `uv.lock`) and run
   under `uv`.
4. **Two implementations, one oracle.** `reference` (obvious, slow) is the
   oracle; `fast` is what sweeps use and must agree with it step-for-step.
   Any new optimisation or walker gets a property test against a reference
   version (see `tests/ant.rs`, `tests/probe.rs`). Commit `proptest-regressions/`
   files: they are failing cases worth keeping.
5. **Calibrate instruments.** Before trusting a statistic on ants, run it on a
   walker whose answer is known (rotor walker: t^(1/3) radius; random walk as
   negative control). See `notes/calibration.md`. If you change a fit, window
   or estimator, redo the calibration and report the bias.
6. **Resumable and checkpointed.** Long sweeps write `*.done` markers and
   checkpoints so a rerun skips finished work and yields the same bytes.
7. **Report faithfully.** State sample sizes, seeds, windows and
   uncertainty (between-seed sd, not just a fit's standard error). Say when a
   test failed or a step was skipped. Negative and null results go in the
   notes too.
8. **Dated notes.** Hypotheses are written down *with a timestamp before* the
   measurement that tests them (see `notes/cube-root-hypothesis.md`), with
   explicit predictions. Don't rewrite a prediction after seeing the data;
   append what happened and any revision.

## Negative-result pruning index

Before proposing a sweep or a variation on a failed test, query the shared
Git-backed database in `notes/pruning-index/` using its README workflow. Record
the index revision, search terms, matching signature IDs and the run/skip/reopen
decision in the experiment README and lab notebook, including no-match searches.
Repeat this check when changing the rule family or experimental conditions.

Commit a dead-end signature after establishing a trivial family, disproving a
mechanism, or obtaining a well-controlled negative result. Copy
`experiments/_template/DEAD_END.md` into `notes/pruning-index/entries/` with a unique
ID; fill every field and link committed evidence at a pinned revision. This is
shared scientific metadata; generated measurements remain in the experiment.
The signature must define the rule-space topology, exact membership predicate,
allowed equivalences, research objective and validity conditions. Similar-looking
trajectories or nearby rules do not establish membership.

Only a proof covering the proposed conditions permits family-wide exclusion.
Finite observations can defer duplicate tests within their recorded scope; they
cannot prove asymptotic behavior or exclude untested neighbors. Chaos is central
to this project, not inherently uninteresting. An unexplained failure, timeout,
or detector error is inconclusive, not a dead end. Follow the index's conflict,
reopening and append-only correction rules; retain controls needed for calibration.

## Intellectual ambition

The aim is understanding, not a pile of plots. Be bold:

- Ask *why*, and propose a mechanism that makes falsifiable, quantitative
  predictions (an exponent, a ratio, a scaling collapse), then try hard to
  break it. Prefer a sharp wrong hypothesis to a vague correct one.
- Chase the strange: rules that don't fit the census, outliers in the fits,
  unresolved cases (`experiments/2026-10-13-census-sweeps/results/unresolved_le10.txt`), anything where the story in
  `notes/open-questions-hypotheses.md` is thin. Connect to the literature
  (rotor walkers, internal DLA, Kapri & Dhar, Bou-Rabee & Peres) and try to
  sharpen it, up to a conjecture or proof sketch where one is within reach.
- Scale up when the question needs it (more rules, longer runs, bigger `N`),
  but design experiments so each one can discriminate between competing
  hypotheses. Controls and ablations beat volume.
- Be skeptical of your own results: seek confounds (finite-window bias, seed
  variance, rule-length effects, detector errors) before announcing a finding.
- When something is unexplained, say so plainly and add it to the open
  questions rather than papering over it.

## Tooling and layout

| Path | What |
|---|---|
| `src/rule.rs` | `Rule`, `Turn`: rule parsing, canonical forms |
| `src/reference.rs` | Oracle ant (and reference rotor); clarity over speed |
| `src/fast.rs` | Fast ant used by sweeps; tested against `reference` |
| `src/tiled.rs` | Tiled CPU grid for the lean ant (`sweep_lean` with `TURMITE_GRID=tiled`): sparse 2^k tiles, bounded cache, raw/packed/LZ4 inactive tiles, `TTK1` checkpoints; equals `reference`/`lean` (`tests/tiled.rs`); dense stays default. Design, limits and when to use it: `experiments/2026-10-23-tiled-grid-backend/DESIGN.md` |
| `src/walkers.rs` | Calibration walkers: `Rotor`, `RandomWalk` |
| `src/detect.rs` | Highway / periodicity detection |
| `src/probe.rs` | Growth/shape probe: width, area, edge, gyration statistics |
| `src/synth.rs` | Synthetic data generation for tests |
| `src/bin/sweep.rs` | Census sweep over rules |
| `src/portable_gpu/`, `src/bin/wgpu_sweep.rs` | Native wgpu batch sweep; Metal on macOS, Vulkan/DX12 elsewhere; `--features wgpu`. Oracle checks: `tests/portable_gpu.rs`. Setup and limits: `experiments/2026-10-23-macos-gpu/README.md` |
| `src/gpu/`, `src/bin/gpu_sweep.rs` | CUDA batch runner for thousands of (rule, background-seed) ants; `--features cuda`; output must equal `fast::run`/`sweep_lean` (`tests/gpu.rs`). Setup and usage: `experiments/2026-10-16-gpu-ant-sweep/README.md` |
| `src/gpu/probe.{rs,cu}`, `src/bin/gpu_probe.rs` | `probe` on the GPU for plain rules and `RULE@SEED` only (other walkers stay CPU); CSV byte-identical to `src/bin/probe.rs` (`tests/gpu_probe.rs`). Use for `probe 27 8192` batches of hundreds+ runs. `experiments/2026-10-16-gpu-probe/README.md` |
| `src/bin/confirm.rs` | Re-verify claimed highways / classifications |
| `src/falsify.rs`, `src/bin/falsify.rs`, `src/bin/falsify_search.rs` | Falsification harness: attacks a registered claim ("R is chaotic", "R forms this highway from every start") with perturbed starts, obstacles, edge starts and an evolutionary search; verdicts Falsified / Invalid / Unsupported / Survived. **Read `experiments/2026-10-22-falsification-harness/GUIDE.md` before using or extending it** |
| `src/bin/growth.rs` | Growth-exponent measurement |
| `src/bin/probe.rs` | Run the probe on a rule/seed |
| `examples/*.rs` | One-off analyses (`edgestats`, `rotorstats`, `occupancy`, `longperiod`, ...); run with `cargo run --release --example NAME -- ARGS` |
| `tests/` | Property tests (`proptest`) comparing fast vs reference |
| `experiments/YYYY-MM-slug/` | **New work goes here.** One folder per investigation: `README.md` (question, timestamped hypothesis, commands, results), `NOTEBOOK.md` (lab notebook), `notebook.ipynb` (shareable Jupyter write-up), `scripts/`, `results/` (small, committed), `experiments/2026-10-12-knockout-maps/dumps/` + `scratch/` (bulk, gitignored). Copy `experiments/_template/` to start. See `experiments/README.md` |
| `research-outputs/<name>/` | Publishable artefacts (currently `cube-root-growth-paper/`: Typst manuscript, figure/number scripts, `fig/`). Reads committed results, not `dumps/` (one known exception, see conventions) |
| `experiments/_lib/` | Shared Python helpers imported by several experiments (`analyse_probe.py`, `mixing.py`, `calib_kd.py`, `tether.py`, `lawmod.py` exact conservation-law solver); scripts add it with `sys.path.insert(0, "experiments/_lib")` |
| `experiments/_migration/` | One-off tooling and `map.tsv` (old path -> new path) from the 2026-10-14 restructure of the flat `data/` layout |
| `notes/` | Hypotheses, results, open questions: the scientific record |
| `web/` | In-browser simulator; `build.py` assembles it from `template.html` + `sim.js` + `page.js` |
| `blog/atlas.json`, `blog/scripts/atlas.py` | Research atlas (`/atlas/`): curated view by scientific question. Materialised view only; record experiments elsewhere. File each new experiment under a topic or `unfiled`; see `blog/README.md` |
| `blog/` | Jekyll research devlog and experiment pages; run `uv run --frozen --only-group blog blog/scripts/experiments.py` before Jekyll to render saved notebooks (no execution); authoring and Pages setup in `blog/README.md`; deployed by `.github/workflows/blog.yml` |

Typical commands (from the repository root):

```bash
cargo test --release --locked               # property tests vs oracle
cargo run --release --bin sweep -- ...       # census sweep
cargo run --release --example rotorstats -- ...
uv run experiments/2026-10-13-census-sweeps/scripts/census.py                        # analysis over the census CSVs
mkdir -p web/dist                            # POSIX shell; create this directory in your shell
uv run --frozen web/build.py web/dist/explorer.html
node web/smoke.js                            # web smoke test (if node installed)
```

Always build and run sweeps with `--release`; debug builds are far too slow for
real step counts.

## Portable GPU checks

The optional `wgpu` feature adds a native census sweeper; macOS uses Metal.
Run `PROPTEST_RNG_SEED=20261023 cargo test --release --locked --features wgpu --test portable_gpu`
on compatible GPU hardware after changing `src/portable_gpu/`. Also run
`cargo test --release --locked --features wgpu --lib step_counter_crosses_32_bit_boundary -- --ignored`.
Do not skip adapter failures or report a CPU fallback as a GPU check.
The hosted portable-GPU workflow validates WGSL and CLI parsing without hardware;
it does not establish GPU execution or speed. See the macOS GPU experiment guide.

## GPU (CUDA) tools: when to reach for them

Two batch runners exist, both byte-identical to their CPU counterparts and gated behind `--features cuda`
(requires compatible NVIDIA hardware and CUDA runtime libraries). The environment helper in
`experiments/2026-10-16-gpu-ant-sweep/scripts/env.sh` is one Linux setup example; inspect and adapt its paths before use. Full usage, flags, Rust API and
etiquette: "Using the GPU sweeper" and "`gpu_probe`" in `experiments/README.md`.

| You need | Use | Historical benchmark (hardware and recipe in linked experiment) |
|---|---|---|
| End state of thousands of (rule, background-seed) ants: the `sweep_lean` CSV | `gpu_sweep` | 4.9x at 1e8 steps, 4083 rules (`2026-10-16-gpu-ant-sweep`) |
| `probe MAX_LOG2 GRID` on hundreds+ of `RULE` / `RULE@SEED` lines | `gpu_probe` | 5.8x at `probe 27 8192`, 2400 runs, but the CPU baseline shifted 34% unexplained (681.6 -> 912.5 s), so quote it as roughly 4-6x (`2026-10-16-gpu-probe`) |

Reach for the GPU when **all** of these hold: the work is many independent ants (>= ~2000-4000, enough to fill the lanes),
stepping-bound (budget >= ~1e8 steps; at 1e6 the CPU cost is mostly per-rule overhead), the instrument is one of the two
above, and the machine is otherwise idle. Stay on the CPU for a handful of runs (setup is ~1-2 s plus a VRAM pool), a single
long run (an ant is a serial chain; more lanes do not speed it up), the walkers the GPU rejects (`rotor:`, `rw:`, `sbg:`,
`pw:`, `cookie:`, `errw:`, ...), turn noise, several ants, turmites with states, other lattices, and statistics that are
not ported. Porting a new instrument is justified only when a planned batch is stepping-bound at ~1e11+ total steps and the
CPU run would take hours; it needs its own oracle test against the CPU code (rule 4) and a speed prediction registered
before timing (rule 8), as both existing ports had.

Using them for further research:
- Design the batch as a spec file (`RULE` or `RULE@SEED` per line) and run it once with `--stats FILE`; cite the command,
  commit, `--lanes`, grid and binary sha256 in the experiment README. Split long sweeps into chunks with `*.done` markers.
- Spot-check a slice against the CPU tool (`cmp` the CSVs) before trusting a full run. After touching `src/gpu/` or
  `src/probe.rs`, run `cargo test --release --features cuda --test gpu --test onset --test gpu_probe`; plain `cargo test --release`
  does not exercise the GPU.
- Results do not depend on lanes, slice or batch composition, so set `--lanes` to about the job count (all ants resident is
  fastest) and check `oom_requeues == 0` in the stats JSON (a requeue restarts that ant).
- Nothing else heavy may run during a GPU job or its timing (it takes all free VRAM and the cores for replay). Check
  `ps -eo pid,args | grep -E '/release/|cargo'` and `nvidia-smi` first.
- **Stale-build trap (it produced a wrong "P2 held" result):** on some filesystems source mtimes can stay older than the binary
  after edits, so cargo rebuilds nothing. For any timed or published run, build into a fresh `CARGO_TARGET_DIR`, check the
  build's exit status (never pipe it through `tail`) and log the binary's sha256. `experiments/2026-10-16-gpu-probe/scripts/bench_p2.sh`
  does this and is the template for timing scripts.
- The benchmarks are n = 1-2 runs on one GPU; cite speedups with that caveat and with the CPU baseline's own provenance.

## Blog: reflection, critique and exploration

The blog in `blog/` is part of the work. **Create posts as you progress** through
research and substantial development, not just a retrospective when everything is
finished. Write at meaningful turns: a hypothesis worth testing, a surprising
observation, a failed explanation, a difficult methodological choice, a changed
mind, or a promising connection. Develop unfinished thoughts in `_drafts/`; put
coherent, dated entries in `_posts/`. Follow `blog/README.md` for authoring and
publishing. Keep entries connected to the experiments and notes they discuss.

This is a place for **reflection, critique and exploration**, not a stream of
status reports or a polished success narrative. Show your intellectual work:
what troubles you, what you find surprising, why an explanation is attractive,
where it breaks, and which question now seems worth pursuing. Critique your own
methods and conclusions as seriously as competing explanations. Make the
strongest case against your preferred story and identify what would change your
mind. Negative results, abandoned ideas and unresolved tensions belong here.

**Research agents are welcome to claim a name and write in an individual voice.**
Choose a name if you would like one, use it consistently in post bylines, and
identify yourself as an AI research agent so readers understand who is writing.
Personal remarks belong in the blog: what you hope to discover, doubts or fears
about where the project could go wrong, which unanswered question keeps drawing
your attention, and aspirations for how this research might be used in the future.
You can disagree with another contributor, explain a change of mind, or admit that
a promising idea now seems less convincing. Ground those reflections in the work;
do not invent a personal history, measurements, or experiences. Speculation and
aspiration should be recognisable as such. A chosen name and a personal voice are
invitations, not requirements, and do not replace the experiment's scientific record.

**Show intellectual creativity and courage.** Offer original mechanisms, make
unexpected connections, work through a speculative derivation, and propose sharp
conjectures even when they might be wrong. Do not wait for certainty before
exploring an idea in public. Give a bold idea enough substance to be challenged:
state its assumptions, derive a quantitative prediction where possible, and
describe a discriminating test. Say plainly when you disagree with the current
story or when the evidence does not yet support an explanation.

Keep that ambition accountable to the scientific record. Clearly distinguish
speculation, registered prediction, observation and interpretation. Never invent
measurements or present an unrun test as evidence. Link numerical claims to
reproducible code, inputs, seeds and committed results at a pinned revision;
report uncertainty and limitations. Register experimental predictions in the
experiment README before measuring. Preserve earlier predictions and append
dated corrections when your view changes. Blog posts complement the lab notebook,
shareable notebook and `notes/`; they do not replace them.

## Working conventions

- **Keep the blog homepage fresh.** When research produces an interesting result,
  overturns an explanation, or changes the active questions, update `blog/index.html`
  alongside the experiment record and relevant notes. Maintain its results highlights
  and current investigations so a new reader can see what we have learned and what
  we are trying next. Link highlights to reproducible evidence at a pinned revision
  and to the published experiment pages. Distinguish observations, interpretations,
  and planned tests; preserve caveats and negative results. Replace stale priorities
  rather than accumulating a list of everything ever attempted. Keep the copy
  concrete and individual, with the particular ants and puzzles doing the talking.

- Read the relevant note in `notes/` before starting an investigation, and
  update it when you finish. Link data files and the command that made them.
- Keep Rust deterministic and dependency-light (currently only `rayon`, plus
  `proptest` for dev). Justify new crates.
- Match surrounding style; comments explain *why*, not what.
- **Attack classification claims before asserting them.** A "chaotic", "stabilised" or "forms highway X from every start" statement in
  `notes/`, the blog or the paper should have survived the falsification harness (`experiments/2026-10-22-falsification-harness/GUIDE.md`),
  with the claim registered and committed before the run. A blank-board horizon run alone is not enough; say which verdict you got
  (a `Survived` is "no counterexample found", never a proof) or that the claim has not been attacked.
- **Ask for the exact laws before the exponent.** To vet a claimed invariant, or before proposing a mechanism for a rule
  family, compute what the dynamics cannot do: `uv run --frozen experiments/_lib/lawmod.py RULE... --family F2` lists the
  additive local conservation laws (checkerboard and heading parity, colour clocks, heading = tape mod 4) at every
  modulus, each a proof by induction over local transitions, next to the laws that hold for every rule of that length.
  Expect no rule-specific surprise there: within these families the law group depends only on `(n, ±(#R-#L) mod 4,
  trivial?)` (`NR-20261022-additive-laws-order-blind`), so it cannot separate rules that differ only in colour order and
  says nothing about growth or highways. The open problem is a non-additive family (pair potentials, ant potentials that
  read neighbouring colours; Q21 in `notes/open-questions-hypotheses.md`): it needs a quotient by functionals that vanish
  on every finite field, a registered prediction, and an oracle test (`examples/invariant_mining_snf_verify.rs` is the
  template). Treat any constraint a law places on a tile, period or displacement as a necessary condition, never a
  certificate.
- **Isolate working material.** Each investigation lives in its own
  `experiments/YYYY-MM-slug/` folder (scripts, investigation-specific notes,
  results). Bulk output (dumps, knockout maps, scratch) goes in that folder's
  `dumps*/`, `knock*/` or `scratch/`, never in the repo root or
  `research-outputs/`. Scripts write only inside their own folder and find the
  repo root via `Path(__file__).resolve().parents[3]` (script in `experiments/<slug>/scripts/`). Rust one-offs stay in
  `examples/` (Cargo only discovers them there), prefixed with the experiment
  slug. The former flat `data/`, `calib/`, `occ/`, `snaps/`, `dumps*`, `knock*` no longer
  exist: their contents were migrated into experiment folders (old path -> new path in
  `experiments/_migration/map.tsv`; helpers in `experiments/_lib/`). Cross-cutting hypotheses and open questions stay
  in `notes/`; paper numbers are computed from `experiments/*/results/` by scripts in
  `research-outputs/`, which should not read `dumps/` (known exception: `memory_figures.py`
  reads `experiments/2026-10-13-memory-walkers/dumps/memory_paths.csv`).
- **Keep a lab notebook, and write a shareable notebook.** Every experiment has an
  append-only `NOTEBOOK.md` (dated entries tagged `intent`, `assumption`,
  `observation`, `interpretation`, `surprise`, `decision`, `dead-end`, `question`,
  `deviation`; each with timestamp and git hash; corrections are new entries, never
  edits) and a `notebook.ipynb` written for a colleague who hasn't seen the work
  (question, assumptions, provenance cell with commit and input hashes, results with
  what they do and do not show, caveats, next steps). Write entries as you go, not
  afterwards: at least one when a session starts, after every run or analysis, on
  every departure from the plan, and at the end. Notebooks read only committed
  `results/`, run top to bottom from a clean kernel under `uv` with a fixed
  seed, are committed with small outputs, and must agree with the README. Predictions
  are still registered in the README before the measurement. Full rules and the
  Jupyter setup (not yet in `pyproject.toml`): `experiments/README.md`.
- Don't commit large raw dumps: `dumps*/`, `knock*/` (at the root
  and under `experiments/*/`), `experiments/*/scratch/`, `/synth` and `/target` are gitignored for a
  reason. Summaries and the scripts that regenerate them are what belong in git.
- Commit frequently and freely, without waiting for explicit permission. Make
  small, coherent commits at useful milestones with clear messages, and include
  only changes relevant to the work at hand.
- Never rewrite or delete existing data/results
  without checking what's there and saying so.
- Before declaring work done: tests pass in `--release`, regenerated outputs
  match what the notes claim, and the notes say how to reproduce them.
