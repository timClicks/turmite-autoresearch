# Frontier status: items in research-frontier.md

Started 2026-10-12. Goal: every item investigated, except item 9 (knockout map; another agent owns it and `experiments/2026-10-12-knockout-maps/knock/`,
`experiments/2026-10-12-knockout-maps/scripts/knockout*.py`, `examples/knock.rs`, `notes/knockout-map-hypotheses.md`; I only read their output files).
All results, hypotheses (timestamped before runs), commands and corrections: `notes/frontier-results.md` (append-only log).
Environment: WSL, `CARGO_TARGET_DIR=~/turmite-target-frontier`, 2-3 rayon threads; uncommitted tree on HEAD bbaa8c8.
`bash experiments/2026-10-13-census-sweeps/scripts/regen_frontier_stats.sh` regenerates every analysis text output from the raw data (checked: two runs give identical bytes).
Bar for "investigated": timestamped hypothesis with predictions; experiment (pilot allowed for L items, limits stated); result including nulls; command.

| # | Item | Status | Verdict (one line) |
|---|------|--------|---------|
| 1 | P1-P5 on ants | done (existing paper results re-checked + P2.1) | P5 is an identity, not a test; mechanism tests are P2.1 (supported) and mixing (24/33 rules) |
| 2 | persistent-walk MSD | done (+ calibration added) | estimator accurate to 1% (q<=0.7), +8% at q=0.9 |
| 3 | why c ~ 0.44 | done | letters 1-2 explain 75% of c variance (R on young colours lowers c); seed noise of c is 0.0006 |
| 4 | exponent exactly 1/3? | done (11 rules x 24 seeds to 2^30, rotor-calibrated) | 6 of 11 rules match the rotor's finite-time value (0.677), 5 do not (0.660 to 0.696); asymptote undecided; one rule non-self-averaging |
| 5 | limit shape | done | round (aniso 0.07), CV falls (9/11), visit density = cone 3(1-r/R) for ants AND rotor to a few % |
| 6 | rotor reduction | pilot done | no peak at n visits (rotor 0.93, ants 0.02-0.07): no lead; ants overdispersed |
| 7 | boundary-width exponent | done | ants 0.25-0.27 at 2^28 vs rotor 0.13-0.16 (same estimator): wider edge, class not decided |
| 8 | edge exponent 0.52 | done | drifts toward 0.5 (0.51-0.52 at k26-28), not established to be exactly 0.5; RLR not converged |
| 9 | knockout map | SKIPPED (other agent) | cross-check from my side: hot tiles are rich in rare-colour cells (partial rho 0.41-0.48) |
| 10 | 1x1 refinement | done (own single-cell scan on top of the knockout agent refine3/5 data; `examples/cell1.rs`) | one cell can cost 4-5% of the tether (null p99 1-2%); 3 cells reproduce the 3x3 effect, saturating ~0.15 (5x5 level); no closed cycle or minimal object, locally diffuse region; rare-colour cells not minimal (earlier null) |
| 11 | bound state | done | statistical attractor: 1-100 flips never lose the home, damage spreads, 700 flips (~10%) always do |
| 12 | formation | done (method changed, noted) | no detectable formation event: real-field spread is flat (11.8 -> 14.4) while the cup grows |
| 13 | age dependence | done | critical corrupted *fraction*, not count, is age independent (H13a falsified) |
| 14 | carrier test | done (+ 24-rule generalisation) | rare colours are critical in all tested tethered rules (swap ratio ~2, recolour ~1.3); parity is not |
| 15 | how many hard | done (560 log-class rules; cutoff corrected) | hardness is graded and bimodal in the size-free measure (35% keep / 38% cup-wide / 27% between); tracks home size |
| 16 | graded home | done | graded, no threshold (10-90% width 0.25-0.5), per-seed outcomes not bimodal |
| 17 | unresolved 854 | done (807 rules to 1e10) | 38 new highways (4.7%) in (1e9,1e10], pre-registered ~1% falsified; 28 of them in onset clusters (shared-prefix rules, probably ~10 independent events) **[Corrected 2026-10-21: 22 of the 38 (1e9,1e10] and 4+ of the 16 (1e10,1e11] "highways" are board artefacts; genuine yields 1.98% and 0.68-1.64% (1.64% if the 7 pending rechecks confirm); see `experiments/2026-10-21-late-highway-board-check/README.md`.]** |
| 18 | onset-time distribution | done (corrected) | flat per decade (slope +0.015 +- 0.026), last decade 11 vs 17.4 expected (p = 0.07) |
| 19 | highway catalogue | done | 96% diagonal, period always even, period independent of n (prediction falsified), period 18 = 22% |
| 20 | chaos vs highway predictors | done | CV AUC 0.70: weak |
| 21 | slow-growth outliers | done (68 outliers + 30 controls x 12 seeds) | outliers are real: only 17% / 34% regress; slope of re-measure on census 0.81 |
| 22 | tethered drift | done, downgraded | v/D agrees with the decay length for all five rules, but that is close to an identity (not discriminating) |
| 23 | rule equivalences | done | mirror exact; repeats u^k identical to u (52 census rules, no effect) |
| 24 | other grids | done (hex + triangular) | area exponent: hex 0.712, triangular 0.676, square 0.682 (same window); cube-root class on all three |
| 25 | turmites | done (65536 tables, 2 states x 2 colours) | 85% of the 2290 chaotic growers within 0.1 of 2/3 (median 0.70 at 2^26); separate exact sqrt(t) cluster (1560 tables) |
| 26 | randomised variants | done | random background: radius exponent 0.47; noise: cube root survives eps <= 0.1, class changes between 0.1 and 0.6 |
| 27 | many ants | done | exponent unchanged; A_m(t) ~ A_1(m t) within 0.87-1.23 |
| 28 | higher dimensions | done (1416 rules to 2^24, 24 to 2^28) | extent exp 0.245, volume exp 0.788 at k24-28: consistent with 1/4 and 3/4; 3D rotor is transient (no calibration) |
| 29 | literature | done | B-R&P prove a convex limit, not a disc; d/(d+1) is only a lower bound; no proof route for reversible ants |
| 30 | heavier statistics | done | between-seed sds tabulated; compute_numbers fails loudly; numbers.json reproduces bit for bit |
| 31 | faster ant | done | lean ant 2.1x, identical results (4000-case proptest + production-scale spot check) |
| 32 | web demo | done | cup overlay in web/ with live c, kappa, P/A; checks vs Rust pass |

New unexplained findings (also in `notes/open-questions-hypotheses.md`): 28 discrete home types shared by 556 tethered rules (spread values equal to 0.3%);
rare colours critical in every tethered rule; ants' visit density equals the rotor's cone; RRLLLLLLR non-self-averaging.
