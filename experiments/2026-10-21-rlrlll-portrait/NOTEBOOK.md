# Lab notebook: RLRLLL portrait

Append-only. Newest entry last. Never edit an old entry; correct it with a new one
(`corrects: <timestamp>`). Tags: intent, assumption, observation, interpretation,
surprise, decision, dead-end, question, deviation. See `experiments/README.md`.

### 2026-10-21 18:03 (+13:00) · 3fcfce8 · intent
Replace the dense four-panel figure on homepage card 09 with a picture of the whole territory through the switch.
Re-run RLRLLL from blank (cloud container, 4 cores, nothing else running) with `examples/rlrlll_portrait_frames.rs`,
which only adds snapshot writes to the plain loop shared with `g1_ribbon_breakout_builder_dump`. Consistency
checks against the archived run are listed in the README before the run.

### 2026-10-21 18:10 (+13:00) · cb05c24 · observation
`scripts/run_frames.sh` → `results/run_frames.log`: 59 frames, 162 s; left the board after 12,974,495,927
steps. `scripts/render.py` → `results/frames.json`, `arrival_b16.png`, two crops. Visited cells 9,508,817 at
12.676e9 and 83,672,826 at the end. Front block at 1.2e10: x = -1,808 (archive: about ±1,770).

### 2026-10-21 18:10 (+13:00) · cb05c24 · deviation
corrects: the README expectation "leaves after 12,974,495,928 steps". I converted the archived "step
12,974,495,927" as if it were a 0-based index; the macro-transition trace increments t before its board check, so it
already counts steps taken. The new run agrees with it exactly. The README expectation is left as written.

### 2026-10-21 18:10 (+13:00) · cb05c24 · observation
`scripts/figure.py` → `results/portrait.png`. The visual is lopsided in a way I did not anticipate when planning
it: the blob that took 12.7 billion steps is a small disc at one end of a wedge about eight times its area, laid in
0.30 billion steps. That contrast is the point of the figure, so panel (b) shows it as a cumulative-territory curve
on linear axes rather than the log-scale steps-per-new-cell plot of the manuscript figure.

### 2026-10-21 18:10 (+13:00) · cb05c24 · decision
The homepage card shows this portrait; the manuscript keeps `late_switch.pdf` unchanged, and the card links to it
for the quantitative panels (onset statistic, sweep traverse, d|x|²/dt check).
