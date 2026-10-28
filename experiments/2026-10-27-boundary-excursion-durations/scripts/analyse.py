# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy>=1.26"]
# ///
"""Stage-1 collapse scores for boundary excursion durations.

Reads results/{calib,pilot}_{windows,hist}.csv; writes results/analysis.json,
results/analysis.txt and results/figures/*.png (optional, if matplotlib present).

Frozen decision rule (README): prefer D if Score(L^2) <= 0.75 * Score(L);
prefer S if Score(L) <= 0.75 * Score(L^2); else inconclusive. Uninformative if
L_max/L_min < 2 among retained windows. Censoring-fragile if KM preference flips.
"""
from __future__ import annotations

import csv
import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np

EXP = Path(__file__).resolve().parents[1]
RES = EXP / "results"
K_LO, K_HI = 16, 24
MARGIN = 0.75
U_GRID = np.array([2 ** (-8 + j / 2) for j in range(33)], dtype=float)  # 1/256 .. 16


def load_windows(path: Path):
    rows = []
    with path.open() as f:
        for r in csv.DictReader(f):
            rows.append({
                "spec": r["spec"],
                "k": int(r["k"]),
                "t_end": int(r["t_end"]),
                "area": int(r["area"]),
                "perimeter": int(r["perimeter"]),
                "new_cells": int(r["new_cells"]),
                "boundary_steps": int(r["boundary_steps"]),
                "interior_steps": int(r["interior_steps"]),
                "n_completed": int(r["n_completed"]),
                "n_censored": int(r["n_censored"]),
                "unresolved_steps": int(r["unresolved_steps"]),
                "L": float(r["L"]),
                "kappa": float(r["kappa"]),
                "censored_step_share": float(r["censored_step_share"]),
                "escaped": r["escaped"].lower() == "true",
            })
    return rows


def load_hist(path: Path):
    # (spec, k) -> list of (tau_mid, count) from log2 bins; censored as bin=-1
    h = defaultdict(lambda: {"bins": {}, "n_censored": 0})
    with path.open() as f:
        for r in csv.DictReader(f):
            key = (r["spec"], int(r["k"]))
            b = int(r["log2_tau"])
            c = int(r["count"])
            if b < 0:
                h[key]["n_censored"] += c
            else:
                h[key]["bins"][b] = h[key]["bins"].get(b, 0) + c
    return h


def kind_of(spec: str) -> str:
    if spec.startswith("mf:"):
        return "mf"
    if spec.startswith("rotor:"):
        return "rotor"
    if spec.startswith("rw:"):
        return "rw"
    for pre in ("eden", "idlar", "idla"):
        if spec.startswith(pre + ":"):
            return pre
    if spec.startswith("cup:"):
        # cup:P:SEED → cup:P (pool seeds per P)
        parts = spec.split(":")
        if len(parts) >= 2:
            return f"cup:{parts[1]}"
        return "cup"
    return "ant"


def expand_durations(bins: dict[int, int]) -> np.ndarray:
    """Representative tau = 2^b + 2^{b-1} (bin midpoint) repeated by count.
    For b=0, tau=1.
    """
    xs = []
    for b, c in bins.items():
        if c <= 0:
            continue
        tau = 1.0 if b == 0 else (2 ** b + 2 ** (b - 1))
        xs.extend([tau] * c)
    return np.asarray(xs, dtype=float)


def survival_on_grid(taus: np.ndarray, scale: float, grid: np.ndarray) -> np.ndarray:
    if scale <= 0 or len(taus) == 0:
        return np.full_like(grid, np.nan, dtype=float)
    u = taus / scale
    # S(u) = fraction with tau/scale > u
    return np.array([(u > uj).mean() for uj in grid], dtype=float)


