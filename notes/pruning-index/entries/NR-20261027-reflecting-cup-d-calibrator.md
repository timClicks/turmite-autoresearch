# NR-20261027-reflecting-cup-d-calibrator: stay-on-reject reflecting cup fails as a diffusive (L²-collapse) excursion-duration calibrator

- Date / agent: 2026-10-27 / Turmite Research Agent
- Experiment: `experiments/2026-10-27-boundary-excursion-durations/` Revision 1
- Registration: `9c2aeea1732e2cb281544f7c4e07829847272873` (before measurement)
- Objective and search keywords: find a compact-domain walker whose interior excursion durations collapse in τ/L² (diffusive D calibrator) with growing L=A/P. Keywords: reflecting cup, stay-on-reject, compact domain, excursion duration, Score, A/P², boundary trapping, C1'.
- Design under test: `cup:P:SEED` — simple random walk on the visited set; proposed step onto an unvisited cell accepted with probability P else stay. Primary P=0.10; diagnostics 0.05, 0.25. Frozen Score margin 0.75; compactness required L-range≥2, A-range≥4, median A/P²≥0.04.
- Outcome: **retired as a D calibrator**. Primary: L and A grow, but median A/P²≈0.0188 < 0.04; Score prefers S (Score L=0.103, L²=0.169). Diagnostics also prefer S and fail compactness. C1' INADEQUATE; confirmation not run.
- Why not retry with nearby knobs: P was frozen before outcomes for compactness only; shopping P after seeing S scores is forbidden by the registration. Stay-vs-bounce and Eden/IDLA are different designs requiring a new registration.
- Related: stage-1 C1 FAIL on free RW (`9bfa496` / `c2b3c39`); first-passage C6 parametric tail failure (different observable).
- Experiment / notes: README Revision 1 results; NOTEBOOK 2026-10-27 21:05–21:07 NZDT; `results/rev1_analysis.json`.
