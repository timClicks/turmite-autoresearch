# Three focused paper drafts — 2026-10-20

Editorial decision at 21:52 NZDT, base revision 715ab37. Requested by the user; this is manuscript work, not a new experiment. The original synthesis is retained. Concurrent edits to it were not overwritten.

Drafts live in `research-outputs/working-papers/`:

- `growth-census/`: calibrated prevalence, finite-time uncertainty, replication and late transitions.
- `boundary-transport/`: accounting, rule prediction, uniform reference, forecasts and mechanism controls.
- `ant-rotor-boundaries/`: accumulated bulk profiles, surface-growth differences, radius/hull checks and limits of interface interpretations.

The abstracts, introductions and conclusions were rewritten around separate questions. Most evidence paragraphs and figures are inherited from the synthesis snapshot, preserved as `provenance/synthesis-source.typ.txt`. The transport draft also states the later failed six-letter-family hold-out, checked against its README, so the earlier prefix score cannot imply transfer to unseen families. No new simulation, estimator, fitted result or scientific dataset was produced.

The PDFs use a coordinated editorial design with Georgia reading/display type, Lato navigation, three article accents, figure-led covers and an evidence panel. `build.py` compiles all three under WSL and records actual source, numerical input, figure, bibliography, font and PDF hashes. The source snapshot includes editorial changes that were uncommitted when captured; its hash identifies it more precisely than a base revision alone.

Rebuild from the repository root:

```bash
export UV_PROJECT_ENVIRONMENT=$HOME/.venvs/turmite UV_LINK_MODE=copy
uv run research-outputs/working-papers/build.py
```

Publication gates remain: author review, target-venue framing, final availability/disclosure statements and scientific reconciliation against the current research frontier. The third paper is deliberately provisional. Shared datasets are not independent replications. Full provenance audits remain shared with the synthesis.