def km_survival_on_grid(completed: np.ndarray, censored: np.ndarray, scale: float, grid: np.ndarray) -> np.ndarray:
    """Kaplan–Meier using completed durations and right-censored lengths (all / scale)."""
    if scale <= 0:
        return np.full_like(grid, np.nan, dtype=float)
    events = [(t / scale, True) for t in completed]
    events += [(t / scale, False) for t in censored if t > 0]
    if not events:
        return np.full_like(grid, np.nan, dtype=float)
    events.sort(key=lambda z: z[0])
    # Build KM as a step function of u
    n_at_risk = len(events)
    km_u = [0.0]
    km_s = [1.0]
    i = 0
    s = 1.0
    while i < len(events):
        u = events[i][0]
        d = 0
        c = 0
        while i < len(events) and events[i][0] == u:
            if events[i][1]:
                d += 1
            else:
                c += 1
            i += 1
        if n_at_risk > 0 and d > 0:
            s *= (1.0 - d / n_at_risk)
        km_u.append(u)
        km_s.append(s)
        n_at_risk -= d + c
    km_u = np.asarray(km_u)
    km_s = np.asarray(km_s)

    def S(uj):
        # right-continuous: value after last event <= uj
        idx = np.searchsorted(km_u, uj, side="right") - 1
        if idx < 0:
            return 1.0
        return float(km_s[idx])

    return np.array([S(uj) for uj in grid], dtype=float)


def pairwise_score(survivals: list[np.ndarray]) -> float:
    # Clip grid to points where at least one window has S in (0.05, 0.95)
    stack = np.vstack(survivals)
    mask = np.any((stack > 0.05) & (stack < 0.95), axis=0)
    if mask.sum() < 3:
        return float("nan")
    G = stack[:, mask]
    n = G.shape[0]
    if n < 2:
        return float("nan")
    acc = 0.0
    pairs = 0
    for i in range(n):
        for j in range(i + 1, n):
            acc += np.abs(G[i] - G[j]).mean()
            pairs += 1
    return float(acc / pairs)


def secondary_slopes(taus: np.ndarray, L: float) -> float | None:
    if len(taus) < 5 or not math.isfinite(L) or L < 4:
        return None
    lo = max(8.0, 0.25 * L)
    hi = 4.0 * L
    sel = taus[(taus >= lo) & (taus <= hi)]
    if len(sel) < 5:
        return None
    # empirical S at unique sorted tau
    uniq = np.unique(sel)
    if len(uniq) < 5:
        return None
    S = np.array([(taus > t).mean() for t in uniq])
    keep = (S > 0.05) & (S < 0.95)
    if keep.sum() < 5:
        return None
    x = np.log(uniq[keep])
    y = np.log(S[keep])
    # OLS slope
    x = x - x.mean()
    y = y - y.mean()
    den = (x * x).sum()
    if den <= 0:
        return None
    return float((x * y).sum() / den)


