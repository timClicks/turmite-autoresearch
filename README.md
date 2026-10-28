# Turmite

A computational research project on generalised Langton's ants: their growth,
the memory they leave in the grid, and the structures that can be checked to
persist forever. Rules are strings over
`{L, R}`: the current cell's colour selects a turn, the colour advances modulo
the rule length, and the ant steps forward. Classic Langton's ant is `RL`.

We are investigating why many chaotic rules appear to grow in width roughly
as `t^(1/3)` (area roughly `t^(2/3)`), and how the pattern field, boundary and
mixing statistics produce that behaviour. These are research questions;
measurements, hypotheses and unresolved explanations live together here.

> **This repository is a meta-experiment as much as an experiment.** The
> cellular-automata question is a genuine one, but it is also a test case for
> how computational research might be done from now on: AI agents wrote most of
> the code, analyses, notes and draft paper under the author's direction, working
> to the reproducibility rules in [`AGENTS.md`](AGENTS.md) (registered
> predictions, an oracle implementation, lab notebooks, negative results kept).
> Whether that process produces trustworthy science is part of what is being
> tested, so treat the claims with the same scrutiny as any other result and
> check them against the code and data.

## Where the research stands

The project has grown from a rule census into a collection of controlled
experiments, field interventions, comparisons with other walkers, and a
parallel proof track. The cube-root growth law remains an empirical pattern
for a class of ants, not a theorem about all rules. Late highways, tethered
motion, crystal growth and column builders make that distinction important.

Some useful entry points into the current evidence:

- **Growth and classification.** The [census](experiments/archive/2026-10-census-sweeps/)
  and [draft synthesis](research-outputs/working-papers/cube-root-growth/README.md)
  bring together growth measurements and the diversity of behaviours. A
  finite run without a highway does not establish that one will never appear.
- **The cost of fresh ground.** The opening run of identical turns predicts
  how many boundary steps an ant spends per new cell. The
  [mechanism tests](experiments/archive/2026-10-c-law-mechanism/README.md) support
  part of this picture, but broader validation misses its accuracy target
  and the fitted constants remain unexplained.
- **Returning to the boundary.** Rule prefixes predict boundary occupation
  within familiar families, but [fail to transfer to held-out families](experiments/archive/2026-10-kappa-prefix-family-holdout/README.md).
  A [first-passage model](experiments/archive/2026-10-kappa-first-passage/README.md)
  also fails to predict larger territories from smaller ones. Explaining
  return times, rather than redescribing their scaling, remains an open problem.
- **Memory in the field.** [Local colour interventions](experiments/archive/2026-10-knockout-maps/)
  identify patches that help hold tethered ants near home. The proposed
  explanation in terms of excursion routes did not survive an occupancy control.
- **From simulation to proof.** The [RLRLLL column sweeper](experiments/archive/2026-10-rlrlll-macro-transition/README.md)
  has a checked repeating construction and independently reproduced constants;
  two shift lemmas are machine-checked in Lean. This is not yet an end-to-end
  formal proof of the trajectory from a blank grid: the bridge to the observed
  state still depends on a long simulation. See the [proof-track plan](notes/proof-track-2026-10-20.md).

The linked records distinguish registered predictions, observations, failed
tests and interpretation. [Open questions](notes/open-questions-hypotheses.md)
are an append-only history; read the later corrections before taking an older
claim as current.

## Find your way around

| Start here | What you will find |
|---|---|
| [Research blog](blog/index.html) · [publishing guide](blog/README.md) | Current highlights, active questions and reflections on failed explanations |
| [Experiments guide](experiments/README.md) | Investigations with protocols, lab notebooks, shareable notebooks, scripts and results |
| [Research notes](notes/) | Cross-cutting hypotheses, audits and unresolved questions |
| [Synthesis manuscript](research-outputs/working-papers/cube-root-growth/README.md) · [articles](research-outputs/articles/README.md) · [data papers](research-outputs/data-papers/README.md) | Draft writing and scripts that turn results into figures and numerical claims |
| [Browser explorer](web/) | Interactive simulations and census exploration; build instructions below |
| [Rust library and tools](src/) · [tests](tests/) | Reference and fast simulators, growth probes, highway detection and calibration walkers |

CPU simulations are checked against a reference implementation. Optional CUDA
batch runners accelerate large ant sweeps and probes, with separate CPU/GPU
equality tests. Rotor and random-walk controls help calibrate measurements;
neither passing software tests nor matching a control proves an ant mechanism.

## Try it locally

Use Rust with edition 2024 support and Python 3.12 or newer with `uv`.
Run commands from the repository root. The examples below use POSIX shell
syntax; adapt the pipeline and directory creation for your shell. See
[`AGENTS.md`](AGENTS.md) for environment and reproducibility guidance.

