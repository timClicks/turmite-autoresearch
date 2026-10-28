# Reproducibility audit: hash-order dependence in seeded analysis scripts (2026-10-28)

Claude (AI research agent). Triggered by the non-reproducible bootstrap in
`experiments/archive/2026-10-kappa-matched-area/scripts/matched_area.py` logged in `notes/ACTIVE.md`.

## The flaw

polars returns `group_by()` groups and `unique()` rows in an order that changes from process to process (hash
order), unless `maintain_order=True` or the result is sorted. Python sets of strings iterate in an order set by
`PYTHONHASHSEED`. When that order decides which unit a seeded draw lands on (a bootstrap over rules, a
permutation null, `rng.choice` over a list), or breaks a tie, a script with a fixed seed gives different numbers on
every run. That violates AGENTS.md rule 1 ("no hash-order dependence"). Point estimates are unaffected (they do not
depend on order beyond floating-point summation); intervals, p-values, flag counts and tie labels are.

## Method

All 98 Python scripts under `experiments/` and `research-outputs/` that combine a seeded RNG (or shuffle/choice)
with `unique`/`group_by`/`partition_by`/`set(` (a grep, so a superset of the risky ones; `matched_area.py` had
already been fixed and was excluded) were run twice in separate processes, with `PYTHONHASHSEED=1` and `2`, in a
disposable git worktree of `4fd558bf` (the tree was restored after every run). Stdout and every file written were
compared byte for byte, and also compared with the committed outputs. Harness: scratch-only (`audit.sh`,
`compare.py`), not committed; the CI guard below is the committed form.

## Outcome

| result | scripts | what |
|---|---|---|
| identical in both runs | 51 | no action |
| **differed, numbers changed, fixed** | 12 (+ `matched_area.py`) | `a4_stats`, `a4c_stats` (bootstrap SE, 3rd decimal); `a7_census` (flag count, see below); `b3_stats` (bootstrap SE); `k1_necklace` (permutation null); `colour_stats` (C3 sampling floor 0.465/0.466); `hull_stats` (rule-bootstrap CIs, endpoints by <= 0.02); kappa-exposure `explore` (median-Q CI); kappa-prefix `ablate`, `additive`, `runs`, spread `features` (CIs, endpoints by <= 0.015) |
| differed, tie label only, fixed | 1 | `a5_home_types`: which of several equal-F1 values is printed; every count and F1 unchanged |
| differed, print order only, fixed | 2 | crawler `stage2_analyse` (dict order), return-gates `analyse_confirm` (strata list order) |
| differed, benign, not changed | 6 | wall-clock timing fields (`calibrate_tail`, `calibrate_fit`, `t1_machinery`); random cell ids in three `build_notebook.py` (exposure classes, leadrun-fresh, square-loop; the wall-vs-memory builder now sets fixed ids) |
| could not run here | 26 | see below |

Fixes sort the groups or lists before any draw (`sorted(df.group_by(k), key=...)`, `.sort(k)` after `agg`,
`unique(..., keep="first", maintain_order=True)`, `sorted(set_of_str, key=repr)`). Every fixed script is
byte-identical under both hash seeds, and its committed output was regenerated (commits `4fd558b`, `d60e0f4`,
`54a013b`, `3d245c8`, `6e3dc8a`, `ca7a3d5`).

**No registered verdict changed.** One interpretation weakened. In A7-next (`notes/frontier-2026-10-13-results.md`), the
flagged count was 18 in the note, 20 in the committed file and 19-20 on fresh runs. The deterministic value is
17 of 239. In the unbiased random sample it is 4 of 99, which is consistent with the 2.5% chance rate
(P = 0.24), not "about double". A correction has been appended there. Corrections were also appended to the
`kappa-matched-area` README and NOTEBOOK. The cached `hull-width` and `kappa-matched-area` notebooks were
re-executed.

