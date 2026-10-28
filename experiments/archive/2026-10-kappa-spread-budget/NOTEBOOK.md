# Lab notebook: kappa spread budget

Append-only. Newest entry last. Never edit an old entry; correct it with a new one
(`corrects: <timestamp>`). Tags: intent, assumption, observation, interpretation,
surprise, decision, dead-end, question, deviation. See `experiments/README.md`.

### 2026-10-20 02:40 (+13:00) · 89ade3c · intent
Take the ACTIVE.md item 'kappa/kappa_unif distribution' (median 0.81, sd ln 0.35) and answer the part that needs no new runs: a
variance budget of the spread. Registered as a post hoc synthesis because all input headline values were already known (listed in
README). No prediction is registered, none is claimed.

### 2026-10-20 02:40 (+13:00) · 89ade3c · assumption
(1) kappa_unif is rule-independent, so the spread of kappa/kappa_unif is the spread of ln kappa (checked: sd ln 0.004 in `census_spread.txt`).
(2) c, ln A22, a, beta and fill are excluded as predictors: tied to kappa through the growth identity, and ln A22 is the collider of the
c-law Stage 4. (3) The prefix R^2 is against rule-level means, so multiplying by the ICC converts it to a share of single-run variance;
this is only valid if those means are noise-free. Status: (1) checked, (2) a design choice, (3) untested (the pool means average about 12 starts, so the bias is small and conservative).

### 2026-10-20 02:45 (+13:00) · 89ade3c · observation
`scripts/spread_budget.py` -> `results/spread_budget.txt`. Total sd ln kappa 0.349 (census stationary, n=2185); ICC 0.851 (pool-192
stationary patched starts, sd 0.327), so start noise is 15% of variance (sd 0.126). Prefix-8 held-out R^2 0.552 (pool means) or 0.633 (fresh,
strict): prefix-predictable 0.47-0.54, rule-determined but unexplained 0.31-0.38 of single-run variance.

### 2026-10-20 02:50 (+13:00) · 89ade3c · interpretation
Roughly half of the spread is predictable from the first eight rule letters, a third is rule-determined and unexplained, a sixth is
start noise. The unexplained rule-determined sd is about 0.2 in ln kappa. Only the spread is budgeted; the location (about 0.8 x kappa_unif)
is untouched and stays open. Caveats: three cohorts, no propagated uncertainty (shares rough to +-0.1), prefix families overlap train and test.

### 2026-10-20 02:50 (+13:00) · 89ade3c · question
Which letters or structural features carry the unexplained third? A held-out comparison of prefix, suffix and whole-string composition
features on the fresh rules, registered before running, would be the next step (needs the per-rule fresh data and new analysis; not done).
