# Tiled CPU grid backend: memory and throughput of sparse and packed tiles

Bounded engineering experiment (no new science, no classification changes). Architecture, state
transitions, memory accounting, checkpoint format and limits: [DESIGN.md](DESIGN.md).

## Question and registered prediction

Registered 2026-10-23 18:58 +13:00, before any timing run. Starting revision `2ee0086e075eb2b1fca04781870dff37aaaea48b`;
implementation commit `c0b1d5d` (tests pass, CSV byte-identity checked, **no timing or memory measurement yet**). The working tree
is dirty with other contributors' files only (`experiments/archive/2026-10-sweeper-generalisation/`, `highway-decider`); benchmark
binaries are built from a `git archive` of the benchmark commit, not from the working tree.

**Question.** `sweep_lean` allocates `(size+2)^2` bytes per worker and writes all of them at the start of every rule
(`LeanGrid::clear`), so resident memory is `threads x size^2` whatever the ant does. Does a tiled grid (sparse 64x64 tiles; a
bounded cache of uncompressed tiles; bit-packed inactive tiles) give a useful reduction in peak resident memory at an
acceptable throughput cost, on workloads taken from the existing census?

**Backends compared** (same rule, board, budget, `RAYON_NUM_THREADS=1`; the CSV must be byte-identical, which is a hard gate):

| id | backend | settings |
|---|---|---|
| A | dense `LeanGrid` | |
| B | tiled, sparse allocation only | `TURMITE_GRID=tiled TURMITE_CACHE_TILES=unlimited` (tile 2^6; also 2^5, 2^7 on W1, W3) |
| R | tiled, bounded cache, raw inactive | cache 64, `TURMITE_INACTIVE=raw` (isolates caching/copy cost from packing) |
| C | tiled, bounded cache, packed inactive | cache 64, 1024 (and 16 as a thrash probe), `TURMITE_INACTIVE=packed` |
| D | block compression | **only if** criterion A5 below fires; otherwise not implemented |

**Workloads** (all from `experiments/archive/2026-10-census-sweeps/results/sweep_2_12_100M.csv`, board 8192, 1e8 steps unless noted;
the labels are finite-time descriptions of that run, nothing more):

| id | rule | role | evidence in the census run |
|---|---|---|---|
| W1 | `RLR` | compact irregular trajectory | budget, extent 998 x 1035; census class `blob` |
| W2 | `RRRRRRRLLRRR` | repeated local revisits | budget, extent 17 x 18 |
| W3 | `RLLRLLLRRRLL` | growing structured trajectory | budget, extent 7067 x 7068; census class `builder` (alpha 0.50) |
| W4a | `RL` | thin travelling trajectory | escapes the 8192 board at 222061 steps (highway, period 104) |
| W4b | `RL` | same, board 65536, 2e7 steps (does not escape) | memory is proportional to the path, not the board |
| W5 | `RRRRRRRLLRRR` | tile-boundary stress | W2 with tile 2^2 or 2^3 and cache 2: start cell is a tile corner, footprint spans many tiles |

**Predictions** (peak RSS = `VmHWM` of the process; ratios are medians of 5 interleaved repetitions; throughput is steps/s from
the wall time of the run, which includes grid construction):

- P1. Dense RSS is 68-80 MiB on every 8192 workload (the 64 MiB grid is fully written) and about 4.1-4.3 GiB on the 65536 board.
- P2. Empty-process baseline RSS is 2-8 MiB.
- P3. B: RSS <= 12 MiB on W1, <= 8 MiB on W2, <= 10 MiB on W4a, <= 20 MiB on W4b; on W3 55-70 MiB, i.e. 0.75-0.95 of dense
  (no real saving where the footprint nearly fills the board).
