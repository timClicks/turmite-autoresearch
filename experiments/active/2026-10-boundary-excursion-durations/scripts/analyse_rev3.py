# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy>=1.26"]
# ///
"""Revision 3 walker calibration analysis (README "Revision 3 registration").

Reads results/rev3_calib_{windows,hist,fhist}.csv. Gates: C1E-tw (eden), C1I-tw (idla), C2-tw (mf);
idlar diagnostic; rotor reported. Replication line: frozen Rev2 number-weighted analyse_kind.
Writes results/rev3_analysis.{json,txt}.
"""
from __future__ import annotations

import csv
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import analyse as A  # noqa: E402  (frozen Rev2 code: loaders, retention, compactness, number-weighted)
import tw_score as tw  # noqa: E402

RES = Path(__file__).resolve().parents[1] / "results"
KINDS = ("eden", "idla", "idlar", "mf", "rotor")


def load_fhist(path: Path):
    h = defaultdict(dict)
    with path.open() as f:
        for r in csv.DictReader(f):
            h[(r["spec"], int(r["k"]))][int(r["fine"])] = (int(r["count"]), int(r["sum_tau"]))
    return h


def retained_tw(kind, windows, fh):
    kept, dropped = [], defaultdict(int)
    for w in windows:
        if A.kind_of(w["spec"]) != kind or not (A.K_LO <= w["k"] <= A.K_HI):
            continue
        reason = None
        if w["escaped"]:
            reason = "escaped"
        elif w["n_completed"] < 200:
            reason = "n_completed<200"
        elif w["censored_step_share"] > 0.20:
            reason = "censored_share>0.20"
        elif not math.isfinite(w["L"]) or w["L"] < 4:
            reason = "L<4"
        fb = fh.get((w["spec"], w["k"]), {})
        st = tw.window_stats(fb)
        if reason is None and st["n"] < 200:
            reason = "durations<200"
        if reason is None and st["n_eff"] < tw.NEFF_MIN:
            reason = "n_eff<30"
        if reason:
            dropped[reason] += 1
            continue
        cens = float(w["unresolved_steps"]) if (w["n_censored"] > 0 and w["unresolved_steps"] > 0) else None
        kept.append({"spec": w["spec"], "k": w["k"], "L": w["L"], "area": w["area"], "perimeter": w["perimeter"],
                     "fbins": fb, "censored_tau": cens, "n": st["n"], "n_eff": st["n_eff"], "total": st["total"]})
    return kept, dict(dropped)


def main():
    windows = A.load_windows(RES / "rev3_calib_windows.csv")
    hist = A.load_hist(RES / "rev3_calib_hist.csv")
    fh = load_fhist(RES / "rev3_calib_fhist.csv")
    rep, lines = {"kinds": {}, "gates": {}}, []

    def say(s=""):
        print(s)
        lines.append(s)

    say("Revision 3 calibration — time-weighted survival Score (frozen rules, fresh seeds 2026102951..54)")
    for kind in KINDS:
        kept, dropped = retained_tw(kind, windows, fh)
        res = tw.score_tw(kept)
        comp = A.compactness([({"L": w["L"], "area": w["area"], "perimeter": w["perimeter"]}, None, None) for w in kept])
        nw = A.analyse_kind(kind, windows, hist)  # frozen Rev2 number-weighted (replication line)
        tw_mean_over_L = sum(w["total"] for w in kept) and float(
            sum((sum(s * s / c for c, s in w["fbins"].values()) / w["total"]) / w["L"] for w in kept) / len(kept))
        rep["kinds"][kind] = {"n_retained": len(kept), "dropped": dropped, "tw": res, "compactness": comp,
                              "nw": {k: nw[k] for k in ("n_retained_windows", "Score_L", "Score_L2", "verdict",
                                                         "mean_tau_over_L", "censoring_fragile", "L_range_ratio")},
                              "tw_mean_over_L_approx": tw_mean_over_L,
                              "min_n_eff": min((w["n_eff"] for w in kept), default=None)}
        f = lambda x: "nan" if x is None or not math.isfinite(x) else f"{x:.4f}"  # noqa: E731
        say(f"{kind:6s} retained {len(kept)} (dropped {dropped}); L {f(res.get('L_min'))}..{f(res.get('L_max'))} "
            f"(ratio {f(res.get('L_range_ratio'))}); Score_tw(L) {f(res['Score_L'])} vs (L^2) {f(res['Score_L2'])} "
            f"-> {res['verdict']}; censored-incl {f(res['Score_L_cens'])} vs {f(res['Score_L2_cens'])} -> {res['verdict_cens']}; "
            f"compactness {comp['pass']} ({comp['reason']}; L {f(comp['L_range_ratio'])}, A {f(comp['A_range_ratio'])}, "
            f"A/P^2 {f(comp['median_A_over_P2'])}); min n_eff {f(rep['kinds'][kind]['min_n_eff'])}")
        say(f"       number-weighted (Rev2 frozen, replication): {f(nw['Score_L'])} vs {f(nw['Score_L2'])} -> {nw['verdict']}; "
            f"mean tau/L {f(nw['mean_tau_over_L'])}; time-weighted mean/L ~ {f(tw_mean_over_L)}")

    K = rep["kinds"]
    def c1(kind):
        r = K[kind]
        return bool(r["compactness"]["pass"] and r["tw"]["verdict"] == "D" and not r["tw"]["censoring_fragile"])
    g = {"C1E-tw": c1("eden"), "C1I-tw": c1("idla")}
    mr = K["mf"]["nw"]["mean_tau_over_L"]
    g["C2-tw"] = bool(K["mf"]["tw"]["verdict"] == "S" and mr is not None and 0.5 <= mr <= 2.0)
    g["calibrated_for_excluded_pilot"] = all(g.values())
    rep["gates"] = g
    for name, v in g.items():
        say(f"{name}: {'PASS' if v else 'FAIL'}")
    say(f"idlar (diagnostic, predicted D): {K['idlar']['tw']['verdict']}; rotor (reported, guess S): {K['rotor']['tw']['verdict']}")

    def clean(o):
        if isinstance(o, float) and not math.isfinite(o):
            return None
        if isinstance(o, dict):
            return {k: clean(v) for k, v in o.items()}
        if isinstance(o, list):
            return [clean(v) for v in o]
        return o
    (RES / "rev3_analysis.json").write_text(json.dumps(clean(rep), indent=1))
    (RES / "rev3_analysis.txt").write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
