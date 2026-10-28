# Lab notebook: boundary occupation by exposure class

Append-only. Newest entry last. Never edit an old entry; correct it with a new one
(`corrects: <timestamp>`). Tags: intent, assumption, observation, interpretation,
surprise, decision, dead-end, question, deviation. Times are UTC.

### 2026-10-20 09:40 (+00:00) · ba38590 · deviation
Environment differs from AGENTS.md (Windows + WSL, 6 cores, rustc 1.98, Python 3.12). This box:
Linux x86_64 (kernel 6.12.94+), 8 logical cores, 15 GB RAM, rustc 1.85.1 / cargo 1.85.1 (edition
2024 is stable since 1.85, so no upgrade was needed), uv 0.13.3, Python 3.13.5, no GPU
(`nvidia-smi` not found; no CUDA work). Commands run natively, not via `wsl -e`, with
`UV_PROJECT_ENVIRONMENT=$HOME/.venvs/turmite UV_LINK_MODE=copy`. Baseline `cargo test --release` on
ba38590: 144 passed, 0 failed, 0 ignored (log kept outside the repo). No push access: work is
committed locally on branch `turmite-research-agent/onboarding`.

### 2026-10-20 09:42 (+00:00) · ba38590 · intent
Locate the ants' below-uniform boundary occupation (census median kappa/kappa_unif 0.81) within
the boundary: flat edge (u = 1 unvisited neighbour) versus exposed cells (u >= 2). Informs whether
a mechanism for the deficit should be sought in edge roughness/tips or in returns to flat edge.
Also, as a by-product, test the 1.11 uniform reference rule by rule with an estimator that does not
need it.

### 2026-10-20 09:43 (+00:00) · ba38590 · observation
Reading `src/probe.rs`: per window c = new_cells/boundary_steps and kappa = (boundary_steps/S) /
(P_end/A_end), so c * kappa * P_end/A_end = new_cells/S exactly. The identity dA/dt = c kappa P/A
is an accounting identity of the probe's definitions at window level; its only non-trivial content
is the end-of-window convention, which is what makes the uniform value ~1.11. The time-averaged
share sum P(t)/A(t) removes that convention.

### 2026-10-20 09:45 (+00:00) · ba38590 · observation
Instrument validation (before registration; no class statistics examined except two RL windows
printed by `head`): `kappa_exposure_classes 20 512 --check` on 18 specs (ants plain and patched,
rotor, rw, mf) passes. A mutant clipping the class at 2 panics in `--check` (exit 101). mf seeds
2026101601-02 at grid 4096, 2^20 steps reproduce `examples/kappa_uniform_baseline.rs` on all 24
windows (area, perimeter, new_cells, boundary_steps): 0 mismatches.

### 2026-10-20 09:46 (+00:00) · ba38590 · decision
Registered P0-P4 in README.md before running the sample. Sample fixed by `scripts/select_rules.py`
(seed 20261020). Preferred hypothesis H-exposed (median Q >= 1.18).

### 2026-10-20 09:49 (+00:00) · 1593b61 · assumption
corrects: 2026-10-20 09:46 (README rationale for H-exposed). The README cites "depleted sub-edge
layers (`fig:layers`)" as generic. `notes/kappa-experiment-design.md` (Arm A, exploratory) places
the depletion in a "crust" class (15 of 24 selected rules; ~12% of the census by the c >= 0.6
proxy), while "uniform"-class ants have rho(d) within 0.3 of 1 for d = 2..4. The rationale is
therefore weaker than written; the registered prediction P3 itself is unchanged. Untested.
Exploratory follow-up (not registered): split Q by c >= 0.6 (crust proxy).

### 2026-10-20 09:49 (+00:00) · 1593b61 · observation
Main run finished before I looked at any output: `scripts/run.sh` (PID 9888) wrote
`results/classes.csv`, `classes.done`, `run.log` (binary sha256, specs sha256, elapsed). All 344
specs ran in `--check` mode with no panic (exit 0), so every window matched `probe::probe_walker`
and a board scan.

