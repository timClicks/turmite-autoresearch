# Research outputs

Publishable writing and datasets built from committed experiment results. Nothing here runs new simulations; scripts read `experiments/*/*/results/` (see `AGENTS.md`). Since 2026-10-28 the folder has three kinds of output:

| Folder | Contents |
|---|---|
| [`scholarly-articles/`](scholarly-articles/) | Full scholarly manuscripts. [`cube-root-growth/`](scholarly-articles/cube-root-growth/README.md) is the synthesis: Typst source, figure and number scripts, `fig/`, `refs.bib`, and the reproducibility audit (`audit.typ`, `supplementary/`). |
| [`working-papers/`](working-papers/README.md) | Shorter, focused drafts, one subfolder per paper (`growth-census/`, `boundary-transport/`, `ant-rotor-boundaries/`), sharing `build.py`, `build.json`, `editorial.typ`, `provenance/`, `verification.json` and the README at the `working-papers/` level. They reuse the synthesis's figures, numbers and bibliography in `scholarly-articles/cube-root-growth/` rather than copying them. |
| [`data-papers/`](data-papers/README.md) | Datasets meant to be cited on their own: [`rule-census/`](data-papers/rule-census/README.md) and [`walker-reference/`](data-papers/walker-reference/README.md), each with its build script, build record and README. Each still needs a describing data paper. |

Each manuscript and dataset folder has a `CITATION.bib` with a BibTeX entry for that item (`@misc` for the synthesis and the datasets, `@unpublished` for the working papers). The repository-level `CITATION.cff` gives the synthesis as the preferred citation.

Before 2026-10-28 the synthesis lived in `research-outputs/cube-root-growth-paper/` (datasets in its `supplementary/`) and the focused drafts in `research-outputs/focused-papers/`. The old-to-new map is `experiments/_migration/2026-10-28-research-outputs-split.tsv`. Generated hash records, build logs and frozen provenance snapshots made before the move still name the old paths, as they record what was hashed at the time.

Build the synthesis from the repository root:

```bash
typst compile --root . research-outputs/scholarly-articles/cube-root-growth/main.typ
typst compile --root . research-outputs/scholarly-articles/cube-root-growth/supplementary/reproducibility-audit.typ
uv run research-outputs/working-papers/build.py   # working papers; see working-papers/README.md for fonts
```
