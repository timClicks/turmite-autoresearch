# Falsification harness (2026-10-22)

## Question
Claims such as "rule R is chaotic" or "rule R forms a stable highway" have so far been checked by running the
blank-board ant for longer, which cannot discriminate a true property from a horizon artefact. Can an automated
loop that *attacks* a registered claim (perturbed starts, asymmetric colourings, obstacles in front of a highway,
off-centre starts on odd boards, an adaptive hill-climb) find counterexamples a longer run would miss, and report
honestly when it cannot?

## What was built
- `src/falsify.rs`, `src/bin/falsify.rs`: seeded runner (`simulate`), ten attack classes, claim parser, verdicts.
- `tests/falsify.rs`: the runner equals `reference::Ant` step for step on arbitrary finite starts and on
  mid-run obstacles; two exact symmetries (heading = rotation; uniform colour-k background = rule rotated by k);
  known-answer claims (RL, RRL, RLL, from the census); Clopper-Pearson against tabulated values; the mid-run
  obstacle and heading tests were mutation-checked (a deliberately wrong direction window and a dropped heading
  are both caught).
- Usage: `falsify CLAIMS.txt OUT_DIR` (refuses a claims file that is not committed unchanged), and
  `falsify --replay OUT_DIR/ID.counterexamples.txt`.

### Design decisions that carry the science
1. **Asymmetry of evidence.** A confirmed highway is a finite witness, so it refutes "no highway" claims (after
   reproduction on a second board geometry and delta-debugging shrinking). A start that has not escaped by the
   horizon refutes nothing about "highway from every start"; it is reported `Unsupported`, never `Falsified`.
2. **Horizon attack.** `horizon` is what the author looked at; trials run to `horizon * 4^ladder` and the report lists
   confirmed highways by `horizon * 4^k`. A refutation whose every counterexample appears after the stated horizon
   is flagged `horizon-sensitive`.
3. **Instrument controls always run.** Four headings of the blank start (rotations of one another) and blank starts
   near an edge of odd-sized boards (same dynamics as the centred start). If either disagrees with the baseline
   the verdict is `Invalid`, because the detector, not the rule, is then at fault.
4. **Valid perturbations only.** Finite non-blank cells in a blank far field (the highway detector assumes the
   ant walks into blank cells). Dense random backgrounds are out of scope.
5. **Highway types compare up to the lattice symmetries**: `(period, |long drift|, |short drift|)`.
6. **Determinism.** Every trial is a function of (claim seed, rule, class, index); the adaptive chains are
   sequential inside a chain and parallel across chains; rows are sorted before writing.

### Limits (stated, not hidden)
- "Survived" means "no counterexample in N attacks at this horizon", with the Clopper-Pearson bound for probabilistic
  claims; it is never a proof.
- Chaotic claims are only refuted by highways. A rule that is "chaotic" at horizon h but bounded/periodic in some
  other way is not tested for that. Growth-exponent claims (the t^(1/3) question) are not covered yet.
- The adaptive objective for chaotic claims (smallest bounding box) is a heuristic, not derived.
- The board must be large enough for the claimed highway to exit within the horizon (drift/period times size/2).

## Registered predictions (written 2026-10-22 21:35 +13:00, before any attack was run)
Setup: `claims.txt`, 64 trials per class, all ten classes, adaptive 4 chains x 40 evaluations.

| # | prediction | confidence |
|---|---|---|
| P1 | No claim ends `Invalid`: heading and boundary controls agree with the baseline on all five rules. | 85% |
| P2 | C1 (RL, highway, type (104;2,2)): no counterexample of another highway type (`hw_other = 0` in every class). Verdict `Unsupported` rather than `Survived`: at least one dense start (half or sparse) is still unresolved at 2e6 steps. | 65% / 60% |
| P3 | C2 (RRL, type (18;1,1)): `Falsified` by at least one patch/mono/sparse start ending in a highway of another type. | 55% |
| P4 | C3 (RRRL, type (52;2,2)): `Falsified` likewise. | 50% |
| P5 | C4 (RLL chaotic, horizon 1e5, attacked to 1.6e6): `Survived`, zero highways in all attack classes. | 75% |
| P6 | C5 (RRLR chaotic, horizon 1e5): `Falsified`, flagged horizon-sensitive. Census onset is 256240, so the blank start itself escapes only after the stated horizon; rung 0 (by 1e5) shows 0 highways, the top rung shows at least 1. | 90% |
| P7 | The adaptive hill-climb finds a longer delay before escape than the best of the 64 random `patch` starts in each of C1-C3 (the adversary beats sampling). Computed by `scripts/adaptive_vs_sampling.sh`. | 60% |

What would count as the harness failing: P1 false (a control disagrees) means the detector has a bug to fix before
any claim is believed; P6 false means the horizon attack does not do what it was built to do.

## Reproduce
```
cargo build --release --locked --bin falsify
target/release/falsify experiments/active/2026-10-falsification-harness/claims.txt experiments/active/2026-10-falsification-harness/results
```
Provenance (command, commit, claims blob hash) is the header of every `results/*.csv`.

