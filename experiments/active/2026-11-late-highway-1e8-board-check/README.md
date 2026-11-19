# Late-highway board check for the (1e8, 1e9] decade

Created 2026-11-09 09:11 +13:00 on branch `agent/late-highway-1e8-board-check`, base `6fba1c80227eebfcd3f27fee78087dd6c973e0e8`.
Status: **REGISTERED, nothing run yet** (the recheck runs start only after this registration is committed).
Status update (2026-11-09 09:16 +13:00, appended): **done**; P1 and P2 held; see Results.

## Question and registered prediction

`notes/ACTIVE.md` lists as open: *apply the board-independence check to the 1e8/1e9 census*. The 2026-10-21/22 check
(`experiments/archive/2026-10-late-highway-board-check/`) found that 25 of 54 late highways in the (1e9, 1e11] decades were
board fillers on the 32768 board and one (`RLLLRLRRR`) a ray cut off by the board; the other 28 reproduced on a 65536 board.
The (1e8, 1e9] decade enters the per-decade yield comparison as **12/854 = 1.41%** (`notes/frontier-results.md` items 18-20,
`experiments/archive/2026-10-highways-unresolved-rules-1e10-1e11/results/highway_stats.txt`, Q19 in
`notes/open-questions-hypotheses.md`) but has not had the 65536 recheck.

**Source of the rule set (exact).** `experiments/archive/2026-10-census-sweeps/results/sweep_1B.csv` at commit `6fba1c8`
(the 854 length <= 10 survivors of the 1e8 census rerun to 1e9 on a 16384 board; `sweep_lean`-format CSV): the 12 rows with
a non-null `onset`, identical (checked by `scripts/specs.py`) to `results/1B_highways.txt`. The 16 other `escaped` rows have
no onset (chaotic blobs reaching the board at ~5.4e8, not counted as highways) and the 3 rows of `sweep_1B_extra.csv` have no
onset either; neither is part of this check. Rows copied to `results/census_rows.csv`.

**What the record already contains (found while preparing, stated before measuring).** `experiments/archive/2026-10-census-sweeps/results/confirmed_1B.csv`
is a `confirm` run (`src/bin/confirm.rs`: 8192 and 16384 boards, fast ant) on these 12 rules: 11 are
`confirmed=true` (same period, drift, onset on both boards); **`RLLRRLRLR` is `confirmed=false`** (period 4, drift (-2, 0) on
both, but onset 763,443,858 on 8192 vs 822,854,955 on 16384). The web page (`web/build.py`) uses only the confirmed 11, but the
yield 12/854 in `highway_stats.txt`, Q19 and `notes/frontier-2026-10-13-results.md` counts all 12. Also, one of the 12,
`RRRRRRLLLR`, has onset 98,645,078 < 1e8: it is in the decade "found by the 1e9 rerun" (the 12/854 count) but in (1e7, 1e8]
by onset binning (hence "11-12 by two binnings" in the Q19 update of 2026-10-25). The atlas line "The earlier sweeps have not
had the board-size check" is therefore half true: a two-board check exists for this decade, on small boards (8192/16384).

**Classification rule (frozen, reused from `experiments/archive/2026-10-late-highway-board-check/scripts/classify.py`).**
A census escape with a highway is a *board filler* iff `width >= 0.99 G` and `height >= 0.99 G`, with `G` = census board
(16384). Bookkeeping (not a prediction, computed from the committed CSV, same as line 76 of that experiment's
`classify.txt`): **0 of 12** rows meet it (largest footprint 9236).

**Recheck criterion (frozen, as B2).** Each rule is run alone from a blank board on a **65536 board** with budget = census
onset + 1e8 steps. It is *confirmed* iff the run reports the census `period`, `dx`, `dy` and `onset` exactly; otherwise
it is *board-dependent* (an artefact for the yield count). Implementation deviation from B2, decided before running: the box
has ~2.5 GB of free RAM, too little for the dense 65536 board (4.3 GB), so the primary run uses `sweep_lean` with
`TURMITE_GRID=tiled` (unlimited cache, tile 2^6), whose CSV is byte-identical to dense by construction and test
(`tests/tiled.rs`, `experiments/active/2026-10-tiled-grid-backend/DESIGN.md`). Secondary (not scored, a backend and third-board
cross-check): the same specs on a **dense 32768** board.

