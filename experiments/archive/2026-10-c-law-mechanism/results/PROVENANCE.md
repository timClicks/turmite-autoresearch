# Provenance of results/ (written 2026-10-19 after the runs; WSL git cannot resolve this worktree's gitdir, so run logs recorded an empty commit)

Base commit of the code and registrations: `f0b96b7`. Code committed in `b7b4758` (tracer, tests, driver, Stages 1-2c) and `8cc447f` (Stages 3-4, notebook, notes).
`src/`, `tests/` and `examples/` are identical in `b7b4758` and `8cc447f` (checked with `git diff`). The tracer library was unchanged from the first Stage 2 run onward;
the driver gained the band `kind` argument and the `RULE@L` spec syntax after the first band runs (18:41-18:50) and before the ablation (18:53), and the committed driver is that later version
(it reproduces the earlier band output: the U ablation rerun is bit-identical to the main band run). Analysis scripts that produced
`stage*_analysis.*` are the versions in `8cc447f`, except `stage4_analyse.py`, whose first run (before the NaN fix recorded in NOTEBOOK) is superseded by the committed output.

Real clock times (file modification times, +13:00, 2026-10-19), which replace the estimated times written in the first NOTEBOOK entries:

| file | written |
|---|---|
| stage1_profile.*, stage1_explore.txt | 18:31 |
| stage1_k3.* | 18:33 |
| trace_calib / trace_sample / trace_valid_raw (run_stage2.sh) | 18:41-18:42 |
| trace_band_2e30_void.jsonl (void run) | 18:45 |
| trace_calib_rw.jsonl (run_stage2b.sh) | 18:46 |
| trace_band_L24..L29 (run_band.sh) | 18:47-18:50 |
| stage2_analysis.* | 18:52 (final rerun with band) |
| trace_band_abl_{Z,Y,H,U} (run_ablation.sh), stage2c_analysis.* | 18:53-18:54 |
| trace_sbg.jsonl (run_stage3.sh), stage3_analysis.* | 18:59-19:01 |
| trace_s4.jsonl (run_p1.sh, tracer part) | 19:04 |
| P1 probe (`probe 27 8192`, 2192 runs) | start 19:04:38, finish 19:18:57 (`p1/p1_probe.log`) |
| stage4_analysis.*, p1/p1_pairs.csv | 19:19 |

Producing commands are listed in `stage2_run.log` (tracer) and the README; the log's commit field is empty for the reason above.

`experiments/archive/2026-10-edge-statistics/results/edgestats_sample.csv` was produced by `examples/edgestats.rs` with **K = 23** (window (2^22, 2^23], 4096 board): recovered
by rerunning `scripts/find_edgestats_k.sh` on RRRLRRLLLLR for K = 20..26; only K = 23 reproduces the stored rows (colour 0: 2645 edge steps, 1339 births) exactly.
The command was `edgestats 23 RULE...` (rule list not recorded; the 300 rules are those in the file).
