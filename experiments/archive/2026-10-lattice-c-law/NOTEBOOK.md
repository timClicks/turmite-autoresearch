# Lab notebook: lattice c law (hex and triangular ants)

Append-only. Newest entry last. Never edit an old entry; correct it with a new one
(`corrects: <timestamp>`). Tags: intent, assumption, observation, interpretation,
surprise, decision, dead-end, question, deviation. See `experiments/README.md`.

### 2026-10-20 00:25 (+13:00) · 0de4d38 · intent
Start `lattice-c-law`: test whether the square-lattice c law (1/c = 1.36 + 0.70 lead) and the kappa deficit hold on hex and triangular
ants. Registered the three loop-length hypotheses (A: b ~ loop length, B: lattice-independent, C: ~ 4/z) with numeric signature vectors
before any lattice c exists. Decision it informs: whether the 2x2-loop picture of c is specific to square geometry.

### 2026-10-20 00:25 (+13:00) · 0de4d38 · assumption
kappa_unif(a, beta) ports to hex and triangular because it is analytic in the run's own (a, beta); its premise (a uniform walker has P/A
tracking the window) is untested there. Falsified by gate G4 (mean-field walker ratio within 0.05 of 1). Status: untested.

### 2026-10-20 00:25 (+13:00) · 0de4d38 · question
My derivation says loop length cancels per loop cell (b = l_b / N_b) and the data must decide how N_b scales with the loop; I do not know
which limit is right, so the H-A vs H-B odds (25/40) are a guess. The census `cls == blob` is not reproducible from committed code, so I
use an alpha_w proxy (deviation from the census definition, stated in the README).

### 2026-10-20 01:10 (+13:00) · adf6677 · observation
Gates G1-G3 pass (`cargo test --release --test lattice_probe`, 7 tests): square windows equal `probe.rs` on the fields the lattice probe
produces; hex/triangular/square ants and both random movers equal a HashMap re-implementation; ant areas equal `HexSim`/`TriSim` at every
octave; one-letter loop cells are square 4, hex r 6, hex R 3, triangular 6 (the periods predicted from geometry). A deliberate mutation
(`fresh_nbrs += unv + (t & 1)`) failed 5 of 7 tests, then reverted. No c was aggregated on any lattice yet. A timing pilot ran 3 rules not
in the frozen lists (output discarded).

### 2026-10-20 01:10 (+13:00) · adf6677 · deviation
(1) The README said "all fields" for G1 and "2^26 steps": the lattice probe omits the radius-of-gyration and ant-spread fields (not needed
here), so G1 compares the seven fields it produces; and the census kappa window k = 26 is the octave (2^26, 2^27], so runs go to 2^27
steps (windows k = 12..26), as the census. Neither changes any prediction. (2) The kappa-ratio and width-exponent analyses use the
window set k = 20..26 as `analyse_probe.py`.

### 2026-10-20 01:45 (+13:00) · adf6677 · observation
Ran controls (106 s) and 960 ants (488 s). Gates G4 (mean-field ratio 0.994 / 1.005 / 1.004) and G5 (square b 0.696, a 1.286) pass. Registered
fits: b = 0.696 square, 0.355 triangular [0.340, 0.371], 0.876 hex R-lead; hex r-lead OLS is garbage (b 1.98, R^2 0.01) because one rule has
1/c = 390. Decision rule: undecided. L1, L2, K4 failed; K1, K2, K3 held. Files: `results/analysis.txt`.

### 2026-10-20 01:50 (+13:00) · adf6677 · surprise
b falls with loop length; none of A, B, C (all predicted b flat or rising with loop length / coordination) is close. Triangular is half the square.
Per-lead medians (post hoc, `results/explore.txt`) give hex r-lead b ~ 0.27, so the within-hex ratio is ~0.32, not 2.

### 2026-10-20 01:55 (+13:00) · adf6677 · interpretation
All three registered hypotheses are disproven as stated (triangular alone excludes each by >0.3). I do not have a replacement: b(l) = 0.86, 0.70,
0.34, 0.28 for l = 3, 4, 6, 6 is a post hoc description on four points. Alternatives not excluded: the hex fits mix letter types after the lead; the
"loop around a vertex" lengths I used may not be the loops that matter on triangles (they enclose a vertex, not a cell); survivor selection (retention
0.4-0.98 by cell). Confidence in "b depends on lattice": high (CI-level). In "b falls with l": moderate (4 strata, 3 distinct l).

### 2026-10-20 01:55 (+13:00) · adf6677 · decision
Not extending the registered analysis (no outlier trimming added after the fact). Next experiment, if any, must register a b(l) prediction before
using a new loop length or a letter-type-separated hex lead.