### 2026-10-20 09:49 (+00:00) · 181742c · observation
`uv run .../scripts/analyse.py` -> `results/analysis.txt`. P0 held (1152 windows, 0 mismatches
against `probe_all.csv`), P1 held (mf rho 0.9985-1.0020), P2 held (ant median rho 0.874, frac >= 1
0.312; rotor 1.798; rw 1.315), P2b held (median |ln dev| 0.036). P3 FAILED: median Q 1.349
[1.091, 1.593] but Q > 1 in only 64% of rules (needed 75%). P4 failed with the wrong sign
(Spearman +0.197). 5 of 256 patched runs excluded for escape. Between-seed sd: rho 0.023, Q 0.011.

### 2026-10-20 09:50 (+00:00) · 181742c · surprise
The rotor has a larger Q (1.60) than the median ant (1.35). Exposed-cell returns are depleted for
every non-uniform walker (rotor 0.71, rw 0.76, ant 0.41), so Q > 1 is not an ant signature.
The ant's distinctive shortfall is flat-edge returns: rho_1^ret 0.59 versus rotor 1.14 and rw 0.78.

### 2026-10-20 09:50 (+00:00) · 181742c · interpretation
POST HOC (`scripts/explore.py`): across rules rho tracks rho_1^ret (Spearman +0.93) rather than Q
(+0.05). The deficit's rule-to-rule variation lives in returns to flat edge. Confidence moderate:
flat cells are ~72% of time-averaged P, so composition contributes; age/colour/depth were not
recorded and are confounded with exposure. My welcome post's speculation that "the birth part does
not separate ant and rotor" holds only as a fraction of B (c ~ 0.44 vs 0.45); per unit of P/A the
birth part is c*rho and differs (0.33 vs 0.82), so that sentence needs a correction in the next post.

### 2026-10-20 09:51 (+00:00) · 181742c · decision
Byte-identical rerun with RAYON_NUM_THREADS=3 (scratch/, sha256 50ca6573...). Record results in
README (append-only below the registration), update notes, write a short blog progress entry.
Next test proposed, not registered: age-resolved flat-edge returns on a fresh sample.

### 2026-10-20 09:52 (+00:00) · 181742c · surprise
The notebook figure showed two ant rules with rule-mean returns 40-130x uniform. Cause: three patched
runs became board fillers without escaping (`RLLLRLLL@2` births/step 0.4998; `RLRRRRLRR@1` and `@3`
both 0.250116, i.e. the same attractor from two different patches). Blank-board runs of both rules
are census-stationary blobs. The registered plan only excluded escapes, so the registered numbers
include them; medians are robust.

### 2026-10-20 09:52 (+00:00) · 181742c · decision
Post hoc sensitivity in `scripts/explore.py`: drop runs with births/step > 0.05 in window 26
(clear gap: next highest 0.0101). No verdict changes (median Q 1.349, Q > 1 in 64.1%, P4 +0.21).
The notebook figure uses the filtered runs and says so. Open question for the notes: how often does
a 5x5 patch switch a census-stationary rule into a filler within 2^26 steps (here 3 of 256 runs, 2 of
64 rules)?

### 2026-10-20 09:54 (+00:00) · 8ab17a7 · decision
End of session. Release tests pass after adding the example (144 passed, 0 failed). Blog publisher
(`experiments.py`), `test_experiments.py`, `export_results.py --check`, `test_experiment.js`,
`test_ants.js` pass; Jekyll build, `check.rb` and `test_results.js` not run (no Ruby on this box).
Nothing running. Open: register the age-resolved flat-edge test; filler-switch frequency of patched starts.
Not pushed (no GitHub access from this box).

### 2026-10-25 08:55 (+00:00) · 3b0abc9 (merging origin/main df07dfe) · question
Merged upstream `main` (184 commits) by merge, not rebase, so `1593b61` (registration) and `1c9ac05`
(results) keep their hashes. Read `experiments/archive/2026-10-hidden-phase-return` (Rob Ede): it shows,
via one independently reproduced witness, that keeping every interior cell's next turn does not fix
a long return path; its support gate failed (17/24 start/band groups under eight long episodes), so
P1 there is untestable. Relation to this experiment: ours locates the ant-specific shortfall in
*returns to flat edge* (post hoc); theirs says the interior state controlling return timing
includes hidden colour phases. Question: is the flat-edge shortfall a timing effect (long
excursions set by phase organisation) or a targeting effect (fewer returns
reach flat cells at all)? Our data cannot separate these: we recorded neither cell age nor
colour phase. Any registered age-resolved follow-up must record phase too, or age and phase are
confounded. Registered predictions P0-P4 are unchanged.
Post hoc aside: the two `RLRRRRLRR` fillers (births/step 0.250116, about 4.0 steps per new cell)
match the `R^k L R R...` board-filler law `2(k+1)` steps per cell with k = 1 (Q20 in
`notes/open-questions-hypotheses.md`, `experiments/archive/2026-10-late-highway-board-check`); the
`RLLLRLLL@2` filler (0.4998, about 2 steps per cell) is not in that family. Two runs, not a finding.

