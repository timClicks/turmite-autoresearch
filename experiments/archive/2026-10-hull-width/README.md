# hull-width: is the ants' wide edge coastline roughness or porosity?

Registered 2026-10-14 22:15 NZDT, base commit `797704a` (dirty tree), **before any
`hull_width` run** (only its oracle unit test, `cargo test --release --example hull_width`,
was run: a synthetic square with two holes, expected counts hand-derived).

## Question

`W_surf` (sd of the radius of surface cells, Kapri-Dhar definition) grows as ~t^0.22-0.25 for
ants against ~t^0.10-0.13 for the rotor (`2026-10-a4-boundary-width`). The surface set is every
visited cell with an unvisited 4-neighbour, so it includes the rims of interior holes
(`notes/frontier-results.md`, P7: "not separated"). Territory fill is 0.76-0.98. Two readings:

- **H-hole (porosity).** The ants' extra width is lake/pocket rims scattered through the bulk;
  the outer coastline grows like the rotor's.
- **H-rough (interface).** The outer coastline itself roughens about twice as fast.

## Design

Instrument `examples/hull_width.rs`: exterior = unvisited cells 4-connected to the grid border;
*outer* surface cells touch the exterior, *hole* surface cells touch only enclosed unvisited
cells. Per checkpoint k = 16, 18, ..., 30 it reports A, P_all/P_outer/P_hole, number and area of
holes, W_all, W_out, the roughness of the angular profile r(theta) (512 bins, Fourier modes
m <= 2 removed) with its band-summed spectrum (bands 3-4 ... 129-256, in units of rbar^2), and
box counts of the outer cells at box sizes 1..64.

Cohort: the six A4 rules (RLR, RLRLRRRLLR, RLLLRLLRRLR, RLRLLRRLL, RLRLRRRRLR, RLLRLLRLRRRL), fresh
patched-start seeds 221-224 (24 runs, `RULE@SEED`), and rotor seeds 221-228 (8 runs), 8192^2
grid, `MAX_LOG2 = 30`. Runs that leave the grid end early and are listed, not dropped silently.
Calibration: the rotor is the reference walker; the synthetic-oracle test checks the hull split.

Estimators (fixed now): local exponent = least-squares log-log slope over k = 22, 24, 26, 28, 30
(per run); medians over runs, with between-run sd and a rule-level bootstrap (seed 20261014) for
ants. Spectrum exponent: slope of log2(band power) on band index over bands 5-8 ... 65-128
(five bands), equal to -2 zeta_loc for a self-affine profile; hull dimension D_h: slope of
log N against log(1/s) over s = 2 ... 32. All at the median over runs at k = 28 and 30.
The outermost-cell-per-bin profile is an extremal statistic and biased for small R; that bias is
the same for both walkers and is read off the rotor.

## Predictions (fixed now; not to be edited after the run)

Prior: I lean H-rough (about 60%) because the same ratio ~2 appears in the temporal and in the
radius-based fits, and holes are a small share of area (fill 0.76-0.98 is the loosest bound).

1. **Calibration.** Rotor W_out exponent lies in [0.08, 0.14]. If not, the instrument or the
   window is suspect and nothing below is interpreted.
2. **Holes are ants' business.** Median P_hole/P_all at k = 28: ants >= 3x the rotor's, and ants
   >= 0.10.
