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

### 2026-11-12 18:25 (+13:00) · b3394bf · deviation
Fixes from the automated review on PR #37 (no new measurement). `classes.py` writes LF (`lineterminator="\n"`) and both
scripts resolve the archive from the repo root (`parents[4]`); `analyse.py` loses a dead loop and now also prints growing rules
that were slow in (1e9,1e10]: one, RLLLRLRRRR (side 6578 -> 6578 -> 11412, g11 0.239), the rule in the histogram gap. This adds
two lines to `results/analysis.txt`; every P1/P2/yield number is unchanged. `p3_eval.py` compares `20*s2 <= 21*s1` (exact);
`results/p3_analysis.txt` is byte-identical, RRRLLRLL (126/120) is exactly on the bound. `p3_run.sh` now logs failures and keeps
stderr in `<rule>.err`. Regenerated `classes.csv` and `p3_sample.txt` are byte-identical to the committed files (LF sha256
9d867159...827da8a6; the README's registered hash was of a CRLF write).

### 2026-11-12 18:25 (+13:00) · b3394bf · decision
Correction to the 2026-11-11 08:51 entry: its tag should be `decision`, not `housekeeping`. Also, entry timestamps in this
notebook were written ahead of their commits on 11-10 and 11-11, so commit times are the reliable clock.

### 2026-11-12 18:25 (+13:00) · b3394bf · observation
P3 timing gap, likely explained: each of the four second-batch rules finished 14 h 36 min after slot-free time + `wall_s`, in the
predicted order (reviewer's arithmetic). A constant offset fits one suspension of the whole process (`wall_s` uses `Instant`,
which does not count suspended time on Linux), not a relaunch, which would have logged a second start line. Not re-derived here.

### 2026-11-12 18:25 (+13:00) · b3394bf · interpretation
Post hoc, from committed census boxes: all 143 slow rules have non-decreasing sides over 1e8, 1e9, 1e10, 1e11; 127 grew in all
three decades, and in 106 of those the largest increment is at most twice the smallest. All 8 P3 rules grew every decade
(RLRLRRRR 98, 111, 127, 140, then 152). This points to roughly logarithmic growth, `side ~ a + b log10 t`, under which one
doubling adds about 0.3b cells (ratio about 1.01-1.04), so the 1.05 bound sat inside integer-cell noise. P2's zero is an upper
bound (about 1.0% per decade at 95%), not a zero hazard. A registered log-versus-power test on all 143 boxes is the sharper next
step; not run here.


### 2026-11-12 22:15 (+13:00) · b1014be · intent
Tim approved a registered log-versus-power test on the 143 slow rules (reading committed boxes only). Wrote README Amendment A1
before any model was fitted: H-const, H-log, H-power (alpha in [0, 1/3]) and a H-cube control; sigma = max(1, 3%) cells; labels from
chi2 and AIC; P1-P4 with thresholds; gates G1, G2; a parametric bootstrap for the aggregate; the 1e7 box of `sweep_2_10.csv` as the one unseen
data set (out-of-sample backcast). Pruning index `cc7a885`: no matching entry, decision run.

### 2026-11-12 22:15 (+13:00) · b1014be · assumption
H-log came from the post hoc look at these same boxes, so a log fit is not independent evidence. The sigma scale is a guess. 4 points per
rule cannot separate log from power at alpha below about 0.04 (synthetic calibration, below), and the registration says so.

### 2026-11-12 22:15 (+13:00) · b1014be · deviation
Before registering I ran a throw-away prototype (not committed, synthetic data only, `/workspace/scratch/proto.py`, `agg.py`) to choose the thresholds and the
`D >= 4` rule. It read no box. This is stated in the registration; the committed script reruns the same synthetic calibration with seed 20261112.
(Numbers quoted in the registration come from the prototype's seed, and the script's calibration differs by sampling noise only, with the same conclusions.)

### 2026-11-12 22:16 (+13:00) · e357179 · observation
`scripts/growth_fit.py` written and committed before it was run. Calibration shows per-rule 4-point labels `ambiguous` in about 99%+ for
alpha <= 0.06 (any truth), backcast N_log/N 0.58 (log, b = 0.1 y8), 0.77 (b = 0.2 y8), 0.27-0.31 (power 0.06).

### 2026-11-12 22:17 (+13:00) · efeae5b · observation
Ran once (7 s), re-ran byte-identical. G1, G2 pass. P1 143/143, P2 123/143, P3 LOG favoured (S = +71.8; LOG arm mean +87.7, POWER arm -91.8;
p_pow < 0.0005, p_log 0.194), P4 108 vs 35 (p = 7e-10). Per rule 135/143 ambiguous. alpha_hat median 0.059. Details in README "A1 results".

### 2026-11-12 22:17 (+13:00) · efeae5b · interpretation
Log growth describes the slow class over 1e7-1e11 better than a power law, in aggregate and out of sample. It is not shown to hold beyond
1e11, and it does not make the class "unbounded": a log law is unbounded but with a doubling adding ~2.6 cells on a side of ~70. The 5% bound of
P3 was a coin flip under it (predicted 1e11->2e11 ratios 1.03-1.05). Bootstrap p-values treat correlated rules as independent: optimistic.

### 2026-11-12 22:17 (+13:00) · efeae5b · surprise
Both fits slightly over-predict 2e11 for 6 of 8 rules and log over-predicts the 1e7 box by ~1 cell on average: the curve may be a touch flatter
than log (post hoc, not tested). A quick candidate for a future registered check: a saturating form `a - c t^-beta`, which would need five or more points per rule.

### 2026-11-12 22:30 (+13:00) · efeae5b · deviation
Small misstatement in the registration's calibration paragraph: it says truth log is labelled `log` "in at most 2%"; the committed script's calibration
gives up to 2.5% (75 of 3000 at y8 = 120, b = 0.2 y8; the prototype seed gave 2%). No threshold or verdict depends on it.

### 2026-11-12 22:30 (+13:00) · efeae5b · question
Open: would a 1e12 run of the 8 P3 rules distinguish log from a saturating law? Under the 4-point log fit a decade adds b = 8.7 cells (median); a saturating law adds
less. It needs a registration. RLLLR took 55 min for 2e11 on the tiled backend, so about 4.5 h per rule for 1e12.

### 2026-11-12 22:25 (+13:00) · efeae5b · decision
Registered consequences applied (no new measurement): README "A1 results", reader-guide row, atlas wording, `notes/ACTIVE.md`, homepage note, blog post
`2026-11-12-the-five-percent-bound-was-a-coin-flip`, `notebook.ipynb` (reads only `results/`, executed top to bottom with nbclient under `uv run --frozen`, asserts the README counts).
Checks: `growth_fit.py` rerun byte-identical (sha256 csv 09659525..., txt c83df57d...); `blog/scripts/test_atlas.py` (8 OK, after shortening two atlas
strings that the measurement guard rejected), `test_experiments.py` OK, `export_results.py --check` OK, `atlas.py` OK. No Ruby on this box, so the Jekyll strict build is left to CI.
