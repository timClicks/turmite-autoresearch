"""Score the leak-handedness cohort test exactly as registered in the README.

usage (repo root): uv run --frozen python experiments/active/2026-11-leak-handedness-cohort/scripts/analyse.py [RESULTS_DIR]
Reads RESULTS_DIR/probe.csv (default: the committed results/), the committed spec_roles.csv and the committed
wall-vs-memory Stage 3b probe rows (gate G1); writes runs.csv, rules.csv and analysis.txt into RESULTS_DIR.
`fit` and `classify` are wall-vs-memory Stage 1's, `stalled` Stage 3's and `filler` Stage 3c's, copied unchanged
from experiments/active/2026-10-wall-vs-memory/scripts/analyse_stage3c.py.
"""
import sys
from pathlib import Path

import numpy as np
import polars as pl

EXP = Path(__file__).resolve().parents[1]
RES = Path(sys.argv[1]) if len(sys.argv) > 1 else EXP / "results"
S3B = EXP.parents[1] / "active" / "2026-10-wall-vs-memory" / "results" / "stage3b_probe.csv"
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


df = pl.read_csv(RES / "probe.csv")
roles = pl.read_csv(EXP / "results" / "spec_roles.csv", schema_overrides={"ef": pl.Utf8})
s3b = pl.read_csv(S3B)
assert set(df["rule"].unique().to_list()) == set(roles["spec"].to_list()), "probe output does not cover the specs"
P(f"# leak-handedness cohort scoring; {roles.height} specs")

# G1: EF = 0 rows byte-identical (field for field, as parsed) to Stage 3b rows
g1_bad = []
gates = roles.filter(pl.col("role") == "gate_s3b")["spec"].sort().to_list()
for sp in gates:
    a = df.filter(pl.col("rule") == sp).sort("k")
    b = s3b.filter(pl.col("rule") == sp).sort("k")
    if b.height == 0 or not a.equals(b.select(a.columns)):
        g1_bad.append(sp)
P(f"G1 replication: {len(gates) - len(g1_bad)}/{len(gates)} EF = 0 rows identical to Stage 3b -> {'PASS' if not g1_bad else 'FAIL'}")
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

P("classes by cohort/arm/EF (EF > 0):")
for (co, arm, ef), g in sorted(runs.filter(pl.col("ef") > 0).group_by(["cohort", "arm", "ef"]), key=lambda x: x[0]):
    cnt = dict(sorted(g["cls"].value_counts().iter_rows()))
    P(f"  {co} {arm} EF {ef:.1f}: {cnt}")

# per-rule statistics, cohort C
C = runs.filter(pl.col("cohort") == "C")
rule_rows = []
for rule in sorted(C["rule"].unique().to_list()):
    x = C.filter(pl.col("rule") == rule)

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
    st = {(arm, ef): m(arm, ef) for arm in "RL" for ef in (0.1, 0.3, 0.5)}
    ok = (dR >= 0.10 and dL >= 0.10 and n1R >= 3 and n1L >= 3
          and all(st[(arm, ef)][1] >= 3 for arm in "RL" for ef in (0.3, 0.5)))
    F = {(arm, ef): (st[(arm, ef)][0] - (a0R if arm == "R" else a0L)) / (dR if arm == "R" else dL)
         for arm in "RL" for ef in (0.1, 0.3, 0.5)}
    lam = np.mean([F[("R", ef)] - F[("L", ef)] for ef in (0.3, 0.5)])
    rule_rows.append(dict(rule=rule, a0_R=a0R, a0_L=a0L, a1=a1, a1_R=a1R, a1_L=a1L, delta_R=dR, delta_L=dL,
                          F_R_01=F[("R", 0.1)], F_L_01=F[("L", 0.1)], F_R_03=F[("R", 0.3)], F_L_03=F[("L", 0.3)],
                          F_R_05=F[("R", 0.5)], F_L_05=F[("L", 0.5)], lam=lam, scoreable=ok))
