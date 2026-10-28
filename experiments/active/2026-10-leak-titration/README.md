# Leak titration: is there a threshold in how much fresh-ground randomness the compact ant tolerates?

## Question and registered prediction

Registered 2026-10-28 20:59 (+1300) NZDT, base commit `1b14a1e7df1ba0ed1bce2fbe7f9e904e2cf4a047`,
**before any of the 1068 grid runs and before the run or analysis scripts were written**. The only code
that existed at registration is the synthetic calibration (`scripts/calibrate_sharpness.py`, no ant
data) and the spec generator (`scripts/select_specs.py`, no draw). Requested by the project owner.

**Known so far** (`experiments/active/2026-10-wall-vs-memory/README.md`, Stages 1-3c;
`NR-20261026-wall-vs-memory-no-wall-porous`, `NR-20261028-wall-vs-memory-bounded-random-fresh-compact`):
for the six core-class rules, randomising the turn on first departure from a cell with probability
EF changes the early area exponent a by +0.028 on average at EF = 0.1 (all six conditions stay
compact) and by +0.19 to +0.29 at EF = 1 (all six condition means porous). Nothing is measured between.
The mechanism the record currently favours is a *bound on the length of runs of consecutive fresh
steps* (forced R, forced L and reversal all bound it and stay compact; random R/L does not and goes
porous), not determinism and not handedness. The EF dose curve is listed as an unregistered next step
(README "Next questions"; `notes/open-questions-hypotheses.md` Q33).

**Question.** As the leak EF is raised from 0 to 1 on fresh ground only, does the ant's territory go
from compact to porous at a **threshold** (an abrupt, rule-independent-in-position loss, as in a
percolation-like transition), or by a **smooth crossover**? And does the answer depend on the
handedness of the base fresh-ground turn?

### How this design differs from the owner's proposal, and why

The proposal was: coarse sweep EF = 0.1, 0.2, 0.3, 0.4, 0.5 and 1.0 on fresh cells only, fine sweep
around the failure, observables A/P, area exponent and c*kappa, plus a forced-L control. Changes:

1. **Grid.** 0.6, 0.7, 0.8 and 0.9 are added. The proposed grid has a hole from 0.5 to 1.0, which is
   exactly where I expect the action (a linear rise from the one measured point, +0.028 at 0.1, would
   put the half-way point near 0.5; a hole there cannot tell a threshold from an endpoint effect).
2. **Forced L at EF = 0 is already measured** (wall-vs-memory Stages 3, 3b): 0 porous in 318
   deterministic bounded runs, and random-but-bounded fresh turns (R/U, L/U) are also compact. So
   the proposed logic "L compact means determinism, L porous means geometry" is already resolved,
   against both readings (random *and* bounded stays compact). The control that still carries
   information is a **leak on a forced-L base** (arm L below): same leak, mirrored base turn.
   It tests whether the position or shape of any transition depends on the base handedness.
   Caveat from Stage 3: 2 of these 6 rules (`RLRLLRRLRLR`, `RLRLLRRRRRRR`) form a highway under forced L
   at EF = 0 and escape the board; they cannot be scored in arm L (reported, not hidden).
3. **c*kappa is dropped as an observable.** `kappa*c = (dA/dt)(A/P)` is an algebraic identity
   (`notes/kappa-experiment-design.md` B3: "algebra; a check on the code"), so "verifying it across the
   transition" cannot fail and tells nothing. The compactness readouts are the existing ones: early area
   exponent a, perimeter-area exponent beta (beta = 1/2 for a compact blob; the A/P growth that the owner
   calls L is `A^(1 - beta)`), and the frozen class.
4. **No universality-class claim is possible from this design** (see "What this cannot show"). It can
   say whether there is a threshold-like feature and where; naming a class needs a finite-size collapse
   with an order parameter, which is a later stage.

### Hypotheses

