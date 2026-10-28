# Excursion tomography: typical loops or rare journeys? (T1)

Pre-registered 2026-10-13 23:45 NZDT, before any code execution or simulation.
Base commit: `91f312f925b3234a3d3f0b1390598df81e170750` with uncommitted research work preserved.
This implements Work Package 2 (T1) from `notes/research-frontier-2026-10-13-pm.md` (Section T1 and Section W).

## 1. Context and Physical Question

In the growth identity $dA/dt = c \cdot \kappa \cdot (P/A)$:
- $c$ is explained by rule letters ($R^2 = 0.78$).
- $\kappa$ (boundary step density relative to fair share $P/A$) is rule-specific ($\text{ICC} = 0.58$), but unexplained: letters ($R^2 \le 0.04$), local edge dwell ($v_e \approx 1.5$ across all rules, Arm A), and crust depth ($d=2..4$, Arm C sign test $p=0.58$) all failed.

By renewal / ergodic decomposition on a finite growing territory:
$$
\frac{B}{S} = \frac{\langle \tau_{\text{edge}} \rangle}{\langle \tau_{\text{edge}} \rangle + \langle L_{\text{int}} \rangle}
$$
Because boundary contact dwell $\langle \tau_{\text{edge}} \rangle \approx 1.5$ is pinned across rules, the boundary fraction $B/S$ — and therefore $\kappa = (B/S) / (P/A)$ — is mathematically governed by the interior excursion duration distribution $P(L_{\text{int}})$, with mean duration:
$$
\langle L_{\text{int}} \rangle \approx \frac{1.5}{\kappa \cdot (P/A)} \sim \frac{R}{\kappa}
$$
Low-$\kappa$ rules have $\sim 10\times$ larger mean excursion length $\langle L_{\text{int}} \rangle$ than high-$\kappa$ rules.

**The core question:** Where does this $10\times$ difference reside in $P(L)$?
- **Hypothesis A (Shallow loops):** The entire distribution shifts: ordinary excursions take longer (median $L_{\text{med}} \propto 1/\kappa$).
- **Hypothesis B (Trap / rare journeys):** Typical excursions are identical shallow loops ($L_{\text{med}} \sim \mathcal{O}(1)$ for all rules), but low-$\kappa$ rules experience a heavy tail of rare deep bulk plunges that consume the vast majority of the interior time budget.
- **Hypothesis C (Transport / chord journeys):** Returns in high-$\kappa$ rules land adjacent to the departure point ($D/R \ll 1$, localized boundary ping-pong), whereas low-$\kappa$ rules traverse chords across the full territory diameter ($D/R \sim 1$).

## 2. Experimental Design

### Cohorts and Walkers
1. **Target cohort:** The 44 rules in `experiments/archive/2026-10-arm-kappa-depletion-arms/results/armc_specs.txt` comprising the 26 matched pairs from `experiments/archive/2026-10-arm-kappa-depletion-arms/results/armc_pairs.txt`.
   Each pair matches rule length $n$, number of R turns $q$, and growth factor $c$ (within 0.02), while rule-mean $\kappa$ differs by $\ge 0.50$ (up to $10.6$).
2. **Replications:**
   - Patched starts: seeds 0..7 (`RULE@0` .. `RULE@7`), $N = 44 \times 8 = 352$ runs.
   - Blank starts: 44 rules from blank board, evaluated as an independent replication cohort.
3. **Controls:**
   - Rotor walker: `rotor:SEED`, seeds 301..304.
   - Random walk: `rw:SEED`, seeds 301..304.
4. **Grid and Duration:**
   - Grid size: $8192 \times 8192$.
   - Max step count: $2^{26}$ steps (67,108,864 steps).
   - Windows: Octave checkpoints $k = 22..25$ ($t \in [2^{22}, 2^{26}]$).