rules = pl.DataFrame(rule_rows)
rules.write_csv(RES / "rules.csv", float_precision=6)
sc = rules.filter(pl.col("scoreable")).sort("rule")
P(f"cohort C: {rules.height} rules, scoreable {sc.height}")
P("  not scoreable: " + ", ".join(f"{r['rule']} (dR {r['delta_R']:.3f}, dL {r['delta_L']:.3f})"
                                  for r in rules.filter(~pl.col("scoreable")).iter_rows(named=True)))

# G2
d = (sc["a1_L"] - sc["a1_R"]).to_numpy()
g2 = abs(d.mean()) <= 0.02 and np.mean(np.abs(d) <= 0.06) >= 0.90
P(f"G2 shared law at EF = 1: mean d {d.mean():+.4f} (need |.| <= 0.02); |d| <= 0.06 in {np.mean(np.abs(d) <= 0.06):.3f} of rules "
  f"(need >= 0.90) -> {'PASS' if g2 else 'FAIL'}")

# P1
if g1_bad or not g2:
    P("P1 not scored (gate failed)")
elif sc.height < 30:
    P(f"P1 not scored ({sc.height} < 30 scoreable rules)")
else:
    lam = sc["lam"].to_numpy()
    rng = np.random.default_rng(20261112)
    boot = np.median(lam[rng.integers(0, lam.size, size=(10000, lam.size))], axis=1)
    lo, hi = np.quantile(boot, [0.025, 0.975])
    med = float(np.median(lam))
    if lo > 0 and med >= 0.05:
        v = "LAG"
    elif hi < 0:
        v = "REVERSED"
    elif lo >= -0.05 and hi <= 0.05:
        v = "NO LAG"
    else:
        v = "UNRESOLVED"
    P(f"P1 handedness lag: median Lambda {med:+.4f}, rule-bootstrap 95% [{lo:+.4f}, {hi:+.4f}], n = {lam.size}; "
      f"Lambda > 0 in {int((lam > 0).sum())}/{lam.size} -> {v}")
    for ef in ("03", "05"):
        dd = (sc[f"F_R_{ef}"] - sc[f"F_L_{ef}"]).to_numpy()
        P(f"  descriptive EF 0.{ef[1]}: median F_R {np.median(sc[f'F_R_{ef}']):.3f}, F_L {np.median(sc[f'F_L_{ef}']):.3f}, "
          f"median F_R - F_L {np.median(dd):+.3f}")
    P(f"  descriptive: median a0_R {np.median(sc['a0_R']):.3f}, a0_L {np.median(sc['a0_L']):.3f}, a1 {np.median(sc['a1']):.3f}")

# P2
def porous_frac(co: str, arm: str) -> tuple[int, int, int]:
    g = runs.filter((pl.col("cohort") == co) & (pl.col("arm") == arm) & (pl.col("ef") == 0.1))
    return int((g["cls"] == "porous").sum()), int((g["cls"] == "escape").sum()), g.height


pe, ee, ne = porous_frac("E", "L")
pc, ec, nc = porous_frac("C", "L")
per, eer, ner = porous_frac("E", "R")
ok2 = (pe / ne >= 0.50) and (pc / nc <= 0.10)
if g1_bad:
    P("P2 not scored (G1 failed)")
else:
    P(f"P2 ordered-L collapse at EF 0.1, arm L: E porous {pe}/{ne} = {pe / ne:.3f} (need >= 0.50), escapes {ee}; "
      f"C porous {pc}/{nc} = {pc / nc:.3f} (need <= 0.10), escapes {ec} -> {'HOLD' if ok2 else 'FAIL'}")
    P(f"  control arm R at EF 0.1, cohort E: porous {per}/{ner}, escapes {eer}")
    for rule in sorted(runs.filter(pl.col("cohort") == "E")["rule"].unique().to_list()):
        g = runs.filter((pl.col("rule") == rule) & (pl.col("ef") == 0.1))
        s = {arm: g.filter(pl.col("arm") == arm) for arm in "RL"}
        P(f"  E {rule}: L classes {sorted(s['L']['cls'].to_list())} mean a {np.nanmean(s['L']['early_a'].to_numpy()):.3f}; "
          f"R classes {sorted(s['R']['cls'].to_list())} mean a {np.nanmean(s['R']['early_a'].to_numpy()):.3f}")

(RES / "analysis.txt").write_text("\n".join(out) + "\n")
