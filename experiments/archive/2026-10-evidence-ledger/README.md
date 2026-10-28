# Consolidating boundary-access evidence

Editorial audit started 2026-10-23 17:55 +13:00 at
`1461cb96bbc64c396344979d2e81a6f430a485d0`. No new simulations, fits or scientific
predictions. The task is to distinguish observation, failed explanation,
unresolved question and next decision using existing committed evidence.

Read the [compact ledger](results/ledger.md), the machine-readable
[catalogue](results/claims.json), and the [retrieval/access guide](../../../notes/evidence-ledger.md).
The catalogue is a **human-authored editorial dataset**, not generated measurements.
Numbers are quotations from the pinned sources; source recipes, seeds, windows,
controls and uncertainty remain authoritative. The audit snapshot is not a claim
that those results are the latest forever. No blanket classification or novelty
claims are made. A source's highway label is a finite-run observation here;
this audit did not register or run adversarial classification claims.

## Reproduce and query

From the repository root, using Python >=3.12 under uv (stdlib only):

```text
uv run --frozen --no-sync experiments/archive/2026-10-evidence-ledger/scripts/ledger.py validate
uv run --frozen --no-sync experiments/archive/2026-10-evidence-ledger/scripts/ledger.py render
uv run --frozen --no-sync experiments/archive/2026-10-evidence-ledger/scripts/ledger.py query --topic return-dynamics
uv run --frozen --no-sync experiments/archive/2026-10-evidence-ledger/scripts/ledger.py query --text eligibility --json
uv run --frozen --no-sync experiments/archive/2026-10-evidence-ledger/scripts/ledger.py facts
```

`render` creates only `results/ledger.md`; `facts` writes portable Prolog-style
ground facts to stdout (no inference engine). Query returns complete records,
including limits and references. Exact filters compose with AND; text search
is case-insensitive substring retrieval, not a membership or scientific test.
Validation checks IDs, reference integrity, pinned Git paths and catalogue schema.
It does not verify scientific truth. No new dependency or lockfile change.

## Source reconciliation

The supplied inventory is a candidate list, not evidence. Its attachment hash and
disposition are in NOTEBOOK.md; [inventory audit](results/inventory-audit.md)
records material corrections. In particular, the actual pruning entry is empirical
over its finite membership, not an all-length proof; the late-highway audit's final
appendix supersedes the seven-pending summary still present in older notes.

No sweep is proposed or launched. Pruning preflight at the audit revision:
`rg --files notes/pruning-index/entries`; read the sole entry
`NR-20261022-additive-laws-order-blind` in full. Decision: no transport pruning,
no new dead-end signature from this editorial audit. Any next experiment must
repeat preflight for its exact conditions and register predictions separately.

## Completion boundary

This is the initial transport-focused ledger, not an exhaustive project knowledge
base. Next decision: repair eligibility accounting and define competing predictions
before authorizing any new transport measurement. Index and database options in
the guide are architecture proposals; only JSON, Markdown, query and fact export
are implemented. Validation outcomes and environment limitations are in NOTEBOOK.md.

## Verification

Catalogue integrity checks, generated-view equality and fresh-kernel notebook
execution pass. Full `cargo test --release --locked -- --test-threads=1` passes
(exit 0; existing compiler warnings). Logs are in `results/`. No simulations or
source measurements were regenerated for this editorial task.

Blog preparation was attempted after adding this experiment's reader-guide row,
but six existing missing guide entries block it; see `results/blog-prepare.log`
and NOTEBOOK.md. A successful site build is not claimed. The ledger and query
interface can be used directly from the repository.
