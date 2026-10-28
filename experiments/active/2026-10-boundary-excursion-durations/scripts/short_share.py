#!/usr/bin/env python3
"""Post hoc, exploratory (NOTEBOOK 2026-10-28 16:50 plan): share of completed
excursions and of off-boundary time contributed by short excursions in the
Rev2 calibration data. Not a gate. Cutoff fixed before computing: tau <= 3
(log2 bins 0-1); tau <= 7 (bins 0-2) reported as sensitivity only.
Retention filters are imported from analyse.py so they match the Score.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import analyse as A  # noqa: E402

RES = Path(__file__).resolve().parent.parent / "results"
KINDS = ["eden", "idla", "mf", "rotor"]
CUTS = {"tau_le_3": 1, "tau_le_7": 2}  # highest log2 bin included


def retained(kind, windows, hist):
    for w in windows:
        if A.kind_of(w["spec"]) != kind or not (A.K_LO <= w["k"] <= A.K_HI):
            continue
        if w["escaped"] or w["n_completed"] < 200 or w["censored_step_share"] > 0.20:
            continue
        if not math.isfinite(w["L"]) or w["L"] < 4:
            continue
        bins = hist.get((w["spec"], w["k"]), {"bins": {}})["bins"]
        if sum(bins.values()) < 200:
            continue
        yield w, bins


def main():
    windows = A.load_windows(RES / "rev2_calib_windows.csv")
    hist = A.load_hist(RES / "rev2_calib_hist.csv")
    out, lines = {}, []
    for kind in KINDS:
        rows = list(retained(kind, windows, hist))
        n_all = sum(sum(b.values()) for _, b in rows)
        interior = sum(w["interior_steps"] for w, _ in rows)
        comp_lo = sum(c * 2 ** b for _, bs in rows for b, c in bs.items())
        comp_hi = sum(c * (2 ** (b + 1) - 1) for _, bs in rows for b, c in bs.items())
        rec = {"n_windows": len(rows), "n_completed": n_all, "interior_steps": interior,
               "completed_time_bracket": [comp_lo, comp_hi],
               "L_min": min(w["L"] for w, _ in rows), "L_max": max(w["L"] for w, _ in rows)}
        for name, bmax in CUTS.items():
            n_s = sum(c for _, bs in rows for b, c in bs.items() if b <= bmax)
            t_lo = sum(c * 2 ** b for _, bs in rows for b, c in bs.items() if b <= bmax)
            t_hi = sum(c * (2 ** (b + 1) - 1) for _, bs in rows for b, c in bs.items() if b <= bmax)
            rec[name] = {
                "count_share": n_s / n_all,
                "time_share_of_interior": [t_lo / interior, t_hi / interior],
                "time_share_of_completed": [t_lo / (t_lo + (comp_hi - t_hi)),
                                            t_hi / (t_hi + (comp_lo - t_lo))],
            }
        out[kind] = rec
        lines.append(f"{kind}: windows={len(rows)} completed={n_all} interior_steps={interior} "
                     f"L=[{rec['L_min']:.2f},{rec['L_max']:.2f}]")
        for name in CUTS:
            r = rec[name]
            lines.append(f"  {name}: count_share={r['count_share']:.4f} "
                         f"time_share_of_interior=[{r['time_share_of_interior'][0]:.4f},{r['time_share_of_interior'][1]:.4f}] "
                         f"time_share_of_completed=[{r['time_share_of_completed'][0]:.4f},{r['time_share_of_completed'][1]:.4f}]")
    txt = "# Post hoc exploratory (not a gate): short-excursion shares, Rev2 calib\n" + "\n".join(lines) + "\n"
    (RES / "rev2_short_share.txt").write_text(txt)
    (RES / "rev2_short_share.json").write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    print(txt, end="")


if __name__ == "__main__":
    main()
