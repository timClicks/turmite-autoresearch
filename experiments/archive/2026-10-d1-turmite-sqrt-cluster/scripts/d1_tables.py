# /// script
# dependencies = ["polars", "numpy"]
# ///
"""D1: table features of the sqrt(t) turmite cluster vs the cube-root-like cluster. Design and decision rule: notes/frontier-2026-10-13-results.md.
usage: uv run experiments/archive/2026-10-d1-turmite-sqrt-cluster/scripts/d1_tables.py"""
import itertools, numpy as np, polars as pl
d = pl.read_csv("experiments/archive/2026-10-ext-other-lattices-turmites-noise/results/ext_tm_screen_class.csv").filter(pl.col("cls") == "blob")
d = d.with_columns(id=pl.col("spec").str.split(":").list.get(3).cast(pl.Int64))
sq = d.filter(pl.col("a") < 0.505); ch = d.filter((pl.col("a") >= 0.55) & (pl.col("a") < 0.85))
print(f"sqrt set {sq.height}, chaotic set {ch.height}, other blob (0.505-0.55 or >=0.85): {d.height - sq.height - ch.height}")
S, K = 2, 2
def decode(i):
    base = 4 * K * S; tab = []
    for _ in range(S * K):
        e = i % base; i //= base; tab.append((e % K, (e // K) % 4, e // (4 * K)))  # (write, turn, next state), index = state*K + colour
    return tab
def feats(i):
    t = decode(i); f = {}
    f["any_unchanged_write"] = any(t[s * K + c][0] == c for s in range(S) for c in range(K))
    f["all_unchanged_write"] = all(t[s * K + c][0] == c for s in range(S) for c in range(K))
    f["any_straight"] = any(x[1] == 0 for x in t); f["any_uturn"] = any(x[1] == 2 for x in t)
    f["no_uturn"] = not f["any_uturn"]; f["no_straight"] = not f["any_straight"]
    f["state_never_changes"] = all(t[s * K + c][2] == s for s in range(S) for c in range(K))
    f["state1_unreachable"] = all(t[0 * K + c][2] == 0 for c in range(K))
    f["only_R_L"] = all(x[1] in (1, 3) for x in t)
    f["writes_constant"] = len({x[0] for x in t}) == 1
    f["writes_always_flip"] = all(t[s * K + c][0] == 1 - c for s in range(S) for c in range(K))
    f["any_uturn_or_straight"] = f["any_uturn"] or f["any_straight"]
    for s in range(S):
        for c in range(K):
            f[f"turn[{s},{c}]=" + "NRUL"[t[s * K + c][1]]] = True
    return f
def table(idset):
    rows = [feats(i) for i in idset]; keys = sorted({k for r in rows for k in r})
    return {k: np.array([bool(r.get(k, False)) for r in rows]) for k in keys}
# all feature keys come from both sets
Fs = table(sq["id"].to_list()); Fc = table(ch["id"].to_list())
def auc(a, b):  # a: values for positives, b for negatives (binary)
    pa, pb = a.mean(), b.mean(); return 0.5 + 0.5 * (pa - pb)
out = []
for k in sorted(set(Fs) | set(Fc)):
    a = Fs.get(k, np.zeros(sq.height, bool)); b = Fc.get(k, np.zeros(ch.height, bool))
    pa, pb = a.mean(), b.mean(); odds = ((pa + 1e-9) / (1 - pa + 1e-9)) / ((pb + 1e-9) / (1 - pb + 1e-9))
    out.append((k, pa, pb, odds, auc(a, b)))
out.sort(key=lambda r: -abs(r[4] - 0.5))
print("feature | frac in sqrt set | frac in chaotic set | odds ratio | AUC (positive = sqrt)")
for r in out[:14]: print(f"{r[0]:26s} | {r[1]:.3f} | {r[2]:.3f} | {r[3]:8.2f} | {r[4]:.3f}")
print("best single-feature AUC (max of AUC, 1-AUC):", round(max(max(r[4], 1 - r[4]) for r in out), 3))
print("unchanged-write feature:", [round(x, 3) for x in next((r[1:] for r in out if r[0] == "any_unchanged_write"), ())])
