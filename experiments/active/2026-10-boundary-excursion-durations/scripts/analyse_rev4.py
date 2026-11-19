# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy>=1.26"]
# ///
"""Revision 4 walker calibration analysis (README "Revision 4 registration").

Reads results/rev4_calib_{windows,dhist}.csv. Gates: C1E-d (eden -> area), C1I-d (idla -> area),
C-line (bal -> line). Report-only: idlar, mf, rotor; revisit readout gamma for every kind.
Writes results/rev4_analysis.{json,txt}.
"""
from __future__ import annotations

import json
import math
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import analyse as A  # noqa: E402  (frozen loader)
import depth_score as ds  # noqa: E402

RES = Path(__file__).resolve().parents[1] / "results"
KINDS = ("eden", "idla", "bal", "idlar", "mf", "rotor")
GATES = {"eden": ("C1E-d", "area"), "idla": ("C1I-d", "area"), "bal": ("C-line", "line")}
PRED = {"idlar": "area", "mf": "not line (probably area)", "rotor": "area (~55-60%)"}


def main():
    windows = A.load_windows(RES / "rev4_calib_windows.csv")
    dh = ds.load_dhist(RES / "rev4_calib_dhist.csv")
    lines, rep = [], {}

    def say(s=""):
        lines.append(s)

    say("Rev4 walker calibration: depth–duration exponent beta (area >= 1.70, line <= 1.30)")
    for kind in KINDS:
        kept, drop = [], defaultdict(int)
        for w in windows:
            if w["spec"].split(":")[0] != kind or not (ds.K_LO <= w["k"] <= ds.K_HI):
                continue
            reason = None
            if w["escaped"]:
                reason = "escaped"
            elif w["n_completed"] < 200:
                reason = "n_completed<200"
            elif w["censored_step_share"] > 0.20:
                reason = "censored_share>0.20"
            elif not math.isfinite(w["L"]) or w["L"] < ds.L_MIN:
                reason = "L<12"
            axes = dh.get((w["spec"], w["k"]), {})
            if reason is None:
                b, nb, span = ds.window_beta(axes.get("d", []), w["L"])
                if b is None:
                    reason = "not fittable"
            if reason:
                drop[reason] += 1
                continue
            kept.append({"seed": w["spec"].split(":")[1], "k": w["k"], "L": w["L"], "beta": b, "nbins": nb,
                         "span": span, "share": ds.fitted_time_share(axes["d"], w["L"]),
                         "gamma": ds.window_gamma(axes.get("tau", []), w["L"])})
        s = ds.kind_summary(kept)
        g = [w["gamma"] for w in kept if w["gamma"] is not None]
        s["gamma"] = float(np.median(g)) if g else None
        s["gamma_windows"] = len(g)
        s["fit_time_share_median"] = float(np.median([w["share"] for w in kept])) if kept else None
        s["L_range"] = [min(w["L"] for w in kept), max(w["L"] for w in kept)] if kept else None
        s["beta_range"] = [min(w["beta"] for w in kept), max(w["beta"] for w in kept)] if kept else None
        s["dropped"] = dict(drop)
        s["windows"] = kept
        rep[kind] = s
        role = f"gate {GATES[kind][0]} (predict {GATES[kind][1]})" if kind in GATES else f"report-only (predict {PRED[kind]})"
        say(f"\n{kind}: {role}")
        say(f"  retained {s['n_windows']} windows, dropped {dict(drop)}; L {s['L_range']}")
        if s["beta"] is not None:
            say(f"  beta median {s['beta']:.3f}  range {s['beta_range'][0]:.3f}..{s['beta_range'][1]:.3f}  call {s['call'].upper()}")
            say("  per-seed medians " + ", ".join(f"{k}: {v:.3f}" for k, v in s["seed_medians"].items())
                + f"; between-seed SD {s['between_seed_sd']:.3f}")
            say(f"  time share in fitted d-range (median over windows) {s['fit_time_share_median']:.3f}")
        say(f"  revisit gamma median {s['gamma']} over {s['gamma_windows']} windows (report-only)")
    say("\nGates:")
    ok = True
    for kind, (name, want) in GATES.items():
        p = rep[kind]["call"] == want
        ok &= p
        rep[name] = "PASS" if p else "FAIL"
        say(f"  {name}: {kind} -> {rep[kind]['call']} (need {want}) {'PASS' if p else 'FAIL'}")
    rep["walker_gates"] = "PASS" if ok else "FAIL"
    say(f"  walker gates overall: {rep['walker_gates']}")
    (RES / "rev4_analysis.json").write_text(json.dumps(rep, indent=1, default=float))
    (RES / "rev4_analysis.txt").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