### Observables Measured per Window $(t_{\text{start}}, t_{\text{end}}]$
- Exact conservation check: $\text{boundary\_steps} + \sum L_{\text{comp}} + L_{\text{unres}} = \Delta t = t_{\text{end}} - t_{\text{start}}$.
- $N_{\text{exc}}$: number of completed interior excursions.
- $L_{\text{med}}, L_{\text{mean}}, L_{p90}, L_{p99}, L_{\max}$: percentiles of completed excursion duration.
- $f_{\text{top1}}$: fraction of interior steps accounted for by the top 1% longest completed excursions:
  $$f_{\text{top1}} = \frac{\sum_{i \in \text{top 1\%}} L_i}{S_{\text{int}}}$$
- $f_{\text{top5}}$: fraction accounted for by the top 5%.
- $f_{\text{unres}}$: fraction of interior time in excursions crossing window boundaries.
- $D_{\text{med}} / R, D_{\text{mean}} / R$: Euclidean departure-to-return displacement divided by $R = \sqrt{A/\pi}$.
- $\Delta r_{\max} / R$: maximum inward radial depth $(r_{\text{start}} - r_{\min}) / R$.
- $\bar{\tau}_{\text{edge}}$: mean edge contact dwell time.

## 3. Pre-registered Predictions (Fixed Before Measuring)

1. **Prediction 1 (Rare journeys over shallow loops):**
   In $\ge 18$ of the 26 matched pairs ($\ge 69\%$), the low-$\kappa$ member has a larger top-1% excursion time fraction ($f_{\text{top1}}$) than the high-$\kappa$ member, whereas the paired median durations $L_{\text{med}}$ differ by less than a factor of $2.0$.
   (One-sided sign test $p < 0.05$).
2. **Prediction 2 (Edge dwell invariance):**
   Mean boundary dwell $\bar{\tau}_{\text{edge}}$ is invariant across rules ($1.5 \pm 0.3$), confirming dwell does not drive $\kappa$.
3. **Prediction 3 (Chord transport):**
   Low-$\kappa$ excursions exhibit significantly larger normalized return displacement $D_{\text{med}} / R$ than high-$\kappa$ excursions: Spearman $\rho(D_{\text{med}} / R, \kappa) \le -0.60$, confirming cross-territory chord journeys.
4. **Prediction 4 (Held-out prediction):**
   Features extracted at early windows ($k = 22..23$) predict late-window ($k = 25$) $\kappa$ across held-out rules with $R^2 \ge 0.30$ against a constant baseline.

## 4. Falsification and Decision Rules
- **If $L_{\text{med}}$ differs by $> 3\times$ while $f_{\text{top1}}$ fails to separate pairs:** The shallow-loop mechanism is supported; rare journeys are falsified.
- **If neither $L_{\text{med}}$ nor $f_{\text{top1}}$ separates pairs (sign test $p > 0.30$):** The excursion duration mechanism is falsified, implying that $\kappa$ is driven by boundary morphology / fractal perimeter trapping.

---

## 5. Experimental Results (Added 2026-10-14, Predictions Preserved Unchanged)

### Execution and Reproducibility
- **Command:** `cargo run --release --example excursions -- 26 8192 < experiments/archive/2026-10-t1-excursion-tomography/results/t1_specs.txt > experiments/archive/2026-10-t1-excursion-tomography/results/t1_excursions.csv 2> experiments/archive/2026-10-t1-excursion-tomography/results/t1_excursions.log`
- **Analysis:** `uv run experiments/archive/2026-10-t1-excursion-tomography/scripts/t1_excursions.py > experiments/archive/2026-10-t1-excursion-tomography/results/t1_excursions.txt` and `uv run experiments/archive/2026-10-t1-excursion-tomography/scripts/t1_pair_disp.py`
- **Output artifacts:** `experiments/archive/2026-10-t1-excursion-tomography/results/t1_excursions.csv` (1,602 window records), `experiments/archive/2026-10-t1-excursion-tomography/results/t1_excursions.txt`, `experiments/archive/2026-10-t1-excursion-tomography/results/t1_excursions.json`
- **Verification checks:**
  - Exact discrete step budget $\text{boundary\_steps} + \text{interior\_steps} = 2^k$ satisfied for **100% of rows** (`exact_budget == true`).
  - Rotor controls: $\kappa = 1.999 \pm 0.002$, $c = 0.498 \pm 0.001$ (matches exact analytical baseline $\kappa = 2.0$, $c = 0.50$).
  - Random walk controls: $\kappa = 1.373 \pm 0.015$, $c = 0.440 \pm 0.008$.
  - Property tests in `tests/excursions.rs` passed vs brute-force oracle step-for-step across all walkers.

