# Active work and open items

Living index, last updated 2026-10-20 (lattice c-law result added; earlier items as of 2026-10-19 after merging `worktree-paper-figure-proposals`, `8f4b978`, and the lead-effect
reconciliation, `5d866ce`). One line per item: what is open, where it lives, what would close it. Remove an item when it is
done or dropped; record the outcome in the experiment's NOTEBOOK and the relevant note, not here. Scientific claims belong in
`notes/open-questions-hypotheses.md`; this file only tracks what is unfinished.

## Science: open questions

- **Proof track (parallel, started 2026-10-20):** turn simulated regularities into checked macro-transitions
  (`notes/proof-track-2026-10-20.md`). First target: is the `RLRLLL` column sweeper `C(L) -> C(L+g)` for all heights?
  `experiments/2026-10-20-rlrlll-macro-transition/`: P1-P5 held and the family is checked closed for all even m >= 2
  (cycle law 12m + (934, 1058, 898), |x|^2/t -> 3/4). Open: independent assurance, entry, other escapes, a census-wide
  sweeper decider (`notes/proof-track-2026-10-20.md`, Next steps). Single-core runs only; no conflict with the census.

- **First-passage closure (prospective, 2026-10-20):** can depth-crossing kernels predict kappa on independent starts and unseen families, and its size drift? `experiments/2026-10-20-kappa-first-passage/`. Scaffold only; next is oracle/accounting and synthetic calibration, then feasibility. No new measurements or frozen confirmation manifest.
  Proposed work list for it (added 2026-10-20, none started; register predictions in the README before measuring):
  - *Instrument calibration (before trusting any exponent).* Known-answer walkers for theta and z: run the nested-depth and
    survival-tail estimator on the rotor walker (known t^(1/3) radius), a random walk on a growing cluster (theta = 1/2 at fixed
    geometry, negative control) and the mean-field walker (repo mean-field kappa 1.118); reproduce the probe's window-averaging
    convention. Synthetic renewal streams with a planted power-law tail and cutoff tau ~ L^z (known theta, z): check the fit
    recovers z(1-theta) and that censoring does not bias it (the tail-budget calibration covers geometric and mixture laws, not a
    scaling-form family). Censoring accounting: reuse the tail-budget sampler's lower/upper bounds for step-cap cutoffs.
  - *Closing the accounting loop.* Check kappa_inst = (A/P) f_d on the same runs (quasi-static geometry; if it fails, P/A drifts and
    the scaling argument has no footing). Cycle independence: autocorrelation of successive (D, T) pairs (stable means suffice, but
    strong correlation makes finite windows misleading).
  - *Escape mechanism.* Nested-depth crossing probabilities P(reach 2h before returning | reached h) for several h (constant ratio =
    scale-free tail; log ratio gives theta). Local-state ablation: condition on heading, colour phase, then larger neighbourhoods of
    recent history (plateau = local theory; continued gains = collective field organisation). Directional asymmetry via the
    return-gates instrument (its first stage was uninformative). Matched field edits: scramble the field structure the model says
    matters vs a same-size control; the model must predict sign and rough size of the change in kappa.
  - *Sign of kappa below uniform.* Residence-weight test: time-averaged occupation of boundary cells vs a uniform draw over the same
    cells at matched sizes. Moving-boundary coupling: a rotor or memoryless walker whose domain grows at the ant's measured rate;
    does kappa fall below uniform?
  - *Cross-checks.* Show the crossing model contains the failed explanations (dwell, crust depth, square loops) as special cases and
    predicts why they failed. Primary validation: the six-letter family hold-out (`experiments/2026-10-20-kappa-prefix-family-holdout/`),
    fit on some families and beat the training mean on withheld ones. Scale dependence: is fitted z stable across area bands
    (32768, 131072, 524288) as in the tail-budget cohort (the c-law work suggests a size-dependent slope)?

