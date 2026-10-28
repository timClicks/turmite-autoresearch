# Lab notebook: kappa of the calibration walkers against their own uniform reference

Append-only. Newest entry last. Corrections are new entries. Tags: intent, assumption,
observation, interpretation, surprise, decision, dead-end, question, deviation.

### 2026-10-19 (+13) · 6de71f2 · intent
Recompute rotor and memoryless-walker kappa/kappa_unif with each walker's own measured (a, beta); decide whether the ant location (median 0.81) is ant-specific. README registered with predictions before any new run. Informs the open item in the 2026-10-16 01:00 deviation entry.

### 2026-10-19 (+13) · 6de71f2 · observation
`scripts/prior_ab.py` on existing CSVs (a1d_probe.csv, calib_rotor.csv; k=12..22): pw a 0.89-0.93, beta 0.88-0.93, kappa_unif 1.02-1.03, ratio 1.21-1.32; rotor a 0.724, beta 0.564, kappa_unif 1.104, ratio 1.68.

### 2026-10-19 (+13) · 6de71f2 · surprise
The task premise "memoryless reference near 1.16" does not hold: the 1.16 value assumes beta = 1/2, but porous memoryless territories have beta ~0.9, giving kappa_unif ~1.02-1.03. Registered in README before the run. The ratios therefore stay ~1.2-1.3 rather than dropping.

### 2026-10-19 (+13) · 34fbf45 · observation
Ran `scripts/run.sh` (8 seeds 2026101901..08 each of rw, pw:0.25/0.5/0.75 at `probe 23 16384`, rotor at `probe 27 8192`); no escaped windows. Raw output in results/probe_{mem,rotor}.csv.

### 2026-10-19 (+13) · 34fbf45 · deviation
First `analyse.py` gave kappa 0.64-0.93 (ratios 0.6-0.9), half the existing values (rotor 2.0, rw 1.37). Cause: I took t_end = 2^(k+1) (the baseline experiment's window-start labelling) but the probe CSV's t column is already the window end. Fixed to use the CSV t; no data touched, the buggy analysis.txt was overwritten (never committed). Caught only because the output disagreed with the prior_ab.py numbers; the rerun matches them.

### 2026-10-19 (+13) · 34fbf45 · observation
Corrected analysis: rw 1.28, pw 1.24/1.32/1.26, rotor 1.69 (k12-22) / 1.80 (k20-26), all with seed sd <= 0.06, vs kappa_unif 1.02-1.03 (memoryless) and 1.10 (rotor). See README table. All registered predictions 1-3 held; walker ratios all exceed the ant IQR.

### 2026-10-19 (+13) · 34fbf45 · interpretation
Ant median 0.81 is below every non-uniform walker tested, and the mean-field walker sits at 1.0, so the ratio is not walker-universal. Memoryless walkers (1.24-1.32) are inside the ant 5-95% range at its top, so the control is weak there; the rotor (1.7-1.8) is clearly outside. No mechanism claimed. Confounds not excluded: window (memoryless at k<=22, a not asymptotic), single-run ant noise, 8-seed walker means vs ant distribution.

### 2026-10-19 (+13) · 34fbf45 · decision
Stop at accounting. Next step proposed: noisy rotor (eps scan) to locate where ratio crosses 0.81. Release tests pass (`cargo test --release`, no Rust changed).

### 2026-10-19 (+13) · 0169fee · interpretation
Addendum to the interpretation above (second reader, no new data). (1) The "(mean - ant q75)/seed-sd" figures in `analysis.txt` (5-25) compare a walker's 8-seed mean to a quantile of single-run, rule-dependent ant ratios (ln-kappa reliability ~0.6); they measure walker seed noise only and are not significance tests. (2) The walker ratios are > 1 for every non-uniform walker and the ant median is < 1, but the ant 5-95% range spans 0.44-1.33, so rule-level structure, not the median, is the better lever. (3) An earlier version of this session's summary quoted the halved-kappa `analysis.txt` (ratios 0.62-0.90); the deviation entry above gives the cause (window-end `t` taken as window start) and those numbers must not be quoted. (4) Paper edit not made; proposal in `notes/paper-and-supplementary-plan-2026-10-19.md`.

### 2026-10-19 (+13) · f414649 · intent
Step 2 of the README next steps: noisy-rotor scan (9 EPS x 8 seeds, `probe 27 8192`). Predictions (i)-(v) registered in the README at 21:35 NZST before the run. Fresh target dir, binary sha256 logged.

### 2026-10-19 (+13) · f414649 · deviation
First analysis dropped every run with `escaped=true`, leaving no data for EPS >= 0.02. The flag is run-level and repeated on each row; complete windows before the escape are valid. Fixed `analyse_nrotor.py` to keep them. Also: noisy walkers (a ~ 0.9) leave the 8192 board at 2^23-2^26, so the registered window k=20..26 exists only for EPS 0 and 0.01; comparison moved to k=12..22 and k=12..20 after seeing this. No data touched.

### 2026-10-19 (+13) · f414649 · observation
Ratio (k=12..22): EPS 0 1.69, 0.01 2.59, 0.02 2.41, 0.05 2.11, 0.1 1.84, 0.2 1.62, 0.4 1.42, 0.7 1.31, 1.0 1.26. a is 0.87 at EPS=0.01. EPS=0.01-0.05 runs drift (g 0.05-0.10). Minimum ratio 1.26.

### 2026-10-19 (+13) · f414649 · surprise
(i) and (iii) falsified: the ratio is non-monotone (peak ~2.6 at EPS=0.01, above the rotor's 1.7) and a leaves the 2/3 branch at EPS=0.01. (ii), (iv), (v) held. I expected noise to interpolate smoothly between rotor and memoryless; it does not.

### 2026-10-19 (+13) · f414649 · interpretation
No EPS gets below 1, so the ant deficit (median 0.81) is not reproduced by any rotor/noise mixture tested. Stopping rule from README item 5 applies. The low-EPS peak is a non-stationary transient; mechanism untested.

### 2026-10-19 (+13) · 8b290d8 · observation
Census window: `experiments/_lib/analyse_probe.py` takes kappa from the last window (k=26) and fits exponents over k=20..26. This experiment's window mean differs from the last window by ~0 (rotor), -0.01 to +0.08 (memoryless, last window k=22 not 26) and up to 1.5 (non-stationary noisy rotor, EPS 0.01: 4.15 vs 2.59). Memoryless comparison with the ants is not window-matched (a at k<=22).

### 2026-10-19 (+13) · 8b290d8 · deviation
Executing `notebook.ipynb` the first time gave an empty eps=1 row: the notebook selected `nrotor:1:` but the specs say `nrotor:1.0:`. Notebook bug only (`analyse_nrotor.py` groups by parsed float and was right). Fixed; reran from a clean kernel.

### 2026-10-19 (+13) · 8b290d8 · decision
Closing out per AGENTS.md: notebook.ipynb, notes pointer, baseline-experiment window-label note, homepage card, blog post. Steps 1, 3, 4 of the README plan not run (stopping rule: no EPS below 1).
