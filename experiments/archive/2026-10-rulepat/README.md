# rulepat: why do some rules paint a "plateau + diagonal rectangles" picture?

Trigger: a rendered image of `RLLLLLLLRRLRR` at 30M steps (visit-count colouring):
thin diagonal lines forming nested 45-degree rectangles over a flat field.
Reproduced exactly (`examples/rulepat_dump.rs`, 8192^2 board, from the repo root in WSL):
`./target/release/examples/rulepat_dump RLLLLLLLRRLRR 30000000 experiments/archive/2026-10-rulepat/dumps/img`
-> bbox 2322 x 2322, 100% of bbox visited, max visits 274 (all match the image).

## Observation before any hypothesis (2026-10-14 18:50 NZST)
- 81.1% of the 5.39M visited cells have been visited **exactly twice** and sit at
  colour 2 (the flat field in the image). Visits/cell overall = 5.6.
- Area / t = 0.18 and bbox width 2322 at t = 3e7 is roughly t^0.5, i.e. area ~ t,
  NOT the t^(2/3) area of the "chaotic" rules this repo studies. One endpoint is
  not an exponent: step 2 measures it.
- 46% of steps turn opposite to the previous step (staircase / diagonal moves);
  ~1,500 maximal alternating runs of length 32-1023 (the rectangle sides).

## Question
What property of a rule makes the ant (a) leave most cells at a single colour after a
fixed small number of visits (a "plateau"), and (b) travel in long diagonal ballistic
segments that bounce around inside the territory? Is it the same thing as a
different growth class?

## Descriptor (fixed now)
For a run of N steps: `m` = modal visit count among visited cells, `plateau` = share of
visited cells with that count, `pc` = their colour, `area/t`, bbox width, long-run count
(alternating-turn runs >= 32). Calibrate on controls first (step 5).

## Predictions (written before steps 2-5 are run)
- P1 growth: area exponent for this rule >= 0.9 (vs 0.667 for chaotic rules), width ~ t^0.5,
  between-seed sd < 0.03. If the exponent is ~0.667 the plateau is just a different
  texture inside the known class and the story changes.
- P2 ablation (flip each of 13 letters): the pattern is set by the *early* letters. Flipping
  colour 0, 1 or 2 destroys the plateau; flipping any of colours 3..12 keeps plateau >= 0.5
  in a majority (>= 6 of 10) of cases.  [Rationale guess: RL prefix = Langton's ant laying a
  first pass 0->1, colour 2 = L then is the "parked" state; later colours only matter for the
  rare cells that get a third visit.]
- P3 census (data/b3_rules.txt, 1200 rules): plateau rules (plateau >= 0.5) are enriched for
  prefix `RLL` by >= 3x over base rate, and `pc` is 2 in most of them.
- P4 the diagonal segments are transient highways: `detect.rs` confirms periodic motion on
  some, with even period and |dx|=|dy| as in the H19 catalogue. A 2^30 run does not lock
  into one permanent highway (the territory keeps growing in all directions).

## Log
(append below; do not rewrite the predictions above)

### 2026-10-14 19:20 NZST  step 2 (growth class) and step 3 (ablation) done; P1 supported, P2 FALSIFIED
Commands (repo root, WSL, after `cargo build --release --bin probe --example rulepat_scan`):
`./target/release/probe 27 16384 < results/growth_rules.txt > results/growth_probe.csv` (RLLLLLLLRRLRR, `@1..8` random 5x5 start patches, 2 tethered rules, 3 rotors, 2 random walks; the random walks leave the board, dropped) then `uv run scripts/growth_fit.py` -> `results/growth_fit.txt`.
`./target/release/examples/rulepat_scan 26 8192 < results/ablation_rules.txt > results/ablation_scan.csv` (and `calib_*` for the controls).
- **P1 holds, with a regime change.** Fit window k=21..27 (my first try, 16..26, was written before
  seeing the data and gave exponent 1.09 because area/t is NOT constant earlier: it dips to 0.05 at
  k=13-15 and climbs to ~0.19 by k=18-21; the window was moved after looking at per-octave area/t; that
  is a post-hoc choice, stated here). Area exponent 0.995 (sd 0.031 between 8 patch seeds), width
  exponent 0.498 (sd 0.016). Controls in the same fit: rotor 0.68-0.70 (t^(2/3)), the two tethered rules
  0.25-0.29 (area saturating). So this rule is a **diffusive, random-walk-like growth class**
  (area ~ t, width ~ sqrt(t)); a 2D random walk has the same area/t ~ const (rw plateau ~0.17 at m=1,
  `calib_scan.csv`). It is not in the t^(2/3) chaotic class at all.
- Descriptor calibration (`results/calib_scan.csv`, 2^26 steps): target plateau 0.83 at m=2, colour 2;
  controls: RL 0.22 (highway, leaves the board), random walk 0.17-0.18 (m=1), rotor 0.02, chaotic /
  tethered rules 0.01-0.16. So plateau >= 0.5 is far from every control (max 0.22).
