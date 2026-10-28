"""Check every synthetic field independently of the Rust code, and summarise.

Checks per field: same colour counts as the original over visited cells, same
never-visited mask, share of cells equal to the original in place, best such
share over shifts up to 4 cells, and (for matched levels) the L1 histogram
residual recomputed here, compared with what examples/synth reported.

usage: python3 -I experiments/archive/2026-10-patterns-fields/scripts/patterns_analyse.py   (reads experiments/archive/2026-10-patterns-fields/results/patterns_final.csv,
experiments/archive/2026-10-patterns-fields/results/patterns_anneal.csv; writes experiments/archive/2026-10-patterns-fields/results/patterns_summary.json)
"""
import json
from collections import Counter
from pathlib import Path

import numpy as np
import polars as pl

ROOT = Path(__file__).resolve().parents[2 if lib else 3]
S = 4096
PAD = 3
SHAPES = {"pairs": [(2, 1), (1, 2)], "b2": [(2, 2)], "b3": [(3, 3)]}


def crop(g, n):
    ys, xs = np.nonzero(g != 255)
    sub = g[ys.min() - PAD: ys.max() + PAD + 1, xs.min() - PAD: xs.max() + PAD + 1].astype(np.int64)
    sub[sub == 255] = n
    return sub


def hist(sub, n, shapes):
    h = Counter()
    for s, (sw, sh) in enumerate(shapes):
        H, W = sub.shape
        k = np.zeros((H - sh + 1, W - sw + 1), dtype=np.int64)
        for dy in range(sh):
            for dx in range(sw):
                k = k * (n + 1) + sub[dy: dy + H - sh + 1, dx: dx + W - sw + 1]
        h.update((s, int(v)) for v in k.ravel())
    return h


def l1(a, b):
    return sum(abs(a[k] - b[k]) for k in set(a) | set(b))


def best_shift(f, g, vis, m=4):
    ys, xs = np.nonzero(vis)
    best = 0.0
    for dy in range(-m, m + 1):
        for dx in range(-m, m + 1):
            ok = vis[ys + dy, xs + dx]
            best = max(best, float((f[ys + dy, xs + dx][ok] == g[ys, xs][ok]).mean()))
    return best


final = pl.read_csv(ROOT / "experiments/archive/2026-10-patterns-fields/results/patterns_final.csv", infer_schema_length=1000)
ann = pl.read_csv(ROOT / "experiments/archive/2026-10-patterns-fields/results/patterns_anneal.csv").select("rule", "level", "seed", "windows", "distinct", "cost")
rows = []
for r in final.iter_rows(named=True):
    rule, level, seed = r["rule"], r["level"], r["seed"]
    n = len(rule)
    g = np.fromfile(ROOT / "experiments/archive/2026-10-knockout-maps/dumps" / f"{rule}.grid", dtype=np.uint8).reshape(S, S)
    path = ROOT / "experiments/archive/2026-10-knockout-maps/dumps" / f"{rule}.grid" if level == "real" else ROOT / "experiments/archive/2026-10-patterns-fields/synth" / f"{rule}_{level}_{seed}.grid"
    f = np.fromfile(path, dtype=np.uint8).reshape(S, S)
    vis = g != 255
    assert np.array_equal(f == 255, ~vis), (rule, level, "mask changed")
    if not level.startswith("blank_"):
        assert np.array_equal(np.bincount(f[vis], minlength=n), np.bincount(g[vis], minlength=n)), (rule, level, "counts")
    out = {"rule": rule, "level": level, "seed": seed, "own": r["own"], "spread": r["spread"],
           "same": float((f[vis] == g[vis]).mean())}
    if level in SHAPES:
        out["shift_same"] = best_shift(f, g, vis)
        target = hist(crop(g, n), n, SHAPES[level])
        out["resid"] = l1(hist(crop(f, n), n, SHAPES[level]), target)
        a = ann.filter((pl.col("rule") == rule) & (pl.col("level") == level) & (pl.col("seed") == seed)).row(0, named=True)
        assert out["resid"] == a["cost"], (rule, level, seed, out["resid"], a["cost"])
        out["windows"], out["distinct"] = a["windows"], a["distinct"]
        out["matched"] = 1 - out["resid"] / (2 * a["windows"])
    rows.append(out)

df = pl.DataFrame(rows, infer_schema_length=None)
base = df.filter(pl.col("level") == "shuffle").group_by("rule").agg(base=pl.col("same").mean())
summ = (df.group_by("rule", "level")
          .agg(own=pl.col("own").mean(), own_min=pl.col("own").min(), own_max=pl.col("own").max(),
               spread=pl.col("spread").mean(), spread_min=pl.col("spread").min(), spread_max=pl.col("spread").max(),
               same=pl.col("same").mean(), shift_same=pl.col("shift_same").mean(), matched=pl.col("matched").mean(),
               distinct=pl.col("distinct").first(), windows=pl.col("windows").first())
          .join(base, on="rule").sort("rule", "level"))
(ROOT / "experiments/archive/2026-10-patterns-fields/results/patterns_summary.json").write_text(json.dumps(summ.to_dicts(), indent=1))
pl.Config.set_tbl_rows(200)
pl.Config.set_tbl_cols(20)
pl.Config.set_tbl_width_chars(250)
print(summ.select("rule", "level", pl.col("own").round(3), pl.col("spread").round(1), pl.col("spread_min").round(1),
                  pl.col("spread_max").round(1), pl.col("same").round(3), pl.col("shift_same").round(3),
                  pl.col("matched").round(3), "distinct", "windows", pl.col("base").round(3)))
print("all checks passed:", len(rows), "fields")
