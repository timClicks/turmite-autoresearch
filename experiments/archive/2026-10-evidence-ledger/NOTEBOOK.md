# Lab notebook

## 2026-10-23 17:55 +13:00 · intent · 1461cb96bbc64c396344979d2e81a6f430a485d0

Consolidate existing boundary occupation, return dynamics and regime evidence.
No new scientific measurement or registered prediction. Read ACTIVE, accounting
audit, calibration, kappa mechanisms, first-passage corrections, boundary-return
map, single-cell gate notebook, prefix-family holdout, uniform baseline, tail
budget and final late-highway board audit. Preserve historical registrations.
Unrelated sweeper-generalisation work is active and must remain untouched.

## 2026-10-23 17:56 +13:00 · observation · 1461cb96bbc64c396344979d2e81a6f430a485d0

Source corrections change the synthesis. First-passage P1/P3/P4 are uninformative,
not evidence for tail exponents or closure. Single-cell gate baseline eligibility
is unknown. All seven formerly pending late-highway rechecks finished in the final
appendix. The pruning signature explicitly labels its finite census empirical and
the all-n derivation unchecked, despite stronger wording in some summaries.

## 2026-10-23 17:57 +13:00 · decision · 1461cb96bbc64c396344979d2e81a6f430a485d0

Use a small human-authored JSON catalogue, deterministic Markdown rendering and
stdlib query/fact export. Keep verdict, epistemic kind, scope, limitation and next
decision separate. A failed instrument is not a failed mechanism. No logic rule
may convert missing evidence to falsity or an empirical result to permission to
prune. Pruning index read in full; sole match is additive-law signature, which
does not exclude transport work. No sweep or new dead-end entry.

## 2026-10-23 18:02 +13:00 · observation · 38a58985a5166463da74a0c35a242816b98a394a

Catalogue validation passes: 11 claim records, 21 pinned source paths. Focused
checks pass for composed filters, case-insensitive retrieval, empty results,
duplicate-ID rejection, missing-reference rejection, missing-caveat rejection,
Markdown equality and complete fact-export caveats. The notebook's stdlib cells
execute top to bottom in a fresh namespace; no Jupyter kernel integration is
claimed. Initial authoring execution preceded the first commit; repeated after
38a5898, now reading the committed catalogue, with identical saved outputs.

Attachment SHA-256:
`cb9f6fb5b1604a7e8deddc2220b9907635b868a2662be16b08ec45675c7faa71`.
It is a candidate inventory only; no attachment-only scientific assertion was
imported. Reconciliation is in results/inventory-audit.md.

Local verification used uv 0.9.0 / CPython 3.12.11 with
`UV_CACHE_DIR=F:\Code\turmite\target\uv-cache` and
`UV_PROJECT_ENVIRONMENT=F:\Code\turmite\target\evidence-venv` (local provenance,
not contributor setup). Commands: `uv run --frozen --no-sync` followed by
`experiments/archive/2026-10-evidence-ledger/scripts/ledger.py validate`, `render`, or
`experiments/archive/2026-10-evidence-ledger/scripts/check.py`. No dependencies added.

## 2026-10-23 18:05 +13:00 · deviation · 38a58985a5166463da74a0c35a242816b98a394a

Blog preparation (`uv run --frozen --only-group blog blog/scripts/experiments.py`,
WSL, existing project environment) fails on reader-guide coverage. Added this
experiment's entry; six pre-existing gaps remain: falsification-harness,
falsify-adaptive-search, invariant-mining, invariant-mining-snf, single-cell-gates,
and sweeper-generalisation. results/blog-prepare.log records the failure. No
successful full site render/build is claimed; unrelated guide entries were not
invented to bypass validation.

Release tests launched in WSL using `CARGO_BUILD_JOBS=1 RAYON_NUM_THREADS=1
CARGO_TARGET_DIR=/home/tim/turmite-target cargo test --release --locked --
--test-threads=1`, log results/release-tests.log. Three unrelated sweeper jobs
were active, so no timing claim. Simulator and estimator sources unchanged by
this audit. Completion result will be appended.

## 2026-10-23 18:06 +13:00 · observation · 38a58985a5166463da74a0c35a242816b98a394a

The actual Jupyter clean-kernel execution also passed (exit 0): in WSL,
`UV_PROJECT_ENVIRONMENT=/home/tim/.venvs/turmite uv run --frozen --no-sync python
-m nbconvert --to notebook --execute --inplace
experiments/archive/2026-10-evidence-ledger/notebook.ipynb`.
See results/notebook-execution.log. This supersedes the earlier limitation to
stdlib namespace execution; it does not resolve the separate blog coverage failure.

## 2026-10-23 18:08 +13:00 · decision · 38a58985a5166463da74a0c35a242816b98a394a

`cargo test --release --locked -- --test-threads=1` completed with exit 0; no
failures (181 tests passed), existing compiler warnings retained in results/release-tests.log.
Focused integrity checks and fresh-kernel notebook execution passed. Markdown
was generated from the committed catalogue and no source measurement was rerun
or edited. `git diff --check` passes for these changes. A concurrent Lean-only
commit advanced HEAD during verification; the ledger evidence snapshot remains
pinned at 1461cb9 and the initial editorial commit is 38a5898.

Initial consolidation is complete. The full blog build remains unverified
because preparation stops at six existing reader-guide omissions; the ledger's
guide row is supplied. No new sweep, mechanism assertion or pruning exclusion.
Next work is the discriminating-test feasibility decision in ACTIVE, not an
unbounded database project.

## 2026-10-23 18:09 +13:00 · deviation · 7e14934

Final staged whitespace checking reports one trailing blank line in the raw
compiler/test log. The earlier clean-check statement applies to authored files,
before that log was staged. Preserve the raw log rather than editing captured
test output; this is a formatting warning, not a test failure.

## 2026-10-25 22:25 +13:00 · decision · 2bacfc924204df411019fec9b4b1a4b1d79de616

Turmite Research Agent (AI research agent), appended. Added **BO-04** (boundary-occupation, calibration,
supported): the eight mean-field calibration runs of `experiments/archive/2026-10-kappa-exposure-classes`
(seeds 1..8, 2^26 steps, board 8192, k = 17..26) give window-mean probe kappa 1.110, SD 0.007, range
1.102-1.120, against BO-02's 1.118 (SD 0.009, seeds 2026101601..08, 2^23 steps, k = 12..22). This is a
seed-disjoint, longer-horizon replication of BO-02's numeric reference only. BO-02 itself is unchanged.
The exposure experiment's other results do not count as independent support. Its P1 is uniform
by construction, and P2b uses 1.105 as an input. BO-04 is post hoc and uses the same algorithm and probe
definitions; its limits are in the record.

Re-pin: `source_revision` 1461cb9 -> `2bacfc9`, the first branch commit that contains the review sources.
Before re-pinning, `git diff --stat 1461cb9 2bacfc9 -- <all 21 prior source paths>` was empty: every
previously cited file is byte-identical, so the earlier claims still quote the same text. Only BO-04 and its
three new sources were reviewed now. The other 11 records were not re-reviewed, and `reviewed_at` dates this
addition only. `2bacfc9` is a branch commit, so the PR must land with a merge commit (not squash or rebase) for
the pinned links to resolve. `ledger.py validate` (12 claims, 24 paths), `render` and `scripts/check.py` pass;
`notebook.ipynb` outputs were refreshed by check.py. `notes/evidence-ledger.md` reading route updated.
