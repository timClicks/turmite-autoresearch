# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy>=1.26"]
# ///
"""Revision 5 POST HOC diagnostic (not registered; descriptive only): why the frozen retention left 3/4 rules UNREAD.

Per rule over band windows k = 16..24 (all 4 seeds): effective sample size n_eff of the time-weighted law, the share of
completed off-boundary time in fine bins with lo > L^2, the number of d-bins in [4, floor L] with count >= 20 (the beta
fit needs >= 4), counts of completed excursions with d in [4, floor L] and with d > floor L, and max d / L.
Reads results/rev5_pilot_{windows,fhist,dhist}.csv; writes results/rev5_diag.txt. Nothing here changes any reading.

Review fixes (2026-11-26, still POST HOC, no new ant runs):
  * `--res DIR [--out FILE] [--note TEXT]` runs the same diagnostic on any directory holding rev5_pilot_*.csv files.
    The Rev4 calibration walkers are relabelled as fake ant specs by `scripts/selftest_rev5.sh` (eden->RLLR, bal->RLLRL,
    rotor->RLLLRR, idla->RLLLLRLL) into scratch/rev5_selftest/; the committed output is results/rev5_diag_calibrators.txt.
  * A per-log-band density section (counts and time by d/L and by tau/L^2) tests the "bimodal" wording.
    Approximation: each instrument bin (d-bin or fine tau bin) is assigned wholly to the band holding its geometric
    midpoint, so bins that straddle a band edge leak into the neighbouring band. The band shares are descriptive,
    not exact octave shares (review 2026-11-27, Minor 7).
  * Review 2026-11-27 (S1 follow-up): `scripts/calib_idlar_rev5.sh` repeats the calibrator run with `idlar` (IDLA with
    restart-launched excursions dropped) in the RLLLLRLL slot -> results/rev5_diag_calibrators_idlar.txt.
Recipe: bash scripts/selftest_rev5.sh; uv run --frozen python scripts/diag_rev5.py;
        uv run --frozen python scripts/diag_rev5.py --res scratch/rev5_selftest --out results/rev5_diag_calibrators.txt \
            --note "CALIBRATORS relabelled: RLLR=eden RLLRL=bal RLLLRR=rotor RLLLLRLL=idla (Rev4 walker calibration data, no ants)"
"""
from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import analyse as A  # noqa: E402
import analyse_rev3 as R3  # noqa: E402
import depth_score as ds  # noqa: E402
import tw_score as tw  # noqa: E402

RES = Path(__file__).resolve().parents[1] / "results"
RULES = ("RLLR", "RLLRL", "RLLLRR", "RLLLLRLL")


def q(v):
    a = np.asarray(v, float)
    return f"median {np.median(a):.3g} [min {a.min():.3g}, max {a.max():.3g}]"


D_EDGES = [0, 1 / 16, 1 / 8, 1 / 4, 1 / 2, 1, 2, math.inf]  # excursion depth d / L
T_EDGES = [0, 1 / 4, 1, 4, 16, 64, math.inf]  # excursion duration tau / L^2


def band(x, edges):
    for i in range(len(edges) - 1):
        if edges[i] <= x < edges[i + 1]:
            return i
    return len(edges) - 2


def label(edges):
    return [f"[{lo:.3g},{hi:.3g})" for lo, hi in zip(edges, edges[1:])]


def band_profile(W, fh, dh, rule):
    """Bins are assigned wholly to the band of their geometric midpoint (approximate at band edges).
    Median over band windows of the per-window share of completed excursions (count) and of completed
    off-boundary time (sum tau) in log-spaced bands of d/L and of tau/L^2. A dip between a shallow and a deep
    mode would show as a middle band lower than both neighbours; a monotone fall is heavy-tailed, not bimodal."""
    dc, dt, tc, tt = [], [], [], []
    for w in W:
        if w["spec"].split("@")[0] != rule or not (16 <= w["k"] <= 24):
            continue
        L = w["L"]
        c = np.zeros(len(D_EDGES) - 1)
        t = np.zeros(len(D_EDGES) - 1)
        for lo, hi, n, stau, _sd, _sx in dh[(w["spec"], w["k"])]["d"]:
            b = band(math.sqrt(max(lo, 1) * max(hi, 1)) / L, D_EDGES)
            c[b] += n
            t[b] += stau
        dc.append(c / c.sum())
        dt.append(t / t.sum())
        c = np.zeros(len(T_EDGES) - 1)
        t = np.zeros(len(T_EDGES) - 1)
        for f, (n, stau) in fh.get((w["spec"], w["k"]), {}).items():
            lo, hi = tw.fine_range(f)
            b = band(math.sqrt(max(lo, 1) * max(hi, 1)) / L**2, T_EDGES)
            c[b] += n
            t[b] += stau
        tc.append(c / c.sum())
        tt.append(t / t.sum())
    med = lambda a: np.median(np.array(a), axis=0)
    lines = []
    for name, edges, cc, ttm in (("d/L", D_EDGES, dc, dt), ("tau/L^2", T_EDGES, tc, tt)):
        lines.append(f"  by {name} band (median over windows of the share of completed excursions | of completed time):")
        for lab, a, b in zip(label(edges), med(cc), med(ttm)):
            lines.append(f"    {lab:>14}: count share {a:.3f} | time share {b:.3f}")
    return lines


