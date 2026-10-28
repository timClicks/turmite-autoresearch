# knockout-maps

Migrated legacy investigation (2026-10-14). Its files used to sit in the flat `data/` directory (and `calib/`, `occ/`, `snaps/`, `dumps*`, `knock*` where listed) with the label prefix below; `experiments/_migration/map.tsv` gives the exact old -> new path of every file. This stub was generated from file names and script docstrings. It is **not** the original write-up: the question, timestamped hypotheses, commands and results are in `notes/` (mainly `notes/frontier-results.md`, `notes/frontier-status.md`, `notes/research-frontier*.md`; search for the label), and the producing command is usually in the script docstring or a `run_*.sh` here.

Old labels / prefixes: RLLLLRRRRLR, RRRRRLLLLLL, classko, followup, knock, knockout, verdict

## Scripts

- `scripts/classko_stats.py`: Item 14: class knockouts (colour classes, parity classes) vs matched random controls.
- `scripts/followup_stats.py`: Numbers for the page's follow-up section on the two open questions.
- `scripts/knockout.py`: Knockout map: shuffle one 5x5 patch of the real territory at a time.
- `scripts/knockout_analyse.py`: Analyse the coarse knockout map (see notes/knockout-map-hypotheses.md).
- `scripts/knockout_checks.py`: Ad hoc checks quoted in notes/knockout-map-results.md (run in WSL from the repo root, after knockout.py and knockout_analyse.py). Three sections: null hot-rate,
- `scripts/knockout_followup.py`: Checks after the coarse/refine maps (notes/knockout-map-results.md, 'Follow-up').

## Results

20 entries in `results/` (0 are `.log`/`.done` markers); csv/json/txt outputs, `*_stats.txt` hold the summaries quoted in the notes.

## Bulk output (gitignored)

- `dumps/`
- `knock/`
