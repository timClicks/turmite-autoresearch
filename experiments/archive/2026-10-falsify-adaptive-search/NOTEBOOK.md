# Lab notebook: adaptive search for the falsification harness

Append-only. Tags: intent, assumption, observation, interpretation, surprise, decision, dead-end, question, deviation.

### 2026-10-22 22:30 (+13:00) · 253adab · intent
Make the adaptive attacker beat random sampling (user request), as a paired, equal-budget, replicated comparison rather than
one chain vs one sample.

### 2026-10-22 22:32 (+13:00) · 253adab · observation
From `experiments/active/2026-10-falsification-harness/results/C*.csv`: delay is heavy-tailed; the tails come from sparse/obstacle
(RL) and mono/patch (RRRL), not from dense patches. Details in README "Diagnosis".

### 2026-10-22 22:34 (+13:00) · 253adab · decision
New code goes in its own binary (`src/bin/falsify_search.rs`) using only the public `turmite::falsify` API, because another
contributor has uncommitted edits in `src/falsify.rs` and `src/lib.rs`; it can be promoted into the library once those land.
Predictions E1-E4 registered in README before the binary exists.

### 2026-10-22 22:50 (+13:00) · b0c9e8a · observation
Round 1 (`results/`): evolve beats random in C1 (p 2.7e-8) and C2 (p 1.3e-3); old loses to random in C1 and C2; C3 saturates at the
counterexample score and evolve finds a different highway in 22/30 replicates vs random 30/30. E1, E2, E4 failed; E3 held.

### 2026-10-22 22:52 (+13:00) · b0c9e8a · surprise
Evolve is *worse* than uniform random at finding the C3 counterexample. Delay ranking and counterexample search are different
objectives. Registered E5-E7 (immigration variant) before implementing it.

### 2026-10-22 23:05 (+13:00) · 21e025f · observation
Round 2: E5 (27/30), E6 (p 4.2e-5), E7 (p 2.1e-3) held; first three arms reproduced round 1 exactly. Random still finds the C3
counterexample in 30/30 replicates; no adaptive arm matched it.

### 2026-10-22 23:06 (+13:00) · 21e025f · interpretation
The search now beats sampling for long transients, not for counterexamples. Reporting both. Caveat: E5 passed on the threshold.

### 2026-10-22 23:42 (+13:00) · 047e395 · observation
Clean worktree run reproduces round 2 byte for byte for all four arms through the library implementation. Provenance caveat closed.
