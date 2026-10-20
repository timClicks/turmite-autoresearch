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
