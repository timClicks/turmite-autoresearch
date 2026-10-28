# Handover: building the proposed paper figures (2026-10-17)

Worktree `F:\Code\turmite\.claude\worktrees\paper-figure-proposals`, branch `worktree-paper-figure-proposals`
(base `b7c55f9`). **Nothing from this session is committed.** Read `AGENTS.md` first (WSL for all toolchains;
commit only when asked; append-only `NOTEBOOK.md`).

## Task
User: "work on figures", pasting item 4 of `notes/paper-figure-proposals-2026-10-16.md`: the `RLRLLL` column-sweeper
figure with three parts: (i) steps-per-new-cell vs t showing the switch, (ii) a crop of the period-3 boustrophedon
wake, (iii) predicted vs measured d|x|^2/dt (0.86, 0.84 vs 0.86, 0.83). Items 1-3 and 5-8 of that note are not started.

## State of item 4: figure built, not yet in the paper

Draft figure: `research-outputs/cube-root-growth-paper/fig/late_switch.{pdf,png}` (four panels: a steps/new cell vs t;
b y(t) sawtooth; c wake colour crop; d predicted vs measured). Last render was inspected and looks acceptable.

Files created (all untracked):

| File | Role |
|---|---|
| `experiments/archive/2026-10-g1-ribbon-breakout/scripts/g1_wake_extract.py` | Only reader of the gitignored dumps; writes the small committed extract |
| `experiments/archive/2026-10-g1-ribbon-breakout/results/g1_wake_extract.json` | L, x, colour shares, lag agreement, dump sha256, crop coordinates |
| `.../results/g1_wake_shape_<T0>.csv`, `g1_wake_crop_<T0>.csv`, `g1_sweep_trace_<T0>.csv` | T0 = 12800000000 and 12900000000 (about 250 KB total) |
| `research-outputs/cube-root-growth-paper/late_switch_figure.py` | Figure script; reads only committed `results/` |
| `.../fig/late_switch_numbers.json` | Predicted and measured d\|x\|^2/dt, onset, as plotted |

Run (from the worktree root, PowerShell tool; the Bash tool refuses `wsl` here):
```
wsl -e bash -lc 'export UV_PROJECT_ENVIRONMENT=$HOME/.venvs/turmite UV_LINK_MODE=copy; cd /mnt/f/Code/turmite/.claude/worktrees/paper-figure-proposals; uv run experiments/archive/2026-10-g1-ribbon-breakout/scripts/g1_wake_extract.py /mnt/f/Code/turmite/.claude/worktrees/g1-builder-structure/dumps'
wsl -e bash -lc '... uv run research-outputs/cube-root-growth-paper/late_switch_figure.py'
```
Quirks: WSL calls fail if the cwd is a subdirectory or the command has heredocs or `&&` chains inside `bash -lc "..."`;
use single-quoted `-lc` strings and `Set-Location` to the worktree root. Edit tool paths must include the
`.claude\worktrees\paper-figure-proposals` segment.

