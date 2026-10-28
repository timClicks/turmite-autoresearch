# /// script
# dependencies = ["numpy", "polars", "scipy"]
# ///
"""Prefix decode: which compact encodings of the rule prefix recover the lookup's gain over an
ln A(22) spline for stationary rules?  See ../README.md (registered predictions D1-D5).
usage (repo root): uv run experiments/archive/2026-10-kappa-prefix-decode/scripts/decode.py"""
from pathlib import Path
import itertools, json, subprocess, sys
import numpy as np, polars as pl

HERE = Path(__file__).resolve().parent
EXP = HERE.parent
ROOT = HERE.parents[3]
KR = ROOT / "experiments/archive/2026-10-kappa-rule-space/scripts"
sys.path.insert(0, str(KR))
from kcommon import census, per_rule, rule_means, canon  # noqa: E402
from prefix_audit import lookup, basis, predict  # noqa: E402

SEED = 20261016
NB = 2000
rng = np.random.default_rng(SEED)

# ---- data: identical to prefix_audit.py (stationary cohort) ----
raw = pl.read_csv(KR.parent / "dumps/w3c_probe.csv")
runs = per_rule(raw).with_columns(base=pl.col("rule").str.split("@").list.first())
runs = runs.join(raw.filter(pl.col("k") == 22).select("rule", lnA22=pl.col("area").log()), on="rule", how="left")
fresh = rule_means(runs.filter(pl.col("alpha_w").is_between(.25, .42) & (pl.col("kappa") > 0)), 6)
cen = census().filter((pl.col("kappa") > 0) & pl.col("lnA22").is_not_null()).sort("rule")
tr = cen.filter(pl.col("g_k").abs() < .05)
te = fresh.filter(pl.col("g_k").abs() < .05)
rules, tests = tr["rule"].to_list(), te["base"].to_list()
assert not set(rules) & set(tests)
y, v = np.log(tr["kappa"].to_numpy()), te["lnk"].to_numpy()
a, b = tr["lnA22"].to_numpy(), te["lnA22"].to_numpy()
xa, za = basis(a, b, True)          # spline area basis (standardised)
base_pred = predict(xa, y, za)
den = (v - y.mean()) ** 2


def gain_of(pred):
    contrib = (v - base_pred) ** 2 - (v - pred) ** 2
    g = contrib.sum() / den.sum()
    idx = rng.integers(0, len(v), (NB, len(v)))
    bs = contrib[idx].sum(1) / den[idx].sum(1)
    return float(g), [float(q) for q in np.quantile(bs, [.025, .975])]


# ---- feature builders ----
def ind(s, n=8):
    return np.array([(s[i] == "R") if i < len(s) else 0.5 for i in range(n)], float)


def e0(s):
    return np.r_[ind(s), len(s)]


def e1(s):
    f = ind(s)
    return np.r_[f, [f[i] * f[j] for i, j in itertools.combinations(range(8), 2)], len(s)]


def e2(s):
    p = s[:8]
    lead = len(p) - len(p.lstrip(p[0]))
    return np.array([lead, p.count("R"), sum(p[i] != p[i + 1] for i in range(len(p) - 1))], float)


def ridge_gain(feat, lam, shuffle=None):
    f = (lambda s: feat(s if shuffle is None else "".join(s[i] if i < len(s) else "" for i in shuffle)
                        if False else s))
    X = np.array([feat(s) for s in rules]); Z = np.array([feat(s) for s in tests])
    if shuffle is not None:                     # permute feature columns by the same map in train and test
        X, Z = X[:, shuffle], Z[:, shuffle]
    return X, Z


def ridge_fit(Xe, Ze, lam):
    m, s = Xe.mean(0), Xe.std(0) + 1e-9
    X = np.c_[xa, (Xe - m) / s]; Z = np.c_[za, (Ze - m) / s]
    X1 = np.c_[np.ones(len(X)), X]
    pen = np.eye(X1.shape[1]) * lam; pen[0, 0] = 0; pen[1:xa.shape[1] + 1, :] = 0
    beta = np.linalg.solve(X1.T @ X1 + pen, X1.T @ y)
    return np.c_[np.ones(len(Z)), Z] @ beta


