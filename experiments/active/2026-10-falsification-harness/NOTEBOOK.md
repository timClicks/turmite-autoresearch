# Lab notebook: falsification harness

Append-only. Newest entry last. Never edit an old entry; correct it with a new one
(`corrects: <timestamp>`). Tags: intent, assumption, observation, interpretation,
surprise, decision, dead-end, question, deviation. See `experiments/README.md`.

### 2026-10-22 21:30 (+13:00) · cbe7b40 · intent
Build a harness that attacks a registered claim (perturbed starts, asymmetric colourings, obstacles, off-centre
boards, adaptive search) instead of re-running it longer. Motivation: "chaotic" / "stabilised" labels have rested
on one horizon on the blank board.

### 2026-10-22 21:31 (+13:00) · cbe7b40 · decision
Own seeded runner (`falsify::simulate`) rather than `fast::run`: `Grid::reset` clears only the previous bounding box,
so seeded cells would leak between runs, and `fast::highway_onset` replays from a blank board so it is wrong for
perturbed starts (onset is therefore used only for the blank baseline). `Trail` in `fast.rs` made `pub(crate)`.

### 2026-10-22 21:32 (+13:00) · cbe7b40 · observation
`cargo test --release --test falsify`: 13/13 pass first time. That was suspicious, so mutants were tried:
dropping the start heading is caught by two tests; shifting the obstacle direction window by one step (4001 -> 4000)
is NOT caught; a 10x shift (4001 -> 401) is caught only after widening `radius` to 0..7, `ahead` to 0..15 and
`at` to < 6000 in the property test. The one-step mutant is nearly equivalent (it changes the direction vector by one
step's displacement) and stays uncaught. Test was strengthened for the large mutant.

### 2026-10-22 21:34 (+13:00) · cbe7b40 · decision
`horizon` in a claim is the author's horizon; the harness attacks to horizon * 4^ladder and reports highways by
horizon * 4^k, flagging refutations that appear only after the stated horizon. Added the `blank` class so the claim
as literally stated is always one of the attacks.

### 2026-10-22 21:36 (+13:00) · cbe7b40 · assumption
Predictions P1-P7 in README.md are registered before any run. `RRLR` chosen for P6 because the census records its
highway (384; -4,-4) at onset 256240 (`experiments/archive/2026-10-census-sweeps/results/confirmed_v2.csv`).

### 2026-10-22 · fde1103 · decision
Harness hardening: reject malformed claims and preserve full u64 seeds. Correlated adaptive candidates
and heterogeneous attack distributions cannot justify a pooled binomial interval. Probabilistic highway
claims remain Unsupported pending a separately registered IID sampling design. Shrinking must preserve
the witness on both geometries. No new scientific sweep is part of this hardening pass; concurrently
produced results are left untouched. Release regression checks follow.

### 2026-10-22 22:10 (+13:00) · 20b75ae · observation
Registered run (4.7 s, thread-count independent). Held: P1, P4 (RRRL, 8 counterexamples), P5. Wrong: P3 (RRL survived 545/545), P2's
"Unsupported" half, P7 (adaptive lost to sampling in 3/3). Partly wrong: P6 (13 perturbed RRLR starts escape by 1e5; only the blank start is late).

### 2026-10-22 22:12 (+13:00) · 20b75ae · interpretation
The adaptive attacker is not an adversary yet: its score (escape step) is dominated by board-crossing time. A "Survived" verdict
therefore rests on random sampling alone. Confidence that this explains P7: low; not tested.

### 2026-10-22 22:13 (+13:00) · 20b75ae · deviation
(1) The `late` flag was reworked mid-experiment after the run exposed the escape-vs-onset confound; (2) I rewrote my own unpushed commit
fde1103 to drop another contributor's untracked files that `git add -A` had swept in, so that hash no longer exists (their entry above cites it);
(3) the re-run binary included that contributor's uncommitted edits. A clean re-run is owed.

### 2026-10-22 22:14 (+13:00) · 20b75ae · question
Does RRLR's early perturbed highway (onset near 0) differ in type from the blank one? All 463 counterexamples are (384;4,4)-type, so no.
What makes the blank start 256k steps slower than almost every perturbed start? Open; worth an onset-distribution experiment.

### 2026-10-22 23:40 (+13:00) · 047e395 · observation
Other session halted. Committed its claim-field validation and withdrawal of the pooled interval (91186e3). Promoted `evolve_chain` into `falsify`
and re-ran all five claims from a clean worktree at 047e395: verdicts unchanged, thread-independent; RRRL adaptive evaluations find a different
highway in 126/456 (first run: 8 counterexamples total). Pays the clean-re-run debt from 22:13.
