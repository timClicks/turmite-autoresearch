# Lab notebook: kappa spread features

Append-only. Newest entry last. Never edit an old entry; correct it with a new one
(`corrects: <timestamp>`). Tags: intent, assumption, observation, interpretation,
surprise, decision, dead-end, question, deviation. See `experiments/README.md`.

### 2026-10-20 03:10 (+13:00) · 91a2243 · intent
Test whether the rule-determined, predictable part of ln kappa is specific to the start of the rule string (prefix) or shared by the
end (suffix) and by letter composition. Design and predictions F1-F4 registered in README and committed (d5e0ff0) before `scripts/features.py` was written or run.

### 2026-10-20 03:20 (+13:00) · d5e0ff0 · observation
Ran `features.py` (seed 20261020, 2000 bootstraps). Train 2185 stationary blob census rules, test 162 fresh stationary rules, no overlap. Strict held-out R^2: P8 +0.624 [0.486, 0.732], S8 -0.114 [-0.298, 0.034], C +0.079 [-0.052, 0.190], P8+C +0.632. F1-F4 all held.

### 2026-10-20 03:25 (+13:00) · d5e0ff0 · deviation
Added an unregistered control to the script after seeing the S8 result: leave-one-out R^2 inside the training set, because training rules are length 3-12 and test rules 13-14, so S8 might fail only through length misalignment. Result P8 +0.589, S8 -0.065. Labelled POST HOC in the output and README.

### 2026-10-20 03:30 (+13:00) · d5e0ff0 · interpretation
The predictable part of ln kappa is carried by the first eight letters; the last eight and simple composition add nothing. Consistent with the lead-run / early-evolution picture; not evidence about which prefix feature matters, and the prefix lookup is a family-membership predictor with overlapping families across train and test. The unexplained third of the spread is not reached by any summary tried here.

### 2026-10-20 03:30 (+13:00) · d5e0ff0 · question
Which prefix feature matters (lead-run length, the first letters after the lead, position of the first L after it)? And is the unexplained third carried by middle letters or by interactions? A registered comparison of structural prefix features (lead length, second run length) against the 8-letter group mean would address the first.