def cv_lambda(Xe, grid=(1, 10, 100, 1000)):
    """Pick ridge penalty by 5-fold CV on the census residual (training data only)."""
    fold = np.empty(len(y), int); fold[np.random.default_rng(SEED).permutation(len(y))] = np.arange(len(y)) % 5
    best = None
    for lam in grid:
        sse = 0.0
        for f in range(5):
            k, h = fold != f, fold == f
            m, s = Xe[k].mean(0), Xe[k].std(0) + 1e-9
            X = np.c_[np.ones(k.sum()), xa[k], (Xe[k] - m) / s]; Z = np.c_[np.ones(h.sum()), xa[h], (Xe[h] - m) / s]
            pen = np.eye(X.shape[1]) * lam; pen[0, 0] = 0; pen[1:xa.shape[1] + 1, :] = 0
            sse += ((y[h] - Z @ np.linalg.solve(X.T @ X + pen, X.T @ y[k])) ** 2).sum()
        if best is None or sse < best[0]:
            best = (sse, lam)
    return best[1]


results = {}
lines = ["EXPLORATORY prefix decode (see README); cmd: uv run experiments/archive/2026-10-kappa-prefix-decode/scripts/decode.py",
         f"git: {subprocess.run(['git','rev-parse','--short','HEAD'],cwd=ROOT,capture_output=True,text=True).stdout.strip()} (tree dirty) seed {SEED}",
         f"stationary census train n={len(y)}, pool test n={len(v)}; baseline spline R2 on pool = "
         f"{1 - ((v-base_pred)**2).sum()/den.sum():.3f}"]


def report(name, pred, extra=""):
    g, ci = gain_of(pred)
    results[name] = dict(gain=g, ci=ci)
    lines.append(f"{name:34s} gain {g:+.3f}  CI [{ci[0]:+.3f},{ci[1]:+.3f}] {extra}")
    return g


# reference: crossfit lookup, same as audit
fold = np.empty(len(y), int); fold[np.random.default_rng(20261015).permutation(len(y))] = np.arange(len(y)) % 5
cross = np.empty(len(y))
for f in range(5):
    k, h = fold != f, fold == f
    cross[h] = lookup([r for r, kk in zip(rules, k) if kk], y[k], [r for r, hh in zip(rules, h) if hh])[0]
enc, _ = lookup(rules, y, tests)
g_ref = report("LOOKUP prefix-8 (reference)", predict(np.c_[xa, cross], y, np.c_[za, enc]))

for name, feat in (("E0 additive", e0), ("E1 +pairwise interactions", e1), ("E2 summary (3 numbers)", e2)):
    Xe = np.array([feat(s) for s in rules]); Ze = np.array([feat(s) for s in tests])
    lam = cv_lambda(Xe)
    g = report(name, ridge_fit(Xe, Ze, lam), f"lambda={lam} ({g_ref and results[name]['gain']/g_ref:.0%} of lookup)" if False else f"lambda={lam}")
    lines[-1] += f"  = {results[name]['gain']/g_ref:.0%} of lookup"

# E4: control, destroy position identity by shuffling the label of each sample's letters
for name, feat in (("E4a shuffled-labels E0", e0), ("E4b shuffled-labels E1", e1)):
    gs = []
    for rep in range(20):
        r = np.random.default_rng(SEED + 100 + rep)
        perm = r.permutation(len(y))
        Xe = np.array([feat(s) for s in rules])[perm]       # decouple features from targets
        Ze = np.array([feat(s) for s in tests])
        gs.append(gain_of(ridge_fit(Xe, Ze, cv_lambda(Xe)))[0])
    results[name] = dict(gain_mean=float(np.mean(gs)), gain_sd=float(np.std(gs)))
    lines.append(f"{name:34s} gain mean {np.mean(gs):+.3f} sd {np.std(gs):.3f} over 20 target shuffles")

