# Walker comparisons: growth and boundary width

## Registered 2026-10-13 23:27 NZDT, before the refit

Existing A4/A4c time slopes have already been inspected. This is a prospective
analysis specification on existing data, not a blind prediction of unseen data.
Base commit: `91f312f925b3234a3d3f0b1390598df81e170750`; working tree has
uncommitted research work. No existing results will be overwritten.

Fit log Wsurf against log R per trajectory, with primary R = sqrt(A/pi)
and sensitivity R = sqrt(rg2) and rbar. Use pooled A4 and A4c shape files;
primary window k=22..32 (six checkpoints shared by both cohorts), sensitivity
k=26..32 and A4c-only k=26..34. Keep every complete positive trajectory,
report missing/excluded trajectories, between-seed sd, and ant rule means
separately from pooled seeds. No data-dependent growth-band filtering.

Prediction: rotor trajectory slope lies in [0.30, 0.37], as suggested by
W proportional to R^(1/3). Competing time exponent 1/8 with radius exponent
1/3 implies 3/8, so also report distance from 1/3 and 3/8. Ant slope lies
in [0.60, 0.80], and the ant/rotor slope ratio in [1.7, 2.3]. These are
finite-window tests; failure of the bands falsifies these predictions only.
Bootstrap rotor seeds and ant rules (clustered seeds) 2000 times with seed
20261013 for mean intervals. This trajectory exponent is NOT the spatial
roughness exponent from a height correlation function. Global shape and
anisotropy contribute to Wsurf; neither agreement nor a ratio proves KPZ.

Instrument check: synthetic R=t^(1/3), W=R^(1/3) must recover 1/3;
W=t^(1/8) must recover 3/8. Rotor refit is the empirical calibration;
its spatial roughness exponent has no assumed known oracle here.

## Stochastic memory experiment: model choice pending

