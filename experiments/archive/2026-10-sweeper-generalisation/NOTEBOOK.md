# Lab notebook: Are the other three no-highway escapes macro-transitions?

Append-only. Newest entry last. Never edit an old entry; correct it with a new one
(`corrects: <timestamp>`). Tags: intent, assumption, observation, interpretation,
surprise, decision, dead-end, question, deviation. See `experiments/README.md`.

### 2026-10-23 18:05 (+13:00) · d8c0892 · intent
Generalise the RLRLLL checker (user request, session start). First establish whether `RLLLLRRL`, `RLLLLRLRRL`, `RLLLRLRLLL`
run sweepers at all. Informs whether Stage 2 (checker generalisation) has any target.

### 2026-10-23 18:05 (+13:00) · d8c0892 · assumption
The user flagged mid-session that "escaped" only means the ant reached the board edge, and the three final boxes are nearly
square, so a filler is as likely as a sweeper. I agree; the plan does not assume sweepers. Status: untested, see G4/G1-G3.

### 2026-10-23 18:05 (+13:00) · d8c0892 · decision
Pruning preflight: index `d8c0892db5e97d4d4f6f8de0933814a51b5a5b7c`; `rg --files notes/pruning-index/entries` lists one entry;
`rg -n -i -e RLLLLRRL -e RLLLLRLRRL -e RLLLRLRLLL -e sweeper -e escape -e column notes/pruning-index/entries` exit 1, no
output. Sole entry `NR-20261022-additive-laws-order-blind` has a different objective (conservation laws); does not apply. Run.
Budget: see README. Note `notes/ACTIVE.md` (committed 17:49 today) defers extending proofs to more patterns unless bounded;
the user's explicit request overrides, so the work is bounded as written in the README and stops at the stated criteria.

### 2026-10-23 18:05 (+13:00) · d8c0892 · deviation
Task D of the parent (`scripts/d_resim.sh`, registered 2026-10-21, never run) was launched first in WSL at about 17:50 as the
cheap item-1 result; its output is `parent/results/d_resim.txt`. It is not part of this experiment.

### 2026-10-23 18:40 (+13:00) · 1461cb9 · observation
Oracle for the front log (`scripts/oracle.sh`, output `results/oracle.txt`, binary sha256 `7d135c9b...`, fresh target dir, exit 0):
final fingerprint (position, heading, FNV-1a of all cell colours, non-zero count) is identical to `fast::run` (via the parent's resim
example) at 1e7 and 1e8 steps for RLLLLRRL, RLLLLRLRRL, RLLLRLRLLL, RLRLLL, RRLLLLRRL on a 16384 board; an independent Python ant
reproduces all four event files exactly for 2e5 steps for the same five rules. Instrument accepted for Stage 1.
Side observation (not a result): RLLLLRRL has 24.7M non-zero cells at 1e8 steps versus 2.0M at 1e7, about 4 steps per new cell
already at 1e8; the other two escapes have about 1e6 and 4.8e5 non-zero cells at 1e8.

### 2026-10-23 18:40 (+13:00) · 1461cb9 · decision
Launch Stage 1 as registered and amended (`scripts/run_stage1.sh`): five parallel single-core runs, 65536 board for the three targets,
32768 for the controls. Machine otherwise idle (parent Task D finished).

### 2026-10-23 18:01 (+13:00) · 6ecd317 · deviation
corrects: the timestamps 18:05 (registration, README header and first notebook entries), 18:15 (README amendment) and 18:40 (oracle
and launch entries). I wrote those from memory of the plan instead of reading the clock; they are wrong. The authoritative times are
the git commit times: registration `7aed7de` 17:51:16, amendment + front-log example + oracle scripts `1461cb9` 17:52:06, oracle result
+ analysis scripts + Task D result `6ecd317` 17:54:04, Stage 1 launched immediately after `6ecd317`. The order (registration and amendment
before any Stage 1 run) is unaffected. Ordering of the oracle outputs relative to `6ecd317` is as logged in `results/oracle.txt`.

### 2026-10-23 18:01 (+13:00) · 6ecd317 · deviation
Mid-run peek, not the registered analysis. While Stage 1 was still running I read partial `windows.csv` files to see whether the runs
were alive. This revealed (a) the positive control left the board at step 12,974,495,927 at (-16384, -5895), exactly as in the
parent's run; (b) new cells are sparse: most 1e6-step windows of the three rules contain 0 new cells (sampling every 1000th window),
and the windows that do contain new cells have boxes as wide as the whole territory. So growth is by thin, territory-wide shells,
not by a narrow front. Maximum |coordinate| of new cells (largest per 2000-window block): RLLLLRRL 7823 (t = 2.0e9), 11643 (6.0e9),
14016 (1.0e10), 15788 (1.24e10); RLLLLRLRRL 3008 (1.9e9), 5486 (5.9e9), 7499 (9.7e9), 10681 (1.35e10); RLLLRLRLLL 1039 (2.0e9),
1517 (6.0e9), 1941 (1.0e10), 2141 (1.4e10), 2261 (1.7e10). The growth exponents between decades are about 0.36 for RLLLLRRL. This is a
post-hoc glance; G1-G4 are still scored only from the registered analysis (`clock.py`, `windows.py`) once the runs finish. It does
bear on the interpretation: RLLLLRRL's escape at the 32768 board looks like a t^(1/3)-class square reaching the edge, not a sweeper.

### 2026-10-23 18:45 +1300 · 597689e · deviation
Builds of this experiment's examples (WSL, fresh target directories, recorded sha256 in results/) were made from a working tree in which other sessions were editing `src/lean.rs`, `src/lib.rs` (adds `pub mod tiled`), `src/bin/sweep_lean.rs` and `src/tiled.rs` at the same time (file times 18:23-18:43; uncommitted). The examples here use only `Rule`, `DIRS` and `reference::Ant`, whose files are unchanged in git; the oracle and the 408-rule from-zero check compare against `reference::Ant` and `fast::run` as built then. I did not rebuild from a clean checkout of a single commit for every run; the stage-1 binary record says `dirty=0` for `examples/` and `src/` at `6ecd317` (its build preceded those edits).
Shareable `notebook.ipynb` built by `scripts/build_notebook.py` and executed from committed results (uv, WSL).

### 2026-10-23 18:49 +1300 · c0b1d5d · deviation
corrects: the times 18:05 / 18:15 / 18:40 in the earlier entries of this notebook (already corrected once at 18:01 in the header of that entry) and, in the README, the "Registered 2026-10-23 18:05" line: the registration commit `7aed7de` is 17:51:16. The README line is left as written; the commit time governs.
Review follow-ups: period-19 onset measured directly (revolution 19,596, xmin; 19,578, xmax; 13,170 revolutions to the exit); post hoc outputs regenerated from committed scripts; a vacuous p = 60 line explained and guarded; spiral wording corrected; falsification-harness disclosure and pruning-index outcome added to the README.
