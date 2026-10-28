# Literature review plan for cube-root growth

Written 2026-10-15 NZDT, base commit
`da88e61b690507526ba4e2a2c017d9c7941beb91`; working tree contains uncommitted
research and manuscript changes. This is a plan, not a completed review or a
registration of new numerical experiments. The source checks motivating it
were a preliminary spot check in the accompanying discussion.

## Purpose and decision

Do a focused literature review before submission. The empirical census is
substantial enough to motivate a paper, but its novelty and relation to nearby
models need a stronger audit. Prioritise that audit before another broad sweep.

The review must answer three questions:

1. Has growth of non-highway generalised Langton-ant territories already been
   measured, under this name or another?
2. Which existing mechanisms or mathematical arguments could explain the
   observed growth and, especially, boundary occupation and its rule dependence?
3. What comparisons are needed to interpret the wider ant boundary without
   prematurely assigning an interface universality class?

Start from the current [manuscript](../research-outputs/cube-root-growth-paper/main.typ)
and [bibliography](../research-outputs/cube-root-growth-paper/refs.bib), the original
[cube-root hypothesis](cube-root-hypothesis.md), and the current
[research avenues](paper-gaps-research-avenues-2026-10-15.md). Preserve the original
hypotheses and failed predictions; append corrections rather than rewriting them.

## 1. Audit the closest prior work and novelty claims

Search beyond the phrase "Langton's ant": generalised/generalized ants,
turmites, flipping rotators, cyclic scatterers, Lorentz lattice-gas cellular
automata, Eulerian walkers, and rotor walks/rotor-router walks. Search each
with growth, range, visited area, subdiffusion, occupation, and transient.

The initial reading list is:

- Langton (1986), Gale et al. (1995), Bunimovich and Troubetzkoy (1992),
  and Gajardo and collaborators (2001, 2002), already in the bibliography.
  Check the precise scope of unboundedness and complexity results as well as
  any quantitative observations and references they contain.