def analyse_kind(kind: str, windows, hist) -> dict:
    retained = []
    for w in windows:
        if kind_of(w["spec"]) != kind:
            continue
        if not (K_LO <= w["k"] <= K_HI):
            continue
        if w["escaped"]:
            continue
        if w["n_completed"] < 200:
            continue
        if w["censored_step_share"] > 0.20:
            continue
        if not math.isfinite(w["L"]) or w["L"] < 4:
            continue
        key = (w["spec"], w["k"])
        bins = hist.get(key, {"bins": {}, "n_censored": 0})["bins"]
        taus = expand_durations(bins)
        if len(taus) < 200:
            continue
        retained.append((w, taus, bins))

    out = {
        "kind": kind,
        "n_retained_windows": len(retained),
        "L_min": None,
        "L_max": None,
        "L_range_ratio": None,
        "uninformative": False,
        "Score_L": None,
        "Score_L2": None,
        "verdict": None,
        "mean_tau_over_L": None,
        "slopes": [],
        "Score_L_KM": None,
        "Score_L2_KM": None,
        "censoring_fragile": False,
        "windows": [],
    }
    if len(retained) < 2:
        out["uninformative"] = True
        out["verdict"] = "uninformative"
        return out

    Ls = [w["L"] for w, _, _ in retained]
    out["L_min"] = float(min(Ls))
    out["L_max"] = float(max(Ls))
    out["L_range_ratio"] = float(max(Ls) / min(Ls)) if min(Ls) > 0 else float("nan")
    if out["L_range_ratio"] < 2.0:
        out["uninformative"] = True
        out["verdict"] = "uninformative"
        # still compute scores for diagnostics
    surv_L, surv_L2 = [], []
    surv_L_km, surv_L2_km = [], []
    mean_ratios = []
    slopes = []
    for w, taus, bins in retained:
        surv_L.append(survival_on_grid(taus, w["L"], U_GRID))
        surv_L2.append(survival_on_grid(taus, w["L"] ** 2, U_GRID))
        # KM: treat unresolved as one censored at unresolved_steps (if any)
        cens = np.array([w["unresolved_steps"]], dtype=float) if w["n_censored"] > 0 and w["unresolved_steps"] > 0 else np.array([], dtype=float)
        surv_L_km.append(km_survival_on_grid(taus, cens, w["L"], U_GRID))
        surv_L2_km.append(km_survival_on_grid(taus, cens, w["L"] ** 2, U_GRID))
        mean_ratios.append(float(taus.mean() / w["L"]))
        sl = secondary_slopes(taus, w["L"])
        if sl is not None:
            slopes.append(sl)
        out["windows"].append({
            "spec": w["spec"],
            "k": w["k"],
            "L": w["L"],
            "kappa": w["kappa"],
            "n_completed": w["n_completed"],
            "censored_step_share": w["censored_step_share"],
            "mean_tau": float(taus.mean()),
            "slope": sl,
        })

    out["Score_L"] = pairwise_score(surv_L)
    out["Score_L2"] = pairwise_score(surv_L2)
    out["Score_L_KM"] = pairwise_score(surv_L_km)
    out["Score_L2_KM"] = pairwise_score(surv_L2_km)
    out["mean_tau_over_L"] = float(np.mean(mean_ratios)) if mean_ratios else None
    out["slopes"] = slopes

    def verdict(sL, sL2):
        if out["uninformative"]:
            return "uninformative"
        if not (math.isfinite(sL) and math.isfinite(sL2)):
            return "inconclusive"
        if sL2 <= MARGIN * sL:
            return "D"
        if sL <= MARGIN * sL2:
            return "S"
        return "inconclusive"

    out["verdict"] = verdict(out["Score_L"], out["Score_L2"])
    v_km = verdict(out["Score_L_KM"], out["Score_L2_KM"])
    if (not out["uninformative"]) and v_km != out["verdict"] and v_km != "uninformative":
        out["censoring_fragile"] = True
        out["verdict"] = "censoring-fragile"
    return out


def compactness(windows_retained: list) -> dict:
    """Revision-1 compactness pre-check on already-retained windows."""
    if len(windows_retained) < 2:
        return {
            "pass": False,
            "L_range_ratio": None,
            "A_range_ratio": None,
            "median_A_over_P2": None,
            "reason": "too few retained windows",
        }
    Ls = [w["L"] for w, _, _ in windows_retained]
    As = [w["area"] for w, _, _ in windows_retained]
    ap2 = [w["area"] / (w["perimeter"] ** 2) for w, _, _ in windows_retained if w["perimeter"] > 0]
    import statistics
    L_ratio = max(Ls) / min(Ls) if min(Ls) > 0 else float("nan")
    A_ratio = max(As) / min(As) if min(As) > 0 else float("nan")
    med = float(statistics.median(ap2)) if ap2 else float("nan")
    ok = (L_ratio >= 2.0) and (A_ratio >= 4.0) and (med >= 0.04)
    reasons = []
    if not (L_ratio >= 2.0):
        reasons.append(f"L_range {L_ratio:.4g} < 2")
    if not (A_ratio >= 4.0):
        reasons.append(f"A_range {A_ratio:.4g} < 4")
    if not (med >= 0.04):
        reasons.append(f"median A/P^2 {med:.4g} < 0.04")
    return {
        "pass": ok,
        "L_range_ratio": float(L_ratio),
        "A_range_ratio": float(A_ratio),
        "median_A_over_P2": med,
        "reason": "ok" if ok else "; ".join(reasons),
    }


