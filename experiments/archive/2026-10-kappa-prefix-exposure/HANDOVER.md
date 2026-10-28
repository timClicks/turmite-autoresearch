# Handover — kappa prefix exposure (2026-10-16)

## State
Instrument built, tested and calibrated; cohort, arms and seeds frozen; development pilot done; registration appended to README. **No confirmation run has been done and no validation mutant simulated.** Nothing is committed (commit only when asked).

## What exists
- `src/prefix_exposure.rs` (producer with incremental depth map + pure accountant), `tests/prefix_exposure.rs` (11 tests vs brute-force oracles, hand cases, controls; depth update radius 5 shown tight, radius 4 fails 99/120), `examples/kappa_prefix_exposure_sampler.rs`. `src/lib.rs` has one added line; `src/field_age.rs` belongs to another scope and is untouched. Full `cargo test --release`: log in `results/release_tests.log` (no failures seen).
- Scripts: `select_cohort.py` (cohort/arms/specs/manifest), `pilot_analyse.py`, `confirm_analyse.py` (registered analysis; `--dry-run` exercises it on pilot data, prints only), `kpe_lib.py`.
- Results: `cohort.csv`, `arms.csv`, `specs_*.txt`, `selection_manifest.json`, `pilot_stats.txt`, `pilot_pairs.csv`, `registration_hashes.txt`; superseded pilots kept as `*_v1`, `*_v2_oldarms` (raw in gitignored `dumps/`).
- Determinism verified: 1 thread vs resumed 3->6 threads vs original pilot, 144 files byte-identical.

## Run next (WSL, repo root; dev first, then validation)
```
export CARGO_TARGET_DIR=$HOME/turmite-target UV_PROJECT_ENVIRONMENT=$HOME/.venvs/turmite UV_LINK_MODE=copy
cargo build --release --example kappa_prefix_exposure_sampler
cd experiments/archive/2026-10-kappa-prefix-exposure
RAYON_NUM_THREADS=6 nohup $CARGO_TARGET_DIR/release/examples/kappa_prefix_exposure_sampler dumps/confirm_dev 536870912 4096 64 32768-34816,131072-139264 < results/specs_confirm_dev.txt > results/confirm_dev_run.log 2>&1 &
# same for confirm_val with specs_confirm_val.txt; reruns skip finished specs
cd ../../.. && uv run experiments/archive/2026-10-kappa-prefix-exposure/scripts/confirm_analyse.py   # run once, after both finish
```
Before launching: confirm script/binary hashes still match `results/registration_hashes.txt` (binary at registration: d40781439bc239ac...). Estimated ~1.7 h wall. Then fill README results, NOTEBOOK, update `notebook.ipynb` from committed results, and add a line to `notes/kappa-mechanisms-2026-10-15.md` and `notes/open-questions-hypotheses.md`.

## Things to know
- Primary kernel statistic is per-episode Lam_w, not per-discovery windows (those double-count; see NOTEBOOK deviation). w=256 was chosen using the development pilot.
- Pilot noise is large (sd of ln B/S per seed 0.53/0.70), hence 64 seeds; pilot median |Y| for late mutants is at the null level.
- Exposure share per colour is ~1/n for all colours; informative exposure features are read depth / boundary share, which are strongly collinear with position (R^2 0.4), so P2 may be unidentifiable.
- Concurrent W6 matched-area reanalysis (commit 3d00123) motivated positions 1 and 2 for every base and the paired-direction test.
- Caveats: stationary label is outcome-related (g_k); mutants non-canonical; launch statistics have no analytic known-answer calibration (only oracle agreement); one non-trivial non-primitive arm rule per side is simulated as written.
- Other sessions committed during this work (HEAD moved b3a0f76 -> 997c9b2); the working tree is shared and dirty.