- [Boon, *How fast does Langton's ant move?*](https://arxiv.org/abs/cond-mat/0004331).
  The abstract concerns the ordered highway's speed. Read the full paper and
  trace relevant citations; distinguish that question from blob growth.
- [Mishra et al., *Subdiffusion, Anomalous Diffusion and Propagation of a Particle
  Moving in Random and Periodic Media*](https://arxiv.org/abs/1509.06481)
  (published 2016). This missing comparator reports a subdiffusion exponent
  of 2/3 and transient subdiffusion before propagation in periodic media.
  Establish the exact displacement estimator, averaging convention, initial
  configurations and time windows before comparing with our territory growth.
- The cyclic-scatterer and flipping-rotator papers cited by these sources,
  followed by papers citing them. Treat theses and surveys as discovery aids;
  substantiate technical claims from original papers.

For every close comparator record the lattice, local state update, dependence
on incoming heading, initial medium, randomness, observable, run horizon,
averaging, uncertainty and claimed asymptotic status. Establish actual model
equivalence where possible; similar names alone do not establish equivalence.

Keep distinct: visited area/range, bounding-box width, territory gyration
radius, particle displacement, mean-square displacement, and time-averaged
displacement statistics. A displacement-squared exponent of 2/3 does not by
itself establish area growth of 2/3 or our bounding-box exponent of 1/3.

**Decision:** retain, narrow or remove the introduction's statement that we
found no published measurement of non-highway territory growth. A scoped
negative search result must name the model and observable and be supported by
the search record. If earlier work contains the headline result, state it
plainly and reposition the contribution around what the census, calibration,
controls and transport measurements add.

## 2. Review mechanisms and the limits of the rotor analogy

Read Priezzhev et al. (1996),
[Kapri and Dhar (2009)](https://arxiv.org/abs/0906.5506), and
[Bou-Rabee and Peres (2026)](https://arxiv.org/abs/2608.23545), then follow the
references most relevant to occupation, excursions and growth. Verify the
current version and publication status of the preprint when the review runs.

Extract the assumptions behind each theorem, numerical claim and heuristic:
initial-arrow law, rotor order, ensemble, geometric regularity, and whether
the result concerns range, radius or a limit shape. Separate exponent results
from prefactor, occupation-profile and boundary-width results. Do not transfer
a rotor theorem to the ant without establishing its hypotheses.

Look specifically for return-time, boundary hitting, renewal, conservation and
local-time arguments that could constrain kappa or explain its stationarity.
Review relevant self-interacting walks and internal DLA selectively, checking
whether time counts particle steps or added sites. Shared exponents alone are
not evidence of a shared mechanism.

For each candidate mechanism write down its required assumptions, the
quantity it predicts, a testable consequence beyond the measured growth law,
and an observation that would refute it. Compare those consequences with
existing null and negative results before proposing new runs. The exact
growth-rate decomposition and its fitted exponent relation are bookkeeping;
they cannot independently validate the mechanism.

**Decision:** identify at most a few literature-backed mechanisms worth a
discriminating experiment, or explicitly report that no reviewed argument
explains the ants' rule-specific kappa. Do not turn the review into an
unbounded survey of every model with a cube-root exponent.

## 3. Position the boundary measurements

Use Kapri and Dhar as the immediate comparator, then consult original work
on interface scaling, finite-size corrections and roughening where it bears
on the measurements. Compare definitions before comparing exponent values:
all surface cells versus outer hull, radius convention, global shape modes,
spatial height differences, correlation length, temporal growth and size
dependence.

The current [hull-width investigation](../experiments/archive/2026-10-hull-width/README.md)
and [width-radius refit](../experiments/archive/2026-10-w-width-radius-refit/README.md)
set the observational constraints. An exponent from width versus time, or
width versus a growing radius, is not automatically a spatial roughness
exponent. Record which additional observables would distinguish persistent
large-scale shape from local fluctuating roughness and which assumptions
would be needed for a KPZ or other universality-class comparison.

**Decision:** give the manuscript a defensible comparison and a short list
of missing measurements, rather than assigning a universality class from the
width gap alone.

## Search record and deliverables

Keep the cross-cutting synthesis in `notes/`. If carrying out the review
produces substantial working material, use a dedicated dated investigation
folder under `experiments/`, following `experiments/README.md`, with a README,
append-only lab notebook and shareable notebook. No such investigation or
measurement is started by this planning note.

Record search date, service, exact query, any filters, seed paper and citation
direction, papers screened, inclusion/exclusion reason, and access limits.
Record DOI/arXiv identifier, version and section/page/equation for extracted
claims. Distinguish full-text verification from abstract-only screening.
Search snippets identify candidates; they do not establish technical claims.

Produce:

1. A comparison table of the nearest models and results, using the fields
   above and explicitly marking incomparable observables.
2. A claim audit mapping each manuscript contribution to its closest prior
   work, the remaining distinction, and any required wording change.
3. An annotated bibliography and revised related-work prose, with any
   supporting corrections propagated to the abstract, introduction and
   conclusion. Preserve the distinction between empirical consistency and
   asymptotic proof.
4. A short mechanism shortlist tied to existing evidence, failed tests and
   the smallest useful next experiment.

## Order and stopping rule

Complete the novelty audit first, then the mechanism review, then boundary
positioning. Read the closest sources in full and trace their references and
citing papers before expanding into more distant analogies.

The first pass is complete when every headline contribution has a documented
nearest comparator; the known flipping-rotator omission has been resolved;
the rotor statements have been checked against their actual assumptions;
and one further round of backward/forward citation tracing on the closest
papers finds no materially closer result. Record where tracing stopped and
any unresolved access or coverage gaps. This is a practical stopping rule,
not a guarantee of exhaustive coverage.

If a close paper remains inaccessible or ambiguous, flag the affected claim
and qualify it. Finish by stating what the review changed, what remains
uncertain, and whether it changes the priority of the proposed experiments.

## Execution status appended 2026-10-15

The focused review deliverables are in [the experiment report](../experiments/archive/2026-10-literature-review/reports/Cube%20root%20growth%20literature.md) and [cross-cutting synthesis](literature-review-2026-10-15.md). Prior plan and hypotheses above are unchanged. The user supplied Meng–Cohen1994 after initial web access failures; full-text verification establishes direct visited-area/boundary growth measurements and a pocket/return scaling argument anticipating boundary-access reasoning. The broad negative novelty assertion has been removed from the manuscript; calibrated multicolour coverage, explicit factors and held-out predictions are the supported distinctions.

All four deliverables are supplied and manuscript corrections propagated. The nearest full-text gate is now met for Meng; the known flipping-rotator omission and rotor assumptions are resolved. Citation coverage remains selective: the first round did find materially closer work, and a further targeted round on its verified mechanism remains open. Mishra Eq.5 and several inaccessible historical originals remain limitations. Thus this is a useful completed first-pass synthesis with partial coverage stopping status, not an exhaustive priority audit. No new numerical experiments or Rust release tests were run for this documentary/editorial change. Typst compiled without diagnostics and the shareable notebook executed cleanly; commands/hashes and the uncommitted-input exception are documented in the experiment README.