Notation: EF = leak probability per fresh step (the turn is replaced by R or L, equally likely, so on
the base-R arm the fresh turn is L with probability EF/2); `abar_r(EF)` = mean over 8 seeds of early a for rule r;
`Delta_r = abar_r(1) - abar_r(0)`.

- **H-sharp.** One interior EF_c separates a compact phase from a porous one; most of the rise in a
  occurs in one 0.1 step. Run-level classes coexist near EF_c within a rule; EF_c does not drift with
  the fit window.
- **H-smooth.** The rise is spread over the whole range (a crossover); no single 0.1 step carries
  more than about a quarter of it. A real mechanism for this: the fresh-run length has a scale
  that grows continuously with EF (Q33), and compactness is lost when that scale competes with the
  territory size, which grows with t, so the apparent position would drift with the window.
- **H-endpoint** (a trap to rule out): all of the rise sits in the last step 0.9 -> 1.0. Physically
  implausible (P(L) per fresh step moves from 0.45 to 0.5); if seen, suspect an implementation
  singularity at EF = 1 before suspecting physics.

My priors, stated before measuring: H-smooth 50%, H-sharp 25%, unresolved 25%. The one datum (+0.028 at
EF = 0.1, i.e. 0.14 of the rise Delta, against 0.10 for a linear ramp) fits a gentle start.

## Instrument and frozen scoring

Instrument: `probe 27 16384`, unchanged from wall-vs-memory (board 16384, windows k = 9..27, `k` = log2 of
the window end). The classifier is copied from `experiments/active/2026-10-wall-vs-memory/scripts/analyse_stage3c.py`
(`fit`, `classify`, `stalled`, `filler`); a gate checks it against that scorer's committed rows.
Per run: early a and beta over k = 12..22, late a over k = 20..26, class in {compact, intermediate, porous,
escape, stalled, filler}. Fit windows for the drift test: k = 12..k_end for k_end in {16, 18, 20, 22}.

**Arms and grid** (6 rules of `wall-vs-memory/results/rules.txt`, seeds 2026102601..08, as in Stage 1):

| arm | spec | EF values | runs |
|---|---|---|---|
| R (base forced R, the ant's own colour-0 turn) | `hy:RULE:0:EF:SEED` | 0 (deterministic, 1 run per rule), 0.1 .. 1.0 step 0.1 | 6 + 480 |
| L (base forced L on fresh ground) | EF = 0: `ft:RULE:L`; else `fs:RULE:SET:SEED` | 0, 0.1 .. 1.0 | 6 + 480 |
| law gate (base R through the `fs:` encoding) | `fs:RULE:SET:SEED` | 0.5, 0.8 | 96 |

Arm L's 20-letter SET holds k = 10 EF letters of the minority turn (R) and 20 - k of L, so the minority
probability is k/20 = EF/2, the same law as the hybrid's leak (`scripts/select_specs.py` states and asserts
this). Total 1068 specs, `results/specs.txt` (sha256 recorded in the provenance file at run time).

**Curve statistics** (per arm, per rule r, using `abar_r(EF)` on the 11-point grid):

- `S_r = max over adjacent grid steps of [abar_r(EF_{i+1}) - abar_r(EF_i)] / Delta_r`: the share of the
  total rise carried by the steepest 0.1 step; `EF_step,r` = lower end of that step.
- `EF_50,r` = smallest grid EF with `abar_r >= abar_r(0) + 0.5 Delta_r`.
- A rule is **scoreable in an arm** if Delta_r >= 0.10, the EF = 0 run is compact (not escape, stalled or
  filler) and at least 6 of 8 seeds have a complete early fit at every EF >= 0.1.

**Calibration of S before freezing the cuts** (`results/calibration_sharpness.txt`, synthetic curves, rise
0.20, per-seed sd 0.03 and 0.05, 20000 draws, seed 20261028). On a 0.1 grid even a truly sharp transition
(logistic of width 0.05) has median S only about 0.43, because it straddles two steps; a first draft cut of
0.45 would have missed it. The rule is therefore on the **median of S_r over scoreable rules**
(M = median S_r), with cuts 0.40 and 0.28. At sd 0.03 this gives: sharp curves flagged sharp 88%, smooth
(linear, broad logistic) flagged sharp 0.0%, smooth flagged smooth 94-100%. At sd 0.05 smooth curves are
flagged smooth only 17-41% of the time (noise inflates S), so an "unresolved" outcome is the likely
failure mode of H-smooth, not a false "sharp". Cuts were fixed from this table and are not to be moved.