### Outcomes Against Pre-registered Predictions

1. **Prediction 1 (Rare journeys over shallow loops): FALSIFIED in the time-share hypothesis, but typical loop invariance confirmed.**
   - The hypothesis that low-$\kappa$ rules have an *excess* share in the top 1% tail failed: low-$\kappa$ members had higher $f_{\text{top1}}$ in only **7 of 26 pairs** ($p = 0.9953$).
   - The reason is that heavy-tailed excursions dominate the interior budget for **all** rules: $f_{\text{top1}}$ is uniformly high across rules ($85\% - 99\%$).
   - However, the second clause of Prediction 1 held: median excursion duration $L_{\text{med}}$ is strictly $\mathcal{O}(1)$ across all rules (median ratio $= 1.00$; 19 of 26 pairs had ratio $< 2.0$). Typical excursions are immediate 1-step returns everywhere.

2. **Prediction 2 (Edge dwell invariance): CONFIRMED.**
   - Mean edge contact dwell $\bar{\tau}_{\text{edge}} = 2.538 \pm 0.302$ (range 2.04–3.00). Dwell time has weak correlation with $\kappa$ ($\rho = +0.271, p = 0.075$), confirming that local boundary contact duration does not drive $\kappa$.

3. **Prediction 3 (Chord transport and excursion geometry): DECISIVELY CONFIRMED.**
   - In **26 out of 26 matched pairs (100%)**, the low-$\kappa$ member has a larger normalized departure-to-return displacement $D_{\text{med}} / R$ than the high-$\kappa$ member!
   - One-sided sign test: $26/26$ wins, **$p = 1.49 \times 10^{-8}$**!
   - Across all 44 rules at $k = 25$:
     $$\rho(D_{\text{med}} / R, \kappa) = \mathbf{-0.877} \quad (p = 6.01 \times 10^{-15})$$
   - Radial depth penetration also separates $\kappa$ decisively:
     $$\rho(\Delta r_{\text{mean}} / R, \kappa) = \mathbf{-0.892} \quad (p = 4.23 \times 10^{-16})$$
     $$\rho(\Delta r_{\text{med}} / R, \kappa) = \mathbf{-0.857} \quad (p = 1.18 \times 10^{-13})$$

4. **Prediction 4 (Predictive power for $\kappa$): CONFIRMED for log-scale boundary occupancy.**
   - Pearson correlation between $D_{\text{med}} / R$ and $\ln \kappa$: $r = -0.811$ ($R^2 = 0.658, p = 2.44 \times 10^{-11}$).
   - In leave-one-out cross-validation across all 44 rules, the single geometric observable $D_{\text{med}} / R$ predicts $\ln \kappa$ with:
     $$\text{LOOCV } R^2 = \mathbf{0.589}$$
     decisively exceeding the pre-registered benchmark of $R^2 \ge 0.30$!

### Physical Mechanism Identified: Peripheral Trap vs. Chord Traverse

The 26 matched rule pairs share identical $n$, identical $q = \#R/n$, and identical edge growth probability $c \pm 0.02$, yet their boundary occupancy $\kappa$ differs by up to two orders of magnitude (0.24 to 183.9).
Excursion tomography settles where this difference lives:

