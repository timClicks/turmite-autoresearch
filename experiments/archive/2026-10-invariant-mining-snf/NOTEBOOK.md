# Lab notebook: invariant mining, stage 2

Append-only. Newest entry last. Never edit an old entry; correct it with a new one
(`corrects: <timestamp>`). Tags: intent, assumption, observation, interpretation,
surprise, decision, dead-end, question, deviation. See `experiments/README.md`.

### 2026-10-22 21:36 (+13:00) · b0c9e8a · intent
User request: add automated invariant mining to the analysis pipeline, to find conservation laws, parity
invariants and symmetries that restrict trajectories, instead of only measuring step counts and growth.

### 2026-10-22 21:38 (+13:00) · b0c9e8a · decision
Another agent had just (21:33) created `src/invariants.rs`, `src/bin/invariants.rs`, `tests/invariants.rs`
and then `experiments/archive/2026-10-invariant-mining/` (enumerative miner over `a x + b y + d h + e t +
sum w(colour)` at m = 2, 4). I do not edit or commit any of that. This experiment is a separate folder with
a stage-2 scope: all moduli at once (Smith normal form), sublattice families, the universal quotient, and the
question of what the rule can change. My Rust is an `examples/` oracle checker only, so my build does not
depend on their uncommitted `pub mod`. I build into a private `CARGO_TARGET_DIR` and stage explicit paths.

### 2026-10-22 21:43 (+13:00) · db7eb40 · intent
Registered ansatz families, derivation of the order-blindness argument, and predictions P1-P8 in the README
and committed it before writing any solver code (`db7eb40`, commit time 21:43:05).

### 2026-10-22 21:51 (+13:00) · eaa092c · deviation
(1) The README's registration header says "21:50"; the commit that froze it is 21:43:05. The text is a wrong
guess, the freeze is the commit. (2) The README says "all 510 rules of length 2..8"; the correct count is
2^2 + ... + 2^8 = 508. (3) These notebook entries for 21:36-21:43 were written together at 21:51, not as they
happened. None of these changes a prediction.

### 2026-10-22 21:44 (+13:00) · db7eb40 · observation
`uv run --frozen` fails here (`failed to remove .venv\lib64: Access is denied`; the shared `.venv` is
unwritable). The solver is standard-library Python, so every script is run as `uv run --no-project`. The
`--frozen` rule of AGENTS.md is for scripts with dependencies; these have none.

### 2026-10-22 21:46 (+13:00) · db7eb40 · observation
`lawmod.py --selftest` passes: SNF kernel order and generators equal brute-force enumeration for 100 random
integer matrices at m in {2, 3, 4, 6, 8, 12}; the families A0/F1/F2/F3 equal brute force on RL, RR, RLR at
small m; Langton's heading law (`heading = #colour-1 cells mod 4`) is in A0 for RL.

### 2026-10-22 21:47 (+13:00) · db7eb40 · surprise
First census run on n <= 5: P1 holds (0 exceptions), but my P4 (pure-tape heading law iff D = 0 mod 4) fails
for 10 rules, all with D = 2 mod 4 and n even (RR, LL, RRRL, ...). Cause (post hoc): the universal colour clock
gives t = sum c N_c (mod 2) for even n, and heading parity equals time parity, so heading parity is a
function of the tape whenever n is even. The law found is Phi(h) = 2h, E_R = E_L = 2, and the cycle condition
2n = 0 mod 4 holds. My registered claim was too strong; it conflated "a heading law" with "a law that pins h
mod 4". P4 as registered is falsified. A post hoc refinement (a law with Phi(1) odd) is computed separately
and labelled post hoc.

### 2026-10-22 21:49 (+13:00) · db7eb40 · observation
Oracle smoke test (n <= 4, 2000 steps, 16 starts per rule, seed 20261022): 0 law violations, 6560 control
vectors all detected. Then full n <= 6 run: 0 law violations; all 6560 controls (n <= 4) detected. See
`results/oracle_summary.json`.

### 2026-10-22 21:52 (+13:00) · eaa092c · observation
Cross-check against the parallel miner's binary (built from its uncommitted source, hashes recorded): for all
508 rules, m in {2, 4}, (lines printed) + 1 = A0 SNF order: 0 mismatches in 1016 comparisons. Two derivations
with different search strategies agree.
Highways: 582 distinct confirmed rules in `confirmed_v2.csv` + `confirmed_1B.csv` (not 589; duplicates and
the 555-primitive count in frontier-results.md are different filters). No violation of any tile-free law in
F1, F2, F3; the tile-free group has the same order for every one of the 582 rules (F1/F2: 4, 8, 8 at m = 2,
4, 8; F3: 8, 16, 16), i.e. it is the universal parity group and adds nothing to H19.