- P4. C (cache 64) on W3: payload 2560 B per tile (n = 12 gives w = 4: 2048 + 512 bytes) so RSS 38-46 MiB, 0.55-0.75 of B.
- P5. Throughput relative to dense (A = 1): B 0.6-0.95 on W1, 0.25-0.7 on W2 (the start is a tile corner, so a compact pattern
  crosses tile edges constantly), 0.6-0.95 on W3, 0.6-1.0 on W4a. C with cache 1024 on W1 (about 290 tiles touched, so nothing is
  ever evicted) is >= 0.95 of B. C with cache 64 on W3 is < 0.3 of B (miss rate x about 30 microseconds per miss dominates).
  C with cache 16 is a thrash and slower still.
- P6. Codec cost: encode and decode of one 64 x 64 tile at w = 4 are each 8-25 microseconds (measured separately, not in the
  main timing).
- P7. W5 with cache 2 shows transitions/step >= 0.1 and a throughput < 0.15 of dense.

**Adoption criteria** (registered; chosen for these workloads: the point of the backend is a smaller process, so memory is
required to move by a factor, while throughput only has to stay practical):

- A1. Exactness (gate): byte-identical CSV for every backend and setting on every workload, and `cargo test --release --locked`
  green. Failure rejects the backend regardless of anything else.
- A2. Sparse tiles (B) are *adopted as the memory-saving option* if on W1, W2, W4a, W4b peak RSS <= 0.25 x dense AND median
  throughput >= 0.5 x dense on W1 and W4a. If only the memory half holds, B is kept as an opt-in for memory-bound batches and the
  throughput cost is reported as its price.
- A3. Packed inactive storage (C) is *worth keeping over B* only if, at some cache bound, on W3 peak RSS(C) <= 0.75 x peak
  RSS(B) AND throughput(C) >= 0.3 x throughput(B). Otherwise packing is retained as code and tests but documented as not
  recommended, and the negative result is reported.
- A4. Cache sensitivity is reported, not gated; the recommendation names a minimum cache for each workload class.
- A5. Block compression (D) is attempted only if both hold: the packed inactive payload is >= 40% of C's peak RSS on some
  workload, and an offline per-tile compression of the real canonical packed payloads (deflate and xz as proxies that bound what
  LZ4-class codecs can achieve, each tile compressed independently with a 4-byte header and a raw fallback) shrinks the total
  payload by >= 1.3x. Otherwise D is not built.
- Failure of the main prediction: if B's RSS on W1/W2/W4 is > 0.5 x dense, or any exactness gate fails, the design is rejected as
  a memory tool.

Competing explanation for any slowdown: tile-transition overhead (hash lookup, `settle`) versus codec cost versus cache misses.
`R` (raw inactive, same cache) and the unlimited-cache `B` separate them.

## Pruning-index preflight

- Index revision and search commands: `git rev-parse HEAD` = `2ee0086e075eb2b1fca04781870dff37aaaea48b`;
  `git ls-files notes/pruning-index/entries`; `git grep -n -i -l -e tiled -e storage -e memory -e backend -e grid -- notes/pruning-index/entries`.
- Candidate signature IDs: none matched. The sole entry, `NR-20261022-additive-laws-order-blind`, concerns additive conservation
  laws of rules of length 2..8; its membership predicate, objective and observable (law group of a rule) are unrelated to
  storage-backend performance.
- Scope comparison: this experiment varies the data structure under a fixed deterministic ant; it makes no claim about any rule
  family's dynamics and asks no scientific question the index could prune. The census rules are workloads, not subjects.
- Decision: run. No dead-end signature is warranted by a performance result.
- Run spec and exclusions: [scripts/workloads.tsv](scripts/workloads.tsv); nothing excluded.
- Compute/stopping budget: about 600 single-thread runs of at most a few seconds each (W4b at most about 1 minute for the dense
  baseline, which writes 4 GiB), plus the offline compression estimate. No further run is justified by this experiment's result
  unless a criterion above says so.

## Reproduction

