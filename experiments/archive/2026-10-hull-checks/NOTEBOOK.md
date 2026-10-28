# Lab notebook: hull checks

### 2026-10-15 21:36 (+13:00) · da88e61 · intent

User requested an experiment for Hull checks. Implement the registered follow-up
to hull-width and research avenue 5: profiles, matched radii, shape/local split,
persistence and resolution controls. Keep all existing working material intact.
Read experiments/README.md, hull-width README including its correction, and
notes/paper-gaps-research-avenues-2026-10-15.md before registering the design.

### 2026-10-15 21:36 (+13:00) · da88e61 · assumption

The unresolved census pool is useful for sampling candidates, but is not a
certificate of chaos. The angular maximum misses overhangs and depends on bin
size. Test resolution explicitly; retain incomplete and escaping runs. Neither
contour calibration nor matching guarantees a physical interface interpretation.

### 2026-10-15 21:36 (+13:00) · da88e61 · decision

Run a bounded pilot before starting a large sweep. WSL was inaccessible in the
sandbox; the permitted WSL invocation works outside it. No dependency changes.

### 2026-10-15 21:42 (+13:00) · da88e61 · observation

Commands in README completed: scripts/checks.py passed all synthetic controls;
scripts/validate.py matched nine legacy rows and one/six-thread output exactly.
scripts/run.py --pilot and scripts/analyse.py --pilot produced six complete runs,
30 checkpoint rows, 10 valid profiles and 20 empty-bin exclusions in results/pilot/.
Repeating the pilot verified the six hashes and skipped all jobs (results/resume.log).
cargo test --release passed (results/release_tests.log); the new example oracle
passed separately. notebook.ipynb executed from a clean kernel via the exact
uv/nbconvert command in README (results/notebook.log).

### 2026-10-15 21:42 (+13:00) · da88e61 · interpretation

The pilot validates acquisition and explicit sparse-bin handling. It does not test
any scientific prediction: the early contours are sparsely binned and only two
rotor seeds were run. Full-cohort matching and resolution gates remain untested.
No hypothesis was revised after the pilot. No previous results were changed.

### 2026-10-15 21:42 (+13:00) · da88e61 · decision

Experiment preparation is complete. Leave the full registered sweep unstarted;
this session addressed the request to set up an experiment and ran a bounded pilot.
The README contains the background full-run command and analysis command. Next:
run the full cohort, enforce coverage/resolution gates, then report original and
sampled cohorts separately. Working outputs are uncommitted, as requested by the
repository convention. Cross-cutting pointer: notes/hull-checks.md.
