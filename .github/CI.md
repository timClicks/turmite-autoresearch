# Continuous integration

Hosted checks run on pushes and pull requests, and can also be dispatched
manually. They use Ubuntu 24.04, Rust 1.98.1, Python 3.12 with the committed
`uv.lock`, and Node 22.13.0 with `web/package-lock.json`. Rust property tests
use `PROPTEST_RNG_SEED=20261019`; keep regression cases committed.

| Workflow | Contract |
|---|---|
| Rust correctness | `cargo test --release --locked`: CPU instruments and reference agreement |
| Simulator checks | Build from committed results; check page initialization, charts, simulation, pause/resume, rule selection and mechanism readouts |
| Small reproducibility checks | Compare sweep/probe CSV bytes at 1 and 3 Rayon threads; check estimators against exact answers and an independent PRESS calculation |
| Portable GPU compilation | Linux/macOS builds, WGSL validation and CLI parsing with `wgpu`; no hardware execution |
| CUDA compilation | Compile every target with `cuda`; no GPU required and no runtime kernel validation |
| GPU oracle checks (manual) | Run `gpu`, `onset` and `gpu_probe` equality tests on dedicated CUDA hardware |

The existing Research blog workflow builds and checks the site separately.
The simulator workflow saves the generated HTML for seven days; reproducibility
and GPU evidence is retained for fourteen days. Download it for diagnosis;
these artifacts are not committed scientific results.

The reproducibility batch uses every canonical nontrivial rule of lengths
2–6, 32,768 steps and a 256-cell grid. Probe runs use maximum octave 14,
grid 256, `RL`, `RLR`, `LLRR`, patched `RLR` seeds 1 and 2, and rotor/random
walk seeds 1 and 2. `recipe.json` records the revision, exact arguments,
input, thread counts, compiler and binary/input/output hashes. This tests
deterministic output on one toolchain; it does not re-estimate growth laws.
The selected analysis check uses seed 20261016, committed configuration and
synthetic inputs; it never reads bulk dumps or rewrites experiment results.

## Run hosted checks locally

Use WSL on Windows, from `/mnt/f/Code/turmite`:

```bash
export UV_PROJECT_ENVIRONMENT=$HOME/.venvs/turmite UV_LINK_MODE=copy
export PROPTEST_RNG_SEED=20261019
cargo test --release --locked
cargo check --release --locked --features cuda --all-targets
cargo build --release --locked --bin sweep --bin probe
uv run --frozen python .github/scripts/check_determinism.py --output /tmp/turmite-reproducibility
uv run --frozen python experiments/2026-10-15-fixed-area-cycles/scripts/check_analysis.py
npm ci --prefix web
mkdir -p web/dist
uv run --frozen python web/build.py web/dist/explorer.html
npm test --prefix web
```

The simulator tests stub canvas drawing and drive animation frames explicitly.
They validate page behavior and displayed numbers, not pixel appearance or
browser compatibility. Assertion failures and page exceptions exit nonzero.
`jsdom` is a new development-only dependency, pinned along with its transitive
dependencies in the npm lockfile; it is not shipped with the simulator.

## Enable manual GPU validation

Register a dedicated Linux x64 runner with labels `self-hosted`, `linux`,
`x64`, `cuda`. Install Rust toolchain **1.98.1**, an NVIDIA driver, and NVRTC
12.9.86 under `$HOME/cuda-libs` following
`experiments/2026-10-16-gpu-ant-sweep/scripts/env.sh`. The runner service must
have `cargo`, `rustc`, `rustup` and `nvidia-smi` on its PATH. In WSL, register
and run the service inside WSL rather than as a Windows runner.

Create the `gpu-ci` GitHub environment and restrict deployment branches to the
default branch. Where available, require a maintainer review. Restrict the
runner to trusted workflows/repositories; a label alone is not an access
control. Never use this runner for fork PRs. See GitHub's
[self-hosted runner security guidance](https://docs.github.com/en/actions/reference/security/secure-use).

After the workflow reaches the default branch, select **GPU oracle checks
(manual) → Run workflow**, using the default branch. Other refs are skipped.
The job checks for active compute processes and simulation/build commands,
uses a fresh build directory to avoid stale binaries, and records revision,
compiler, hardware, executable hashes and test output. It serializes its own
runs, but cannot prevent unrelated local jobs from starting: keep the runner
dedicated and the device idle throughout validation. Fresh build directories
are left under the runner's temporary directory for normal runner cleanup.

The workflow adds no runner registration or repository settings automatically.
Until hardware is registered, a dispatch waits for a matching runner.

Portable GPU hardware checks use `PROPTEST_RNG_SEED=20261023 cargo test --release --locked --features wgpu --test portable_gpu`. The private counter-carry check is explicitly enabled with `cargo test --release --locked --features wgpu --lib step_counter_crosses_32_bit_boundary -- --ignored`. These need a real GPU; hosted compile checks do not replace them.
