"""Score the leak minority-turn test exactly as registered in the README.

usage (repo root): uv run --frozen python experiments/proposed/2026-11-leak-minority-turn/scripts/analyse.py [RESULTS_DIR]
Reads RESULTS_DIR/probe.csv (default: the committed results/), the committed spec_roles.csv and the committed
leak-handedness probe.csv (gate G1); writes runs.csv, rules.csv and analysis.txt into RESULTS_DIR.
`fit`, `classify`, `stalled`, `filler` and the per-rule statistics (Delta, F, Lambda, scoreable) are copied unchanged
from experiments/active/2026-11-leak-handedness-cohort/scripts/analyse.py.
"""
import sys
from pathlib import Path

import numpy as np
import polars as pl

EXP = Path(__file__).resolve().parents[1]
RES = Path(sys.argv[1]) if len(sys.argv) > 1 else EXP / "results"
LHC = EXP.parents[1] / "active" / "2026-11-leak-handedness-cohort" / "results" / "probe.csv"
WINDOWS = {"early": (12, 22), "late": (20, 26)}


def fit(g: pl.DataFrame, lo: int, hi: int) -> dict | None:
    w = g.filter((pl.col("k") >= lo) & (pl.col("k") <= hi))
    if w.height < hi - lo + 1:
        return None
    t = w["t"].to_numpy().astype(float)
    A = w["area"].to_numpy().astype(float)
    P = w["perimeter"].to_numpy().astype(float)
    return dict(a=np.polyfit(np.log(t), np.log(A), 1)[0], beta=np.polyfit(np.log(A), np.log(P), 1)[0])


def classify(c: dict) -> str:
    a, b = c.get("early_a"), c.get("early_beta")
    if a is None or np.isnan(a):
        return "no early fit"
    if a <= 0.78 and b <= 0.65:
        if c["late_n"] >= 6 and not c["late_a"] <= 0.74:
            return "intermediate"
        return "compact"
    if a >= 0.85 and b >= 0.80:
        return "porous"
    return "intermediate"


def stalled(g: pl.DataFrame, early_a: float) -> bool:
    areas = g.sort("k")["area"].to_list()
    return (not np.isnan(early_a) and early_a < 0.45) or (len(areas) >= 2 and areas[-1] == areas[-2])


def filler(g: pl.DataFrame, early_a: float, early_beta: float) -> bool:
    """Registered: early a >= 0.90, early beta <= 0.62, A/t over the last three windows within 3% of their mean."""
    last = g.sort("k").tail(3)
    at = (last["area"] / last["t"]).to_numpy()
    return early_a >= 0.90 and early_beta <= 0.62 and len(at) == 3 and bool(np.all(np.abs(at / at.mean() - 1) <= 0.03))


out: list[str] = []


def P(s: str = "") -> None:
    out.append(s)
    print(s)


def ranks(v: np.ndarray) -> np.ndarray:
    o = np.argsort(v, kind="stable")
    r = np.empty(v.size)
    r[o] = np.arange(v.size)
    for u in np.unique(v):
        m = v == u
        r[m] = r[m].mean()
    return r


def spearman(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.corrcoef(ranks(a), ranks(b))[0, 1])


def wilson(k: int, n: int) -> tuple[float, float]:
    if n == 0:
        return (0.0, 1.0)
    z, p = 1.959964, k / n
    c = (p + z * z / (2 * n)) / (1 + z * z / n)
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return (c - h, c + h)


df = pl.read_csv(RES / "probe.csv")
roles = pl.read_csv(EXP / "results" / "spec_roles.csv", schema_overrides={"ef": pl.Utf8})
assert set(df["rule"].unique().to_list()) == set(roles["spec"].to_list()), "probe output does not cover the specs"
P(f"# leak minority-turn scoring; {roles.height} specs")

# G1: anchor rows identical to leak-handedness rows
lhc = pl.read_csv(LHC)
anc = roles.filter(pl.col("cohort") == "A")["spec"].sort().to_list()
g1_bad = []
for sp in anc:
    a = df.filter(pl.col("rule") == sp).sort("k")
    b = lhc.filter(pl.col("rule") == sp).sort("k")
    if b.height == 0 or not a.equals(b.select(a.columns)):
        g1_bad.append(sp)
P(f"G1 replication: {len(anc) - len(g1_bad)}/{len(anc)} anchor rows identical to leak-handedness -> {'PASS' if not g1_bad else 'FAIL'}")
if g1_bad:
    P("  mismatches: " + ", ".join(g1_bad))