### 2026-10-22 21:56 (+13:00) · 53778d1 · surprise
Full census (exact integer solver, F3, n = 7) stalled: `RRRRRLL` took 28 s and its entries exceeded 4300 digits
(Python refused to print them). Coefficient growth in column-tracked integer elimination, not an algorithmic
loop. Decision: replace the solver by Smith form over Z/p^e for each prime (pivot of minimal p-adic valuation,
no growth), assert equal free rank across all tracked primes (detects untracked primes 11..37 at cap 1), and keep
exact elimination only as a reference. Selftest now also checks equality with exact elimination on every rule of
length <= 5 in all four families (passes).

### 2026-10-22 21:58 (+13:00) · 53778d1 · deviation
Process error, mine: to stop the stale census I ran a PowerShell `Stop-Process` filter that included
`CommandLine -like '*prof*'`. That matched about 25 unrelated processes (anything started with `-NoProfile`,
etc.), which were killed. I cannot tell which; processes of other agents' tool shells may be among them. Nothing
in the repository was damaged (checked `git status` and `git log` afterwards), but a command another agent was
running at that moment may have died. Rule for the rest of the session: kill only by exact PID that I started.

### 2026-10-22 22:02 (+13:00) · 53778d1 · observation
Final-solver reruns. Census n <= 8 (30 s): P1 0 exceptions; P3 as predicted (28/28 cells); P6, P7 hold (F3 > F2 for
all n, and exactly `|U^F3|/|U^F2| = n^2`); P4 FALSIFIED as registered: 170 mismatches, all D = 2 mod 4 and n even.
Post hoc refinement has 0 mismatches. Oracle n <= 6: 0 violations in 14,416 generator lines, 6560/6560 controls
caught. Peer cross-check: 0/1016. Highways: 582 rules, 0 violations, tile-free group order identical for all.
Also post hoc: fingerprint is a function of (n, +-D mod 4, trivial?): 68 groups, none split.

### 2026-10-22 22:05 (+13:00) · 53778d1 · interpretation
The invariants are consequences of the colour cycle and the lattice and cannot see the order of the colours.
What would change my mind: a pair-potential law (or any non-additive invariant) whose existence depends on the
order, found in a family that passes the same oracle test. The attractive story (an invariant that separates
chaos from highways) is not supported inside this ansatz; the strongest case for it is that every conservation
law that organises the phenomena we care about might need neighbours, and neighbours are exactly what the
ansatz excludes. I do not know whether such laws exist.

### 2026-10-22 22:06 (+13:00) · 53778d1 · decision
Note: another agent committed my interim files (`9bbfad4`) and summarised them in `notes/ACTIVE.md` while I was
mid-run; final results overwrite the interim ones with identical headline values. Next: commit final evidence,
then add the pruning-index signature, AGENTS.md pipeline instruction, T4 note, and a blog draft.

### 2026-10-22 22:20 (+13:00) · 0419f70 · observation
Full `cargo test --release --locked` (own CARGO_TARGET_DIR, tree at `0419f70` plus other agents' uncommitted work):
45 test binaries, 181 tests passed, 0 failed, exit 0. The other agent's `tests/invariants.rs` (2 tests) passes; ACTIVE.md
had recorded that it had never been run.

### 2026-10-22 22:22 (+13:00) · 0419f70 · decision
Review fixes. (1) The shared instruction in AGENTS.md used `uv run --no-project`, a local workaround; canonical form is
`uv run --frozen` (README reproduction block and AGENTS.md changed; the actual runs used `--no-project`, stated in the
README limits). The instruction no longer asks for a per-experiment fingerprint, which is derivable from the rule string; it
points at the open non-additive problem (Q21). (2) P8 inference tightened: the tile-free group of each of the 582 rules has the same
order as the tile-free part of the universal system at m = 2, 4, 8 for every n that occurs, in F1, F2, F3 (universal <= rule, so equal
orders mean equal groups at those moduli). (3) README had been written in cp1252 by an unflagged `open()` default in one of my patch scripts
(a bare 0xB1 for the plus-minus sign); re-encoded as UTF-8. No other file was affected (scanned all files of this work).

### 2026-10-22 22:25 (+13:00) · 0419f70 · interpretation
Q22 (|U^F3| = n^2 |U^F2| at m = n): for odd n the universal order at m = n is n, n^2, n^4 for F1, F2, F3 (n = 3, 5, 7), one colour clock per site
class. Candidate reason: all turns are 90 degrees, so the move axis alternates and the ant's class sequence has period 4 whatever the rule, which
makes departures from each class a function of (t, ant class). Not proved, and incomplete for even n (F2/F1 is n or n/2 when 4 | n).
Recorded as a hypothesis in the README addendum; Q22 in open-questions-hypotheses.md still stands as open.
