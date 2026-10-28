# Invariant mining, stage 2: all moduli at once, sublattice families, and what the rule can and cannot change

Companion to `experiments/archive/2026-10-invariant-mining/` (a parallel agent's enumerative miner for
`I = a*x + b*y + d*h + e*t + sum w(colour)` at moduli 2 and 4). That folder is not edited here. This
one asks what the enumerative miner cannot: which laws exist at *every* modulus, which laws are
merely universal (true of every unit-step walker that turns by 90 degrees, with an n-colour counter,
whatever the rule), and how much of the rest depends on the rule at all.

## Question and registered prediction

Registered 2026-10-22 21:50 +13:00 (NZDT), starting revision `b0c9e8a3be66d75176fb27d0b54d758b17558272`,
before any solver code exists. Nothing below has been computed yet.

**Question.** For an n-colour ant, what is the full group of additive local conservation laws, and does
it carry any information about the rule beyond what is already visible in `(n, #R)`?

### Ansatz families (fixed before mining; no weights are searched and a "best" one reported)

A law is `V = a*x + b*y + e*t + Phi(h, s(pos)) + sum_cells w(s(cell), colour)  (mod m)`, with the
normalisation `w(s, 0) = 0` (the blank field contributes nothing) and one `Phi` value fixed to 0. It is a
*proved* invariant when `V` is unchanged by every local transition the family admits (cell colour `c`,
heading `h`, class `s` of the ant's cell), colour wraps `n-1 -> 0` and heading wraps included. Each
condition is linear over `Z/m`, so all moduli follow from one Smith normal form over `Z` of the
integer constraint matrix.

| family | site class `s` | transitions required | `Phi` | meaning |
|---|---|---|---|---|
| A0 | none | all `(c, h)` | `d*h` (integer heading, as in the parallel miner) | cross-check ansatz |
| F1 | none | all `(c, h)` | arbitrary function of `h` | superset of A0 |
| F2 | `(x+y) mod 2` | `(c, h, s)` with `h = s (mod 2)` | arbitrary on reachable `(h, s)` | sublattice potentials |
| F3 | `(x mod 2, y mod 2)` | `(c, h, s)` with `h = x+y (mod 2)` | arbitrary on reachable `(h, s)` | finer lattice classes |

The restriction "`h + x + y` even" in F2/F3 is itself a proved invariant (every step flips the parity of
`x+y` and of `h`), and the blank start `(h, x, y) = (0, 0, 0)` lies on it, so laws proved on that
manifold constrain every blank-start trajectory. `A0 <= F1 <= F2 <= F3` as sets of functionals.

The *universal* group `U_n` of a family is the solution set when every colour is allowed either turn
(equivalently the intersection over all `2^n` rules of length `n`, and equivalently the "random-turn
walker with an n-colour counter" negative control). The *rule-specific content* of a rule is the
quotient `G(rule) / U_n`, summarised through the Smith invariant factors ("fingerprint": free rank and
the sorted nontrivial factors `d_i`; the law group at modulus `m` is `Z_m^free x prod Z_{gcd(d_i, m)}`).

### Derivation behind P1 (written before computing)

For a fixed rule, a law forces, per colour `c`, the quantity
`E_c(h, s) = a*dx + b*dy + e + Phi(h', s') - Phi(h, s)` (with `h' = h + turn_c`, `(dx, dy)` the step in
direction `h'`) to be independent of `h` (the cell potential cannot see the heading), and then
`w(s, c+1) - w(s, c) = -E_c(s)`. Going once round the colour cycle leaves one condition per class:
`#R * E_R(s) + #L * E_L(s) = 0 (mod m)`. The order of the colours never enters.

### Predictions

| # | prediction | confidence | failure means |
|---|---|---|---|
| P1 | For each of F1, F2, F3 the fingerprint of a rule is a function of `(n, #R)` alone: zero exceptions among all 510 rules of length 2..8 (non-primitive and non-canonical included). Corollaries: complement, reversal and every cyclic shift preserve the fingerprint. | 90% | derivation error or solver bug |
| P2 | A0 agrees with the parallel miner: for every rule of length 2..8 and `m` in {2, 4}, (number of nonzero tuples listed by `invariants RULE`) + 1 = size of the A0 solution set from the SNF solver. | 85% | one of the two solvers is wrong; resolve against the oracle |
| P3 | The universal F1 group at `m = 2` has order `2^3` for even `n` and `2^2` for odd `n` (checkerboard parity, heading parity, and for even `n` the colour clock). At odd prime `p` the universal F1 group is trivial unless `p` divides `n`, when it has order `p` (colour clock only). | 80% | a universal law I did not enumerate |
| P4 | In F1 at `m = 4`, a rule has a law with `a = b = e = 0` and non-constant `Phi` (heading determined by the tape; for Langton's ant, heading = number of colour-1 cells mod 4) **iff** `D = #R - #L = 0 (mod 4)`. Checked on all 510 rules. | 90% | derivation error |
| P5 | Oracle: every SNF generator of A0, F1, F2, F3 for every rule of length 2..6 at `m` in {2, 3, 4, 6, 8, n, 2n, 4n} is conserved along 2000 reference-ant steps from 16 seeded random starts on the manifold: 0 violations. Control: random vectors outside the solution set are violated within the same runs in at least 99% of draws (so the checker has power). | 95% | solver, sign convention or checker bug |
| P6 | Sublattice accounting is new: at modulus `n` the universal order satisfies `|U_n^{F2}| > |U_n^{F1}|` for every `n` in 2..8, because the ant alternates sublattices (departures from even cells minus departures from odd cells = `t mod 2`). | 75% | no sublattice accounting law (my argument is wrong) |
| P7 | The universal F3 order exceeds F2 at modulus `n` for at least one `n` in 2..8. | 45% | finer classes add nothing |
| P8 | Tile-free consequences for highways: the laws with every `w = 0` (no dependence on the laid tile) constrain `(period, dx, dy)` only through "period even" and "`dx + dy` even". All confirmed highways in `experiments/archive/2026-10-census-sweeps/results/confirmed_*.csv` obey every such law (`a*dx + b*dy + e*period = 0 mod m`). I expect no constraint beyond the known H19. | 85% | detector bug (a violation) or a genuinely new constraint (a surprise) |

If P1 holds, every law in these families is a function of `(n, #R)`, so the instrument cannot separate
`RRLL` from `RLRL`. That would be a finding (an order-blind class of invariants), not a failure of the
instrument, and it is what I expect.

### Explicitly not tested here (open)
- Laws that couple the ant to the colours of neighbouring cells, pair potentials, edge flux, any
  history dependence. These are the only places left where rule *order* could enter. A pair-potential
  ansatz needs a quotient by functionals that vanish on all finite fields (telescoping
  `kappa(c) - kappa(c')` terms and duplicates of site potentials), otherwise group orders are inflated;
  not built.
- Any claim about growth exponents or highway formation beyond P8.

## Pruning-index preflight

- Index revision `b0c9e8a3be66d75176fb27d0b54d758b17558272`. `rg --files notes/pruning-index/entries`
  returned nothing (no entries). `rg -n -i -e invariant -e conservation -e parity -e symmetr -e modular
  notes/pruning-index/entries` returned nothing (rc=1).
- Candidate signature IDs: explicit no matches (a no-match is a recorded outcome, not evidence of novelty).
- Scope: exact algebraic computation on all rules of length 2..8; the solver has no randomness; the
  oracle check uses seeded starts.
- Decision: run. No exclusions. No family pruned.
- Compute budget: seconds to minutes on one core; stop after the registered tables.

## Reproduction

All exact algebra or seeded; no wall-clock dependence. From the repository root (the shared `.venv` was
unwritable here, so `uv run --no-project` was used; the scripts are standard-library Python and need no
environment):

```sh
uv run --frozen experiments/_lib/lawmod.py --selftest                       # solver vs brute force and vs exact elimination
uv run --frozen experiments/archive/2026-10-invariant-mining-snf/scripts/census.py --nmax 8   # fingerprints, universal groups, P4  (~30 s)
uv run --frozen experiments/archive/2026-10-invariant-mining-snf/scripts/summarize.py         # evaluates P1, P3, P4, P6, P7 -> results/summary.json
cargo build --release --locked --example invariant_mining_snf_verify --bin invariants       # own CARGO_TARGET_DIR
uv run --frozen experiments/archive/2026-10-invariant-mining-snf/scripts/oracle.py --exe <target>/release/examples/invariant_mining_snf_verify[.exe] --nmax 6 --steps 2000 --starts 16
uv run --frozen experiments/archive/2026-10-invariant-mining-snf/scripts/cross_check_peer.py --exe <target>/release/invariants[.exe]
uv run --frozen experiments/archive/2026-10-invariant-mining-snf/scripts/highways.py          # reads the committed census confirmed_*.csv
uv run --frozen experiments/archive/2026-10-invariant-mining-snf/scripts/build_notebook.py    # rebuilds notebook.ipynb from results/
```

Seeds: oracle seed 20261022 (a start is a function of seed, rule string and start index only); control
vectors are drawn with `random.Random(f"{seed}-{rule}-{family}-{m}")`. Provenance (commit, command, hashes of
`lawmod.py`, the oracle binary, the laws file and the parallel miner's sources) is written next to each result
(`results/*_provenance.json`, `oracle_summary.json`, `crosscheck_peer.json`). Interim results from an earlier
solver (exact integer elimination, n <= 6) were overwritten by the final-solver runs; the headline numbers were
identical (0 violations, 0 mismatches, 0 P1 exceptions at n <= 5).

## Results, uncertainty and limitations

Appended below this line only, after each run; the predictions above are not edited.

### Results (2026-10-22, written after the runs; evidence at the commit that contains this section)

| # | outcome | numbers |
|---|---|---|
| P1 | **held** | 0 exceptions among 508 rules x 4 families (fingerprint depends on `(n, #R)` only). Complement, reversal and all rotations preserve the fingerprint: 0 differences in 2032 rule-family checks. Post hoc (noticed in the table afterwards): coarser still, the fingerprint is a function of `(n, Â±D mod 4, rule trivial?)`: 68 (family, n, ±D, trivial) groups in total, none split. Only 2-3 distinct fingerprints exist per `n` in F1..F3. |
| P2 | **held** | 0 mismatches in 1016 comparisons (508 rules x m in {2, 4}) against `src/bin/invariants.rs` (sources hashed in `crosscheck_peer.json`; they were uncommitted when first run, committed by the time of the final run). |
| P3 | **held** | F1 universal order at m = 2 is 8 (even n) and 4 (odd n) for every n in 2..8; at p = 3, 5, 7 it is p when p divides n and 1 otherwise (21 of 21 cells). |
| P4 | **FALSIFIED as registered** | 170 mismatches among 508 rules, all with `D = 2 mod 4` and `n` even. A pure-tape heading law (a = b = e = 0, Phi non-constant) exists for every even `n`: heading parity is a function of the tape (`Phi = 2h`), because the universal colour clock gives `t = sum c N_c mod 2` and heading parity equals time parity. What `D = 0 mod 4` buys is the full heading mod 4. A post hoc refinement (a law with `Phi(1)` odd) has 0 mismatches over 508 rules; it was written after seeing the failure, uses the same derivation, and is not independent evidence. 170 rules have `D = 0 mod 4`. |
| P5 | **held** | 0 violations in 14,416 generator lines (A0 2280, F1 2816, F2 3672, F3 5648), each applied to 16 starts (8 on-manifold for F2/F3), 2000 reference-ant steps, plus a from-scratch recomputation at the end of each start. Controls: 6560 of 6560 random non-law vectors (n <= 4) violated. |
| P6 | **held** | `|U^F2| / |U^F1|` at m = n is 2, 3, 2, 5, 6, 7, 4 for n = 2..8: always > 1. |
| P7 | **held (predicted at 45%)** | F3 exceeds F2 at m = n for **all** n in 2..8. Post hoc regularity: `|U^F3| / |U^F2| = n^2` exactly for all seven n (4, 9, 16, 25, 36, 49, 64); unexplained here. |
| P8 | **held** | 582 distinct confirmed rules (`confirmed_v2.csv` + `confirmed_1B.csv`; not 589): 0 violations of any tile-free law in F1, F2, F3. The tile-free group has the *same order for all 582 rules* (F1/F2: 4, 8, 8 at m = 2, 4, 8; F3: 8, 16, 16) and, for every `n` that occurs, that order equals the order of the tile-free part of the *universal* system at m = 2, 4, 8 (`rule_tile_free_equals_universal_for_all` is true in F1, F2, F3). The universal group is contained in each rule's group, so equal orders mean equal groups at those moduli: tile-free laws are the universal parity laws and add nothing to H19. (Equality is checked at m = 2, 4, 8 only.) |

Reading. Within these families the law group of a rule is a function of the colour count `n`, the net
turn `D = #R - #L (mod 4)` up to sign, and whether the rule is trivial. The order of the colours never
matters, so `RRLL` and `RLRL` (or any rotation, reversal, or other permutation) have isomorphic law groups.
The laws that exist (checkerboard parity, heading parity, the colour clock mod `n`, sublattice colour
clocks, and for `D = 0 mod 4` heading = tape mod 4) are bookkeeping consequences of the colour cycle and the
lattice; none of them says anything about growth, highways or chaos, and none can be used as a feature that
separates rules with the same `(n, D class)`. Whatever distinguishes a chaotic rule from a highway rule
among its permutations lies outside additive local laws.

Addendum on P7's regularity (hypothesis, not tested by a registered prediction). For odd `n` the universal order at `m = n` is exactly `n^1, n^2, n^4` for F1, F2, F3 (n = 3, 5, 7), i.e. one colour clock per site class. A candidate reason: every turn is ±90°, so the move axis alternates and the class sequence of the ant cycles with period 4 whatever the rule, which makes the number of departures from each class a function of `(t, ant class)`; each class then carries its own clock. For even `n` the ratio F3/F2 is still `n^2` but F2/F1 is `n` or `n/2` (`n/2` when `4 | n`), where dividing by 4 is not free, so this explanation is incomplete there. Unproved.

### Limits and deviations (stated, not hidden)
- Exhaustive only for `n <= 8` (census) and `n <= 6` (oracle). The extension to all `n` rests on the
  derivation above, not on a checked proof; a Lean proof would be natural for this bookkeeping argument.
- The local solver tracks primes 2, 3, 5, 7 (up to 2^8, 3^4, 5^3, 7^3) and detects primes 11..37 (cap 1) by a
  free-rank consistency assertion that did not fire on any rule. Primes above 37 are not detected; moduli are
  restricted to those products. Validated against exact integer elimination on every rule of length <= 5.
- The first solver (exact integer elimination with column tracking) was replaced mid-experiment: on F3 at
  `n = 7` (`RRRRRLL`) its entries exceeded 4300 digits and a single rule took 28 s, stalling the census.
- Registered text errors, not edited above: the header time "21:50" (the freezing commit is 21:43:05) and
  "510 rules" (correct: 508).
- The oracle's controls are random vectors, not adversarial near-laws, and exist for `n <= 4` only.
- P8 for F2/F3 is existential over the unknown reference class, so weaker than for F1.
- The scripts were actually run with `uv run --no-project` (the shared `.venv` is unwritable in this environment, `uv run --frozen` fails with `Access is denied` on `.venv\lib64`); the commands above show the canonical `--frozen` form, and the scripts need no packages.
- Full `cargo test --release --locked` (own `CARGO_TARGET_DIR`, 2026-10-22, tree at `0419f70` plus uncommitted work of other agents): 45 test binaries, 181 passed, 0 failed, exit 0.

### What is not shown
Nothing about growth exponents, onset of highways, or whether any non-additive invariant (pair potentials,
edge flux, history dependence) separates rules of equal `(n, D class)`. That is the open question this
instrument makes sharp.

## Pruning-index outcome and next question

Outcome: signature `NR-20261022-additive-laws-order-blind` (see `notes/pruning-index/entries/`), empirical,
scoped to the stated families and `n <= 8`. It defers re-mining A0-F3 for order-sensitive invariants; it does
not prune any non-additive ansatz.

Next question: build the pair-potential family (potential on horizontally and vertically adjacent cell pairs,
ant potential depending on the colour of the cell it enters), quotient by functionals that vanish on all
finite fields, and ask whether any law depends on the order of the colours. Register the prediction first; my
prior is that the quotient is trivial (60%).