- **Why does the c-law slope b fall with loop length, and what sets the intercept?** Registered Moore-lattice test (follow-up B, `experiments/2026-10-20-lattice-c-law/README.md`): b = 0.775 at loop 4 (z = 8), 0.260 at loop 8; M-lin refuted, M-inv missed its own consistency clause by 0.005, so neither supported. b looks floor-like (~0.26-0.28 at l = 6 and 8), within-lattice doubling of l multiplies b by ~0.3. Intercept is lattice-set (1.3 for z = 3, 4; 2.4 for z = 6, 8), not loop-set. No mechanism; closing needs a derivation of N_b(l) and the intercept, then a registered test on another lattice.
- **Why is the hex lead fit so noisy, and what sets its intercept?** Follow-up A (2026-10-20, registered, `experiments/2026-10-20-lattice-c-law/README.md`) removed the lacy outlier (beta < 0.8) and
  separated tail letter types: clean r-lead b = 0.262 [0.21, 0.31] (R^2 only 0.42), R-lead 0.876 (R^2 0.69), b_r/b_R = 0.30 [0.24, 0.37]; tail letter type adds ~nothing
  (R-lead CV gain +0.014, r-lead none). Intercept stays 2.4-2.8. Unexplained scatter remains; candidate features untested: second run length, letters 6-8.
- **Where does the lead slope of 1/c live, by colour? (follow-up, `experiments/2026-10-20-lattice-c-law-colours/`, 2026-10-20).** The registered circulation
  decomposition failed (P1, P2, P6 failed; P3 passed on a flawed interior-contaminated estimator and is not counted). Post hoc: the slope lives in
  boundary reads at the circulating colours, ~0.95 per colour (hex R), 0.8 (square), 0.65 to 0.35 (tri), 0.7 to 0.5 (hex r); lag-ell ring returns carry them
  only on the square lattice; hex r fills ring centres (15% of lead-1 births). Shareable `notebook.ipynb` built and published (38 blog notebooks). Next: boundary-only episode segmentation, and what sets the per-colour survival plateau.
- **Origin of the c law constants a = 1.4, b = 0.68** (1/c = 1.36 + 0.70 lead). Candidate: loop-formation probability x 4 steps
  per revolution / births per chain. Also why letters 5-8 matter. `experiments/2026-10-19-c-law-mechanism/README.md` (Stage 3,
  "Still open"), `experiments/2026-10-19-c-law-mechanism/NOTEBOOK.md` (19:22 closing entry).
- **Local renewal mechanism for c:** rich lookup lacks pilot support (`0fa4db2`). Exact-rule finite colour-memory model then
  fails M1/M2 at r=4 and r=8 (`a878d5e`): nearby phase clocks plus uniform forgotten phases miss the cost/budget. An exact
  return bound ensures r=4 directly changes only >16-step phases. Long-budget loss can be hidden by more short loops.
  Read/write/pair closures also fail native return-budget and birth-wait tests (`94516e5`), rejecting physical-time stretching as a sufficient rescue. Next proposal: one coupled phase edit preserving two turns, with full memory thereafter; register branching/censoring and response horizons before measuring.
  Main cohort remains unopened. `experiments/2026-10-20-c-law-renewal/README.md`.
- **S-arm kappa drop (d = -0.198) is unexplained.** A total effect, not area-conditioned; confounded with flip direction
  (L>R +0.15, R>L -0.21, post hoc). Needs direction-balanced flips. `experiments/2026-10-19-c-law-mechanism/README.md` (Stage 4
  results), `experiments/2026-10-16-kappa-leadrun-fresh/README.md` (Part B addendum, Proposal 1).
- **Does lead have any direct effect on kappa?** Current bound |b| < ~0.06 per step given ln c, one cohort, one window,
  survivor-selected. A tighter test needs a mediator-free kappa (late windows only) or a second cohort.
  `experiments/2026-10-19-c-law-mechanism/results/stage4_analysis.txt`, `notes/open-questions-hypotheses.md` (Reconciliation).
- **Mixed-turn loops (period 6/8) and opening-transient loops** were not tested; the square-loop failure only covers same-turn
  2x2 loops. (CI on the 8% figure done 2026-10-20: 7.6% [3.2, 12.3] at lead 6.)
  `experiments/2026-10-16-kappa-square-loop/NOTEBOOK.md` (22:58 end-of-session entry), `experiments/2026-10-16-kappa-square-loop/README.md` (Results).
- **Blob-regime boundary** of the c law between sparse-background density 0.2 and 0.7 (kept fraction 0-2% at density 1).
  `experiments/2026-10-19-c-law-mechanism/README.md` (Stage 3 results).
