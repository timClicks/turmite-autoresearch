# /// script
# dependencies = ["polars", "numpy"]
# ///
"""B5: highway onsets in (1e10, 1e11] for a 240-rule unbiased sample of the rules still unresolved at 1e10 (experiments/archive/2026-10-highways-unresolved-rules-1e10-1e11/results/h1e11/chunk_*.csv with .done markers).
Decision rule and pre-stated expectations: notes/frontier-2026-10-13-results.md. Scales the Poisson expectations to the number of rules actually completed.
usage: uv run experiments/archive/2026-10-b5-late-highways/scripts/b5_stats.py [FIRST_CHUNK]   (20 = the 492-rule extension; default all 61 chunks = all 732 survivors)"""
import glob, math, re, sys, numpy as np, polars as pl
FIRST = int(sys.argv[1]) if len(sys.argv) > 1 else 0  # first chunk index to include (20 = the 492-rule extension only)
files = [f for f in sorted(glob.glob("experiments/archive/2026-10-highways-unresolved-rules-1e10-1e11/results/h1e11/chunk_*.csv")) if glob.glob(f.replace(".csv", ".done")) and int(re.search(r"chunk_([0-9]+)", f).group(1)) >= FIRST]
d = pl.concat([pl.read_csv(f, schema_overrides={"period": pl.Utf8, "dx": pl.Utf8, "dy": pl.Utf8, "onset": pl.Utf8, "tail_period": pl.Utf8}) for f in files])
N = d.height
hw = d.filter(pl.col("period").is_not_null() & (pl.col("period") != "")).with_columns(onset_i=pl.col("onset").cast(pl.Float64))
esc = d.filter((pl.col("stop") == "escaped") & (pl.col("period").is_null() | (pl.col("period") == "")))
bud = d.filter(pl.col("stop") == "budget")
print(f"chunks complete: {len(files)} (chunk index >= {FIRST}; 61 exist, 12 rules each); rules: {N}; still unresolved at 1e11: {bud.height}; new highways: {hw.height}; escaped the 32768 board without a recognised highway: {esc.height}")
def pois_cdf(k, mu): return sum(math.exp(-mu) * mu ** i / math.factorial(i) for i in range(0, k + 1))
def pois_sf(k, mu): return 1 - pois_cdf(k - 1, mu)
mu_flat, mu_fall = 0.047 * N, 0.01 * N
print(f"flat rate (4.7% of survivors per decade) expects {mu_flat:.1f}; falling rate (1%) expects {mu_fall:.1f}")
print(f"observed {hw.height}: P(X <= obs | flat) = {pois_cdf(hw.height, mu_flat):.3f}; P(X >= obs | falling) = {pois_sf(hw.height, mu_fall):.3f}; P(X >= obs | flat) = {pois_sf(hw.height, mu_flat):.3f}")
rate = hw.height / N; se = math.sqrt(max(hw.height, 1)) / N
print(f"rate per decade among survivors: {100*rate:.1f}% (+- {100*se:.1f}% Poisson); the 10^10 decade had 38/807 = 4.7% (previous decades 11-26 per decade out of ~850)")
print("\nnew highways (rule, onset, period, drift):")
for r in hw.sort("onset_i").iter_rows(named=True): print(f"  {r['rule']:14s} onset {float(r['onset']):.4g}  period {r['period']}  dx,dy {r['dx']},{r['dy']}  n={r['n']}")
print("\nescaped without highway:", [(r["rule"], r["steps"]) for r in esc.iter_rows(named=True)])
# escape (breakout) rate, for comparison with the 1e10 run (37 of 807 = 4.6%)
print(f"escaped-without-highway rate {100*esc.height/N:.1f}% of this sample over (1e10, 1e11] (the 10^10 run had 4.6% over (1e9, 1e10])")
# prefix families: do rules sharing a prefix share onset times? uses onsets from the 10^10 run (38) plus the new ones
old = pl.read_csv("experiments/archive/2026-10-highways-unresolved-rules-1e10-1e11/results/h1e10_stats.txt", has_header=False, separator="\x00", infer_schema_length=0) if False else None
import re, ast
txt = open("experiments/archive/2026-10-highways-unresolved-rules-1e10-1e11/results/h1e10_stats.txt").read()
m = re.search(r"highways found: (\[.*?\])\n", txt, re.S)
old_hw = ast.literal_eval(m.group(1)) if m else []
rows = [(r[0], float(r[5])) for r in old_hw] + [(r["rule"], float(r["onset"])) for r in hw.iter_rows(named=True)]
print(f"\nprefix test on {len(rows)} highway onsets (38 from the 10^10 run + new): median |delta log10 onset| for pairs sharing the first L letters vs pairs that do not")
for L in (4, 6, 8):
    same, diff = [], []
    for i in range(len(rows)):
        for j in range(i + 1, len(rows)):
            (same if rows[i][0][:L] == rows[j][0][:L] and len(rows[i][0]) >= L and len(rows[j][0]) >= L else diff).append(abs(math.log10(rows[i][1]) - math.log10(rows[j][1])))
    if same: print(f"  L={L}: sharing pairs {len(same)}, median {np.median(same):.4f}; non-sharing pairs {len(diff)}, median {np.median(diff):.4f}; ratio {np.median(same)/np.median(diff):.3f}")
