# Lab notebook: highway preconditions (causal seeds)

Append-only. Newest entry last. Never edit an old entry; correct it with a new one
(`corrects: <timestamp>`). Tags: intent, assumption, observation, interpretation,
surprise, decision, dead-end, question, deviation. See `experiments/README.md`.

### 2026-10-21 20:05 (+13:00) · 3fcfce8 · intent
Tim suggested analysing the grid state together with the rule, to find shared preconditions of highway onset across
rules. Plan: define the dependency set D(tau) (nonzero cells at tau that the future reads), take its minimum near onset
as the causal seed, encode seeds by turn words (rule-independent) and compare across all 583 census highways with onset
<= 1e9. Registered P1-P5 and controls C1-C4 in README before writing code.

### 2026-10-21 20:05 (+13:00) · 3fcfce8 · assumption
After a highway leaves the old territory it never reads an old cell again. Checked per event by C2: the transplant must
match the original for 200 periods beyond the read window. Status: untested.