- **kappa/kappa_unif distribution, location (open):** why the median is 0.81 x kappa_unif (below every walker reference).
  `experiments/2026-10-16-kappa-uniform-baseline/results/census_spread.txt`, `notes/open-questions-hypotheses.md`.
- **kappa spread, remainder (open):** budgeted 2026-10-20 (post hoc, `experiments/2026-10-20-kappa-spread-budget/`): about 0.15 start
  noise, 0.47-0.54 prefix-predictable, 0.31-0.38 rule-determined but unexplained. A registered held-out comparison
  (`experiments/2026-10-20-kappa-spread-features/`, F1-F4 held) found the predictable part is in the first 8 letters (R^2 0.62),
  not the last 8 (-0.11) or composition (+0.08; adds +0.008 to the prefix). A second registered test
  (`experiments/2026-10-20-kappa-prefix-runs/`, H1-H3 FAILED, H4 held) found the lead alone has R^2 ~0 unconditionally and the signal
  accumulates over the first four runs (0.25, 0.34, 0.48 vs 0.62 for 8 letters). A registered per-position ablation
  (`experiments/2026-10-20-kappa-prefix-ablation/`, A3 FAILED) found the information is not front-loaded: loss from ablating
  position 5 is 0.40, positions 2-7 each 0.2-0.4, position 8 0.07. A registered additive comparison
  (`experiments/2026-10-20-kappa-prefix-additive/`, B2 FAILED) found additive letter-by-position 0.11, plus pairwise 0.35, vs 0.62 for
  the lookup: the signal needs higher-order interactions. A registered family hold-out
  (`experiments/2026-10-20-kappa-prefix-family-holdout/`, D2 and D3 FAILED) then found every model falls below the training mean on
  held-out 6-letter prefix families (lookup 0.59 -> -0.16; pairwise 0.30 -> -0.69): the signal is family membership, not a
  transferable letter-level rule. Still open: a family random effect plus within-family letter structure, other family
  granularities (4, 8 letters), and what the unexplained third is (middle letters, dynamics).
- **CLAIMED 2026-10-20 (compute-heaviest item): the 10^11 survivor census is running.** Chunks 20-27 were killed ~2026-10-14 (only 20-26 had `.done`); resumed with `run_1e11b.sh`, then restarted at 21:36 with checkpointing (`run_1e11c.sh`, `TURMITE_CKPT_EVERY=5e9`, checkpoints in gitignored `scratch/ckpt/`, binary sha in `results/h1e11/resume_binary_ckpt.sha256`, log `run5.log`; a kill now loses <=5e9 steps per rule; rerun the same script to resume), ~33 chunks x 35-50 min, i.e. roughly a day of all cores. Do not start other heavy jobs. Prediction already registered in `notes/frontier-2026-10-13-results.md` (~6 highways in 492, range 2-11); `b5_stats.py` must be re-pointed at all chunks before analysis.
- **Late-highway tail / unresolved rules** and why `RLRLLL` switches to a period-3 column sweeper (trigger unknown).
  `experiments/2026-10-13-highways-unresolved-rules-1e10-1e11/`, `experiments/2026-10-13-g1-ribbon-breakout/README.md`,
  `experiments/2026-10-13-census-sweeps/results/unresolved_le10.txt`.
- **Paper figures 1-5 are built** (2026-10-20: `fig:walker-map`, `fig:edge-gap`, `fig:layers`, `fig:prefix`; late-switch earlier). `rebuild_figures.py`
  confirmed 2026-10-20 to regenerate all figures and `main.pdf` cleanly. Proposals 6-8 remain unattempted.
  `notes/paper-figure-proposals-2026-10-16.md`, `notes/handover-paper-figures-2026-10-17.md` (stale for item 4).

## Uncommitted work in progress (do not lose)

- **c-law renewal work is active in its owning session:** instrument and oracle tests committed (`ccbd9cd`), release suite passes,
  finite-memory model/clock (`c826721`) and failures (`a878d5e`) committed. All own jobs are terminal. Do not replace its pilot
  families, relaunch completed pilots, or open main outcomes before the next mechanism is registered.
