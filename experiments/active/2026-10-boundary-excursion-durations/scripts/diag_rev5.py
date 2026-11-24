# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy>=1.26"]
# ///
"""Revision 5 POST HOC diagnostic (not registered; descriptive only): why the frozen retention left 3/4 rules UNREAD.

Per rule over band windows k = 16..24 (all 4 seeds): effective sample size n_eff of the time-weighted law, the share of
completed off-boundary time in fine bins with lo > L^2, the number of d-bins in [4, floor L] with count >= 20 (the beta
fit needs >= 4), counts of completed excursions with d in [4, floor L] and with d > floor L, and max d / L.
Reads results/rev5_pilot_{windows,fhist,dhist}.csv; writes results/rev5_diag.txt. Nothing here changes any reading.
"""
from __future__ import annotations

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


def main():
    W = A.load_windows(RES / "rev5_pilot_windows.csv")
    fh = R3.load_fhist(RES / "rev5_pilot_fhist.csv")
    dh = ds.load_dhist(RES / "rev5_pilot_dhist.csv")
    out = ["Rev5 POST HOC diagnostic (descriptive; not registered; changes no reading). Band k=16..24, 36 windows per rule."]
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
    (RES / "rev5_diag.txt").write_text("\n".join(out) + "\n")
    print("\n".join(out))


if __name__ == "__main__":
    main()
