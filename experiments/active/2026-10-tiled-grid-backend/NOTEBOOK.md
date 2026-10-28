# Lab notebook: Tiled CPU grid backend

Append-only. Newest entry last. Never edit an old entry; correct it with a new one
(`corrects: <timestamp>`). Tags: intent, assumption, observation, interpretation,
surprise, decision, dead-end, question, deviation. See `experiments/README.md`.

Environment: Windows host, Rust 1.98.1 only inside WSL2 Ubuntu (6 vCPUs of the 8 logical CPUs of an Intel Xeon W-2125, 47 GiB);
builds use `CARGO_TARGET_DIR=/home/tim/turmite-target` on the WSL filesystem (not `/mnt/f`). Another contributor works in the
same checkout and WSL concurrently (their commits keep arriving on `main`; their untracked/modified files are not mine and are
never staged here).

### 2026-10-23 18:05 (+13:00) · 2ee0086 · intent
Add a memory-efficient CPU grid backend as an alternative to the dense grid, first for `sweep_lean`/`run_lean_ckpt`. Stages:
sparse tiles, then bounded cache + bit-packed inactive tiles, then block compression only if measured to pay. Dense stays default;
no new sweeps, no classification changes. Decision informed: whether tiled storage is worth recommending and for which workloads.

### 2026-10-23 18:15 (+13:00) · 2ee0086 · decision
Target is `sweep_lean`: it has checkpoints, highway/onset/extent reporting and the plainest dense cost (`LeanGrid::clear` writes
every byte, so resident memory is `threads x size^2`). Probe integration deferred until the stepping backend is correct, then
judged by size (its `Region::visit` writes the four neighbours of every new cell, across tile edges).

### 2026-10-23 18:22 (+13:00) · 2ee0086 · observation
Before designing, probed what lean does when `max_steps` ends exactly on the step that leaves the board (scratch test, then
pinned in `tests/tiled.rs::budget_ending_on_the_escaping_step_is_lean_compatible`). RL, boards 8/9/10: `fast::run` reports
`Escaped` at step 36/209/214; `run_lean` with that budget reports `Budget` with the ring position and extent (5,6), (0,9), (10,10)
against fast's (5,5), (9,9), (10,9). With one more step of budget both agree. The extent code computes `(idx % s) - 1` on a ring
cell (wraps for the left/top ring). Cause: lean detects escape by reading the sentinel on the *next* step.
Interpretation: a latent quirk of dense lean that only a budget landing exactly on the escaping step reaches.
Decision: tiled copies it (CSV equality is the contract); lean is not fixed here because that would change sweep CSVs; recorded
in DESIGN.md. `lean::finish_extent` now holds the old code verbatim with wrapping arithmetic (same bytes in release).

### 2026-10-23 18:25 (+13:00) · 2ee0086 · decision
Pruning-index preflight (engineering task; no sweep over a rule family). Index revision `2ee0086e075eb2b1fca04781870dff37aaaea48b`;
`git ls-files notes/pruning-index/entries` lists only `NR-20261022-additive-laws-order-blind`; `git grep -n -i -l -e tiled -e storage
-e memory -e backend -e grid -- notes/pruning-index/entries` found nothing. The sole entry concerns additive conservation laws, not
storage performance. Decision: run. No signature warranted by a performance result.

### 2026-10-23 18:30 (+13:00) · 2ee0086 · assumption
Design: reuse `lean::advance` unchanged inside `(T+2)^2` tiles whose halo and off-board cells are `SENT`, so the hot loop gains no
coordinate test; tile changes happen in `settle`. Assumed to cost one hash lookup per transition and to be competitive with dense
when transitions are rare. Untested until the benchmark.

### 2026-10-23 18:42 (+13:00) · c0b1d5d · observation
`tests/tiled.rs` (20 tests; 120-case properties for state vs `reference::Ant`, vs `run_lean`, vs `fast`, config independence, reuse
across rules, pack round trips; deterministic tests for escape through all four edges, one-colour rules, visited-colour-0, the
lean escape-budget quirk, Langton highway across many tiles, onset vs `highway_onset_flat` and the published 9976, checkpoint
exactness/rejection, tiny configs, huge board). First run: one failure, a bug in my test (a checkpoint test on a 40-cell board
escaped before the first save, so the file did not exist). Fixed the test, not the backend. Also found `RLLRLLLRRRLL` escapes a
512 board before 120k steps (my assumption in a roomy-board test was wrong; test now compares at the actual step count).

