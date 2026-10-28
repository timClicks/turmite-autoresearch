# Independent-area test of the excursion-cutoff association

Registered 2026-10-15 21:12 +13:00, base `da88e61` (dirty tree), before analysis.
Question: does higher kappa still predict shorter extreme excursions when the
area used to match rules comes from independent trajectories?

Input: committed `../2026-10-t1-excursion-tomography/results/t1b_cutoff_seeds.csv`.
Reuse k=22,25, exclude escaped windows. Partition seeds by seed modulo 3;
require >=2 surviving seeds in each group for each rule/window. Use all six
permutations assigning groups to area, kappa, and ln(L999/R). Match rule pairs
with |difference in mean ln A| <=0.05, sensitivity 0.10. Each permutation has
equal weight; statistic is mean fraction of pairs with opposite signed kappa
and cutoff differences. Report all six fractions and counts. No z selection.
Bootstrap rules (2000, seed 20261015), keeping roles and windows together;
pair weights are products of rule multiplicities. Overlapping pairs are not
independent observations. Report between-rule-bootstrap uncertainty.

Prediction: at tolerance 0.05, mean concordance >=0.65 and bootstrap lower
95% bound >0.5 at BOTH windows. If not, independent-area replication fails;
do not proceed to a transplant on this evidence. Fewer than 20 rules or any
role with <20 pairs makes that window inconclusive. Passing supports an
association, not a mechanism or causality. Matching noisy area does not hold
true area fixed; disjoint seeds remove shared-trajectory selection only.

Instrument calibration: this is a new association estimator, not a growth
fit. Before ant analysis run synthetic rule-level null and negative-association
controls (44 rules, 3 groups, 200 independent datasets, seed 20261015):
null mean within 0.05 of 0.5, negative-association mean >0.8. Synthetic area
independent of predictors; this checks signs and role handling, not biological
confounding. No new rotor/random-walk growth estimates are made.

Command (WSL, repository root):
`export UV_PROJECT_ENVIRONMENT=$HOME/.venvs/turmite UV_LINK_MODE=copy; uv run experiments/archive/2026-10-independent-area/scripts/analyse.py`
Outputs: `results/analysis.json` (full hashes, commit, controls, per-role results).
No new simulations. No existing results overwritten.

## Results — 2026-10-15 21:18 +13:00

Registered prediction **held at both windows**, 44 rules retained at each.
At tolerance 0.05, concordance is 0.730 (rule-bootstrap 95% 0.605–0.842)
at k=22 and 0.757 (0.617–0.881) at k=25. At tolerance 0.10 it is
0.694 (0.573–0.799) and 0.728 (0.603–0.845). All six role assignments
meet the 20-pair requirement. Null synthetic mean 0.497; negative-association
control 0.957, both passing the registered calibration gates.
Numbers, individual assignments and hashes: `results/analysis.json`, command above.

This rejects shared-trajectory area selection as a sufficient explanation of
the observed concordance. It does not establish that cutoff determines kappa:
matching uses noisy area, the rules were previously selected, escapes are excluded,
and k=22 and k=25 are repeated windows of the same trajectories. Confidence
intervals are marginal per window, not independent replications or a joint CI.
Implementation clarification: rule resampling is joint over all six role
assignments within each window; bootstrap draws differ between windows. No
cross-window statistic or confidence interval is estimated.

What changes: retain the cutoff as a credible rule-level lead despite the failed
earlier noise-floor gate; **that gate is not retroactively passed**, and no
transplant is justified by this analysis alone. Next discriminating test:
new matched-area trajectories with direct tail measurements and a powered
intervention designed around the residual kappa effect, rather than more
pairwise correlations. These results reuse old simulations and are not fresh
rule validation.

## Verification

`cargo test --release` passed; log `results/cargo-test.log` (base commit above).
The analysis reran byte-identically: output SHA-256
`737ad21e7495302cfc70176a60b7adb4d6a86c3136db8bc521962fcaaeebf610`.
The shareable notebook executed from a clean kernel:

```bash
uv run experiments/archive/2026-10-independent-area/scripts/make_notebook.py
uv run --with nbconvert --with ipykernel --with nbformat jupyter nbconvert --to notebook --execute --inplace experiments/archive/2026-10-independent-area/notebook.ipynb
```

Run in WSL with the environment exports above. No dependency declarations
changed. Results are uncommitted pending user request, as repository policy requires.