### 2026-10-20 03:10 (+13:00) · 3117e1b · interpretation
corrects: 01:45 observation and the README K4 sentence. K4 still failed as registered, but the explanation "I misremembered the square comparison" was
wrong: the pooled ant median c reflects my uniform sampling of leads 1-5. Lead-1 medians of 1/c (explore.txt) give ant c = 0.48 square, 0.63 triangular
(above rw 0.44, 0.46) and 0.38 hex r-lead, 0.28 hex R-lead (below rw 0.42).

### 2026-10-20 03:10 (+13:00) · 3117e1b · observation
The hex r-lead outlier is `rrrrrLrrrLrrLL` (lead 5): 1/c = 390, c = 0.0026 at k = 26, but perimeter = area at every window (perimeter exponent beta = 1.0:
every visited cell has an unvisited neighbour, a lacy territory) while the area exponent (0.65) and width exponent (0.34) look blob-like, so the alpha_w proxy and
|g_k| < 0.05 (g_k = 0.0 because P/A = 1) both let it through. The proxy therefore leaks on hex; a beta filter (e.g. beta < 0.8) would have excluded it. The next
three largest 1/c on hex (12.9, 9.7, 8.8) have beta 0.59-0.62 and are genuine. `results/outlier.txt`, `scripts/outlier.py`. Not re-filtering the registered analysis.

### 2026-10-20 03:10 (+13:00) · 3117e1b · observation
Provenance: the 88 "dirty" files in `run.log` are stat/line-ending noise: `git diff --ignore-cr-at-eol --stat adf6677 -- src examples` reports 0 insertions and 0 deletions.
The triangular stratum carries the refutation alone and none of the listed confounds can rescue A, B or C there: retention 0.75-0.98 (the highest of the three
lattices), R^2 0.94, OLS slope 0.355 agrees with the per-lead-median slope 0.335.

### 2026-10-20 03:25 (+13:00) · 3117e1b · observation
Full `cargo test --release` (WSL, after adding `src/lattice_probe.rs`): every test binary reports ok, no failures. Registered result and post hoc reading are kept
separate in README, notes and blog; the outlier was not trimmed from the registered fit.

### 2026-10-20 00:50 (+13:00) · 7df6d35 · intent
Registered follow-up A in README (letter-typed hex lead, beta < 0.8 filter, T1-T5) before running anything on it. Also added ipykernel/nbformat/nbclient to
`pyproject.toml` (user chose `uv add`). The b(l) model on a new loop length is not started: it needs a lattice with a new loop length and a registered model; see next entry.

### 2026-10-20 01:05 (+13:00) · 78122d9 · observation
Follow-up A ran as registered (`results/hex_letters.txt`). T2 and T5 held; T1 partly failed (r-lead R^2 0.42, b 0.262 clean); T3 and T4 failed. The r-lead slope was never an
outlier-driven artefact: b_r/b_R = 0.30 [0.24, 0.37].

### 2026-10-20 01:05 (+13:00) · 78122d9 · interpretation
Letter type after the lead has a small detectable effect in R-lead only (d ~ 1.0, CV gain 0.014); it does not explain the hex intercept or the poor fit. The open items "hex intercept"
and "hex letter types" shrink to: why the hex scatter is large and why a ~ 2.4-2.8. The b(l) model on a new loop length is not attempted this session: it needs a new lattice
with a new loop length (implementation plus oracle tests per AGENTS rule 4) and a model registered first; no model with a mechanism exists yet beyond the post hoc line.

### 2026-10-20 01:30 (+13:00) · plan
user selected the b(l) item. Added the Moore lattice (new loop length 8, plus a loop-4 control at z = 8) to `lattice_probe` with oracle tests; registered M-lin / M-inv and B1-B6 in README before any Moore ant was run. Reason for Moore: hex offers only loops 3 and 6, triangular 6; any new loop length needs a new lattice.

### 2026-10-20 02:05 (+13:00) · 02f5d13 · observation
Follow-up B ran as registered (`results/analysis_moore.txt`). B1, B3, B4, B6 held; B5 failed; B2 gave M-lin refuted, M-inv number met but its own consistency clause missed by 0.005, so by the frozen rule neither is supported. b = 0.260 (l=8), 0.775 (l=4, z=8); intercept 2.4 on both.

### 2026-10-20 02:05 (+13:00) · 02f5d13 · interpretation
b looks like ~0.26-0.28 for l = 6 and 8, so a floor-like or slowly falling dependence, not linear to zero. Intercept tracks the lattice (z >= 6 gives 2.4+), not the loop. Both remain without mechanism; the b(l) item is narrowed, not closed.
