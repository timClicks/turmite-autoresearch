# Lab notebook: hidden phase and boundary return

### 2026-10-23 11:37 UTC · b942a828 · intent
Read AGENTS, ACTIVE, the evidence ledger, boundary-return and gate records, and
the c-law renewal scope. Choose one causal pilot under the boundary-access
priority. An independent source audit suggested exact seed minimisation; defer
that option because ACTIVE explicitly limits new proof work this phase.
Register competing turn-map/hidden-clock explanations before measurement.

### 2026-10-23 11:37 UTC · b942a828 · decision
Pruning query and sole signature inspected as recorded in README: no applicable
signature. RUN the frozen 12-start pilot, no exclusions. Full eligibility counts
are a prerequisite; no main renewal outcomes will be opened. Build a separate
instrument and compare against the reference ant. Stop after this pilot even if
it invites a broader study.

### 2026-10-23 11:45 UTC · 9d36304 · observation
Instrument controls passed before any pilot: four Rust tests compare dense replay
with the independent sparse reference on six rules x 24 fields and all five
prefix arms, check depth-bin histograms and fixed boundary cells, exercise real
path divergences, equivalent RLRL phases and a one-step exact return at the cap.
Analysis controls plant known effects, replay censoring and a rare overflow that
carries most of the time. The latter illustrates why count eligibility alone is
not enough. Commands are in scripts/run.py and scripts/test_analysis.py.

### 2026-10-23 11:45 UTC · 9d36304 · decision
Freeze instrument and analysis before measuring. Use three worker threads, then
repeat the complete pilot with one thread and compare all CSV bytes. No justfile
or flake exists. Rust 1.100.0-beta.4, macOS arm64, locked dependencies. Resource
inspection via ps was sandbox-blocked; three workers is a conservative cap.
No scientific outcome inspected yet. The fresh build runner logs binary/source
hashes and refuses to overwrite existing measurements.

### 2026-10-23 11:43 UTC · bcfceeb · deviation
Corrects the two preceding 11:45 timestamps: those labels were written from an
estimated clock and are two minutes ahead. The actual freeze commit completed
at 11:43 UTC; all controls were already run. Registration and instrument commits
precede the pilot. Subsequent entries use the system clock directly.

### 2026-10-23 11:44 UTC · bcfceeb · observation
scripts/run.py finished the 12-start pilot and complete one-thread replication:
24 CSV files match. Frozen analyze.py: 9,680 departures, 160 sampled, 3,200
replays. All baseline and replay censor counts zero. Support fails in 17/24
groups; P1 fails in two of six rule/band cells. Report the registered stop,
not a larger run. Full CPU release suite also completed successfully.

### 2026-10-23 11:48 UTC · bcfceeb · interpretation
Independent source critique found no clear simulation bug. Incorporate its
limits: effect ratios are not information fractions; long-baseline selection
limits signed effects; equal-start summaries can rest on one episode; live
agreement checks endpoints, not full live paths. Add whole-field edit fractions
and signed effects to a supplemental report without altering frozen analysis.
Cite the earlier c-law delayed-phase proposal; the prefix idea is not novel.

### 2026-10-23 11:48 UTC · bcfceeb · observation
Post hoc witness chosen by maximum k=1 shortening: RLLLRRLRLL, seed 2026102304,
t0=759018, 86030 -> 6 steps. Independent sparse Python checker recreated the
full patched-start trajectory, permutation and returns. Split on read 2 of
(-54,-65), phase 5 -> 4 (RL vs RR). This is a checked example under a many-cell
shuffle, not a single-cell attribution. Output results/witness.json.

### 2026-10-23 11:48 UTC · bcfceeb · decision
Stop as registered. No pruning signature because the support gate failed; no
family exclusion. Preserve the narrower counterexample to exact next-turn-map
sufficiency on edited fields. Write the shareable notebook, reader-facing account
and PR with the failed thresholds alongside the observation.

### 2026-10-23 11:52 UTC · bcfceeb · observation
The shareable notebook executed from a fresh kernel and reproduced the frozen
analysis exactly, including CSV hash checks. Kernel startup required local socket
access outside the sandbox. The CPU release suite passed. Strict Clippy failed
on 35 warnings in existing library modules before checking the new example;
ordinary Clippy completed with advisory warnings. No unrelated cleanup was made.
The local Ruby is 2.6, below the blog's Ruby 3.3 requirement, so a full Jekyll
build is not available through that toolchain. Python publication checks follow.

### 2026-10-23 11:56 UTC · 1c0d631 · observation
Publication preparation rendered 119 experiment pages and 47 saved notebooks;
this experiment has six output blocks and no notebook errors. Its source/image
links resolve. The two unavailable links are in older experiments. Atlas
validation and eight atlas tests passed. Publisher fixtures need unsigned dummy
commits and a physical temporary path on this Mac: use TMPDIR=/private/tmp and
GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=commit.gpgsign GIT_CONFIG_VALUE_0=false for
that test process only. No repository signing setting was changed. The default
macOS temporary-path alias caused the first fixture attempt to miss its image.

### 2026-10-25 · correction · P1 status and 640/640 framing
Review of PR #8: with the support gate failed, P1 was untestable, so earlier
entries saying it "failed" should be read as "ratios descriptive". 640/640
changed paths is near-guaranteed under a ~10^4-label edit. Wording changed in
README (appended section), blog, homepage, atlas and notes; no data or code touched.

### 2026-10-25 · deviation · Clippy tidy of the frozen example
Post-merge, `examples/hidden_phase_return.rs` was edited for Clippy only
(`to_string`-free `?` on a `String` error, three collapsed `if` blocks via let
chains, rustfmt). The frozen run is not superseded: a fresh release build at
three threads reproduced all 24 CSVs byte-identical to `results/`. The library
was tidied in the same change (`cargo clippy --lib --example hidden_phase_return
-- -D warnings --no-deps` is clean); `cargo test --release --locked` passed.
Other examples still carry Clippy warnings and were left untouched.
