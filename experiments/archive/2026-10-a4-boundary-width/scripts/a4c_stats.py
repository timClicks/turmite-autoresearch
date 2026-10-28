# /// script
# dependencies = ["polars", "numpy"]
# ///
"""A4: boundary-width (Wsurf) local exponents for the rotor and the ants out to 2^32. Inputs experiments/archive/2026-10-a4-boundary-width/results/a4c_shape_rotor.csv, experiments/archive/2026-10-a4-boundary-width/results/a4c_shape_ants.csv
(new, to 2^32) and experiments/archive/2026-10-shape-limit/results/shape_rotor.csv, experiments/archive/2026-10-shape-limit/results/shape_ants.csv (stored, to 2^26 / 2^28). Design/decision: notes/frontier-2026-10-13-results.md. usage: uv run experiments/archive/2026-10-a4-boundary-width/scripts/a4_stats.py"""
import numpy as np, polars as pl
cols = "kind,spec,k,A,rg2,aniso,rbar,rsd,h2,h4,h8,Wsurf,fill".split(",")
def load(path):
    rows = [l.strip().split(",") for l in open(path) if l.startswith("cp,")]
    d = pl.DataFrame(rows, schema=cols, orient="row").with_columns([pl.col(c).cast(pl.Float64) for c in cols[2:]])
    return d
def local(d):
    out = {}
    for (spec,), g in d.group_by("spec"):
        g = g.sort("k"); k = g["k"].to_numpy().astype(int); W = g["Wsurf"].to_numpy()
        out[spec] = {int(k[i]): (np.log(W[i + 1]) - np.log(W[i])) / ((k[i + 1] - k[i]) * np.log(2)) for i in range(len(k) - 1) if W[i] > 0 and W[i + 1] > 0}
    return out
rng = np.random.default_rng(20261013)
def series(loc, ks):
    m = {k: np.mean([s[k] for s in loc.values() if k in s]) for k in ks if any(k in s for s in loc.values())}
    n = {k: sum(k in s for s in loc.values()) for k in m}
    return m, n
def trend(loc, kmin=20, kmax=30):
    # d(k) is the exponent between checkpoints k and k+2; regress on log10 t at the midpoint k+1 (octaves) over k = kmin..kmax-2
    specs = list(loc)
    def fit(sel):
        ks = [k for k in range(kmin, kmax, 2) if any(k in loc[s] for s in sel)]
        y = np.array([np.mean([loc[s][k] for s in sel if k in loc[s]]) for k in ks]); x = np.array([(k + 1) * np.log10(2) for k in ks])
        return np.polyfit(x, y, 1)[0], len(ks)
    t0, nk = fit(specs)
    bs = [fit([specs[i] for i in rng.integers(0, len(specs), len(specs))])[0] for _ in range(1000)]
    return t0, float(np.std(bs)), nk
for label, paths in (("rotor (new, to 2^32)", ["experiments/archive/2026-10-a4-boundary-width/results/a4c_shape_rotor.csv"]), ("ants (new, to 2^32)", ["experiments/archive/2026-10-a4-boundary-width/results/a4c_shape_ants.csv"]), ("rotor (stored, to 2^26)", ["experiments/archive/2026-10-shape-limit/results/shape_rotor.csv"]), ("ants (stored, to 2^28)", ["experiments/archive/2026-10-shape-limit/results/shape_ants.csv"])):
    try:
        d = pl.concat([load(p) for p in paths])
    except Exception as e:
        print(label, "no data", type(e).__name__); continue
    loc = local(d); ks = list(range(12, 32, 2)); m, n = series(loc, ks)
    print(f"\n{label}: runs {len(loc)}")
    print("  local exponent d(k) between k and k+2 (mean over runs; n): " + " ".join(f"{k}:{m[k]:.3f}({n[k]})" for k in sorted(m)))
    kmax = max(max(s) for s in loc.values()) + 2
    if kmax >= 26:
        t, se, nk = trend(loc, 20, min(kmax, 32)); print(f"  trend of d(k) vs log10 t over k=20..{min(kmax,32)}: {t:+.4f} per decade (bootstrap SE {se:.4f}, {nk} points)")
    late = [k for k in sorted(m) if k >= 22]
    if late: print(f"  mean d over k>=22: {np.mean([m[k] for k in late]):.3f}")

# pooled with the A4 runs (same estimator): rotors 201-208 + 211-216, ants 24 + 12
print("\n== pooled A4 + A4c")
for label, paths in (("rotor pooled", ["experiments/archive/2026-10-a4-boundary-width/results/a4_shape_rotor.csv", "experiments/archive/2026-10-a4-boundary-width/results/a4c_shape_rotor.csv"]), ("ants pooled", ["experiments/archive/2026-10-a4-boundary-width/results/a4_shape_ants.csv", "experiments/archive/2026-10-a4-boundary-width/results/a4c_shape_ants.csv"])):
    d = pl.concat([load(p) for p in paths]); loc = local(d); ks = list(range(12, 34, 2)); m, n = series(loc, ks)
    print(label, len(loc), "runs; d(k):", " ".join(f"{k}:{m[k]:.3f}({n[k]})" for k in sorted(m)))
    for kmax in (32, 34):
        t, se, nk = trend(loc, 22, kmax); print(f"  trend k=22..{kmax}: {t:+.4f} +- {se:.4f} per decade ({nk} points)")
