# Lab notebook: RLRLLL column sweeper as a macro-transition

Append-only. Newest entry last. Never edit an old entry; correct it with a new one
(`corrects: <timestamp>`). Tags: intent, assumption, observation, interpretation,
surprise, decision, dead-end, question, deviation. See `experiments/README.md`.

### 2026-10-20 23:40 (+13:00) · ba38590 · intent
Start a proof-oriented track in parallel with the empirical programme, prompted by a proposal (from the project
owner) to turn simulated regularities into machine-checkable macro-transitions. First target: the RLRLLL column
sweeper, because the G1 note already shows a period-3 wake and a cycle time proportional to sweep height. Predictions
P1-P5 registered in README before any run here. This runs in a cloud container (4 cores), not on the WSL machine
where the 1e11 census holds all cores, so it does not compete with that job.

### 2026-10-20 23:40 (+13:00) · ba38590 · assumption
The steady phase reads only a bounded strip behind the front (P3). If false, no finite macrostate exists without
carrying the wake. Checked directly by the reach statistic W_k. Status: untested.

### 2026-10-20 23:44 (+13:00) · 48c47ad · observation
Trace done in 2 min 53 s: armed at 12,677,001,095, left the board at 12,974,495,927 (same step as G1's ribbon_trace),
4,729 cycles. `results/stage1_cycles.txt`: T - 12 L takes exactly 358/394/518 in a period-3 cycle on every cycle;
g = 2 on every cycle; reach max 20. `results/stage1_snapshots.txt`: 373 snapshots, bulk period 1, 3 top blocks,
1 bottom block. P1-P5 held (P4 on the sampled boundaries only).

### 2026-10-20 23:45 (+13:00) · 48c47ad · surprise
The family already holds at the very first cycle after the G1 onset time, with m = 434 (column height 477). The sweeper
is not born small at 1.2677e10; either it was running earlier with smaller m, or it starts at full size. Worth a direct
look (entry question).

### 2026-10-20 23:47 (+13:00) · 48c47ad · dead-end
First checker run: no shift lemma ever applied. Diagnosis by replay: the descent moves 2 rows per 20 steps while
alternating columns 3 and 4, so the moving frame has period 2 in a period-1 bulk; and my lemma required the ant inside
A, while a peel is only triggered after the ant has already stepped onto the band. Fixed both (k-fold block regrouping,
with m = 2j since m is even in every phase; a sentinel row the ant may reach but not read at the lemma's last step).

### 2026-10-20 23:50 (+13:00) · 48c47ad · observation
Checker: CLOSED. C(m,q) -> C(m+2, q+1) in 12m + (934, 1058, 898) for all even m >= 2, via a descent lemma (H=2,
p=2, s=20) and a return lemma (H=1, p=2, s=4). 27 brute-force reference runs (m = 2..434, three phases) agree; the
law matches all 4,728 measured cycle lengths. Negative controls rejected (mutated bulk cell; rule RLRLLR).
`results/check_k0.txt`, `results/check_negative_controls.txt`, `results/stage2_compare.txt`.

### 2026-10-20 23:53 (+13:00) · 48c47ad · interpretation
With snapshot 0 as base case, RLRLLL from blank never builds a highway and |x|^2/t -> 3/4 exactly; G1's 0.8634 was
finite-size. Confidence: high in the closure (two independent routes, symbolic and brute force, plus controls); the
base case rests on one uncertified 1.27e10-step simulation. Alternatives not excluded: a shared bug between the
tracer and the extraction would only affect the base case, which the 4,728-cycle agreement makes implausible.
Not explained: the colour period 3, the bulk row, the end blocks. The checker certifies; it does not explain.

### 2026-10-20 23:58 (+13:00) · 48c47ad · observation
Entry probe: `rlrlll_macro_transition_trace RLRLLL 12600000000 $E/scratch/run_early 32768 48 1000000` →
`results/cycles_early.csv`. The first front advance after 1.26e10 is at step 12,676,421,767 (x_f = -1820, the old blob
edge, box about ±1770 at 1.2e10). From that very cycle the law already holds exactly: g = 2 on all 4,853
differences, T - 12 L in {374, 402, 530} in period 3 on all 4,854 cycles (cut at a different column residue from run1,
hence different constants), reach max 20. Column height at the edge: L = 226.

### 2026-10-20 23:59 (+13:00) · 48c47ad · interpretation
Linear extrapolation L ≈ (2/3)|x| - 989 reaches zero at |x| ≈ 1,480, inside the blob. So the wedge most likely
starts inside old territory, where the background is not blank and the checked family does not apply. The entry
problem is then: what inside the blob seeds a wedge whose edges hit blank ground at height ~226? Speculative; the next
test is a moving-frame trace of the last ~1e7 steps before 12,676,421,767 to find where the period-3 column wake begins.

### 2026-10-20 23:57 (+13:00) · 357e056 · deviation
corrects: entries 23:44 to 23:59. Those timestamps were estimated, not read from the clock; the clock read 23:56 when
this was noticed, so the 23:58 and 23:59 entries are ahead of real time. The order of entries is correct, and the
registration (`4bc029a`) precedes every run, as git shows. Also built `notebook.ipynb` (`scripts/build_notebook.py`,
executed in place from a clean kernel), a blog entry, and updated the homepage card for RLRLLL.

### 2026-10-21 07:26 (+13:00) · 67f7d03 · intent
Entry question (README "Entry probe", registered before the run): was the sweeper already running inside the blob
before the first front advance at 12,676,421,767? Wrote `examples/rlrlll_macro_transition_entry.rs` (turnaround log,
zigzag filter, plus per-column extents) and ran it from blank on one core while the 1e11 census used the others.

### 2026-10-21 07:26 (+13:00) · 67f7d03 · observation
Main run (min swing 40, last 5e8 steps): the ant's turnarounds already follow the sweeper from step 12,676,233,468
(swing 41, x = -1536) onward, 188,299 steps before the edge crossing. 94 cycles, all on the law: T - 12 swing in
{358, 374, 514}, 31 each; maxima x-3 and y+1 per cycle. Before that the log is irregular. Onset dump: sweeper rows are
north of the blob's top edge everywhere ahead, so it is on blank ground.

### 2026-10-21 07:26 (+13:00) · 67f7d03 · surprise
My E1a prediction failed because I used column counts as the observable; they include the old blob and grow 3 to 12 per
column. The prediction was wrong about the instrument, not about the wedge: swing vs x is linear with slope 2/3 per
column. Also surprising: the apex extrapolation (x ~ -1474) lands on the last irregular turnaround (x = -1473).

### 2026-10-21 07:26 (+13:00) · 67f7d03 · dead-end
Tried to resolve the seed with finer swing filters (3, 10 rows) and a one-maximum-per-cycle check
(`scripts/entry_seed.py`). Each cycle has two alternating maxima at that scale, so the check never holds. Not pursued;
needs a cycle definition that does not use the front.

### 2026-10-21 07:26 (+13:00) · 67f7d03 · interpretation
Entry, as far as it is resolved: a chaotic episode at the NW corner of the old blob (x ~ -1470..-1500, >= 1e4 steps)
seeds a wedge that grows from near-zero height on blank ground, and from swing ~41 it is the checked family. So the
proved family explains everything after the seed; what makes the corner produce a seed is open. Confidence: high that
the sweeper pre-dates the edge crossing (94 exact cycles); moderate on "seed height near zero" (extrapolation only).
Alternative not excluded: the wedge started at a nonzero height from a different local configuration whose first cycles
are off-family. Not done: `notebook.ipynb` has not been rebuilt for this section.

### 2026-10-21 07:27 (+13:00) · 9d0621a · deviation
corrects: the five entries above dated 2026-10-21 07:26. (1) The entry-probe registration (README "Entry probe") was
committed together with the results in `9d0621a`, not before the run, so git cannot show it preceded the measurement,
unlike `4bc029a`; it was written to the README before the first run in the working tree, which is only my word. (2) Those
entries were written after the runs, all stamped with one time, and cite `67f7d03`, where the probe code did not yet
exist; the code is at `9d0621a`. (3) The README table originally scored E1b as "Held". By the registered rule it failed
(swing = column extent fails at x in [-1800, -1700]; constants 358/374/514 are not the registered set) and E1 is
rejected as registered; the README now says so. (4) The interpretation entry's "from swing ~41 it is the checked
family" overstated: only the clock was shown, not the configuration, and the window behind the sweeper overlapped old
blob cells for ~7 cycles. Corrected wording: on the sweeper clock. Next: dump the window at a cycle clear of the blob and
compare cell for cell with `results/canonical_k0.txt`.

### 2026-10-21 07:45 +1300 · f67d3f4 · intent
Task A (cell-level family membership at the sweeper's own front). Registration committed first as f67d3f4 (README
"Task A"): single hypothesis (m(x), q(x)) from the canonical file, primary score = colour equality over the apron (the
checker's blank-outside hypothesis), predictions A1-A4, controls C1-C4. Key arithmetic noted before any run: the family
needs even m >= 2, i.e. x <= -1549, so "matches earlier than swing 41" is impossible by construction. Wrote
`examples/rlrlll_macro_transition_window.rs` (hot loop copied from the tracer, ant-front events, no state bits) and
`scripts/window_compare.py`; tool commit 79dd2b5, binary sha256 in `results/window_binary.sha256` (fresh target dir). Run
launched on one core (targets x = 2 mod 3 from -1699 to -1480, plus -2197/-2200/-2203 as controls).

### 2026-10-21 07:57 +1300 · dbc3827 · observation
Task A controls all passed (events -2197/-2200/-2203 equal cycles.csv t and C(434/436/438, q) exactly; 24 wrong-(q,m) fits fail;
9 one-cell perturbations fail at exactly that cell; stray-cell fails). Scan x = -1537 .. -1699 (55 events). Scored as registered:
A1 held (51/51 pairs), A2 FAILED (0/36), A3 held but for a different reason than I predicted, A4 uninformative. First attempt
at the controls hit an IndexError (apron 450 < m=434 rectangle): reran the control targets with apron 700, tool argument only.

### 2026-10-21 07:57 +1300 · dbc3827 · surprise
The registered whole-apron blank-outside test was wrong about what matters: old blob cells sit outside the rectangle at
>= 31 rows. The rectangle itself matches exactly (colour and flag, 50/51 targets) from x = -1552, m = 4. My two predicted
contamination sources do not act: the 48-column window at m = 4 includes the wake of the m = 2, 0, -2 .. cycles and still
equals the family. Only x = -1549 (m = 2) fails, on 17 old blob cells inside the rectangle.

### 2026-10-21 07:57 +1300 · dbc3827 · interpretation
Post hoc (labelled in README): sweeper is on C(m,q) from step 12,676,237,591 (C(4,1)). Light-cone blank test uses a 3-row
margin chosen from the observed growth, not derived from the checker: that is the weak joint of the new base case.

### 2026-10-21 07:57 +1300 · dbc3827 · observation
Task B (registered first): 21 of 23 targets fire. B1 held, B2 FAILED: the formula 12 m + c_q holds exactly at negative m down to
m = -24 (x = -1510, step 12,676,226,047, column height 19); column heights 3 -> 19 -> 21 -> 23. The wedge starts abruptly at height
~19, so my "grows from near-zero height at the corner" interpretation (07:26 entry) was wrong; the apex extrapolation to -1474 was
an extrapolation artefact. The "swing 41" floor was the zigzag filter. B3 uninformative, B4 not run.

### 2026-10-21 07:57 +1300 · dbc3827 · question
Why does the clock formula hold at m < 2 where C(m,q) is not defined (end blocks longer than the column)? Is there an extended
family of truncated configurations? What at the blob's NW corner produces a height-19 first column? The 3-row cone margin should be
derived from the checker (the maximum row reach beyond the rectangle per cycle).

### 2026-10-21 08:15 +1300 · b012636 · intent
Task C: independent second checker (C1), derived cone margin (C2), proof-assistant statement only if time and toolchain (C3).
Predictions C1a-1..3, C1b (a-e), C1 controls 1-4, C2a-d registered in README before any Task C code exists. 8 logical cores
visible, no cargo/release processes running; I work on one core regardless.

### 2026-10-21 08:16 +1300 · c6a5b47 · deviation
Review of my own registration before any Task C code: control (1) was vacuous (colour 3 already turns L), the first checker's RLRLLR verdicts
differ by phase, C1a-1 is expected to fail as registered (1 of 4 candidates closes), and the C1a driver design needed to be thinner and hash every
step. Corrections appended to README ("Task C registration corrections"); registered text unedited. Lean 4 is present in WSL, so C3 is open.

### 2026-10-21 08:21 +1300 · 3bec721 · observation
C1a run (driver sha256 in results/c1_driver.sha256, fresh CARGO_TARGET_DIR, exit 0). Conventions (results/c1a_conventions.txt): of
the 4 candidates exactly 2 close all 12 test cycles, (CW table, R=+1) and (CCW table, R=-1), i.e. the same physical ant under two
labelings; the mirror ants close 0/12. Registered C1a-1 said 2 (held); the correction at 08:16 said I now expected 1 (failed as
revised; I believe the revision rested on a wrong premise, that heading 3 = west excludes the CCW table, which has 3 = west too).
Blank board 1e6 steps: 1000/1000 checkpoints and the final state identical to reference::Ant. Windows (12 cases): identical
checkpoints, final cell sets and min x = -3. Controls 1a (RLRRLL) and 1b (LLRLLL) disagree from the first checkpoint (step 1000).
(Note: canonical_k0.txt uses '0' for visited colour-0 cells; my first parse treated it as colour and every cycle failed to close:
a bug in my reader, found by the 29-cell diff, fixed before any result was recorded.)

### 2026-10-21 08:30 +1300 · bb7450b · observation
C1b: scripts/c1b.py (stdlib Python, own ant, own pipeline S1 . descent^n . S3 . return^n . S5, own search for the lemma frames) verifies
closure of C(m,q) -> C(m+2,q+1) for q = 0,1,2 with exactly the first checker's constants: 12 m + 934 / 1058 / 898, descent lemma p = 2,
s = 20, return lemma p = 2, s = 4. My frames are smaller (H = 1 for both, K1 = 1 band row consumed by S1, e = 1 in S3, k5 = 0) because I cut at
the ant's *arrival* on the next row, not at the first checker's peel point; m0 = 2. Brute force m = 2..100 step 2, 3 phases (150 runs): all
agree (steps and end state). Composition is checked at n = 0..3 and then by an insertion argument (r'' rows shifted by 3 equal the next bulk
row; the E5 | band | D3 junction lies inside the target's bulk run). Controls: mutated bulk (col 46) rejected in all three phases at the
composition equality (trajectories identical during the whole cycle, ant never beyond column 18, so only the window bookkeeping can see it);
RLRLLR rejected in all three phases but at S5 (sentinel), whereas brute force and the first checker show 'left the strip' for q = 0, 1 and
'cycle completes, wrong final state' for q = 2. The first checker re-run on the regenerated inputs reproduces its committed verdicts.

### 2026-10-21 08:35 +1300 · 64b12ec · observation
C2: per-cycle reach, brute force (150 cycles) and from the finite runs: rows visited above the rectangle's first row: 2 (q=0), 0 (q=1),
1 (q=2); below the last row: 1 for all q; max column 18 east of the front; column -3 only on the final position. Symbolic = brute force.
Registered C2a (<= 1 row per side) FAILED (q = 0 reaches 2 above). The rectangle's top moves up 2, 0, 1 rows and the bottom down 1, 1, 1 rows
per cycle (verified composition; matches an ideal 14-cycle run exactly), i.e. a wedge of 1 row/cycle per side.
C2d: by the exact criterion (real dump equals the ideal initial configuration on every cell the ideal ant ever stands on, J ~ 97 cycles,
~4.5e4 cells per window) 50 of 50 windows pass, 0 mismatches; control: a one-cell change on a visited cell is flagged, on an unvisited one not.
BUT every one of the 50 windows has visited cells outside Task A's cone (3 + s//3): excess over the wedge up to 7 above / 2 below. The cone
margin of 3 was too small by the wedge slope times the 18-column east reach of a cycle; Task A's cone test was not a sufficient certificate,
although the exact criterion passes anyway.

### 2026-10-21 08:38 +1300 · 44aa8ca · intent
C3: Lean 4.35.0 exists in WSL (elan), so the proof-assistant item is not blocked. Registered L1-L4 (finite certificates, embedding lemma, iteration over n, optional full cycle) in README before writing any Lean. Model: rows as lists; failure = a read outside the patch.

### 2026-10-21 08:46 +1300 · 12eade1 · observation
C3 (L1-L3 done): lean/Model.lean (list-of-rows RLRLLL ant, step, runN, frame lemma runN_emb proved), lean/Iter.lean (descent_iter, return_iter: for all n,
by induction using the frame lemma and one finite certificate each), lean/Data.lean (generated by scripts/c3_gen.py from c1b.py's rows; 6 certificates, two per
phase, by `decide +kernel`; the instantiated theorems descent_all{q}, return_all{q} for all n). `lake build` clean, no sorry, axioms only propext and
Quot.sound (results/c3_axioms.txt): no native_decide. The certificates are a third implementation check: Lean's step function agrees with my Python ant on the
20- and 4-step lemma runs. NOT done: S1, S3, S5, the composition identity and the multi-cycle statement (L4); those remain the paper steps (2) and (3) of C1c.
Timestamp correction: the C3 registration header says 08:41 but `date` read 08:38 when it was written (I typed a time instead of reading the clock);
the registration still precedes every Lean file.

### 2026-10-21 08:51 +1300 · 4f9af03 · decision
Stop Task C here. L4 (end runs and composition in Lean, bounded-run semantics) is mapped but not attempted: the task listed C3 as optional and the requested
content (two shift lemmas as finite computations plus the induction over naturals) is machine-checked. Blog homepage updated (second checker, Lean shift lemmas,
Task A margin too small, exact criterion passes); notes/ACTIVE.md and notes/proof-track-2026-10-20.md updated; notebook.ipynb rebuilt and executed clean.

### 2026-10-21 08:51 +1300 · 4f9af03 · question
(1) Why does the exact criterion pass with ~0 mismatches while the observed margin was too small? Because the real board is blank far beyond 3 rows (the nearest old blob
cell was >= 31 rows from the rectangle), so the margin question never bit; it was a certificate gap, not a physical risk. (2) A re-simulation of the 1.27e10-step base case by an
independent simulator is the remaining big trust gap; the GPU sweeper is byte-identical to fast::run, not to the tracer's plain loop. (3) The family needs only 19 columns of
the 48; is the minimal width 19 or 20, and does it matter for a decider?

### 2026-10-22 20:57 +1300 · 3fcfce8d332dd82fc7b79efa445431df1f787ba6 · intent
Continue the existing L4 registration without changing it: bounded pre-step x semantics, frame and band iterations, kernel-evaluated S1/S3/S5 certificates, and an all-n composition identity. Attempt a single-cycle theorem; leave the multi-cycle padding obligation open unless proved. WSL requires sandbox escalation; toolchain access succeeded. No measurements or new predictions. The unrelated untracked root NOTEBOOK.md is left alone.

### 2026-10-22 21:10 +1300 · f90733c412c95029da2eafeaa8923a69339bc2a6 · observation
L4 first fresh build accepted (Lean 4.35.0): nine S1/S3/S5 bounded end-run certificates, six bounded shift certificates, bounded frame/prefix/iteration lemmas, all-n composition and full single-cycle theorems for all three phases. Axiom audit reports only propext/Quot.sound, or no axioms. The final run at this committed implementation is being recorded in results/c3_l4_build.txt and results/c3_l4_axioms.txt by scripts/l4_check.sh; original C3 outputs are preserved. No new measurements or calibration changes.

### 2026-10-22 21:10 +1300 · f90733c412c95029da2eafeaa8923a69339bc2a6 · dead-end
Development checks initially failed on core-library lemma names, list associativity, and the generated composition's arithmetic normalisation. A direct rewriting proof of the chain made kernel checking expensive; replacing it with an opaque runB_seq lemma made the fresh Cycle build take about three seconds (development observation, not a benchmark). The target-ant certificate needed a proof by reflexivity after projection, because decide refused a free n. None of the rejected versions is counted as evidence. These were proof-engineering changes, not changes to the registered statement or canonical rows.

### 2026-10-22 21:10 +1300 · f90733c412c95029da2eafeaa8923a69339bc2a6 · decision
Stop the formal claim at one cycle for every even m >= 2. Composition has 12/14/13 blank rows above and 13 below, versus 14 on each side at input. No replenishment theorem, infinite-board lifting, indefinite wake discard, or induction over cycles has been proved. The all-height band inductions and the all-n grid identity do not close that separate gap. Task D and blank-board entry are unchanged. Release tests and a final fresh-build/hash audit are running; record their actual exit status below.

### 2026-10-22 21:16 +1300 · f90733c412c95029da2eafeaa8923a69339bc2a6 · observation
Final committed-code check: `bash experiments/archive/2026-10-rlrlll-macro-transition/scripts/l4_check.sh` exited 0 using a fresh scratch build; all ten Lake jobs passed and Check.lean accepted every audited declaration. Source commit and SHA256s are in results/c3_l4_build.txt; theorem axiom lists in results/c3_l4_axioms.txt. `cargo test --release` exited 0 (log scratch/l4-cargo-test.log). The updated shareable notebook generated and executed top-to-bottom with uv/nbconvert, exit 0 (scratch/l4-notebook.log); it will be executed once more after the result logs are committed. No dependencies, Rust or CUDA code changed. Added a reflective blog draft about consumed blank context and updated the homepage and proof-track notes. Earlier registration and historical scores are unchanged.

### 2026-10-22 21:16 +13:00 · 35d8e27 · decision
Completed: notebook regenerated and executed from the committed result logs, exit 0; blog experiment rendering and production Jekyll build/check, exit 0 (128 HTML pages, local links and required outputs OK). Final scope is bounded single cycles at every even height and the exact composition identity; multi-cycle padding remains explicitly open. No tests were skipped other than inapplicable CUDA checks. Timestamp correction: the preceding entry labelled 21:16 was drafted before reading the clock, at approximately 21:14; its validation outcomes were already observed. This entry uses the clock directly.

### 2026-10-23 18:15 +1300 · 642b4f4c710e0488dc8f1a1fc6af6298c4c09656 · observation
L5 (plane closure): `Plane.lean`, `PlaneChain.lean`, `PlaneForever.lean` build in a fresh directory (`scripts/l5_check.sh`, 13 Lake jobs, exit 0); `Check.lean` lists
`forever`, `relink`, `runN_sim`, `good_ideal`, `forever_ideal` with axioms propext, Classical.choice, Quot.sound only (`results/c3_l5_axioms.txt`). The registered prediction (about 45%)
held: no new finite run was needed; the padding identity is `composition` plus blank-row merging (`pad_pad`). Development mistakes: `blank` was already defined in L4Data (name clash),
a rcases pattern with the wrong arity tried to case on an equation, and a replicate length had to be normalised before applying a lemma; none changed the statement.

### 2026-10-23 18:15 +1300 · 642b4f4c710e0488dc8f1a1fc6af6298c4c09656 · interpretation
This removes the padding and infinite-plane caveats of L4 for the ideal plane, not for the real board (the real board is not `Good`; see README L5 "does not close" item 1).
The remaining Lean-side gap that matters for the headline claim is a plane-agreement lemma: real = ideal on the ideal ant's visited cells, then `forever` applies to the real run.

### 2026-10-23 18:18 +1300 · 035e32a · observation
Task E (registered 1370bd3 at 18:15:39, script 035e32a, run after): one visit profile a(d) = (1, 4, 4, 2, 1) on offsets -2 .. 2 for every interior bulk row, every phase and parity; every deep interior wake cell's colour equals its total visit count (3, 5 or 4 by x mod 3), 1836/1836. E-a, E-b, E-d held; E-c failed as registered on the support clause (0..20 vs -2..2). `results/e_visits.txt`.

### 2026-10-23 18:18 +1300 · 035e32a · deviation
corrects: the time 18:15 on the two L5 entries above (written at about 18:08 by the commit clock: `1035e5f` is 18:08:06) and the line "18:15" in the L5 README section header text: I wrote those times from the plan, not the clock. Order of events is unaffected (L5 files `642b4f4` at 18:05:43 precede the L5 notes).

### 2026-10-23 18:49 +1300 · 652e517 · deviation
corrects: the time "18:18" on the Task E entries (Task E results commit `354eab7` is 18:16:47) and "18:15" on the two L5 entries (`1035e5f` is 18:08:06; already corrected once). The README header "registered 2026-10-23 18:16" for Task E is also late: registration commit `1370bd3` is 18:15:39. Commit times govern.