# E3: standalone-prefix rule in the census (residual of ln kappa after the spline, fitted on all census rows)
allc = census().filter((pl.col("kappa") > 0) & pl.col("lnA22").is_not_null())
cr = allc["rule"].to_list(); cy = np.log(allc["kappa"].to_numpy()); ca = allc["lnA22"].to_numpy()
cx, _ = basis(ca, ca[:2], True)
cres = cy - predict(cx, cy, cx)
cmap = dict(zip(cr, cres)); cmapy = dict(zip(cr, cy))
stat_c = dict(zip(cr, np.abs(allc["g_k"].to_numpy()) < .05))
for p in (4, 5, 6, 7):
    def f3(s, p=p):
        k = canon(s[:p])
        return k in cmap and stat_c.get(k, False)
    cover = np.mean([f3(s) for s in rules if len(s) > p]), np.mean([f3(s) for s in tests])
    fill = float(np.mean([cmap[canon(s[:p])] for s in rules if len(s) > p and f3(s)]))
    def feat3(s, p=p):
        k = canon(s[:p]) if len(s) > p else None
        return [cmap[k] if k in cmap and stat_c[k] else fill, float(k in cmap and stat_c[k])] if k else [fill, 0.0]
    Xe = np.array([feat3(s) for s in rules]); Ze = np.array([feat3(s) for s in tests])
    r_in = np.corrcoef(Xe[:, 0], y - predict(xa, y, xa))[0, 1]
    report(f"E3 own-prefix p={p}", ridge_fit(Xe, Ze, cv_lambda(Xe)),
           f"coverage tr/te {cover[0]:.2f}/{cover[1]:.2f}; train corr(feature,resid)={r_in:+.3f}")
    lines[-1] += f"  = {results[f'E3 own-prefix p={p}']['gain']/g_ref:.0%} of lookup"

# A-series: POST HOC ablations (unregistered), added after E0-E2 beat the lookup
lines.append("A-series post hoc ablations (gain over spline; same train/test):")


def Rcount(s, n=8):
    return sum(c == "R" for c in s[:n])


ablations = {
    "A1 length only": lambda s: [len(s)],
    "A2 R count in first 8": lambda s: [Rcount(s)],
    "A3 R fraction of whole rule": lambda s: [s.count("R") / len(s)],
    "A4 R count whole rule + length": lambda s: [s.count("R"), len(s)],
    "A5 letter 2 only": lambda s: [s[1] == "R"],
    "A6 letters 1-3 indicators": lambda s: list(ind(s, 3)),
    "A7 letters 4-8 indicators": lambda s: list(ind(s)[3:]),
    "A8 leading run only": lambda s: [e2(s)[0]],
    "A9 switches in first 8 only": lambda s: [e2(s)[2]],
    "A10 R count first 8 + switches": lambda s: [Rcount(s), e2(s)[2]],
    "A11 R count first 4": lambda s: [Rcount(s, 4)],
    "A12 R count letters 9+": lambda s: [Rcount(s[8:], 99)],
    "A13 full-rule indicators (12)": lambda s: list(ind(s, 12)),
}
for name, feat in ablations.items():
    Xe = np.array([feat(s) for s in rules], float); Ze = np.array([feat(s) for s in tests], float)
    lam = cv_lambda(Xe)
    report(name, ridge_fit(Xe, Ze, lam), f"lambda={lam}")
    lines[-1] += f"  = {results[name]['gain']/g_ref:.0%} of lookup"

# D5: descriptive greedy tree on the stationary residual over prefix letters
res = y - predict(xa, y, xa)
P = np.array([[s[i] == "R" if i < len(s) else False for i in range(8)] for s in rules])
L = np.array([[i < len(s) for i in range(8)] for s in rules])


def tree(idx, depth, indent=""):
    if depth == 0 or len(idx) < 60:
        return
    best = None
    for pos in range(8):
        ok = idx[L[idx, pos]]
        l, r_ = ok[~P[ok, pos]], ok[P[ok, pos]]
        if len(l) < 30 or len(r_) < 30:
            continue
        sse = ((res[l] - res[l].mean()) ** 2).sum() + ((res[r_] - res[r_].mean()) ** 2).sum()
        if best is None or sse < best[0]:
            best = (sse, pos, l, r_)
    if best is None:
        return
    _, pos, l, r_ = best
    gain = ((res[idx] - res[idx].mean()) ** 2).sum() - best[0]
    lines.append(f"{indent}split pos {pos+1}: L n={len(l)} mean {res[l].mean():+.2f} | R n={len(r_)} mean {res[r_].mean():+.2f}  (SSE drop {gain:.1f})")
    tree(l, depth - 1, indent + "  L> "); tree(r_, depth - 1, indent + "  R> ")


lines.append("descriptive tree on stationary census residual (not a held-out claim):")
tree(np.arange(len(y)), 3)
first = lines[-1] if False else None

(EXP / "results").mkdir(exist_ok=True)
(EXP / "results/decode.txt").write_text("\n".join(lines) + "\n")
(EXP / "results/decode.json").write_text(json.dumps(results, indent=2) + "\n")
print("\n".join(lines))