- The n-rotor reference, uniform-baseline notebook edit and blog index/post listed here earlier are committed (`18b79d7`,
  `3117e1b`); `main` equals `origin/main` (`bf4ca54`) as of 2026-10-20 00:42.
- **rulepat, branch `claude/rule-pattern-experiment-aa95e3`**: committed 2026-10-20 as `275d52b` and merged into local `main`
  on 2026-10-20 at the user's request (reader guide added, covering only the early README steps). Still open: its gitignored
  `dumps/` (192 MB) and `scratch/` (3 MB) exist only in the worktree, so archive them before removing it; its README
  census steps (C1-C4) were not reviewed here.

## Repository housekeeping

- **Jupyter**: `ipykernel`, `nbformat`, `nbclient` added to `pyproject.toml`/`uv.lock` (`7df6d35`). The leadrun-fresh notebook's Proposal 2 bounds are not in it (rebuild with `scripts/build_notebook.py` if wanted).
- **Refresh `blog/index.html`** (convention in `AGENTS.md`): the c-law and lattice results were already on it; a kappa-spread highlight (family hold-out) was added 2026-10-20. Not yet on it: lead-slope-by-colour. A null-result post
  (`blog/_posts/2026-10-20-where-kappa-is-not.md`, with reader guides for the three 2026-10-20 kappa experiments) was added 2026-10-20;
  the post itself is not linked from the index cards. The experiment pages were
  re-rendered 2026-10-20 (from a worktree under WSL set `GIT_DIR=/mnt/f/Code/turmite/.git/worktrees/<name>` and `GIT_WORK_TREE=$PWD`).
- **Stale worktrees and branches** (nothing deleted). On 2026-10-20 tracked work was committed on their own branches
  (`agent-a810708e829d8af34` as `4cb0261`, `g1-builder-structure` as `b985636`, rulepat as `275d52b`), but **gitignored data
  exists only in the worktrees and is lost on removal** (checked with `git status --ignored`): `g1-builder-structure/dumps/`
  73 MB (the only raw input for `g1_wake_extract.py`; regenerating takes hours), `rule-pattern-experiment-aa95e3/experiments/2026-10-14-rulepat/dumps/`
  192 MB and `scratch/` 3 MB (plus `target/`, rebuildable), `agent-a810708e829d8af34/experiments/2026-10-16-gpu-probe-port/scratch/` 19 MB.
  Archive what matters before any removal. `g1-builder-structure` is also the only home of `examples/builder_dump.rs` and
  `notes/g1-builder-structure-2026-10-14.md` (handover item 3). Deletion needs the user's go-ahead:
  - `.claude/worktrees/agent-a810708e829d8af34` and branch `backup/pre-census-split`: same commits; the unique `39df9f2` content is in
    `main`. Its uncommitted GPU probe port (`src/gpu/probe.rs`, `experiments/2026-10-16-gpu-probe-port/`) is an earlier attempt at what
    `main` has as `gpu_probe`; checked 2026-10-20: the two `results/` dirs differ (the port has `full_L2400*`, `cpu_full.*`, `block_sweep_*`; `gpu-probe` has the bench files), so keep the port's results before discarding.
  - `.claude/worktrees/g1-builder-structure`: old `data/` layout; content appears superseded by `main`. Checked 2026-10-20: no
    `TODO(G1)` remains in `main.typ`. Still archive `dumps/` (73 MB) first.
  - `.claude/worktrees/paper-figure-proposals` (locked): merged into local `main` on 2026-10-20 (user-approved local merge, not
    pushed; `main.typ` and `rebuild_figures.py` auto-merged, `ACTIVE.md` and `main.pdf` resolved by hand / recompile). Checked 2026-10-20: no commits
    beyond `main`; the worktree can be removed when finished.

## Closed (for reference, do not reopen without new grounds)

- **Paper follow-up revision (2026-10-20):** c law, corrected uniform reference,
  conditioning check and negative-test statuses incorporated; PDF rebuilt and
  visually checked, release tests passed. Recipe and output hash in the paper README.

- `experiments/2026-10-16-kappa-square-loop/`: H-loop dead at this scale (P2 failed).
- `experiments/2026-10-16-kappa-loop-surgery/`: closed unrun on 2026-10-19 (gate failed; premise further weakened by the collider result).

