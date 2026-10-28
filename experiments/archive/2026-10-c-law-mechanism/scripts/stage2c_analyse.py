# /// script
# dependencies = ["numpy"]
# ///
"""Stage 2c (README): band interior ablation A1-A4. usage: uv run experiments/archive/2026-10-c-law-mechanism/scripts/stage2c_analyse.py"""
import json
from pathlib import Path

import numpy as np

root = Path(__file__).resolve().parents[4]
R = root / "experiments/archive/2026-10-c-law-mechanism/results"
area0 = 256 * 512
lines, res = [], {}


def say(s=""):
    print(s)
    lines.append(s)


def load(k):
    out = {}
    for l in (R / f"trace_band_abl_{k}.jsonl").read_text().splitlines():
        d = json.loads(l)
        out[d["spec"].split("@")[0]] = d
    return out


def lead(r):
    k = 1
    while k < len(r) and r[k] == r[0]:
        k += 1
    return k


D = {k: load(k) for k in "UZYH"}
ok = lambda d: (d["area"] - area0) / area0 <= 0.9 and d["births"] >= 5000
c = lambda d: d["births"] / d["boundary_steps"]
main = {}
for l in (R / "trace_band_L24.jsonl", ):
    pass
# consistency: U rerun must equal the main band run for the same rule and L
mainL = {}
for L in range(24, 30):
    for l in (R / f"trace_band_L{L}.jsonl").read_text().splitlines():
        d = json.loads(l)
        mainL[(d["spec"], L)] = d
same = all(mainL[(r, int(D["U"][r]["log2"]))]["births"] == D["U"][r]["births"] and mainL[(r, int(D["U"][r]["log2"]))]["boundary_steps"] == D["U"][r]["boundary_steps"] for r in D["U"])
say(f"U rerun identical to the main band run on births and boundary steps for all {len(D['U'])} rules: {same}")
cu = {r: c(d) for r, d in D["U"].items() if ok(d)}
res["n_U"] = len(cu)
for k in "ZYH":
    rr = [r for r, d in D[k].items() if ok(d) and r in cu]
    x = np.array([c(D[k][r]) for r in rr])
    u = np.array([cu[r] for r in rr])
    m = np.array([min(lead(r), 5) for r in rr], float)
    rel = np.abs(x / u - 1)
    sl, ic = np.polyfit(m, 1 / x, 1)
    cons = np.median([(D[k][r]["area"] - area0) / area0 for r in rr])
    res[k] = dict(n=len(rr), dropped=len(D[k]) - len(rr), median_rel=float(np.median(rel)), median_ratio=float(np.median(x / u)), slope=float(sl), intercept=float(ic),
                  corr2=float(np.corrcoef(x, u)[0, 1] ** 2), median_consumption=float(cons), passed=bool(np.median(rel) <= 0.05))
    say(f"{k}: kept {len(rr)}/60, median |c_{k}/c_U - 1| = {np.median(rel):.4f} (median ratio {np.median(x / u):.4f}, corr2 {np.corrcoef(x, u)[0, 1] ** 2:.4f}), "
        f"1/c = {ic:.3f} + {sl:.3f} lead, median band consumption {cons:.2f} -> A{'ZYH'.index(k) + 1} {'PASS' if res[k]['passed'] else 'FAIL'}")
res["A4"] = bool(all(0.55 <= res[k]["slope"] <= 0.85 for k in "ZYH"))
say(f"A4 (all slopes in [0.55, 0.85]): {'PASS' if res['A4'] else 'FAIL'}")
(R / "stage2c_analysis.json").write_text(json.dumps(res, indent=1, default=float))
(R / "stage2c_analysis.txt").write_text("\n".join(lines) + "\n")