### 2026-10-25 08:56 (+00:00) · 3b0abc9 (merging origin/main df07dfe) · decision
Retrospective pruning preflight at `df07dfe`: no matching signature (queries in README addendum).
No dead-end signature committed: P3/P4 are failed registered predictions in one cohort with
age/phase/depth confounded, not a disproved mechanism; an `empirical` signature deferring an exact
repeat is a candidate for review. Upstream's narrowed plan (`notes/ACTIVE.md`, 2026-10-23) defers
side follow-ups: the age-resolved flat-edge test is not scheduled and must pass the priority-1
feasibility gate first. Homepage card and ACTIVE entry reworded to say so; experiment filed in
`blog/atlas.json` under boundary-return (counter).

### 2026-10-25 09:16 (+00:00) · 0a010ff · deviation
Adversarial review of this branch (owner request, PR #14). Two process facts not recorded at the
time. (1) Toolchain: the 2026-10-20 run used rustc 1.85.1 (`results/run.log`); upstream now pins
`RUSTUP_TOOLCHAIN: 1.98.1` in CI, and every command from the merge (`8a073b7`) onwards uses
rustc 1.98.1 (48a229cea 2026-09-01). (2) The registration commit was amended before the run: local
commit `9d011fc` (09:46:25 UTC) was amended 7 s later into `1593b61`, changing only timestamps that
had been written ahead of the clock: README "Registered 09:50 UTC (22:50 +13:00)" became 09:46
(22:46), and NOTEBOOK headings 09:46 -> 09:45 (instrument validation) and 09:50 -> 09:46
(registration decision). No prediction, threshold, sample or code changed (`git diff 9d011fc 1593b61`:
3 lines, timestamps only). The run started at 09:46:44 UTC, after `1593b61`. Neither commit was
pushed before 2026-10-25.

### 2026-10-25 09:17 (+00:00) · 0a010ff · observation
Oracle coverage gap. `--check` compared window sums (area, perimeter, new_cells, boundary_steps,
fresh_nbrs = sum u b_u) and the end-of-window class counts p_u, so a per-step class mis-split that
preserves both sums passes. Demonstrated with a scratch mutant (not committed) that reports one
class-1 step as class 2 and the next class-3 step as class 2: on `RLLR@1`, 2^20 steps, grid 2048,
the committed instrument's `--check` exited 0 (output differs from the true one from line 2). Fix in
`examples/kappa_exposure_classes.rs`: `--check` now keeps an independent visited bitmap and class
counts (`Shadow`) and asserts at every step the start cell's class, the newborn flag behind f_u and
the class shares summed into m_u. The same mutant now panics on `RLLR@1`, `RL@2`, `RLR@1` (exit 101,
"start-cell class"). Also fixed the module doc (windows are (2^j, 2^(j+1)] with output k = j + 1,
as in the README, not (2^k, 2^(k+1)]) and the two clippy warnings (`doc_lazy_continuation`,
`needless_range_loop`, the latter by an iterator over the same indices 1..5 in the same order).
`cargo clippy --release --all-targets` reports no warning in this example.

### 2026-10-25 09:18 (+00:00) · 0a010ff · observation
Full reproduction with the corrected instrument, as `scripts/run.sh` but into gitignored
`scratch/recheck/` (`results/run.log` and `classes.done` untouched): fresh target dir
`$HOME/turmite-target-exposure-recheck`, rustc 1.98.1, binary sha256
`926d57d3fe47897533cd81e691e33014c3225e001981701bf182f7213b79c229` (working tree: only this example
modified), `RAYON_NUM_THREADS=8`, `26 8192 --check < results/specs.txt`, started 09:11:38 UTC, 105 s,
exit 0: all 344 specs pass the per-step checks. Output sha256
`50ca657398a6245ab76ac9d1fc7569d1203186926b8b6e5765b52acb9f284f79`, byte-identical to
`results/classes.csv` (`cmp` silent). So the committed data have no hidden class mis-split, and the
edit is behaviour-neutral on the registered output.

### 2026-10-25 09:20 (+00:00) · 599ec93 · observation
Post hoc review statistics (`scripts/posthoc_review.py`, committed in `599ec93`; unregistered,
no claims scored). P3 fraction Q > 1: 41/64, Wilson [0.518, 0.747], bootstrap P(>= 0.75) 0.037.
P4 Spearman +0.197 [-0.094, 0.475]. Spearman(rho, rho_1^ret) +0.934 [0.866, 0.966], part-whole.
P2b ratio 5-95% 0.931-1.086 (23/64 beyond 5%). Exact split rho = birth + w_1 rho_1^ret +
(1 - w_1) rho_2+^ret (max residual 7e-15). Fillers removed, variance shares birth 0.34 / flat 0.44
/ exposed 0.22; at w_1 = 1/2 they become 0.28 / 0.29 / 0.43. Rotor-ant gap 0.924: birth 51%,
flat 40%, exposed 11%; ant/rotor ratios 0.51 flat and 0.55 exposed, ant/rw 0.75 and 0.52.
Mean-field probe kappa 1.110 (SD 0.007, 8 seeds).

### 2026-10-25 09:20 (+00:00) · 599ec93 · interpretation
corrects: 2026-10-20 post hoc exploration (README) and progress post. "Flat-edge returns carry the
rule-to-rule variation, and that is where the ant differs most" does not survive the composition
check. The 0.93 is part-whole. The flat-edge share of variance comes from flat cells being ~72%
of the boundary, and relative to the rotor the ant is equally short in both classes. Still
standing: ant rho_1^ret <= 1.01 in every non-filler rule, and about half the rotor gap is births.
Scoring corrections: P3's outcome set was not exhaustive (the result fits no registered outcome);
P4 is unscored, not failed (its condition, H-exposed, did not hold); P1 covers classes 1-3 and is
uniform by construction. The welcome post's "most of the gap sits in returns" is wrong: births are
about half. Corrections were appended to the README (review addendum), the posts (dated
headings), `notes/open-questions-hypotheses.md` and `notes/ACTIVE.md`. The homepage card and
reader guide were reworded. `scripts/build_notebook.py` gained a review section, the corrected
scoring and caveats, and was rebuilt with `uv run --frozen`. The rebuild re-rendered
`results/returns_by_class.png` with different bytes (same data, plotting stack differs from
2026-10-20). The committed PNG was restored and is unchanged.

### 2026-10-25 09:23 (+00:00) · 2bacfc9 · decision
Pruning index: queried at `2bacfc9` (`rg --files notes/pruning-index/entries`; `rg -n -i -e exposure
-e exposed -e corner -e flat -e occupation -e kappa notes/pruning-index/entries`). Result: one entry
(`NR-20261022-additive-laws-order-blind`, conservation laws, no overlap) and no ID collision. Added
`NR-20261025-kappa-exposure-classes-exposed-edge`, empirical. It defers an exact repeat of the
H-exposed test only (the 256 patched specs, 2^26 steps, board 8192, k = 17..26, instrument
`1593b61`/`181b0b8`). Why it still holds after the review: the P3 fraction CI excludes 0.75 at the
Wilson level and has bootstrap P(>= 0.75) = 0.037. The controls have Q > 1, the instrument gap was
closed with a byte-identical rerun, and P4 is unscored, so the entry does not rest on it. The
flat-edge reading is excluded from the claim (post hoc, composition).

### 2026-10-25 09:34 (+00:00) · 10ee953 · cross-reference
The exposure classifier was checked independently in `experiments/archive/2026-10-exposure-classifier-check/`: 65/65 z3 checks as expected (incl. 6 negative controls). P3/P4 verdicts here stand; only wording is qualified (u = 2 includes one-cell strips, u = 1 includes T-junctions, u = 4 never occurs).

### 2026-10-25 09:39 (+00:00) · 05de7b2 · interpretation
Wording qualification after merging `turmite-research-agent/formal-checks` (`421d477`) into this
branch. Checker P6/P7: class labels are exposure counts, not shapes. "2+" is u ∈ {2, 3} (u = 4
absent in all committed rows); u = 2 includes one-cell strips; u = 1 includes T-junctions. Appended
to README ("Wording qualification from the classifier check") and to the 25 October corrections in
both 2026-10-20 posts. No number, verdict or registered text changed.