## Results
(appended below after the run; predictions above are not edited.)

## Statistical correction (2026-10-22)
The previous pooled Clopper-Pearson interpretation is withdrawn: adaptive candidates are correlated,
and attack classes have different distributions. The harness now omits that interval and reports
probabilistic highway claims as Unsupported. Universal claims still use individual counterexamples.
Shrunk witnesses must reproduce on both board geometries. Claim fields use checked integer parsing;
invalid budgets, duplicate keys, unsafe IDs and misspelled booleans/quantifiers are rejected.

## Results of the registered run (appended 2026-10-22; predictions above are unedited)
Data: `results/C*.csv` (545 attack trials per claim + 69 controls), verdicts in `results/*.verdict.txt`. Output is
byte-identical for `RAYON_NUM_THREADS=1` and the default 8 (header command line excluded). Whole run: 4.7 s.

| # | outcome |
|---|---|
| P1 controls agree | **Held.** No `Invalid`. |
| P2 RL: no other type, and some start unresolved | **Half wrong.** `hw_other = 0` held. `Unsupported` was wrong: all 545 resolved (verdict `Survived`). |
| P3 RRL falsified | **Wrong.** 545/545 end in (18;1,1). |
| P4 RRRL falsified | **Held.** 8 counterexamples (7 mono, 1 patch), all (156;2,2) vs blank (52;2,2); 5 of 5 checked reproduce on a second geometry. A 6-cell patch suffices. |
| P5 RLL survives | **Held**, at 0/545 highways by 1.6e6 (a survival, not a proof). |
| P6 RRLR falsified and late | **Partly wrong.** Falsified, yes. "Rung 0 shows 0" was wrong: 13/545 perturbed starts have escaped by 1e5 (earliest 98263; with drift 4 per 384 steps the crossing alone takes about 98k steps, so those highways started near step 0). Only the blank start is late: onset 256240, escape 349510. |
| P7 adaptive beats sampling | **Wrong, 0 of 3.** Longest delay, adaptive vs 64 random patches: RL 76386 vs 94565; RRL 19466 vs 20118; RRRL 27726 vs 79915. |

### Consequences
- **Adaptive search is weak as built, so `Survived` is weaker than it looks.** Likely reasons (untested): the score is the
  escape step, which is mostly the board-crossing time plus a small transient, so it is nearly flat and the climb is
  noise; 40 single-cell mutations per chain is a short climb; and acceptance on ties (`>=`) lets it drift. Until it beats
  random sampling on a rule with a known sensitive start, treat adaptive rows as extra random samples, not as an adversary.
  To do: score by the transient length (needs a seeded onset), and calibrate on a rule with a known rare trigger.
- **Both the 'late' flag and the escape rungs were wrong in kind, not just degree.** The first version fired only when *all*
  counterexamples were late; it now uses the exact blank-board onset (`late` = onset > stated horizon). Escape counts still
  lag onset by the crossing time, so they are conservative. Perturbed starts that form a highway early are real
  counterexamples to a "chaotic at 1e5" claim and are listed separately, not hidden by the flag.
- **The pooled Clopper-Pearson interval printed in the first verdict files is withdrawn** (see the correction above).
- RL and RRL surviving 545 attacks is evidence of robustness within these classes only. Dense random backgrounds,
  larger patches, and onset-time statistics are not tested.

### Deviations
Results were regenerated after the onset-flag fix. The CSVs are unchanged by it; the earlier verdict text is in git
history (commit before the re-run). The re-run binary was built from a working tree that also held another contributor's
uncommitted hardening edits (claim-field validation, no pooled CI), so the provenance header's commit hash does not fully
describe the source; the trial rows are unaffected by those edits but a clean re-run is owed.

## Clean re-run with the promoted search (appended 2026-10-22, commit 047e395)
`results/rerun-clean/`, built from a throwaway worktree at 047e395 (no uncommitted source; binary sha256
`c7b699c578e6b96ddbd165815c6192f164338ef00ded4ef4dd769bc30e3e117e`, 11.6 s, identical output for 1 and 8 threads). This pays the
"clean re-run owed" item above. The harness's adaptive class is now `falsify::evolve_chain` (200 evaluations per chain, 4 chains,
immigration on), per `experiments/archive/2026-10-falsify-adaptive-search`. It is not a new registered test: no new prediction was made.
- Verdicts are unchanged: C1 Survived, C2 Survived, C3 Falsified, C4 Survived, C5 Falsified (horizon-sensitive, blank onset 256240).
- The attacker finds far more on RRRL: 126 of 456 adaptive evaluations end in a different-type highway (143 counterexamples in all),
  against 8 in total in the first run. Five were shrunk and reproduced on a second geometry, as before.
- Class rows now include the evolutionary chain's random draws under their generator's name (patch, mono, obstacle, ...), so those rows have
  more than 64 trials; mutated children are `adaptive`. Row totals are therefore not comparable with the first run.
- C1/C2: still no counterexample after ~1,300 attacks each; with the search now beating random at long transients, that survival is
  somewhat stronger evidence than before, but it remains "no counterexample in these classes at this horizon".