See [scripts/](scripts/): `build_bench.sh` (fresh `CARGO_TARGET_DIR`, build from `git archive` of the stated commit, binary
sha256), `bench.sh` (interleaved repetitions, writes `results/*.json` and a CSV-identity check), `summarise.py` (uv, stdlib only),
`compress_estimate.py` (criterion A5). The exact commands, toolchain, CPU, load, binary hashes and benchmark commit are recorded
in [results/provenance.txt](results/provenance.txt) (written by `bench.sh`) and in `NOTEBOOK.md`.

## Results, uncertainty and limitations

Filled in after the runs (below the line; the registration above is not edited).

---

## Addendum 1 (registered 2026-10-23 19:25 +13:00, before any stage-D timing): block compression

Stage-1/2 results exist (below); they fired criterion A5 (see "Results"): on W3 the packed inactive payload is about 69% of C's
RSS and per-tile deflate shrinks the real payload 64x (xz 74x). Stage D was therefore built: `TURMITE_INACTIVE=lz4`
(`Inactive::Compressed`): the canonical packed (or raw) payload is LZ4-block-compressed (`lz4_flex` 0.14, pure safe Rust, no
transitive dependencies, `default-features = false`) on eviction only, kept when smaller, and expanded on a miss; checkpoints
stay in the canonical form. Configs L64, L1024, L4096 (cache sizes, tile 2^6) on W1 and W3, plus A, B6, C1024 re-run as references
in the same interleaved batch (5 repetitions, results/runs_d).

Predictions: (D1) W3, L1024: peak RSS 14-28 MiB (resident 4.4 MiB + compressed payload 1-8 MiB + 8 MiB process baseline), i.e.
<= 0.6 x C1024's. (D2) W3, L1024 throughput 0.3-0.6 x B6 and >= 0.8 x C1024's (LZ4 expansion is cheap next to the 14 us bit-unpack, but a
compress is added per eviction). (D3) W3, L64: < 0.05 x B6 (thrash). (D4) W1, L1024 (no evictions): equal to B6 within 5%.
(D5) Compressed bytes on W3 at the end: LZ4 will reach less than the deflate figure; I expect 15-60x vs packed, not 64x.
Criterion A6 (adoption of D over C): on W3, RSS(L, some cache) <= 0.6 x RSS(C, same cache) AND throughput >= 0.8 x C's at that cache.
If A6 fails, D stays as an opt-in with its measured trade-off reported.

## Results (2026-10-23, written after the runs)

Setup: bench binaries from `git archive` of `e93d4c7c18a428e07f2a7f1621ca27798fd1f0d2` (stages A-C; sha256 in
`results/runs_provenance.txt`) and `b53bcb69d15c24908805ea374e2e05118bdfe648` (adds stage D; `results/runs_d_provenance.txt`),
each in a fresh `CARGO_TARGET_DIR` under `/home/tim/bench-<commit>`; Rust 1.98.1; WSL2 on an Intel Xeon W-2125 (6 of 8 logical
CPUs, 47 GiB); `RAYON_NUM_THREADS=1`; 5 repetitions interleaved (3 for W4b). The machine is shared with another contributor's
sessions: load average at the start was 0.7 (main batch) and 3.3 (stage-D batch); each run's load is in `runs*/*.load`.
**Dense throughput varies by up to about 20% between batches** (W3 dense: 1.10-1.32e8 steps/s in the main batch, 0.87-1.01e8 in the
stage-D batch), so a ratio against dense within about 1.2x of 1 is not distinguishable from noise; ratios among tiled
configurations of the same batch are tighter. Per-config tables: `results/summary.csv`, `results/summary_runs_d.csv`; raw per-run
JSON: `results/runs*/`; codec: `results/codec_bench.tsv`; A5 estimate: `results/compress_estimate.json`.

**Exactness (A1): met.** All 149 + 55 benchmark runs gave CSV bytes identical to dense (`results/runs*/identity.tsv`); the earlier
57-rule x 9-setting x 2-thread-count batch and the full `cargo test --release --locked` also pass (NOTEBOOK.md). The first
benchmark pass reported 121 "differences": a bug in `bench.sh` (it deleted the dense reference file before comparing); fixed in
`8d89328` and the whole batch re-run. The discarded pass is recorded in the notebook.

