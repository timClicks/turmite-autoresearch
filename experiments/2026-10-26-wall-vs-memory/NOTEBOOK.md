# Lab notebook: wall or memory

Append-only. Newest entry last. Never edit an old entry; correct it with a new one
(`corrects: <timestamp>`). Tags: intent, assumption, observation, interpretation,
surprise, decision, dead-end, question, deviation. See `experiments/README.md`.

### 2026-10-26 22:50 (+1300) · 5b96f68 · intent
Owner asked to set up the "hybrid walker" experiment proposed in chat: a walker
with memoryless turns inside its territory but the ant's forced R on fresh
ground, to separate the two ingredients of the original cup mechanism. Informs
whether the next boundary-access work should look at the edge rule or at
interior memory.

### 2026-10-26 22:58 (+1300) · 5b96f68 · decision
While designing, generalised the hybrid into a 2x2 factorial: turn noise applied
separately on fresh cells (EF) and revisited cells (EV). The hybrid is the
corner EV=1, EF=0; EV=EF=1 is exactly pw:0.5; EV=EF=0 is the ant. The extra
corner F1 (EV=0, EF=1) tests the ant itself, which the hybrid alone cannot.
Dropped the Q (interior chirality) and P (wall strength) ladder from the chat
proposal: P is covered by EF, and Q only adds chirality.

### 2026-10-26 22:58 (+1300) · 5b96f68 · decision
Pruning preflight at 5b96f68: queries and outcome in README (three entries,
incidental word hits only, none in scope). Decision: run.

### 2026-10-26 23:00 (+1300) · 5b96f68 · assumption
Thinking the hybrid through before registering moved my prior towards
H-memory: a forced-R step on fresh ground closes a loop of at most four steps
back to the entry cell, then the walker leaves at random, so loops can chain
outward; the random-cookie walker (similar first-visit-only structure) stayed
at a ~ 0.92. I said the opposite emphasis in chat (wall as the leading
candidate). Status: untested; the run decides.

### 2026-10-26 23:05 (+1300) · 5b96f68 · decision
Registered question, walker semantics, exact identities, classification,
calibration gates G1-G3 and corner/dose predictions in README before writing
the walker. Rule cohort drawn with `scripts/select_rules.py` (seed 20261026).
