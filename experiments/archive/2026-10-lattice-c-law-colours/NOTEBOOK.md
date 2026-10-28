# Lab notebook: lattice c law, colours and circulations

Append-only. Newest entry last. Never edit an old entry; correct it with a new one
(`corrects: <timestamp>`). Tags: intent, assumption, observation, interpretation,
surprise, decision, dead-end, question, deviation. See `experiments/README.md`.

### 2026-10-20 00:55 (+13:00) · 6049d6a (+uncommitted instrument) · intent
Take the top open item of `notes/ACTIVE.md` (why b falls with loop length) and measure the two factors of the parent's
identity b = l_b / N_b rather than fit b(l). Built `src/lattice_trace.rs` (edge_trace's per-colour, lag, N_b tallies on three
lattices, plus runs of consecutive lag-`ell` returns and hole births). Gates T1 passed (square equals `edge_trace`, all lattices
equal a HashMap re-implementation, two mutations caught; the mutation runs left a `proptest-regressions` file that I deleted
because its cases fail only under the mutants). Predictions P1-P6 are in the README, written before running the 960 ants.

### 2026-10-20 00:56 (+13:00) · 6049d6a · assumption
A circulation of the lead letter shows up as a run of consecutive reads with lag exactly `ell`. This can be false where the
ant crosses its own ring or a second loop shares cells; it is checked only through P1 (does Cb carry the slope). Untested.

### 2026-10-20 00:56 (+13:00) · 6049d6a · assumption
Alternative I cannot exclude: the b(l) drop is survivor selection (the kept set differs by lattice; square lead 2 and hex R lead 2 lose >50%).
The tracer is run on all 960 rules and quantities are reported for kept rules only, with retention printed; a check on all non-escaped rules is a planned robustness line.

### 2026-10-20 01:20 (+13:00) · 34bb110 (+driver fix) · deviation
First two launches failed: (1) git inside WSL cannot read the worktree's Windows gitdir (fixed with GIT_DIR/GIT_WORK_TREE as in
`notes/ACTIVE.md`); (2) the driver did not strip the `ant:` prefix of the parent's spec lines, so every rule panicked on the letter `a`.
Fixed in `examples/lattice_c_law_colours.rs` only (one line, spec parsing); `src/lattice_trace.rs` and the tests are unchanged since the
registration commit. `run.log` will show the binary built from a dirty tree for that reason. No data had been produced by the failed runs.

### 2026-10-20 01:12 (+13:00) · 34bb110 (+driver fix) · observation
T2 passed (855 rules, 0 mismatches). P1 FAILED, P2 FAILED, P4 and P5 HELD, P6 FAILED (0.781 vs 0.80). Numbers in README Results; `results/analysis.txt`.

### 2026-10-20 01:13 (+13:00) · 34bb110 (+driver fix) · surprise
P3 passed formally (eps ratios 7.2 and 75) but I do not trust it: my run definition counts interior lag-ell loops, and C is 30-120 steps per birth while 1/c is 2-5.
Interior behaviour swamps the boundary episodes. So the headline discriminator was badly designed, and passing it would have been a false positive.
The boundary-only version (Cb) carries 17-42% of the slope. Recorded as a failed instrument design, not a result.

### 2026-10-20 01:14 (+13:00) · 34bb110 (+driver fix) · observation
Post hoc `explore.py`: slope lives in circulating-colour reads (0.95 per colour on hex R, 0.8 square, 0.65 to 0.35 triangular, 0.69 to 0.47 hex r), cancelled partly by
the kill and later colours. Lag-ell share of circulating reads is low off the square lattice (0.05-0.44). Hex r lead-1 hole births 15%.

### 2026-10-20 01:15 (+13:00) · 34bb110 (+driver fix) · interpretation
Reads per birth at colour k = fraction of born cells still on the boundary at their k-th read, so the c law is a boundary-survival plateau rho(geometry), b = rho - losses.
This restates 1/c = E[N_b]; it is not a mechanism. The ring-loop explanation looks wrong off the square lattice (lag share is a crude proxy; moderate confidence).
Outside neighbours per ring cell (square 2, tri 1, hex R 4, hex r 3) do not order the plateaus monotonically (tri 0.5, square 0.8, hex r 0.6, hex R 0.95): a question, not a hypothesis.

### 2026-10-20 01:16 (+13:00) · 34bb110 (+driver fix) · deviation
run.log reports "dirty: 0 files" although the driver fix was uncommitted when the binary was built; the `git status` under the GIT_DIR workaround is unreliable. The fix is committed together with the results.

### 2026-10-20 21:15 (+13:00) · 44ed81f · decision
Constructed and executed shareable notebook `notebook.ipynb` using `scripts/build_notebook.py`. It audits all committed results (`traces.jsonl`, `analysis.json`, `analysis.txt`, `explore.txt`, `run.log`), presents the registered prediction outcomes, explains why the interior-contaminated circulation estimator P3 was invalidated, and displays the post hoc colour-decomposition plateaus across square, triangular, and hexagonal lattices. Verified that `blog/scripts/experiments.py` renders the notebook (38 notebooks published).

