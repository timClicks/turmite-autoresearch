# Lab notebook: late-highway board check

Append-only. Newest entry last. Entries before 2026-10-22 09:25 were written retrospectively from the README and git
history (this notebook was not started with the experiment; a deviation from the conventions).

### 2026-10-21 21:00 (+13:00) · fd03a6d · intent
The axis-aligned late highways have onsets at (k+1)*2^31 on a 2^30-cell board; registered H-artefact (B1) before running.

### 2026-10-21 21:10 (+13:00) · 8deb569 · observation
Onset scales as G^2 on 1024/2048/4096 boards; B1 failed only its 1% tolerance (perimeter term). 25 fillers by footprint.

### 2026-10-21 21:20 (+13:00) · 8deb569 · surprise
RLLLRLRRR is not a filler but does not escape on 65536: a ray inside its own territory cut off by the 32768 board edge.

### 2026-10-21 21:30 (+13:00) · 8deb569 · decision
Registered B2 (>= 24/26 reproduce on 65536) and launched the rechecks two at a time (4.3 GB each).

### 2026-10-22 07:40 (+13:00) · 6d5c49c · deviation
The recheck processes stopped twice while the session was idle (no process, partial .tmp outputs). Relaunched; the script
skips finished rules, so every result is from one uninterrupted run. Logged in results/recheck/recheck.log.

### 2026-10-22 09:25 (+13:00) · ecab728 · observation
B2 held, 26/26. Final genuine yields 16/807 = 1.98% and 12/732 = 1.64%. Flat-rate reading stands (p 0.45, 0.70).