rows = []
for r in roles.iter_rows(named=True):
    g = df.filter(pl.col("rule") == r["spec"]).sort("k")
    e = fit(g, *WINDOWS["early"])
    l = fit(g, *WINDOWS["late"])
    late_n = g.filter((pl.col("k") >= 20) & (pl.col("k") <= 26)).height
    escaped = bool(g["escaped"].any()) if "escaped" in g.columns else False
    ea = e["a"] if e else np.nan
    eb = e["beta"] if e else np.nan
    c = dict(early_a=ea, early_beta=eb, late_a=l["a"] if l else np.nan, late_n=late_n)
    if escaped:
        cls = "escape"
    elif stalled(g, ea):
        cls = "stalled"
    elif e and filler(g, ea, eb):
        cls = "filler"
    else:
        cls = classify(c)
    rows.append(dict(spec=r["spec"], rule=r["spec"].split(":")[1], cohort=r["cohort"], arm=r["arm"],
                     ef=float(r["ef"]), role=r["role"], early_a=ea, early_beta=eb, late_a=c["late_a"], cls=cls))
runs = pl.DataFrame(rows).sort(["cohort", "rule", "arm", "ef", "spec"])
runs.write_csv(RES / "runs.csv", float_precision=6)

# eligibility (frozen): compact under ft:R and ft:L at EF = 0
H = runs.filter(pl.col("cohort") == "H")
elig, inel = [], []
for rule in sorted(H["rule"].unique().to_list()):
    b = H.filter((pl.col("rule") == rule) & (pl.col("ef") == 0.0))
    cr = b.filter(pl.col("arm") == "R")["cls"][0]
    cl = b.filter(pl.col("arm") == "L")["cls"][0]
    (elig if cr == "compact" and cl == "compact" else inel).append((rule, cr, cl))
P(f"cohort H: {H['rule'].n_unique()} rules, eligible {len(elig)}")
P("  ineligible: " + ", ".join(f"{r} (R {cr}, L {cl})" for r, cr, cl in inel))
P("classes, eligible H, EF > 0:")
E_ = runs.filter(pl.col("rule").is_in([r for r, _, _ in elig]) & (pl.col("cohort") == "H"))
for (arm, ef), g in sorted(E_.filter(pl.col("ef") > 0).group_by(["arm", "ef"]), key=lambda x: x[0]):
    P(f"  {arm} EF {ef:.1f}: {dict(sorted(g['cls'].value_counts().iter_rows()))}")

rule_rows = []
for rule in sorted(r for r, _, _ in elig):
    x = E_.filter(pl.col("rule") == rule)

    def m(arm: str, ef: float) -> tuple[float, int]:
        v = x.filter((pl.col("arm") == arm) & (pl.col("ef") == ef))["early_a"].to_numpy()
        v = v[~np.isnan(v)]
        return (float(v.mean()) if v.size else np.nan, int(v.size))

    a0R, _ = m("R", 0.0)
    a0L, _ = m("L", 0.0)
    v1 = x.filter(pl.col("ef") == 1.0)["early_a"].to_numpy()
    v1 = v1[~np.isnan(v1)]
    a1 = float(v1.mean()) if v1.size else np.nan
    a1R, n1R = m("R", 1.0)
    a1L, n1L = m("L", 1.0)
    dR, dL = a1 - a0R, a1 - a0L
    st = {(arm, ef): m(arm, ef) for arm in "RL" for ef in (0.3, 0.5)}
    ok = (dR >= 0.10 and dL >= 0.10 and n1R >= 3 and n1L >= 3
          and all(st[(arm, ef)][1] >= 3 for arm in "RL" for ef in (0.3, 0.5)))
    F = {(arm, ef): (st[(arm, ef)][0] - (a0R if arm == "R" else a0L)) / (dR if arm == "R" else dL)
         for arm in "RL" for ef in (0.3, 0.5)}
    lam = np.mean([F[("R", ef)] - F[("L", ef)] for ef in (0.3, 0.5)])
    rule_rows.append(dict(rule=rule, fr=rule.count("R") / len(rule), a0_R=a0R, a0_L=a0L, a1=a1, a1_R=a1R, a1_L=a1L,
                          delta_R=dR, delta_L=dL, F_R_03=F[("R", 0.3)], F_L_03=F[("L", 0.3)],
                          F_R_05=F[("R", 0.5)], F_L_05=F[("L", 0.5)], lam=lam, scoreable=ok))
