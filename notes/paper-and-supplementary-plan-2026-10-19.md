# Paper updates and supplementary datasets: plan (2026-10-19)

Written at 34fbf45 after a day of mostly infrastructure work. This is a plan and
a status check, not a result. Nothing here changes a claim in the paper.

## What happened on 2026-10-18/19

| Work | Kind | Status |
|---|---|---|
| `experiments/active/2026-10-gpu-probe` (P2, P4, script fixes) | engineering | P2 falsified at HEAD on its upper bound: 5.81x vs the registered 4.9x line. The earlier "3.84x, held" came from a stale binary and is superseded (not edited). P4 held (lane scaling). GPU output byte-identical to CPU `probe`; tests pass on a verified build. The 34% CPU slowdown against the old baseline is unexplained and unbisected. |
| `experiments/archive/2026-10-kappa-walker-reference` | science | Finished; interpretation in its `NOTEBOOK.md`. |
| `research-outputs/.../supplementary/rule-census` builder rewrite, `rebuild_figures.py`, `.githooks/pre-commit` | infrastructure | `build_rule_census.py --check` passes (4083 rows, 3512 census, 3055 analysed, blob median alpha_w 0.3326). |
| Paper accounting-identity audit (2026-10-16 wording changes) | editorial | In the working tree, uncommitted. |

### The one new scientific result

`kappa / kappa_unif(a, beta)` with each walker's own measured exponents
(8 seeds each, windows k = 12..22; rotor also k = 20..26):

| walker | ratio (between-seed sd) |
|---|---|
| rw | 1.277 (0.042) |
| pw:0.25 / 0.5 / 0.75 | 1.235 (0.026) / 1.316 (0.043) / 1.255 (0.056) |
| rotor k = 12..22 | 1.686 (0.035) |
| rotor k = 20..26 | 1.799 (0.033) |
| mean-field (earlier expt, not rerun) | 1.010 (0.009) |
| **ant census, single run per rule** | **median 0.814**, IQR 0.664-0.957, 5-95% 0.443-1.332 |

Registered predictions 1 (memoryless) and 2 (rotor) held. The registered
"memoryless reference near 1.16" premise was wrong: porous territories have
beta ~ 0.9, so kappa_unif is ~1.02-1.03. Reading: the ant sits below every walker
tested, including the uniform walker. Only the rotor is outside the ant's 5-95%
range, so the memoryless walkers do not discriminate. No mechanism is implied.

**Caveat on process.** An earlier working summary quoted halved kappas (ratios
0.62-0.90) from a stale `analysis.txt`; the probe CSV's `t` is the window end, so
the correct denominator is `t/2` (the first script took the window end as 2^(k+1)). The notebook has the correction entry. Those
halved numbers should not be quoted anywhere.

## Paper: what to change and when

- **Do not change** the abstract, the cube-root exponent, or any headline claim.
- **Add one calibration paragraph** where the paper compares kappa across walkers
  (`main.typ` ~L319-321 and ~L391): restate walker kappa as a ratio to each
  walker's own `kappa_unif(a, beta)`, next to the ant census distribution. The
  existing sentence "the ants' kappa is about half the rotor's" is consistent
  (0.81 vs 1.69-1.80). The memoryless kappa 1.3-1.45 in the text is consistent
  with 1.27-1.35 measured here.
- **Gate:** only after the user has read the walker-reference interpretation
  entry. Numbers should enter via a script in `research-outputs/` that reads
  `experiments/archive/2026-10-kappa-walker-reference/results/analysis.txt` or a CSV
  derived from it, not typed by hand.
- **Leave the GPU benchmark out of the paper.** It belongs in the experiment README.
- Commit the pending audit wording separately from any new science.

## Supplementary datasets (priority order)

1. **Walker-reference table.** One row per (walker, seed): `a, beta, kappa,
   kappa_unif, ratio` and the window set. Source: `results/probe_*.csv`; needs a
   producing script, a data dictionary and a home under `supplementary/`.
   Cheapest, and the data exists.
2. **Extended per-rule census** (`rule_census.csv`). Add kappa columns: the
   eight-letter prefix prediction, `kappa/kappa_unif` per rule, the growth clock.
   Add them in `build_rule_census.py` and its dictionary, not in figure scripts;
   the CSV is regenerated, never hand-edited. Most reusable artefact for others.
3. **Unresolved-rules list.** The `unresolved_le10` cases with one `probe` spec
   per rule and the command to reproduce. An open problem others can attack.
4. **Benchmark rules.** About 30 rules spanning blob, builder, highway and log,
   with seed-pinned expected outputs (area at 2^k, fitted exponent). Lets someone
   validate a new simulator without rerunning 4083 rules. The GPU probe is
   byte-identical to the CPU probe, so generation is cheap.
5. **Raw `area(t)` / edge series for the calibration set.** Only if a few MB;
   otherwise an external archive link. Do not commit bulk dumps.

All of these need: producing command, git commit, seeds and windows recorded next
to the data (AGENTS.md reproducibility rules 1-2, 6-7).

## Open items

- Cause of the CPU `probe` 681.6 s -> 912.5 s slowdown is unexplained.
- Plain `cargo test --release` was run on the verified build for the GPU work;
  it has not been rerun after any change made by this plan.
- Stray untracked files in the repo root (`notebook.ipynb`, `numbers_check.py`,
  `run_check.sh`) have no provenance in this plan and are not committed here.
- Proposed next experiment (from the walker-reference README): a noisy rotor
  (`nrotor:EPS`) with a ~ 2/3, beta ~ 1/2 and intermediate memory, to find where
  the ratio crosses the ant median 0.81. Not registered yet; needs a dated
  prediction before any run.
- The GPU-probe work (P2/P4) was committed by a parallel session as `a12ecd5`;
  the walker-reference results as `0169fee`. Nothing from step 1 remained to commit
  there.

## Status (2026-10-19, later)

- Dataset 1 done: `supplementary/walker-reference/` (4e09f65).
- Dataset 2 done in part: `rule_census.csv` gained `probe_kappa_unif`, `probe_kappa_ratio`,
  `kappa_stationary` (63 columns; the original 60 are byte-identical). The builder asserts the
  ratio quantiles equal `census_spread.txt`. The prefix-prediction and growth-clock columns were not
  added: those quantities exist only for rule sets other than the 4083 swept rules.
- Datasets 3-5 not started.
