# Lab notebook: is a chaotic edge a broken crawler?

Append-only. Newest entry last. Never edit an old entry; correct it with a new one
(`corrects: <timestamp>`). Tags: intent, assumption, observation, interpretation,
surprise, decision, dead-end, question, deviation. See `experiments/README.md`.

### 2026-10-25 22:55 (+13:00) · 56aac50 · intent
Tim asked me to take the square-ring crawler's "cost per filled cell" over to the chaotic edge. I read the c-law
record first (chiral-edge, c-law-mechanism, renewal, lattice) so I would not repeat H-loop or the K3/K4 kernels. The
fact that matters most is Stage 2c: c does not depend on the interior's colours, so it is a property of the
self-built edge layer. The crawler is a self-built edge layer that has been solved exactly.

### 2026-10-25 23:00 (+13:00) · 56aac50 · observation
Exploration, before registering: `c_law_mechanism_trace blank 22 2048` on `R^k L R^(k+1)`, k = 1..8 (scratchpad,
not kept). For k = 5 and 7, r_j = 1.00 for j <= k, 0.25 at k+1, 0 beyond; 1/c = 6.241 and 8.231 (k + 5/4 = 6.25 and
8.25); chains {1, 3} half each. For the other k, 1/c = 2.320, 3.175, 4.089, 5.149, 7.061, 8.972, with chain-2 shares of
0.10-0.30. Three of those rules later turned out to be in the P1 cohort (disclosed in the README).

### 2026-10-25 23:05 (+13:00) · 56aac50 · interpretation
The crawler line `1/c = m + 5/4` and the chaotic lead law `1.363 + 0.696 m` share an intercept to within 0.11. Read
through the crawler, the chaotic edge loses about 0.3 boundary reads per lead step. My conjecture (H-crawl) is that
those are circulations broken by shared cells reading the wrong letter. The crawler names the counts at which shared
cells must read `s_0`: m+1..2m+1. Confidence is moderate. H-young (support from young shared cells, no window) is
just as natural, and C4's weak prefix-4 gain is mild evidence against a window at m = 1.

### 2026-10-25 23:10 (+13:00) · 56aac50 · decision
Pruning preflight at 56aac50: two entries, no match (queries in README). Run. Budget under 1e11 steps.
Cohort sizes from rule strings only: 40 Pi-blobs with m >= 2 (17, 9, 4, 2, 3, 2, 2, 1 for m = 2..9), all "other" in
square-ring P6. W parents are drawn from 1045 / 417 / 276 stationary blobs (m = 1 / 2 / 3, n in 10..12).

### 2026-10-25 23:30 (+13:00) · 56aac50 · intent
Registering H-crawl, P0-P3 and the decision rule in the README, then committing before any list or run.

### 2026-10-25 23:22 (+13:00) · a387d27 · deviation
corrects: 23:30 registration time. The README header says "Registered 2026-10-25 23:30". That was the time I
planned, not a clock reading. The registration commit `a387d27` is timestamped 10:14:17 UTC (23:14 +13:00), and the
commit time governs. From here on, times are read from `date`.

### 2026-10-25 23:22 (+13:00) · a387d27 · observation
P0a (`scripts/p0_strip.py` -> `results/p0_strip.txt`, written after the registration): HELD exactly for k = 1..8,
`1/c = k + 5/4` in exact rationals, with r and chains as derived. Lists (`scripts/make_lists.py` -> `results/lists/`):
25 fillers, 40 Pi rules, 73 control draws (56 distinct), 90 parents, 748 mutants (664 distinct). Two Pi rules
(`RRRRRRRRLRRR`, m = 8; `RRRRRRRRRLRR`, m = 9) have no composition-matched control at any relaxation, because no
non-Pi stationary blob has lead 8 or 9 at those lengths and R-counts. P1b is therefore scored over the 38 Pi rules that
have controls. This is a consequence of the frozen matching rule, not a choice I made after seeing data.

### 2026-10-25 23:25 (+13:00) · 082fb7b · deviation
corrects: 23:22 entries. Their times were estimates. `date` read 23:12 before the registration commit and 23:21 after
the runs, so those entries ran a few minutes ahead of the clock. Order of events, from git and run.log (UTC):
registration commit 10:14:17, lists and P0a commit after it, tracer runs 10:16-10:18, analysis after that.

### 2026-10-25 23:25 (+13:00) · 082fb7b · observation
Registered scoring (`results/analysis.txt`): P0b, P1a, P1b, P1c, W1 (all m), R1, R2 and R3 held; W2 and W3 failed;
N0 passed. The full table is in the README.