def main(res=RES, out_path=None, note=None):
    W = A.load_windows(res / "rev5_pilot_windows.csv")
    fh = R3.load_fhist(res / "rev5_pilot_fhist.csv")
    dh = ds.load_dhist(res / "rev5_pilot_dhist.csv")
    out = ["Rev5 POST HOC diagnostic (descriptive; not registered; changes no reading). Band k=16..24"
           + (", 36 windows per rule." if note is None else f". {note}")]
    for rule in RULES:
        neff, big, nbins, nmid, ndeep, dmax, ncomp, tl2, twin, ta = [], [], [], [], [], [], [], [], [], []
        for w in W:
            if w["spec"].split("@")[0] != rule or not (16 <= w["k"] <= 24):
                continue
            fb = fh.get((w["spec"], w["k"]), {})
            st = tw.window_stats(fb)
            neff.append(st["n_eff"])
            big.append(sum(s for f, (c, s) in fb.items() if tw.fine_range(f)[0] > w["L"] ** 2) / st["total"])
            d = dh[(w["spec"], w["k"])]["d"]
            lm = math.floor(w["L"])
            nbins.append(sum(1 for r in d if r[0] >= 4 and r[1] <= lm and r[2] >= 20))
            nmid.append(sum(r[2] for r in d if r[0] >= 4 and r[1] <= lm))
            ndeep.append(sum(r[2] for r in d if r[1] > lm))
            dmax.append(max(r[1] for r in d) / w["L"])
            ncomp.append(w["n_completed"])
            tmax = max(tw.fine_range(f)[0] for f, (c, s) in fb.items() if c > 0)
            tl2.append(tmax / w["L"] ** 2)
            twin.append(tmax / 2 ** (w["k"] - 1))
            ta.append(tmax / w["area"])
        out.append(f"\n{rule}")
        out.append(f"  n_completed per window: {q(ncomp)}")
        out.append(f"  n_eff (frozen floor 30): {q(neff)}; windows with n_eff >= 30: {sum(x >= 30 for x in neff)}/36")
        out.append(f"  time share in excursions with tau > L^2: {q(big)}")
        out.append(f"  d-bins in [4, L] with count >= 20 (fit needs >= 4): {q(nbins)}")
        out.append(f"  completed excursions with 4 <= d <= L: {q(nmid)}; with d > L: {q(ndeep)}")
        out.append(f"  max d / L (bin upper edge): {q(dmax)}")
        out.append(f"  longest completed tau (fine-bin lower edge) / L^2: {q(tl2)}; / window length 2^(k-1): {q(twin)}; / area A: {q(ta)}")
        if note is not None:
            out.append(f"  windows in band: {len(neff)}")
    out.append("\nPer-log-band density (post hoc test of 'bimodal'; added 2026-11-26 in response to review finding S3)")
    for rule in RULES:
        out.append(f"\n{rule}")
        out += band_profile(W, fh, dh, rule)
    (out_path or res / "rev5_diag.txt").write_text("\n".join(out) + "\n")
    print("\n".join(out))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--res", type=Path, default=RES, help="directory with rev5_pilot_{windows,fhist,dhist}.csv")
    ap.add_argument("--out", type=Path, default=None, help="output path (default: <res>/rev5_diag.txt)")
    ap.add_argument("--note", default=None, help="header note (marks a non-ant run)")
    a = ap.parse_args()
    main(a.res.resolve(), a.out.resolve() if a.out else None, a.note)
