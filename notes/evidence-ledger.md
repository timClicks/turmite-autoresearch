# Evidence ledger and access guide

Initial audit: 2026-10-23. Start with the [compact claim ledger](../experiments/archive/2026-10-evidence-ledger/results/ledger.md).
It covers boundary occupation (BO), return dynamics (RD) and regime changes (RG).
The [JSON catalogue](../experiments/archive/2026-10-evidence-ledger/results/claims.json)
is the editable source; Markdown is generated. This is an editorial synthesis of
existing evidence, not a new experiment or an exhaustive project inventory.

## What the evidence currently licenses

Boundary accounting and uniform-reference calibration are useful instruments;
they do not explain boundary access. Prefix models predict within represented
families but the tested models fail on unseen families. Typical excursions and
time-weighted returns respond at different spatial scales under shuffling, yet
this does not identify the relevant field structure. Gate ranking remains
inconclusive, with unknown baseline eligibility. Regime diagnosis is prerequisite
to interpreting occupation drift: board effects have already changed census counts.

**Next decision:** before another confirmation study, require (1) complete
baseline eligibility accounting, (2) two explanations with distinguishable
predictions about time-weighted outcomes, and (3) an excluded pilot establishing
calibration, support and censoring precision. Keep fresh starts and whole families
reserved where relevant. No new sweep is proposed or registered by this ledger.

## Reading routes

| Reader's question | Read first | Then inspect |
|---|---|---|
| Does this explain cube-root growth? | BO-01, RD-02 | Accounting audit and first-passage corrections |
| What does kappa below uniform mean? | BO-02, BO-04 | Exact window/geometry baseline; seed-disjoint 2^26-step replication |
| Can the rule predict occupation? | BO-03, RD-01 | Family split and persistence comparator |
| Are long returns local? | RD-03, RD-04, RD-05 | Calibration, weighting, shuffle intervention and missing eligibility |
| Can excursion-duration shape tell diffusion from sweeping? | RD-06 | Compact-walker calibration of the collapse Score; pruning entry for the retired calibrators |
| Is the ant still in the modeled regime? | RG-01, RG-02, RG-03 | Censoring, second-board checks, calibrated windows |
| Can a null result justify skipping a family? | [Pruning index](pruning-index/README.md) | Exact membership, objective and evidence class; never this ledger alone |

The [inventory reconciliation](../experiments/archive/2026-10-evidence-ledger/results/inventory-audit.md)
explains why the supplied broad inventory was not imported as facts. It includes
the finite scope of the additive-law result and unsupported taxonomy claims.

## A small knowledge base now; indexed views when needed

The implemented interface is Git-backed JSON plus a CLI: see the
[commands](../experiments/archive/2026-10-evidence-ledger/README.md#reproduce-and-query).
It is sufficient for exact topic/verdict filters and full-record text retrieval.
No database service, embedding model or Prolog runtime is installed.

| Option | Useful for | Cost / failure mode | Decision |
|---|---|---|---|
| Markdown index and reading routes | Human orientation; linking from notes/blog | Summaries drift if copied manually | Implemented; generate claim rows from JSON |
| JSON plus stable IDs and pinned sources | Scripts, agents, reviewable changes, complete caveats | Human curation still required; finite initial coverage | Implemented; canonical editorial records |
| SQLite tables plus FTS | Ranked lexical retrieval and joins over many claims/evidence records | Derived index must be rebuilt when catalogue changes | Preferred next increment when substring search becomes inadequate |
| Semantic retrieval | Queries using unfamiliar terminology | Similarity can retrieve obsolete registrations without corrections | Defer; retrieve whole claim + scope + corrections, not isolated sentences |
| Prolog or Datalog | Joins over evidence, instruments, conditions and review needs | Closed-world negation can misread unknown as false; prose scope is not executable membership | Ground-fact export implemented; inference deferred until predicates are typed |
| Hosted graph/vector knowledge base | Multi-user query service across repositories | Operational overhead, permissions, provenance synchronization | No present requirement; retain portable source first |

These are design tradeoffs for this repository, not a benchmark or survey of
current products. JSON avoids duplicating assertions across several hand-edited
databases. A later SQLite build should have `claim`, `source`, `claim_source`,
`condition`, `amendment` and `relation` tables; derived indexes carry the catalogue
hash and schema version. Keep generated databases out of Git. First add typed
conditions for rule set, initial state, seed role, horizon, window, board,
estimator, calibration and censoring before automated cross-study comparisons.

## Logic access without overstating the science

`ledger.py facts` exports quoted ground facts such as
`claim('RD-05','return-dynamics','intervention','uninformative').`
along with observation, scope, limitations, next decision and pinned source facts.
It does **not** assert `false(sparse_gates)` or `true(cube_root_universal)`.
The export is Prolog-style text, not a database or a dialect-independent Datalog
program; adapt quoting/types to the chosen engine and test that adapter.

Example Prolog query after loading the export:

```prolog
claim(Id, 'return-dynamics', _, 'uninformative'),
limitations(Id, Limit), next_decision(Id, Decision), evidence(Id, Source).
```

A possible future positive-only review rule is:

```prolog
needs_review(Id) :- claim(Id, _, _, 'uninformative').
needs_review(Id) :- claim(Id, _, _, 'unresolved').
```

This derives a workflow item, never a physical conclusion. Do not implement
`may_skip` by absence of support or by a failed verdict: the pruning index has
stricter proof/membership rules. No automatic rule equivalence, neighborhood
inference, asymptotic extrapolation, or merging of patched starts with random
backgrounds. A registration is a historical event, not the current verdict.

## Update contract

1. Read the complete source, including appended corrections. Verify evidence
   exists at a full Git revision; preserve commands/seeds/windows in the source.
2. Keep a stable claim ID for the same scoped question. Record a new dated audit
   entry for a changed reading; a changed scope gets a new record. Do not erase
   prior experiment predictions or pruning amendments.
3. Separate `kind` (identity, calibration, prediction, instrument, intervention,
   observation) from `verdict`. `failed_explanation` names a rejected inference;
   it is not a declaration that every version of a mechanism failed.
4. Return scope and caveats with every search hit. A RAG chunk should contain the
   entire record, source revision and references. Related registrations and
   corrections should be linked with typed relations before larger-scale ingestion.
5. Validate source paths, regenerate Markdown, review the diff and commit together.
   Update ACTIVE and the homepage when the next decision changes. A source update
   is a review trigger, not automatic scientific truth.

Initial limitations: source revision is common to this snapshot; no correction
graph, structured measurement quantities, formal membership predicates or automated
source freshness checking yet. The catalogue preserves scope as text and exports
full records; it cannot soundly answer whether two experiments have equal conditions.
