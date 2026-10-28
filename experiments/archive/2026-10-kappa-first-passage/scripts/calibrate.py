# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "scipy", "polars"]
# ///
"""Synthetic calibration of the segment-state estimator (README "Calibration registration", C1-C4).

Planted worlds have a known E[T] (exact linear solve over hidden (milestone, mode) states).
    uv run --frozen experiments/archive/2026-10-kappa-first-passage/scripts/calibrate.py [--quick]
Writes results/calibration.json. Seeds are 202610207000 + k; no other randomness.
"""
from __future__ import annotations

import json
import sys
import time
from collections import defaultdict
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fpkernel  # noqa: E402

EXP = Path(__file__).resolve().parents[1]
BASE_SEED = 202610207000
COLS = ["band", "m", "dir", "heading", "phase", "patch", "hist", "nm", "ndir", "nheading", "nphase", "npatch", "nhist", "n", "time", "skipped", "jumps", "revisits"]


class World:
    def __init__(self, pu, mu, q=0.5, tail=("exp",), visible=False, d0=2.0, patch_noise=0, entry_p1=0.5):
        self.pu = np.array(pu, float)  # [mode][m], m = 0..7
        self.mu = np.array(mu, float)  # mean dwell of a segment starting at (m, mode)
        self.q, self.tail, self.visible, self.d0, self.patch_noise, self.entry_p1 = q, tail, visible, d0, patch_noise, entry_p1

    def dwell(self, rng, mean, m):
        if self.tail[0] == "pareto" and m >= self.tail[2]:
            a = self.tail[1]
            xm = mean * (a - 1) / a
            return xm * (1 - rng.random()) ** (-1 / a)
        return rng.exponential(mean)

    def true_ET(self):
        # u(m,g) for m = 1..7, g in {0,1}; absorbing at m = 0
        idx = {(m, g): (m - 1) * 2 + g for m in range(1, 8) for g in range(2)}
        A = np.eye(14)
        b = np.zeros(14)
        P = np.array([[self.q, 1 - self.q], [1 - self.q, self.q]])
        for (m, g), i in idx.items():
            b[i] = self.mu[g][m]
            pu = 0.0 if m == 7 else self.pu[g][m]
            for gp in range(2):
                if m < 7:
                    A[i, idx[(m + 1, gp)]] -= pu * P[g, gp]
                if m > 1:
                    A[i, idx[(m - 1, gp)]] -= (1 - pu) * P[g, gp]
        u = np.linalg.solve(A, b)
        p1 = self.entry_p1  # entry mode law at the cycle start; the hit of milestone 1 follows one mode switch
        pe1 = p1 * self.q + (1 - p1) * (1 - self.q)
        pi = np.array([1 - pe1, pe1])
        return float(sum(pi[g] * u[idx[(1, g)]] for g in range(2))), self.d0

    def simulate(self, rng, ncycles=None, budget=None):
        """Aggregate pair rows. Stop after `ncycles` cycles or when elapsed time exceeds `budget`
        (the segment in progress is then recorded as open)."""
        agg = defaultdict(lambda: [0, 0.0])
        clock = 0.0
        cyc = 0

        def key(m, dir_, g, hist):
            ph = g if self.visible else 0
            pt = int(rng.integers(0, self.patch_noise)) if self.patch_noise else 0
            return (m, dir_, 0, ph, pt, hist)

        while True:
            if ncycles is not None and cyc >= ncycles:
                break
            cyc += 1
            g = int(rng.random() < self.entry_p1)
            m, dir_, hist = 0, 2, 0
            src = key(m, dir_, g, hist)
            while True:
                mean = self.d0 if m == 0 else self.mu[g][m]
                dw = self.dwell(rng, mean, m)
                if budget is not None and clock + dw > budget:
                    r = agg[(src, None)]
                    r[0] += 1
                    r[1] += budget - clock
                    return self.frame(agg)
                clock += dw
                if m == 0:
                    m2 = 1
                elif m == 7:
                    m2 = 6
                else:
                    m2 = m + 1 if rng.random() < self.pu[g][m] else m - 1
                g2 = g if rng.random() < self.q else 1 - g
                hist = ((hist << 3) | m2) & 0xFFF
                nxt = key(m2, 1 if m2 > m else 2, g2, hist)
                r = agg[(src, nxt)]
                r[0] += 1
                r[1] += dw
                if m2 == 0:
                    break
                m, dir_, g, src = m2, (1 if m2 > m else 2), g2, nxt
        return self.frame(agg)

    @staticmethod
    def frame(agg):
        rows = []
        for (s, nx), (n, t) in agg.items():
            ns = nx if nx is not None else (None,) * 6
            rows.append((0, *s, *ns, n, t, 0, 0, 0))
        return pl.DataFrame(rows, schema=dict(zip(COLS, [pl.Int64] * 13 + [pl.Int64, pl.Float64, pl.Int64, pl.Int64, pl.Int64])), orient="row")


