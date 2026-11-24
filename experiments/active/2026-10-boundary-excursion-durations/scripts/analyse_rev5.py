# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy>=1.26"]
# ///
"""Revision 5 excluded ant pilot readout (README "Revision 5 registration").

Reads results/rev5_pilot_{windows,fhist,dhist}.csv. Per rule (4 seeds pooled):
Score_tw verdict (Rev3 retention + tw_score, unchanged), beta call (Rev4 retention + depth_score, unchanged),
fit coverage, shallow (d <= 3) time share, report-only gamma; frozen agreement table; flags L-range-fragile
(L <= 50.7) and seed-heterogeneous. Writes results/rev5_analysis.{json,txt}. EXCLUDED pilot: not evidence for
confirmation; no diffusion claim.
"""
from __future__ import annotations

import json
import math
import os
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import analyse as A  # noqa: E402  (frozen loader)
import analyse_rev3 as R3  # noqa: E402  (frozen Score_tw retention: retained_tw, load_fhist)
import depth_score as ds  # noqa: E402
import tw_score as tw  # noqa: E402

RES = Path(__file__).resolve().parents[1] / "results"
# Self-test only (see scripts/selftest_rev5.sh): read/write another directory instead of results/.
if os.environ.get("REV5_SELFTEST_DIR"):
    RES = Path(os.environ["REV5_SELFTEST_DIR"])
RULES = ("RLLR", "RLLRL", "RLLLRR", "RLLLLRLL")
COVER_MIN = 0.05
L_CAL_MAX = 50.7
SHALLOW_HI = 3


def rule_of(spec: str) -> str:
    return spec.split("@")[0]


def seed_of(spec: str) -> str:
    return spec.split("@")[1]


def retained_beta(windows, dh):
    """Rev4 retention and per-window fit, copied from analyse_rev4.main (unchanged), keyed by spec."""
    kept, drop = [], defaultdict(int)
    for w in windows:
        if not (ds.K_LO <= w["k"] <= ds.K_HI):
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
        drows = axes["d"]
        tot = sum(r[3] for r in drows)
        shallow = sum(r[3] for r in drows if r[1] <= SHALLOW_HI)
        kept.append({"spec": w["spec"], "seed": seed_of(w["spec"]), "k": w["k"], "L": w["L"], "beta": b, "nbins": nb,
                     "span": span, "share": ds.fitted_time_share(drows, w["L"]),
                     "gamma": ds.window_gamma(axes.get("tau", []), w["L"]),
                     "time_total": tot, "time_shallow": shallow})
    return kept, dict(drop)


def beta_readout(kept):
    s = ds.kind_summary(kept)
    s["fit_time_share_median"] = float(np.median([w["share"] for w in kept])) if kept else None
    tot = sum(w["time_total"] for w in kept)
    s["shallow_time_share"] = (sum(w["time_shallow"] for w in kept) / tot) if tot else None
    g = [w["gamma"] for w in kept if w["gamma"] is not None]
    s["gamma_report_only"] = float(np.median(g)) if g else None
    s["L_range"] = [min(w["L"] for w in kept), max(w["L"] for w in kept)] if kept else None
    s["beta_range"] = [min(w["beta"] for w in kept), max(w["beta"] for w in kept)] if kept else None
    call = s["call"]
    if call in ("area", "line") and (s["fit_time_share_median"] is None or s["fit_time_share_median"] < COVER_MIN):
        call = "covers little of the time"
    s["call_read"] = call
    return s


def reading(tw_verdict: str, beta_call: str) -> tuple[str, str | None]:
    if tw_verdict not in ("D", "S"):
        return "UNREAD", f"Score_tw {tw_verdict}"
    if beta_call not in ("area", "line"):
        return "UNREAD", f"beta {beta_call}"
    if tw_verdict == "D" and beta_call == "area":
        return "AREA-FILLING", None
    if tw_verdict == "S" and beta_call == "line":
        return "LINE-LIKE", None
    return "DISAGREE", None


def overall(readings: list[str]) -> str:
    n = len(readings)
    c = {r: readings.count(r) for r in ("AREA-FILLING", "LINE-LIKE", "DISAGREE", "UNREAD")}
    if c["AREA-FILLING"] == n:
        return "4/4 AREA-FILLING"
    if c["LINE-LIKE"] == n:
        return "4/4 LINE-LIKE"
    if c["UNREAD"] >= 2:
        return ">=2 UNREAD: pilot uninformative for ants at this horizon"
    if c["DISAGREE"] >= 1 or (c["AREA-FILLING"] >= 1 and c["LINE-LIKE"] >= 1):
        return "rule-dependent or instrument-disagreeing; no family-level reading"
    return "counts only; no family-level reading"