- **High-$\kappa$ rules are peripheral pinball machines:** When the walker steps into the interior, it is immediately turned around by dense, divergence-free local loop structures near the boundary. Its penetration depth $\Delta r / R$ is tiny ($\approx 0.002$), and it re-emerges immediately adjacent to its departure cell ($D / R \approx 0.002$). Because it is trapped in a shallow boundary skin, it executes a vast number of return contacts per unit time ($N_{\text{completed}} \sim 85,000$, $\rho = +0.832$), driving boundary occupancy $\kappa$ high.
- **Low-$\kappa$ rules are deep bulk transports:** The interior field does not reflect the walker. Excursions penetrate deeply into the core ($\Delta r / R$ up to $0.007$, $3\times$ deeper) and traverse long chords across the territory diameter ($D/R \approx 0.006 - 0.007$). The walker spends its interior time crossing the bulk rather than orbiting the perimeter, sharply depressing the return frequency at any given boundary sector ($N_{\text{completed}} \sim 17,000$).
- **Conclusion:** $\kappa$ is not governed by temporal duration statistics ($L_{\text{med}}$ or tail shares, which are identical across rules), but by **spatial excursion geometry** ($D/R$ and $\Delta r/R$).

---

## 6. Audit and correction (2026-10-14; §3 predictions and §5 text left as written, but §5 conclusions are retracted where stated)

Audit script: `uv run experiments/archive/2026-10-t1-excursion-tomography/scripts/t1_audit.py > experiments/archive/2026-10-t1-excursion-tomography/results/t1_audit.txt` (reads `experiments/archive/2026-10-t1-excursion-tomography/results/t1_excursions.csv`; the instrument itself re-passed `cargo test --release --test excursions`, 4/4). The counters are sound; the interpretation in §5 is not.

1. **Prediction 3 and the "chord transport" mechanism: RETRACTED (normalisation artefact).** The median departure-to-return displacement is 1.41 cells (sqrt 2, a diagonal return) for every rule (quartiles 1.41-1.42 at k=25), and median depth is about 1 cell (0.86-1.32). So `disp_med/R` is just sqrt(2)/R, an inverse territory size. Territory size at fixed t is set by kappa through the growth identity (Spearman(R, kappa) = +0.88, r(ln A, ln kappa) = +0.92), so rho(D/R, kappa) = -0.88 is the same identity read backwards. In raw cells, rho(D_cells, kappa) = -0.14 (p = 0.37). The "3x deeper, chords across the diameter" description is false: D/R is 0.002-0.008 because R is 200-1100 cells, not because anything crosses the territory. The "26/26 pairs" sign test is the same artefact (low-kappa member of a matched pair has the smaller R). The LOOCV R^2 = 0.589 is therefore a size predictor, not a mechanism.
2. **Prediction 4 as registered: FAILED, not confirmed.** The registered test (k=22 features predicting k=25 kappa on held-out rules, R^2 >= 0.30) gave R^2 = -0.047 in `t1_excursions.txt`. §5 replaced it with a same-window leave-one-out fit on D/R, which is a different, weaker and artefact-contaminated test.
3. **Prediction 2: FAILED as registered.** It said 1.5 +- 0.3; observed 2.54 +- 0.30 (range 2.04-3.00), outside the band for most rules. Weak correlation with kappa (rho = +0.27) stands, but "confirmed" is wrong. (The 1.5 in Arm A was v_e from the layer tally, a different definition of dwell; this probe counts consecutive boundary steps. They should not have been equated.)
4. **Prediction 1** stays as §5 reports it: the top-1% share clause fails (7/26 pairs; blank-board replication 6/26), the median-ratio clause holds trivially because the median completed excursion is a 1-step return for everyone. That a median of 1 carries no information is itself the finding; the 19/26 "ratio < 2" is not a supportive test.
5. What the data do support, as description only: interior time is dominated by the rare long excursions in every rule (top-1% share 0.85-0.99; mean 116-1157 steps against median 1); unresolved (window-crossing) excursion time is 5-20% of interior time and correlates with kappa (rho = +0.62), so completed-excursion statistics are biased for exactly the high-kappa rules, and this was not corrected; mean depth in cells ranges 1-6. Whether the tail's *shape* (not just its share) differs between pair members has not been tested, and depth-in-cells vs kappa (rho = -0.55) is confounded with the same size effect. The size-controlled analysis was not done.
6. Not done: spatial return-location sectors (hypothesis C proper, needs return position relative to departure in boundary arc length, not Euclidean distance over R), tail-exponent fits, treatment of unresolved excursions, pair-level resampling, early-to-late held-out features beyond the single failed fit.

