# Chunked plan (2026-10-20)

Each chunk is one commit (stage files by explicit path; never include
`2026-10-highways-unresolved-rules-1e10-1e11/results/h1e11/` chunk files).
A chunk is done only when its gate passes. Failures are recorded, not
worked around; thresholds in README are not loosened after seeing data.
HANDOFF step numbers in brackets.

| # | Chunk | Gate (done when) | Output |
|---|---|---|---|
| 0 | Correct the record | NOTEBOOK `correction` entry: the 21:26 prototype's geometry flag can never be true, non-adjacent milestone jumps are dropped, full BFS per step is quadratic; the B+I=S test holds by construction | NOTEBOOK.md |
| 1 | Depth monotonicity check | BFS oracle shows depths never decrease on insertion (random trajectories, hole fills); written skipped-milestone policy in README | test + README |
| 2 | Fast depth field `src/first_passage.rs` [3] | proptest vs BFS oracle after every step, depth clamped at 65; fixtures from HANDOFF 4 (empty, one cell, no return, hole fill, band edges) | src + tests |
| 3 | Milestone accountant, layered on `field_age`/`fixed_area` [4] | per-band B, I, area, P, sum_pa byte-equal to `fixed_area::run`; segment + fragment times sum to band time; frozen-depth variant | src + tests |
| 4 | Synthetic calibration [5] | planted semi-Markov, absorbing interval walk, heavy tails + cap, hidden-state chain where the memoryless closure must visibly fail; rotor/rw bookkeeping only | calibration.json |
| 5 | Checkpoint, resume, threads [8] | mid-trajectory resume and 1-vs-N thread outputs byte-identical | readiness.json |
| 6 | Sampler binary and manifest | `examples/kappa_first_passage_sampler.rs`, SCHEMA outputs, atomic writes, `.done` markers | example |
| 7 | Pilot freeze + feasibility [6] | seeded shuffle, census hash, 8 rules x 4 starts frozen before reading outcomes; fresh `CARGO_TARGET_DIR`, binary sha256; runtime/memory measured; machine idle checked | results/pilot* |
| 8 | Confirmation freeze [7] | dated README section before any outcome-role run: cohort algorithm and list, strata, folds, M2 encoding with backoff to M1 and count floor, stopping/cap schedule, synthetic power study, seed grep clean | README |
| 9 | Confirmation run [8] | 48 rules x 16 seeds, background with logs and `.done`; readiness gates reported with full denominators | results/ |
| 10 | Analysis [9] | P1-P4 each get pass, fail, uninformative or untested, bootstrap seed 202610207099, baselines | analysis.json |
| 11 | Write-up | notebook.ipynb from committed results, `notes/kappa-mechanisms` ledger, blog post, `blog/index.html` | docs |

"Complete" means every prediction has a verdict; untested and uninformative
are acceptable. Chunks 0-3 need no simulation budget; 7 onward need an idle
machine (an unrelated `sweep_lean` 1e11 job is currently running).
