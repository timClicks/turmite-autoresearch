# /// script
# dependencies = ["polars", "numpy"]
# ///
"""A5: are the ~28 spread clusters of tethered rules labelled by a single feature of the rule string?
Clusters as in spread_clusters.py (2% relative gap). Features: length, #R, #L, #runs, run-length multiset,
rotation/reversal/complement-canonical form, first two letters, last two letters.
Separable = best single (feature,value) for the cluster has F1 >= 0.8 for membership. Held-out check:
choose the (feature,value) on a random half (seed 20261013) of the cluster's rules and the matching half
of non-members, score F1 on the other halves.
usage: uv run experiments/archive/2026-10-a5-home-types/scripts/a5_home_types.py   (from repo root)"""
import re, random, collections
import polars as pl, numpy as np
d = pl.read_csv("experiments/archive/2026-10-tether-rules/results/tether_screen.csv").filter(pl.col("spread_real").is_not_null() & (pl.col("spread_real") < 25)).sort("spread_real")
v = d["spread_real"].to_numpy(); lab = np.zeros(len(v), int)
for i in range(1, len(v)): lab[i] = lab[i - 1] + (v[i] > v[i - 1] * 1.02)
rules = d["rule"].to_list(); lab = lab.tolist()
def runs(s): return [len(m) for m in re.findall(r"R+|L+", s)]
def canon(s):
    c = s.translate(str.maketrans("RL", "LR"))
    forms = []
    for t in (s, s[::-1], c, c[::-1]):
        forms += [t[i:] + t[:i] for i in range(len(t))]
    return min(forms)
def feats(s):
    r = runs(s)
    return {"n": s.count("") - 1, "nR": s.count("R"), "nL": s.count("L"), "nruns": len(r),
            "runs_multiset": tuple(sorted(r)), "n_nR": (len(s), s.count("R")), "n_nruns": (len(s), len(r)),
            "nR_nL_nruns": (s.count("R"), s.count("L"), len(r)), "canon": canon(s), "head2": s[:2], "tail2": s[-2:],
            "maxrun": max(r), "maxrun_n": (max(r), len(s))}
F = [feats(s) for s in rules]
names = list(F[0])
def f1(members, pred):
    tp = sum(1 for i in members if pred(i)); fp = sum(1 for i in range(len(rules)) if i not in members and pred(i))
    fn = len(members) - tp
    return 0 if tp == 0 else 2 * tp / (2 * tp + fp + fn)
def best(idx, pool):
    mem = set(idx); bestv = (0, None, None)
    for nm in names:
        for val in {F[i][nm] for i in idx}:
            tp = sum(1 for i in idx if F[i][nm] == val); fp = sum(1 for i in pool if i not in mem and F[i][nm] == val)
            sc = 2 * tp / (2 * tp + fp + (len(idx) - tp))
            if sc > bestv[0]: bestv = (sc, nm, val)
    return bestv
rng = random.Random(20261013)
out = []; ncl = max(lab) + 1; n_sep = n_held = n_big = 0
print("cluster n spread  best_feature value F1_full F1_heldout")
for c in range(ncl):
    idx = [i for i in range(len(rules)) if lab[i] == c]
    if len(idx) < 5: continue
    n_big += 1
    sc, nm, val = best(idx, range(len(rules)))
    rng.shuffle(idx); h = len(idx) // 2; tr, te = idx[:h], idx[h:]
    others = [i for i in range(len(rules)) if lab[i] != c]; rng.shuffle(others); oh = len(others) // 2
    sc_tr, nm_tr, val_tr = best(tr, tr + others[:oh])
    te_mem = set(te); pool = te + others[oh:]
    tp = sum(1 for i in te if F[i][nm_tr] == val_tr); fp = sum(1 for i in others[oh:] if F[i][nm_tr] == val_tr)
    held = 2 * tp / (2 * tp + fp + len(te) - tp)
    n_sep += sc >= 0.8; n_held += held >= 0.8
    print(f"{c:2d} {len(idx):3d} {np.median(v[[i for i in range(len(rules)) if lab[i]==c]]):6.2f}  {nm:14s} {str(val)[:28]:28s} {sc:.2f} {held:.2f} (train-chosen: {nm_tr}={str(val_tr)[:20]})")
print(f"\nclusters with >=5 rules: {n_big}; separable in-sample (F1>=0.8): {n_sep}; separable held-out: {n_held}")
# is the cluster a function of the canonical form (symmetry class)?
by = collections.defaultdict(set)
for i, s in enumerate(rules): by[F[i]["canon"]].add(lab[i])
multi = {k: v_ for k, v_ in by.items() if len(v_) > 1}
print(f"symmetry classes (rotation/reversal/complement): {len(by)}; with >1 cluster: {len(multi)}")