### Where the raw data is
The dumps (`g1_<T0>.traj.csv`, `g1_<T0>.wake.bin`, 38 MB each) exist only in the sibling worktree
`F:\Code\turmite\.claude\worktrees\g1-builder-structure\dumps\` (gitignored; branch `worktree-g1-builder-structure`,
commit `18b49fc`). If that worktree is deleted the extract cannot be regenerated without rerunning
`builder_dump RLRLLL 12800000000 400000 ...` (about 1.3e10 steps each, takes hours). The extract script records input
sha256s in `g1_wake_extract.json`. Treat the committed extract as the durable record.

### Numbers reproduced (agree with paper text and with the g1-builder note)
- Switch at t = 1.2677e10 (g1_stats.py rule: steps/new stays < 8 afterwards); paper text rounds to 1.3e10.
- L = 6,400 and 8,610; |x| = 11,070 and 14,386 (mean of first and last x of each 4e5-step dump).
- Predicted d|x|^2/dt = |x|/(2L) = 0.865, 0.835. Measured by polyfit of x^2 vs t over 40 fine 1e6-step windows within
  +-2e7 of each dump: 0.860, 0.832. Rounds to the paper's 0.86/0.84 vs 0.86/0.83. (The g1 note's 0.862/0.833 used a
  slightly different window; difference is in the third decimal.)
- Wake: colours 3, 4, 5 each about 0.33; lag-3 column agreement 0.994, lags 1, 2, 4, 5 below 0.003.
- Caveat the figure does not hide: both L values come from the same single trajectory, so panel d is a consistency
  check, not a test of L ~ |x|. Say this in the caption (the main.typ prose already does).

## Remaining work for item 4
1. **Insert into `main.typ`** in section `sec:late-switch` (around line 589-595): `#figure(image("fig/late_switch.pdf", width: 100%), caption: [...]) <fig:late-switch>`
   and reference it from the prose. Caption must state: single blank-board trajectory, panel a coarse (1e8) and fine (1e6)
   windows, black ticks = windows with no new cell, panel b/c from the 1.28e10 dump, c is a stretched 36x80 crop,
   d predicted vs measured with the same-trajectory caveat. Then compile (`typst compile --root . research-outputs/cube-root-growth-paper/main.typ ...`; check typst is available in WSL or Windows).
2. **Register in `rebuild_figures.py`**: add `late_switch_figure.py` to `SCRIPTS`; add `g1_ribbon.csv`, `g1_wake_extract.json`,
   `g1_wake_shape_*`, `g1_wake_crop_*`, `g1_sweep_trace_*` to `INPUTS`. Don't run the full rebuild casually (it overwrites all figures and the recipe).
3. **Provenance gaps** (the paper's audit table already flags them as "absent from checkout"):
   `git show 18b49fc:examples/builder_dump.rs > examples/builder_dump.rs` and
   `git show 18b49fc:notes/g1-builder-structure-2026-10-14.md > notes/g1-builder-structure-2026-10-14.md`; check the example still builds
   (`cargo build --release --example builder_dump` via WSL; it was written against an older tree, `DIRS`/`Rule` API may have changed).
   The original `data/g1_builder_*.py` scripts were not ported; `g1_wake_extract.py` supersedes the analysis parts used here.
4. **Notebook entries**: append dated `NOTEBOOK.md` entries to `experiments/archive/2026-10-g1-ribbon-breakout/` (intent, observation of the
   reproduced numbers, decision to commit a small extract instead of reading dumps, deviation: new extract script) with git hash; add a
   short section to its `README.md` listing the new script/results. Update `notebook.ipynb` only if you add a cell for the figure (must read committed results only).
5. **Polish (optional)**: panel c bracket label "one period (3 columns)" sits close to the title; the crop's ragged top is the wake's low-y
   boundary (turnaround region) and is real, the clean stripes begin about 25 rows in; panel a's black rug of empty windows is a thick bar.
   Check the PDF at final width in the compiled paper, not just the PNG.
6. Add `late_switch*` to the figure list in `research-outputs/cube-root-growth-paper/README.md` if it enumerates figures.
7. Update `notes/paper-figure-proposals-2026-10-16.md` status line for item 4 (append, don't rewrite).

## Other figures still to do (priority order from the proposals note)
1 walker map (a, kappa) plane; 2 edge gap W(t) ants vs rotor; 3 layer profiles rho(d); then 5 prefix lookup, 7 calibration local slope.
The note says data availability was **not** checked for any of them; step one for each is locating the committed CSV/JSON
(audit numbers in `research-outputs/cube-root-growth-paper/audit.typ` give script and result paths). Follow the same pattern as above:
figure script reads only committed `results/`, uses `style.py` (`st.apply()`, `st.save`, palette meanings), writes into `fig/`,
gets registered in `rebuild_figures.py`.

## Not done / not verified
- `cargo test --release` was not run (no Rust changes yet). The advisor tool was not consulted.
- The figure was only viewed as PNG; the Typst build was not attempted.
- No commit was made; per `AGENTS.md` and the background-job rules, commit (and push, no force, not to main) once the figure is in `main.typ` and notebook entries are written.
