# Excursion tomography lab notebook

### 2026-10-14 22:00 (+13:00) · 797704a · intent

User requested continuation of an experiment and explicitly reminded me to follow AGENTS.md. Continue the unresolved T1b cutoff analysis using existing committed bin/window inputs; preserve legacy files and all unrelated working changes. Register the descriptive follow-up in README before measurement. Add seed dispersion and an honest treatment of quantile resolution. No new simulation or tail fit is planned.

### 2026-10-14 22:00 (+13:00) · 797704a · assumption

The log-linear within-bin 99.9th percentile used by T1b is an approximation, not an observed exact quantile. Its containing octave gives rigorous bounds for the completed-excursion sample. Window-crossing excursions remain censored; open-time share diagnoses but does not correct this bias. Seed replicates are patched starts, not independent rules. Input provenance is historical commit dd0e234 plus work then uncommitted, as recorded by t1b.commit; hashes will identify current input bytes.

### 2026-10-14 22:07 (+13:00) · 797704a · deviation

First analysis invocation failed its no-escape input assertion. Inspection of t1b_windows.csv found escaped windows; conservation remained true. Exclude escaped windows before any summary rather than treating board-truncated runs as complete. Report available seed counts instead of assuming eight. Command: the README analysis command. Initial sandbox WSL access failed; escalated execution succeeded in reaching the script. No result files were written by the failed analysis.

### 2026-10-14 22:15 (+13:00) · 797704a · observation

README analysis command produced results/t1b_cutoff.json and seed/rule CSVs. Across 44 rules, correlations at k=22/25 are -0.835/-0.918; median between-seed ln-ratio sample sd is 0.129/0.128. Ten escaped windows were excluded; available bin records give 6–8/7–8 seeds per rule. Rotor final-window kappa is 1.971 +/- 0.040 (four seeds); no random-walk final-window records exist. Conservation passes. See JSON input hashes and README for sample counts and sensitivity results.

### 2026-10-14 22:15 (+13:00) · 797704a · interpretation

The descriptive direction holds but radius remains a confound; this is no mechanistic advance. Quantile octave bounds and missing/truncated records limit inference. Duration/radius is not a chord length. Rotor mean misses its registered tolerance and the random-walk final-window control cannot be assessed.

### 2026-10-14 22:16 (+13:00) · 797704a · decision

Session closes with analysis, README, cross-cutting note and executed shareable notebook agreeing. Release suite passed (results/t1b_cutoff_tests.log), clean-kernel notebook execution passed (results/t1b_cutoff_notebook.log), and rerunning the analysis reproduced all three output hashes. No commits or dependency changes. New outputs await a requested commit; notebook inputs are tracked historical results plus these new summaries. Next: matched-area/intervention design and exact quantile/censoring treatment rather than interpreting this ratio causally.

### 2026-10-14 22:30 (+13:00) · 797704a · decision

User requested the proposed manuscript change. Added a qualitative negative-result paragraph to the cube-root paper's kappa discussion and qualified the conclusion's claim that the hitting-problem candidate was untested. Included size, quantile, censoring and control limitations; no new headline claim or numerical result. Rebuilt main.pdf with `typst compile --root . research-outputs/cube-root-growth-paper/main.typ research-outputs/cube-root-growth-paper/main.pdf`. Existing figure and number assets were preserved. Text extraction confirmed the two changed passages on pages 10 and 22; rendered those pages for visual review. Poppler was unavailable, so used uv with pypdf for text and Typst for PNG rendering. No dependency-file changes or commits.
