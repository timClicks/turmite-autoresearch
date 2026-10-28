# Hidden-phase pilot results

gates failed; capped conditional effects only; mechanistic comparison unresolved

Paired start bootstrap, four starts per rule; intervals do not measure between-rule uncertainty.

| Rule | Area | k=0 effect | k=1 effect (seed SD) | Ratio [95% interval] | k=1 read edits | P1 cell |
|---|---:|---:|---:|---:|---:|---|
| RLLLLRLLRLRL | 4096 | 6.476 | 3.059 (0.873) | 0.472 [0.377, 0.548] | 0.820 | False |
| RLLLLRLLRLRL | 16384 | 7.184 | 3.802 (0.579) | 0.529 [0.468, 0.565] | 0.817 | True |
| RLLLRRLRLL | 4096 | 9.570 | 3.082 (0.259) | 0.322 [0.264, 0.384] | 0.755 | False |
| RLLLRRLRLL | 16384 | 11.537 | 7.141 (2.573) | 0.619 [0.484, 0.727] | 0.773 | True |
| RLLRRLLLLLLL | 4096 | 8.451 | 4.340 (0.458) | 0.514 [0.480, 0.540] | 0.784 | True |
| RLLRRLLLLLLL | 16384 | 8.936 | 5.076 (0.704) | 0.568 [0.521, 0.619] | 0.783 | True |

Effects are mean absolute log2 capped return-time ratios, with equal start weights.

## Eligibility

```json
{
  "departures": 9680,
  "short": 9438,
  "eligible_long": 242,
  "overflow": 0,
  "sampled": 160,
  "gap_or_quota": 82,
  "unfinished": 0,
  "completed_time": 1141585,
  "overflow_time": 0,
  "unfinished_time": 0
}
```

## Gates

```json
{
  "all_starts_complete": true,
  "eight_departures_each": false,
  "baseline_censoring_below_one_percent": true,
  "each_arm_censoring_at_most_one_percent": true,
  "turn_map_edit_support": true,
  "equivalent_phase_sham": true,
  "prefix_guarantee": true
}
```

## Replay censoring

```json
{
  "0": {
    "censored": 0,
    "n": 640
  },
  "1": {
    "censored": 0,
    "n": 640
  },
  "2": {
    "censored": 0,
    "n": 640
  },
  "4": {
    "censored": 0,
    "n": 640
  },
  "n": {
    "censored": 0,
    "n": 640
  }
}
```

The first long departures are selected, not a random or time-representative sample.
Capped effects do not estimate uncensored means. Sensitivity is not prediction or a growth mechanism.