Peak RSS (MiB) and throughput (millions of steps/s), medians:

| workload | A dense | B6 sparse | C1024 packed | L1024 lz4 | C64 packed | L64 lz4 |
|---|---|---|---|---|---|---|
| W1 RLR, 8192, 1e8 steps | 70.1 MiB, 217 | 8.8 MiB (0.13x), 254 | 8.9, 262 | 8.9, 283* | 8.4, 159 | 8.9, 186* |
| W2 RRRRRRRLLRRR | 70.0, 247 | 7.9 (0.11x), 136 (0.55x) | - | - | 8.0, 135 | - |
| W3 RLLRLLLRRRLL | 70.0, 131 | 61.3 (0.88x), 207 | 41.1 (0.59x), 128 | **13.4 (0.19x)**, 134* | 39.4, 4.6 | 10.7, 4.8* |
| W4a RL, escapes at 222061 | 82.3, 2.2 | 7.9 (0.10x), 24.7 | - | - | 7.7, 13.9 | - |
| W4b RL, board 65536, 2e7 | **4227**, 0.29 | **12.3 (0.003x)**, 53.5 | - | - | 9.3, 24.5 | - |

(*stage-D batch; its own dense and B6 references: W1 242 / 282, W3 93 / 211.) The empty-process baseline is 7.8 MiB and the
run's own trail arrays are inside every figure. W4a's dense figure is dominated by writing a 64 MiB grid and the dense onset replay
for a 222k-step run, so its apparent 11x says nothing about the stepping loop.

**Findings.**

1. *Sparse tiles (B) cut memory where the footprint is small and cost little time.* RSS is 0.10-0.13x dense on W1, W2, W4a and
   0.003x on W4b (12 MiB against 4.2 GiB). On W3, whose footprint covers 7067^2 of an 8192 board, B saves 12%. Throughput on W1 and
   W3 is higher than dense (the working set sits in 66-byte rows instead of 8194-byte rows), but see the noise caveat; the one clear
   slowdown is W2 (0.55x), a 17x18 pattern sitting on a tile corner with 0.128 transitions per step.
2. *Packing alone (C) is worth little for irregular patterns and a modest win on a large footprint only with a big cache:* C1024 on W3
   has 0.67x of B's RSS at 0.60x of B's throughput; C64 (cache 64 of 12,544 tiles) thrashes (0.022x of B: 768k misses in 1e8 steps;
   `codec_bench.tsv` measures 10-13 us to encode and 14-15 us to decode a 4096-cell tile).
3. *LZ4 on top of packing (D) is what moves memory on structured patterns:* W3 L1024 RSS 13.4 MiB = 0.19x dense, 0.22x of B, 0.32x of
   C1024, at 1.06x C1024's throughput. The 11,520 evicted tiles occupy 295 KB compressed against 28.1 MiB packed (about 25 bytes per
   tile: a highly regular structure; far better than deflate's 64x per tile on the same payload). On W1 (chaotic) per-tile deflate
   shrinks the payload only 1.9x (xz 1.7x), and W1's whole footprint is 0.9 MiB anyway. The W3 figure is a property of that
   pattern, not of "typical" rules.
4. *Cache cliffs are steep.* A miss costs O(T^2); W3 with cache 64 spends its time in 768k misses. W5 (tile 4 or 8, cache 2, 0.13
   transitions per step, 9 million evictions) runs at 0.155x (tile 4) and 0.075x (tile 8) of dense.
5. *The dense baseline pays the board always:* 70 MiB at 8192 and 4.2 GiB at 65536 whatever the ant does.