Standard once-excited walks bias first departures in a fixed direction,
then use simple random walk departures thereafter (Benjamini & Wilson,
https://arxiv.org/abs/math/0302271). This introduces drift and anisotropy.
An isotropic edge-reinforced walk is a cleaner comparator for persistent
board memory, but needs edge weights rather than the existing u8 cell API.
No prediction or measurement for this arm is registered yet: specify the
model and reinforcement strength before simulating. A negative result for
one memory model cannot rule out memory as necessary for ant scaling.

## Registered memory pilot, 2026-10-13 (before simulation)

User selected all three models, simplest first. `cookie:B:SEED` uses one
east-pointing cookie per site: first departure chooses east with probability
B, otherwise chooses a uniform neighbour. Revisit departures are uniform.
`rcookie:B:SEED` replaces east with a seeded i.i.d. uniform arrow per site.
B=0.25 and 0.75. This randomly oriented variant is our specified experimental
model, not the standard directional excited walk.
`errw:I:SEED` starts every undirected edge at weight 1, chooses a neighbour
proportional to edge weight, then adds I to that edge, shared by both
directions. I=1 and 4 (equivalent initial weights 1 and 1/4 in conventional
unit-increment notation). Definition background:
https://arxiv.org/abs/math/0608220.

Run each plus random walk and rotor controls for seeds 301..308, to 2^20,
grid 8192, blank start except random cookies/rotors. Primary fits use complete
k=14..18 checkpoints; sensitivity k=16..20. Report every escape and excluded
fit; do not treat survivor-only averages as representative of a censored
family. kappa=(boundary_steps/window_steps)/(perimeter/area), using the
end-window geometry, reported at k=18 and k=20. Between-seed sd required.

Predictions (finite-window, deliberately falsifiable): random walk area
slope in [0.85,1.05], rotor [0.63,0.75]; directional cookies area slope >0.8
and at least one escape by 2^20; random cookies at B=.25 area slope >0.8,
whereas B=.75 and edge reinforcement I=1 produce slopes in [0.60,0.75]
with kappa in [0.5,3] at k=18. Strong edge reinforcement I=4 reduces mean
area relative to I=1 at k=18. Memory-sufficiency evidence requires both the
growth and kappa predictions and replication in the late window with no
escape bias; the pilot cannot establish an asymptotic universality class.

Property checks compare seeded trajectories to independent sparse reference
implementations, and zero-bias cookies exactly match the random-walk probe.
Run the full release test suite before simulations. Per-spec checkpoint
files and .done markers make the sweep resumable; a finished spec is skipped.

## Refit results (appended; predictions unchanged)

Recipe: `export UV_PROJECT_ENVIRONMENT=$HOME/.venvs/turmite UV_LINK_MODE=copy;
uv run experiments/archive/2026-10-w-width-radius-refit/scripts/width_radius_refit.py > experiments/archive/2026-10-w-width-radius-refit/results/width_radius_refit.log`, in WSL from
`/mnt/f/Code/turmite`. Script: `experiments/archive/2026-10-w-width-radius-refit/scripts/width_radius_refit.py`; machine-readable
fits, input hashes, commit and seed: `experiments/archive/2026-10-w-width-radius-refit/results/width_radius_refit.json`.
Synthetic instrument checks passed. All trajectories in each cohort completed
their specified window, and none were excluded.

Primary k=22..32: 14 rotor seeds, 36 ant runs across 6 rules (6 seeds/rule).
Rotor Req slope 0.4010, seed sd 0.0733, mean bootstrap 95% interval
[0.3657,0.4374]. Ant rule-mean slope 0.7138, between-rule sd 0.0663,
RMS within-rule seed sd 0.1337, rule bootstrap interval [0.6638,0.7609].
Ratio 1.780. Rotor registered band fails; ant and ratio bands pass.
Rotor mean time slope 0.1359, radius time slope 0.3387: the radius refit
is closer to 3/8 (distance 0.0260) than 1/3 (distance 0.0677). The primary
bootstrap interval excludes 1/3 but includes 3/8; this is finite-window
evidence, not an asymptotic proof.

Sensitivity k=26..32: rotor 0.3893 (sd 0.0849), ant 0.6851 (RMS
within-rule sd 0.2103), ratio 1.760. A4c-only k=26..34: 6 rotor seeds and
12 ant runs (2 seeds/rule), rotor 0.3949 (sd 0.0684), ant 0.6369 (RMS
within-rule sd 0.1948), ratio 1.613; ratio band fails in this window.
Rg/rbar instead of Req changes means by at most 0.005 in these windows.
Thus R^(1/3) rotor growth is not supported by the primary fit, and the
exact factor-two slope claim is not stable across cohorts/windows. Local
height correlations and removal of global shape modes remain necessary
before interpreting any trajectory slope as spatial roughness.

## Memory pilot results (appended; predictions unchanged)

All 64 runs finished or reported grid escape. Driver:
`export UV_PROJECT_ENVIRONMENT=$HOME/.venvs/turmite UV_LINK_MODE=copy;
uv run experiments/archive/2026-10-memory-walkers/scripts/memory_walkers_pilot.py $HOME/turmite-target-memory/release/probe`.
Build: `CARGO_TARGET_DIR=$HOME/turmite-target-memory cargo build --release --bin probe`.
Run log: `experiments/archive/2026-10-memory-walkers/results/memory_walkers_pilot.log`. Per-spec CSVs, hashes, .done markers,
source/binary hashes and exact recipe: `experiments/archive/2026-10-memory-walkers/results/memory_walkers_pilot/recipe.json`.
Analysis: `uv run experiments/archive/2026-10-memory-walkers/scripts/memory_walkers_pilot.py --analyse`, producing
`combined.csv` and `summary.json` in that directory. Full `cargo test --release`
passed (including independent reference comparisons); log `experiments/archive/2026-10-memory-walkers/results/memory_walkers_tests.log`.

Primary k=14..18, eight complete seeds per uncensored row; numbers are mean
plus/minus between-seed sd, kappa evaluated at k=18:

| Model | Area slope | kappa |
|---|---|---|
| Random walk | 0.924 +/- 0.043 | 1.350 +/- 0.082 |
| Rotor | 0.740 +/- 0.027 | 1.845 +/- 0.118 |
| Random cookies B=.25 | 0.942 +/- 0.047 | 1.327 +/- 0.075 |
| Random cookies B=.75 | 0.920 +/- 0.044 | 1.293 +/- 0.094 |
| Edge reinforcement I=1 | 0.698 +/- 0.303 | 0.312 +/- 0.132 |
| Edge reinforcement I=4 | 0.187 +/- 0.092 | 0.328 +/- 0.447 |

Both directional-cookie groups: 8/8 escaped before completing k=18; no
registered-window fit is available. Their area-slope prediction is untested,
not confirmed by extrapolating survivors; the escape prediction passed.
Both calibration area bands passed, but rotor bias is +0.074 relative to 2/3
in this early window (+0.048 over k=16..20). Do not subtract this bias from
other walkers as though their finite-time effects were identical.
Random-cookie B=.25 prediction passed; B=.75 growth prediction failed.
Weak reinforcement passed the growth band but failed the kappa band.
Strong reinforcement mean area at k=18 is 49.75 versus 4830.125 for I=1,
so the suppression prediction passed. The tiny territories and large seed
variation make strong-reinforcement kappa especially unstable.

Late k=16..20: random-cookie slopes 0.926 +/- 0.026 and 0.922 +/- 0.039;
random walk 0.921 +/- 0.027; rotor 0.715 +/- 0.019. I=1 slope
0.701 +/- 0.277, kappa falls to 0.155 +/- 0.084; I=4 slope
0.216 +/- 0.096. None reproduces the joint growth/kappa prediction in both
windows. Board memory is not sufficient in these tested settings. Weak
reinforcement's mean slope is interesting, but its broad seed variation and
nonstationary boundary occupancy prevent a cube-root universality claim.

## Illustrations and manuscript update

User requested trajectory plots and manuscript updates. Equal-step paths:
`CARGO_TARGET_DIR=$HOME/turmite-target-memory cargo run --release --example memory_paths -- 301 16 > experiments/archive/2026-10-memory-walkers/dumps/memory_paths.csv`.
Seed 301 selected before inspecting paths; 65,536 steps, ant RLR blank start.
The raw path dump is gitignored. `uv run research-outputs/scholarly-articles/cube-root-growth/memory_figures.py` creates
`research-outputs/scholarly-articles/cube-root-growth/fig/memory_paths.pdf` and `memory_growth.pdf` (plus PNG previews), with
input/source hashes in `research-outputs/scholarly-articles/cube-root-growth/fig/memory_recipe.json`. Panels use equal aspect
except the labelled directional-cookie panels, whose transverse axis is
expanded for legibility; cell coordinates show actual scales and extents.
Growth plots show individual seeds and means; directional curves stop at
censoring and terminal counts are labelled. No missing seeds are imputed.
Manuscript `research-outputs/scholarly-articles/cube-root-growth/main.typ` adds these figures, a pilot table and the radius
refit, and weakens the inference that a failed memoryless control proves
memory necessary. New typed numbers are traceable to the two summary JSONs.

Final verification: `typst compile --root . research-outputs/scholarly-articles/cube-root-growth/main.typ research-outputs/scholarly-articles/cube-root-growth/main.pdf`
succeeded; changed manuscript pages 11, 12 and 16 were rendered with Poppler
and visually inspected, with no clipping or overlapping labels. The final
full `cargo test --release` passed after the buffered illustration exporter
and fixed property-test seed were added. Re-running both analyses produced
identical SHA256 hashes (`experiments/archive/2026-10-w-width-radius-refit/results/width_radius_refit.verify` and
`experiments/archive/2026-10-memory-walkers/results/memory_walkers_pilot/analysis.verify`). Text-source whitespace checks
passed (`experiments/archive/2026-10-memory-walkers/results/memory_diff_check.log`); an initial repository-wide check tried
to interpret the generated binary PDF as text, so it was rerun on source
files only. No dependencies changed and no commit was made.
