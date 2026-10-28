# Focused research papers

Three editorial drafts, 20 October 2026. The existing synthesis in `../working-papers/cube-root-growth/` is retained. No new simulations or fits were performed.

This folder was `research-outputs/focused-papers/` until 2026-10-28. The drafts read the synthesis's figures, numbers and bibliography from `../working-papers/cube-root-growth/`, and the rule census and walker-reference datasets are in `../data-papers/`.

| Draft | Question | Reading copy |
|---|---|---|
| Eight times the steps | How widespread is calibrated cube-root growth, and where does the evidence stop? | [PDF](growth-census/main.pdf) |
| The cost of the edge | Which transport quantities can rules predict, and which mechanisms survive controls? | [PDF](boundary-transport/main.pdf) |
| A shared bulk, a different edge | How can ant and rotor bulk profiles agree while surface growth differs? | [PDF](ant-rotor-boundaries/main.pdf) |

Each folder contains editable Typst source, provenance and a PDF. The third paper is a developing comparison, not an interface-class claim. The transport draft explicitly distinguishes the original within-cohort prefix score from the later failed family hold-out.

## Editorial design

A coordinated magazine-style series: large Georgia display type, Georgia reading text, Lato navigation and captions, and one restrained accent per question (forest, copper, indigo). Equations retain a dedicated mathematical font. Spacious opening pages orient the reader before the detailed argument; unboxed full-width scientific figures preserve the plots' scale and their original visual encodings. Colour identifies articles rather than changing evidence. Figure captions and qualification panels remain part of the scientific argument.

## Build and check

In WSL, from the repository root:

```bash
export UV_PROJECT_ENVIRONMENT=$HOME/.venvs/turmite UV_LINK_MODE=copy
uv run research-outputs/articles/build.py
```

The builder checks every compilation's exit status, writes per-paper logs and records source, PDF, shared numerical-input, bibliography, figure and font hashes in `build.json`. It uses `/mnt/c/Windows/Fonts` when available for Georgia; elsewhere pass `--font-path PATH` to a local Georgia installation. Georgia is not redistributed. Without Georgia, Typst falls back to Libertinus Serif; this changes layout and must be reviewed. Lato and the remaining fonts are supplied by the existing manuscript environment.

The original figure and JSON producers remain those documented in `../working-papers/cube-root-growth/README.md`; this builder does not rerun them. Shared assets are deliberately reused, so this is not an independent archival package. Build metadata records the inputs actually used, and `provenance/synthesis-source.typ.txt` freezes the editorial source snapshot taken while another session was editing the original manuscript.

## Scope and publication gates

The three outputs share data and some methods. They must not be presented as independent replications. Detailed registration records and full controls remain in the original supplementary audit. All drafts need author review, final archive/DOI and disclosure statements, and a scientific reconciliation before submission. The current research frontier is newer than some paragraphs inherited from the synthesis; this split does not claim a comprehensive incorporation of every ongoing experiment.

Verification is editorial: compile all sources, check internal references, render every page in contact sheets, inspect cover/reading/figure pages at larger scale, and record output hashes. No simulator, estimator or experimental result was changed; Rust tests were not rerun for these manuscript-only changes.