**Net verdict on T1:** pre-registered predictions 2, 3-as-interpreted and 4 failed or were uninformative; prediction 1's rare-journey bet failed. Hypotheses A (shallow loops shift whole distribution), B and C are all unsupported by this probe; kappa remains unexplained and the typical excursion is rule-independent. The earlier "peripheral pinball vs deep bulk transport" mechanism should not be cited (it should not have reached the paper; grep `paper/` before any further use).

---

## 7. T1b: size-free excursion geometry (pre-registered 2026-10-14 00:10 NZST, before any T1b code was written or run; base commit `dd0e234` plus uncommitted work)

Motivation: §6. The first instrument's D/R and depth/R were size-contaminated and its medians are all the 1-step return. T1b targets the part of P(L) that carries the time budget and uses size-free or cell-unit observables.

### Instrument (`examples/sectors.rs`, test `tests/sectors.rs`)
Same state machine as `examples/excursions.rs` (boundary = visited cell with an unvisited 4-neighbour; excursion = run of interior steps; length L = number of steps taken from interior cells). New: (i) for each completed excursion the **angular displacement** Δθ in [0, π] between departure and return cells about the visited-set centroid at the return time, the Euclidean displacement and inward depth **in cells**; (ii) bounded log2-bin tables (bin = floor(log2 L)) of count, sum L, sum Δθ, sum D, sum depth, max depth per window; (iii) exact window accounting: interior_steps = sum over completed excursions of (the part of L done inside this window) + the open part at the window end (`conserved` column, asserted). Excursions are attributed to the window where they complete; the open part is reported, never dropped.
Cohort, grid, steps, windows: identical to §2 (`experiments/archive/2026-10-t1-excursion-tomography/results/t1_specs.txt`, 404 specs, 8192 grid, 2^26 steps, k = 22..25). Pairs and the rule-mean-kappa ordering: `experiments/archive/2026-10-arm-kappa-depletion-arms/results/armc_pairs.txt` as in §3; rule-level quantities are means over the 8 patched seeds; the unit of inference is the pair, and I will also report a rule-level bootstrap (resampling rules, pairs recomputed) because rules appear in several pairs.

### Quantities (defined now)
- Theta_w(L0) = (sum of L·Δθ) / (sum of L) over completed excursions with L >= L0, L0 = 64 (primary), 16 and 256 as sensitivity. Time-weighted, so it describes where the time budget goes. Null reference: independent uniform return angle gives Theta_w = pi/2.
- alpha_hat = Hill estimate of the tail exponent of P(L > l) ~ l^-alpha from binned counts above L0 = 64 (maximum-likelihood for the discretised power law over the log2 bins, stated in the script), with the cutoff l_c = largest bin with >= 10 excursions.
- Lbar = completed-excursion mean length; identity used: kappa ~ tau_edge · A / (P · Lbar) with tau_edge ~ 2.0-3.0 (this is bookkeeping; §1 of the original note).

