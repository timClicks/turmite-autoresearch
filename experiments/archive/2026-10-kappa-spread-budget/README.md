# kappa spread budget (2026-10-20)

**Status: post hoc synthesis.** Every input value was seen before this was written; nothing here is a registered test. No new
simulations.

## Question
`notes/ACTIVE.md` / `notes/open-questions-hypotheses.md` ask why `kappa/kappa_unif` has median 0.81 and a 5-95% range of 0.44-1.33
over stationary blob rules. That is two questions: the **spread** and the **location**. This folder budgets the spread only.

## Reframing
`kappa_unif(a, beta)` is rule-independent (1.105, sd ln 0.004; `experiments/archive/2026-10-kappa-uniform-baseline/results/census_spread.txt`),
so the spread of `kappa/kappa_unif` is the spread of ln kappa, sd 0.349 over 2185 stationary rules (variance 0.122). Predictors such as c, ln A(2^22), a, beta and fill are tied to kappa
through the growth identity, and conditioning on area is the collider flagged in `experiments/archive/2026-10-c-law-mechanism/`; the
budget therefore uses only start-to-start noise and predictors read off the rule string (the prefix lookup).

## Result (`results/spread_budget.txt`, `.json`)
Shares of the single-run variance of ln kappa (stationary cohort):

| component | share | source |
|---|---|---|
| start-to-start noise (not rule-determined) | 0.15 | 1 - ICC, ICC = 0.851, pool-192 patched starts (`w2_stationarity.txt`) |
| rule-determined, predicted by the first 8 letters | 0.47 - 0.54 | prefix-8 held-out R^2 0.552 (pool patched means, `x2_prefix_heldout.txt`) to 0.633 (fresh rules, strict, `w3c_stats.txt`), times the ICC |
| rule-determined, not predicted by the prefix | 0.31 - 0.38 | remainder |

Absolute scale: noise sd 0.13, rule-mean sd 0.30, total sd 0.35.

## What it does and does not show
- About half of the spread is predictable from the first eight letters, about a third is rule-determined but not captured
  by the prefix, and about a sixth is start noise. The unexplained rule-determined part (sd about 0.2 in ln kappa) is where a
  mechanism for the spread would have to act.
- Not shown: anything about the **location** (why about 0.8 x kappa_unif, below every walker reference). Open.
- Caveats: three cohorts (census single runs, pool-192 patched starts, fresh 13-14 letter rules); the prefix R^2 is against
  rule-level means and is scaled by the ICC as if those means were noise-free; no uncertainty is propagated (shares are rough to
  about +-0.1); prefix families overlap between training and test, so this is transfer within families, not to unseen ones.

## Reproduce
`uv run experiments/archive/2026-10-kappa-spread-budget/scripts/spread_budget.py` (parses the committed result files; input sha256
in `results/spread_budget.json`). `notebook.ipynb` reads only `results/spread_budget.json`.
