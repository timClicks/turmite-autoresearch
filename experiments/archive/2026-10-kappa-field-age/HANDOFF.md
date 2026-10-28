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
`uv run experiments/archive/2026-10-kappa-field-age/scripts/preflight.py`

Notebook execution (no simulation):
`uv run --with nbconvert --with ipykernel --with nbformat jupyter nbconvert --to notebook --execute --inplace experiments/archive/2026-10-kappa-field-age/notebook.ipynb`

## Superseding handoff after the 2026-10-15 instrument pilot

The initial planning-only description is historical. Instrument implementation,
synthetic calibration, reference tests, and a registered full supported-cohort
feasibility pilot are complete. Read the appended README status and
results/REPORT.md, then results/pilot_summary.json and NOTEBOOK.md. The executed
notebook is now a result write-up, not a planning scaffold.

Use scripts/run.py --name pilot-v2 to verify/reuse finished results while preserving
the original runtime audit. The frozen low-level pilot.py is intentionally kept
unchanged; it can resume partial batches but rerunning it directly after completion
would replace timing with skip overhead. scripts/check_resume.py verifies the safe
wrapper. No raw payloads were moved across experiments or added to version control.

Scientific T1/T2 and A1/A2/A3 have NOT been evaluated. Before confirmation, calibrate
and freeze the actual survival/prediction estimator, choose role/fold assignments
and seed counts, implement state checkpoints and verify interrupted/resumed bytes,
and resolve reserve/cohort failures prospectively. The age pool contains only 23
drifting rules (24 needed), and median age has weak smaller-band precision. Third-
band age nonattainment is concentrated in two drifting rules. Do not erase these
failures, relabel a pilot as confirmation, or silently drop missing rules.

Simulation base b3a0f76; later shared HEAD 3d00123 is an unrelated external commit.
Source/input hashes still validate; this chat made no commit. The user asked to
proceed with these two investigations, not the other mechanism plans.
