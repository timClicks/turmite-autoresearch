# kappa and the square-loop trap (H-loop)

**Status (updated 2026-10-16 ~21:55 +13:00): instrument, tests and cohort run written/started; see Results at the bottom
(filled after the single analysis run). The registered predictions below are unchanged.**

**Cohort caveat (stated plainly).** The cohort here (the 300 fresh lead-stratified rules x seeds 601..608) is the *same* cohort in
which the lead effect on ln kappa was found and measured (parent, `+0.152` per lead step on the 176 stationary rules). Mediation tests on it
are legitimate (the question is "what carries the effect that exists in these data"), but they are NOT a replication of the lead effect and
cannot be read as independent confirmation of H-loop; any mechanism fitted here is fitted on the data that produced the phenomenon.
The only out-of-sample element is C3 (the parent's mutants, different rules), which is unpowered.

**Frozen analysis choices** (NOTEBOOK entry 21:58, committed before any loop data): the deciding P3 mediator is the *interior-only* loop-step
rate (loop steps on interior start cells / interior steps), not a boundary-based one (boundary-cell loop steps are boundary steps by
construction, so that mediator is nearly an identity with B/S); the all-loop-steps fraction and boundary-based variants are accounting only.
Pass rule, leads 1-4 check, and the ICC reliability rule are in that entry. Retention by lead is reported in every P2/P3 table.
Parent: `../2026-10-kappa-leadrun-fresh/` (leading-run effect on ln kappa; read its README first).
The hypothesis was first written in that folder's `NOTEBOOK.md`, entry "2026-10-16 20:45 ... question, intent",
before any loop measurement. The statements below copy it. Do not reword predictions after seeing data; append instead.
Causal follow-up (draft): `../2026-10-kappa-loop-surgery/`.

## Question

Why does a longer opening same-letter run ("lead" k: `R^k L...` or `L^k R...`) raise kappa = (B/S)/(P_end/A_end)
at fixed area? kappa is defined in `notes/kappa-mechanisms-2026-10-15.md`. The effect, on fresh stationary rules:
+0.152 ln-kappa per lead step [0.130, 0.174], concave (leads 1-3: +0.235), mean residual -0.15 (lead 1) to +0.42 (lead 6).

## Mechanism under test (H-loop)

On fresh (colour 0) cells an all-R lead traces the 2x2 loop O -> E -> SE -> S -> O (4 steps per lap), and each lap
raises all four cells by one colour. The loop persists while the four cells' colours are < k: k laps = 4k steps, until
the first L-turn breaks it. Young cells are the frontier. So a longer lead means more of the ant's frontier time is
spent circling in short loops, hence more boundary occupation (higher B/S) at the same area.
Derivation check (P1): `scripts/p1_sanity.py`, result `results/p1_sanity.txt`.

## Operational definitions (fixed before any code; do not tune after seeing data)

- **Loop step** at time t: pos[t] == pos[t-4] AND the four turns made at steps t-3..t are the same letter. A same-turn
  closed 4-path is exactly a 2x2 lap; pos-repeat alone also catches back-and-forth artefacts. Chirality-agnostic.
- **Lead-colour loop step**: a loop step in which all four cells entered in the lap had colour < lead (before the update).
  **Other loop step**: any other loop step (for example a lap inside a later same-letter run of the rule). This split is the specificity control.
- **Loop entry**: first loop step of a maximal run of consecutive loop steps. Report loop-step fraction and loop-entry rate.
- **Boundary step**: the probe's definition: the step starts on a cell with an unvisited 4-neighbour (`Region::on_boundary`, `src/probe.rs`).
- **Windows**: probe octave windows (2^k, 2^(k+1)]. Reported kappa is the **k = 26** window value
  (`experiments/_lib/analyse_probe.py`: KLO=20, KHI=26, `kappa=float(g["kappa"][-1])`); ln A uses k = 22.
  The instrument reports loop statistics for k = 20..26. Primary window for P2-P3 is k = 26; k = 22 and 24 are secondary.
  (The 20:45 notebook entry said only "the probe window"; this fixes it. See NOTEBOOK 20:58 `decision`.)

## Registered predictions (copied from the 20:45 notebook entry; thresholds are my design choices, not findings)

- **P1** (rule-only): on a blank board a lead-k rule's opening 4k steps repeat with period 4 exactly (100%).
- **P2**: loop-step fraction in the window rises monotonically with lead 1..6 on the fresh stationary rules (176 in
  `../2026-10-kappa-leadrun-fresh/results/fresh_rules.csv`), and within each ln A22 tertile Spearman(fraction, lead) > 0.5.
- **P3** (mediation): adding per-rule loop fraction to spline(ln A22) + lead removes >= half of the lead coefficient
  (same stationary rules; coefficient before is 0.152). An unchanged coefficient means loops are a symptom, not the carrier.
- **P4**: P(loop step | step on boundary cell) >= 2 x P(loop step | interior step).
- Kill/downgrade logic (registered): P2 fails => H-loop dead. P2 holds, P3 fails => loops are a symptom of lead.
  P2 and P3 hold, P4 fails => loops matter but not through boundary occupation: unexplained, say so.

**Added now, before any loop data (written after P1-P4, so flagged as later additions):**
- **C1 (specificity)**: P3 repeated for the *other* loop kind only. H-loop predicts the mediation fraction for other-loops is
  less than half that of lead-colour loops. If both mediate equally, "loop" is a generic recurrence proxy, not the lead mechanism.
- **C2 (identity caveat)**: loop steps on boundary cells are boundary steps by construction, so P3 partly restates B/S. Also run
  P3 with *interior-only* loop steps and with loop-entry rate. If mediation vanishes when boundary loop steps are excluded, report it as accounting.
- **C3 (mutation link)**: on the usable base/mutant pairs of `../2026-10-kappa-leadrun-fresh/results/mutant_pairs.csv` (exists only after
  that folder's `analyse_mutants.py` has run), the paired change in loop fraction should have the sign of d = ln kappa(mut) - ln kappa(base),
  Spearman > 0.3 over arms E and S pooled. Not powered; report whatever it is.

## Competing explanations the data should also be able to support

1. **Young-cell exposure / colour phase** (`notes/kappa-mechanisms-2026-10-15.md` section 2, `../2026-10-kappa-prefix-exposure/`):
   lead matters only because early colours are read most. Would predict loop fraction adds nothing beyond exposure of colours 0..k-1.
2. **Lead as proxy for composition**: R-count alone gained 0.29 vs lead 0.65 (parent L6), so composition is not the whole story; other prefix letters are untested.
3. **Survivor selection** (parent L5 failed): high-lead rules drop out more. Loop statistics on survivors inherit this.
4. **Generic short-period recurrence** (period 2/4/6 trapping of any kind, not tied to lead). C1 addresses this.

## How to evaluate (decision table)

| P2 | P3 | C1 | P4 | Reading |
|---|---|---|---|---|
| fail | any | any | any | H-loop dead at this scale. Write it up; add to `notes/open-questions-hypotheses.md` |
| hold | fail | any | any | loops correlate with lead but do not carry the kappa effect |
| hold | hold | fail | any | generic recurrence, not lead-specific |
| hold | hold | hold | fail | loops carry the effect, but not via boundary occupation as assumed: unexplained |
| hold | hold | hold | hold | consistent with H-loop, still observational. Proceed to `../2026-10-kappa-loop-surgery/` |

## Files

`PLAN.md` instrument and analysis spec. `SCHEMA.md` output columns. `HANDOFF.md` first steps. `NOTEBOOK.md` lab notebook.
`notebook.ipynb` executed write-up (built by `scripts/build_notebook.py`). `scripts/p1_sanity.py`, `scripts/run.sh`, `scripts/analyse_loops.py`. Sampler `examples/kappa_square_loop_sampler.rs`, tests `tests/kappa_square_loop.rs`.

## Commands (WSL, repo root)

```bash
export UV_PROJECT_ENVIRONMENT=$HOME/.venvs/turmite UV_LINK_MODE=copy
uv run experiments/archive/2026-10-kappa-square-loop/scripts/p1_sanity.py   # done: results/p1_sanity.txt
cargo test --release --test kappa_square_loop            # 7 tests: identity, calibration, 1-vs-6 threads
bash experiments/archive/2026-10-kappa-square-loop/scripts/run.sh cohort    # 16 min, dumps/loops_cohort.csv (bulk, gitignored)
bash experiments/archive/2026-10-kappa-square-loop/scripts/run.sh mutants   # 22 min, dumps/loops_mutants.csv (C3)
uv run experiments/archive/2026-10-kappa-square-loop/scripts/analyse_loops.py   # results/analysis.txt, .json, loops_per_rule.csv, c3_pairs.csv
```

## Results

P1 only: 240/240 rules (k = 1..6, both chiralities) repeat with exactly k laps (`results/p1_sanity.txt`, seed 20261016).
This confirms the hand derivation for the blank-board opening. It says nothing about the 2^26-2^27 window, where the
cells around the frontier are not blank and a pure lead-colour loop needs four cells all below the lead; how often that happens is what P2 measures.

### Results (single analysis run 2026-10-16 ~22:31 +13:00, git f26b6ef; `results/analysis.txt`, `analysis.json`; full reasoning in NOTEBOOK 22:45-22:48)

Cohort: 300 fresh rules x seeds 601..608, 2400 runs to 2^27 steps (board 8192), 176 stationary rules (the parent's analysis set). Sampler run
`scripts/run.sh cohort` (16 min), mutants `scripts/run.sh mutants` (22 min). **Window = probe-CSV k = 26 (t_end = 2^26)**, the window that gives the parent's kappa
(correcting the earlier text above which said "steps 2^26..2^27"; NOTEBOOK 22:36). Instrument checks before the run: 7 tests pass (identity to
`probe_walker` and to a store-the-whole-path reference, 300 ant + 256 walker proptest cases, blank-board traps, PersistentWalk exact fractions
q = 0.5/0.7/0.3 within 1.1 se, rotor exactly 0 loop steps (theorem), 1 vs 6 threads byte-identical); the sampler also reproduces the parent's probe rows
(area, perimeter, new_cells, boundary_steps, escaped) on all 14509 rows with k >= 21.

Retention by lead 1..6 (kept / stationary of 50 sampled): 37/34, 32/32, 35/34, 31/31, 28/26, 20/19.

| lead | n stat | total loop-step fraction | lead-colour loop fraction | interior loop rate M_int | mean resid ln kappa |
|---|---|---|---|---|---|
| 1 | 34 | 0.1587 | 0.00001 | 0.1597 | -0.209 |
| 2 | 32 | 0.1839 | 0.00024 | 0.1843 | -0.031 |
| 3 | 34 | 0.1661 | 0.00099 | 0.1660 | +0.008 |
| 4 | 31 | 0.1791 | 0.0039 | 0.1791 | +0.033 |
| 5 | 26 | 0.2016 | 0.0104 | 0.2010 | +0.157 |
| 6 | 19 | 0.2567 | 0.0163 | 0.2559 | +0.144 |

| prediction | verdict | numbers |
|---|---|---|
| P1 | held (before) | 240/240 blank-board traps |
| **P2** | **FAILED** | not monotone (lead 3 < lead 2); tertile Spearman +0.50 / +0.40 / +0.17 (need > 0.5 each) |
| **P3** (deciding: interior-only loop rate M_int) | **FAILED** | b1/b0 = 0.957 [0.907, 0.997] (need <= 0.5); leads 1-4: 0.981 [0.930, 1.033]; g = +0.024/SD [0.002, 0.044]; log/rank variants 0.957/0.966 |
| P3 accounting: all-loop fraction / boundary-loop rate | 0.955 / 0.727 [0.560, 0.913] | only the boundary-based variant removes anything (it is nearly B/S) |
| **C1** | **FAILED** | lead-colour interior rate: b1/b0 = 1.134 (wrong sign, g = -0.048/SD); other loops 0.959 |
| **C2** | **FAILED** | is P3 on the interior-only variant |
| **P4** | **FAILED** | median P(loop\|boundary)/P(loop\|interior) = 0.776 [0.579, 0.957] (needed >= 2) |
| **C3** | **FAILED** | 154 E+S pairs, Spearman(dM_int, d ln kappa) = +0.218 [0.061, 0.364] (needed > 0.3; unpowered) |
| Reliability | ICC(1) = 1.000 | between-rule sd 0.080, between-seed sd 0.0002: informative, not a noise-limited null |

**Reading (decision table row 1): H-loop is dead at this scale.** P2 failed, and every downstream test also failed. Loop steps are plentiful (16-26% of all steps at
every lead) but almost all of them are "other" same-turn 4-loops that are present at lead 1 and are determined by the rule (ICC 1.0), not by the seed; the lead-colour
laps that the mechanism is about rise monotonically with lead but are at most 1.6% of steps (8% of loop steps) even at lead 6, and their partial association with ln kappa at fixed area and lead is negative.
(CI added 2026-10-20, post hoc, `scripts/lead_share_ci.py` -> `results/lead_share_ci.txt`, bootstrap over rules: the 8% is 7.6% [3.2, 12.3] at lead 6, n=20 rules; 5.4% [3.4, 7.4] at lead 5; 2.3% [1.6, 3.0] over all leads. The ratio-of-means variant gives 6.3% [2.9, 10.2] at lead 6.)
Not shown: that loops of other shapes (period 6/8, mixed turns), or loops earlier in the run, play no role; and the lead effect itself is still unexplained. This is the cohort in which the lead effect
was found: mediation here is legitimate but is not a replication of the effect, and the single out-of-sample element (C3, parent's mutants) is unpowered.
`../2026-10-kappa-loop-surgery/` was not started (gate: P2 must hold).