3. **Decisive.** Ants' median W_out exponent (k >= 22): >= 0.18 supports H-rough; <= 0.15
   supports H-hole (gap mostly porosity); in between is reported as mixed. The ratio
   (ants W_out exponent)/(rotor's) must be reported either way.
4. **Spectrum.** Ants' spectrum exponent zeta_loc exceeds the rotor's by >= 0.10 at k = 28 and 30
   (H-rough); under H-hole the two differ by < 0.10.
5. **Hull dimension.** Both D_h lie in [1.0, 1.4]; ants' exceeds the rotor's by >= 0.05.
6. **Decomposition check.** beta_out (log P_outer on log A, k >= 22) is within 0.03 of beta_all for
   both walkers (holes a roughly constant share of the edge). Not met means holes are a changing
   share, which would add a drifting factor to the edge in the three-factor decomposition.

## Decision rules

- 1 fails: stop, debug the instrument (compare W_all with `shape`'s Wsurf on the same specs; they
  must agree to 4 digits).
- 3 and 4 both H-rough: the wider edge is a property of the outer interface; next step is
  equal-time height correlations on the hull (KPZ-type exponents), not more windows.
- 3 and 4 both H-hole: revise the paper's edge claims to "porosity"; investigate hole statistics.
- 3 and 4 disagree, or 3 mixed: report as unresolved; do not summarise as either.

## Commands (WSL, from `/mnt/f/Code/turmite`)

```bash
export CARGO_TARGET_DIR=~/turmite-target
cargo test --release --example hull_width
cargo build --release --example hull_width
bash experiments/archive/2026-10-hull-width/scripts/run_hull.sh
uv run experiments/archive/2026-10-hull-width/scripts/hull_stats.py
```

## Status

Run and analysed 2026-10-14; band-power follow-up (README, bottom) run and corrected 2026-10-15. OPEN, not run: real-space S(dtheta) and band power vs k (needs a rerun with r(theta) dumps), larger census-sampled rule set.

## Results (2026-10-14 22:55 NZDT; predictions above unchanged)

Run: `scripts/run_hull.sh` (commit `797704a`, dirty tree; 24 ant runs, 8 rotor runs, no escapes,
k = 16..30), then `scripts/hull_stats.py` -> `results/hull_stats.txt`. Decision rule 1 cross-check:
W_all equals `shape`'s Wsurf on 160 matched (spec, k) rows to 4 digits (max diff 0.0000).

| prediction | outcome |
|---|---|
| 1 calibration: rotor W_out exponent in [0.08, 0.14] | **held**, 0.135 (sd 0.062 over 8 seeds; edge of the band) |
| 2 holes: ants P_hole/P_all >= 0.10 and >= 3x rotor | **FAILED, direction reversed:** ants 0.038, rotor 0.252 (k=28) |
| 3 ants W_out exponent (k>=22) >= 0.18 -> H-rough | **held:** 0.239 (sd 0.049, rule-bootstrap [0.220, 0.247]); rotor 0.135; ratio 1.77. W_all exponents: ants 0.239, rotor 0.130 |
| 4 spectrum zeta_loc, ants - rotor >= 0.10 | met numerically (+0.183 at k=28, +0.200 at k=30; ants 0.63/0.60, rotor 0.44/0.40), **but see below: the direction of my reasoning was wrong** |
| 5 hull dimension: ants >= rotor + 0.05, both in [1.0, 1.4] | **FAILED, reversed:** ants 1.07/1.06, rotor 1.16/1.17 |
| 6 beta_out within 0.03 of beta_all | **held:** max difference 0.017 (ants), 0.016 (rotor) |

Reading (interpretation). The ants' wide edge is **not** porosity: removing hole rims leaves its
exponent unchanged (0.239 -> 0.239), and ants have few hole-rim cells (4%). The rotor is the
holey one (25% of its surface cells are hole rims), yet its W_out and W_all exponents also agree
(0.135, 0.130), so the surface-width comparison in the paper was not biased by holes in either
walker. H-hole is rejected; H-rough, as defined by prediction 3, holds.
Prediction 4 was badly specified: a larger spectral exponent means a *smoother* profile at small
scale, not a rougher one, and box counting agrees (ants' hull dimension is lower). Together they say
the ants' outer hull has fewer small-scale kinks than the rotor's yet a larger overall width, i.e.
the extra width sits at long wavelengths (lobes, notches), not in fine roughness. I did not register
that reading, so it is a hypothesis, not a result. Caveats: 6 rules x 4 seeds (the A4 rules, chosen
earlier and not sampled from the census); the r(theta) profile is the outermost cell per bin (extremal,
misses overhangs; zeta_loc over bins 5-8..65-128 uses only 5 bands, rotor sd 0.08-0.11); the
exterior is 4-connected (diagonal channels count as closed, unchecked per the notebook assumption);
all exponents are finite-window (k >= 22); D_h over s = 2..32 is a short range.
Next: equal-time height correlations/structure function of r(theta) at fixed k (registered first),
and a larger rule sample from the census.

## Band-power ratio: long-wavelength excess (registered 2026-10-15 20:56 +13:00, base commit `da88e61`, before `scripts/hull_bands.py` was written or any `spec_bands` value was inspected)

**Scope note.** The registered "next step" above (equal-time height correlations) cannot be run on the stored data: `hull_width` saved only the band-summed
spectrum `spec_bands` (7 dyadic bands of the m-bin Fourier power of r(theta), modes m <= 2 removed, in units of rbar^2), not r(theta) itself. The band power is the Fourier-space
form of the structure function, so this is the same question asked of existing results; a real-space S(dtheta) would need a rerun with profile dumps and is **not** done here.
No new simulation. Data: `results/hull_ants.csv`, `results/hull_rotor.csv` (24 ant runs = 6 rules x 4 seeds; 8 rotor runs), k = 28 and 30 (k >= 28 so the bands have values).
The only thing I have seen of the spectrum is its fitted slope over bands 5-8..65-128 (ants steeper by +0.18 / +0.20); the per-band values have not been looked at.

**Hypothesis (H-lobe, from the unregistered reading above).** The ants' extra width relative to the rotor sits at long wavelengths. Let R_b = (median over runs of band power b, ants) / (same, rotor)
at a given k. Unit of inference for ants = rule (median over its 4 seeds first), rotor = its 8 runs.

**Predictions.**
1. R_b > 1 for the two lowest bands (3-4 and 5-8) at both k = 28 and 30, in at least 5 of the 6 rules individually (rule median vs rotor median).
2. R_b < 1 for the 65-128 band at both k, in at least 5 of 6 rules. (A steeper ants' slope forces some crossing; this checks that it happens at high, not low, wavenumber.)
3. log R_b decreases with band index: Spearman rho(band index, log R_b) <= -0.8 on the 7 bands at both k (NaN bands dropped; need >= 5).
4. The crossover band b* (first band with R_b < 1) is the same, to within one band, at k = 28 and 30.
5. Control: the rotor's own spectrum between k = 28 and 30 changes by a factor in [0.7, 1.4] per band (checks that comparing windows at k = 28/30 is stable, so a ratio of order 2 is not window noise). Rotor run-to-run sd of log band power is reported as the noise floor; any ratio claimed as "> 1" must exceed 2 sd of the log rotor median (bootstrap over its 8 runs, seed 20261014).

**Decision.**
- 1-3 all hold: the extra width is long-wavelength (lobes/notches); the follow-up is a profile-dump rerun to measure S(dtheta) and the lobe size in real space. Still observational.
- 1 fails (R_b <= 1 in a low band): the ants' extra W is not carried by the lowest wavelengths; the H-lobe reading is dropped and the discrepancy goes into `notes/open-questions-hypotheses.md`.
- 1 holds, 2 or 3 fails: report as mixed; no summary as either.
- Confounds to state with the result: the profile is the outermost cell per bin (extremal, misses overhangs); 6 rules chosen earlier, not census-sampled; finite window; band power is normalised by rbar^2 so a bigger R_b means relatively rougher, not larger in cells.

### Band-power ratio: result (2026-10-15 20:58 +13:00, commit `da88e61`; predictions above unchanged)

`uv run experiments/archive/2026-10-hull-width/scripts/hull_bands.py` -> `results/hull_bands.txt` (no simulation; 6 ant rules x 4 seeds, 8 rotor runs; bootstrap seed 20261014).

| Prediction | Outcome |
|---|---|
| 1 low bands R_b > 1 at both k in >= 5/6 rules | **HELD**: R(3-4) = 4.09 / 5.99 and R(5-8) = 2.12 / 3.08 at k = 28 / 30; 5/6 and 6/6 rules; both bands exceed 2 sd of the rotor's bootstrap median |
| 2 band 65-128 R_b < 1 at both k in >= 5/6 rules | **FAILED**: k=28 R = 0.72 (5/6 rules), k=30 R = 0.97 (3/6 rules) |
| 3 Spearman(band, log R_b) <= -0.8 at both k | **HELD**: -1.00 and -0.96 |
| 4 crossover band within one band across k | **HELD** (33-64 at k=28, 65-128 at k=30), but it moves to higher wavenumber with k |
| 5 rotor band power k=30/k=28 within [0.7, 1.4] | **FAILED**: 0.63, 0.46, 0.65, 0.56, 0.59, 0.62, 0.62 |

Decision rule: 1 and 3 hold, 2 fails -> **mixed, not summarised as H-lobe**. What the data do show: relative to the rotor the ants carry 2-6x the long-wavelength power (bands 3-4 to 17-32; exceeds the rotor noise floor
by more than 2 sd of its log median), the excess decreases monotonically with wavenumber, and the high-wavenumber deficit seen at k = 28 is gone by k = 30 (R(129-256) is still 0.62 / 0.75).
Prediction 5 failed, so the comparison is **not stable across windows**: the rotor's normalised band power drops by a factor of about 0.6 in every band from k = 28 to 30 while the ants' lowest band is nearly unchanged
(1.34e-3 -> 1.23e-3; rotor 3.3e-4 -> 2.1e-4). That is an unregistered observation: it makes R_b at low wavenumber *grow* with k (4.1 -> 6.0), i.e. the ants' long-wavelength roughness does not
decay as the rotor's does. It is consistent with the larger W exponent of the ants but is a post hoc reading from two checkpoints, so it is a lead, not a result.
Caveats: single checkpoint pair; the rotor control noise at 3-4 is large (run sd of log 0.8-1.1); the profile is the outermost cell per bin; band power is in units of rbar^2 and rbar grows;
6 rules not census-sampled; real-space S(dtheta) not computed (no profile dumps). Next (unregistered): rerun with profile dumps at k = 24..30 to get the band power as a function of k per walker
and the lobe size in real space.

### Band-power ratio: correction after review (21:24 +13:00, commit `da88e61`)

`hull_width.rs` divides the profile spectrum by rbar^2 (line 166), so band power scales as (W/R)^2. The rotor's drop of about 0.6 per band between k = 28 and 30 (factor 4 in t) is then what the measured W exponents already imply:
4^(2(0.135 - 1/3)) = 0.58 for the rotor, and 4^(2(0.239 - 1/3)) = 0.77 for the ants (observed ants' lowest-band ratio 0.92 and median about 0.75). So **prediction 5 was mis-specified** (a size-free band power is not stable across windows because W/R itself decays);
it still failed as registered and the verdict is not changed. The "lead" above (ants' long-wavelength power not decaying as the rotor's does, R_b growing with k) only restates the W-exponent gap between the walkers that was measured earlier;
it is not an independent finding. The independent content of the band analysis is the within-k shape: R_b decreasing monotonically with wavenumber at both k (predictions 1 and 3).
