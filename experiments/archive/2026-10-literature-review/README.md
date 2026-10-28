# Literature review, 2026-10-15

Started 2026-10-15 22:03 +13:00 (NZDT), base commit da88e61b690507526ba4e2a2c017d9c7941beb91, with pre-existing uncommitted manuscript/research changes.

Question: execute notes/literature-review-plan-2026-10-15.md: audit novelty, mechanisms and boundary comparisons before further simulation.

This is documentary research, not a numerical experiment. No new numerical hypothesis or measured prediction is registered. Existing timestamped predictions remain intact. No randomness or seeds apply. Literature numerical claims must retain their original observable and averaging definitions.

Method: search-service connector searches and full-text retrieval; exact queries, filters, source identifiers and access limits in results/*search*.md. Evidence notes in research_notes/Cube root growth literature/. Final synthesis in reports/ and notes/. Searches are time-dependent and cannot guarantee identical future results; log exact date and accessed versions.

Status: research in progress. Review notebooks and results will be finalized after evidence synthesis. Do not infer an exhaustive novelty proof from a negative search. No commits authorized.

## Synthesis and verification, 2026-10-15

Completed deliverables: [full report](reports/Cube%20root%20growth%20literature.md), [cross-cutting synthesis](../../../notes/literature-review-2026-10-15.md), all-field model comparison, contribution claim audit, annotated bibliography, revised related-work prose and mechanism shortlist. Supporting corrections are propagated into the manuscript abstract, introduction, occupation/boundary discussion and conclusion, with six added bibliography entries. Pre-existing edits were preserved; no commits were made.

The late user-supplied Meng–Cohen full text changes the strongest finding: visited territory growth and boundary-access scaling are direct prior art. Its A~t^0.75/B~t^0.50 measurements and pocket/return mechanism distinguish the earlier periodic binary media from our uniform multicolour census; d=1 in its scaling formula gives area exponent2/3. The previous abstract-only access gap is superseded by appended evidence, not erased. No reviewed source explains the rule-specific occupation prefactor.

Status: focused first-pass deliverables complete, strict coverage stopping condition only partially met. Every headline claim has a nearest comparator, the flipping-rotator omission and closest Meng full-text gap are resolved, and rotor assumptions checked. One selective citation round found closer work and incorporated it; a further targeted round on the now-verified Meng mechanism, comprehensive forward coverage and Mishra Eq.5 clarification remain open. Original Family–Vicsek, internal-DLA and some historical ant texts remain inaccessible. No exhaustive novelty assertion is made.

Verification: final Typst compile succeeded with no diagnostics; 27-page PDF. Rendered pages1,2,21,25 were visually inspected (opening, introduction, boundary passage and conclusion); no clipping was seen. Notebook executed from a clean kernel through nbconvert; only a routine local-kernel transport warning. Provenance and file hashes are in `results/verification.json`; exact commands below. No simulator, estimator or dependency declarations changed, so no simulations or Rust release tests were rerun. Jupyter/PDF rendering use one-off uv environments and do not change pyproject/lock files.

```bash
export UV_PROJECT_ENVIRONMENT=$HOME/.venvs/turmite UV_LINK_MODE=copy
cd /mnt/f/Code/turmite
uv run experiments/archive/2026-10-literature-review/scripts/build_notebook.py
uv run --with nbconvert --with ipykernel --with nbformat jupyter nbconvert --to notebook --execute --inplace experiments/archive/2026-10-literature-review/notebook.ipynb
typst compile --root . research-outputs/scholarly-articles/cube-root-growth/main.typ research-outputs/scholarly-articles/cube-root-growth/main.pdf
uv run --with pypdfium2 experiments/archive/2026-10-literature-review/scripts/verify_artifacts.py
```

The editorial scripts `revise_manuscript.py`, `update_meng_synthesis.py` and `finalize_review.py` document the one-time sequence against the prior working manuscript; they are not general rerunnable transforms. `build_notebook.py` and `verify_artifacts.py` are rerunnable. Notebook inputs are exclusively small results, but newly produced inputs remain uncommitted because commit authorization is absent. This explicit exception must be closed by committing and re-executing before archival sharing. The notebook prints each working-input status and SHA-256 rather than implying committed provenance.

Priority changes: complete fixed-area censor-complete boundary/interior time accounting, compare spatial local-time balance only as a conditional rotor-inspired mechanism, and complete already registered hull checks before another broad sweep or interface-class assignment.
