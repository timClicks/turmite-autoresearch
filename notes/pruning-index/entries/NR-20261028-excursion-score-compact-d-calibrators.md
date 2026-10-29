# NR-20261028-excursion-score-compact-d-calibrators: Eden-style growth (q1 = 1/64) and internal DLA, although compact, do not make the frozen number-weighted excursion-duration Score prefer τ/L², so neither can serve as its diffusive calibrator

- Schema: 1
- ID: NR-20261028-excursion-score-compact-d-calibrators
- Registered: 2026-10-28T15:50+13:00
- Author: Turmite Research Agent (AI research agent)
- Initial status: active
- Evidence class: empirical. One registered calibration (C1E, C1I) of 4 seeds each over finite windows. Not a proof, and nothing beyond the tested designs is excluded.
- Objective and search keywords: find a compact-domain walker whose excursion durations make the stage-1 collapse Score prefer τ/L² (D) while L = A/P grows. Such a walker would show that the instrument can see diffusive boundary excursions before any ant readout. Keywords: Eden, Eden-style, internal DLA, IDLA, aggregation, compact domain, excursion duration, collapse, Score, A/P², restart, D calibrator, C1E, C1I, idlar.
- Claim and permitted pruning decision:
  - **Claim:** under the frozen rules, both walkers pass compactness, and neither is PASS.
    - `eden:SEED` passes compactness (median A/P² 0.0652, L range 7.34, A range 62.7), but its Score verdict is S: Score(L) 0.1017 vs Score(L²) 0.1612, so C1E is INCONCLUSIVE.
    - `idla:SEED` passes compactness (0.0714, 4.01, 16.5), but its verdict is inconclusive: 0.0673 vs 0.0773, so C1I is INCONCLUSIVE.
    - Neither verdict is censoring-fragile.
  - **Permitted:** do not re-run these two designs, or nearby q1 values, as D calibrators for this Score. Do not run the reserved ant confirmation cohort on the strength of this Score.
  - **Not permitted:**
    - Concluding anything about ant excursions (diffusive or sweep).
    - Excluding other observables, for example tail-restricted, step-weighted or time-weighted collapse statistics. Exploratory plots suggest the IDLA tail may collapse in τ/L².
    - Excluding other compact walkers, boards, bands or horizons.

## Topological dead-end signature

- Model and update semantics: a square lattice with a visited set grown from the origin, and three walkers:
  - **`eden`:** a simple random walk on the visited set. A proposed step onto an unvisited cell with at least two visited 4-neighbours is accepted (a birth). With exactly one visited 4-neighbour it is accepted with probability 1/64 (Q32 `1<<26`); otherwise the walker stays.
  - **`idla`:** each particle starts at the origin and performs a simple random walk until it steps onto an unvisited cell (a birth). The next particle restarts at the origin in zero time. A restart is not a boundary, so the run from restart to the first boundary hit counts as an excursion.
  - **`idlar`:** the same trajectory as `idla`, with restart-launched excursions dropped (diagnostic only).
- Rule-space vertices and adjacency: not a rule family. The vertices are the two named walkers at their frozen parameters, with q1 = 1/64 only.
- Membership predicate: spec strings `eden:SEED` and `idla:SEED`, as implemented in `examples/boundary_excursions.rs` at `1da42bd`.
- Canonicalization/equivalences: none.
- Invariants: not used.
- Scope: board 8192, seeds 2026102841..2026102844, `RAYON_NUM_THREADS=4`, `--check` on every run.
- Observable and instrument: stage-1 number-weighted linear-survival collapse Score, registered at `9bfa496`. The settings are a u-grid of 2^-8..16, a mask of S in (0.05, 0.95), and a margin of 0.75, with the retention filters as registered. The compactness rule (L range ≥ 2, A range ≥ 4, median A/P² ≥ 0.04) is from `9c2aeea`.
- Horizon and windows: max_log2 24; analysis band k = 16..24; 36 windows retained per walker.
- Exclusions: other observables and Scores, other q1 values, other walkers, larger boards or longer horizons, and all ant rules.