### 2026-10-23 18:44 (+13:00) · c0b1d5d · observation
Mutation check of the test suite: made `encode` write an empty touched plane. 13 of 19 tests failed (state vs oracle, vs lean, vs
fast, checkpoint, packing round trip, config independence, edge timing). The source was restored (diff against a saved copy: identical).

### 2026-10-23 18:44 (+13:00) · c0b1d5d · deviation
The mutation run made proptest write `tests/tiled.proptest-regressions` with six shrunk cases that fail only on the mutated
code. AGENTS.md says to commit regression files for real failures; these were not real failures of the shipped code, so the file
was deleted and three of the tiny cases (bits/n/size/steps) were kept as the explicit test
`tiny_board_cases_that_caught_a_dropped_touched_bit`. No genuine proptest failure of the shipped code has occurred, so there is no
regression file to commit.

### 2026-10-23 18:47 (+13:00) · c0b1d5d · observation
CSV identity, `sweep_lean 2 6 32768 256` (57 rules; the CI batch shape): dense at 1 and 3 threads identical; tiled identical to
dense for tile 2^6/unlimited/raw, 2^6/unlimited/packed, 2^6/2/packed, 2^6/4/raw, 2^3/2/packed, 2^2/2/packed, 2^4/7/packed,
2^5/3/raw, 2^10/4/packed, each at 1 and 3 threads (`cmp` on the CSV bytes). Script: scratch `csvcheck.sh` (not committed; the same
check is re-done inside `bench.sh` for every benchmark run).

### 2026-10-23 18:50 (+13:00) · c0b1d5d · surprise
The first identity run seemed to hang: tile 2^10 with cache 2 on a 256 board. Not a hang: the start is a corner of four tiles, the
ant circles it, a cache of 2 evicts a 1 MiB tile on almost every crossing, and encode+decode cost O(T^2). A thrash cliff to
document, not a correctness bug (config 2^10/cache 4 is identical to dense and fast). Two earlier shell mishaps are noise: a
`pkill -f` matched my own command line, and a non-login WSL shell lacked `cargo` (exit 127 on the first full-suite attempt; the
rerun passed).

### 2026-10-23 18:55 (+13:00) · c0b1d5d · observation
`PROPTEST_RNG_SEED=20261019 cargo test --release --locked` (all suites, CPU only; GPU not touched): exit 0. The `lean`, `lean_ckpt`
and `tiled` suites were re-run after the last test was added: all pass.

### 2026-10-23 18:58 (+13:00) · c0b1d5d · decision
Registered predictions and adoption criteria in README.md (before any timing). Benchmarks will be built from a `git archive` of the
registration commit into a fresh `CARGO_TARGET_DIR`, with binary hashes recorded by `scripts/build_bench.sh`.

### 2026-10-23 19:02 (+13:00) · e93d4c7 · deviation
First full benchmark pass (149 runs) reported the CSV differing from dense in 121 runs. Hand-run of one case showed byte-identical
output: the bug was in `scripts/bench.sh`, which deleted the dense reference CSV right after the dense run (the cleanup `rm` also hit
config A), so every later `cmp` compared against a missing file. Timings were unaffected, but identity and timing must come from one
consistent pass, so the script was fixed (`8d89328`) and the whole batch re-run (second pass, 19:0x). The first pass's numbers were
discarded, not used. Lesson recorded: an identity check that can fail "closed" is good, but look at one case by hand before believing
121 differences.

### 2026-10-23 19:08 (+13:00) · 8d89328 · observation
Second pass: 149/149 runs byte-identical to dense. Medians and ranges in `results/summary.csv`; headline: RSS 0.10-0.13x dense on
W1/W2/W4a, 0.003x on W4b (12.3 MiB vs 4227 MiB), 0.88x on W3 (footprint nearly fills the board). Throughput of B: W1 1.17x, W3 1.6x,
W2 0.55x, W4b 185x (dense zeroes 4 GiB). C64 on W3: 0.022x of B (768k misses). Machine load 0.7-1.0 at start/end, other contributor
idle at the time.

