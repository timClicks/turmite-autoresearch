# Why does the c-law slope b fall with loop length? Circulations per birth versus reads per circulation

Registered 2026-10-20 00:55 (+13:00), base commit `6049d6a` plus the uncommitted instrument (`src/lattice_trace.rs`,
`tests/lattice_trace.rs`, `examples/lattice_c_law_colours.rs`), committed together with this file before any run on the
960-ant list. **Nothing in this folder has been run on that list.** Disclosure of what was seen before: the lattice
c-law results (`experiments/archive/2026-10-lattice-c-law`, slopes b and intercepts per stratum, per-lead medians), and on the
*square* lattice only, the per-colour and lag-4 findings of `experiments/archive/2026-10-c-law-mechanism` (r_k decays ~0.88 per
read; 48-78% of circulating reads return after exactly 4 steps). No per-colour, lag or run statistic has been looked at
on the triangular or hexagonal lattice. The tracer's own gates (below) ran on short random rules only.

## Question

`1/c = a + b * lead` holds on three lattices (R^2 0.94-0.95 square and triangular), but b falls with the loop that the lead
letter closes: 0.86 (hex R, loop 3), 0.70 (square, 4), 0.34 (triangular, 6), 0.28 (hex r, 6; per-lead medians, since the
OLS is destroyed by one rule). The lattice study's first-principles reading, `b = l_b / N_b` (boundary cells per lap over
births per circulation episode), was never measured on either side, and its three hypotheses (b grows with l, constant,
~4/z) are all disproven. A fitted b(l) would be a fourth guess. Instead: **measure the two factors of b.**

## Definitions (frozen)

- Everything as in `experiments/archive/2026-10-lattice-c-law` (windows, boundary step, birth, lead, strata, `alpha_w` blob filter, kept set).
  The tracer `src/lattice_trace.rs` uses the last octave only (steps (2^26, 2^27]), identical to the probe's window k = 26.
- **Return**: a step that starts on a cell last read exactly `ell` steps earlier; `ell` = loop length of the rule's first
  letter: square 4, triangular 6, hex `r`/`l` 6, hex `R`/`L` 3 (checked by stepping in `tests/lattice_probe.rs`, gate G3 of the parent).
- **Circulation**: a maximal run of consecutive returns (any colour, boundary or not) of length >= `ell` (one full lap
  re-read). `eps` = circulations per birth. `R` = mean run length of circulations (lengths capped at 63). `C` = total steps
  inside circulation runs per birth = `eps * R`. `Cb` = the same counting only boundary steps in those runs.
- **Slopes** are Theil-Sen over kept rules (primary, robust to the 1/c = 390 outlier) and the slope of per-lead medians
  (secondary), leads 1..5 for 1/c, and m = lead for C, Cb, eps, R. OLS is reported but is not primary.
- `b_med` = slope of per-lead medians of 1/c, recomputed from this run (not copied).

## Gates (instrument; a fail voids the dependent claims)

- **T1** (done before this registration, `cargo test --release --test lattice_trace`): square `LTrace` equals `edge_trace::trace_blank`
  in every field on 30 random rules; hex, triangular and square equal a HashMap re-implementation on 30 random rules each;
  two one-line mutations (lag off by one, return lag `ell + 1`) were each caught by the tests.
- **T2** on the 960-ant list: for every rule not escaped on the 8192 board, `births` and `boundary_steps` equal `ants.csv` window k = 26
  exactly, and `sum_k edge_k = boundary_steps`.
- **T3** `1/c` from the tracer equals the parent's to 1e-12 (follows from T2; reported anyway).

## Predictions (kept rules, per stratum; my odds in brackets)

- **P1 (circulation accounts for the lead slope).** `Cb` per-lead-median slope is within [0.8, 1.2] x `b_med` in all four strata. [45%]
  (If this fails the reads that grow with the lead are not in lag-`ell` runs, and the loop picture of the slope is incomplete off the square lattice.)
- **P2 (reads per circulation).** `R` per-lead-median slope divided by `ell` lies in [0.5, 1.1] in all four strata (this is `l_b / l`:
  the fraction of a loop that is boundary and survives a lap). [50%]
- **P3 (the discriminator).** `b = eps * lambda` with `lambda = dR/dm`. The drop of b with loop length is carried by `eps`, not by
  `lambda`: `eps` at lead 3 (stratum median over kept rules) is lower on triangular than on square by a factor >= 2.0, and lower
  on hex r than hex R by a factor >= 3.0. [55%]
  Rival (lambda carries it, N_b/l roughly constant): ratios of `eps` within [0.7, 1.4] of 1, with `lambda/ell` falling instead. Reported with the measured vector either way.
- **P4 (primary robust slope).** Theil-Sen b is within the parent's OLS bootstrap CI on square, triangular and hex R, and in [0.15, 0.45] on hex r. [60%]
- **P5 (hex ring centre).** Births into a cell whose neighbours are all already visited (`hole_births`, e.g. a 6-ring centre) per birth are >= 2x
  higher on hex r-lead than hex R-lead (median over kept rules), because only the r ring encloses a cell. [40%]
- **P6 (letter-typed hex lead).** Splitting hex R-lead kept rules by the killing letter (the first letter different from the lead:
  `r`, `l`, `L`) and fitting `1/c ~ lead` per type raises the mean R^2 weighted by n from 0.69 to >= 0.80. [40%]
  Not registered: any claim about U-turn letters (turn 2 on square, 3 on hex); a second stage with a new loop length (period 2) would need its own registration.

## Decision rule

