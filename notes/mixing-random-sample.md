# Mixing test on a random sample of rules

Written 2026-10-12, before running. Reason: the earlier mixing sample
(experiments/archive/2026-10-mixing/results/mix_rules.txt, 49 rules) has no recorded selection procedure.

Protocol: draw 40 rules uniformly at random (numpy default_rng seed 20261012)
from the core class (blob, 0.30 < alpha_w < 0.37, not bursty, in
experiments/archive/2026-10-probe-growth-census/results/probe_summary.csv); dump each at 2^24 steps (examples/dump.rs, as before);
run experiments/_lib/mixing.py unchanged; summarise as in experiments/archive/2026-10-mixing/scripts/mixing_stats.py.
Driver: research-outputs/scholarly-articles/cube-root-growth/mixing_random.py. Output: experiments/archive/2026-10-mixing/results/mixing_random.csv.

Predictions (from the earlier sample, so a replication test):
- P1. 60-85% of rules have colour_tv < 0.05 (earlier: 24/33 = 73%).
- P2. For those, median measured/predicted MSD slope in [0.95, 1.10].
- P3. For the rest, the ratio departs more (median > 1.1).
Falsifier: fewer than 50% uniform, or median ratio for uniform rules outside
[0.9, 1.2]; then the "well-mixed for most rules" statement is a property of
the earlier convenience sample.

## Result (2026-10-12)

40 random core rules (experiments/archive/2026-10-mixing/results/mixing_random_rules.txt, experiments/archive/2026-10-mixing/results/mixing_random.csv).
35/40 (87.5%) near-uniform: P1 missed on the high side (predicted 60-85%).
Uniform rules: measured/predicted MSD slope min 0.845, median 1.005, max 1.575:
P2 holds. Other 5: median ratio 1.30: P3 holds. Falsifier not triggered.
Reproduce: `uv run research-outputs/scholarly-articles/cube-root-growth/mixing_random.py` (needs `cargo build --release --example dump`).
