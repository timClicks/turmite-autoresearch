# Lab notebook: lean/tiled CI identity check

(Append-only. Each entry: timestamp, git hash, tag.)

## 2026-10-24T09:57Z `2474a93`... base `b942a82` - intent
Read AGENTS.md, README, CI.md, notes/ACTIVE.md, open PRs (#8, #9, both external, none touching this). Three candidates
ranked: (1) extend CI determinism check to `sweep_lean` and tiled backend [chosen: high value, low effort/risk];
(2) independent Python ant to spot-check census rows [higher value, too large for budget];
(3) re-verify one highway certificate at a different budget [narrow]. Pruning index searched: no match.

## 2026-10-24T10:00Z `b942a82` - decision
Registered P1-P4 in README before running anything.

## 2026-10-24T10:10Z - observation
All of P1-P3 held on first manual run (cmp of CSVs).

## 2026-10-24T10:15Z - surprise
First lz4 config (2^6 tile, 16 cache) agreed with dense but TURMITE_GRID_STATS showed 0 evictions and 0 compressed
stores: vacuous. Changed to 2^3 tile / 4 resident and added a stats-based guard to the script.
Also: first loop at 2^3 "differed at char 1" - my own error (stderr redirected into the CSV), not a discrepancy.

## 2026-10-24T10:25Z - observation
Script run: PASS (14 runs). Sabotaged cache size: script exits 1 as intended. See README for table.

## 2026-10-24T10:30Z - deviation
No `notebook.ipynb`: this is a CI/engineering check with no data analysis; the README table is the record.