def clean(o):
    if isinstance(o, float) and not math.isfinite(o):
        return None
    if isinstance(o, dict):
        return {k: clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [clean(v) for v in o]
    if isinstance(o, np.floating):
        return clean(float(o))
    return o


def main():
    windows = A.load_windows(RES / "rev5_pilot_windows.csv")
    fh = R3.load_fhist(RES / "rev5_pilot_fhist.csv")
    dh = ds.load_dhist(RES / "rev5_pilot_dhist.csv")
    lines, rep = [], {"rules": {}}

    def say(s=""):
        lines.append(s)

    f = lambda x: "nan" if x is None or (isinstance(x, float) and not math.isfinite(x)) else f"{x:.4f}"  # noqa: E731
    say("Rev5 EXCLUDED ant pilot: Score_tw (Rev3) + beta (Rev4), frozen rules; seeds 2026112501..04. Not evidence for confirmation;")
    say("no diffusion claim (neither readout separates diffusion from area-filling sweeps).")
    escaped = sorted({w["spec"] for w in windows if w["escaped"]})
    say(f"specs: {len({w['spec'] for w in windows})}; escaped specs: {escaped or 'none'}")
    for rule in RULES:
        ws = [w for w in windows if rule_of(w["spec"]) == rule]
        kept_tw, drop_tw = R3.retained_tw("ant", ws, fh)
        twr = tw.score_tw(kept_tw)
        kept_b, drop_b = retained_beta(ws, dh)
        br = beta_readout(kept_b)
        rd, why = reading(twr["verdict"], br["call_read"])
        # Flag: L-range-fragile.
        twr_c = tw.score_tw([w for w in kept_tw if w["L"] <= L_CAL_MAX])
        br_c = beta_readout([w for w in kept_b if w["L"] <= L_CAL_MAX])
        rd_c, why_c = reading(twr_c["verdict"], br_c["call_read"])
        # Flag: seed-heterogeneous.
        seeds = sorted({seed_of(w["spec"]) for w in ws})
        seed_tw = {s: tw.score_tw([w for w in kept_tw if seed_of(w["spec"]) == s])["verdict"] for s in seeds}
        nwin_seed = defaultdict(int)
        for w in kept_b:
            nwin_seed[w["seed"]] += 1
        seed_b = {s: ds.call(v, nwin_seed[s]) for s, v in br["seed_medians"].items()}
        het = ({"area", "line"} <= set(seed_b.values())) or ({"D", "S"} <= set(seed_tw.values()))
        cens_mass = max((w["censored_tau"] or 0.0) / w["total"] for w in kept_tw) if kept_tw else None
        r = {"reading": rd, "unread_reason": why,
             "score_tw": {k: twr.get(k) for k in ("Score_L", "Score_L2", "verdict", "verdict_primary", "Score_L_cens",
                                                   "Score_L2_cens", "verdict_cens", "L_min", "L_max", "L_range_ratio")},
             "score_tw_retained": len(kept_tw), "score_tw_dropped": drop_tw, "max_censored_mass_share": cens_mass,
             "beta": {k: br[k] for k in ("beta", "call", "call_read", "n_windows", "seed_medians", "between_seed_sd",
                                         "fit_time_share_median", "shallow_time_share", "gamma_report_only",
                                         "L_range", "beta_range")},
             "beta_dropped": drop_b,
             "beta_windows": [{k: w[k] for k in ("spec", "k", "L", "beta", "nbins", "span", "share")} for w in kept_b],
             "L_le_50.7": {"score_tw_verdict": twr_c["verdict"], "Score_L": twr_c["Score_L"], "Score_L2": twr_c["Score_L2"],
                           "tw_windows": sum(1 for w in kept_tw if w["L"] <= L_CAL_MAX),
                           "beta": br_c["beta"], "beta_call": br_c["call_read"], "beta_windows": br_c["n_windows"],
                           "reading": rd_c, "unread_reason": why_c},
             "L_range_fragile": rd_c != rd,
             "seed_score_tw": seed_tw, "seed_beta_call": seed_b, "seed_heterogeneous": bool(het)}
        rep["rules"][rule] = r
        say(f"\n{rule}: reading {rd}{' (' + why + ')' if why else ''}"
            f"{'  [L-range-fragile]' if r['L_range_fragile'] else ''}{'  [seed-heterogeneous]' if het else ''}")
        say(f"  Score_tw: retained {len(kept_tw)} (dropped {drop_tw}); L {f(twr.get('L_min'))}..{f(twr.get('L_max'))} "
            f"(ratio {f(twr.get('L_range_ratio'))}); Score_tw(L) {f(twr['Score_L'])} vs (L^2) {f(twr['Score_L2'])} -> "
            f"{twr['verdict']}; censored-incl {f(twr['Score_L_cens'])} vs {f(twr['Score_L2_cens'])} -> {twr['verdict_cens']}; "
            f"max censored mass share {f(cens_mass)}")
        say(f"  beta: retained {br['n_windows']} (dropped {drop_b}); median {f(br['beta'])} range "
            f"{br['beta_range']} -> {br['call']} (read: {br['call_read']}); fit-range time share {f(br['fit_time_share_median'])}; "
            f"shallow d<=3 time share {f(br['shallow_time_share'])}; gamma (report-only) {f(br['gamma_report_only'])}")
        say("  per-seed beta medians " + ", ".join(f"{k}: {v:.3f}" for k, v in br["seed_medians"].items())
            + f"; between-seed SD {f(br['between_seed_sd'])}; per-seed Score_tw {seed_tw}")
        say(f"  L <= 50.7 sensitivity: Score_tw {twr_c['verdict']} ({f(twr_c['Score_L'])} vs {f(twr_c['Score_L2'])}, "
            f"{r['L_le_50.7']['tw_windows']} windows); beta {f(br_c['beta'])} -> {br_c['call_read']} "
            f"({br_c['n_windows']} windows); reading {rd_c}")
    rds = [rep["rules"][r]["reading"] for r in RULES]
    rep["counts"] = {k: rds.count(k) for k in ("AREA-FILLING", "LINE-LIKE", "DISAGREE", "UNREAD")}
    rep["overall"] = overall(rds)
    say(f"\nCounts: {rep['counts']}")
    say(f"Overall (frozen statement): {rep['overall']}")
    (RES / "rev5_analysis.json").write_text(json.dumps(clean(rep), indent=1))
    (RES / "rev5_analysis.txt").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
