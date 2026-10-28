# Making the falsification harness's adaptive search beat random sampling (2026-10-22)

## Question
In `experiments/active/2026-10-falsification-harness` the adaptive attacker lost to 64 random patches in 3 of 3 highway claims
(longest escape delay: RL 76386 vs 94565, RRL 19466 vs 20118, RRRL 27726 vs 79915). Is that because hill-climbing is
the wrong tool here, or because this particular climber was badly built?

## Diagnosis (observed 2026-10-22, from the committed CSVs, before any new code)
- Escape delay is heavy-tailed and plateau-dominated. RL: typical 53-62k, rare 94k-123k. The rare values come from
  `sparse` (max 114116) and `obstacle` (max 122842), not from dense patches (patch max 94565, class mean 57756).
  RRRL: typical 26.5-27.5k, rare 79-80k from `mono` and `patch`.
- The old chain (a) started from a dense radius-3 random patch, which is typical rather than tail; (b) mutated one
  cell at a time on a plateau, so almost every step is a tie or noise; (c) never touched the obstacle (a drop in front
  of the highway), the one lever that gave the largest delay on RL.

## Hypothesis
The landscape is rugged but has structure the old search ignored. An evolutionary search that (1) seeds its population
from the same random draws as the control, (2) keeps an elite set, (3) mutates at several scales (recolour, add, delete,
shift, heading) and (4) includes the obstacle's parameters as genes, will find longer delays than random search at the
same evaluation budget.

## Design (fixed before measuring)
- Claims: C1 RL, C2 RRL, C3 RRRL, as registered in `../../active/2026-10-falsification-harness/claims.txt` (horizon 2e6, board 2048).
- Three arms, each given exactly B = 200 evaluations per replicate, 30 independent replicates per claim:
  - `random`: 200 draws, each a uniformly chosen class of {patch, mono, half, stripe, sparse, obstacle}, via the harness's `make_trial`.
  - `old`: the harness's existing `adaptive_chain` (one-cell hill-climb), 200 evaluations.
  - `evolve`: 50 random draws as in `random`, then (mu + lambda) search, mu = 8 elites, 150 children, each a 1-3 stacked
    mutations of a uniformly chosen elite.