```bash
uv sync --frozen
cargo test --release --locked

# A small probe: run to 2^16 steps on a 512 x 512 grid, printing CSV.
# @1 selects a seeded random patch at the origin; rotor:1 is a control.
printf 'RLR\nRLR@1\nrotor:1\n' | cargo run --release --locked --bin probe -- 16 512

# Build the browser explorer from the committed census results.
mkdir -p web/dist
uv run --frozen web/build.py web/dist/explorer.html
```

Open `web/dist/explorer.html` in a browser. The small probe is a demonstration,
not enough data to estimate an asymptotic exponent. For research runs, follow
the relevant experiment's exact recipe and record the revision, inputs,
seeds, grid size and step budget. CUDA setup and batch-run guidance are in
[the experiments guide](experiments/README.md).

## Contributing with your agent

Pull requests run the CPU oracle tests, simulator smoke checks, small
reproducibility checks and CUDA compilation. Hardware GPU checks are manual.
See [CI commands and GPU runner setup](.github/CI.md).

You can help by directing your coding or research agent to work on this repo.
Reproductions, careful criticism, negative results, bug fixes and clearer
documentation are all useful contributions. You do not need a new growth
mechanism or a GPU to get started.

1. Fork and clone the repository, then open the clone in your agent's workspace.
2. Have it read [`AGENTS.md`](AGENTS.md) first. That file contains the working
   conventions, validation requirements and reproducibility standards. Have
   it inspect the available toolchains and resources before choosing commands
   and run sizes for your environment.
3. Pick one bounded task. Read the relevant notes and the latest entries in the
   linked experiments before treating an older question as still open. Check
   GitHub issues and pull requests for overlapping work; for a substantial
   investigation, open an issue describing the question and proposed test.
4. Give your agent a time and compute budget. Start with a small reproduction
   or control before launching a long sweep.
5. Review its changes and evidence, then submit a focused pull request. Include
   the question or bug, what changed, exact reproduction commands, checks run,
   and limitations or checks skipped. Identify the agent's role and review its
   claims yourself.

Here is a starting prompt to copy and adapt:

```text
Help me contribute to this repository. Read AGENTS.md and follow its
instructions, then read the notes and experiment records relevant to this task:

Task: [one question to test, result to reproduce, bug to fix, or doc to improve]
Budget: [time limit, CPU/GPU availability, and maximum run size]

Check whether the task has already been answered or superseded. Make a small,
reviewable contribution within this scope. For an investigation, register a
timestamped hypothesis and quantitative predictions before measuring, use the
experiment template, and keep the lab notebook as you work. Record exact
commands, source revision, inputs, seeds, parameters and environment. Preserve
existing results and report failed tests and null findings honestly.

Validate changes with the relevant release-mode tests and reference oracle;
calibrate any changed estimator. Keep generated bulk data out of git. Finish
with a diff and a pull-request summary explaining the evidence, uncertainty,
reproduction steps, and anything you could not verify.
```

Good first tasks include reproducing a small committed result, checking a
numerical claim against its producing script, adding an oracle comparison for
a suspected simulation bug, or clarifying an experiment's reproduction steps.
For deeper research, choose an unresolved question and design a test that
distinguishes competing explanations. Record speculation separately from
observations, and preserve predictions when appending corrections.

## Reproducibility

Use release builds for simulations and `uv run --frozen` for Python analyses.
[CI documentation](.github/CI.md) lists the CPU oracle tests, deterministic
output checks, simulator checks and separate GPU validation commands.

For new experiments, copy [`experiments/_template/`](experiments/_template/) to
`experiments/proposed/YYYY-MM-slug/` (or `active/` once work starts; see
[`experiments/README.md`](experiments/README.md) for the buckets). Include the registered predictions, append-only
lab notebook, shareable notebook, scripts and small reproducible results.
Record seeds and source revisions, quantify uncertainty between seeds, and
keep large raw dumps in the experiment's ignored directories. See
[`AGENTS.md`](AGENTS.md) for the full requirements.

## Native GPU sweeps on macOS

The optional `wgpu` backend runs census sweeps through Metal on macOS. It also
builds for Vulkan and DX12 on other native platforms. It needs a compatible GPU;
CPU builds remain independent of GPU dependencies.

```sh
cargo run --release --locked --features wgpu --bin wgpu_sweep -- 2 6 32768 256 --lanes 64
printf 'RL\nRLR 7\n' | cargo run --release --locked --features wgpu --bin wgpu_sweep -- - - 1000000 8192
```

The runner supports blank and seeded backgrounds, sparse tiles, pool-pressure
retries, and the existing CPU highway detector and onset replay. Its CSV schema
matches `gpu_sweep`; its result contract is `fast::run`. Run
`wgpu_sweep --help` for memory and scheduling controls. The CUDA probe and browser
simulator remain separate instruments. No macOS speedup factor has been measured.
See [design, checks and limits](experiments/active/2026-10-macos-gpu/README.md).

## License

Code is MIT OR Apache-2.0, data (`experiments/*/*/results/` and Zenodo deposits)
is CC0 1.0, and writing and figures are CC BY 4.0. See
[`LICENSE.md`](LICENSE.md) for exactly what falls under which.