### Predictions (fixed now)
1. **Sector transport (hypothesis C, proper).** Low-kappa member has larger Theta_w(64) in >= 18 of 26 pairs (one-sided sign p < 0.05) at k = 25 AND at k = 22 (both). Failure at either window, or Theta_w within 0.1 rad of pi/2 for >= 80% of rules (long excursions decorrelate completely), means return-sector structure does not separate rules.
2. **Tail shape vs cutoff.** Across the 44 rules at k = 25, between-rule variance of ln(Lbar) is split between the tail exponent alpha_hat and the cutoff. Prediction: alpha_hat alone explains >= 50% (r^2) of var ln(Lbar); the cutoff (ln of the 99.9th-percentile L) alone explains < 25%. If the cutoff explains more than alpha_hat, the rules differ in the range of excursion scales, not in the shape of the tail.
3. **Held-out, size-controlled.** Leave-one-rule-out regression of ln kappa(k=25) on features measured at k=22 only: baseline = ln A(k=22); model = baseline + {Theta_w(64), alpha_hat, ln mean depth in cells}. Prediction: the model beats the baseline by >= 0.10 in held-out R^2. Note the baseline itself is expected to be strong (§6: area tracks kappa); the claim is only about what the excursion features add. Report both R^2 values.
4. **Controls.** Rotor and random walk (4 seeds each): the conservation flag is true in every window; rotor Theta_w(64) and alpha_hat are reported as the reference, with no numerical prediction beyond conservation and kappa = 2.00 +- 0.01 (rotor), 1.37 +- 0.05 (random walk) reproducing the first instrument.

### Decision rules
- 1 holds: kappa depends on where long excursions return; next step is a transplant test (T2) on return sectors.
- 1 fails, 2 holds with alpha_hat: kappa tracks the tail exponent; next step is to ask what in the rule sets alpha_hat.
- 1 and 2 fail, 3 fails: the T1 family of excursion statistics does not explain the rule dependence of kappa beyond size; report as null and drop excursion tomography as the route.
- Not decided here and will not be claimed: any causal statement (these are observational; T2/T3 interventions are required).

### T1b results (2026-10-14; predictions above unchanged)
Commands: `cargo build --release --example sectors`; `./target/release/examples/sectors 26 8192 experiments/archive/2026-10-t1-excursion-tomography/results/t1b < experiments/archive/2026-10-t1-excursion-tomography/results/t1_specs.txt` (commit in `experiments/archive/2026-10-t1-excursion-tomography/results/t1b.commit`, plus the uncommitted tree; log `experiments/archive/2026-10-t1-excursion-tomography/results/t1b.log`) -> `experiments/archive/2026-10-t1-excursion-tomography/results/t1b_windows.csv`, `experiments/archive/2026-10-t1-excursion-tomography/results/t1b_bins.csv`; `uv run experiments/archive/2026-10-t1-excursion-tomography/scripts/t1b_analysis.py > experiments/archive/2026-10-t1-excursion-tomography/results/t1b_analysis.txt`. Oracle: `cargo test --release --test sectors` (5/5: angle values, RL/rotor/random walk and a proptest over 3-6 letter rules against a HashSet brute force; checks counts, time sums, angle/displacement/depth sums and the window conservation identity). Deviation: bins store sum(Δθ), not sum(L·Δθ), so Theta_w is the bin-time-weighted mean of bin mean angles (analysis docstring). Same 404 specs as T1; 1602 window rows, conservation flag true in all; controls reproduce the first instrument (rotor kappa 1.999, random walk 1.373). Unit of analysis: rule means over 8 patched seeds; pairs with an undefined Theta_w (no bin >= 64) drop out (24-25 of 26 usable). Between-seed sd was not reported; rule-level bootstrap CIs are given instead.

