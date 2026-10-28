# Loop surgery: does breaking 2x2 loops lower kappa? (causal test of H-loop)

**Status: CLOSED without running (2026-10-19). Gate failed: the parent's P2 failed (H-loop dead at this scale). Nothing was implemented, frozen or measured. The text below is the original draft plan, kept unedited for the record; its S1-S4 were never registered and make no claim.**
Depends on `../2026-10-kappa-square-loop/` (H-loop, operational definitions of "loop step", P1-P4 and the decision table). Do not run
this before that folder's P2 holds; if P2 fails the hypothesis is dead and this folder should be marked closed without running.

## Question

Observation cannot separate "loops carry the lead effect" from "high boundary occupancy creates more loops". An intervention can: suppress loop
completions in high-lead rules and see whether kappa falls toward the low-lead level, against a control that perturbs the same number of steps without targeting loops.

## Intervention (new walker, to be written: `src/walkers.rs` `LoopBreakAnt`, tested against a reference)

Ant with the unchanged rule, except: when the next step would be a loop step (the last three turns were the same letter and the
current cell would make the fourth equal turn close on the cell entered 4 steps ago), with probability `q` flip this turn. Flipping a turn
is a deterministic function of (state, hash(seed, t)), so runs stay reproducible and rayon-order independent.

Arms, all with the same rule set, seeds and `probe 27 8192` pipeline as the parent:
- **S (surgery)**: `LoopBreakAnt` at `q` in {0.25, 0.5, 1.0} **[choose after the instrument pilot]**.
- **N (noise control)**: flip one turn at random times at the *same mean per-step rate* as arm S measured in the pilot, not tied to loops. Matched on rate per rule, not globally.
- **M (mirror control)**: flip turns that would close a *non-loop* shape: any turn ending an alternating (L,R,L,R) four-step path closing on its start. Same rate matched; tests that the shape, not the closure geometry, matters.
- **0 (baseline)**: the unmodified ant (already in the parent's data for these rules).

Cohort: **[choose]** 8 rules per lead 1..6 from the 176 fresh stationary rules, chosen by a seeded draw stratified on lead and ln A22 tertile (seed 20261016),
8 background seeds 601..608. Drawn before any surgery run, list committed in `results/cohort.txt`.

## Draft predictions (to be frozen as `decision` entries in NOTEBOOK.md before any run)

Let d_S(r) = mean over seeds of ln kappa under S minus under 0, per rule, similarly d_N, d_M.
- **S1** d_S - d_N is negative for lead >= 4 rules (mean of per-rule differences, 95% CI upper bound < 0). Loop suppression reduces kappa beyond what generic noise does. ~45%.
- **S2** dose-response: (d_S - d_N) grows more negative with lead (slope of per-rule difference on lead, CI upper bound < 0) and with q. ~40%.
- **S3** specificity: (d_S - d_M) < 0 with the same sign test. ~40%.
- **S4** the share of the lead effect removed: [mean ln kappa of lead 5-6 rules under S] - [mean of lead 1-2 rules under 0] over the unsurgered lead gap (use parent residuals for the gap, 0.15 per step, concave) is >= 0.5 at q = 1. ~25%.
- Known issue: any perturbation changes growth regime (noisy-rotor kappa rose during crossover; `notes/kappa-experiment-design.md`). Perturbed rules may leave the stationary core band;
  retention by arm is reported (M4-style) and a dropped rule is not imputed. If retention differs strongly between S and N, S1-S3 are uninformative, not null.

## Interpretation table (draft)

| S1 | S3 | Reading |
|---|---|---|
| holds | holds | loops causally carry (part of) the lead effect |
| holds | fails | any trap-geometry breaking lowers kappa; loops not special |
| fails | any | loops are not the carrier at this resolution, or the intervention cannot separate them from noise; say which using the retention table |

## Commands

None yet. Needs: `LoopBreakAnt`, its test against a reference, a `probe` front-end spec syntax (for example `lbreak:RULE:SEED:Q`), then `run.sh` and `scripts/analyse_surgery.py`. See `PLAN.md`.
