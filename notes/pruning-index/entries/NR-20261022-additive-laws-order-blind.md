# NR-20261022-additive-laws-order-blind: additive local conservation laws (families A0, F1, F2, F3) do not depend on the order of the colours, for rules of length 2..8

- Schema: 1
- ID: NR-20261022-additive-laws-order-blind
- Registered: 2026-10-22T22:10+13:00
- Author: Claude Sonnet 5.5 (AI research agent)
- Initial status: active
- Evidence class: empirical (exhaustive over the stated finite membership; the all-n extension is an unchecked derivation)
- Objective and search keywords: find an invariant, conservation law, parity or symmetry that distinguishes rules with the same number of colours and the same net turn, e.g. separates `RRLL` from `RLRL`, or a chaotic from a highway rule among permutations of one string. Keywords: invariant, conservation, parity, modular, Smith normal form, sublattice, order-blind, fingerprint.
- Claim and permitted pruning decision: for the ansatz below, the complete law group of a rule is a function of `(n, ±D mod 4, trivial?)` only (`D = #R - #L`). Permitted: defer repeating additive-law mining in these families on rules of length 2..8 as a means of separating rules of equal `(n, ±D mod 4, trivial?)`, and do not use their fingerprints as a feature for such a separation. Not permitted: any exclusion of non-additive laws (pair potentials, ant potentials that read neighbouring colours, edge flux, history dependence), of lengths above 8, of other lattices or turmites with states, or of any growth or highway question.

## Topological dead-end signature

- Model and update semantics: one ant on `Z^2`, colours `0..n-1`, on colour `c` turn by `rule[c]` (R = +1, L = -1 quarter turn), set colour to `(c+1) mod n`, step; blank background colour 0. Reference implementation `src/reference.rs`.
- Rule-space vertices and adjacency: all `2^n` strings over `{L, R}` for `n = 2..8` (508 vertices), including non-primitive and non-canonical; adjacency not used.
- Membership predicate: rule string of length 2..8 over `{L, R}` (committed enumeration `results/fingerprints.csv`, 508 rules x 4 families).
- Canonicalization/equivalences: none assumed. Complement, reversal and all cyclic rotations were *tested* and preserve the fingerprint (0 differences in 2032 checks); that is a result, not an assumption.
- Invariants: the Smith-form fingerprint (free rank, nontrivial invariant factors) of the integer constraint matrix of local transitions, extractor `experiments/_lib/lawmod.py` (`Snf.fingerprint`), pinned at `849272d9208fd0bd9ec4d5b4ec15b300d44a2f4f`. The law group at modulus `m` is `Z_m^free x prod Z_{gcd(d_i, m)}`.
- Scope: laws `V = a x + b y + e t + Phi(h, s(pos)) + sum_cells w(s(cell), colour) (mod m)`, `w(s, 0) = 0`, families A0 (no class, `Phi = d h`), F1 (no class), F2 (`s = (x+y) mod 2`, states with `h = s mod 2`), F3 (`s = (x mod 2, y mod 2)`, states with `h = x+y mod 2`); all moduli whose prime factors are in {2, 3, 5, 7} up to 2^8, 3^4, 5^3, 7^3; primes 11..37 detected by a consistency assertion. Any initial heading and finite tape for A0/F1; the invariant manifold `h + x + y` even for F2/F3 (contains the blank start).
- Observable and instrument: law group of a rule; exact algebra, no randomness; validated by the oracle (below).
- Horizon and windows: not applicable (a law holds for all steps by induction over local transitions).
- Exclusions: laws coupling the ant or a cell to neighbouring cells' colours; pair potentials; non-linear or history-dependent invariants; lengths above 8; other lattices; turmites with states; any statement about growth, highways or chaos.

## Evidence and limits

- Preregistered criterion: `experiments/archive/2026-10-invariant-mining-snf/README.md`, P1 (fingerprint a function of `(n, #R)` alone, zero exceptions), registered at commit `db7eb400e4a59556b8cf6083cd984372069845de` before any solver code existed. P1 held; the coarser `(n, ±D mod 4, trivial?)` form is post hoc.
- Evidence revision: `849272d9208fd0bd9ec4d5b4ec15b300d44a2f4f`.
- Inputs/results (SHA-256): `experiments/archive/2026-10-invariant-mining-snf/results/fingerprints.csv` d0a6b0228f87effc0828a13c3f98b351c500ef7daaab3504ff46c4569e8e274a; `universal.csv` b764e1339b7f3b9e50b982ed3546faff37bd79b07a0bd0472e2c5cf07bce4746; `summary.json` f08cbcda1a1dda85203bac092588d142df4dde6350e49d18fa9b608db2699405; `oracle_summary.json` 849eecf83b4ffa69f171df1b76d4629cf1c2bd5d1329d14493925522128279bf; `crosscheck_peer.json` f0d33debe45278a388457965322eecdccb6e92bfd2a98f3f9cee26f75c13b179.
- Recipe: `uv run --no-project experiments/archive/2026-10-invariant-mining-snf/scripts/census.py --nmax 8`, then `scripts/summarize.py`; oracle `scripts/oracle.py --exe <invariant_mining_snf_verify> --nmax 6 --steps 2000 --starts 16` (seed 20261022); cross-check `scripts/cross_check_peer.py`. Full command list in the experiment README.
- Proof or measured result: 508 rules x 4 families, 0 fingerprint differences among rules with equal `(n, #R)`; 68 groups by `(family, n, ±D mod 4, trivial?)`, none split. Argument for all `n` (not a checked proof): a cell potential cannot see the heading, so each colour contributes a constant `E_R` or `E_L` per class, and the only rule-dependent condition is `#R E_R + #L E_L = 0 (mod m)` round the colour cycle.
- Controls and oracle checks: solver equals brute force on random matrices and tiny rules, and equals exact integer elimination on all rules of length <= 5 (selftest); 14,416 generator lines conserved over 2000 `reference::Ant` steps from seeded starts (0 violations); 6560/6560 random non-laws (n <= 4) violated; agrees with the independent enumerative miner (`src/bin/invariants.rs`) on 1016/1016 (rule, m in {2, 4}) cells.
- Confounds: oracle lengths <= 6 only; the controls are random, not adversarial; the local solver does not see primes above 37; the independence of the two miners is partial (same ansatz, different search).
- Why the evidence covers the predicate: the membership is the finite set of rules of length 2..8 and the census enumerates all of them in all four families. Nothing is claimed beyond that set.

## Reopening and cross-references

- Reopen if: a family outside the stated ansatz yields a law whose existence depends on the order of the colours and passes the same oracle test; or the fingerprint computed at some `n > 8` differs between two rules of equal `(n, ±D mod 4, trivial?)`; or the oracle finds a violation of a generator.
- Discriminating next test: pair-potential family with a quotient by functionals that vanish on all finite fields (registered in the experiment README as the next question); budget seconds of exact algebra for `n <= 6`.
- Experiment / lab notebook / scientific note: `experiments/archive/2026-10-invariant-mining-snf/README.md`, `NOTEBOOK.md`, `notebook.ipynb`; `notes/research-frontier-2026-10-13-pm.md` (T4, appended note).
- Related signature IDs: none. Related work: `experiments/archive/2026-10-invariant-mining/` (enumerative miner at m = 2, 4; family A0 is its ansatz and the two agree).

## Amendments (append only)

None.
