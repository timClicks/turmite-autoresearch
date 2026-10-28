# Output schema (proposed; not implemented)

`dumps/loops.csv` (gitignored, bulk): one row per (rule spec `RULE@SEED`, window k in 20..26). Columns, in order:

`rule, k, t, steps, escaped, area, perimeter, new_cells, boundary_steps,`
`loop_lead_b, loop_lead_i, loop_other_b, loop_other_i,`   loop steps by kind, on boundary (b) / interior (i) cells
`entry_lead_b, entry_lead_i, entry_other_b, entry_other_i,`   loop entries, same split
`laps_1, ..., laps_8, laps_gt8`   completed-run counts by lap length, lead-colour loops

The first nine columns must reproduce the corresponding `probe` CSV columns for the same spec (identity test). Derived:
loop_frac = (sum of the four loop_*) / steps.

`results/loops_per_rule.csv` (committed, small): per-rule aggregates the notebook reads, with the command, commit and seed in a header line.

**Implemented 2026-10-16 (appended; the text above is the original proposal).** `dumps/loops_<cohort|mutants>.csv` has exactly the proposed columns, with two differences found
at analysis time: (1) `k` is the window index of `probe_walker` (steps in [2^k, 2^(k+1)), t_end = 2^(k+1)), NOT the probe CSV's `k`, which is log2(t_end) = window index + 1; join on `t`.
(2) `steps` = 2^k (as in `per_rule`'s `t // 2`). Loop-step definitions are in the header comment of `examples/kappa_square_loop_sampler.rs`.
`results/loops_per_rule.csv` has a `#` header line (read with `comment_prefix="#"`); columns include the per-rule means of each mediator at probe-CSV k = 26.