def main():
    import sys
    mode = "stage1"
    if len(sys.argv) > 1 and sys.argv[1] in ("rev1", "rev2", "confirm"):
        mode = sys.argv[1]

    if mode == "stage1":
        win_path, hist_path = RES / "calib_windows.csv", RES / "calib_hist.csv"
        out_json, out_txt = RES / "analysis.json", RES / "analysis.txt"
        kinds = ("rw", "mf", "rotor")
        pilot = True
    elif mode == "rev1":
        win_path, hist_path = RES / "rev1_calib_windows.csv", RES / "rev1_calib_hist.csv"
        out_json, out_txt = RES / "rev1_analysis.json", RES / "rev1_analysis.txt"
        kinds = ("cup:0.05", "cup:0.10", "cup:0.25", "mf", "rotor")
        pilot = False
    elif mode == "rev2":
        win_path, hist_path = RES / "rev2_calib_windows.csv", RES / "rev2_calib_hist.csv"
        out_json, out_txt = RES / "rev2_analysis.json", RES / "rev2_analysis.txt"
        kinds = ("eden", "idla", "idlar", "mf", "rotor")
        pilot = False
    else:  # confirm
        win_path, hist_path = RES / "confirm_windows.csv", RES / "confirm_hist.csv"
        out_json, out_txt = RES / "confirm_analysis.json", RES / "confirm_analysis.txt"
        kinds = ("ant",)
        pilot = False

    calib_w = load_windows(win_path)
    calib_h = load_hist(hist_path)
    report = {"mode": mode, "calibration": {}, "pilot": None, "gates": {}, "confirmation": None}
    lines = []

    def say(s=""):
        print(s)
        lines.append(s)

    say(f"=== {mode} ===")
    for kind in kinds:
        a = analyse_kind(kind, calib_w, calib_h)
        # Attach compactness for cup kinds using retained window records
        if kind.startswith("cup:") or kind in ("eden", "idla", "idlar"):
            retained = []
            for w in calib_w:
                if kind_of(w["spec"]) != kind:
                    continue
                if not (K_LO <= w["k"] <= K_HI):
                    continue
                if w["escaped"] or w["n_completed"] < 200:
                    continue
                if w["censored_step_share"] > 0.20:
                    continue
                if not math.isfinite(w["L"]) or w["L"] < 4:
                    continue
                key = (w["spec"], w["k"])
                bins = calib_h.get(key, {"bins": {}, "n_censored": 0})["bins"]
                taus = expand_durations(bins)
                if len(taus) < 200:
                    continue
                retained.append((w, taus, bins))
            a["compactness"] = compactness(retained)
        report["calibration"][kind] = a
        comp = a.get("compactness")
        comp_s = ""
        if comp:
            comp_s = (
                f" compact_pass={comp['pass']} A/P2_med={comp['median_A_over_P2']} "
                f"A_range={comp['A_range_ratio']} ({comp['reason']})"
            )
        say(
            f"{kind}: nwin={a['n_retained_windows']} L_range={a['L_range_ratio']} "
            f"Score(L)={a['Score_L']} Score(L^2)={a['Score_L2']} "
            f"verdict={a['verdict']} mean_tau/L={a['mean_tau_over_L']} "
            f"fragile={a['censoring_fragile']}{comp_s}"
        )

    if mode == "stage1":
        rw_v = report["calibration"]["rw"]["verdict"]
        mf_v = report["calibration"]["mf"]["verdict"]
        mf_ratio = report["calibration"]["mf"]["mean_tau_over_L"]
        c1_ok = rw_v == "D"
        c2_ok = mf_v == "S" and mf_ratio is not None and 0.5 <= mf_ratio <= 2.0
        report["gates"] = {
            "C1_rw_prefers_D": c1_ok,
            "C2_mf_prefers_S_and_mean_in_band": c2_ok,
            "instrument_adequate": c1_ok and c2_ok,
            "rw_verdict": rw_v,
            "mf_verdict": mf_v,
            "mf_mean_tau_over_L": mf_ratio,
        }
        say()
        say(f"C1 (rw→D): {'PASS' if c1_ok else 'FAIL'} (verdict={rw_v})")
        say(f"C2 (mf→S & E[tau]/L in [0.5,2]): {'PASS' if c2_ok else 'FAIL'} (verdict={mf_v}, ratio={mf_ratio})")
        say(f"Instrument adequate: {c1_ok and c2_ok}")
    elif mode == "rev1":
        cup = report["calibration"]["cup:0.10"]
        mf = report["calibration"]["mf"]
        mf_ratio = mf["mean_tau_over_L"]
        compact_ok = bool(cup.get("compactness", {}).get("pass"))
        c1p_pass = cup["verdict"] == "D" and compact_ok and not cup["censoring_fragile"]
        c1p_inconclusive = cup["verdict"] in ("S", "inconclusive") and compact_ok
        c1p_inadequate = (
            cup["verdict"] in ("uninformative", "censoring-fragile")
            or not compact_ok
            or cup["censoring_fragile"]
        )
        c2_ok = mf["verdict"] == "S" and mf_ratio is not None and 0.5 <= mf_ratio <= 2.0
        if c1p_pass:
            c1p_label = "PASS"
        elif c1p_inconclusive and not c1p_inadequate:
            c1p_label = "INCONCLUSIVE"
        else:
            c1p_label = "INADEQUATE"
        gates_ok = c1p_pass and c2_ok
        report["gates"] = {
            "C1prime_cup010": c1p_label,
            "C1prime_pass": c1p_pass,
            "C2_mf_prefers_S_and_mean_in_band": c2_ok,
            "run_confirmation": gates_ok,
            "cup_verdict": cup["verdict"],
            "cup_compactness": cup.get("compactness"),
            "mf_verdict": mf["verdict"],
            "mf_mean_tau_over_L": mf_ratio,
            "rotor_verdict": report["calibration"]["rotor"]["verdict"],
        }
        say()
        say(
            f"C1' (cup:0.10→D + compactness): {c1p_label} "
            f"(verdict={cup['verdict']}, compact={compact_ok})"
        )
        say(f"C2 (mf→S & E[tau]/L in [0.5,2]): {'PASS' if c2_ok else 'FAIL'} (verdict={mf['verdict']}, ratio={mf_ratio})")
        say(f"Run confirmation cohort: {gates_ok}")
    elif mode == "rev2":
        def label(a):
            compact_ok = bool(a.get("compactness", {}).get("pass"))
            if a["verdict"] == "D" and compact_ok and not a["censoring_fragile"]:
                return "PASS"
            if (not compact_ok) or a["verdict"] in ("uninformative", "censoring-fragile") or a["censoring_fragile"]:
                return "INADEQUATE"
            return "INCONCLUSIVE"
        cal = report["calibration"]
        c1e, c1i = label(cal["eden"]), label(cal["idla"])
        mf = cal["mf"]
        mf_ratio = mf["mean_tau_over_L"]
        c2_ok = mf["verdict"] == "S" and mf_ratio is not None and 0.5 <= mf_ratio <= 2.0
        c0_ok = True  # run_rev2.sh aborts before measurement if C0 fails
        gates_ok = c0_ok and c2_ok and (c1e == "PASS" or c1i == "PASS")
        report["gates"] = {
            "C0": c0_ok,
            "C1E_eden": c1e,
            "C1I_idla": c1i,
            "idlar_diagnostic_verdict": cal["idlar"]["verdict"],
            "C2_mf_prefers_S_and_mean_in_band": c2_ok,
            "mf_mean_tau_over_L": mf_ratio,
            "rotor_verdict": cal["rotor"]["verdict"],
            "run_confirmation": gates_ok,
        }
        say()
        say(f"C1E (eden→D + compactness): {c1e} (verdict={cal['eden']['verdict']})")
        say(f"C1I (idla→D + compactness): {c1i} (verdict={cal['idla']['verdict']})")
        say(f"idlar diagnostic (restart excursions dropped): verdict={cal['idlar']['verdict']}")
        say(f"C2 (mf→S & E[tau]/L in [0.5,2]): {'PASS' if c2_ok else 'FAIL'} (verdict={mf['verdict']}, ratio={mf_ratio})")
        say(f"Run confirmation cohort: {gates_ok}")
    else:
        # confirmation: per-rule + family
        say("=== Confirmation (reserved cohort) ===")
        rules = sorted({w["spec"].split("@")[0] for w in calib_w})
        per = {}
        eligible = []
        for rule in rules:
            sub_w = [w for w in calib_w if w["spec"].split("@")[0] == rule]
            a = analyse_kind("ant", sub_w, calib_h)
            per[rule] = a
            say(
                f"  {rule}: nwin={a['n_retained_windows']} L_range={a['L_range_ratio']} "
                f"Score(L)={a['Score_L']} Score(L^2)={a['Score_L2']} verdict={a['verdict']} "
                f"mean_tau/L={a['mean_tau_over_L']}"
            )
            if a["verdict"] in ("D", "S"):
                eligible.append((rule, a["verdict"]))
        n_d = sum(1 for _, v in eligible if v == "D")
        n_s = sum(1 for _, v in eligible if v == "S")
        n_el = len(eligible)
        if n_el >= 4 and n_d / n_el >= 0.75:
            family = "D"
            decision = "retain-diffusive"
        elif n_el >= 4 and n_s / n_el >= 0.75:
            family = "S"
            decision = "retain-sweep"
        else:
            family = "neither"
            decision = "revise"
        pooled = analyse_kind("ant", calib_w, calib_h)
        report["confirmation"] = {
            "per_rule": per,
            "pooled": pooled,
            "n_eligible": n_el,
            "n_D": n_d,
            "n_S": n_s,
            "family": family,
            "decision": decision,
            "escapes": sum(1 for w in calib_w if w["escaped"]),
            "n_window_rows": len(calib_w),
        }
        say()
        say(f"eligible rules with D/S: {n_el} (D={n_d}, S={n_s})")
        say(f"family={family} decision={decision}")
        say(
            f"pooled: nwin={pooled['n_retained_windows']} verdict={pooled['verdict']} "
            f"Score(L)={pooled['Score_L']} Score(L^2)={pooled['Score_L2']}"
        )

    if mode == "stage1" and pilot:
        pilot_path = RES / "pilot_windows.csv"
        if pilot_path.exists():
            say()
            say("=== Pilot (EXPLORATORY / EXCLUDED) ===")
            pilot_w = load_windows(pilot_path)
            pilot_h = load_hist(RES / "pilot_hist.csv")
            a_all = analyse_kind("ant", pilot_w, pilot_h)
            report["pilot"] = {"pooled": a_all, "per_rule": {}}
            say(
                f"ant pooled: nwin={a_all['n_retained_windows']} L_range={a_all['L_range_ratio']} "
                f"Score(L)={a_all['Score_L']} Score(L^2)={a_all['Score_L2']} "
                f"verdict={a_all['verdict']} mean_tau/L={a_all['mean_tau_over_L']} "
                f"(EXPLORATORY — not evidence)"
            )
            rules = sorted({w["spec"].split("@")[0] for w in pilot_w})
            for rule in rules:
                sub_w = [w for w in pilot_w if w["spec"].split("@")[0] == rule]
                a = analyse_kind("ant", sub_w, pilot_h)
                report["pilot"]["per_rule"][rule] = a
                say(
                    f"  {rule}: nwin={a['n_retained_windows']} L_range={a['L_range_ratio']} "
                    f"Score(L)={a['Score_L']} Score(L^2)={a['Score_L2']} verdict={a['verdict']} "
                    f"mean_tau/L={a['mean_tau_over_L']}"
                )

    def clean(o):
        if isinstance(o, float) and not math.isfinite(o):
            return None
        if isinstance(o, dict):
            return {k: clean(v) for k, v in o.items()}
        if isinstance(o, list):
            return [clean(v) for v in o]
        return o

    out_json.write_text(json.dumps(clean(report), indent=2))
    out_txt.write_text("\n".join(lines) + "\n")
    say()
    say(f"wrote {out_json} and {out_txt.name}")




if __name__ == "__main__":
    main()
