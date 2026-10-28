# Research frontier (2026-10-13 PM)

**Reading guide, added 2026-10-13:** The original proposals and subsequent results are preserved below. The expansion in **S–W** revises the experimental priorities, flags mathematical and inferential limitations in earlier proposals, and adds new hypotheses. Read W for the suggested next programme. This is a research agenda, not a report of new experiments.

Open questions, mechanistic hypotheses and experimental designs for the next phase of the investigation.
This note builds directly on:
- `notes/research-frontier.md` (items 1–32),
- `notes/research-frontier-2026-10-13.md` (items A1–A7, B1–B5, C1–C3, D1–D5, E1–E6),
- `notes/frontier-2026-10-13-results.md` (results ledger documenting the resolution of all Phase 2 items),
- `notes/kappa-experiment-design.md` (Arms A, B, C testing and ruling out five mechanisms for $\kappa$),
- `notes/open-questions-hypotheses.md` (questions Q8–Q16),
- and `research-outputs/working-papers/cube-root-growth/main.typ` / `notes/summary-2026-10-13.md`.

**Pre-registration declaration:**
Nothing here has been measured. Every prediction below is an explicit proposal written on 2026-10-13 PM *before* any test; per `AGENTS.md`, do not edit a prediction after seeing data, append what happened and any revision underneath. Predictions are quantitative guesses designed to discriminate between competing physical mechanisms, not summaries of results.

---

## F. What sets kappa? Global, topological and excursion mechanisms

### Context
In the growth identity $dA/dt = c \cdot \kappa \cdot P/A$, $\kappa = (B/S) / (P/A)$ measures the over-representation of the walker on the perimeter relative to a uniform spread.
In Phase 2, five candidate explanations for $\kappa$ were tested and decisively falsified:
1. Rule letters, $q = \#R/n$, prefixes, and substrings: no prediction (held-out $R^2 \le 0.04$, A1c).
2. Memoryless persistent walker: gives $\kappa \approx 1.35$ with an incorrect area exponent 0.95 (A1d).
3. Local boundary dwell time $v_e$: edge dwell is pinned at $v_e = 1.5$ for 10 of 12 extreme ants regardless of whether $\kappa = 0.12$ or $\kappa = 15$ (Spearman $\rho = -0.26$, A3).
4. Depleted crust depth $D$ (layers $d = 2..4$): failed to separate matched pairs of rules with equal length, equal $q$, and equal $c$ (Arm C sign test 13/26, $p = 0.58$).
5. Noisy rotor: adding memory noise does not smoothly interpolate $\kappa$ down to 1.4; instead, $\kappa$ spikes up to $6.65$ during the crossover to diffusion (Arm B).

Yet $\kappa$ has high between-rule repeatability ($\text{ICC} = 0.58$ across patched starts; blank-board runs agree on pair ordering in 25 of 26 pairs). If $\kappa$ is not set by the first cell layer (dwell) nor the near-surface crust, it must be determined by the **global interior excursion dynamics** connecting boundary visits.

---

### F1. Interior excursion length distribution $P(L)$ and the mean return time
By renewal / ergodic theory on a finite territory, the boundary occupancy fraction $B/S$ is given by:
$$
\frac{B}{S} = \frac{\langle \tau_{\text{edge}} \rangle}{\langle \tau_{\text{edge}} \rangle + \langle L_{\text{int}} \rangle}
$$
where $\langle \tau_{\text{edge}} \rangle$ is the mean dwell time during a boundary contact ($v_e \approx 1.5$), and $\langle L_{\text{int}} \rangle$ is the mean number of steps taken into the interior (layer $d \ge 1$) before returning to layer $d = 0$.
Since $\kappa = (B/S) \cdot (A/P)$ and $A/P \sim R \sim t^{1/3}$, $\kappa$ is governed by whether interior excursions are shallow loops that return rapidly to the perimeter or deep diffusive journeys that explore the core.

- **Hypothesis:** Rule-to-rule variation in $\kappa$ is inversely proportional to the median interior excursion length: $\kappa \propto 1 / L_{\text{med}}$. Low-$\kappa$ rules plunge deeply into the bulk (large $\langle L_{\text{int}} \rangle$), whereas high-$\kappa$ rules perform shallow, localized loops near the perimeter.
- **Test:** Instrument `src/probe.rs` to track excursion lengths $L$ (steps between leaving layer 0 and next landing on layer 0) across the 44 rules of the matched-pairs pool (`experiments/archive/2026-10-arm-kappa-depletion-arms/results/armc_specs.txt`) in octave windows $k = 22..25$. Measure the median excursion length $L_{\text{med}}$ and fit the power-law tail exponent $\gamma$ of $P(L) \sim L^{-\gamma}$ for $L \in [10, 10^4]$.
- **Prediction:**
  1. Median interior excursion length $L_{\text{med}}$ strongly anti-correlates with $\kappa$: Spearman $\rho(\kappa, L_{\text{med}}) \le -0.70$ ($p < 10^{-4}$).
  2. The distribution $P(L)$ has a heavy tail with $\gamma \in [1.2, 1.8]$. The tail exponent $\gamma$ correlates positively with $\kappa$ ($\rho \ge 0.60$): high-$\kappa$ rules have steeper cutoffs (fewer deep excursions).
- **What breaks it:** If $L_{\text{med}}$ is uncorrelated with $\kappa$ ($|\rho| < 0.25$), bulk excursion length is not the carrier of $\kappa$, implying that the difference arises from anisotropic boundary geometry or multi-scale trapping.

---

### F2. Tangential edge currents and boundary velocity polarization
Does the walker reflect isotropically from the boundary, or does it set up a persistent directed current along the perimeter?

- **Hypothesis:** High-$\kappa$ rules establish a boundary-gliding state: on layer 0, the ant's velocity vector $\vec{v}$ is strongly polarized along the local perimeter tangent $\vec{t}$ ($\langle |\vec{v} \cdot \vec{t}| \rangle \gg \langle |\vec{v} \cdot \vec{n}| \rangle$). Low-$\kappa$ rules experience immediate normal reflection into the interior ($\langle \vec{v} \cdot \vec{n}_{\text{in}} \rangle \approx 1$).
- **Test:** On each step visiting layer 0 in octave windows $k = 22..25$, compute the local boundary normal $\vec{n}$ (pointing into the interior) and tangent $\vec{t}$. Compute the polarization ratio:
  $$
  \mathcal{R}_{\text{edge}} = \frac{\langle |\vec{v} \cdot \vec{t}| \rangle}{\langle \max(0, \vec{v} \cdot \vec{n}_{\text{in}}) \rangle}
  $$
  across the 24 rules of Arm A (12 extreme-kappa and 12 typical-kappa rules).
- **Prediction:** $\mathcal{R}_{\text{edge}}$ correlates strongly with $\kappa$: Spearman $\rho(\mathcal{R}_{\text{edge}}, \kappa) \ge 0.65$. Rules with $\kappa > 2.0$ have $\mathcal{R}_{\text{edge}} > 1.4$, while rules with $\kappa < 0.5$ have $\mathcal{R}_{\text{edge}} < 0.8$.
- **What breaks it:** If $\mathcal{R}_{\text{edge}}$ is invariant across rules ($1.0 \pm 0.1$), boundary motion is locally isotropic and does not carry the $\kappa$ variation.

---

### F3. Critical singularity of boundary occupancy in the noisy rotor
Arm B showed that adding memory noise $\epsilon$ to the rotor caused $\kappa$ to spike up to $6.65$ at $\epsilon = 0.01$ during crossover, rather than decreasing from 2.0 to 1.4.

- **Hypothesis:** The spike in $\kappa$ is a dynamic crossover singularity. In the rotor, arrow updates enforce exact Eulerian flux balance. Weak noise $\epsilon$ destroys Eulerian cycle closure in the bulk first, destroying interior recurrence, while the boundary reflection remains trapped by unvisited outer cells. The peak boundary enhancement $\kappa_{\max}(\epsilon)$ diverges as $\epsilon \to 0$ with an anomalous scaling:
  $$
  \kappa_{\max}(\epsilon) \sim \epsilon^{-\mu}, \quad t^*(\epsilon) \sim \epsilon^{-\nu}
  $$
- **Test:** Run the noisy rotor (`NoisyRotor` in `src/walkers.rs`) at finer geometric noise levels $\epsilon \in \{10^{-4}, 3\times 10^{-4}, 10^{-3}, 3\times 10^{-3}, 10^{-2}\}$ to $2^{29}$ steps on a $32768^2$ board, with 8 seeds each. Locate the peak $\kappa$ and its step $t^*$.
- **Prediction:**
  1. $t^*(\epsilon) \sim \epsilon^{-1.0 \pm 0.15}$.
  2. $\kappa_{\max}(\epsilon) \sim \epsilon^{-0.28 \pm 0.06}$.
  3. For $\epsilon = 10^{-4}$, the $t^{2/3}$ area scaling survives up to $2^{26}$ with $\kappa = 2.05 \pm 0.10$.
- **What breaks it:** If $\kappa_{\max}$ plateaus for $\epsilon \le 10^{-3}$ rather than growing, the peak is a finite-board artifact rather than a true scaling singularity.

---

### F4. Macroscopic boundary impedance and Robin boundary condition
In continuum diffusion problems, a reflecting boundary with partial penetration is modeled by a Robin boundary condition: $-D \nabla \rho \cdot \vec{n} = \lambda \rho$, where $b = D/\lambda$ is the extrapolation length.

- **Hypothesis:** The ant's interior density satisfies a quasi-stationary Helmholtz/diffusion equation in the comoving frame with an effective boundary impedance $\lambda_r$. $\kappa$ is directly determined by the macroscopic impedance $\lambda_r$: $\kappa = \kappa_0 / (1 + b_r / R)$.
- **Test:** For the 24 rules of Arm A, measure the radial density gradient $\partial \rho / \partial r$ at $r = 0.8 R_{\text{eq}} .. 0.95 R_{\text{eq}}$. Compute the effective impedance $\lambda_{\text{eff}} = (D \partial \rho / \partial r) / \rho_{\text{edge}}$.
- **Prediction:** $\lambda_{\text{eff}}$ explains $> 60\%$ of the variance of $\kappa$ across the 24 rules ($R^2 \ge 0.60$).

---

## G. Breakout instabilities, ribbon dynamics, and late escapes

### Context
In Phase 2, three major anomalies in asymptotic confinement were discovered:
1. `RLRLLL` (one of the 14 core rules tested to $2^{34}$) escaped a $32768^2$ board at $\approx 1.3 \times 10^{10}$ steps with **no highway** (Q8). It built an anomalous $\sim 10^4$-cell thin ribbon structure along the boundary (bounding box jumped from 3,377 at $10^{10}$ to 18,175 at $1.3 \times 10^{10}$).
2. In `RRLLLLLLR` (A7c), 1 of 62 runs at $2^{32}$ suffered a massive 14x area blowout. About 5% of random rules exhibit rising seed-to-seed CV, heavily concentrated in `RLLL...` prefixes.
3. In the 1e10–1e11 decade, the highway onset rate fell from 4.7% to 1.25% (3/240), but 3 additional rules escaped the board as unclassified non-highway frame/ribbon builders (B5). **[Corrected 2026-10-21: 22 of the 38 (1e9,1e10] and 4+ of the 16 (1e10,1e11] "highways" are board artefacts; genuine yields 1.98% and 0.68-1.64% (1.64% if the 7 pending rechecks confirm); see `experiments/archive/2026-10-late-highway-board-check/README.md`.]**

---

### G1. Anatomy of the `RLRLLL` non-highway boundary breakout
What is the ant doing when a blob rule suddenly leaves the grid without forming a highway?