def rel(est, truth):
    return (est - truth) / truth


def markov_world():
    pu = [[0, 0.45, 0.45, 0.45, 0.45, 0.45, 0.45, 0]] * 2
    mu = [[0] + [1.5 * 2 ** (m / 2) for m in range(1, 8)]] * 2
    return World(pu, mu)


def hidden_world(visible):
    pu = [[0, 0.20, 0.20, 0.20, 0.20, 0.20, 0.20, 0], [0, 0.70, 0.70, 0.70, 0.70, 0.70, 0.70, 0]]
    mu = [[0] + [1.0 * 1.5 ** m for m in range(1, 8)], [0] + [6.0 * 1.5 ** m for m in range(1, 8)]]
    return World(pu, mu, q=0.95, visible=visible)


def run(quick: bool) -> dict:
    out: dict = {"seed_base": BASE_SEED, "quick": quick}
    t0 = time.time()
    k = 0

    def rng_next():
        nonlocal k
        k += 1
        return np.random.default_rng(BASE_SEED + k)

    # ---------- C1: Markov chain, bias and bootstrap coverage ----------
    w = markov_world()
    truth, d0 = w.true_ET()
    ndata, nchunk, nboot, ncyc = (20, 6, 40, 120) if quick else (80, 8, 100, 40)
    big = []
    for _ in range(40 if not quick else 8):
        big.append(fpkernel.fit(pl.concat([w.simulate(rng_next(), ncycles=400) for _ in range(5)]), level=0, floor=1)["ET"])
    cover = 0
    cis = []
    for d in range(ndata):
        reps = [w.simulate(rng_next(), ncycles=ncyc) for _ in range(nchunk)]
        est = fpkernel.fit(pl.concat(reps), level=0, floor=1)["ET"]
        ci = fpkernel.bootstrap(reps, nboot, BASE_SEED + 9000 + d, level=0, floor=1)
        cover += ci["lo"] <= truth <= ci["hi"]
        cis.append(est)
    out["C1"] = dict(truth_ET=truth, mean_rel_bias_2000cycles=float(np.mean(rel(np.array(big), truth))), sd_rel=float(np.std(rel(np.array(big), truth))),
                     coverage=cover / ndata, n_datasets=ndata, cycles_per_dataset=ncyc * nchunk,
                     criterion="|bias|<5% and coverage in [0.90,0.99]")
    out["C1"]["pass"] = bool(abs(out["C1"]["mean_rel_bias_2000cycles"]) < 0.05 and 0.90 <= out["C1"]["coverage"] <= 0.99)

    # ---------- C2: hidden mode ----------
    res = {}
    for vis, level in [(False, 0), (True, 1), (False, 2)]:
        w = hidden_world(vis)
        truth, _ = w.true_ET()
        b = []
        for _ in range(6 if quick else 20):
            df = pl.concat([w.simulate(rng_next(), ncycles=1500) for _ in range(3)])
            b.append(fpkernel.fit(df, level=level, floor=20)["ET"])
        res[f"visible={vis},level=M{level}"] = dict(truth_ET=truth, mean_rel_bias=float(np.mean(rel(np.array(b), truth))), sd_rel=float(np.std(rel(np.array(b), truth))), n=len(b))
    out["C2"] = res
    out["C2"]["pass_M0_fails"] = bool(abs(res["visible=False,level=M0"]["mean_rel_bias"]) > 0.20)
    out["C2"]["pass_M1_visible_ok"] = bool(abs(res["visible=True,level=M1"]["mean_rel_bias"]) < 0.05)

    # ---------- C3: heavy tail and cap censoring ----------
    pu = [[0, 0.5, 0.5, 0.5, 0.45, 0.45, 0.45, 0]] * 2
    mu = [[0] + [2.0 * 1.6 ** m for m in range(1, 8)]] * 2
    w = World(pu, mu, tail=("pareto", 1.3, 4))
    truth, d0 = w.true_ET()
    c3 = []
    for budget_mult in ([20, 200] if quick else [20, 200, 2000, 20000]):
        budget = budget_mult * (truth + d0)
        b, cens = [], []
        for _ in range(8 if quick else 30):
            df = w.simulate(rng_next(), budget=budget)
            r = fpkernel.fit(df, level=0, floor=1)
            if "ET" in r:
                b.append(r["ET"])
                cens.append(r["censored_time"] / (r["censored_time"] + r["completed_time"]))
        c3.append(dict(budget_in_cycles=budget_mult, n=len(b), mean_rel_bias=float(np.mean(rel(np.array(b), truth))) if b else None,
                       sd_rel=float(np.std(rel(np.array(b), truth))) if b else None, mean_censored_share=float(np.mean(cens)) if cens else None))
    out["C3"] = dict(truth_ET=truth, rows=c3, note="Pareto alpha=1.3 at milestones >= 4; acceptance only where censored share < 5%")

    # ---------- C4: sparse M2 keys ----------
    w = markov_world()
    w.patch_noise = 2048
    truth, _ = w.true_ET()
    c4 = {}
    for floor in (1, 20):
        b = []
        for _ in range(5 if quick else 15):
            df = pl.concat([w.simulate(rng_next(), ncycles=300) for _ in range(4)])
            b.append(fpkernel.fit(df, level=2, floor=floor)["ET"])
        c4[f"floor={floor}"] = dict(mean_rel_bias=float(np.mean(rel(np.array(b), truth))), sd_rel=float(np.std(rel(np.array(b), truth))), n=len(b))
    out["C4"] = c4
    out["C4"]["pass"] = bool(abs(c4["floor=20"]["mean_rel_bias"]) < 0.10)
    out["seconds"] = time.time() - t0
    return out