rules = pl.DataFrame(rule_rows)
rules.write_csv(RES / "rules.csv", float_precision=6)
sc = rules.filter(pl.col("scoreable")).sort("rule")
P(f"eligible H: {rules.height} rules, scoreable {sc.height}")
P("  not scoreable: " + ", ".join(f"{r['rule']} (dR {r['delta_R']:.3f}, dL {r['delta_L']:.3f})"
                                  for r in rules.filter(~pl.col("scoreable")).iter_rows(named=True)))

d = (sc["a1_L"] - sc["a1_R"]).to_numpy()
g2 = d.size > 0 and abs(d.mean()) <= 0.02 and np.mean(np.abs(d) <= 0.06) >= 0.90
if d.size:
    P(f"G2 shared law at EF = 1: mean d {d.mean():+.4f} (need |.| <= 0.02); |d| <= 0.06 in {np.mean(np.abs(d) <= 0.06):.3f} "
      f"of rules (need >= 0.90) -> {'PASS' if g2 else 'FAIL'}")

if g1_bad or not g2:
    P("P1-P3 not scored (gate failed)")
elif sc.height < 30:
    P(f"P1-P3 not scored ({sc.height} < 30 scoreable rules)")
else:
    lam = sc["lam"].to_numpy()
    fr = sc["fr"].to_numpy()
    rho = spearman(lam, fr)
    rng = np.random.default_rng(20261113)
    idx = rng.integers(0, lam.size, size=(10000, lam.size))
    boot = np.array([spearman(lam[i], fr[i]) for i in idx])
    nb = int(np.isnan(boot).sum())
    lo, hi = np.quantile(boot[~np.isnan(boot)], [0.025, 0.975])
    v1 = "REPLICATES" if lo > 0 else ("FAILS" if hi < 0.20 else "UNRESOLVED")
    P(f"P1 Spearman(Lambda, R fraction) {rho:+.4f}, rule-bootstrap 95% [{lo:+.4f}, {hi:+.4f}], n = {lam.size} "
      f"({nb} degenerate resamples dropped) -> {v1}")
    P(f"  descriptive: median Lambda {np.median(lam):+.3f}, sd {lam.std(ddof=1):.3f}; Lambda > 0 in {int((lam > 0).sum())}/{lam.size}")
    for a, b in [(0, 0.45), (0.45, 0.55), (0.55, 1.01)]:
        mm = (fr >= a) & (fr < b)
        if mm.any():
            P(f"  fr in [{a:.2f}, {min(b, 1):.2f}): n {mm.sum()}, median Lambda {np.median(lam[mm]):+.3f}, Lambda > 0 in {int((lam[mm] > 0).sum())}")
    m2 = (fr != 0.5) & (np.abs(lam) >= 0.10)
    k2 = int(np.sum(np.sign(lam[m2]) == np.sign(fr[m2] - 0.5)))
    wl, wh = wilson(k2, int(m2.sum()))
    v2 = "HOLDS" if wl > 0.5 else ("FAILS" if wh < 0.60 else "UNRESOLVED")
    P(f"P2 sign agreement {k2}/{int(m2.sum())} = {k2 / max(int(m2.sum()), 1):.3f}, Wilson 95% [{wl:.3f}, {wh:.3f}] -> {v2}")
    names = sc["rule"].to_list()
    pr = np.array([s.startswith("RRRR") for s in names])
    pl_ = np.array([s.startswith("RLLL") for s in names])
    fR = float((lam[pr] > 0).mean()) if pr.any() else np.nan
    fL = float((lam[pl_] < 0).mean()) if pl_.any() else np.nan
    desc = f"RRRR n {pr.sum()}, Lambda > 0 in {int((lam[pr] > 0).sum())}; RLLL n {pl_.sum()}, Lambda < 0 in {int((lam[pl_] < 0).sum())}"
    if pr.sum() >= 5 and pl_.sum() >= 5:
        v3 = "HOLDS" if fR >= 0.75 and fL >= 0.75 else "FAILS"
        P(f"P3 prefix: {desc} -> {v3}")
    else:
        P(f"P3 prefix not scored (a group has < 5 scoreable rules): {desc}")

(RES / "analysis.txt").write_text("\n".join(out) + "\n")
