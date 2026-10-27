# NR-20261026-wall-vs-memory-no-wall-porous: for six core-class ants, keeping the colour memory but randomising every turn taken on a fresh cell destroys the compact cube-root regime (porous, a ~ 0.86-0.91)

- Schema: 1
- ID: NR-20261026-wall-vs-memory-no-wall-porous
- Registered: 2026-10-26T23:30+13:00
- Author: Claude (AI research agent)
- Initial status: active
- Evidence class: empirical. One registered test (F1) on a pinned cohort of 6 rules x 8 seeds, finite windows. Not a proof; nothing beyond the tested specs is excluded.
- Objective and search keywords: decide whether the ant's interior colour memory alone, without the forced turn on fresh ground, keeps the territory compact with area exponent near 2/3 (H-memory sufficiency). Observables: area exponent a, perimeter exponent beta, compact/porous class. Keywords: wall, fresh ground, blank repels, colour 0 turns R, memory, local-time balancing, turn noise, hybrid walker, HybridWalker, hy:, F1, cube root, porous, compact.
- Claim and permitted pruning decision: Claim: in each of the 6 rules, `hy:RULE:0:1` (no noise on revisited cells, noise rate 1 on fresh cells) is porous by the registered criterion (early a >= 0.85 and beta >= 0.80): per-rule early a 0.861-0.906, beta 0.836-0.891, a raised by +0.19 to +0.29 over the deterministic ant; the registered H-memory criterion (compact and within 0.03) held in 0 of 6 rules. Permitted: defer an exact repeat of the EF = 1 / EV = 0 condition on these 6 rules with the same seeds, instrument and windows. Not permitted: concluding that interior memory is irrelevant (the same experiment's hybrid V1 suggests it supplies part of the exponent); excluding other rules, rule classes, intermediate fresh-noise rates (EF = 0.1 left all six compact), other fresh-ground perturbations (e.g. forced L, partial bias), backgrounds, or longer horizons.

## Topological dead-end signature

- Model and update semantics: one walker on Z^2, board 16384 x 16384 (run stops on reaching within 2 cells of the edge). `HybridWalker` (`src/walkers.rs`): the ant `RULE` (turn by rule[colour], colour -> colour+1 mod n), except that each step draws one SplitMix64 value from a stream seeded by SEED and, if the walker stands on a cell for the first time, replaces the turn with R or L (probability 1/2 each) with probability EF; on other cells with probability EV. The colour advances regardless.
- Rule-space vertices and adjacency: vertices are (rule, EV, EF, seed). No adjacency is claimed.
- Membership predicate: a spec belongs if and only if it is one of the 48 lines `hy:RULE:0:1:SEED` in `experiments/2026-10-26-wall-vs-memory/results/specs.txt` (RULE in `RLRLLRRLRLR`, `RLRLLRRRRRRR`, `RRLLLRLRRRLL`, `RRLLRLLRLR`, `RRRLLLLR`, `RRRRLLLLLLLR`; SEED 2026102601..2026102608).
- Canonicalization/equivalences: none.
- Invariants: not used.
- Scope: blank background, start at the centre heading north, the stated seeds.
- Observable and instrument: `bin/probe` (`probe 27 16384`) octave windows; per run a = slope of ln area vs ln t and beta = slope of ln perimeter vs ln area over windows k = 12..22 (t = window end), means over the 8 seeds; class thresholds as registered. Binary sha256 75fe757a7b84cb20259e8b64bab0018223520d82b3317321089dd3694cf74d82 (rustc 1.97.0), commit `f1bd2c8aebe67b08815438f037660a28510e53ab`.
- Horizon and windows: 2^27 steps; early window k = 12..22 (all 48 runs complete), late window k = 20..26 (46 of 48 complete; 10 runs escaped after the early window).
- Exclusions: EF < 1, EV > 0 with EF = 1, other rules, patched or random backgrounds, other boards and horizons, other observables (kappa, c).

## Evidence and limits

- Preregistered criterion: `experiments/2026-10-26-wall-vs-memory/README.md`, F1 row and classification, registered at `086c1ac` (22:55 NZDT) before code or runs; scoring script committed at `f1bd2c8` before the run.
- Evidence revision: `3040a0b86f69489a999e3881b8d4ff89886a0ac8`.
- Inputs/results (SHA-256, under `experiments/2026-10-26-wall-vs-memory/results/`): `rules.txt` a4fcff15f30dc97e2b7c9b574a77a2d3438d1a3a504e7ba5d534a9607f352591; `specs.txt` 17d15e9b9c1abefa4cc648b591755645ba6af182cfab7a5e24b833337b52dc61; `probe.csv` 49e83b9c688d2ea26ee19e0e58c9db8bd17da70a8025b5511377502d681532b8; `runs.csv` d6305f0d9287c6e9a04200c3503438fd28941f75fffb16a18f96eabac71f30dd; `conditions.csv` 473b737fe4e94d348b2d7101b6d801fe8a9a6ee4191bd108210cacadd4027997; `analysis.txt` 88a9508a4a9c29b82f7aec93ce5d6e9b076e4b0a26f9bb842e136a33ad44329c; `provenance.txt` 2a209bf89de9c8584203fa3c96371933a032936b715dab6acc30349bcd0ecc4f.
- Recipe: `uv run --frozen experiments/2026-10-26-wall-vs-memory/scripts/select_rules.py`; `RAYON_NUM_THREADS=4 sh experiments/2026-10-26-wall-vs-memory/scripts/run.sh`; `uv run --frozen experiments/2026-10-26-wall-vs-memory/scripts/analyse.py`.
- Proof or measured result: 48 runs, all with a complete early window. Per rule (mean, between-seed sd): early a 0.883 (0.026), 0.861 (0.027), 0.869 (0.026), 0.906 (0.028), 0.877 (0.023), 0.867 (0.029); deterministic ants 0.591-0.705. Porous in 6/6.
- Controls and oracle checks: gates G1 (rotor), G2 (`pw:0.5` corner), G3 (deterministic runs reproduce the census exactly) passed. `tests/hybrid_walker.rs`: sparse independent reference, no-noise = `reference::Ant`, full noise = `PersistentWalk(seed, 0.5)`, revisit-only noise rule-free; full `cargo test --release --locked` passed.
- Confounds: finite windows (early window ends at 2^23); six rules from one class (cls blob, 0.30 < alpha_w < 0.37, not bursty); escapes truncate late windows for 10 runs but not the scored early window.
- Why the evidence covers the predicate: the membership is exactly the 48 tested specs and every one was fitted. Nothing is claimed for untested rules or conditions.

## Reopening and cross-references

- Reopen if: an instrument or walker correction changes `HybridWalker`'s fresh-cell semantics; a longer horizon shows these specs returning to a ~ 2/3; other rules or rule classes are proposed (they are not members).
- Discriminating next test: a dose curve in EF between 0.1 and 1 on the same rules, to locate where the reflecting edge fails and whether the loss is sharp. Not registered.
- Experiment / lab notebook / scientific note: `experiments/2026-10-26-wall-vs-memory/README.md`, `NOTEBOOK.md`, `notebook.ipynb`; `notes/cube-root-hypothesis.md` (2026-10-26 update); `notes/open-questions-hypotheses.md`.
- Related signature IDs: none. The other entries concern conservation laws, the c law and kappa exposure classes.

## Amendments (append only)

### 2026-10-27 amendment 1 (review of PR 19): narrowed reading, status stays `active`

- Evidence revision: data `15d41a95d852d81713d0bab2900b6cd690760520` (unchanged); individual-run counts in `experiments/2026-10-26-wall-vs-memory/results/posthoc_review.txt`, added with this amendment.
- Reason: external review. The original claim text above is kept; read it with these limits.
  1. **Condition means, not runs.** "Porous in 6/6" classifies the six *condition means* under the registered criterion. Applying the same thresholds (early a >= 0.85 and beta >= 0.80) to individual runs, 39 of the 48 specs meet both (per rule: 7, 6, 6, 8, 7, 5 of 8; lowest run a = 0.824). The entry does not claim that all 48 trajectories are individually porous. Seeds are shared across rules, so the independent units are the six selected rules, not 48.
  2. **What the intervention is.** F1 randomises the turn on first departure; it also breaks coherent first-visit chirality and short-loop geometry and changes how the colour field develops. The entry records that this intervention disrupts compact growth, not that reflection is the mechanism or that deterministic R is the only first-departure policy that keeps growth compact (forced L is untested).
  3. **Window.** The early window `k = 12..22` ends at 2^22, not 2^23 (`k` is log2 of the window end); the Confounds line above is corrected by this amendment. The frozen fit is unchanged.
  4. **Noise.** EF = 0.1 shifted mean early a by +0.028 and left all six conditions compact: a statement about classification, not about a negligible effect.
- Replacement status: `active`, scope unchanged (exactly the 48 tested specs, same instrument and windows).
