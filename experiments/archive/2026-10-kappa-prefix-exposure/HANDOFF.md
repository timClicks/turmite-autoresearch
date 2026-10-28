# Fresh-session handoff

1. Read AGENTS.md, this README, PLAN.md, SCHEMA.md and the linked mechanism note.
2. Check git status: this scaffold was made in a dirty, actively edited workspace.
   Preserve unrelated work and all historical results.
3. Append an intent entry to NOTEBOOK.md before implementation or analysis.
4. Implement and calibrate the proposed instrument, using the reference oracle.
5. Resolve draft choices and freeze the registration BEFORE confirmation runs.
6. Run only after the feasibility/reliability gates and resource plan are fixed.
7. Report nulls and failed gates; update the notebook from committed summaries.

Current state: planning only. There is no scientific runner, selected cohort,
validated new estimator, frozen seed manifest, or new result. The scaffold is
not evidence for any proposed mechanism. The immediate deliverable for the next
session is a calibrated instrument and concrete preregistration, not a large sweep.

Available now (from repo root under the required WSL/uv environment):
`uv run experiments/archive/2026-10-kappa-prefix-exposure/scripts/preflight.py`

Notebook execution (no simulation):
`uv run --with nbconvert --with ipykernel --with nbformat jupyter nbconvert --to notebook --execute --inplace experiments/archive/2026-10-kappa-prefix-exposure/notebook.ipynb`
