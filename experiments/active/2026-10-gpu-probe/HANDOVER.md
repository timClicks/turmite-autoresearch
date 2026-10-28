# Handover: GPU probe (rewritten 2026-10-19 after finishing the 2026-10-19 morning handover)

## State in one paragraph
`gpu_probe` (GPU port of `probe` for plain rules and `RULE@SEED`) is implemented, committed and byte-identical to the CPU `probe` on every
full-scale run (all 2400 kappa-leadrun specs, 9/9 HEAD-build runs). P1, P3, P4 held. **P2 is falsified at HEAD from above**: on a verified
build the speedup is 5.81x (CPU 912.5 s vs GPU 157.0 s), over the registered 4.9x line. The old "P2 held, 3.84x" came from a stale binary.
The CPU baseline moved from 681.6 s to 912.5 s (+34%) for a reason **not found**, so quote the speedup as roughly 4-6x (n = 1 CPU run).

## Results (details in README "Results", "P2 re-measure", NOTEBOOK)
| Prediction | Status | Evidence |
|---|---|---|
| P1 correctness | held | 24-spec spot check; all 2400 specs identical to the CPU dump in 9 HEAD-build runs; tests on a verified build pass |
| P2 speed (2-6x, falsified at >= 4.9x) | **falsified from above at HEAD** | `results/bench_p2.log`: gpu 157.06/156.94 s, cpu 912.49 s, 5.81x. Stale-build 3.84x superseded |
| P3 memory | held | 0 requeues, pool about 2.41e6 tiles |
| P4 lanes | held | device time 278.1 / 217.2 / 154.3 s at 1024 / 1536 / 2400 lanes |

Verified tests (`~/turmite-target-p2`, HEAD 6de71f2): `cargo test --release` all ok; `--features cuda --test gpu --test onset --test gpu_probe` 7/7, 1/1, 5/5.

## Done in this round
`scripts/bench_p2.sh` (new, the template for timed runs), `bench.sh` and `spotcheck.sh` fixed (build exit status, stale-binary check), README and
NOTEBOOK appended (not edited), `notebook.ipynb` extended and executed. GPU guidance added to `AGENTS.md` and `experiments/README.md`.

## Open
1. **Why is the HEAD CPU `probe` 34% slower than the old one (681.6 s)?** Cheap test: build `probe` at the commit before the `src/probe.rs` refactor into a fresh
   target dir and time a 100-spec subset against HEAD, on an idle machine; also rerun the full CPU timing once to get a spread (n = 1 so far).
2. Optional, unmeasured: 16-bit cell vs two byte planes; one-byte packing for n <= 32. Only if VRAM binds (about 13-19 GB of 20 used at 2400 lanes).
3. Per-lane throughput falls 23% from 1024 to 2400 lanes; cause untested (memory traffic is a guess).

## Things to know
- Env: `source experiments/active/2026-10-gpu-ant-sweep/scripts/env.sh` in every WSL build/run. Use `wsl -e bash -lc "..."`; run long jobs via the Bash tool's background mode.
- Stale-build trap: on `/mnt/f` source mtimes can stay older than the binary, so cargo rebuilds nothing. Use a fresh `CARGO_TARGET_DIR`, check build status, log the sha256.
  `~/turmite-target` binaries since 10-16 are suspect; verified dirs are `~/turmite-target-p4` and `~/turmite-target-p2`.
- Timing is contaminated if anything else is live (`ps -eo pid,args | grep -E '/release/|cargo'`, `nvidia-smi`).
- The patch is initialised at tile allocation (it straddles four tiles at 8192); do not "simplify" it to the first tile.
- `gpu_probe` rejects non-ant specs; rotor/rw/sbg/pw/cookie/errw stay CPU-only. `total_steps` counts the budget for non-escaped runs only.
- Untracked and not mine to commit: a stray `notebook.ipynb` at the repo root, `numbers_check.py`, `run_check.sh`, `.claude/`, `.codex/`, `.githooks/`; plus modified paper/notes files from other work. Stage explicit paths only.
- `scratch/` (gitignored) holds benchmark CSVs and helper scripts.