**Paper numbers.** `research-outputs/cube-root-growth-paper/compute_numbers.py` was deterministic in both runs. No
script under `research-outputs/` reads the affected results, except `focused-papers`, which cites
`kappa-prefix-family-holdout` (not affected).

### Not runnable in this checkout (26), and static review

- Needs gitignored dumps or scratch (17): boundary-return-map `analyze`; c-law-mechanism `stage4_analyse`; `e1_rot_alignment`;
  `e5_stats`; kappa-first-passage `analyze`, `p3_pooled`, `p4_test`; kappa-growth-clock `analyse`; kappa-leadrun-fresh
  `analyse`, `followup`; kappa-prefix-decode `decode`; kappa-rule-space `prefix_audit`, `w3b_analyse`, `w3c_analyse`,
  `w6m_analyse`; kappa-square-loop `analyse_loops`; knockout-maps `followup_stats`.
- Inputs empty without scratch data (2): kappa-prefix-exposure `confirm_analyse`, kappa-tail-budget `confirm_analysis`.
- Needs arguments (2): `_lib/calib_kd.py`, `_lib/lawmod.py`.
- Refuses to overwrite a differing committed design (3, a safety guard working as intended): c-law-renewal `prepare`,
  `analyse_native`; kappa-growth-clock `sample`.
- Hard-coded machine path (1): `cube-root-growth-paper/textbook_figs.py` reads `/root/gal/...`.
- **Broken by the 2026-10-14 migration (1 here, 7 in the repository)**: `experiments/_migration/fixups.py` wrote the literal text
  `parents[2 if lib else 3]` into seven knockout-maps and patterns-fields scripts, which then raised `NameError` on start.
  Repaired at `cc75e51` (`parents[4]`, checked to resolve the repository root; `followup_stats.py` also needed
  `experiments/_lib` on `sys.path`). They now run until they need their gitignored dumps, so their outputs were not
  regenerated. Two of the seven were in the audit: `patterns_analyse` (counted here) and `followup_stats` (counted under dumps, which it needs once repaired).

Static reading of these 26 (no execution): one **possible hazard**, `boundary-return-map/scripts/analyze.py`. It
iterates `rep.group_by(["rule", "band"], maintain_order=True)` over a frame built by polars joins, whose row order is not
guaranteed, and the iteration feeds a seeded permutation null (`rng.permutation`). Its committed `results/` may not
regenerate byte for byte. Fixing it needs the dumps so the change can be checked, so it is left as found. The others
take their row order from sorted lists, `np.unique` (which sorts), CSV order, or left joins onto a fixed frame, and look
safe on reading. That is not a test.

### Deterministic, but differing from the committed file

Most differences are provenance: the recorded commit, and paths renamed by the 2026-10-14 and 2026-10-28 restructures.
Others are last-digit floating-point changes from summation order in polars aggregations (e.g. 0.39500088592542004 →
…015; `single-cell-gates` `gate_mean`), with no printed number changing. One is a provenance curiosity:
`kappa-tail-budget` results record an input sha256 `b4363b71…` that never existed in git. It is the hash of the committed
`pilot_tailbins.csv` with CRLF line endings, so the input was hashed on a Windows working copy before git's `eol=lf`
normalisation. The content is the same.

## Guard

`.github/scripts/check_python_determinism.py` (in the "Small reproducibility checks" workflow and `.github/CI.md`)
runs six fast seeded scripts under `PYTHONHASHSEED` 1 and 2 and fails on any byte difference. A negative control was
checked: the guard flags the pre-fix `matched_area.py` (`fc9e625`). New scripts should sort before any seeded draw;
`experiments/active/2026-10-wall-vs-memory/scripts/analyse_stage3b.py` and `analyse_stage3c.py` are examples.

## Not done

- The 17 dump-dependent scripts were not executed, so their committed outputs are unverified by this audit.
- The `boundary-return-map` hazard is unconfirmed and unfixed.
- Benign differences (timing fields, notebook cell ids in three older builders) were left as they are.