**Oracle / control.** `RRLRLR` (budget 1,176,356,698) must reproduce `experiments/archive/2026-10-late-highway-board-check/results/control_65536.csv`
(dense 65536: period 220, drift (2, -2), onset 1,076,356,698) exactly; on the tiled run this also checks tiled = dense at 65536.
If the control fails, no rule is scored. Also run once: `cargo test --release --locked` (includes the `fast`/`lean`/`tiled`
vs `reference` oracle tests).

**Mechanism and predictions.** A filler on a G board escapes at about `2(k+1) G^2` steps, >= `4 G^2` = 1.07e9 on the 16384
board, above this decade; and no row has a full-board footprint. So the 32768-type artefact cannot be in this decade.
The remaining artefact class is a board-truncated ray, and the record already flags `RLLRRLRLR` (speed-1/2 axis drift, onset
moved by 6e7 steps between boards) as the candidate.

- **P1** (confidence 90%): all 11 rules confirmed by `confirm` on 8192/16384 reproduce period, drift and onset exactly on
  65536. Fails if any of the 11 differs.
- **P2** (confidence 85%): `RLLRRLRLR` does **not** reproduce its census row on 65536 (different onset, or no highway within
  the budget). Fails if it reproduces exactly (then the 8192 run was the odd one out, and the 16384 census value stands).
- **Consequence registered in advance.** If P1 and P2 both hold, the (1e8, 1e9] count drops from 12 to **11** in the
  "found by the 1e9 rerun" binning (11/854 = 1.29%) and from 11 to **10** by onset binning; the flat-yield reading (Q19) is
  unaffected (one rule moves a 1.41% to 1.29%). If P1 fails for any rule, that rule is an artefact and the count drops
  further; a second artefact class at <= 1e9 would need its own investigation.
- **Competing explanation.** H-real-RLLRRLRLR: its highway is genuine and only the 8192 run was disturbed (the territory
  is ~8000 wide, so the 8192 board could truncate it); then P2 fails and the count stays at 12.

**Exploratory (not scored, decided before running).** If P2 holds, run `RLLRRLRLR` alone on the tiled 65536 board to 1e10
steps (cheap) and report what it does (escape, highway, footprint), without changing any count on that basis.

## Pruning-index preflight

- Index revision and search commands: `6fba1c80227eebfcd3f27fee78087dd6c973e0e8`; `rg --files notes/pruning-index/entries`
  (7 entries); `rg -n -i -e highway -e board -e onset -e filler -e census notes/pruning-index/entries`; `rg -l -F -w RULE`
  for each of the 13 rule strings in `results/recheck_specs.txt`. Titles and membership predicates of all 7 entries read.
- Candidate signature IDs: no matches (the keyword hits are in `NR-20261022-additive-laws-order-blind`, which excludes
  "any growth or highway question", and `NR-20261025-kappa-exposure-classes-exposed-edge`, a boundary-occupation objective
  on other rules).
- Scope comparison: no entry covers highway onset, board dependence or these rules.
- Decision: **run**. This is a deliberate replication (the 65536 recheck of an already-reported census row), needed to
  apply the same validity criterion to every decade of Q19.
- Run spec and exclusions: `results/recheck_specs.txt` (12 census rules + control), generated by `scripts/specs.py`; no
  exclusions.
- Compute/stopping budget: 1.3e10 steps primary + 1.3e10 secondary + 1e10 exploratory; the lean ant ran ~2e8 steps/s in a
  timing run on `RLR`, so well under one core-hour. Stop at the results; no follow-up sweep is implied.

## Reproduction

```bash
export UV_PROJECT_ENVIRONMENT=... UV_LINK_MODE=copy   # local environment choice
uv run --frozen experiments/active/2026-11-late-highway-1e8-board-check/scripts/specs.py     # results/census_rows.csv, recheck_specs.txt
bash experiments/active/2026-11-late-highway-1e8-board-check/scripts/recheck.sh              # results/recheck_{65536,32768}/RULE.csv + recheck.log
uv run --frozen experiments/active/2026-11-late-highway-1e8-board-check/scripts/classify.py > experiments/active/2026-11-late-highway-1e8-board-check/results/classify.txt
cargo test --release --locked
```

No seeds (blank-board deterministic runs; no random draws). Binary sha256 and commit in each `recheck.log`.

## Results, uncertainty and limitations

(Appended below after the runs; the registration above is not edited.)

### Results (appended 2026-11-09 09:16 +13:00; data commit `00fee4a4d76c904002ebd71904621bb44f399d8b`)