### 2026-10-25 23:25 (+13:00) · 082fb7b · surprise
W3 went the wrong way. Making one window letter `s_0` lowers `1/c` more often than it raises it (31% raise), yet a
table with all window letters `s_0` sits far above the lead law. Support is collective. One extra `s_0` letter in an
otherwise broken window does not buy circulation, and may cost some, perhaps by changing which cells end up shared.

### 2026-10-25 23:25 (+13:00) · 082fb7b · interpretation
Post hoc K3 check (`results/posthoc_k3.txt`): K3 predicts the Pi cohort's census `c` almost exactly at m = 2-3. So the
P1 "crawler limit" there is not new information; it is K3's post-kill run term seen from another angle. What K3 misses
is the high-lead Pi rules (m >= 4), where `1/c` keeps climbing at about 0.87 per lead step while K3 saturates. That is
the part of H-crawl still standing, and it rests on 1-4 rules per lead. Next step: register a fresh-rule test of the
slope.

### 2026-10-25 23:22 (+13:00) · 285497a · decision
Stage 2 registered in the README (H-slope, S1-S4) before writing its list script or running anything. Pruning
preflight unchanged (same revision family, no new entries since 56aac50). The rule family changes (fresh lengths
13-18), so I repeated the query: `rg --files notes/pruning-index/entries` still lists the same two unrelated entries.

### 2026-10-25 23:25 (+13:00) · bb2801d · observation
Stage 2 (`results/stage2_analysis.txt`): S1, S2 and S3 failed; S4 held. The Pi slope is 0.884, but paired controls
reach 0.784 (difference 0.044, CI [-0.023, 0.114]). 166 of 256 fresh Pi rules were filler-like (area ratio > 1.9) by
2^24 steps, against 9 of 236 controls.

### 2026-10-25 23:25 (+13:00) · bb2801d · interpretation
The census high-lead "slope 0.87" (post hoc) was mostly composition and small n. Fresh R-rich controls also climb
faster than the census lead law. What survives across both stages: phi of about 0.5-0.65 for Pi rules, and the crawler
line as a ceiling. I hold this at moderate confidence. The selection is heavy (two-thirds of fresh Pi rules fill), and
I have not checked whether phi depends on how close a kept rule is to filling.

### 2026-10-25 23:25 (+13:00) · bb2801d · decision
Write a dead-end signature for the single-letter window (W2/W3, well controlled: N0 passed, 78 parents scored).
Do not write one for H-slope: S1 failed on a paired subset of 42 with a CI that includes 0, which is underpowered,
so it is inconclusive rather than a dead end.

### 2026-10-25 23:25 (+13:00) · bb2801d · deviation
corrects: Stage 1 results header "23:25". Like the earlier entries, it ran ahead of the clock: `date` read 23:22 at
the Stage 2 registration, which came after it. Git commit times govern the order (285497a, then be07015, then bb2801d).

### 2026-10-25 23:27 (+13:00) · 25bf366 · deviation
Commit 25bf366 appended the Stage 2 results through an unquoted shell heredoc, which stripped every backtick-quoted
span. The next commit rewrites only those just-appended sections (README "Stage 2 results", "Overall verdict",
"Pruning-index outcome", and the four NOTEBOOK entries above) with the intended text. No registered text and no
numbers changed. The git diff shows exactly what was restored.

### 2026-10-25 23:33 (+13:00) · a5f994b · decision
Filed the experiment in the atlas under boundary-return (evidence, with the failures named), added a reader-guide row,
built the figure and the shareable notebook (executed clean, 0 errors). Pruning entry
`NR-20261025-crawler-window-single-letter` committed with evidence at b4798f8. Q27 added to the open questions.

### 2026-10-25 (+13:00) · 2b1d794 · deviation
corrects: 23:33 entry ("Q27 added"). At Tim's request the question is numbered Q28 in
`notes/open-questions-hypotheses.md`; question numbers stay plain integers. The cross-reference to the square-ring
ring-onset question is now worded without a number, because `main` currently has two questions numbered Q25.

### 2026-10-25 (+13:00) · PR #17 · deviation
corrects: the previous entry's "worded without a number". The duplicate question numbers are now resolved: the square-ring
ring-onset question is Q27 and its reversed-family/corner question is Q29; rotation boxes keep Q25 and Q26; this
experiment's question stays Q28. The note's cross-reference now reads "Q27 link".