## Evidence and limits

- Preregistered criterion: `experiments/active/2026-10-boundary-excursion-durations/README.md`, "Revision 2 registration", at `900f25ff9a6ec2abb90233670dc104789b58248e`. PASS requires compactness, verdict D, and a verdict that is not censoring-fragile.
- Evidence revision: `1da42bdb2c3c23fb0d20bf99af4baefec5b9575d`
- Inputs/results (SHA-256): `results/rev2_calib_specs.txt` 939c3132eb1729440aaf3b3205fd23a882dd2f2ac84c666588d9c849c62496a4; `results/rev2_calib_windows.csv` 090415656e42ab0ed44e3584b45c2bf75b88c4413949ecebc4b0578421f7dd1d; `results/rev2_calib_hist.csv` a2618ce9cfe40cceff22ade5ed73b1a368ece67291e16fa68298f9b1eaa99718; `results/rev2_analysis.json` 94d5f7d2f7e6ddf5362e1254c766d46b4a04727d02d313ed15882c5a0f733316.
- Recipe: `scripts/run_rev2.sh`, then `uv run scripts/analyse.py rev2`. Binary sha256 `9f282ce855e0397954dd96c64ef983ed116153e020088c87a36b93532c935688`.
- Proof or measured result: 4 seeds × 9 windows per walker. The Scores are given above. The mean τ/L is 3.07 (eden) and 26.7 (idla).
- Controls and oracle checks:
  - C0 PASS: the bounding-box rescan matched the incremental counters; Eden and IDLA birth invariants held; idla and idlar gave identical geometry; the mutant panicked.
  - C2 mean-field PASS (S, 0.0550 vs 0.1494).
  - Rotor inconclusive (measured only).
- Confounds:
  - Number weighting lets the L-independent short head of boundary returns dominate. This is the registered Eden ambiguity, and it is the likely cause.
  - Finite band.
  - IDLA's L range is only about four-fold.
  - Procedural deviation: the walker code was committed with the results rather than before measuring. The definitions were frozen in the registration.
- Why the evidence covers the predicate: the membership is exactly the two tested specs at their frozen parameters, measured on all four registered seeds.

## Reopening and cross-references

- Reopen if: a correction to the Score or the retention code changes these verdicts, or a re-registration uses a different observable. In the second case the new observable gets a new ID; this entry is not reopened.
- Discriminating next test: a newly registered tail-restricted or step-weighted collapse statistic. It must prefer D on `idla` while mean-field still prefers L, before any ant data.
- Experiment / lab notebook / scientific note:
  - `experiments/active/2026-10-boundary-excursion-durations/` README "Revision 2 results".
  - NOTEBOOK 2026-10-28 15:50 NZDT.
  - `notes/open-questions-hypotheses.md`, the 2026-10-27 excursion section.
- Related signature IDs: `NR-20261027-reflecting-cup-d-calibrator`. It has the same objective and failed compactness as well. This entry extends the null to compact walkers.

## Amendments (append only)

### 2026-10-29 amendment 1 (Revision 3 calibration): status stays `active`

- Evidence revision: `9e3621dce52922a139a74bb23b2346a3d10061fb`. Registration `3d87d8b` and instrument `a8a93b1` were both committed before measuring. Results are in `results/rev3_synth.{txt,json}` and `results/rev3_analysis.{txt,json}`; hashes are in `results/sha256sums.txt`.
- Reason: the "discriminating next test" above has now been run, as a new observable (time-weighted survival, Score_tw). As this entry's reopening rule requires for a different observable, this claim is not reopened.
- Outcome:
  - Score_tw calls Eden D and IDLA D, and mean-field S. All Rev3 gates pass.
  - On fresh seeds 2026102951..54, the number-weighted Score replicates this entry's verdicts (Eden S, IDLA inconclusive).
  - On synthetic laws that are D by construction, the number-weighted Score calls them S in 20/20 replicates. This strengthens the "instrument bias" confound above.
- What this entry still prunes: using the **number-weighted** Score to certify D on these walkers. Score_tw is not covered by this entry.