Runs: `scripts/recheck.sh` at registration commit `214377a`, `sweep_lean` built with `--locked` into a separate target dir,
binary sha256 `1ecc3e8d6bcbe351980fe98aaf72090cda39e4ea6fc427fc6bc0d51bf2ac7e0e` (`results/recheck_{65536,32768}/recheck.log`).
Every rule ran uninterrupted from a blank board, one per process. Wall time: 21 s for the 13 tiled 65536 runs (4 in
parallel), 2 min for the 13 dense 32768 runs (serial). Scored by the frozen `scripts/classify.py` -> `results/classify.txt`.

- **Control / oracle.** `RRLRLR` on the tiled 65536 board reproduces the dense 65536 row of the earlier experiment exactly
  (period 220, drift (2, -2), onset 1,076,356,698, footprint 33549 x 33401), and the dense 32768 run agrees too: tiled = dense
  at this board size, as the backend tests say. `cargo test --release --locked`: 227 passed, 0 failed (includes
  `tests/ant.rs`, `tests/probe.rs`, `tests/tiled.rs` oracle tests).
- **P1 held (11 of 11).** Every rule that `confirm` had confirmed on 8192/16384 reproduces period, drift and onset exactly on
  the 65536 board, and also on the dense 32768 board. The escape footprints are now ~33,000 (65536) and ~17,000 (32768) wide,
  i.e. the highway arm simply runs further on the bigger board.
- **P2 held.** `RLLRRLRLR` does **not** reproduce: on both new boards it has no highway by the budget (onset + 1e8 =
  922,854,955 steps; stop `budget`, footprint 12831 x 11947, identical on both boards). It is board-dependent and is removed
  from the count.
- **Bookkeeping as registered:** 0 board fillers (frozen footprint criterion).

**Corrected (1e8, 1e9] count** (`scripts/yields.py` -> `results/yields.txt`): **11/854 = 1.29%** in the "found by the 1e9
rerun" binning (was 12/854 = 1.41%), **10/854 = 1.17%** by onset binning (was 11). Against (1e9, 1e10] at 16/807 = 1.98%:
Fisher exact p = 0.33 (0.24 by onset binning); against (1e10, 1e11] at 12/732 = 1.64%: p = 0.67. The flat-yield reading of
Q19 is unchanged; one event moves within the Poisson error (sd ~3 per decade). The registered competing explanation
(H-real-RLLRRLRLR) is rejected.

**Exploratory (registered: `RLLRRLRLR` to 1e10 on tiled 65536)** (`results/explore/RLLRRLRLR_1e10_65536.csv`): it escapes
at 2,118,888,449 steps with "highway" period 4, drift (-2, 0), **onset 2,118,845,739**, footprint 33446 x 32563. So the census
onsets are 763,443,858 (8192), 822,854,955 (16384) and 2,118,845,739 (65536): the "highway" is a fast straight run (speed 1/2,
axis-aligned) that is detected only when it ends at the board edge; the reported onset is the start of the last run before
the edge. **Deviation (unregistered, exploratory, decided after seeing the 65536 escape):** the same rule on tiled 262144 and
1048576 boards to 1e10 steps (`results/explore/RLLRRLRLR_1e10_{262144,1048576}.csv`, about 50 s each) does not escape; both stop at
the budget with footprint 84683 x 83799 (identical on both boards) and `tail_period` 4 at the end, i.e. it is in a period-4 run
at that moment but the run does not continue indefinitely. Reading (interpretation, not tested): `RLLRRLRLR` is a ray emitter,
a growing structure that repeatedly launches period-4 straight runs which terminate, like `RLLLRLRRR` in the earlier check.
Its bounding box grows quickly (12.8k at 9.2e8 steps, 84.7k at 1e10, an apparent exponent near 0.8 from two points), so it
is not a cube-root blob either. Not classified further here.

**Limitations.** One board size beyond the census (65536) for the score, plus 32768 as a cross-check; a rule whose onset
depended on the board only above 65536 would pass. The B5-style `confirm` (two boards, fast ant) already existed for this
decade, so this check mostly adds a bigger board; the change in the count comes from the yield bookkeeping having ignored
`confirmed_1B.csv`, not from a new artefact class. `RLLRRLRLR` is not a highway on any board tested, but "never a highway" is
not shown.

## Pruning-index outcome and next question

No signature: nothing here is a dead end; the result is a corrected count and one rule reclassified as not-a-highway on
finite boards (a finite observation that cannot exclude a later highway). Next questions (not registered): what are
`RLLRRLRLR`'s period-4 runs (what do they run over, why do they stop), and is it the same class as `RLLLRLRRR`? Q19's
fourth-decade experiment (`experiments/proposed/2026-10-late-highway-fourth-decade/`) should use 11 (or 10 by onset) for this
decade.
