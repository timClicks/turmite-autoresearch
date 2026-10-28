# Prospective transport forecast

Registered 2026-10-13 23:35 NZDT, before computing forecasts. Base commit
91f312f925b3234a3d3f0b1390598df81e170750; existing working changes preserved.
This tests V3 in research-frontier-2026-10-13-pm.md on existing data, not unseen simulations.

For each octave let A0=A-new_cells, dt=t/2, X=A^(3/2).
The exact discrete budget is Q=(X-X0)/dt. Endpoint c*kappa*g equals
new_cells*sqrt(A)/dt; its 3/2 multiple is a right-end approximation,
not the exact transformed increment. Use the exact budget for prediction.

Primary cohort: every complete nonescaped trajectory in experiments/archive/2026-10-b2-between-rule-variance/results/b2_probe.csv,
training k=20..22, forecasts k=23..26. No outcome growth-band filter.
Estimate constant Q by the arithmetic training mean; a competing drift model
fits log Q against log t on the same three windows. Predict each held-out
increment, and integrate all four from observed A at k=22. Baseline is the
median of training rule-mean budgets excluding the target rule (all its seeds).
Report median absolute relative increment error, trajectory medians then
equal-weight rule means, and final area error. Prediction: constant Q reduces
primary median increment error at least 30% against the baseline. Bootstrap
rules 2000 times, seed 20261013; report within-rule seed sd.

Calibration uses identical estimators: rotor k=20..22 ->23..26; random walk
k=17..19 ->20..23. Synthetic A=C*t^(2/3) must have constant exact Q and zero
forecast error; synthetic A=C*t must have Q proportional to sqrt(t), so the
drift forecast must be exact and constant Q must underpredict. No known
finite-window accuracy threshold is assigned to empirical controls.

Diagnosis only: log change in endpoint budget decomposes exactly into log
changes of c, kappa, g=P/sqrt(A). Compare their absolute magnitudes, but do
not interpret cancellation or this identity as causal attribution. Record
exclusions and input hashes. No new walker or estimator of growth exponents.

## Results (appended after measurement)

Recipe in WSL from /mnt/f/Code/turmite:
`export UV_PROJECT_ENVIRONMENT=$HOME/.venvs/turmite UV_LINK_MODE=copy && uv run experiments/archive/2026-10-transport-forecast/scripts/transport_forecast.py > experiments/archive/2026-10-transport-forecast/results/transport_forecast.log`.
Full trajectory records, input SHA256 hashes, exclusions, commit and seed:
[transport_forecast.json](../data/transport_forecast.json). Producing script:
[transport_forecast.py](../data/transport_forecast.py).

Primary: 1,185 complete trajectories, 99 rules, approximately 12 patched
seeds/rule; 15 excluded by the registered completeness criteria. These are
survivor forecasts and do not cover censored escapes. Endpoint budget exceeds
the exact discrete budget by a typical factor 1.112.

| Forecast | Typical increment relative error | Final area relative error |
|---|---:|---:|
| Constant trajectory budget | 0.08486 | 0.05378 |
| Early drift fit | 0.23288 | 0.17032 |
| Other-rule baseline | 0.26922 | 0.17575 |

Entries are medians across equal-weight rule means of trajectory errors;
trajectory increment error is the median over four held-out octaves.
Constant-budget reduction is 68.48%, rule-bootstrap 95% interval
61.33–80.58% (2,000 resamples, seed 20261013). The registered 30% prediction
passes on this unfiltered complete cohort. This is a future-window test on
existing simulations, not a proof of asymptotic scaling.

The tail matters: RMS within-rule seed sd of relative errors is 188.68 for
constant, 918.80 for drift, and 8.67 for baseline. RLLRRRLLRLRR@108 has
constant error 6,505.83; @104 has 20.74 and drift error 31,779.13. Extreme
ratios occur when a future increment is tiny relative to the forecast. The
robust headline does not imply uniformly reliable predictions or small mean
squared loss. These runs remain included.

Controls: 64 rotor seeds give constant error 0.06108 vs baseline 0.05670
(reduction -7.71%, interval -23.85–11.40%); 16 random-walk seeds give
0.60260 vs 0.58766 (-2.54%, interval -7.65–4.59%). Random-walk drift improves
to 0.47876 but remains poor. Rotor provides a finite-window error floor;
random walk rejects a universal stationary transformed budget. Synthetic
constant-budget and sqrt(time)-budget instrument checks passed.

Diagnosis: typical absolute log changes are 0.00475 for c, 0.09316 for kappa,
0.04085 for geometry. Kappa changes are larger typically; this does not
establish which factor drives extreme failures or causal direction.

Exploratory follow-up, specified after the primary result: replace a
trajectory's training budget with the median training budget of its other
seeds of the same rule. Typical increment error is 0.07433, slightly better
than using the trajectory itself. This suggests persistent rule-level
transport plus seed noise and motivates an independent cohort test rather
than noisy three-point drift fits. This is not a pre-registered test. The
missing mechanism remains: what spatial memory makes transport persistent?

Verification: two consecutive analysis runs produced byte-identical JSON
(`cmp` against /tmp/turmite-transport-forecast.json). Full `cargo test --release`
passed; log [transport_forecast_tests.log](../data/transport_forecast_tests.log).
Existing unused-mut warning in examples/lastvisits.rs was retained. No Rust
changes or dependencies were introduced, and nothing was committed.

Paper integration: added the discrete estimator, prospective design, results,
controls, extreme-error caveat and exploratory cross-seed check to the growth
decomposition section of research-outputs/working-papers/cube-root-growth/main.typ. Numbers load directly from the JSON.
Built with `typst compile --root . research-outputs/working-papers/cube-root-growth/main.typ research-outputs/working-papers/cube-root-growth/main.pdf`; visually
checked the forecast section on pages 9–10. The missing pre-existing memory
figure was regenerated with `uv run research-outputs/working-papers/cube-root-growth/memory_figures.py` to complete the
build. Updated research-outputs/working-papers/cube-root-growth/README.md with the forecast recipe and build root.
