# Prefix causal horizon: what a rule's later letters cannot yet have done

Registered 2026-10-25, base `a25ab35`, branch `ccr-9a56d193-javkym`. Status: **REGISTERED; nothing run.**
Prompted by the user's remark that the prefix analysis may be amenable to formal methods, and by the Q19 work
(`experiments/proposed/2026-10-late-highway-fourth-decade/`), where 680 of 702 survivors extend another survivor and
prefix-sharing highway rules had identical onsets.

## Question

Several notes treat "rules sharing a prefix" as if they shared dynamics for a while (identical late-highway onsets, the kappa prefix
lookups). Is there an exact statement of *how long*, can it be proved for all rules rather than tested on samples, and does it say
anything about the data we have?

## Statements (to be proved, and tested against the oracle)

Rules `w` (length `n`) and `w'` (length `n'`), blank board, start at the origin, one step = read colour `c`, turn by `rule[c]`,
write `(c+1) mod n`, move. Steps are numbered from 1. `lcp` = length `p` of the longest common prefix. `F_c(w)` = the number of the
first step that reads colour `c` (a cell's `(c+1)`-th visit, for `c < n`; colour `c` is written on visit `c`).

* **Clock lemma (K).** For `c < n` colour `c` is read for the first time on the first `(c+1)`-th visit to any cell. Hence `F_c` is the
  record time of the maximum per-cell visit count, and is the same number for every rule whose prefix of length `c` is the same
  (it needs only the first `c` letters; see A).
* **Lemma A (diverge exactly at the first read of the first differing colour).** If `p < min(n, n')` then positions agree after steps
  `0 .. F_p - 1` and differ after step `F_p`, where `F_p` is computed in either run (they coincide until then).
* **Lemma B (prefix case).** If `w` is a proper prefix of `w'` (`p = n < n'`): positions agree after steps `0 .. F_n(w') - 1`, and
  differ after step `F_n(w')` iff `w[0] != w'[n]`.
* **Lemma L (lift / periodic extension).** Let `q` = least `c < n'` with `w'[c] != w[c mod n]` (infinity if none), and `W` = first step
  that reads a cell previously written 0 by a wrap of `w'` (a cell visited `n'` times). Then positions agree after steps
  `0 .. min(F_q(w'), W) - 1` (and, when `n | n'`, the wrap term `W` is dropped).
* **Lemma R (roots).** If `n | n'` and `w'` is `w` repeated, the two trajectories are identical forever (already used in `src/rule.rs::root`).

Pen proof for A: by induction on steps, the pair of states is equal (position, heading, every cell) as long as the colour read is `< p`,
because the letters and the successor `c + 1` coincide for `c < p < min(n, n')`; the first read of colour `p` turns by different
letters, and the four headings give four different moves. The induction is over an unbounded grid, which is why the step obligation is
checked by SMT over an array-valued grid rather than over finite boards.

## Registered predictions (before any run)

* **S1.** z3 proves the inductive step (negated goal `unsat`) for: colour-range invariant, A, B-step, L (concrete lengths 1..12, every
  letter pattern symbolic), R. For A with symbolic `n, n', p` too.
* **S2 (instrument calibration, must come out `sat`).** Negative controls: A with the guard widened to `c <= p`; L without the
  turn-agreement premise; L without the wrap flag when `n` does not divide `n'`; R with `n` not dividing `n'`.
* **R1.** Exhaustively for all rule pairs with `n, n' <= 6` (cap 4000 steps, reference ant on both): A holds with equality, B holds,
  L's bound holds, R holds, and the number of pairs not reaching their `F_p` within the cap is reported (not silently dropped).
  A proptest at lengths up to 12 agrees. A failure would be a bug in the statement or in `first_reads`.
* **R2 (scaling).** For the 702 survivors of `experiments/proposed/2026-10-late-highway-fourth-decade/results/survivors_1e11.txt`, `F_c(w)`
  grows like `c^gamma` with gamma in [2.5, 3.5] (a cube root of time for the maximum visit count, as for the mean). 55% confident;
  outside [2, 4] I would call it wrong. Every survivor reads its last colour (`F_{n-1}`) before 1e7 steps: 85%.
* **R3 (consequence for Q19).** Because `F_p` is small (R2), prefix sharing makes rules identical only for the first ~1e4-1e6 steps:
  of the 21 groups of survivors with identical box at 1e11, at most 3 contain a pair that Lemmas A/B/L cannot separate before 1e11.
  So equal boxes are coincidences of boundedness/size, not shared trajectories, and "dedupe by prefix" saves nothing. 75% confident.
* **R4 (filler pairs).** For the 54 late-highway onsets, every pair with identical onsets (within 1e-4 relative) is explained by the
  lemmas: a Lift or prefix pair whose bound exceeds the onset. The pairs with 6+ shared letters that the earlier note counted
  as "prefix" evidence but that are Case A with `F_p` far below the onset would contradict the lemma or the note. 70% confident that none do.

## Pruning-index preflight

Index revision `a25ab35`; `rg -n -i -e prefix -e lcp -e "shared trajectory" notes/pruning-index/entries`: no candidates (the one entry
concerns additive conservation laws). Decision: run. A proof is not a dead-end claim; no signature planned.

## Reproduction (filled in as run)

```bash
uv run --frozen experiments/archive/2026-10-prefix-causal-horizon/scripts/prove_prefix.py        # z3; PEP 723 header, no change to uv.lock
cargo test --release --locked --test prefix_horizon
cargo run --release --example prefix_horizon -- ...
```

## Addendum 2026-10-25 (before R1-R4 or the Rust test were run): the sharper unified form

Working through the Lift proof I noticed that `W` (first read of a wrapped cell, visit `n'+1`) always exceeds `F_c(w')` for every
`c < n'` (a cell cannot have `n'+1` visits before it has `c+1`), and no wrap happens before `F_{n'-1} >= F_q`. So Lemmas A, B and L
collapse into one statement. For `n <= n'` and `q` = least `c < n'` with `w'[c] != w[c mod n]` (infinity if none):

* **(i)** if `q < n'`: the first step after which the positions differ is **exactly** `F_q(w')`;
* **(ii)** if `q = infinity` and `n | n'`: the trajectories are identical forever;
* **(iii)** if `q = infinity` and `n` does not divide `n'`: positions agree at least until `W(w')`, the first step that reads a cell
  visited `n'` times before.

(A is (i) with `q = p`; B is (i) with `q = n` when `w[0] != w'[n]`, otherwise (i) with a later `q` or (iii).) This is the form R1 tests;
the registered lemmas are its special cases, so a failure of either is a failure of the registration. The z3 lift obligation is still
needed for (iii) (the wrap flag), and for (i) up to `F_q`.
**z3 note (first run, before this addendum):** the negative control NC1 returned `unknown` rather than `sat` because the quantified
range premises stop z3 from building a model, so S2 as written is not yet a valid calibration. Controls will be restated with
quantifier-free premises (the grid is the zero grid plus the cell under the ant) and rerun; this is a deviation from S2, not a result.

## Results (appended 2026-10-25; code and evidence commit `5a9da7d`; the registration and addendum above are unchanged)

Provenance: the Rust runs were made from the working tree on top of `1e8d1f6` and the code was committed unchanged as `5a9da7d`
(`results/r4_provenance.txt`, `results/r4_iii_provenance.txt` carry binary hashes). Full `cargo test --release --locked` passes;
`cargo clippy --lib --test prefix_horizon --example prefix_horizon --example prefix_pair_diff -- -D warnings` is clean.

**S1 held.** `scripts/prove_prefix.py` -> `results/prove_prefix.txt`: 75 `unsat` obligations, none `sat`/`unknown`: colour range invariant
(n symbolic); Lemma A step and divergence (n, n', p and every letter symbolic, unbounded grid as an SMT array); Lemma B; the lift step with
wrap flag for **every** pair 1 <= n < n' <= 12 (66 pairs, letters symbolic); Lemma R for n | n' in {(1,3), (2,4), (3,6), (4,12), (5,10)}.
**S2 held after a repair.** `scripts/prove_controls.py` -> `results/prove_controls.txt`: 8/8 (four twins `unsat`, four controls `sat`).
The first NC1 returned `unknown` (quantified premises); the controls were rewritten quantifier-free before any lemma result was used
(logged as a deviation above and in the notebook).
What this does and does not establish: z3 discharges the one-step simulation obligations. The outer induction over steps and the definition of `F_q`
as the first violating step are pen-and-paper (short), not mechanised; no proof assistant was available here (GitHub release downloads, hence
Lean's installer, are blocked by the proxy). Model fidelity (does the SMT step equal the real ant?) rests on R1 below, not on z3.

**R1 held.** `tests/prefix_horizon.rs`: `first_reads` equals the reference ant for all 510 rules of length <= 8; the unified statement
(i)-(iii) holds for all 8,001 unordered pairs with n, n' <= 6 (branch tally 7,761 exact, 152 repeated, 72 + 16 lower-bound; no pair needed more than the 2,500-step cap),
for every prefix extension by up to four letters of rules up to length 8, and for 400 random pairs up to length 12 with forced common prefixes.
Two manual mutants (divergence claimed one step late; wrap bound made strict) fail the test, so it is not vacuous. The strict mutant also exposed a tight
case of (iii): `RL` vs `RLR` first differ exactly at the wrapped read, step 17. The lockstep instrument `first_position_difference` equals the reference for all pairs up to length 5.

**R2 FAILED as registered.** `results/analysis.txt`: the median first-read time of colour c over the 702 survivors is 5, 9, 17, 29, 33, 41, 53, 57, 73 steps for c = 1..9;
the log-log slope is **1.33**, not 2.5-3.5. (My cube-law analogy was wrong: the record of the maximum per-cell visit count is set by the crowded start region
within the first hundred steps, long before the growth law applies.) The second half of R2 holds, trivially: every survivor reads its last colour by step 389 (registered: before 1e7)
and reads a wrapped cell by step 1009; none escapes the board in that time.

**R3 held (trivially).** Of the 702 survivors, 52 rules in 21 groups share their bounding box at 1e11 (42 pairs): all 42 pairs are class (i) and separate by step 45. Registered: at most 3 groups
with a pair the lemma cannot separate; observed 0. Shared prefix saves nothing in the census, and the equal boxes are not shared trajectories.
Exploratory: 19 of the 42 pairs are cyclic rotations of each other, 2 are rotations of a mirror image, 11 differ in length and 10 are unrelated; every such box is small (30-118 cells after 1e11 steps).
A cyclic rotation of a rule from a blank board is the original rule on a uniform non-zero background, so this may be background-independence of small bounded attractors. Untested; see Q25.

**R4 FAILED as registered, and what failed is an earlier interpretation, not the lemma.** The 51 late-highway pairs with equal onset (< 1e-4 relative; onsets 4.29e9-1.29e10) are the pairs among
exactly the 25 board fillers of `late-highway-board-check` (the 25 equal-onset rules are that set); none of the 28 genuine late highways shares an onset with another. For 46 pairs (class i) the lemma
gives positions that differ at step F_q <= 105. For the 5 class (iii) pairs the lemma gives only a lower bound, so the first difference was measured by lockstep run (`results/r4_iii_pair_diff.csv`):
97, 113, 145, 173, 205 steps. So **all 51 pairs separate within 205 steps**, seven orders of magnitude before their identical onsets. Equal onsets there reflect a common fill rate of the board
(onset = 2(k+1) G^2, k the number of leading R's), as the board check found; they are not evidence of shared trajectories.
Registered prediction (70% that no pair would contradict the notes' reading) was wrong on that reading.

### Interpretation (not tested beyond the above)

1. The prefix lemma is exact and cheap, but its reach is tiny: any two rules separate by the first read of the first differing colour, which for all 702 survivors, all 25 fillers and every tested pair happens
   within ~10^3 steps. Letters are never "unused until late" for length <= 10 rules. Two sentences in the notes rest on the opposite: `notes/frontier-2026-10-13-results.md` (B5 extension: "rules sharing a prefix have identical onsets when the extra letters are unused at that time")
   and `notes/frontier-results.md` ("related rules sharing one trajectory until a late colour is reached"). Both are refuted as stated; the second was already superseded in effect by the board check. Appended corrections, not edits, in `notes/open-questions-hypotheses.md`.
2. A causal-horizon explanation of the kappa prefix effects cannot work: every letter of every survivor has influenced the trajectory by step ~1000, while kappa is measured over windows ending at 2^22 and beyond. Whatever makes
   the first letters predictive (family membership, per `kappa-prefix-family-holdout`) is not "later letters have not acted yet". Caveat: this says nothing about *how much* a late letter matters, only that it has acted; and only for length <= 10 survivors.
3. Where formal methods could go further (not done): mechanise the induction in a proof assistant; or prove an upper bound on `F_c` for all rules (here `F_c` is only observed: max 389 over 702 survivors, no proof it is bounded for every rule);
   or look for a non-additive invariant (Q21) with the same SMT-on-arrays technique, since a simulation relation between two runs is exactly the kind of statement it can discharge.
4. Alternatives not excluded: the lemma concerns positions. Two rules can agree on every position for longer than F_q only through (ii) or (iii), and (iii) is a lower bound (measured: five pairs, all short).

### Pruning-index outcome

No signature. The negative observation "prefix sharing saves nothing" is empirical (702 survivors and 25 fillers), not a proof that `F_c` is bounded for every rule, and the index forbids family-wide exclusion on finite observations.
