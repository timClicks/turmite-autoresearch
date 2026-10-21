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
