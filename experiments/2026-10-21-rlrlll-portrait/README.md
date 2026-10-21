# RLRLLL portrait: the blob and the wedge on one canvas

**Question.** The homepage card for the RLRLLL late switch (finding 09) shows the manuscript's four-panel figure,
which is dense on a phone and shows the switch only through a statistic (steps per new cell). Can we *show* the
switch: the whole territory, before and after, at a scale where a reader sees a small blob that sat for 12.7 billion
steps and the wedge it then lays down in about 0.3 billion more?

This is a visualisation experiment. It makes no new measurement and registers no prediction. Every pixel comes
from one deterministic blank-board run of `RLRLLL` on a 32768² board (no seed: the blank board is the only
input), the same trajectory as the G1 record and the macro-transition trace.

**Expectations written down before the run (2026-10-21, 3fcfce8)**, as consistency checks against the archived records,
not as hypotheses:
- the ant leaves the board after 12,974,495,928 steps (G1 and the macro-transition trace report step index
  12,974,495,927, counted from 0);
- at 1.2e10 the territory is a blob about ±1,770 cells across, and the front reaches x = -16,378 by the end;
- after the switch the territory is a wedge whose column height grows about 2 rows per 3 columns.

## Commands

```bash
experiments/2026-10-21-rlrlll-portrait/scripts/run_frames.sh        # ~3-5 min, ~1.1 GB RAM, ~3.5 GB scratch
uv run experiments/2026-10-21-rlrlll-portrait/scripts/render.py     # frames -> results/ (small PNGs + JSON)
```

`scripts/times.txt` lists the snapshot steps: every 5e8 to 1.25e10, three just before the switch, then every 1e7
from 1.268e10 to 1.297e10, plus one at the step the ant leaves the board.

`scripts/figure.py` then draws `results/portrait.png` (homepage card 09) and `results/territory_map.png` from
`results/` alone. `blog/scripts/export_results.py` copies the portrait to `blog/assets/results/rlrlll_portrait.png`.

## Results (2026-10-21)

Run log: `results/run_frames.log` (commit, binary sha256, command; 162 s wall in the cloud container).

- **Consistency with the archive.** The ant left the board after 12,974,495,927 steps, identical to the
  macro-transition trace, which also counts steps taken. (My pre-run expectation of ...928 was a wrong conversion
  of conventions; see NOTEBOOK.) At 1.2e10 the westmost visited 16-cell block starts at x = -1,808, consistent with
  the archived blob of about ±1,770. The last frame's front is at the board edge, x = -16,384.
- **Territory.** 9,508,817 cells visited at t = 12,676,000,000 (421,767 steps before the first front advance past
  the blob edge, the switch time used in the figure); 83,672,826 when the ant leaves the board. The last 2.3% of the
  steps reach 7.8 times as many new cells as the first 97.7%. These are exact cell counts from one trajectory, not
  estimates; they are bounded by the board, and on a larger board the sweeper would keep going.
- **Wedge shape.** The final territory is 10,016 cells tall over the ~14,500 columns west of the blob, a slope of
  about 0.69, consistent with 2 rows per 3 columns. Read off the picture, not fitted.

**What the picture does and does not show.** Blocks are coloured by the first snapshot at which half their cells
were visited, so the colour resolution is the snapshot spacing (5e8 steps in the blob, 1e7 in the wedge). The blob's
blue ramp is spaced as (t / t_switch)^(2/3) to spread its rings; that is a display choice, not a measurement. The
wake crop (t = 1.29e10) shows the front and the identical bulk rows reported by the macro-transition snapshots. The
picture says nothing about what triggers the switch.