- **Hypothesis:** The breakout is an **edge unravelling mode** (a "boundary highway" or surface wave). The ant does not build a periodic highway into open space; instead, it encounters a specific boundary defect that locks it into a 1D perimeter-following crawl. The crawl advances along the envelope of the existing blob, carving a thin ribbon until it reaches open boundary corners and shoots outward.
- **Test:** Run `examples/escape_trace.rs` on `RLRLLL` across the escape window $t \in [1.25 \times 10^{10}, 1.31 \times 10^{10}]$. Measure:
  1. Manhattan ribbon thickness $\Delta_\perp$ (transverse width).
  2. Local step efficiency $\eta_{\text{step}} = \Delta t / \Delta A$.
  3. Periodicity of displacement modulo perimeter length.
- **Prediction:**
  1. The transverse width remains tightly bounded: $\Delta_\perp \le 12$ cells across $> 95\%$ of the escape trajectory.
  2. The step efficiency is quasi-ballistic: $\eta_{\text{step}} < 8$ steps per new cell (contrasting with $> 100$ steps/cell in the blob phase).
  3. The motion has a repeating quasi-period $p \in [24, 256]$ that shifts adiabatically as the local boundary radius of curvature changes.
- **What breaks it:** If the ant's visited set expands isotropically in 2D with $\Delta_\perp > 100$ cells, the escape is an accelerated diffusive blob, not a boundary wave-guide.

#### G1 result (done 2026-10-13; predictions not edited)
`cargo run --release --example ribbon_trace -- RLRLLL 12000000000 13100000000 1000000 100000000 32768 > experiments/archive/2026-10-g1-ribbon-breakout/results/g1_ribbon.csv` (120 coarse windows of $10^8$ steps, 975 fine windows of $10^6$ steps; output log `experiments/archive/2026-10-g1-ribbon-breakout/results/g1_ribbon.log`; analysis `experiments/archive/2026-10-g1-ribbon-breakout/scripts/g1_breakout_stats.py` and `experiments/archive/2026-10-g1-ribbon-breakout/scripts/g1_stats.py`). The ant left the $32768^2$ board at step **12,974,495,927** ($x = -16,384, y = -5,895$).
- **Breakout identification:** The breakout begins abruptly at step $t \approx 1.2677 \times 10^{10}$ and continues for 299 fine windows (297.5M steps) until grid escape.
- **Prediction 2 decisively confirmed:** The step efficiency collapses to $\eta_{\text{step}} = 4.027$ steps per new cell (mean across all 299 breakout windows; min 3.954, max 5.690), firmly within the predicted quasi-ballistic regime ($\eta_{\text{step}} < 8$, contrasting with $> 1000$ steps/cell in the preceding blob phase).
- **Prediction 1 falsified in strict cell width, but physical mechanism confirmed:** The predicted $\Delta_\perp \le 12$ was too narrow: transverse thickness `thin` $= \min(W_x, W_y)$ has median 54.0 cells (min 30, max 478, p95 126.6, with 64.9% $\le 60$ cells and 91.0% $\le 100$ cells). However, the longitudinal extent `wy` per 1M steps spans up to 9,939 cells while `wx` is only 30–45 cells. The aspect ratio exceeds **200:1**. The ant executes a colossal vertical sweep ($\Delta y \sim 10^4$) while advancing westward by only $\sim 40$ cells per million steps.
- **Breakout criterion:** An isotropic diffusive blob ($\Delta_\perp > 100$ in both dimensions) is completely ruled out. The escape is a macroscopic surface wave carving a vertical slab that marches ballistically to the western boundary. Quasi-periodicity $p$: local step efficiency is pinned near 4.00 (the 4-step cycle modulo direction), showing that the ant enters a directed limit cycle that continuously erodes the perimeter.

