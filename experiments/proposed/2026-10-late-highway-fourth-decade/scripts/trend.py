"""What the existing three decades say about the trend in late-highway yield, and what a fourth would add.

Model: highways in decade d (d = 0 for (1e8,1e9], 1, 2, 3) ~ Poisson(n_d * p0 * f**d), n_d = survivors entering the decade.
f = 1 is "flat". Poisson approximates the binomial at p ~ 1.7%. Profile likelihood in f (p0 maximised in closed form).
Counts are the corrected genuine yields of experiments/archive/2026-10-late-highway-board-check/README.md.
Part 2 repeats the fit counting highways with identical onset once (rules sharing a prefix replay one trajectory).
Part 3 simulates adding decade 3 with m run rules (numpy seed fixed) and reports the 95% interval width for f.
Run: uv run --frozen experiments/proposed/2026-10-late-highway-fourth-decade/scripts/trend.py
"""
import re, pathlib
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[4]
GRID = np.linspace(0.05, 3.0, 1200)  # candidate f values
CHI2_95 = 1.9207  # chi2(1)/2 at 0.95


def profile(k, n, d):
    """Profile log-likelihood over GRID; returns (loglik array, f_hat, (lo, hi))."""
    k, n, d = map(np.asarray, (k, n, d))
    w = n[None, :] * GRID[:, None] ** d[None, :]
    p0 = k.sum() / w.sum(axis=1)
    ll = (k * np.log(p0[:, None] * w / n * n + 1e-300)).sum(axis=1) - (p0[:, None] * w).sum(axis=1)
    ok = ll >= ll.max() - CHI2_95
    return ll, GRID[ll.argmax()], (GRID[ok][0], GRID[ok][-1]) if ok.any() else (np.nan, np.nan)


def genuine_onsets():
    """Onsets of genuine highways: decade 0 from highway_stats.txt, decades 1-2 from classify.txt (non-filler, non-ray)."""
    hs = (ROOT / "experiments/archive/2026-10-highways-unresolved-rules-1e10-1e11/results/highway_stats.txt").read_text()
    d0 = [int(x) for x in re.search(r"onsets of those: \[([\d, ]+)\]", hs).group(1).split(",")]
    out = {0: d0, 1: [], 2: []}
    for line in (ROOT / "experiments/archive/2026-10-late-highway-board-check/results/classify.txt").read_text().splitlines():
        c = [x.strip() for x in line.strip("│ ").split("┆")]
        if len(c) >= 8 and c[0] in ("(1e9,1e10]", "(1e10,1e11]") and c[-1] == "false" and c[1] != "RLLLRLRRR":
            out[1 if c[0] == "(1e9,1e10]" else 2].append(round(float(c[-4]) * 2**31))
    return out


def distinct(onsets, tol=2e-4):
    s = sorted(onsets)
    return sum(1 for i, x in enumerate(s) if i == 0 or (x - s[i - 1]) / x > tol)


N = [854, 807, 732]
K = [12, 16, 12]
d3 = np.arange(3)
ll, fh, (lo, hi) = profile(K, N, d3)
print(f"decades 0-2 as counted: k={K}  f_hat={fh:.2f}  95% interval [{lo:.2f}, {hi:.2f}]  (f=1 is flat; LR vs flat: "
      f"{2*(ll.max()-ll[np.abs(GRID-1).argmin()]):.2f} on 1 df)")
on = genuine_onsets()
Kd = [distinct(on[i]) for i in range(3)]
print(f"genuine highways by decade (listed): {[len(on[i]) for i in range(3)]}, distinct onsets: {Kd}")
ll2, fh2, (lo2, hi2) = profile(Kd, N, d3)
print(f"decades 0-2 distinct onsets only: f_hat={fh2:.2f}  95% interval [{lo2:.2f}, {hi2:.2f}]")

rng = np.random.default_rng(20261025)
print("\nProjection: add decade 3 with m rules run to 1e12 (2000 simulated outcomes per row, seed 20261025)")
print(f"{'truth f':>8} {'m':>4} {'median 95% interval':>22} {'median width':>13} {'P(interval excludes 1)':>23}")
for ftrue in (1.0, 0.5):
    p0 = sum(K) / sum(N) / np.mean([ftrue ** x for x in range(3)])  # keep the observed pooled level
    for m in (0, 48, 200, 702):
        wid, los, his, excl = [], [], [], 0
        for _ in range(2000):
            k = [rng.poisson(N[i] * p0 * ftrue ** i) for i in range(3)]
            n = list(N)
            if m:
                k.append(rng.poisson(m * p0 * ftrue ** 3)); n.append(m)
            _, _, (a, b) = profile(k, n, np.arange(len(k)))
            wid.append(b - a); los.append(a); his.append(b); excl += not (a <= 1 <= b)
        print(f"{ftrue:>8} {m:>4} {f'[{np.median(los):.2f}, {np.median(his):.2f}]':>22} {np.median(wid):>13.2f} {excl/2000:>23.2f}")

# ---- Part 4: the whole census, decades 1e1..1e11 (results/hazard_by_decade.csv from hazard_all_decades.py) ----
import polars as pl
hz = pl.read_csv(ROOT / "experiments/proposed/2026-10-late-highway-fourth-decade/results/hazard_by_decade.csv")
print("\nPart 4 (EXPLORATORY: windows chosen after seeing the table; shown for sensitivity). Hazard = highways / at-risk per decade of onset.")
print(f"{'decades (k)':>12} {'n decades':>9} {'f_hat':>6} {'95% interval':>14} {'p at last decade':>17} {'predicted next decade':>22}")
for a, b in ((2, 10), (3, 10), (1, 10), (5, 10), (8, 10)):
    w = hz.filter((pl.col("k") >= a) & (pl.col("k") <= b))
    k = w["highways"].to_numpy(); n = w["at_risk"].to_numpy(); d = (w["k"].to_numpy() - a)
    _, fh_, (l_, h_) = profile(k, n, d)
    p0 = k.sum() / (n * fh_ ** d).sum()
    last = p0 * fh_ ** d[-1]
    print(f"{f'{a}..{b}':>12} {len(k):>9} {fh_:>6.2f} {f'[{l_:.2f}, {h_:.2f}]':>14} {100*last:>16.2f}% {100*last*fh_:>13.2f}% ({702*last*fh_:.1f} of 702)")