P3 is the headline. Supported if both ratios pass; "rival" if both eps ratios are in [0.7, 1.4]; otherwise undecided with
the measured vector. A gate failure (T2) on a lattice means no claim on that lattice.

## Commands

```
bash experiments/archive/2026-10-lattice-c-law-colours/scripts/run.sh   # fresh target dir, sha256 logged, writes results/traces.jsonl
uv run experiments/archive/2026-10-lattice-c-law-colours/scripts/analyse.py
```

## Results

Run 2026-10-20 (`scripts/run.sh`, 509 s wall on 6 threads, shared with another job; binary sha256 `24ea23a2...a8701` in `results/run.log`;
`traces.jsonl` 1.8 MB), `uv run scripts/analyse.py` -> `results/analysis.{txt,json}`, post hoc `scripts/explore.py` -> `results/explore.txt`.
`run.log` says "dirty: 0 files" but the one-line driver fix (see NOTEBOOK 01:20) was uncommitted at run time (the `git status` under the
`GIT_DIR` workaround is unreliable); it is committed with these results.

**Gate T2 passed**: 855 rules compared (105 escaped in the tracer or the parent), 0 mismatches in births, boundary steps, or per-colour sum.

**Registered predictions**

| | verdict | numbers |
|---|---|---|
| P1 Cb slope / b_med in [0.8, 1.2] | **FAILED** | 0.42 / 0.19 / 0.29 / 0.17 (square / tri / hex R / hex r) |
| P2 R slope / ell in [0.5, 1.1] | **FAILED** | 0.08 / 0.07 / 0.20 / 0.10 |
| P3 eps ratios >= 2.0 and >= 3.0 | formally met (7.2, 75) but **not interpretable** | see below |
| P4 Theil-Sen b in parent CI | **HELD** | 0.691, 0.347, 0.850; hex r 0.306 in [0.15, 0.45] |
| P5 hole births r/R >= 2 | **HELD** | 0.094 vs 0.0097 per birth (9.7x); hex r at lead 1: 0.155 |
| P6 per-kill-letter hex R fits, weighted R^2 >= 0.80 | **FAILED** (0.781) | kill `l`: R^2 0.941 (b 0.88); kill `L` 0.717; kill `r` 0.696 (pooled 0.689) |

**Why P3 is not evidence.** My circulation definition (runs of lag-`ell` returns of any cell, boundary or not) counts interior
loops too. `C` (steps in such runs) is 30-120 per birth on the square lattice while `1/c` is 2-5, so `eps` (1-19 circulations per
birth) and `R` are dominated by interior behaviour and say nothing about the boundary episodes in b = l_b / N_b. The boundary-only
version, `Cb`, is what P1 tests, and it carries only 17-42% of the slope. The decomposition I intended (circulations per birth times
boundary cells per circulation) is therefore **not measured**; P3 passing is an artefact of a bad estimator and I do not count it.
The headline question is unanswered by the registered tests.

**Post hoc (unregistered, `results/explore.txt`; all non-escaped rules, per-lead medians, no blob filter).** Boundary reads per birth by
the colour the cell had when read (`1/c` is their sum). The lead slope lives in reads at the circulating colours 1..m-1 and is
partly cancelled by falling reads at the killing colour and later:

| stratum | circulating reads added per extra lead step | slope of circ | slope of kill | slope of later | total slope |
|---|---|---|---|---|---|
| hex R (loop 3) | 0.95 each (0.95, 0.96, 0.96, 0.94) | 0.95 | -0.02 | -0.07 | 0.88 |
| square (4) | 0.85, 0.78, 0.79, 0.77 | 0.80 | -0.05 | -0.06 | 0.69 |
| triangular (6) | 0.65, 0.50, 0.37, 0.35 | 0.46 | -0.08 | -0.02 | 0.36 |
| hex r (6) | 0.69, 0.62, 0.53, 0.47 | 0.58 | -0.11 | -0.20 | 0.28 |

Since a cell is read once per colour, "reads per birth at colour k" is the fraction of born cells that are still boundary cells at
their k-th read. So the c law reads: that fraction is a plateau of about 0.95 (hex R), 0.8 (square), 0.4-0.65 (triangular),
0.5-0.7 (hex r) across the lead colours, with a slow decay for the larger loops, and **b is that plateau minus the loss at the killing and
later colours**. This restates the identity `1/c = E[N_b]` and is not a mechanism, but it says what must be explained: why a ring
cell stays a boundary cell through the circulating reads with probability ~1 for loop 3 and ~0.5 for loop 6.
Two further observations. (a) The ring-circulation picture does not carry the circulating reads off the square lattice: the share of
circulating reads with lag exactly `ell` is 0.67-0.87 square but 0.05-0.44 triangular, 0.28-0.40 hex R, 0.06-0.24 hex r (rising with lead).
(b) Hex r-lead rules fill holes: 15% of births at lead 1 land in a cell whose neighbours are all visited (the ring centre), falling to 6% at lead 5;
hex R and square sit at 1-2%.

**Reading.** Not explained. What this run adds: the slope is carried by circulating-colour reads at a plateau rate that falls as the
loop lengthens; loop-return (lag-`ell`) circulation is the dominant carrier only on the square lattice, so the "2x2 loop" picture
should not be transplanted to other lattices; hex r rules behave differently through hole filling; the kill letter's type matters on hex
(`l`-killed R-lead rules are linear in lead with R^2 0.94 and the other two types are not). Next registered step, if pursued: a
boundary-only episode segmentation (maximal runs of consecutive boundary reads of colours 1..m-1), and the plateau fraction itself
as a function of ring geometry (outside neighbours per ring cell: square 2, triangular 1, hex R 4, hex r 3), which is a measurable
prediction not yet made.