### Predictions (all scored on the committed output, none re-fitted)

Gates first. If G1-G2 fail nothing is scored; if G3-G4 fail the L-versus-R comparison (P4) is not scored.

- **G1 (replication).** The 102 `gate_hy` rows (EF = 0, 0.1, 1.0) are byte-identical to the committed
  wall-vs-memory Stage 1 `probe.csv` rows with the same labels. Deterministic code, so exact.
- **G2.** The 6 `ft:RULE:L` rows are byte-identical to the committed Stage 3 rows.
- **G3 (encoding law).** For EF in {0.5, 0.8}, `d_r = abar^fs_r(EF) - abar^hy_r(EF)`: |mean over rules of d_r|
  <= 0.02 and every |d_r| <= 0.04 (about three standard errors of a difference of two 8-seed means).
- **G4.** Same test comparing arm L at EF = 1.0 (SET of 10 R and 10 L) with arm R at EF = 1.0 (same law).
- **G5 (classifier).** `fit`/`classify` reproduce the Stage 1 classes of the 6 EF = 0, 6 EF = 1 conditions
  and the per-rule early a in the committed `runs.csv` of wall-vs-memory to within 0.0005.
- **Code oracle.** `cargo test --release --locked --test hybrid_walker --test fresh_set` passes (independent
  sparse references); recorded in the NOTEBOOK.

Scored predictions:

- **P1 (shape, arm R).** M >= 0.40: H-sharp; M <= 0.28: H-smooth; otherwise unresolved. If H-sharp with
  `EF_step` = 0.9 for the majority of rules: reported as H-endpoint and not interpreted. Prior as above.
- **P2 (location, arm R).** Median over rules of `EF_50` lies in [0.3, 0.7]. About 60%.
- **P3 (monotone, arm R).** In at least 5 of 6 rules every step of `abar_r` is >= -0.015. About 75%.
- **P4 (handedness, arm L vs R).** Among rules scoreable in both arms (expect 4 of 6): `|EF_50^L - EF_50^R| <= 0.1`
  in at least two thirds of them, and the arm-L reading of P1 equals arm R's. If fewer than 3 rules are
  scoreable, not scored. About 55%. A miss means the mismatch between the fresh-ground turn and colour 0 matters.
- **P5 (window drift, arm R).** `D_r = EF_50,r(k_end = 22) - EF_50,r(k_end = 16)`. Median |D_r| <= 0.1: no
  detectable drift; >= 0.2: drift; otherwise unresolved. Priors: drift 40%, no drift 30%, unresolved 30%.

Reading table (what each outcome would mean; interpretation is mine and tentative):

| P1 | P5 | reading |
|---|---|---|
| sharp | no drift | candidate threshold; go to Stage B |
| sharp | drift | threshold-like at these sizes, but position moves with territory size: finite-size effect to resolve |
| smooth | any | no abrupt feature at 0.1 resolution; a crossover. Test the scale-competition account (Q33) |
| unresolved | any | Stage B only if M >= 0.34; otherwise report as unresolved |

Descriptive, not scored: between-seed sd of a at each EF; within-rule coexistence cells (>= 2 compact and
>= 2 porous of 8 at one EF); share of intermediate runs; escape rate versus EF in both arms (does a small
leak break the forced-L highways?); beta curves; late-window a.

### Conditional Stage B and a deferred Stage C (not registered for running)

