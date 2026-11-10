# Lab notebook: slow growers among the 702 late survivors

Append-only. Newest entry last. Never edit an old entry; correct it with a new one
(`corrects: <timestamp>`). Tags: intent, assumption, observation, interpretation,
surprise, decision, dead-end, question, deviation. See `experiments/README.md`.

### 2026-11-10 09:05 (+13:00) · 251100a · intent
Daily session. Open PRs (#30-#35) wait on the user's review or design choices, so pick unblocked regime-validation work:
the ACTIVE open item "whether the 702 include bounded rules". It matters for Q19 because the 702 are the hazard denominator.

### 2026-11-10 09:07 (+13:00) · 251100a · observation
Exploratory look (stated in README): g11 over the 702 is bimodal; 143 below 0.2, 528 at 0.25-0.35. Cut 0.2 chosen from this look.

### 2026-11-10 09:15 (+13:00) · 251100a · decision
Pruning preflight (README): no signature covers the cohort; run. Registered P1-P3 and the consequence before reading the 1e8/1e9
boxes, the highway list against the class, or running P3. Budget ~40 min wall on 4 cores; stop after P3.

### 2026-11-10 09:12 (+13:00) · 8fae18c · deviation
corrects: 2026-11-10 09:15. The README says "Registered 09:15"; the registration commit is 8fae18c at 09:08:22 (+13:00), which is
the binding time (I wrote the README time ahead). Also: classes.csv was written with CRLF and git normalises it to LF, so the
sha256 in the README is of the working-copy CRLF file, not the committed blob. analyse.py lost its PEP 723 header (uv --frozen
needs a lock for script headers); it is stdlib-only and runs in the project env.

### 2026-11-10 09:12 (+13:00) · 8fae18c · observation
`uv run --frozen experiments/proposed/2026-11-survivor-slow-growers/scripts/analyse.py` -> results/analysis.txt. P1 HOLD: 143/143 slow rules were slow in (1e9,1e10]; 558/559
growing rules were growing. P2 HOLD: 0/28 genuine late highways were slow in the decade before onset (all g 0.30-0.47).
Pools: (1e9,1e10] 143 slow of 807 (17.7%); (1e10,1e11] 144 of 732. Growing-only genuine yields 16/664 = 2.41%, 12/588 = 2.04%.
P3 runs started 09:09, 4 at a time.

### 2026-11-11 08:03 (+13:00) · 67ba451 · observation
P3 runs all finished (run.log end 2026-11-11T01:13:42+13:00); every rule stopped on budget at 2e11 steps, no highway, no escape.
`uv run --frozen experiments/proposed/2026-11-survivor-slow-growers/scripts/p3_eval.py` -> results/p3_analysis.txt. P3 **FAIL**: 7/8 within the registered bound
(ratios 1.000-1.050; RRRLLRLL sits exactly on 1.05), RLRLRRRR at 1.086 (side 140 -> 152). All 8 are far below the cube-root
1.26, so the slow class is still slow, but the registered claim "stays put (<= 1.05)" does not hold for every rule.

### 2026-11-11 08:03 (+13:00) · 67ba451 · deviation
Provenance gap: run.log has one start line (09:08:33 on 11-10) and the second batch of four finished about 15 h after the first,
while per-run wall_s is 1700-3300 s. The relaunch (or pause) of the second batch is not logged; outputs are complete CSVs and
the script skips finished rules, so results are usable, but the timing is unexplained. The four `.tmp` files committed in 67ba451
were in-flight outputs and are removed here.

### 2026-11-11 08:03 (+13:00) · 67ba451 · interpretation
Bounded vs slowly-growing remains unresolved: 3/8 did not move at all over the half-decade, 5/8 grew a few cells. P3 cannot
separate "bounded with late transients" from "very slow growth" (local exponents 0-0.12). The Q19 consequence from P1/P2
(growing-only denominator) is unaffected by P3 in kind, but the slow class should not be called bounded. Any exact-recurrence
bounded check or 1e12 run needs its own registration (README). Stopping here as budgeted.

### 2026-11-11 08:51 (+13:00) · 169c908 · housekeeping
CI "Research blog" failed on PR #37: the atlas validator found this experiment neither filed nor in `blog/experiment-guides.tsv`.
Fixed with no new measurement: folder moved `proposed/` -> `active/` (results exist; README status line and script/README self-paths
updated; earlier NOTEBOOK entries keep the old path as written), reader-guide row added, filed under the atlas `late-highways` topic
(evidence, open question on bounded vs slow, turning point), and the `notes/ACTIVE.md` open item updated. Local checks:
`python3 blog/scripts/test_atlas.py` (8 OK), `blog/scripts/test_experiments.py` (OK), `export_results.py --check` (OK).