### 2026-10-23 19:12 (+13:00) · 8d89328 · surprise
P5 predicted B at 0.6-0.95x dense on W1 and W3. Observed 1.17x and 1.6x. Likely cause: 66-byte tile rows vs 8194-byte dense rows
(cache/TLB locality) - a hypothesis, not tested (an ablation would use a dense board of the footprint's size). The stage-D batch
(load 3.3) shows dense W3 at 0.9e8 steps/s against 1.3e8 earlier, so dense is noisy to about 20% and I treat the "faster than dense"
result as weak evidence; the same-batch comparisons B vs C vs L are firmer.

### 2026-10-23 19:15 (+13:00) · 8d89328 · observation
Codec (`tiled_grid_backend_codec 20000`, real central 64x64 tile after 3e6 steps): encode 10.4-13.1 us, decode 14.3-14.9 us per
tile; w = 2/4/4 gives 1536/2560/2560 bytes. Checkpoints of RLR/RRRRRRRLLRRR/RLLRLLLRRRLL at 1e8 steps (scratch/, gitignored) fed
`scripts/compress_estimate.py` (an independent parser of TTK1, which also verifies the FNV checksum): per-tile deflate-9 shrinks the
payload 1.95x / 28x / 80x, xz 1.74x / 28x / 74x. Criterion A5 (inactive payload >= 40% of C's RSS; >= 1.3x) fired for W3
(69%; 80x).

### 2026-10-23 19:20 (+13:00) · 8d89328 · decision
Built stage D (`Inactive::Compressed`, LZ4 block of the canonical payload via `lz4_flex` 0.14.0, `default-features = false`,
features std + safe-encode + safe-decode; one new package in Cargo.lock, no transitive crates; pure safe Rust, so no `unsafe`
dependency). Justification: A5. Checkpoints stay canonical (tests compare bytes across all four modes). Predictions D1-D5 registered
in README Addendum 1 before timing (commit `b53bcb6`).

### 2026-10-23 19:25 (+13:00) · b53bcb6 · observation
Stage-D batch (W1, W3; A, B6, C1024, L64, L1024, L4096; 55 runs, all byte-identical). W3: L1024 RSS 13.4 MiB (0.19x dense, 0.32x of
C1024) at 1.06x C1024's throughput; L4096 26.2 MiB; L64 thrashes (0.023x B). Compressed payload 295 KB for 11,520 tiles. D5 failed:
compression ~100x vs predicted 15-60x. A6 met.

### 2026-10-23 19:30 (+13:00) · b53bcb6 · interpretation
The strong W3 result reflects an unusually regular structure ("builder" rule, 25 bytes/tile after LZ4); for the chaotic W1 the
payload barely compresses (1.9x deflate) and it is small anyway. I would not extrapolate the 0.19x to chaotic rules. The recommendation
is therefore: sparse tiles broadly, packed/lz4 with a cache only for large structured footprints. Alternative explanations I have not
excluded: that B's speed over dense is a layout effect specific to this CPU's caches; that W3's structure is a periodic frame whose
tiles are near-identical.

### 2026-10-23 19:35 (+13:00) · b53bcb6 · question
Probe integration not done (see README). Would a tile-grid offset (start in a tile centre) recover W2's 0.55x? Untested.

### 2026-10-23 20:25 (+13:00) · cc5b228 · observation
Code review (see README Addendum 2). No correctness bug; fuzz of 720 cases vs dense lean, 0 failures. Confirmed a memory problem: a reused
`TiledGrid` keeps its high-water buffers across rules (61.2 MiB RSS after a big rule, unchanged over three following small ones).
Single-rule benchmarks did not exercise it. Recorded in the README; fix not applied.

### 2026-10-23 20:30 (+13:00) · 8cb574b · decision
Fixed the two Addendum 2 problems (retained buffers capped at 8 MiB in `begin`; O(1) LRU list). 22 tiled tests pass in release.
Not re-measured: mixed-batch RSS and throughput. See README Addendum 3.
