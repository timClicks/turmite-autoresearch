# ext-other-lattices-turmites-noise

Migrated legacy investigation (2026-10-14). Its files used to sit in the flat `data/` directory (and `calib/`, `occ/`, `snaps/`, `dumps*`, `knock*` where listed) with the label prefix below; `experiments/_migration/map.tsv` gives the exact old -> new path of every file. This stub was generated from file names and script docstrings. It is **not** the original write-up: the question, timestamped hypotheses, commands and results are in `notes/` (mainly `notes/frontier-results.md`, `notes/frontier-status.md`, `notes/research-frontier*.md`; search for the label), and the producing command is usually in the script docstring or a `run_*.sh` here.

Old labels / prefixes: ext, tm, tri

## Scripts

- `scripts/ext_lattice_stats.py`: Items 24, 28 (and 25 with kind=tm): classify growth of hex / cube / turmite screens.
- `scripts/ext_long_stats.py`: Items 25 and 28 follow-ups: local exponents at late times for the turmite candidates (experiments/archive/2026-10-ext-other-lattices-turmites-noise/results/ext_tm_lo
- `scripts/ext_screens.py`: Spec generators for the lattice/turmite screens (items 24, 25, 28). usage: python3 experiments/archive/2026-10-ext-other-lattices-turmites-noise/scripts/ext_screens.
- `scripts/ext_specs_26_27.sh`: Items 26/27 experiments. usage (WSL): bash experiments/archive/2026-10-ext-other-lattices-turmites-noise/scripts/ext_specs_26_27.sh   (writes experiments/2026-10-13-
- `scripts/ext_stats.py`: Items 26 and 27: analyse experiments/archive/2026-10-ext-other-lattices-turmites-noise/results/ext_many.csv, ext_noise.csv, ext_bg.csv (made by experiments/2026-10-1

## Results

39 entries in `results/` (11 are `.log`/`.done` markers); csv/json/txt outputs, `*_stats.txt` hold the summaries quoted in the notes.
