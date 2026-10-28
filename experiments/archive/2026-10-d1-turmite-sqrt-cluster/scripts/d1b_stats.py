# /// script
# dependencies = ["polars", "numpy"]
# ///
"""D1b: 2-state 3-colour random tables: classes, 'state 0 never leaves state 0' enrichment, single-feature AUCs, area/extent^2. Design/prediction: notes/frontier-2026-10-13-results.md."""
import numpy as np, polars as pl
d = pl.read_csv("experiments/archive/2026-10-d1-turmite-sqrt-cluster/results/d1b_screen.csv"); esc = set(d.filter(pl.col("k") == -1)["spec"].to_list()); rows = []
for (sp,), g in d.filter(pl.col("k") > 0).group_by("spec"):
    g = g.sort("k"); k = g["k"].to_numpy().astype(float); A = g["area"].to_numpy().astype(float); E = g["extent"].to_numpy().astype(float)
    if sp in esc or k.max() < 20: continue
    s = (k >= 14) & (k <= 20); a = np.polyfit(k[s] * np.log(2), np.log(A[s]), 1)[0]; ratio = A[k == 20][0] / A[k == 14][0]
    cls = "bounded" if ratio < 1.15 else ("slow" if a < 0.5 else ("blob" if a < 0.9 else "fast"))
    rows.append((sp, cls, a, A[k == 20][0] / E[k == 20][0] ** 2, (A[k == 20][0] / E[k == 20][0] ** 2) / (A[k == 16][0] / E[k == 16][0] ** 2)))
r = pl.DataFrame(rows, schema=["spec", "cls", "a", "fill20", "fill_ratio"], orient="row")
sq = r.filter((pl.col("cls") == "blob") & (pl.col("a") < 0.505)); ch = r.filter((pl.col("cls") == "blob") & (pl.col("a") >= 0.55) & (pl.col("a") < 0.85))
print(f"classified {r.height}; blob {int((r['cls']=='blob').sum())}: sqrt set {sq.height}, chaotic set {ch.height}")
K, S = 3, 2
def feats(sp):
    i = int(sp.split(":")[3]); t = []
    for _ in range(S * K):
        e = i % 24; i //= 24; t.append((e % K, (e // K) % 4, e // (4 * K)))
    f = {}
    f["state0_never_leaves"] = all(t[0 * K + c][2] == 0 for c in range(K))
    f["state_never_changes"] = all(t[s * K + c][2] == s for s in range(S) for c in range(K))
    f["any_unchanged_write"] = any(t[s * K + c][0] == c for s in range(S) for c in range(K))
    f["any_straight"] = any(x[1] == 0 for x in t); f["any_uturn"] = any(x[1] == 2 for x in t)
    f["writes_constant"] = len({x[0] for x in t}) == 1; f["only_RL"] = all(x[1] in (1, 3) for x in t)
    for s in range(S):
        for c in range(K): f[f"turn[{s},{c}]={'NRUL'[t[s*K+c][1]]}"] = True
    return f
def tab(df): 
    F = [feats(s) for s in df["spec"]]; keys = sorted({k for f in F for k in f}); return {k: np.array([bool(f.get(k, False)) for f in F]) for k in keys}
Fs, Fc = tab(sq), tab(ch)
for k in ("state0_never_leaves", "state_never_changes"):
    print(f"{k}: sqrt set {Fs[k].mean():.3f} ({int(Fs[k].sum())}), chaotic set {Fc[k].mean():.3f} ({int(Fc[k].sum())})")
aucs = sorted(((k, 0.5 + 0.5 * (Fs[k].mean() - Fc.get(k, np.zeros(ch.height, bool)).mean())) for k in Fs), key=lambda x: -abs(x[1] - 0.5))
print("best single-feature AUCs (sqrt vs chaotic):", [(k, round(v, 3)) for k, v in aucs[:5]], "; best |AUC-0.5|+0.5 =", round(max(max(v, 1 - v) for _, v in aucs), 3))
for name, df in (("sqrt", sq), ("chaotic", ch)):
    if df.height: print(f"{name}: median area/extent^2 at k=20 {df['fill20'].median():.3f}; median (fill at k=20)/(fill at k=16) {df['fill_ratio'].median():.3f}")
