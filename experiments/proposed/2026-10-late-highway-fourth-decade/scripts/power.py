"""Power and cost of the fourth-decade late-highway yield test (Q19).

Pure arithmetic (no simulation): given the three corrected decade yields, how many of the 702 survivors must
run to 1e12 steps to tell a flat yield from a falling one, and what does that cost in CPU time?
Run: uv run --frozen experiments/proposed/2026-10-late-highway-fourth-decade/scripts/power.py
"""
from scipy.stats import binom

# Corrected genuine highways / survivors per decade (experiments/archive/2026-10-late-highway-board-check/README.md).
DECADES = {"(1e8,1e9]": (12, 854), "(1e9,1e10]": (16, 807), "(1e10,1e11]": (12, 732)}
k, n = (sum(v[i] for v in DECADES.values()) for i in (0, 1))
P0 = k / n  # pooled flat-yield estimate, the registered H-flat value
SURVIVORS = 702
ALPHA = 0.05
STEPS = 1e12
RATES = (1.0e8, 1.5e8, 2.0e8)  # steps/s/core, spanning the measured dense and tiled range

print(f"pooled yield {k}/{n} = {P0:.4f}")
print(f"{'m':>4} {'E[flat]':>8} {'cut':>4} {'power x0.7':>10} {'power x0.5':>10} {'power x0.3':>10}   core-hours at 2/1.5/1 e8")
for m in (48, 100, 200, 350, 702):
    # One-sided exact test: reject H-flat when X <= cut with P(X <= cut | p0) <= ALPHA.
    cut = max((c for c in range(m + 1) if binom.cdf(c, m, P0) <= ALPHA), default=-1)
    pw = [binom.cdf(cut, m, P0 * f) if cut >= 0 else 0.0 for f in (0.7, 0.5, 0.3)]
    hrs = [m * STEPS / r / 3600 for r in reversed(RATES)]
    print(f"{m:>4} {m*P0:>8.1f} {cut:>4} {pw[0]:>10.2f} {pw[1]:>10.2f} {pw[2]:>10.2f}   " + " / ".join(f"{h:,.0f}" for h in hrs))
