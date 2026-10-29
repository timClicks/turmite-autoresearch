# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy>=1.26"]
# ///
"""Revision 3 gate G1: synthetic discrimination of the time-weighted Score (README "Revision 3 registration").

Laws with known D/S status by construction, 4 pseudo-seeds x 9 windows (k = 16..24,
L_k = 6 * 2^{3(k-16)/8}), iid durations until cumulative tau first reaches 2^{k-2}
(last draw kept). 20 replicates per law; SeedSequence(2026102971).spawn in the fixed
order (law alphabetical, replicate 0..19). PASS: correct verdict >= 18/20 and the
opposite verdict 0/20 for every law. Number-weighted Score reported only.
Writes results/rev3_synth.{json,txt}.
"""
from __future__ import annotations

import json
import math
import sys
from functools import lru_cache
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tw_score as tw  # noqa: E402

RES = Path(__file__).resolve().parents[1] / "results"
MASTER = 2026102971
N_REP = 20
N_SEEDS = 4
KS = list(range(16, 25))
LAWS = {"SD": "D", "SD2": "D", "SG": "S", "SS1": "S", "SS2": "S"}  # alphabetical order used for spawn
OPP = {"D": "S", "S": "D"}


def L_of(k: int) -> float:
    return 6.0 * 2 ** (3 * (k - 16) / 8)


@lru_cache(maxsize=None)
def ruin_cdf(M: int) -> np.ndarray:
    """CDF of absorption time of SRW from 1 on {0..M}; residual (< 1e-12) put on the cap."""
    v = np.zeros(M + 1)
    v[1] = 1.0
    pm = [0.0]
    alive = 1.0
    while alive >= 1e-12:
        nv = np.zeros_like(v)
        nv[:-1] += 0.5 * v[1:]
        nv[1:] += 0.5 * v[:-1]
        absorbed = nv[0] + nv[M]
        nv[0] = 0.0
        nv[M] = 0.0
        v = nv
        pm.append(absorbed)
        alive = v.sum()
    pm = np.asarray(pm)
    pm[-1] += alive
    cdf = np.cumsum(pm)
    cdf[-1] = 1.0
    return cdf


def draw_ruin(rng, M, n):
    cdf = ruin_cdf(M)
    return np.searchsorted(cdf, rng.random(n), side="right").astype(np.int64)


def draw_short(rng, n):
    return rng.geometric(0.5, n).astype(np.int64)  # P(j) = 2^{-j}, j >= 1


def draw(law, rng, L, n):
    if law == "SD":
        return draw_ruin(rng, int(round(2 * L)), n)
    if law == "SD2":
        short = rng.random(n) < 0.7
        out = draw_ruin(rng, int(round(2 * L)), n)
        out[short] = draw_short(rng, int(short.sum()))
        return out
    if law == "SS1":
        short = rng.random(n) < 0.6
        out = np.ceil(L * rng.uniform(0.5, 3.0, n)).astype(np.int64)
        out[short] = draw_short(rng, int(short.sum()))
        return out
    if law == "SS2":
        return draw_ruin(rng, int(round(4 * math.sqrt(L))), n)
    if law == "SG":
        return rng.geometric(1.0 / L, n).astype(np.int64)
    raise ValueError(law)


def window(law, rng, k):
    L = L_of(k)
    B = 2 ** (k - 2)
    parts, tot = [], 0
    while tot < B:
        n = max(1000, int(1.2 * (B - tot) / max(L, 1.0)))
        x = draw(law, rng, L, n)
        cs = np.cumsum(x) + tot
        idx = np.searchsorted(cs, B, side="left")
        if idx < len(x):
            parts.append(x[: idx + 1])
            tot = int(cs[idx])
            break
        parts.append(x)
        tot = int(cs[-1])
    tau = np.concatenate(parts)
    return {"L": L, "k": k, "fbins": tw.bin_taus(tau)}


def main():
    ss = np.random.SeedSequence(MASTER)
    children = ss.spawn(len(LAWS) * N_REP)
    results = {}
    lines = []
    ci = 0
    for law in sorted(LAWS):
        rows = []
        for r in range(N_REP):
            rng = np.random.default_rng(children[ci])
            ci += 1
            wins = []
            for _seed in range(N_SEEDS):
                for k in KS:
                    wins.append(window(law, rng, k))
            kept = []
            for w in wins:
                st = tw.window_stats(w["fbins"])
                if st["n"] >= tw.N_MIN and st["n_eff"] >= tw.NEFF_MIN and w["L"] >= 4:
                    w["coarse"] = tw.coarse_from_fine(w["fbins"])
                    kept.append(w)
            res = tw.score_tw(kept)
            nw = tw.number_weighted_score(kept)
            rows.append({"rep": r, "n_windows": len(wins), "n_retained": len(kept),
                         "Score_tw_L": res["Score_L"], "Score_tw_L2": res["Score_L2"], "verdict_tw": res["verdict"],
                         "Score_nw_L": nw["Score_L"], "Score_nw_L2": nw["Score_L2"], "verdict_nw": nw["verdict"]})
        exp = LAWS[law]
        n_ok = sum(x["verdict_tw"] == exp for x in rows)
        n_opp = sum(x["verdict_tw"] == OPP[exp] for x in rows)
        n_ok_nw = sum(x["verdict_nw"] == exp for x in rows)
        n_opp_nw = sum(x["verdict_nw"] == OPP[exp] for x in rows)
        ok = n_ok >= 18 and n_opp == 0
        med = lambda key: float(np.median([x[key] for x in rows]))  # noqa: E731
        results[law] = {"expected": exp, "tw_correct": n_ok, "tw_opposite": n_opp, "pass": ok,
                        "nw_correct": n_ok_nw, "nw_opposite": n_opp_nw,
                        "median_Score_tw_L": med("Score_tw_L"), "median_Score_tw_L2": med("Score_tw_L2"),
                        "median_Score_nw_L": med("Score_nw_L"), "median_Score_nw_L2": med("Score_nw_L2"),
                        "min_retained": min(x["n_retained"] for x in rows), "reps": rows}
        line = (f"{law:4s} expect {exp}: Score_tw correct {n_ok}/20 opposite {n_opp}/20 -> {'PASS' if ok else 'FAIL'}; "
                f"median Score_tw(L) {med('Score_tw_L'):.4f} vs (L^2) {med('Score_tw_L2'):.4f}; "
                f"number-weighted (report only) correct {n_ok_nw}/20 opposite {n_opp_nw}/20, "
                f"median {med('Score_nw_L'):.4f} vs {med('Score_nw_L2'):.4f}; retained >= {results[law]['min_retained']}/36")
        print(line, flush=True)
        lines.append(line)
    g1 = all(v["pass"] for v in results.values())
    lines.append(f"G1 synthetic discrimination: {'PASS' if g1 else 'FAIL'}")
    print(lines[-1])
    (RES / "rev3_synth.txt").write_text("\n".join(lines) + "\n")
    (RES / "rev3_synth.json").write_text(json.dumps({"G1_pass": g1, "master_seed": MASTER, "laws": results}, indent=1))


if __name__ == "__main__":
    main()