if __name__ == "__main__" and "--c2b" not in sys.argv and "--c5" not in sys.argv:
    quick = "--quick" in sys.argv
    res = run(quick)
    dest = EXP / "results" / ("calibration_quick.json" if quick else "calibration.json")
    dest.parent.mkdir(exist_ok=True)
    dest.write_text(json.dumps(res, indent=2, sort_keys=True))
    print(json.dumps(res, indent=2, sort_keys=True))


def run_c2b() -> dict:
    """README "C2 revision": train on entry mixture 0.5, predict a world whose entry law is 0.9 excursion-prone."""
    out = {"seed_base": BASE_SEED + 500}
    res = {}
    for vis, level in [(False, 0), (True, 1)]:
        train, target = hidden_world(vis), hidden_world(vis)
        target.entry_p1 = 0.9
        truth, _ = target.true_ET()
        b = []
        for k in range(20):
            rng = np.random.default_rng(BASE_SEED + 500 + 2 * k + 1 + (1000 if vis else 0))
            tr = pl.concat([train.simulate(rng, ncycles=1500) for _ in range(3)])
            tg = pl.concat([target.simulate(rng, ncycles=1500) for _ in range(3)])
            b.append(fpkernel.fit(tr, level=level, floor=20, entry_df=tg)["ET"])
        res[f"visible={vis},level=M{level}"] = dict(truth_ET_target=truth, truth_ET_train=train.true_ET()[0], mean_rel_bias=float(np.mean(rel(np.array(b), truth))), sd_rel=float(np.std(rel(np.array(b), truth))), n=len(b))
    out["C2b"] = res
    out["pass_M0_fails"] = bool(abs(res["visible=False,level=M0"]["mean_rel_bias"]) > 0.20)
    out["pass_M1_visible_ok"] = bool(abs(res["visible=True,level=M1"]["mean_rel_bias"]) < 0.10)
    return out


if __name__ == "__main__" and "--c2b" in sys.argv:
    r = run_c2b()
    (EXP / "results" / "calibration_c2b.json").write_text(json.dumps(r, indent=2, sort_keys=True))
    print(json.dumps(r, indent=2, sort_keys=True))


def run_c5(ndata=400, nboot=1000) -> dict:
    """Coverage of the percentile family bootstrap used by analyze.py (12 groups x 4 rules)."""
    out = {"seed_base": BASE_SEED + 800}
    rows = []
    for icc, mu in [(0.3, 0.3), (0.6, 0.3), (0.3, 0.0)]:  # (share of variance between families, true mean improvement)
        rng = np.random.default_rng(BASE_SEED + 800 + int(10 * icc) + int(100 * mu))
        cover, width = 0, []
        for _ in range(ndata):
            g = rng.normal(0, np.sqrt(icc), 12)
            d = mu + g[:, None] + rng.normal(0, np.sqrt(1 - icc), (12, 4))  # paired improvements per rule
            est = d.mean()
            boots = np.array([d[rng.integers(0, 12, 12)].mean() for _ in range(nboot)])
            lo, hi = np.quantile(boots, [0.025, 0.975])
            cover += lo <= mu <= hi
            width.append(hi - lo)
        rows.append(dict(between_family_share=icc, true_mean=mu, coverage=cover / ndata, mean_width=float(np.mean(width))))
    out["rows"] = rows
    out["pass"] = bool(all(0.90 <= r["coverage"] <= 0.99 for r in rows))
    return out


if __name__ == "__main__" and "--c5" in sys.argv:
    r = run_c5()
    (EXP / "results" / "calibration_c5.json").write_text(json.dumps(r, indent=2, sort_keys=True))
    print(json.dumps(r, indent=2, sort_keys=True))
