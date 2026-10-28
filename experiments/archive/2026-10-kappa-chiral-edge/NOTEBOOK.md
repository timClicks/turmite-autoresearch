# Lab notebook: kappa and the chiral edge layer

Append-only. Newest entry last. Never edit an old entry; correct it with a new one
(`corrects: <timestamp>`). Tags: intent, assumption, observation, interpretation,
surprise, decision, dead-end, question, deviation. See `experiments/README.md`.

### 2026-10-19 08:40 (+13:00) · 3f23de3 · intent
Goal: investigate a promising mechanism for kappa. Read notes/open-questions-hypotheses.md and kappa-mechanisms-2026-10-15.md. The only predictor that survived fresh data is the leading run (L1, L3, A1, M3), but causality is unestablished (M1/M2 failed because lengthening the lead also cuts A22). Chosen hypothesis: the opening run acts on fresh ground as a chiral edge layer (m same-turn reads of a young cell = a 4-step loop, dwell ~4m), a wall-localised persistence in the sense of active-matter wall accumulation / skipping orbits. Advisor-suggested design: first a within-necklace test (rotations keep composition and cyclic sequence, change only what fresh ground reads first), on existing census data; then SparseBg dose-response with rule fixed. README registers N1-N5 before the analysis runs.

### 2026-10-19 08:46 (+13:00) · 3f23de3 · assumption
K1 says only ~20% of ln kappa variance lies between necklaces (ICC 0.199), so there is plenty of within-necklace variance for lead to explain. Not verified that rotations' lead varies enough inside necklaces; the script drops necklaces whose members all have the same capped lead and reports the count. Also: lead and trail are anticorrelated within a necklace when the cut falls inside a run, so N3 uses the marginal trail fit and I additionally report lead+trail jointly (descriptive).

### 2026-10-19 08:50 (+13:00) · 3f23de3 · deviation
First launch of necklace_lead.py failed (script not written because the combined command was refused by the harness; then WSL path/$HOME quoting under PowerShell). Fixed by writing the script with the editor tool and passing the command in single quotes. No analysis output was seen before the successful run.

### 2026-10-19 09:00 (+13:00) · 3f23de3 · observation (results/necklace_lead.txt)
Within-necklace slope of ln kappa on lead: -0.007 [-0.037, 0.017] (all blob, 536 necklaces, 2358 rules), +0.044 [0.027, 0.060] stationary (474 / 1891). Within-necklace slope of ln c on lead: -0.243 [-0.249, -0.237], R^2 0.83 (stationary -0.228, 0.86). N1 and N4 FAILED, N2 HELD, N3 moot.

### 2026-10-19 09:02 (+13:00) · 3f23de3 · surprise
ln c is almost a deterministic function of the opening run within a necklace (R^2 0.83). I expected c to fall but not by this much. The kappa edge-layer picture is wrong at the census level; the c part is right.

### 2026-10-19 09:12 (+13:00) · 3f23de3 · observation (results/cyclic_run.txt)
Registered Stage 1b (cyclic max run M): M1, M2, M3 all FAILED. Census-wide ln kappa on lead R^2 0.001 slope +0.010; M slope -0.056. So the lead effect on kappa appears only conditional on ln A(22). 

### 2026-10-19 09:20 (+13:00) · 3f23de3 · interpretation
Lead drives c; c drives growth and so A22 (via dA/dt = c kappa P/A); kappa at fixed A22 shifts with lead (+0.15/step) while kappa total does not. Implies d ln kappa/d ln A ~ +0.5, part of it definitional (kappa = B A/P). So the earlier "lead raises kappa" is a conditional statement; conditioning on a variable the predictor itself moves (here via c) makes the sign of any "effect" depend on that choice. Confidence moderate: the conditioning argument is arithmetic from numbers in earlier notes, not re-measured here. Alternatives: genuine fixed-area edge effect (M3 supports), selection (L5).

### 2026-10-19 09:36 (+13:00) · 3f23de3 · observation (results/c_law.txt)
Registered Stage 3: C1 held (fresh R^2 0.877, rel err 0.041), C2 held (b 0.683 [0.658, 0.707] vs census 0.696), C3 held (naive loop b = 1 rejected), C4 FAILED (prefix lookups keep gaining: 0.845 / 0.887 / 0.924 / 0.950 at 4 / 5 / 6 / 8). Exploratory linear alignment model worse than lead (0.81).

### 2026-10-19 09:40 (+13:00) · 3f23de3 · decision
Stop here for the kappa claim; write up, update notes and commit. Reason: the pre-registered kappa mechanism is refuted and the replacement (lead -> c law) is a strong, validated empirical regularity, but its mechanism (a = 1.36, b = 0.70) is unexplained. Next experiment, unregistered: sbg density dose-response for the c law; and an exact edge-strip enumeration for b.
### 2026-10-19 09:41 (+13:00) · 3f23de3 · question
Is b = 0.70 derivable from a flat-edge scattering calculation (young cells coloured 1..m, ant arrives with random heading)? Why does the fit give kappa >~ 1.25-1.5 at lead 7-8 (n = 6, 4)?

### 2026-10-19 19:06 (+13:00) · b7b4758 · decision
Follow-up opened in `experiments/archive/2026-10-c-law-mechanism` (the open questions above: where 1.36 and 0.70 come from, the sbg dose-response, and whether the fixed-area kappa shift is real). Nothing in this experiment's results is revised by that work; its outcomes are recorded there and summarised in notes/open-questions-hypotheses.md. In one line: the fixed-area lead effect on kappa was reproduced by conditioning on ln A22 with no direct effect (collider), the sbg dose-response was run, and the flat-edge simulation reproduces the c law rule by rule.
