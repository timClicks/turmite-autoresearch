# Lab notebook: highway preconditions (causal seeds)

Append-only. Newest entry last. Never edit an old entry; correct it with a new one
(`corrects: <timestamp>`). Tags: intent, assumption, observation, interpretation,
surprise, decision, dead-end, question, deviation. See `experiments/README.md`.

### 2026-10-21 20:05 (+13:00) · 3fcfce8 · intent
Tim suggested analysing the grid state together with the rule, to find shared preconditions of highway onset across
rules. Plan: define the dependency set D(tau) (nonzero cells at tau that the future reads), take its minimum near onset
as the causal seed, encode seeds by turn words (rule-independent) and compare across all 583 census highways with onset
<= 1e9. Registered P1-P5 and controls C1-C4 in README before writing code.

### 2026-10-21 20:05 (+13:00) · 3fcfce8 · assumption
After a highway leaves the old territory it never reads an old cell again. Checked per event by C2: the transplant must
match the original for 200 periods beyond the read window. Status: untested.

### 2026-10-21 20:45 (+13:00) · 4db511a · observation
C1 passed: `cargo test --release --test seed` (5 tests, 64 proptest cases each). Pilot on RL, RRL, RRRRLR
(scratch/pilot): transplants all exact; onsets recomputed equal census. RL curve: |D| rises 0 -> ~320 by 50 periods
before onset, falls to 11-22 (the highway's own self-overlap) at onset. RRRRLR: chaos level 384286 vs |D(tau*)| = 25.

### 2026-10-21 20:50 (+13:00) · 4db511a · deviation
Window included tau = 0 (blank board, |D| = 0) for early onsets. Fixed lower bound; added pre-onset seed columns.
Written into README as Deviation 1 before any full run.

### 2026-10-21 20:50 (+13:00) · 4db511a · surprise
I expected the bottleneck before onset with a few extra cells (P2 alternative). In RRRRLR it is after onset and equals
the highway's own floor: the highway starts from almost nothing but itself. One rule; wait for the census.