**Predictions against outcomes** (as registered above).
P1 held (68-80 MiB; 4227 MiB on 65536; W4a 82 MiB, 2 MiB above the range because the dense onset replay allocates a second grid).
P2 held at its edge (7.8 against 2-8). P3 held (8.8 <= 12, 7.9 <= 8, 7.9 <= 10, 12.3 <= 20; W3 61 MiB = 0.88x, inside 55-70).
P4 held (39.4 MiB, 0.64x of B). **P5 failed in direction for B**: predicted 0.6-0.95x dense on W1 and W3, got 1.17x and 1.6-2.3x
(a cache-locality effect I did not foresee, partly noise); the W2 prediction held (0.55x); C1024 on W1 >= 0.95x B held (0.997);
C64 on W3 < 0.3x B held (0.022). P6 held (encode 10-13 us, decode 14-15 us). P7: transitions per step held (0.133), throughput
0.155x narrowly missed "< 0.15x". Stage D: D1 RSS 13.4 MiB is below the registered 14-28 MiB (better, but outside); D2 0.63x of B6
(registered 0.3-0.6, narrowly above) and 1.06x C1024 (>= 0.8x held); D3 held (0.023); D4 held (1.003); **D5 failed**: about 100x
compression, not 15-60x.

**Adoption criteria.** A1 met. A2 met (RSS <= 0.25x dense on W1, W2, W4a, W4b; throughput >= 0.5x dense on W1 and W4a). A3 met
only with a cache that holds a good fraction of the footprint: C1024 on W3 is 0.67x of B's RSS (<= 0.75) at 0.60x of its throughput
(>= 0.3); C4096 is 0.76x (fails the RSS bar); C64 fails. A5 fired (inactive payload 69% of C1024's RSS on W3; per-tile deflate 64x on
W3, 1.9x on W1, 28x on W2), so D was built. A6 met on W3 (L1024: 0.32x C1024's RSS at 1.06x its throughput; L4096: 0.57x at 1.01x).

**Recommendations** (limits in DESIGN.md).
- `TURMITE_GRID=tiled` with the default 2^6 tile and an unlimited cache when the footprint is much smaller than the board or the
  board is huge (>= 32768): exact, 0-45% throughput cost on compact patterns here, 12 MiB where dense needs 4 GiB.
- A bounded cache with `lz4` only when the footprint is large (thousands of tiles) *and* structured, with a cache of at least
  ~8% of the tile footprint (1024 tiles for 12,544 here). A cache of a few dozen tiles on a large footprint is 20-40x slower than
  unlimited. Never combine a tile much larger than the structure with a tiny cache.
- Keep dense for boards up to ~8192 whose footprint fills much of the board, or when the fastest single run matters. The default
  stays dense.

**Limits of this evidence.** One machine, one build, WSL2, a shared environment, single-thread runs (with several workers the dense
cost multiplies by the worker count, which widens the gap but was not measured); five census workloads; the structured-pattern
compression result rests on a single rule (W3); boards of 8192 and 65536 only. Peak RSS is `VmHWM`; logical bytes
(`peak_total_mib`) match it only after adding the ~8 MiB process baseline and the trail arrays.

**Probe (not integrated).** Judged a separate refactor once the stepping backend was complete. `probe_walker` keeps a colour array and
an unvisited-neighbour-count array (2 bytes per cell) and `Region::visit` writes four neighbours per new cell. Measured peak RSS of
`probe 22 <grid>` on RLR: 19.7 MiB at grid 4096 and 68.9 MiB at 8192 (zero-initialised arrays commit pages only where the ant has
been, so this is not the 2 x size^2 bound). The count array is visited-status plus a 0-4 counter, so colour packing does not apply
to it. Follow-up: tiled `unv` plane in the same tiles, neighbour updates pinned to the five tiles around the cell, exact comparison
with `probe`'s CSV.

## Pruning-index outcome and next question

No signature: a performance result is not a dead end. Open engineering questions: a tile-grid offset so the start cell sits in a tile
centre (W2's 0.55x is probably a corner artefact; untested); the tiled probe; whether very long runs on boards of 2^16 and more
behave as W4b suggests (not run: that would be a new sweep).

## Addendum 2 (2026-10-23 20:25 +13:00, commit cc5b228): code review findings; known memory problem

A review of `src/tiled.rs` and this experiment found no correctness bug (21 tests pass; a differential fuzz against dense `lean` of
720 cases, 6 seeds, 0 failures, covering 1-99 colours, tile 2^2..2^12, chained checkpoint resumes, budgets at the escape step and the
onset replay; the fuzzer was temporary and is not committed). It did find the following. **Nothing below is fixed yet.**

**Known problem: a reused `TiledGrid` never gives memory back.** `TiledGrid::begin` keeps every resident-tile buffer (and the
directory's hash-table capacity) from earlier rules "for reuse". After one big-footprint rule a worker stays at that high-water mark.
Measured once (unlimited cache, tile 2^6, board 8192, 1 thread): `RLR` 2.5 MiB RSS; then `RLLRLLLRRRLL` (W3) 61.2 MiB RSS and 53 MiB
logical; then `RLR` three more times: still 61.2 MiB RSS and 53 MiB logical for a ~1 MiB footprint. Consequences:
- The benchmarks above ran one rule per process, so they never exercised this. The "12 MiB vs 4 GiB" and "0.10-0.13x dense" figures hold
  for a single run, **not for a sweep of many rules**: there each rayon worker's memory is the largest footprint of any rule it has run,
  so sustained RSS tends towards threads x (largest footprint) once a few big rules have passed through.
- Until fixed, treat the sparse backend's saving on a mixed sweep as unmeasured, and do not quote the single-run numbers for one.
- Intended fix (not applied): cap retained buffers at a byte budget (about 8 MiB, never fewer than 2) and drop an oversized directory in
  `begin`, with a test that a reused grid shrinks, and re-measure a mixed batch.

**Other findings**
- Eviction picks the victim by a linear scan over every cache buffer per miss. Harmless at cache 1024-4096 (microseconds, against
  10-15 us of codec), but it grows with the cache and would dominate at tens of thousands of tiles. An O(1) recency list gives the
  identical eviction order (check: identical `TileStats`). Not applied.
- On W3, every C1024, C4096, L1024 and L4096 run has `misses = 0` (`results/summary*.csv`): the ant never re-enters an evicted tile,
  so the timed region contains no decoding. The "L1024 = 1.06x C1024 throughput" result measures encode cost only; decode is only
  exercised by the thrashing L64/C64 runs (L64 about 1.04x C64).
- Two reported ratios: C1024 on W3 vs B6 is 0.62x (0.618), not 0.60x; the "0.997" for C1024 on W1 is from the stage-D batch (the main
  batch gives 1.034).
- The cache-locality explanation of tiled beating dense (66-byte vs 8194-byte rows) is a hypothesis, not a result (as the notebook says).
- `bytes_decoded` counts the stored (compressed) size for LZ4 tiles while `bytes_encoded` counts the canonical size, so they are not
  comparable in `lz4` mode.

## Addendum 3 (2026-10-23 20:30 +13:00, base commit 8cb574b): the two Addendum 2 performance/memory problems fixed

Both fixes are in `src/tiled.rs`; no registered prediction was involved (engineering fixes, not a measurement).
- **Retained memory.** `begin` now keeps at most 8 MiB of idle tile buffers (never fewer than 2) and drops a directory whose
  capacity exceeds 8 MiB, instead of keeping the high-water mark. New test `reused_grid_releases_buffers_beyond_the_retain_budget`.
  **Not re-measured:** the mixed-batch RSS figures from Addendum 2 have not been redone, so the sparse backend's saving on a
  multi-rule sweep remains unmeasured; only the mechanism is fixed. Small-tile configs with a footprint under 8 MiB still retain it.
- **Eviction.** The per-miss linear scan is replaced by an intrusive recency list (O(1) touch and victim). The order is identical
  (oldest entry wins; entries had unique ticks). Evidence: all 22 tests pass in `--release` (cargo test --release --locked --test tiled),
  including the lean/reference equality tests with small caches that force thrashing. A direct `TileStats` comparison before/after
  was not run, and no speed re-benchmark was done.
