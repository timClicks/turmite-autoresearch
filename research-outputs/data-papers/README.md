# Data papers

Datasets that are meant to be cited and reused on their own, apart from any one manuscript. Each subfolder holds the dataset, the script that rebuilds it from committed experiment results, a build record with input hashes, and a README describing columns and scope.

| Dataset | Contents | Used by |
|---|---|---|
| [`rule-census/`](rule-census/README.md) | `rule_census.csv`: one row per rule (all 4083 canonical L/R rules of length 2–12, 65 columns), joining the per-rule quantities behind the census tables and figures | [`../scholarly-articles/cube-root-growth/`](../scholarly-articles/cube-root-growth/) and the [working papers](../working-papers/README.md) |
| [`walker-reference/`](walker-reference/README.md) | `walker_reference.csv`: 48 rows of calibration-walker boundary occupation `kappa` as a ratio to each walker's own uniform-territory reference `kappa_unif(a, beta)` | as above |

These folders moved here from `research-outputs/cube-root-growth-paper/supplementary/` on 2026-10-28 (map in `experiments/_migration/2026-10-28-research-outputs-split.tsv`). Their content was not changed.

**Status:** each dataset still needs a describing data paper (its scope, methods, validation and citation). None has been written yet; the READMEs are the current documentation.