- Score (higher is the attacker's win): escape step for a highway of the baseline type; horizon*2 for an unresolved or edge
  escape; 4*horizon for a highway of a *different* type (a counterexample). Metric per replicate: the maximum score over its
  200 evaluations. Comparison: one-sided Mann-Whitney between arms over the 30 replicates (normal approximation, tie-corrected).
- Output is keyed by (claim, arm, replicate); thread count must not change it (checked).

## Registered predictions (2026-10-22, before any run of the new code)
| # | prediction | confidence |
|---|---|---|
| E1 | `evolve` beats `random` (median max-score higher, one-sided Mann-Whitney p < 0.01) in **both** C1 (RL) and C3 (RRRL). | 55% |
| E2 | In C2 (RRL, thin tail) `evolve` vs `random` is not significant at p < 0.05. | 60% |
| E3 | `old` does not beat `random` (p > 0.05) in any claim, reproducing the earlier loss under this paired design. | 75% |
| E4 | In C3 `evolve` finds a different-type highway (a counterexample) in more replicates than `random` does. | 50% |

If E1 fails the harness's adaptive class stays labelled "extra random samples" and no claim should lean on it. If E1
holds, it shows only that this search beats this sampler on these three rules; it is not a general adversary.

## Reproduce
`cargo run --release --locked --bin falsify_search -- experiments/archive/2026-10-falsify-adaptive-search/results` (provenance
header: command, commit, and a hash of any uncommitted `src/`+`tests/` diff, which is empty for a clean run).

## Results
(appended after the run; predictions above are not edited.)

## Round 1 results (run 2026-10-22, 30 replicates x 200 evaluations; `results/search.csv`, `results/search_summary.txt`)
Provenance caveat: the binary was built from a working tree that also held another contributor's uncommitted edits to
`src/falsify.rs` (listed in the CSV header). The arms use only the public API and the shared start generators, so I do not
expect them to matter, but a clean re-run is owed. Run time 23.6 s; output identical for 1 and 8 threads (checked on a small run).

| claim | arm | median max score | one-sided Mann-Whitney vs `random` |
|---|---|---|---|
| C1 RL | random | 124144 | - |
| | old | 90350 | p = 1.00 (random is better) |
| | evolve | 154172 | P(evolve>random) = 0.91, p = 2.7e-8 |
| C2 RRL | random | 37712 | - |
| | old | 20648 | p = 1.00 |
| | evolve | 45996 | P = 0.73, p = 1.3e-3 |
| C3 RRRL | random | 8000000 (saturated) | - |
| | old | 29526 | p = 1.00 |
| | evolve | 8000000 (saturated) | P = 0.37, p = 0.999 |

Counterexample discovery in C3 (a highway of another type; score 4 x horizon): random 30/30 replicates, evolve 22/30, old 11/30.

### Predictions vs outcome
- **E1 (evolve beats random in both C1 and C3): failed.** It holds in C1 by a wide margin (median 154k vs 124k; best single
  start 308448 steps vs 164313). In C3 the score saturates at the counterexample value, so the delay metric cannot show a win
  there, and the discovery rate is *lower* than random's.
- **E2 (C2 not significant): failed.** `evolve` beats `random` in C2 (p = 1.3e-3).
- **E3 (old does not beat random): held**, and more strongly than predicted: `old` is significantly *worse* than `random`
  in C1 and C2 (it spends 200 evaluations on a dense-patch plateau).
- **E4 (evolve finds counterexamples in more C3 replicates than random): failed** (22 vs 30).

### Interpretation
- The original failure was mostly the search design, not a property of adaptivity: seeding from the random draws, keeping an
  elite set, multi-scale mutations and the obstacle genes make the same budget find substantially longer delays on RL and RRL.
- The C3 result is an objective conflict I did not anticipate: ranking by delay pulls the population toward long-transient
  starts and away from the rare structures (one-colour patches) that produce a different highway type. A counterexample is
  rare (about 2% of draws), so spending 150 of 200 evaluations on children of delay-elites loses discoveries that pure random
  draws make. Untested explanation; round 2 tests it.
- Superiority is over this sampler (uniform over six generators) on three rules, at one budget.

## Round 2: registered 2026-10-22, before the variant was implemented
Variant `evolve2`: identical to `evolve`, except each child is, with probability 1/4, a fresh random draw ("immigration")
instead of a mutation of an elite. Same budget, same 30 replicates, same claims; the other three arms are re-run and must
reproduce round 1 exactly (a determinism check).
| # | prediction | confidence |
|---|---|---|
| E5 | In C3, `evolve2` finds a different-type highway in >= 27/30 replicates (random 30/30, evolve 22/30). | 65% |
| E6 | In C1, `evolve2` still beats `random` on max delay, one-sided p < 0.01. | 70% |
| E7 | In C2, `evolve2` beats `random`, p < 0.05. | 60% |
Round 2 results go to `results/round2/`.

## Round 2 results (`results/round2/`; same provenance caveat as round 1)
The `random`, `old` and `evolve` rows reproduce round 1 byte for byte (md5 of the arm's CSV rows), so the added arm changed nothing else.

| claim | `evolve2` vs `random` (max delay) | `evolve2` different-type highway found |
|---|---|---|
| C1 RL | median 146679 vs 124144, P = 0.80, p = 4.2e-5 | n/a (no other type exists in the data) |
| C2 RRL | median 44813 vs 37712, P = 0.72, p = 2.1e-3 | n/a |
| C3 RRRL | saturated | 27/30 replicates (random 30/30, evolve 22/30) |

- **E5 held, barely** (27/30 meets the registered threshold of 27; a coin-flip away from missing it). **E6 held** (p = 4.2e-5). **E7 held** (p = 2.1e-3).
- `evolve2` vs `evolve` on delay: no loss (C1 p = 0.94 that evolve2 is larger, i.e. evolve is nominally ahead; C2 0.77), and a nominal
  gain in C3 discovery (27 vs 22, p = 0.038, not corrected for the three-claim family).

### Conclusion
- **On the delay objective the adaptive search now beats random sampling** at equal budget on RL (p ~ 1e-5 to 1e-8) and RRL (p ~ 1e-3), with
  30 replicates each, replicated seeds, and the earlier loss reproduced for the old climber.
- **As a counterexample finder it does not beat random** on the one rule that has a counterexample (RRRL): the best arm
  (27/30) is still below plain random draws (30/30). Immigration repairs most of the damage but not all. Do not describe the
  adaptive class as stronger than sampling for falsification; it is stronger at hunting long transients.
- Not tested: other rules, other budgets, the chaotic-claim objective (still the unvalidated smallest-bounding-box heuristic),
  and an objective that rewards structural novelty rather than delay. The comparison is against one sampler.
- Next, if worth the effort: promote `evolve2` into `falsify::adaptive_chain` (blocked on the other contributor's uncommitted edits to
  `src/falsify.rs`), re-run `claims.txt`, and calibrate on a rule with a known rare trigger and a rarer one than RRRL's mono patch.

## Clean re-run (commit 047e395, `results/clean/`)
`evolve` and `evolve2` now call the library function `falsify::evolve_chain`; the `random` and `old` arms are unchanged. Built from a worktree with
no uncommitted source (`# uncommitted src/tests files: none` in the CSV header). All four arms are byte-identical to `results/round2/`, which
closes the provenance caveat of rounds 1 and 2 and confirms the port to the library did not change behaviour. Round-2 conclusions stand unchanged.