> **Superseded (2026-10-13, resolving the paper's `TODO(G1)`).** The "macroscopic surface wave", "directed limit cycle" and "erodes the perimeter" wording above is withdrawn; the later "G1 result" (end of this note) is the reading of record. Reasons: (i) at onset the ant is at x = -2,190 while the blob box at 1.2e10 is about 3,540 wide (x roughly ±1,770), so it starts ~420 cells outside the blob rather than crawling its envelope (`experiments/archive/2026-10-g1-ribbon-breakout/results/g1_stats.txt`, coarse windows); (ii) 4 steps per new cell is an efficiency, not a demonstrated period (no tape-repeat or moving-frame test was run; see lesson 4 below); (iii) the abrupt step onset is a phase switch, not an adiabatic crossover. Numbers (4.02-4.03 steps/cell, 299 windows, exit at 12,974,495,927) are unchanged. Open: the trigger, one ribbon vs parallel strokes, the actual period.

---

### G2. Asymptotic survival analysis of blob rules: hazard rate decay
Is every blob rule strictly metastable (destined to escape eventually), or is there a non-zero measure of truly confined chaotic rules?

- **Hypothesis:** The hazard rate of escaping into any ballistic or ribbon state decays as a power law:
  $$
  h(t) = -\frac{1}{S(t)} \frac{dS}{dt} \sim t^{-\theta}, \quad \theta \approx 0.65 \pm 0.15
  $$
  Because $\theta < 1$, the cumulative hazard $\int h(t) dt$ diverges as $t^{1-\theta}$, implying that asymptotically as $t \to \infty$, almost all rules eventually break out, but the median lifetime is $> 10^{16}$ steps.
- **Test:** Merge the full 732 survivor census at $10^{11}$ steps (`experiments/archive/2026-10-highways-unresolved-rules-1e10-1e11/results/h1e11/run3.log`). Fit the survivor function $S(t)$ over decades $10^8, 10^9, 10^{10}, 10^{11}$.
- **Prediction:**
  1. The total number of new escapes in $(10^{10}, 10^{11}]$ across all 732 rules will be $\le 10$ (escape rate $\le 1.4\%$).
  2. The fitted hazard exponent $\theta \in [0.5, 0.8]$ (falsifying both a flat rate $\theta = 0$ and an exponential cutoff $\theta > 1$).
- **What breaks it:** If new escapes in $(10^{10}, 10^{11}]$ exceed 25 rules (hazard rate $\ge 3.4\%$), the thinning was a small-sample fluctuation and the rate is approximately constant.

---

### G3. Heavy-tailed area distributions in the `RLLL...` family
Why does `RRLLLLLLR` exhibit rare 14x blowouts (A7c), and why do 5% of rules show rising seed-to-seed CV?

- **Hypothesis:** Rules prefixed with `RLLL` possess an absorbing boundary defect that can trigger temporary unravelling. The territory area distribution $P(A)$ at fixed $t$ has a heavy Fréchet / Pareto tail:
  $$
  P(A > x) \sim x^{-\alpha_{\text{tail}}}
  $$
  with $\alpha_{\text{tail}} \in (1, 2)$, producing an infinite variance (hence rising empirical CV) even while the bulk median converges.
- **Test:** Run 100 patched starts to $2^{30}$ steps for 4 `RLLL`-prefixed rules (`RRLLLLLLR`, `RLLLRRRRLR`, `RLLLLRRRRL`, `RLLLRLLLRR`) and 4 control core rules (`RLR`, `RLLR`, `RLRL`, `RRLR`). Compute the Hill estimator of the tail exponent $\alpha_{\text{tail}}$ for $A / \text{median}(A)$.
- **Prediction:**
  1. For `RLLL` rules, $\alpha_{\text{tail}} = 1.6 \pm 0.3$ ($\alpha_{\text{tail}} < 2$ explains the rising CV).
  2. For control core rules, $\alpha_{\text{tail}} > 4.5$ (thin sub-Gaussian tails, falling CV).
- **What breaks it:** If `RLLL` rules have $\alpha_{\text{tail}} > 3.0$, the 14x outlier was a unique fluke rather than a heavy-tailed phase.

---

## H. The area vs width discrepancy and territory geometry

### Context
Phase 2 established a major geometric puzzle (Q10, Q11, B2):
- The ICC of the **width exponent** across rules is only $0.12$ (rule identity explains almost nothing; run noise dominates).
- The ICC of the **area exponent** across rules is $0.34 - 0.43$ (rule identity explains 3x–4x more variance!).
- Furthermore, under initial arrow bias (C2b/c), width at $2^{28}$ expanded by 2.6x at bias 0.25 while the width exponent stayed $0.33$, but the area exponent increased to $0.79$.

How can rule identity control the area exponent while the width exponent is universally pinned near $1/3$?

---

### H1. Dynamic lacunarity: explaining the area ICC via filling fraction drift
Area and bounding box dimensions are geometrically related by:
$$
A(t) = \eta(t) \cdot W_x(t) W_y(t)
$$
where $\eta(t) \in (0, 1]$ is the territory compactness (filling fraction).
Taking logarithmic derivatives:
$$
a(t) = 2 \alpha_w(t) + \frac{d \ln \eta}{d \ln t} \equiv 2 \alpha_w(t) + \gamma_\eta(t)
$$

- **Hypothesis:** The excess rule-specificity in the area exponent ($ICC = 0.38$) is entirely carried by the logarithmic drift of the filling fraction, $\gamma_\eta$. Rules with $a > 2/3$ are steadily consolidating internal bays ($\gamma_\eta > 0$), while rules with $a < 2/3$ are steadily developing internal dendritic fissures or lacunarity ($\gamma_\eta < 0$).
- **Test:** Compute $\eta(t) = A(t) / (W_x(t) W_y(t))$ across all 152 rules with $\ge 6$ runs in `experiments/archive/2026-10-b2-between-rule-variance/results/b2_probe.csv` in octave windows $k = 20..26$. Fit $\gamma_\eta = d \ln \eta / d \ln t$.
- **Prediction:**
  1. $\gamma_\eta$ accounts for $> 80\%$ of the variance in $a - 2\alpha_w$ ($R^2 \ge 0.80$).
  2. The between-rule ICC of $\gamma_\eta$ is $\ge 0.35$ (matching the excess ICC of area).
  3. The mean compactness $\bar{\eta}$ is negatively correlated with $\gamma_\eta$: rules with low initial compactness consolidate fastest.
- **What breaks it:** If $\gamma_\eta \approx 0$ for all rules, or if $\gamma_\eta$ fails to correlate with $a - 2\alpha_w$, the area-width discrepancy is an artifact of bounding-box orientation rather than internal compactness.

#### H1 result (done 2026-10-13; predictions not edited)
`uv run experiments/archive/2026-10-h1-lacunarity-decomposition/scripts/h1_lacunarity.py > experiments/archive/2026-10-h1-lacunarity-decomposition/results/h1_lacunarity.txt` (new script; input `experiments/archive/2026-10-b2-between-rule-variance/results/b2_probe.csv`, window $k = 20..26$ and the run filter of `experiments/archive/2026-10-b2-between-rule-variance/scripts/b2_anova.py`, so the numbers are comparable with B2). 99 rules, 1,185 non-escaped patched-start runs (1,164 in the core band $0.25 < \alpha_w < 0.42$), ~12 seeds each; $\gamma_\eta$ is `g_fill` of `analyse_probe.per_rule`, the log-log slope of $A/(W_xW_y)$ against $t$. Sanity check: $a - \alpha_x - \alpha_y$ equals $\gamma_\eta$ exactly in all runs (max abs diff 0.0000), so the identity holds with the two box sides.
- **Prediction 1 falsified.** $R^2(\gamma_\eta \to a - 2\alpha_w) = 0.456$ (core band 0.454; slope 1.05), against the $\ge 0.80$ required. The missing half is that $2\alpha_w$ uses the longer box side while the identity needs $\alpha_x + \alpha_y$; when the box is not square the two differ.
- **Prediction 2 falsified.** Between-rule ICC of $\gamma_\eta$ is **0.116** (core band 0.113; sd within 0.016, sd between 0.0056), against $\ge 0.35$ required. The same ICC of $a - 2\alpha_w$ is 0.087. So the area exponent's rule-specific share (ICC 0.27 all runs, 0.34 core band; $\alpha_w$ 0.26 / 0.12) is **not** carried by drift in the filling fraction; $\gamma_\eta$ is mostly run noise, as the width exponent is.
- **Prediction 3 supported, weakly.** Across rule means, corr(final fill, $\gamma_\eta$) = $-0.43$ (core band $-0.44$): low-compactness rules consolidate faster. Final fill is part of what $\gamma_\eta$ integrates, so this is partly mechanical; no control was run for that.
- **Sign claim.** Mean $\gamma_\eta = +0.006$; 85% of rules have $\gamma_\eta > 0$. Rules with $a > 2/3 + 0.01$ (n = 62) average $+0.0077$; rules with $a < 2/3 - 0.01$ (n = 6, too few to say anything) average $-0.0009$, not negative as predicted. corr($a$, $\gamma_\eta$) across rule means is $+0.43$ in the core band but $+0.09$ over all runs (outlier runs dominate). The picture "territories slowly consolidate" ($\gamma_\eta > 0$, small: 0.006 per unit $\ln t$) is real; "rules differ in area exponent because they consolidate at different rates" is not what these data show.
- **Residual question (new, unresolved).** If neither $\alpha_w$ (ICC 0.12) nor $\gamma_\eta$ (ICC 0.11) carries the between-rule variance of $a$ (ICC 0.34), where is it? The identity $a = \alpha_x + \alpha_y + \gamma_\eta$ says it must be in $\alpha_x + \alpha_y$ taken separately (the shorter side's exponent, i.e. box *shape* drift) or in covariances between the three terms. Not decomposed here; an ICC and covariance table of $(\alpha_x, \alpha_y, \gamma_\eta)$ is the natural next step and was not run. Limit: single window $k = 20..26$ (7 points per slope), and the 6-rule $a < 2/3$ group is too small for the sign test.

---

### H2. Anisotropic elongation under arrow bias
In the biased rotor (C2b/c), why does bias $0.25$ jump the area exponent from $0.68$ to $0.79$ while the width exponent remains $0.33$?

- **Hypothesis:** Arrow bias induces an elliptic deformation of the territory. If the major axis grows as $W_\parallel \sim t^{\alpha_1}$ and the minor axis as $W_\perp \sim t^{\alpha_2}$, bounding-box width is dominated by the major axis ($\alpha_w = \alpha_1 \approx 1/3$), while area grows as $A \sim W_\parallel W_\perp \sim t^{\alpha_1 + \alpha_2}$. At bias 0.25, the minor axis grows faster than the major axis ($\alpha_2 \approx 0.46$), filling in transverse space.
- **Test:** Measure the principal eigenvalues $\lambda_1(t), \lambda_2(t)$ of the spatial gyration tensor for the biased rotor at bias $\beta \in \{0, 0.05, 0.10, 0.15, 0.20, 0.25\}$ up to $2^{28}$ steps. Fit the individual exponents $\alpha_1, \alpha_2$ of $\sqrt{\lambda_1}$ and $\sqrt{\lambda_2}$.
- **Prediction:**
  1. At bias $0$, $\alpha_1 = \alpha_2 = 0.335 \pm 0.005$.
  2. At bias $0.25$, $\alpha_1 = 0.333 \pm 0.008$, while $\alpha_2 = 0.455 \pm 0.015$.
  3. The sum $\alpha_1 + \alpha_2 = 0.788 \pm 0.015$, exactly matching the measured area exponent $0.787$.
- **What breaks it:** If $\alpha_1$ and $\alpha_2$ remain equal at bias $0.25$, the area exponent increase is not driven by anisotropic axis scaling.

---

### H3. Universal scaling collapse of the blob class
Can the diverse growth curves of all core blob rules be collapsed onto a single universal master curve?

- **Hypothesis:** All core blob rules belong to a single scale-invariant universality class governed by the dimensionless time:
  $$
  \tau = (c_r \cdot \kappa_r)^{3/2} \cdot t
  $$
  Under this rescaling, the area growth curve $\tilde{A}(\tau) = A(t) / (c_r \kappa_r)$ and the radial density profile $\tilde{\rho}(\tilde{r})$ collapse onto a universal curve across all blob rules with no free parameters.
- **Test:** Take 30 diverse blob rules from `experiments/archive/2026-10-b2-between-rule-variance/results/b2_probe.csv` with $\kappa$ spanning $0.4$ to $2.5$. Rescale $A(t)$ by $\tau^{2/3}$ and compute the variance across rules before and after rescaling.
- **Prediction:** Rescaling by $(c_r \kappa_r)$ reduces the between-rule variance of normalized area $A(t) / t^{2/3}$ by $> 75\%$.
- **What breaks it:** If the variance reduction is $< 30\%$, the prefactor $K_r$ depends on additional invariants beyond $c_r$ and $\kappa_r$.

---

## I. Interface universality and surface roughness

### Context
Phase 2 settled the asymptotic behavior of the surface width exponent (A4c, Q7):
- Ants: $W_{\text{surf}} \sim t^{0.235 \pm 0.015}$ out to $2^{34}$.
- Rotor: $W_{\text{surf}} \sim t^{0.125 \pm 0.015}$ out to $2^{34}$.
The factor-of-two gap does not close over 6 decades. Yet both have identical bulk growth exponent $\approx 1/3$.
Kapri & Dhar conjectured $W_{\text{surf}} \sim t^{1/8} = t^{0.125}$ for the rotor. For ants, $0.25 = 1/4$ matches the classic Edwards-Wilkinson (EW) interface.

---

### I1. Edwards-Wilkinson vs Eulerian hyperuniform interface class
In standard interface growth in $1+1$ dimensions:
- **Edwards-Wilkinson (EW):** temporal exponent $\beta = 1/4 = 0.25$, spatial roughness exponent $\chi = 1/2 = 0.50$.
- **Kardar-Parisi-Zhang (KPZ):** temporal exponent $\beta = 1/3 \approx 0.33$, spatial roughness exponent $\chi = 1/2 = 0.50$.
- **Eulerian / Rotor interface:** Kapri & Dhar propose $\beta = 1/8 = 0.125$, $\chi = 1/4 = 0.25$.

- **Hypothesis:** The ant's perimeter belongs to the Edwards-Wilkinson class ($\beta = 1/4, \chi = 1/2$), where turn-sequence stochasticity acts as uncorrelated white noise on interface height. The rotor belongs to an Eulerian hyperuniform interface class ($\beta = 1/8, \chi = 1/4$), where the divergence-free rotor field suppresses interface fluctuations.
- **Test:** Unfold the perimeter $s \in [0, P(t)]$ into a 1D interface $h(s, t) = r(s, t) - \bar{r}(t)$. Compute the spatial height-height correlation function:
  $$
  C(l, t) = \langle (h(s+l, t) - h(s, t))^2 \rangle_s
  $$
  across spatial lags $l \in [2, P/4]$ for 10 core ants and 10 rotors at $t = 2^{30}$. Fit $C(l) \sim l^{2\chi}$.
- **Prediction:**
  1. For ants, $\chi = 0.50 \pm 0.04$ (Edwards-Wilkinson).
  2. For the rotor, $\chi = 0.25 \pm 0.04$ (Kapri-Dhar Eulerian class).
  3. This proves that ants and rotors belong to **distinct interface universality classes** despite sharing the bulk $t^{1/3}$ exponent.
- **What breaks it:** If ants have $\chi \approx 0.25$, they share the rotor's surface class and $\beta \approx 0.24$ is a very slow transient.

---

### I2. Hyperuniformity of boundary step fluctuations
Why would the rotor suppress surface fluctuations compared to the ant?

- **Hypothesis:** Rotor boundary visits are hyperuniform: in equal perimeter angular sectors of angle $\Delta \theta$, the variance of visit counts $\text{Var}(N)$ scales sub-linearly with the mean: $\text{Var}(N) \sim \langle N \rangle^{\gamma}$ with $\gamma < 1$. For ants, boundary visits are diffusive/Poissonian: $\text{Var}(N) \sim \langle N \rangle^1$.
- **Test:** Partition the boundary into 64 equal angular sectors. Count visits $N_i$ to each sector in octave windows $k = 22..26$ for 8 ants and 8 rotors. Fit $\text{Var}(N)$ vs $\langle N \rangle$.
- **Prediction:**
  1. For ants, $\gamma = 1.00 \pm 0.05$ (Poissonian).
  2. For rotors, $\gamma = 0.52 \pm 0.08$ (hyperuniform suppression of fluctuations).
- **What breaks it:** If both have $\gamma \approx 1$, hyperuniformity does not explain the rotor's smoother surface.

---

## J. Tethering physics: phase-space resonance, hubs, and formation

### Context
In Phase 2, three striking discoveries re-framed the nature of tethered ("hard") rules:
1. `RRRRRLLLLLL` tether is intermittent in age: taking the frozen field at $2^{25}$ and dropping a fresh ant at the origin heading North yields an **untethered** walk (`near_home` 0.061), whereas at $2^{22}, 2^{24}, 2^{26}$ it is tethered (0.36–0.47) (Q9).
2. The self-healing hypothesis was **reversed**: corrupting the *most-visited* cells hurts most, and rare colours double the damage at equal visit quartile (A6, Q13).
3. The hot windows become critical *late* in development ($2^{22}..2^{24}$), not early (E6).
4. Contiguous 5x5 patches cause $\approx 35\%$ less damage per rare cell changed than scattered swaps (E4, Q14).

---

### J1. The phase-space lock: mapping the attraction basin of RRRRRLLLLLL (Q9)
Why does the $2^{25}$ frozen field fail to tether a fresh ant starting North at the origin?

- **Hypothesis:** Tethering is a phase-locked limit cycle on the joint space $(x, y, \text{heading}, \text{colour})$. The basin of attraction $\mathcal{B}_{\text{home}}$ occupies only a tiny volume fraction of the core state space ($< 5\%$). The native ant remains tethered because its internal heading and arrival coordinates are synchronized with the field's cyclic rewrites; dropping an ant with an arbitrary heading (North) lands outside the basin.
- **Test:** On the frozen $2^{25}$ field of `RRRRRLLLLLL`, test all 4 headings $\{N, E, S, W\}$ and all entry coordinates $(x, y)$ in the core $r \le 10$ (441 sites $\times$ 4 headings = 1,764 initial conditions). Run each for $10^7$ steps and record `near_home`. Also extract the *exact* native state $(x^*, y^*, h^*)$ of the continuous run at step $2^{25}$.
- **Prediction:**
  1. Fewer than $5\%$ of test states achieve `near_home` $> 0.30$.
  2. The native state $(x^*, y^*, h^*)$ is strictly inside the tethered basin (`near_home` $\ge 0.40$).
  3. The tethered initial conditions form connected 1D orbit filaments in phase space, not a solid 2D spatial disc.
- **What breaks it:** If $> 50\%$ of initial conditions are tethered, the $2^{25}$ North start was an unlucky rare exception rather than evidence of phase locking.

---

### J2. The home as a reversible permutation network: centrality of critical cells
Why do the most-visited cells hurt most when corrupted, and why do rare colours double the damage?

- **Hypothesis:** The home functions as a cycle-preserving permutation network. The most-visited cells are high-centrality "hub switches" in the transition graph $G = (V, E)$; corrupting a hub breaks the cycle closure, converting closed recurrent loops into escaping open paths. Rare colours act as conditional control bits (branch selectors); corrupting a rare colour redirects entire loop families.
- **Test:** Construct the directed transition multigraph $G$ on cells within $r \le 12$ of the tether center for `RRRRRLLLLLL` over $10^6$ steps. Compute betweenness centrality $C_B(v)$ and page rank for every cell. Correlate $C_B$ with single-cell knockout damage measured via `examples/knock.rs`.
- **Prediction:**
  1. Knockout loss correlates strongly with betweenness centrality: Spearman $\rho(\text{loss}, C_B) \ge 0.72$.
  2. Controlling for $C_B$, cells holding rare colours still exhibit a $1.8\times \pm 0.3\times$ higher loss than common colours (confirming their role as branch selectors).
- **What breaks it:** If knockout loss does not correlate with betweenness centrality ($|\rho| < 0.25$), the network topology does not explain why visit frequency dictates vulnerability.

---

### J3. Contiguity penalty vs spatial dispersion: resolving E4 / Q14
Why does a contiguous 5x5 patch cost $\approx 35\%$ less per rare cell changed than scattered swaps?

- **Hypothesis:** High-centrality critical cells are clustered in an ultra-compact core ($r \le 4$). A contiguous 5x5 patch inevitably covers both critical hub cells and redundant peripheral cells (diminishing the marginal loss per corrupted cell), whereas scattered swaps select rare cells independently across multiple separate functional loops.
- **Test:** Compare contiguous $3 \times 3$ and $5 \times 5$ patches positioned directly over the highest-centrality hubs against scattered swaps whose radial distance distribution from the center is strictly matched to that of the patch.
- **Prediction:** When radial distance and hub centrality are matched, the damage ratio of patches to swaps shifts from $0.65$ to $1.00 \pm 0.12$.
- **What breaks it:** If radially matched patches still cause $< 75\%$ of the damage of swaps, spatial contiguity inherently promotes self-healing.

---

### J4. Late home formation: the condensation transition (E6)
Why do critical windows only become sensitive late in history ($2^{22}..2^{24}$)?

- **Hypothesis:** The home undergoes a sharp condensation transition. Prior to $t_c \approx 2^{21}$, the ant is in an extended chaotic transient with $R(t) \sim t^{1/3}$. At $t_c$, the boundary closes into a self-reinforcing reflecting cage; once closed, subsequent steps accrete frozen rings from inside out, locking the critical cells into place.
- **Test:** Trace the maximum displacement $R_{\max}(t)$ and the radius of gyration $R_g(t)$ continuously from $t = 10^5$ to $10^8$ for `RRRRRLLLLLL` and `RLLLLRRRRLR`.
- **Prediction:** $R_g(t)$ grows as $t^{0.33 \pm 0.03}$ up to a sharp transition time $t_c \in [10^6, 5\times 10^6]$, where $d R_g / dt$ drops abruptly by $> 90\%$ within a single octave.
- **What breaks it:** If $R_g(t)$ shows a smooth, continuous logarithmic deceleration across all octaves, there is no discrete condensation transition.

---

## K. Microscopic reversibility, dimensions, and skeleton classes

### Context
Phase 2 resolved the 3D exponents ($V \sim t^{0.769}$, $R \sim t^{0.237}$, D2c) and showed that the turmite $\sqrt{t}$ cluster is a 1D filamentary skeleton (D1).
Two fundamental theoretical questions remain open:
1. What role does microscopic invertibility play in enforcing the $t^{1/3}$ law?
2. What is the limit shape in 3D, and do the 289 ant frame builders belong to the turmite 1D skeleton class?

---

### K1. The No-Interior-Void theorem and microscopic reversibility
Why do Langton's ants grow as compact 2D discs with zero internal unvisited voids, whereas non-reversible growth models (Eden, DLA, percolation) produce porous fractals?

- **Hypothesis:** Microscopic invertibility prohibits isolated unvisited interior voids. An unvisited void requires a perimeter loop that self-intersects and traps empty sites; in an invertible deterministic automaton, any such enclosing orbit would create a conflict of pre-images upon time reversal.
- **Test:** Compute the Euler characteristic $\chi = N_{\text{components}} - N_{\text{holes}}$ and total void volume $V_{\text{void}}$ of the visited territory across 200 blob rules at $2^{26}$ steps. Compare against an explicitly non-invertible ant variant: rule updates increment $c \to (c+1) \bmod (n-1)$ when $c > 0$, merging colours 0 and 1 into a common absorbing sink.
- **Prediction:**
  1. For reversible ants, $V_{\text{void}} = 0$ for $100\%$ of rules at $2^{26}$ steps (no internal voids).
  2. For the non-reversible variant, $> 35\%$ of rules produce permanent internal voids with $V_{\text{void}} / A \in [0.02, 0.18]$, and the area growth exponent crosses over from $2/3$ to $0.85 \pm 0.08$.
- **What breaks it:** If any standard reversible ant generates a verified internal unvisited void of area $\ge 5$ cells, reversibility does not prohibit voids.

---

### K2. 3D limit shape: spherical isotropy vs faceted polyhedra (Q12)
In 3D, volume grows as $t^{0.769}$ and extent as $t^{0.237}$ (approaching $3/4$ and $1/4$). But is the asymptotic shape a sphere, an octahedron, or a cube?

- **Hypothesis:** The 3D limit shape is an isotropic sphere. The anisotropy tensor $A_{ij} = I_{ij} / \text{Tr}(I) - \frac{1}{3} \delta_{ij}$ decays toward zero as a power law:
  $$
  \|A(t)\| \sim t^{-\mu}, \quad \mu \approx 0.07 \pm 0.02
  $$
  explaining why the filling fraction converges from below.
- **Test:** Compute the inertia tensor eigenvalues $\lambda_1 \le \lambda_2 \le \lambda_3$ for the 3D ant at octave windows $k = 24..34$. Compute the sphericity $\Psi = \lambda_1 / \lambda_3$.
- **Prediction:** $\Psi(t)$ increases monotonically from $\approx 0.72$ at $2^{24}$ to $\ge 0.88$ at $2^{34}$, extrapolating to $1.00 \pm 0.03$ as $t \to \infty$.
- **What breaks it:** If $\Psi(t)$ plateaus at $< 0.80$, the 3D limit shape is an anisotropic or faceted polyhedron (e.g. rhombic dodecahedron).

---

### K3. Unifying the 289 ant frame-builders with the 1,560 turmite skeletons (Q15, D1)
The census contains 289 rules that stay on the grid but fill bounding boxes at only 2–6 steps per cell ("frame builders", e.g. `RLLR`). Turmites have an exact $\sqrt{t}$ cluster of 1,560 tables that form 1D skeletons (area/extent$^2 \approx 0.001$).

- **Hypothesis:** The 289 ant frame builders belong to the exact same dynamical class as the $\sqrt{t}$ turmite cluster: they expand by executing periodic perimeter patrols of length $L(t) \sim t^{1/2}$, laying a 1-cell thick boundary frame every cycle.
- **Test:** Run all 289 frame builders to $2^{26}$ steps using `src/bin/probe.rs`. Measure bounding box side $W(t)$ and area $A(t)$.
- **Prediction:**
  1. For $\ge 85\%$ of the 289 frame builders, the width exponent is $\alpha_w = 0.50 \pm 0.03$ (matching $\sqrt{t}$).
  2. The area exponent is $a \le 0.55$, and compactness $A / W^2$ decays as $t^{-0.48 \pm 0.04}$.
  3. This unifies the 289 ant frame-builders with the 1,560 turmite $\sqrt{t}$ tables into a single 1D perimeter-patrolling universality class.
- **What breaks it:** If the frame builders have $\alpha_w \approx 0.33$, they are slow-filling 2D blobs rather than 1D frames.

---

## M. Information thermodynamics and entropy production of territory growth

### Context
The ant begins on a blank tape ($c=0$ everywhere, Shannon entropy $S=0$). In the bulk territory, repeated visits randomize cell states, and 35 of 40 rules are empirically well-mixed (colours uniform, $S_{\text{cell}} \to \ln n$). Expanding the boundary requires writing virgin cells (erasing the blank background). In thermodynamic terms, does the $t^{1/3}$ growth rate reflect an information-theoretic work-dissipation balance?

---

### M1. Bulk entropy generation rate as the driver of boundary expansion
- **Hypothesis:** Territory expansion is governed by an information-theoretic rate limit. Each outward boundary step converts a deterministic zero-entropy site into a disordered state with entropy $\Delta S = \ln n$. Because the interior has an ergodic recurrence time $\langle \tau_{\text{return}} \rangle \sim R \sim t^{1/3}$, the marginal step cost to expand the perimeter by 1 cell scales as $t^{1/3}$. The $t^{1/3}$ exponent is the unique scaling where the rate of bulk Shannon entropy generation $\dot{S}_{\text{bulk}}$ balances the boundary Landauer expansion work.
- **Test:** Compute the Shannon entropy production rate $\dot{H}(t) = \frac{d}{dt} \left( -\sum_{c=0}^{n-1} p_c(t) \ln p_c(t) \right)$ and the mutual information between adjacent cells $I(c_x; c_{x+1})$ across octave windows $k = 20..28$ for 25 core blob rules using `src/bin/colourstats.rs`.
- **Prediction:**
  1. The ratio of bulk entropy production to territory growth rate, $\mathcal{Q} = \dot{H}_{\text{bulk}} / (dA/dt)$, converges to a universal constant $\mathcal{Q}^* = 1.00 \pm 0.08$ across all rules regardless of rule length $n$.
  2. The mutual information between adjacent bulk cells decays as $I(r) \sim r^{-\eta_{\text{info}}}$ with $\eta_{\text{info}} \approx 1.0 \pm 0.15$ (hyperuniform spatial information structure).
- **What breaks it:** If $\mathcal{Q}$ varies by more than a factor of 2 across rule lengths $n \in [3, 12]$, information dispersal does not govern the boundary growth rate.

---

### M2. Algorithmic compressibility deficit of chaotic pattern fields
Are the visited patterns truly incompressible pseudo-random fields, or do Eulerian cycle constraints imprint measurable algorithmic compressibility?
- **Hypothesis:** The interior configuration is not i.i.d. random noise. It carries a persistent algorithmic compression deficit: the normalized compressed size $\mathcal{C}(t) = \text{compressed\_bytes} / (A \cdot \log_2 n)$ scales as $\mathcal{C}(t) = 1 - c_0 t^{-1/6}$, reflecting the divergence-free loop constraints of the ant's trajectory.
- **Test:** Save 2D territory snapshots at $t = 2^{24}, 2^{26}, 2^{28}$ across 16 rules. Compress the visited cell arrays with Zstandard (level 19) and PAQ8.
- **Prediction:** $\mathcal{C}(t)$ approaches 1 from below with an exponent $0.16 \pm 0.04$, matching the predicted $t^{-1/6}$ loop-correlation density.
- **What breaks it:** If compression ratio is strictly independent of $t$ (within 0.1%), bulk patterns have no scale-dependent algorithmic correlations.

---

## N. Topological monodromy, cycle holonomy, and phase-space fibrations

### Context
An ant tracing loops on $\mathbb{Z}^2$ induces a permutation $\sigma \in S_n$ on cell colours. In rotor-router networks, the Abelian Sandpile Group / Jacobian $\text{Jac}(G)$ completely determines cycle invariants. What algebraic group governs Langton's ants?

---

### N1. Monodromy group transitivity: the topological order parameter for chaos vs tethering
- **Hypothesis:** The transition between chaotic $t^{1/3}$ expansion and tethered log-confinement is a topological symmetry-breaking transition. Every closed cycle $\gamma$ on the square grid induces a monodromy permutation $\sigma_\gamma \in S_n$ on the colour states. For chaotic rules, the holonomy group $\mathcal{H} = \langle \sigma_\gamma : \gamma \in \pi_1(\text{visited}) \rangle$ is 2-transitive (isomorphic to the full symmetric group $S_n$ or alternating group $A_n$). For tethered ("hard") rules, $\mathcal{H}$ collapses to an intransitive, solvable subgroup of order $|\mathcal{H}| \le 4n \ll n!$.
- **Test:** Instrument `src/probe.rs` to extract all closed cycles of lengths $L \in [4, 16]$ traversed by the ant in windows $k = 20..24$. Compute the generated permutation group on $\{0, \dots, n-1\}$ for 40 chaotic rules and all 26 tested tethered rules using cycle multiplication.
- **Prediction:**
  1. For $100\%$ of chaotic blob rules, the cycle holonomy group is $S_n$ (or $A_n$).
  2. For $100\%$ of tethered rules, $\mathcal{H}$ has at least 2 non-trivial invariant sets (intransitive) and $|\mathcal{H}| < 24$.
  3. This establishes a computable, finite-time topological order parameter that rigorously separates chaos from tethering without requiring long-time simulation.
- **What breaks it:** If any tethered rule generates a 2-transitive group $S_n$, cycle holonomy does not govern confinement.

---

## O. Conformal curvature damping and the Anti-Mullins-Sekerka stability

### Context
Why do Langton's ants form isotropic circular discs rather than fractal dendrites? In classical Laplacian growth (DLA, Eden model, Hele-Shaw flow), protruding fingers absorb higher flux and sprout instabilities (Mullins-Sekerka instability). Why is the ant's boundary strictly stable against fingering?

---

### O1. Curvature-driven negative feedback on boundary protrusions
- **Hypothesis:** Langton's ant exhibits an intrinsic **anti-Mullins-Sekerka mechanism**. When a boundary protrusion of height $\delta h > 0$ forms, its convex corners deflect the arriving ant away from the tip and back into the adjacent concave bays. This creates negative feedback: the probability of adding cells to the tip decreases with tip height, while the bays receive enhanced visit flux, damping perturbations at rate $\frac{d(\delta h)}{dt} \sim -\lambda (\delta h)^\mu$.
- **Test:** Prepare a circular territory of radius $R_0 = 200$ at $t = 2^{26}$. Artificially attach a rectangular protrusion of width $W = 8$ and height $H \in \{5, 10, 20, 40\}$ cells to the boundary, or carve an indentation of depth $H$. Resume the simulation and measure the relaxation time $T_{\text{relax}}(H)$ until the envelope is restored to roundness.
- **Prediction:**
  1. Protrusions are damped sub-diffusively: $T_{\text{relax}}^{\text{bump}}(H) \sim H^{1.45 \pm 0.12}$.
  2. Indentations are filled ballistically: $T_{\text{relax}}^{\text{notch}}(H) \sim H^{0.95 \pm 0.08}$.
  3. The asymmetric ratio $T^{\text{bump}} / T^{\text{notch}} \sim H^{0.5}$ guarantees that indentations fill twice as fast as bumps can grow, explaining why the macroscopic envelope remains strictly convex.
- **What breaks it:** If $T_{\text{relax}}^{\text{bump}} \sim H^3$ (standard diffusive leveling) or if bumps accelerate and grow into needles ($d(\delta h)/dt > 0$), the circular limit shape is not stabilized by geometric curvature deflection.

---

## P. Coordination number and lattice geometry: Hexagonal ($z=3$) vs Triangular ($z=6$)

### Context
Phase 2 measured area exponents across planar lattices:
- Square ($z=4$): $a = 0.679 \approx 2/3$.
- Triangular ($z=6$): $a = 0.676 \approx 2/3$.
- Hexagonal ($z=3$): $a = 0.712 \pm 0.015$ (anomalously high!).
Why does coordination number $z=3$ systematically elevate the growth exponent above $2/3$?

---

### P1. Immediate backtracking prohibition and boundary mean free path on $z=3$
- **Hypothesis:** On the honeycomb lattice ($z=3$), an ant on a vertex has only 3 incident edges. A turn rule $\{L, R\}$ deflects by $\pm 120^\circ$; immediate $180^\circ$ U-turns are geometrically impossible on a single node. The absence of immediate back-tracking inflates the boundary mean free path $\ell_{\text{mfp}} \sim 1/(z-2) = 1.0$ (compared to $1/2$ on $z=4$ and $1/4$ on $z=6$). This suppresses normal reflection and forces tangential boundary gliding, elevating $\kappa$. As $t \to \infty$, the territory radius outgrows $\ell_{\text{mfp}}$, and $a(t)$ must cross over to $2/3$.
- **Test:** Run 30 hexagonal rules to $2^{32}$ steps using `src/ext.rs` on a honeycomb grid. Compute the local exponent series $a_k$ over octave windows $k = 22..32$ and measure the boundary persistence length $\ell_{\text{edge}}(t)$.
- **Prediction:**
  1. The local exponent $a(t)$ decreases monotonically from $0.712$ at $2^{26}$ toward $0.670 \pm 0.008$ at $2^{32}$.
  2. The deviation $\Delta a(t) = a(t) - 2/3$ decays as a power-law crossover: $\Delta a(t) \sim t^{-0.065 \pm 0.015}$.
  3. Triangular lattice ($z=6$) shows the opposite sign: $a(t)$ approaches $2/3$ from below ($0.665 \to 0.667$).
- **What breaks it:** If $a(t)$ on the hexagonal lattice remains constant at $0.712 \pm 0.005$ across all 10 octaves with zero downward drift, the honeycomb ant belongs to a distinct non-cube-root universality class.

---

## Q. Multi-ant chiral domain walls and collective exclusion dynamics

### Context
What happens when two or more ants inhabit the same board? Langton's ant rules have definite chirality ($L \leftrightarrow R$). If multiple ants interact on a shared tape, do they coalesce, partition territory, or form phase boundaries?

---

### Q1. Chiral domain walls between conjugate ant pairs $(A, \bar{A})$
- **Hypothesis:** When an ant $A$ (rule string $R$) and its chiral conjugate $\bar{A}$ (rule $\bar{R}$ with $L \leftrightarrow R$ inverted) start on a blank board separated by distance $d_0$, their territories do not blend. Upon collision, the opposite chiralities induce destructive interference in turn parity, freezing a stationary 1D domain wall between them. The two ants bounce off this mutual boundary as if it were an unvisited wall, cleanly partitioning the plane.
- **Test:** Run $(A, \bar{A})$ pairs for 12 core rules at initial separations $d_0 \in \{50, 100, 200\}$ cells to $2^{28}$ steps using a multi-walker extension of `src/fast.rs`. Measure the number of mutual territory trespasses $N_{\text{cross}}$ and the roughness $\chi_{\text{wall}}$ of the contact interface.
- **Prediction:**
  1. $N_{\text{cross}} = 0$ for $> 85\%$ of matched pairs after initial territory contact.
  2. The interface between territories is an Edwards-Wilkinson line with roughness exponent $\chi_{\text{wall}} = 0.50 \pm 0.04$.
  3. The joint area growth satisfies $A_{\text{total}}(t) = 2 \cdot A_{\text{single}}(t/2)^{2/3} \cdot (1 - O(d_0 / R))$.
- **What breaks it:** If the ants interpenetrate freely, erasing each other's boundaries and creating a homogeneous single blob, chirality does not induce phase separation.

---

## R. The "fast tail" census outliers ($a \approx 0.75 - 0.85$): intermediate scaling vs latent highways

### Context
In the census of 2,622 blob rules, 103 rules have $\gamma_\kappa > 0$ and area exponents significantly above $2/3$ ($a \approx 0.75 - 0.85$). Are these rules a genuine non-cube-root scaling phase, or are they latent highways with long incubation periods?

---

### R1. Fourier spectral signature of latent highways in fast-tail blob rules
- **Hypothesis:** The 103 fast rules are **not** an anomalous scaling class; they are latent long-period highways. A true chaotic blob rule has a continuous, broadband velocity power spectrum $S_v(f) = \int e^{i f \tau} \langle \vec{v}(t) \cdot \vec{v}(t+\tau) \rangle d\tau$. A rule with an impending highway instability develops discrete, sharp spectral resonances at harmonic frequencies $f_k = k / P_{\text{highway}}$ millions of steps before the highway actually detaches.
- **Test:** Compute the discrete Fourier transform of the ant velocity vector $\vec{v}(t)$ over $t \in [10^7, 10^8]$ for all 103 fast rules and 100 control core blob rules. Compute the spectral peak-to-floor ratio $\mathcal{R}_{\text{peak}} = \max_f S(f) / \bar{S}$.
- **Prediction:**
  1. $> 65\%$ of the 103 fast rules exhibit sharp spectral peaks with $\mathcal{R}_{\text{peak}} \ge 8.0$ (indicating latent highway resonance).
  2. For control blob rules, $\mathcal{R}_{\text{peak}} \le 2.2$ (featureless broadband noise).
  3. In the extended $10^{11}$-step sweep (`experiments/archive/2026-10-h1-lacunarity-decomposition/scripts/run_1e11b.sh`), rules with $\mathcal{R}_{\text{peak}} \ge 8.0$ have a 10x higher breakout hazard rate than rules with flat spectra ($p < 10^{-5}$).
- **What breaks it:** If all 103 fast rules exhibit flat, featureless spectra identical to core blob rules while maintaining $a > 0.75$ out to $10^{11}$, the fast tail is an intrinsic, non-highway dynamical phase.

---

## L. Suggested priority and resource budget

| Priority | Item | Target | Cost | What it decides | Status |
|---|---|---|---|---|---|
| **1** | **F1** | Interior excursion distribution $P(L)$ | ~1 CPU-hour (`experiments/archive/2026-10-arm-kappa-depletion-arms/results/armc_specs.txt`) | Explains what sets rule-specific $\kappa$ | Queued |
| **2** | **I1** | Interface correlation $C(l)$ (EW vs Rotor) | ~2 CPU-hours (20 runs to $2^{30}$) | Decides whether ants and rotors are different surface universality classes | Queued |
| **3** | **G1** | `RLRLLL` escape trace | < 15 CPU-min (`ribbon_trace.rs`) | Reveals the mechanism of non-highway grid breakouts | **Done**, mechanism **not** established (abrupt switch to a 4.03 steps/cell builder; see final G1 result) |
| **4** | **H1** | Dynamic lacunarity & covariance decomposition | Analysis of existing `b2_probe.csv` | Resolves the area ICC (0.34) vs width ICC (0.12) discrepancy | **Done** (joint axis co-variation, not lacunarity) |
| **5** | **N1** | Topological monodromy group transitivity | ~1 CPU-hour (`src/probe.rs`) | Finite-time algebraic order parameter separating chaos from tethering | Queued |
| **6** | **O1** | Curvature damping / Anti-Mullins-Sekerka | ~2 CPU-hours (`examples/shape.rs`) | Explains why Langton's ants form discs rather than DLA dendrites | Queued |
| **7** | **P1** | Hexagonal lattice ($z=3$) crossover to 2/3 | ~3 CPU-hours (`src/ext.rs` to $2^{32}$) | Tests if $z=3$ is anomalous scaling or backtrack-suppressed transient | Queued |
| **8** | **Q1** | Chiral domain walls between $(A, \bar{A})$ | ~2 CPU-hours (`src/fast.rs` 2-ant) | Tests if chirality induces phase separation in multi-walker systems | Queued |
| **9** | **R1** | Fast-tail FFT velocity spectrum | ~1 CPU-hour (103 fast rules) | Decides whether $a > 0.75$ rules are latent highways or an anomalous class | Queued |
| **10** | **M1** | Landauer entropy production rate $\dot{H}$ | ~1 CPU-hour (`colourstats`) | Tests if $t^{1/3}$ is derived from information erasure work balance | Queued |
| **11** | **J1** | `RRRRRLLLLLL` phase-space basin | ~2 CPU-hours (`examples/tetherlab.rs`) | Explains why frozen fields fail to tether arbitrary fresh ants | Queued |
| **12** | **K3** | 289 ant frame-builders vs turmite $\sqrt{t}$ | ~3 CPU-hours (`sweep_lean`) | Unifies the census frame builders with the 1D turmite cluster | Queued |
| **13** | **K1** | No-Interior-Void test (reversibility) | ~2 CPU-hours (`src/colours.rs`) | Links compact disc growth to microscopic invertibility | Queued |
| **14** | **G2** | Complete $10^{11}$ survivor census | Ongoing (`experiments/archive/2026-10-h1-lacunarity-decomposition/scripts/run_1e11b.sh`) | Decides if late highway onset keeps thinning or reaches a floor | Running |

---

## Appended results (2026-10-13, while the 10^11 census runs)

### H3 result (predictions above not edited)
`uv run experiments/archive/2026-10-h3-scaling-collapse/scripts/h3_collapse.py > experiments/archive/2026-10-h3-scaling-collapse/results/h3_collapse.txt` (input `experiments/archive/2026-10-b2-between-rule-variance/results/b2_probe.csv`, 99 rules, 1,164 core-band patched-start runs, rule means over ~12 seeds). This tests a weaker version of H3 than written: the 99 b2 rules rather than 30 chosen to span $\kappa$ 0.4-2.5, no radial-profile collapse, and $c$, $\kappa$ taken from the last window ($k = 26$) of the same runs, so part of the agreement is the growth identity itself, not independent confirmation.
- Variance of $\ln(A/t^{2/3})$ at $k = 26$ across rule means: 0.127. After subtracting $\ln(c\kappa)$ (the prediction's parameter-free rescaling): 0.053, a reduction of **58.6%**. Prediction ($> 75\%$) **falsified**; the "breaks it" level ($< 30\%$) is not reached either. A free fit $\ln K = 1.79 + 0.695\ln(c\kappa)$ gives $R^2 = 0.73$ (corr $+0.85$): $c\kappa$ is a strong but not exact carrier of the prefactor, and the fitted power 0.70 is not 1. Not done: the radial-density-profile collapse; the 30-rule selection.

### H1 follow-up: where the between-rule variance of the area exponent sits
Scripts `experiments/archive/2026-10-h1-lacunarity-decomposition/scripts/h1_lacunarity.py` and `experiments/archive/2026-10-h1-lacunarity-decomposition/scripts/h1_decomp.py` (input `experiments/archive/2026-10-b2-between-rule-variance/results/b2_probe.csv`, 99 rules, 1,164 core-band patched-start runs, rule means over ~12 seeds).
- **Axis-specific ICCs:** In the core band ($0.25 < \alpha_w < 0.42$), $\mathrm{ICC}(a) = 0.337$. When bounding-box axes are aligned to major and minor growth directions:
  - $\mathrm{ICC}(\alpha_{\text{long}}) = \mathbf{0.267}$ (sd within 0.0176, sd between 0.0106).
  - $\mathrm{ICC}(\alpha_{\text{short}}) = \mathbf{0.118}$ (sd within 0.0168, sd between 0.0062).
  - $\mathrm{ICC}(\gamma_\eta) = \mathbf{0.113}$ (sd within 0.0158, sd between 0.0056).
  The reason $\alpha_w$'s ICC was reported as only 0.120 in B2 is that $\alpha_w$ took $\max(W_x, W_y)(t)$ at each individual step, which introduces switching noise. Tracking the major axis directly recovers an ICC of 0.267!
- **Between-rule variance decomposition:** For the rule-mean identity $a = \alpha_{\text{long}} + \alpha_{\text{short}} + \gamma_\eta$, the total between-rule variance $\mathrm{Var}_{\text{between}}(a) = 3.54 \times 10^{-4}$ decomposes as:
  - $\mathrm{Var}(\alpha_{\text{long}})$: **39.1%**
  - $2 \times \mathrm{Cov}(\alpha_{\text{long}}, \alpha_{\text{short}})$: **24.8%**
  - $\mathrm{Var}(\alpha_{\text{short}})$: **17.5%**
  - $\mathrm{Var}(\gamma_\eta)$: **15.0%**
  - $2 \times \mathrm{Cov}(\alpha_{\text{long}}, \gamma_\eta)$: **10.1%**
  - $2 \times \mathrm{Cov}(\alpha_{\text{short}}, \gamma_\eta)$: **-6.5%**
- **Conclusion:** Over 64% of the between-rule variance of the area exponent is carried directly by the major axis growth rate $\alpha_{\text{long}}$ and its positive covariance with $\alpha_{\text{short}}$. The two orthogonal dimensions expand in lockstep with rule-specific vigor (scale), while dynamic shape distortion and internal lacunarity ($\gamma_\eta$) account for only a minor fraction of the between-rule variation.

### G1 follow-up: summary of the boundary breakout
See Section G1 above. `ribbon_trace.rs` demonstrated that the non-highway escape of `RLRLLL` is an extreme anisotropic surface wave: the ant undergoes an abrupt transition from high steps/cell ($> 1000$) to quasi-ballistic step efficiency ($\eta_{\text{step}} = 4.027$ steps/new cell) with an aspect ratio exceeding 200:1 ($\Delta y \sim 10^4$ vs $\Delta x \sim 40$ per million steps), continuously carving a vertical slab until leaving the grid at step 12.97B. *(Superseded: "surface wave" is withdrawn, see the note under the first G1 result; the breakout is an abrupt switch to a 4-steps-per-cell builder with no established mechanism.)*

---

## S. A sharper frontier: what would constitute an explanation?

### Status and scope of this expansion (2026-10-13, after the results above)

The proposals below are **new, untested hypotheses**, informed by the recorded G1, H1 and H3 results and the Arm A–C ledger in `notes/kappa-experiment-design.md`. No new measurements were made for this expansion. Numerical thresholds below are proposed decision rules, not observed values or calculated power guarantees. Before execution, commit a protocol recording the exact rules, seeds, checkpoints, estimators and exclusions; the present date alone does not establish ordering relative to unrelated work running elsewhere.

The central question is becoming more precise: **what information in the evolving tape controls the rate at which the walker finds new ground?** A useful answer should predict a future window from an earlier one, survive a targeted intervention, and explain both ordinary blobs and a conspicuous failure case. Explaining only the ensemble-average exponent is too weak: many different mechanisms could produce the same exponent.

### S1. Repair the questions before spending compute

These are amendments to the interpretation and design of earlier items; the original predictions remain unchanged.

1. **F1: a mean-return identity does not predict a median.** If edge episodes and interior excursions partition a window, their total durations determine boundary occupancy, up to incomplete episodes. Thus a relation between mean excursion duration and kappa is partly bookkeeping. A rare tail can change the mean with almost no change in the median. Failure of the median prediction would not rule out excursions. Record incomplete excursions, maximum depth and return displacement; compare tail contribution and typical duration separately. Define layers on the evolving territory, and quantify the difference from layers frozen at window start.
2. **F3 and G2: separate censoring from physics.** A kappa peak that plateaus is not necessarily a board artifact; it could be a bounded physical crossover. Conversely, a peak not reached before termination is not a measured maximum. Board exit is a computational event, not proof of a dynamical transition. For survival fits retain the full risk set, interval-censored onset times and distinct causes of exit. A declining escape fraction per logarithmic decade does not by itself establish the proposed instantaneous hazard exponent, a nonzero survivor fraction, or a median lifetime of $10^{16}$.
3. **F4 and H3: do the scaling algebra first.** With $P=g\sqrt A$ and constant $c,\kappa,g$, the growth identity integrates to
   $$A(t)^{3/2}-A(t_0)^{3/2}=\frac32 c\kappa g(t-t_0).$$
   The prefactor of $t^{2/3}$ therefore scales as $(c\kappa g)^{2/3}$, not $c\kappa$. H3's fitted power near 0.70 is compatible with this conditional derivation; it is not independent evidence for it. Test an early-window estimate of $c\kappa g$ against later growth, including variation in $g$. Similarly, fixed $b$ in F4 gives $b/R\to0$ and erases persistent rule differences: a surviving impedance explanation needs a scale-dependent $b$ or a rule-dependent limiting coefficient. A continuum boundary law also needs a defined source and moving-boundary mass balance.
4. **G1 and R1: efficiency is not periodicity.** Four steps per new cell does not establish a four-step limit cycle. Verify repeated tape configurations and displacement in a moving frame. Spectral peaks must beat surrogates with the same short-lag correlations and lattice parity; the maximum over many frequency bins cannot be compared with an arbitrary flat-spectrum cutoff independent of record length.
5. **G3 and H2: finite-time bounds matter.** At fixed step count the visited area is bounded, so its distribution cannot literally have infinite variance. Test a growing, truncated heavy tail against a two-population mixture of ordinary runs and breakouts. Likewise, a presently shorter axis can grow faster for a finite window, but cannot remain the shorter axis with a larger asymptotic power forever. Track axis crossings and distinguish transient rounding from different limiting exponents.
6. **I1–I2 and K2: an exponent or tensor is not a universality class.** The interface grows on an expanding domain, and raw sector-count variance mixes mean shape, unequal exposure and temporal correlations. Define the growth clock, remove deterministic angular structure and measure spatial *and* temporal correlations. A cube has isotropic second moments: an inertia eigenvalue ratio near one cannot distinguish it from a sphere. Add directional support radii and fourth-order angular modes before claiming a spherical limit shape.
7. **K1 and N1: reversibility is weaker than the proposed topology.** A unique predecessor does not forbid holes in a projected visited set. For a prescribed path, cell updates are additions of visit counts modulo $n$: on a fixed set of sites they lie in a product of cyclic groups. This construction alone cannot generate the proposed arbitrary $S_n$ holonomy. A state-dependent return map on a specified section of the full configuration space might be interesting, but must be defined before group computation. Neither a finite classification sample nor reversibility alone proves an asymptotic classification theorem.
8. **M1–M2: distinguish information proxies from physical entropy.** A deterministic blank-start field is not a thermodynamic bath. Single-site histogram entropy is bounded by $\ln n$; it is not extensive bulk entropy, and its derivative cannot be substituted for $d(AH)/dt$. No Landauer work balance has been specified. Compression can test statistical structure, with bits/bytes corrected and occupancy masks encoded separately, but is not an estimate of algorithmic complexity. Use same-mask, same-histogram shuffled controls.
9. **O1, P1 and Q1: make interventions and clocks explicit.** Visited territory does not shrink, so a bump can relax only relative to a growing envelope. Editing colours is different from editing the visited mask. Square-grid L/R ants also cannot immediately reverse in one step, so this alone cannot explain a honeycomb anomaly. Multi-ant updates need a fixed scheduler, collision semantics and a time unit: two independent walkers with total budget $T$ have benchmark union area $2K(T/2)^{2/3}$ before overlap, not an extra power of the single-ant area.

These repairs sharpen rather than diminish the interesting questions. The strongest new experiments below ask where the memory resides, how it travels, and whether rare changes in that memory reorganize the entire walk.

## T. Where does the tape store transport memory?

### T1. Excursion tomography: typical loops or rare journeys?

**Question.** Can almost all boundary contacts look identical while a tiny fraction of interior journeys sets kappa?

**Competing mechanisms.** In a shallow-loop mechanism, rules differ in ordinary return times. In a trap mechanism, their typical excursions agree but rare long journeys consume different fractions of the time budget. In a transport mechanism, durations agree after scaling but returns land in different boundary sectors, changing which frontier is accessible next.

**Experiment.** Start with the existing 44-rule matched-pair pool. Use patched-start seeds 0–7, windows $k=22..25$, and retain blank starts as a separate replication rather than a ninth seed. For each excursion record duration $L$, maximum inward depth divided by $R=\sqrt{A/\pi}$, and departure-to-return displacement divided by $R$. Record the fraction of interior time accounted for by the longest 1% of completed excursions, plus the unresolved time in excursions crossing a window endpoint. Do not silently discard the latter. Use bounded summaries and checkpointed long-excursion records rather than a dump of every step.

**Proposed prediction.** In at least two thirds of usable matched pairs, the low-kappa member has a larger long-excursion time fraction, while paired median durations differ by less than a factor of two. This is a specific bet on rare journeys rather than a re-test of the occupancy identity. Resample rules, respecting shared members of pairs; 26 overlapping pairs are not 26 independent experiments.

**Decisive follow-up.** Estimate duration/depth/return-location features in the early windows, then predict later kappa for entirely held-out rules. Require held-out $R^2\ge0.3$ against a constant baseline before calling this a useful predictor, following the existing kappa design. If only same-window mean durations work, we have an accounting description, not a mechanism.

### T2. The memory transplant: geometry, histogram, or spatial arrangement?

**Question.** If the field is the walker's memory, can we transplant its transport behaviour without changing the rule?

**Design.** At checkpoints $2^{22}$ and $2^{24}$, clone each state into four continuations: untouched; colours permuted within narrow depth bands; colours permuted only in the deep interior; colours permuted only within four cells of the frontier. Preserve position, heading, visited mask and each permuted region's colour counts. Use deterministic Fisher–Yates permutations with recorded intervention seeds. Include a sham operation and several independent permutations per original state. Original states, not shuffled descendants, are the replication units.

**Prediction.** If global spatial memory controls kappa, deep-interior scrambling changes post-intervention boundary occupancy by more than twice the seed-matched sham variation, even with unchanged geometry and depth-conditioned histograms. If the frontier is sufficient, only the edge intervention has a sustained effect. If every effect disappears after one ordinary excursion, the relevant memory is short-lived rather than a persistent bulk structure.

**Readout.** Measure response against time since the walker first reaches an edited cell, as well as steps since intervention. Compare at equal added area and equal elapsed steps. A perturbation that has not been encountered is not a null causal test. Artificial fields need not be naturally reachable: interpret the test as a sufficiency/necessity intervention, then replicate the strongest result with smaller, naturally occurring patches.

### T3. Age versus depth: is the depleted crust a fossil or an active barrier?

**Idea.** Radial depth conflates geometry with history. Two cells at the same depth may have been discovered at very different times; an apparently special spatial layer could instead be an age cohort that has not been revisited.

**Test.** Maintain discovery times for a pilot subset and measure revisit hazard conditional on cell age, depth, colour and local exposed-neighbour count. Sample cells by a seeded, fixed spatial hash to keep memory bounded. Compare models using depth alone, age alone, and both, evaluating later windows and held-out rules. Split the analysis between the crust and uniform classes identified in Arm A.

**Prediction.** A fossil-layer explanation predicts that adding age removes at least half of the held-out predictive improvement previously attributed to depth. An active barrier predicts a residual depth effect after age matching. Follow cohorts as the frontier passes them: do they remain inactive, reactivate abruptly, or recover smoothly?

**Why it matters.** An age-controlled mechanism suggests a renewal description; a depth-controlled mechanism suggests transport through a spatial barrier. Their radial profiles can look almost identical in a single snapshot.

### T4. A local conservation law hiding behind apparent disorder

**Question.** Can we replace an unsupported topological group with an exact balance law that constrains transport?

For each site, the number of departures fixes its colour increment modulo $n$. Globally, path continuity also constrains incoming minus outgoing edge traversals by the walk's endpoints. These are exact starting points. The nontrivial issue is whether the turn rule forces an additional cancellation in directed edge flux over completed local colour cycles.

**First experiment is algebraic.** Enumerate admissible short histories for small rules and search for rule-dependent weighted sums of directed crossings and local states that remain bounded. Test candidates against the reference implementation before trying to fit a scaling law. Incoming headings must be retained: visit count alone generally does not determine exit direction.

**Proposed conjecture.** A subset of ordinary blob rules has a coarse flux discrepancy that grows with boundary size rather than visited area, while fast-tail and tethered examples violate the same bound or satisfy a different one. Specify the candidate observable before a large sweep; searching many weights and reporting the best cancellation would be exploratory.

**Payoff if true.** A bound on flux imbalance could explain why a noisy-looking field still redistributes visits evenly. The proof target would be a discrepancy bound under explicit assumptions, not a direct proof of the cube-root exponent. If no extra cancellation survives tiny counterexamples, stop this branch cheaply.

**Update 2026-10-22 (appended; the text above is the 2026-10-13 proposal).** The algebraic first experiment was run twice
with different search strategies: an enumerative miner at moduli 2 and 4 (`experiments/archive/2026-10-invariant-mining/`) and a
Smith-normal-form solver for all moduli with sublattice families (`experiments/archive/2026-10-invariant-mining-snf/`, solver
`experiments/_lib/lawmod.py`). They agree exactly (508 rules, 1016 cells). Result: within additive local laws
(`a x + b y + e t + Phi(h, class) + sum w(class, colour)`) the whole law group of a rule is a function of
`(n, ±D mod 4, trivial?)`, `D = #R - #L`; it is **blind to the order of the colours**, so `RRLL` and `RLRL` have isomorphic
groups. The laws are checkerboard parity, heading parity, the colour clock mod `n`, sublattice colour clocks (universal
order at `m = n`: F3 = n^2 x F2 for n = 2..8, unexplained), and for `D = 0 mod 4` heading = tape mod 4 (Langton: heading =
number of colour-1 cells mod 4). So the "extra cancellation" this section hoped for does not exist in the additive
ansatz; flux discrepancy, if it constrains transport at all, has to come from laws that couple the ant to neighbouring
colours. Registered `P4` (heading from tape iff `D = 0 mod 4`) failed: heading *parity* is tape-determined for every even
`n`. No claim about growth, highways or the exponent. Signature `NR-20261022-additive-laws-order-blind`.

## U. Rare reorganizations: nucleation, susceptibility and ageing

### U1. Is a ribbon a replicating defect?

G1 gives a striking geometric observation but leaves the causal question open: does a finite patch carry the breakout, or does the entire old blob support it?

**Experiment.** Replay a checkpoint just before the recorded breakout and save local windows around the first sustained ribbon segment. Transplant nested patches into three recipient contexts under the same rule: virgin background, a matched quiet frontier, and the original field with the surrounding region scrambled. Vary patch side lengths over 16, 32, 64 and 128 cells; test all four headings. Preserve or explicitly reconstruct the visited mask and distinguish the colours needed for dynamics from the mask used for measurement. Use several quiet-frontier recipients selected before outcomes are known.

**Prediction.** A self-propagating defect will reproduce sustained directed growth from some finite patch in at least half the matched recipients, with a bounded transverse profile over successively doubled observation lengths. A boundary-supported mode will require an existing frontier but tolerate bulk scrambling. A global transport state will fail both local transfers.

**Theory opportunity.** If a repeatable moving tile appears, seek a finite certificate: a patch plus an incoming state maps after $p$ steps to a translated copy, with all touched cells accounted for and no reliance on an unverified exterior. Such a certificate could prove propagation for that initial pattern even if predicting spontaneous nucleation remains hard. Failure to transfer is informative only after checking the patch contains every cell touched during the candidate cycle.

### U2. Damage spreading: chaos in trajectories versus stability of growth

**Question.** Why might one changed cell completely alter the trajectory while leaving the growth law unchanged?

**Design.** Clone a natural snapshot and change one cell by one colour increment. Choose cells separately from the hot core, ordinary interior and frontier; pair each with an untouched continuation. Track first encounter, walker separation, number of differing cell states and differences in area and kappa. Use identical underlying noise streams for stochastic controls, with the coupling rule recorded.

**Prediction.** Ordinary blobs exhibit rapid trajectory divergence but recovery of macroscopic area differences relative to between-seed spread. Near breakout or tether failure, equally small interventions create a persistent mixture of different macroscopic outcomes. Define persistence over at least two successive doubled horizons, not a single divergent trajectory.

**Discriminator.** Compare random edits with edits to cells selected using *earlier* visit histories. If susceptibility predicts later breakout beyond current area, anisotropy and kappa drift on held-out rules, it offers an early-warning variable that is mechanistic rather than merely a spectral label. Report null prediction too: deterministic sensitivity need not imply useful forecasting.

### U3. Does escape wait for a rare pattern or for an old field?

Two explanations of late onset make different clocks relevant. A rare-pattern mechanism has an approximately constant chance per suitable frontier encounter. An ageing mechanism changes the chance per encounter as the tape organizes. A mixture of intrinsically easy and hard rules can mimic ageing even if each rule has a constant hazard in its own opportunity clock.

**Test.** Alongside step time, accumulate boundary contacts, new cells and completed long excursions. Fit onset models in each clock using the same at-risk runs, with separate highway and ribbon endpoints. Use within-rule seed replication to distinguish ageing from changing cohort composition. Keep already known onset cases out of the held-out evaluation.

**Prediction.** Under frontier nucleation, survival curves across seeds and ages collapse more closely in boundary-contact time than in step time, and an extra age term does not improve held-out likelihood. Under field ageing, age remains predictive after opportunity count and rule effects are included. If event counts are too small to distinguish these, report the likelihood range rather than extrapolating an astronomical median.

### U4. Tethering as a learned controller, not just a damaged cage

**Question.** Does a home contain a small reusable control circuit, or does return depend on phase distributed over many cells?

**Experiment.** Extend J1 with paired restoration. After a knockout that destroys return, restore only the edited cells, then separately restore the walker heading/position and the remaining field from the original checkpoint. Compare recovery after each restoration, allowing the same observation horizon. Run all four initial headings on untouched fields as a baseline for phase sensitivity.

**Prediction.** A localized controller predicts rescue when a small core and compatible entry state are restored, despite altered outer cells. Distributed phase memory predicts failure of local rescue but recovery after a larger state restoration. Search for a minimal sufficient core by nested regions first; unrestricted subset search risks finding a fragile, overfit rescue set.

This turns the existing knockout result into a constructive question: **what is sufficient to rebuild a home?** A transferable home motif would be more explanatory than another correlation between centrality and damage.

## V. Growth as a moving transport problem

### V1. What is the interface's natural clock?

The ant takes many steps without changing the territory. The temporal roughness exponent in step time may combine interface physics with a slowing supply of growth events.

**Design.** For ants and rotors, measure the same height correlations in step time $t$, added-area time $\Delta A$, and boundary-contact time. Compare surfaces at matched radius. Separate angular lattice modes and centre drift before measuring roughness; use an outer envelope and explicitly report what happens to bays and holes under that representation.

**Conditional prediction.** If $A\sim t^{2/3}$ and roughness $W\sim t^b$, reparameterizing the same data gives $W\sim A^{3b/2}$. This conversion is algebra, not evidence. The mechanistic test is whether spatial correlation functions and relaxation times collapse after matching the growth clock. Persistence of the ant–rotor difference across all clocks would strengthen the case for different interface dynamics; disappearance would identify event supply as the missing variable.

### V2. Measure a response spectrum instead of guessing a universality class

**Idea.** Ask how a boundary mode relaxes before assigning it an EW or KPZ label.

Use naturally occurring angular height modes as the observational pilot, then apply small, explicitly defined colour interventions in alternating boundary sectors. Compare untouched clones and rotate the perturbation relative to the lattice. For mode $m$, estimate whether its amplitude decays, oscillates or grows in excess of the baseline. Work at multiple radii and amplitudes to check linear response. The physical wavelength is proportional to $R/m$, so fixed mode number and fixed wavelength are different experiments.

**Competing predictions.** Local smoothing suggests a relaxation rate proportional to squared wave number; a nonlocal return process can produce another power or delayed response. A delay tied to the excursion distribution would connect this directly to T1. No numerical exponent is pre-assigned here: first define the response estimator and calibrate it on a synthetic interface with a known relaxation law, then register competing fits.

**Failure mode.** Growth dilutes relative bumps even without active restoring transport. Subtract that geometric effect before declaring damping. Colour perturbations also alter transport, so agreement with unperturbed fluctuation measurements is needed before attributing the response to curvature alone.

### V3. Predict the next octave with an integrated transport budget

H3 suggests a particularly cheap, strong test. Set $g(t)=P(t)/\sqrt{A(t)}$. The instantaneous identity gives
$$\frac{dA^{3/2}}{dt}=\frac32 c(t)\kappa(t)g(t).$$
For window-aggregated outputs, derive the discrete counterpart from the actual tally definitions; products of separately averaged quantities need not equal the average product.

**Experiment.** Estimate $c,\kappa,g$ in one octave and forecast the next octave's increment in $A^{3/2}$ without refitting. Compare a constant transport budget, a fitted drift budget and a rule-independent baseline. Partition forecast residuals into geometry change, kappa change and c change using subsequent measurements only for diagnosis, never for prediction.

**Prediction.** On ordinary blobs, a constant early budget cuts held-out median absolute prediction error by at least 30% relative to the rule-independent baseline. Fast-tail and breakout rules fail primarily through subsequent kappa drift. If geometry dominates the failures instead, the programme should shift from excursion kinetics toward shape dynamics.

**Why prioritize it.** This converts a same-window identity into a future prediction and immediately identifies where the approximation of stationary coefficients fails. Use existing probe data before adding instrumentation.

### V4. Controlled geometry: bulk transport versus narrow connections

**Question.** Is compact growth protected by efficient communication across the interior, or can a thin connection split a territory into effectively independent dynamical regions?

Prepare two comparable naturally generated patches connected by corridors of several widths, with deterministic matching of colours at the seams. Treat these as artificial initial conditions. Measure residence times in each lobe, crossings and frontier discovery per lobe. Include a single patch, a broad connection and a scrambled corridor as controls. Do not treat the artificial visited mask as evidence that those sites were dynamically explored.

**Prediction.** If bottleneck transport controls kappa, narrowing the corridor strongly increases residence-time asymmetry while leaving local edge efficiency approximately unchanged. If the walker rapidly rewrites the corridor and restores balanced access, this reveals an active repair process. Repeat at increasing lobe sizes to distinguish a fixed seam transient from a scale-dependent obstruction.

This geometry experiment could link the ordinary blob, the tether and the ribbon: three regimes of communication between regions rather than three unrelated visual classes.

## W. Suggested programme and stopping rules

The earlier L table is retained as historical planning. Its CPU-hour estimates are not benchmarks, and several listed tests need the amendments in S before execution. The revised priority is based on explanatory value per new instrument, not on how striking a conjecture sounds.

| Order | Work package | First deliverable | Advance only if |
|---|---|---|---|
| 1 | V3: next-octave transport forecast | Reproducible analysis of existing probe rows; per-rule held-out errors | Early coefficients predict future growth or isolate a clear failure term |
| 2 | T1: excursion tomography | Reference-checked event counters and a small paired pilot | Tail/depth/return-location measurements are stable under censoring and layer definitions |
| 3 | T2 + T3: memory location and age | Cloned-state interventions with sham controls | Encounter-aligned effects distinguish bulk arrangement, frontier state and cell age |
| 4 | U1: ribbon transfer | A local replay and one transplant matrix | A finite motif or frontier context reproducibly carries propagation |
| 5 | V1 + V2: interface clocks and response | Matched-radius correlations and calibrated mode response | A distinction survives geometry, clock and finite-window controls |
| 6 | U2 + U4: susceptibility and home rescue | Paired perturbation/restoration outcomes | A local mechanism predicts macroscopic outcome beyond visit frequency |
| 7 | U3: opportunity-clock survival | Auditable risk sets and cause-specific onset intervals | Enough independent onsets exist to compare mechanisms |
| Parallel intellectual track, no sweep yet | T4: exact balance laws | A candidate invariant, proof sketch or smallest counterexample | The observable is well-defined and survives oracle checks |

**Recommended first commitment:** do V3, then build a single excursion instrument serving T1, U3 and V2. Reserve one small exploratory branch for U1: the ribbon is the most conspicuous counterexample to the comfortable blob picture, and a propagating motif could produce a more decisive result than another long exponent fit. Defer thermodynamic analogies and group calculations until their observables are mathematically specified.

### Execution contract for these proposals

- Use a small instrument pilot before the full design. Benchmark measured steps/second and bytes/state; set concurrency from memory as well as the six logical cores. A dense $32768^2$ board already contains over a billion sites before auxiliary arrays.
- For new walkers, interventions and event tallies, write tiny reference versions and compare step-for-step. Calibrate estimators on known synthetic records and the rotor/random-walk controls; changing an estimator requires repeating its calibration.
- Freeze rule selection, discovery/validation splits and seeds before measurement. Patched starts, blank starts and altered fields are different populations. Report them separately. Multiple interventions on one snapshot are paired descendants, not independent seeds.
- Save commands, source commit plus any uncommitted patch needed to reproduce the run, parameters and checkpoint provenance. Do not overwrite the existing G1/H1/H3 outputs. New scripts and result files should carry the new item IDs, with long jobs logged and resumable under `data/`.
- Run Rust workloads in release mode through WSL. Run Python with `uv` and `UV_PROJECT_ENVIRONMENT=$HOME/.venvs/turmite UV_LINK_MODE=copy`; keep the committed environment reproducible. No new dependencies are required by this note itself.
- Append outcomes underneath the dated prediction: confirmed, contradicted, underpowered, censored or not run. Report between-seed uncertainty and held-out performance; a successful pilot does not license an asymptotic claim.

The most valuable possible outcome is a causal chain: **a measurable feature of tape memory changes excursion transport; that transport predicts boundary access; boundary access predicts subsequent growth.** A failed link is also useful, because it tells us exactly which level of description is missing.


### G1 result (predictions above not edited): not a boundary wave-guide; an abrupt switch to a steady 4-steps-per-cell builder
`examples/ribbon_trace.rs` (new; same plain loop as `escape_trace`, first-visit flag in the top bit; deterministic, not separately property-tested against `reference` — it is the loop `escape_trace` already used) `ribbon_trace RLRLLL 12000000000 13000000000 > experiments/archive/2026-10-g1-ribbon-breakout/results/g1_ribbon.csv` (blank board, 32768 grid, 1e8-step windows before 1.2e10, 1e6-step windows after; left the board at step 12,974,495,927 as in `experiments/archive/2026-10-c2-arrow-bias/results/escape_trace.txt`, which is a consistency check on the run). `uv run experiments/archive/2026-10-g1-ribbon-breakout/scripts/g1_stats.py > experiments/archive/2026-10-g1-ribbon-breakout/results/g1_stats.txt`. One rule, one trajectory.
- **Switch.** Up to 1.2676e10 the ant is in the blob regime: steps per new cell hundreds to thousands (median over 1e6 windows 1,176, a third of windows with no new cell at all, new-cell boxes up to 1,400 across). The window ending at t = 12,677,000,000 starts a steady phase that lasts all 299 remaining windows to the board edge (2.97e8 steps, 7.4e7 new cells): **steps per new cell 4.02 (range 3.95-5.69)**, about 249,000 new cells per 1e6 steps, ant x going from -2,190 to -16,384. The onset is a step change within a few windows, not an adiabatic crossover (onset was defined as the last window with $\ge 8$ steps/cell, so "all later windows below 8" is by construction; the tightness of 4.02 is the finding).
- **Prediction 1 (transverse width $\le 12$ for $> 95\%$): falsified as measured.** Width of the bounding box of cells first visited in a 1e6-step window: median 54 in x (0% of steady windows $\le 12$, 91% $\le 100$), while the y extent of the same new cells grows from 478 to 9,939 over the phase. This is not a literal ribbon thickness (a 1e6-step window of a structure swept in y covers several sweeps), so the "$\le 12$" level was probably the wrong observable, but the structure is neither 12 cells thick nor an isotropic blob ($\Delta_\perp > 100$ in 9%; extremely anisotropic otherwise). Not decided by these data: is it one thin ribbon or a set of parallel strokes.
- **Prediction 2 ($< 8$ steps per new cell): supported in the steady phase** (4.02), against $> 100$ in 69% of the earlier fine windows. The value being so close to an integer and constant suggests a regular local pattern, so the earlier "no exact period $\le 10^6$" result of `escape_trace` leaves a long-period (or aperiodic but regular) structure open.
- **Prediction 3 (quasi-period 24-256): not tested**; no period analysis was run beyond `escape_trace`'s earlier null.
- **Reading and link.** The breakout is a *phase switch* of the ant into a different growth mode (4 steps/cell, front advancing about 4.8e-5 cells/step in x while sweeping $\sim10^4$ in y), not a slow instability of the blob envelope; the hypothesis' "perimeter-following crawl along the envelope" is not supported (the ant is at x = -2,190, about 400 outside the blob box, at onset). 4 steps/cell sits inside the 2-6 range of the 289 frame builders (K3), which makes K3's question concrete: is this the frame-builder mode entered late by a blob rule? Unresolved: what triggers the switch at 1.2677e10 (one trajectory; no neighbouring seeds exist for a blank-board run), whether other late grid escapes (B5: RLLLLRRL, RLLLLRLRRL, RLLLRLRLLL) do the same.

### J4 result (predictions above not edited): no condensation transition; smooth deceleration
`probe 28 8192 < experiments/archive/2026-10-j4-tethered-gyration/results/j4_specs.txt > experiments/archive/2026-10-j4-tethered-gyration/results/j4_probe.csv` (RRRRRLLLLLL and RLLLLRRRRLR, blank board plus patched seeds 301, 302; none escaped), `uv run experiments/archive/2026-10-j4-tethered-gyration/scripts/j4_stats.py > experiments/archive/2026-10-j4-tethered-gyration/results/j4_stats.txt`. Octave resolution only; $R_g$ from the probe's `rg2`.
- Local exponent $d\log_2 R_g/d\log_2 t$ per octave: RRRRRLLLLLL falls steadily 0.26 (k = 14-15) -> 0.21 (20) -> 0.15 (24) -> 0.11 (28); the two patched runs agree (0.25 -> 0.13 -> 0.10). RLLLLRRRRLR is noisier (single octaves 0.04-0.55) with a similar trend 0.2-0.3 -> 0.1-0.15. $R_g$ at $2^{28}$ is 47-48 and 59-62, A about 14,000 and 21,000-23,000.
- **Prediction ($t^{0.33 \pm 0.03}$ up to a sharp $t_c \in [10^6, 5\times10^6]$ followed by a $>90\%$ drop of $dR_g/dt$ within one octave): falsified.** The exponent never reaches 0.33 on average over $k \ge 14$ (0.2-0.3), and no octave shows a drop to below a tenth of its predecessor's value; the deceleration is gradual over 14 octaves, which is the stated "breaks it" outcome (smooth deceleration). Caveat: a transition between $2^{20}$ and $2^{22}$ that is steep but spread over 2-3 octaves would also read as smooth here; the data cannot exclude a crossover of that width, only a single-octave break. These are the same two rules as the tethering experiments of E6, whose "late hot window" ($2^{22}..2^{24}$) is where the exponent has fallen to 0.15-0.2.

**T1 outcome (appended 2026-10-14): contradicted / null.** Registered predictions failed after size control; see `notes/excursion-tomography-2026-10-13.md` sections 5-7 (section 5's headline claims were retracted in section 6). Data `experiments/archive/2026-10-t1-excursion-tomography/results/t1_excursions.csv`, `experiments/archive/2026-10-t1-excursion-tomography/results/t1b_*.csv`; instruments `examples/excursions.rs`, `examples/sectors.rs` with oracle tests.