- **Stage B** runs only if P1 = sharp, or unresolved with M >= 0.34. A new dated registration, with the
  spec file committed first, is required: spacing 0.025 across `[EF_step - 0.1, EF_step + 0.2]`, **16 new
  seeds** (2026102901..16; fresh seeds so that the bracket, chosen on Stage A, is not also scored on
  Stage A's noise), arm R plus arm L if P4 was scoreable, at most 600 runs.
- **Stage C** (mediator, deferred, needs probe instrumentation): record the fresh-run length distribution at
  each EF and test whether the dose curves collapse on run-length scale over territory radius (Q33).

## Pruning-index preflight

- Index revision `1b14a1e7df1ba0ed1bce2fbe7f9e904e2cf4a047`. Commands:
  `rg --files notes/pruning-index/entries`;
  `rg -n -i -e fresh -e leak -e noise -e titrat -e dose -e threshold -e "EF" notes/pruning-index/entries`;
  and a read of the membership predicates of all seven entries.
- Candidates: `NR-20261026-wall-vs-memory-no-wall-porous` (exactly the 48 `hy:RULE:0:1:SEED` specs; it
  states that intermediate EF and forced-L perturbations are **not** excluded) and
  `NR-20261028-wall-vs-memory-bounded-random-fresh-compact` (exactly 196 `fs:` specs with sets RU and LU;
  it names a dose curve in the bound as the discriminating next test, not registered). The other five
  entries (additive laws, crawler window, kappa exposure, reflecting cup, excursion score) matched on incidental
  words ("noise gate", "fresh target").
- Scope comparison: no new spec is a member of either entry. The EF = 1 and EF = 0.1 rows and the forced-L
  rows (102 + 6 specs) repeat tested specs **deliberately**, as byte-for-byte replication gates, and as the
  anchors of the curve; the entry permits deferring such repeats, we run them to prove that this experiment
  uses the same instrument. The 864 `new` specs are untested conditions.
- Decision: **run**. Specs: `results/specs.txt` and `results/spec_roles.csv` (role per spec). No exclusions.
- Budget: one pass of 1068 runs of 2^27 steps, `RAYON_NUM_THREADS=3`, expected 15-30 minutes on 4 cores.
  Stage B or C only after a new registration.

## Reproduction

```sh
uv run --frozen python experiments/active/2026-10-leak-titration/scripts/calibrate_sharpness.py   # synthetic
uv run --frozen python experiments/active/2026-10-leak-titration/scripts/select_specs.py
cargo test --release --locked --test hybrid_walker --test fresh_set
RAYON_NUM_THREADS=3 sh experiments/active/2026-10-leak-titration/scripts/run.sh
uv run --frozen python experiments/active/2026-10-leak-titration/scripts/analyse.py
```

`run.sh` builds `probe` into a fresh `CARGO_TARGET_DIR` (stale-build trap, AGENTS.md), records commit, binary
sha256 and the specs hash, and writes `probe.csv`, `probe.log`, `provenance.txt` and `run.done`. As in
wall-vs-memory, the committed `results/` carries `run.done`, so the bare command skips; to re-simulate pass a fresh directory.

## What this cannot show

- **A universality class.** Even a sharp feature here would be a feature of a finite-window exponent
  estimate (early window ends at 2^22) for six rules from one class (core: blob, 0.30 < alpha_w < 0.37, not
  bursty), selected for compact growth under their own R turn. Assigning a class needs an order parameter
  with a definite scaling form, exponents from a finite-size collapse over several decades of territory
  size, and a model that says why. "Percolation" in particular is a property of connectivity in a
  quenched random medium; here the randomness is annealed dynamic noise on a self-generated territory, and "porous" is a
  growth-exponent class, not a cluster-connectivity statement. If a threshold appears, the percolation
  analogy is a hypothesis to test, not a label.
- That a(EF) is asymptotic: a shift of the window (P5) is the only size information in Stage A.
- Anything about other rules, backgrounds, the leak on revisited cells (EV), or colour-zero noise.

## Results, uncertainty and limitations

Appended below after the run, in order, never edited.

## Pruning-index outcome and next question

Pending the run.