1. **Prediction 1 (sector transport): FAILED as registered, and the part that passed is a size artefact.** Low-kappa member has larger Theta_w(64) in 18/24 pairs at k=25 (p=0.011) but only 17/25 at k=22 (p=0.054); both were required. Rule-bootstrap win fraction 0.65-0.68 with 95% interval [0.28-0.33, 0.94-0.96], i.e. not distinguishable from 0.5 at the rule level. Sensitivity to L0=16/256 is the same. Theta_w medians 0.83-0.84 rad (quartiles 0.76-0.91), far from pi/2 (no complete decorrelation; 0-2% of rules within 0.1 of pi/2), and 60x the rotor/random-walk values (0.011-0.013 rad). Exploratory size check (not registered): an angle is displacement / R, and low-kappa members are smaller, so I converted. In cells the sign reverses: time-weighted return displacement is larger for the *high*-kappa member in 18/24 pairs at k=25 (low>high 6/24) and 19/25 at k=22; partial correlation of Theta_w with ln kappa given ln A is -0.08 (k=25) and +0.16 (k=22), both p > 0.3. Return location carries nothing beyond size. Hypothesis C is not supported.
2. **Prediction 2 (tail exponent vs cutoff): FAILED.** alpha_hat explains r^2 = 0.23 of var ln Lbar (not >= 0.50); the cutoff ln L_99.9 explains 0.11 (the "< 0.25" half held); together 0.50. alpha_hat is only defined for 32 of 44 rules (the others have < 10 excursions in bin 64-127), median 0.49 (range 0.16-0.63): a very heavy tail whose time share is set by the cutoff, so a power-law fit between 64 and the cutoff is weak. Given ln A, alpha_hat has partial r with ln kappa of -0.04 (k=25).
3. **Prediction 3 (held-out): FAILED.** On the 31 rules with all features at k=22, held-out R^2 for ln kappa(k=25): ln A(22) alone 0.59; adding the excursion features 0.54 (gain -0.05, needed +0.10). Excursion features alone 0.37, but those include the size-contaminated angle. (R^2 here is measured against the constant fit on all data, which is mildly generous to every model.)
4. **Controls: as registered.**

### Exploratory residue (added after seeing the above; one of about 14 partial correlations looked at, so treat as a hypothesis, not a result)
- The only quantity with a size-independent association with kappa is the extreme tail: partial r(ln L_99.9, ln kappa | ln A) = -0.40 (k=22, p=0.008) and -0.41 (k=25, p=0.005), n=44. Bonferroni over ~14 tests puts the threshold at 0.004, so neither passes it. Its direction is the accounting one (longer extreme excursions take more of the time budget) and Lbar, which contains the same information with more noise, does not show it (partial -0.08 at k=25).
- Within a rule, L_99.9 grows with time at exponent median 0.38 (IQR -0.41..0.46, 22->25) against 0.34 for R, i.e. consistent with extreme excursion length proportional to territory radius, as expected if the longest excursions span the territory scale. Across rules at fixed k it falls with R (slope -2.6 to -4.3), again because kappa and area are tied at fixed t. The between-rule effect and the scaling-with-R need a per-rule estimate of L_99.9/R, which has not been done.

### Verdict on excursion tomography (T1 and T1b together)
None of the registered mechanisms (shallow loops, rare-journey time share, return-sector transport) explains the rule dependence of kappa once territory size is controlled; every effect that looked strong (D/R, depth/R, return angle) was inverse territory size, which kappa itself sets at fixed t. The typical excursion is a 1-step return for every rule; the time budget sits in a tail with alpha ~0.5 whose extreme length scales with R. What remains is a weak, uncorrected hint that the extreme-excursion cutoff relative to R is the rule-specific quantity. Excursion statistics measured at a fixed step count cannot separate cause from the size confound; the route forward is intervention (T2/T3), or comparison at matched territory size, not more observation at matched t. Not done: matched-area comparison across pair members, per-rule L_99.9/R estimate, Sum(L·Δθ) tallies, seeds' between-run sd.

### Cutoff/radius continuation (2026-10-14 NZDT)

The per-rule cutoff/radius estimate and seed dispersion are now reported in
[the experiment README](../experiments/archive/2026-10-t1-excursion-tomography/README.md)
with command `uv run experiments/archive/2026-10-t1-excursion-tomography/scripts/t1b_cutoff.py`
and hashed provenance in `results/t1b_cutoff.json`. Across 44 rules, the
descriptive Spearman association is -0.835 at k=22 and -0.918 at k=25;
median between-seed sample sd of ln ratio is 0.129 and 0.128. This does not
resolve the size confound. Ten escaped windows were excluded. Rotor kappa
misses its original final-window tolerance and random-walk final-window
controls are unavailable. Exact quantiles, censoring correction, matched-area
comparison and interventions remain outstanding; duration/radius is not
spatial displacement.