- **P2 FALSIFIED.** Not one of the 10 flips of colours 3..12 keeps the plateau (0/10 >= 0.5; all <= 0.25),
  and the flips of colours 0-2 fail too. Three outcomes appear, not two: trapped (area ~1e3, max_visits
  saturated: flips of letters 8-12), chaotic t^(2/3)-like (area ~3e5, plateau ~0.01: flips of letters
  2-7) and the plateau phase. The family is fragile: truncating to the 11-letter prefix RLLLLLLLRRL gives
  plateau 0.86 (area 1.8e7!), RLLLLLLLRRLRR 0.83, RLLLLLLLRRLRRL 0.76, but RLLLLLLLRRLR, ...RRR and every
  other truncation/flip fail. The late letters matter for the ant's dynamics even though plateau cells
  never reach them (they only ever have colour <= 2), so the mechanism lives at the boundary / on the
  rare >=3-visit cells, not in the plateau interior.

### Hypotheses for step 4 (census), written BEFORE running it (2026-10-14 19:25 NZST)
Census: every rule starting with R, lengths 2..14 (16,383 rules), 2^24 steps, 4096 board.
Class "plateau-diffusive" = plateau >= 0.5 and area/t >= 0.05 and not escaped.
- C1 the class is rare: < 2% of rules overall, and absent for n <= 8.
- C2 nearly all members (>= 90%) have prefix `RLL`; plateau colour is 2 in >= 80%.
- C3 members have an L-run of length >= 4 right after the leading R (colours 1..4 all L) in >= 90%.
- C4 members come in extension families (like RLLLLLLLRRL, ...RRL, ...RRLRR, ...RRLRRL): if rule X is a
  member then at least one extension of X by 1-3 letters is also a member (checked for each member of
  length <= 11).
If C2 fails (many members with other prefixes) the explanation is not "colour 2 is the parked state".

### 2026-10-14 census result (`scripts/run_census.sh`, `census_stats.py`, `census_split.py`; 16,382 rules, 2^24 steps, 4096 board, 1,985 escaped)
Outputs: `results/census_scan.csv`, `census_stats.txt`, `census_split.txt`.
- My membership rule (plateau>=0.5, area/t>=0.05, not escaped) caught 1,085 rules (6.6%), so **C1 FAILED** as
  written. Cause: it lumps two different things. 950 of them have plateau >= 0.98: *regular fillings*
  (every cell visited the same m times, m = 4, 6, 8..., area = t/m, ordered growth, no long diagonal runs).
  Only 135 (0.8%) are irregular plateau rules like the target (0.5 <= plateau < 0.98, random-walk-like
  area/t 0.05-0.43). The split at 0.98 is **post hoc**. None of the irregular ones is shorter than 8 letters.
- **C2 FAILED:** only 64/135 irregular members start with RLL, and plateau colour is 2 in 43/135 (mode visits
  = 2 in 41); other modes are 4, 6, 8, 10, 12 (even only). Colour 2 as "the parked state" is one
  sub-family (RLL...), not the explanation. **C3** not met either (RLLLL prefix in 54 of 1,085 all members;
  not tested separately on the irregular ones). **C4 supported** (132/139 members of length <= 11 have a
  member extension within 3 letters; this includes the regular ones, so it is weak evidence).
- Caveat: classification at one horizon (2^24) is crude. The target itself only settles after k~18, so
  some "irregular" rules may be transients and slower ones missed. Not checked.

### 2^30 run (`rulepat_scan 30 20000`, `results/long_scan.csv`)
RLLLLLLLRRLRR does not lock into a highway or stop growing: 2^30 steps, bbox 15224, area/t 0.216,
plateau 0.863 at m=2, 20,930 long alternating runs, no escape. Width/sqrt(t) = 0.465 (0.44 at 2^27). P4
(second half) holds.

## Status / what is NOT done
- **Mechanism unexplained.** Established: (i) the pattern is a diffusive, random-walk-like growth class, not
  t^(2/3); (ii) most cells receive exactly two visits (colour 2 for this rule); (iii) it is fragile in
  rule space (single flips kill it), about 0.8% of R-prefixed rules up to length 14; (iv) a separate
  regular-filling class (5.8%) with the same area ~ t but perfectly uniform visit counts.
  Untested ideas: why even mode visit counts only (2,4,6,...: parity of passes needed to leave a cell back at
  a "parked" colour?); whether the plateau interior is entered at all after being formed
  (last-visit-time map); the front dynamics at the territory edge.
- P4 first half (are the diagonal segments transient highways per `detect.rs`, H19 period/displacement) was
  **not run**. The 45-degree rectangle sides are alternating-turn runs of 32-1023 steps (~2,000 per 2^26).
- Not yet linked from `notes/`; nothing committed (files are staged only).
