# Lab notebook: <experiment title>

Append-only. Newest entry last. Never edit an old entry; correct it with a new one
(`corrects: <timestamp>`). Tags: intent, assumption, observation, interpretation,
surprise, decision, dead-end, question, deviation. See `experiments/README.md`.

### YYYY-MM-DD HH:MM (+TZ) · <git short hash> · intent
What I am about to do, why, and which decision it informs.

### YYYY-MM-DD HH:MM (+TZ) · <git short hash> · assumption
Statement. How it could be checked / what would show it false. Status: untested.

### YYYY-MM-DD HH:MM (+TZ) · <git short hash> · observation
Fact, with the command and file that produced it.

### YYYY-MM-DD HH:MM (+TZ) · <git short hash> · interpretation
What I think it means; confidence; the alternative explanations I have not excluded.

### 2026-10-16 00:25 (+13) · 997c9b2 · intent
Goal: explain kappa. Advisor-guided first step: establish what "uniform" kappa is under the probe's windowing (window-mean B/S over end-of-window P/A). Prediction 1.110 for a=2/3, beta=1/2 registered in README before any run. Informs how to restate the ant 0.9, memoryless 1.3-1.45, rotor 2.0.

### 2026-10-16 00:26 (+13) · 997c9b2 · observation
src/probe.rs: B counts steps starting on a visited cell with >=1 unvisited 4-neighbour (holes included); P and A are read at window end; windows (2^k,2^(k+1)]. Confirms kappa is window-mean over end-value. Existing "memoryless" walker kappa 1.31 (E1c) was a different, non-teleporting walker, so no uniform baseline existed in notes.

### 2026-10-16 00:41 (+13) · 997c9b2 · observation
Ran `cargo run --release --example kappa_uniform_baseline -- 2026101601 8 23 results/mf_walker.csv` (8 seeds, 2^23 steps, board 4096) then `uv run scripts/analyse.py` -> results/analysis.txt. Mean-field walker: area slope a=0.677 (seed sd 0.005), perimeter exponent beta=0.520 (sd 0.007), probe kappa 1.118 (seed sd 0.009, windows k=12..22, range 1.103-1.139). Formula with measured (a,beta): 1.107; with (2/3,1/2): 1.110. Registered predictions 1 and 2 both held (difference 0.011 < 0.03).

### 2026-10-16 00:43 (+13) · 997c9b2 · interpretation
The probe's kappa for a walker with instantaneous edge-occupation ratio exactly 1 is ~1.11-1.12, not 1, because B/S is a window mean while P/A is read at window end and A,P grow during the octave. Reference for restating: ant ~0.9 is ~0.81x uniform; memoryless 1.3-1.45 about 1.2-1.3x; rotor 2.0 about 1.8x (rotor/memoryless used their own a, beta only approximately; not recomputed). Caveat: a uniform-on-territory walker is one idealisation; "uniform" could also be taken as uniform over visits-weighted area. This is accounting, not mechanism: the level of the ant's kappa remains unexplained.

### 2026-10-16 00:44 (+13) · 997c9b2 · decision
Stop at the baseline. The four mechanism plans (tail budget, prefix exposure, gates, field age) are blocked by failed reserve gates / missing checkpoints and are not worth rushing here.

### 2026-10-16 00:58 (+13) · 997c9b2 · observation
Estimator check (advisor-prompted): experiments/_lib/analyse_probe.py:18-26 forms kappa = (boundary_steps/steps)/(perimeter/area) per octave with steps = t//2 (window length) and P, A at window end; the paper reports the last octave. Same estimator as scripts/analyse.py, single octave, not pooled. So the ~1.11 reference applies to the paper's kappa. Not run through analyse_probe.per_rule itself (schema rename not done).

### 2026-10-16 00:59 (+13) · 997c9b2 · observation
Added brute-force recount of area and boundary count (two ways) at the end of every mean-field run; assert passes on all 8 seeds. unused_mut warning cleared. Reran: results unchanged (analysis numbers identical). sha256 examples/kappa_uniform_baseline.rs = ffde79de...ac8; results/mf_walker.csv = 94bc152e...260d48 (full hashes: run sha256sum).

### 2026-10-16 01:00 (+13) · 997c9b2 · deviation
corrects: 2026-10-16 00:43 interpretation. The rotor (1.8x) and memoryless ratios used the 1.11 reference although those walkers have different a (memoryless a~0.95 gives ~1.16, so 1.3-1.45 is ~1.1-1.25x). Only the ant ratio (a~2/3) is justified; treat the rotor/memoryless ratios as unrecomputed. Also not done: notebook.ipynb, tail-budget estimator calibration on this walker, and any mechanism test. Goal (explain kappa level) is NOT met.

### 2026-10-18 (+13) · 8266186 · observation
Checked the spread of census kappa before treating "0.81x uniform" as a derivation target. `scripts/census_spread.py` -> `results/census_spread.txt` (probe_summary.csv, cls == blob, single run per rule). Stationary rules (|g_k|<0.05, n=2185): kappa q05/25/50/75/95 = 0.49/0.73/0.90/1.06/1.47, sd ln kappa 0.35 (0.59 over all 2630). kappa_unif(a,beta) is 1.105 with sd ln 0.004, so the reference is effectively one number. kappa/kappa_unif: median 0.814, geometric mean 0.792, q05..q95 = 0.44..1.33, and 20% of stationary rules are >= 1.

### 2026-10-18 (+13) · 8266186 · decision
The 0.81 is the median of a wide rule-dependent distribution, not a constant. The target is the distribution (location plus spread), not one number. A derivation of the median alone would not be falsifiable on its own: median and geometric mean differ (0.81 vs 0.79), and single-run noise inflates the observed spread. Does NOT show a universal constant is absent; it shows the data do not call for one.

### 2026-10-19 (+13) · 8b290d8 · observation
Window labelling note from `2026-10-kappa-walker-reference` (no change to any number here). This experiment's own CSVs label windows by their start, so "k = 12..22" has window ends 2^13..2^23; the probe CSV's `t`/`k` columns label by window end (window (t/2, t]). Same estimator, one octave apart in label. Using `t` as the start for probe CSVs halves kappa (that experiment caught and fixed this). Also: the census kappa is the last window (k = 26) of `analyse_probe.py`, not a window mean.
