# Lab notebook: leak titration

Append-only. Newest entry last. Never edit an old entry; correct it with a new one
(`corrects: <timestamp>`). Tags: intent, assumption, observation, interpretation,
surprise, decision, dead-end, question, deviation. See `experiments/README.md`.

### 2026-10-28 20:59 (+1300) · 1b14a1e · intent
Owner asked for a leak-titration experiment: raise the probability of a random turn on fresh ground and
look for a percolation-like threshold where compact growth fails, with a forced-L control. Reason: EF = 0.1
leaves all six core rules compact (+0.028 in a), EF = 1 makes all six porous (+0.19..+0.29), nothing between.

### 2026-10-28 20:59 (+1300) · 1b14a1e · decision
Read the record before designing. Three departures from the proposal, all in README: (1) added EF 0.6-0.9
(the proposed grid jumps 0.5 -> 1.0); (2) forced L at EF = 0 was already run in wall-vs-memory Stages 3/3b
(0 porous of 318) so the control becomes a leak on a forced-L base, run through `fs:` with a 20-slot set (no
new Rust); (3) dropped c*kappa, an algebraic identity that cannot fail. Pruning preflight: no member
overlap; the EF = 0.1 / 1 / forced-L rows are deliberate byte-for-byte replication gates.

### 2026-10-28 20:59 (+1300) · 1b14a1e · observation
Synthetic calibration of the sharpness statistic S (no ant data). On a 0.1 grid a truly sharp transition
(logistic width 0.05) has median S about 0.43, not near 1, so my first-draft cut of 0.45 would have missed it
more often than not. Switched to the median of S over the 6 rules with cuts 0.40 / 0.28:
`results/calibration_sharpness.txt`. At seed sd 0.05 smooth curves are only flagged smooth 17-41% of the
time, so "unresolved" is the likely failure mode of H-smooth.

### 2026-10-28 20:59 (+1300) · 1b14a1e · decision
Registered hypotheses, priors (smooth 50 / sharp 25 / unresolved 25), gates G1-G5 and predictions P1-P5 in the
README before writing `run.sh` or `analyse.py`. Cuts are frozen. Stage B and C are conditional and need their
own registration.

### 2026-10-28 20:59 (+1300) · 1b14a1e · question
Could the leak on revisited cells (EV) show the same shape? Not in scope; recorded so it is not forgotten.

### 2026-10-28 21:15 (+1300) · 7608a6f · observation
Ran the 1068 specs (14 min). Gates G1-G5 pass (102/102 and 6/6 byte-identical to the committed rows). Scoring: P1 arm R
unresolved (M = 0.289 against a smooth cut of 0.28), P2 held (median EF_50 0.30), P3 held (5/6), P4 failed (1/3), P5 unresolved
(median |D| 0.10). No coexistence cells, no sd peak. See README "Results".

### 2026-10-28 21:15 (+1300) · 7608a6f · surprise
In arm L the two forced-L highway rules are already porous (a 0.88-0.90) at EF = 0.1: a 10% leak sends an ordered structure
straight to porous growth, skipping the compact stage. Post hoc, three-rule-thin elsewhere.

### 2026-10-28 21:15 (+1300) · 7608a6f · interpretation
The data lean smooth (steepest 0.1-step carries at most 43% of the rise, class passes through a wide intermediate band, no
coexistence) but the frozen rule says unresolved and I keep that word. I expected the rise to be spread out to EF = 1; it
saturates by about 0.5. My prior put median EF_50 near 0.5; it came out 0.3 (inside the registered interval, at its edge).

### 2026-10-28 21:15 (+1300) · 7608a6f · decision
Stage B not triggered (M < 0.34). No pruning-index signature. Next candidates in README; none registered.

### 2026-10-30 09:20 (+1300) · 8904956 · deviation
The registered code oracle (`cargo test --release --locked --test hybrid_walker --test fresh_set`) was not recorded here at
run time. Ran it on 2026-10-30 at `8904956`, whose `src/`, `tests/`, `Cargo.toml` and `Cargo.lock` are unchanged since the run
commit `7608a6f` (`git diff 7608a6f 8904956` on those paths is empty): fresh_set 4/4 and hybrid_walker 6/6 pass. This is a
check made after the run, not a substitute for recording it at the time.

### 2026-10-30 09:20 (+1300) · 8904956 · decision
Write-up only, no new runs and no new claims (Grok Bot, AI research agent). Added `scripts/build_notebook.py` and the
executed `notebook.ipynb`. It checks `probe.csv` and `specs.txt` against the hashes in `provenance.txt`, re-runs the frozen
`analyse.py` on a copy of the committed `probe.csv` (analysis.txt, runs.csv and curves.csv come out byte-identical; the PNG
is not compared because it is not byte-stable), and redraws the dose curves and class shares from the committed CSVs. Also
added the blog post `2026-10-30-turning-up-the-leak`, a homepage card, a figure entry, and the post in the atlas
`cube-root-growth` topic. The atlas wording was narrowed to "no sharp threshold visible on the registered grid". The verdict wording
stays "unresolved" everywhere. No `experiments/README.md` line was added: that file maps old paths from the
2026-10-28 reorganisation, and this experiment was created afterwards directly in `active/`.
