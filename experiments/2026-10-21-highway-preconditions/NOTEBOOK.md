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

### 2026-10-21 20:15 (+13:00) · efb53a5 · observation
Full scan, 566 rules, 5 min 50 s (run.log). C2/C3 566/566, C4 20/20, dedupe consistent 406/406. P1, P2 (trivially), P3,
P4 held; P5 failed (rho -0.063). `results/analysis.txt`.

### 2026-10-21 20:20 (+13:00) · efb53a5 · surprise
The pre-onset seed is the highway's own trail plus a median of 3 cells, and the collapse to highway level happens a
median 0.11 periods before onset. I expected at least some events to need old structure. None visibly does.

### 2026-10-21 20:22 (+13:00) · efb53a5 · interpretation
P4 "held" but is a prefix-family artefact: all 8 classes are long-common-prefix families; 0 seeds shared across unrelated
rules (`results/followup.txt`). I will report P4 as held-as-registered and say plainly it does not support shared
preconditions across unrelated rules. Post hoc: onset tracks highway size (h_min rho 0.45, speed -0.54), about 0.018
decades per overlap cell, far flatter than a random colour search (log10 n per cell). Not registered; needs a
registered test before it is cited as a finding.

### 2026-10-21 20:25 (+13:00) · efb53a5 · question
Is the "+3 cells" the trigger? Next: knock out each extra pre-onset cell (relative to the highway trail) and see whether
the launch survives; and scan the 54 late highways to test the size-onset law out of sample (register slope first).
