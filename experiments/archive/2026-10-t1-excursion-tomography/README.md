# t1-excursion-tomography

**Status (added 2026-10-15): closed.** T1/T1b analysis, README, cross-cutting note and executed `notebook.ipynb` agree (see `NOTEBOOK.md`, last entries). Its "next work" (matched-area comparison) was done in `experiments/archive/2026-10-kappa-matched-area`: unresolved-to-weak, no T2 on that pair set. An intervention (T2) remains undesigned.

Migrated legacy investigation (2026-10-14). Its files used to sit in the flat `data/` directory (and `calib/`, `occ/`, `snaps/`, `dumps*`, `knock*` where listed) with the label prefix below; `experiments/_migration/map.tsv` gives the exact old -> new path of every file. This stub was generated from file names and script docstrings. It is **not** the original write-up: the question, timestamped hypotheses, commands and results are in `notes/` (mainly `notes/frontier-results.md`, `notes/frontier-status.md`, `notes/research-frontier*.md`; search for the label), and the producing command is usually in the script docstring or a `run_*.sh` here.

Old labels / prefixes: t1, t1b

## Continuation registered 2026-10-14 22:00 NZDT

Base commit: `797704a2988ea8d958df39ac96e3ece27bec0980` (dirty workspace).
Question: does the exploratory extreme-excursion cutoff relative to radius
retain its negative association with kappa across patched seeds?
Before measurement: expect Spearman correlation between rule-mean
`ln(L_99.9/R_eq)` and rule-mean `ln(kappa)` to be negative at both k=22 and
k=25. This is a descriptive consistency check on previously seen data,
not an independent confirmation or causal test. No significance threshold.
Use the existing T1b log-linear binned quantile, additionally report its
containing-octave bounds, between-seed sample sd (ddof=1), and open-time
shares. Keep all seeds; separately describe seeds with open share <=0.10
as a censoring sensitivity, which cannot remove censoring bias.
No fit or instrument change: no new calibration is required; report existing
rotor/random-walk conservation and kappa controls on these same inputs.
Script: `uv run experiments/archive/2026-10-t1-excursion-tomography/scripts/t1b_cutoff.py`.
Analysis seed 20261014 (no random operations); simulation seed IDs are read
from specs. Notebook reads tracked source inputs and the new generated
summary once committed; no commit is made without user instruction.

## Continuation results (2026-10-14)

`results/t1b_cutoff.json` records the command, commit, script and input hashes;
`t1b_cutoff_seeds.csv` and `t1b_cutoff_rules.csv` retain quantile bounds and
between-seed sample sd. At k=22 and 25, respectively, 44 rules have 6–8 and
7–8 available seed records. Ten escaped windows were excluded; some specs
also lack completed-excursion bin records. Spearman correlations of rule-mean
ln cutoff/radius with rule-mean ln kappa are -0.835 and -0.918. The registered
descriptive direction holds. Median between-seed sd of ln cutoff/radius is
0.129 and 0.128; median geometric-mean ratios are 156.1 and 147.1 steps/cell.
Keeping only seed windows with open-time share <=0.10 gives correlations
-0.830 and -0.921 across all 44 rules (325 and 334 seed windows).

This remains a size-contaminated descriptive association, not a causal
explanation. The binned quantile spans an octave; excursion duration divided
by radius has units steps/cell and is not a chord displacement. All input
conservation flags pass. Final-window rotor kappa is 1.971 +/- 0.040 sample
sd (four seeds), outside the original mean tolerance 2.00 +/- 0.01; no random
walk records reach k=25. Report these failed/unavailable controls rather
than claiming calibration success. No estimator fit was changed.

Validation: `cargo test --release` passed in the current dirty workspace
(`results/t1b_cutoff_tests.log`). The shareable notebook executed top to
bottom under `uv run --with nbconvert --with ipykernel --with nbformat jupyter
nbconvert --to notebook --execute --inplace experiments/archive/2026-10-t1-excursion-tomography/notebook.ipynb`
(`results/t1b_cutoff_notebook.log`). New outputs remain uncommitted as requested
by repository policy. Next work: matched-area comparison or intervention,
with exact quantiles and explicit censoring treatment.

## Scripts

- `scripts/t1_audit.py`: T1 audit: is D_med/R vs kappa a normalisation artefact (D in cells ~ 1)?
- `scripts/t1_depth_analysis.py`
- `scripts/t1_excursions.py`: Analysis of T1 excursion tomography data (experiments/archive/2026-10-t1-excursion-tomography/results/t1_excursions.csv).
- `scripts/t1_pair_disp.py`
- `scripts/t1_specs.py`: Patched starts seeds 0..7
- `scripts/t1b_analysis.py`: T1b analysis (notes/excursion-tomography-2026-10-13.md section 7).

## Results

12 entries in `results/` (2 are `.log`/`.done` markers); csv/json/txt outputs, `*_stats.txt` hold the summaries quoted in the notes.
