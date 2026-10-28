"""Apply the prefix lemma to the census data (R2-R4 of the README).

  analyse.py specs   -> results/r4_rules.txt  (late-highway rules that share an onset with another rule)
  analyse.py report  -> results/analysis.txt  (needs results/survivors_first_reads.csv and results/r4_first_reads.csv)
Run from the repository root: uv run --frozen experiments/archive/2026-10-prefix-causal-horizon/scripts/analyse.py specs|report
"""
import csv, itertools, math, pathlib, statistics as st, sys
import polars as pl

ROOT = pathlib.Path(__file__).resolve().parents[4]
E = ROOT / "experiments/archive/2026-10-prefix-causal-horizon/results"
X = ROOT / "experiments"


def late_onsets():
    rows = []
    for line in (X / "2026-10-late-highway-board-check/results/classify.txt").read_text().splitlines():
        c = [x.strip() for x in line.strip("│ ").split("┆")]
        if len(c) >= 8 and c[0].startswith("(1e"):
            rows.append(dict(rule=c[1], onset=round(float(c[-4]) * 2**31), filler=c[-1] == "true"))
    return rows


def theorem(w, w2):
    """(class, q) for n <= n'. class: 'i' differs exactly at F_q(w'); 'ii' identical; 'iii' agree at least until the wrapped read."""
    if len(w) > len(w2):
        w, w2 = w2, w
    q = next((c for c in range(len(w2)) if w2[c] != w[c % len(w)]), None)
    if q is not None:
        return "i", q, w2
    return ("ii" if len(w2) % len(w) == 0 else "iii"), None, w2


def load_first(path):
    out = {}
    for r in csv.DictReader(open(path)):
        out[r["rule"]] = dict(n=int(r["n"]), escaped=r["escaped"] == "true", W=int(r["wrapped_read"]) if r["wrapped_read"] else None,
                              F=[int(x) if x else None for x in r["first_reads"].split(";")], steps=int(r["steps"]))
    return out


def main_specs():
    rows = late_onsets()
    groups = []
    for a, b in itertools.combinations(rows, 2):
        if abs(a["onset"] - b["onset"]) / max(a["onset"], b["onset"]) < 1e-4:
            groups.append((a["rule"], b["rule"]))
    rules = sorted({r for p in groups for r in p})
    (E / "r4_rules.txt").write_text("\n".join(rules) + "\n")
    print(len(rows), "late-highway rows;", len(groups), "pairs with equal onset (<1e-4);", len(rules), "distinct rules")


def main_report():
    out = []
    P = lambda *a: (print(*a), out.append(" ".join(str(x) for x in a)))
    F = load_first(E / "survivors_first_reads.csv")
    # ---- R2 ----
    P("R2: first-read times F_c over the 702 survivors (steps; every survivor read every colour: wrapped read exists)")
    P(f"  max F_(n-1) = {max(v['F'][-1] for v in F.values())}, max wrapped read = {max(v['W'] for v in F.values())}, escaped = {sum(v['escaped'] for v in F.values())}")
    xs, ys = [], []
    P("  c   rules   median   p90    max")
    for c in range(1, 10):
        v = sorted(f["F"][c] for f in F.values() if len(f["F"]) > c)
        P(f"  {c:<3} {len(v):<7} {int(st.median(v)):<8} {v[int(.9*len(v))]:<6} {v[-1]}")
        if c >= 2:
            xs.append(math.log(c)); ys.append(math.log(st.median(v)))
    mx, my = st.mean(xs), st.mean(ys)
    b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)
    P(f"  slope of log(median F_c) on log c, c = 2..9: {b:.2f}  (registered: 2.5-3.5; FAILED)")
    # ---- R3 ----
    surv = {r["rule"]: r for r in csv.DictReader(open(X / "2026-10-highways-unresolved-rules-1e10-1e11/results/h1e11/chunk_00.csv"))}
    boxes = {}
    import glob
    for f in sorted(glob.glob(str(X / "2026-10-highways-unresolved-rules-1e10-1e11/results/h1e11/chunk_*.csv"))):
        for r in csv.DictReader(open(f)):
            if r["stop"] == "budget":
                boxes.setdefault((r["width"], r["height"]), []).append(r["rule"])
    groups = [v for v in boxes.values() if len(v) > 1]
    cls = {"i": 0, "ii": 0, "iii": 0}
    unsep_groups, maxbound = 0, 0
    for g in groups:
        has = False
        for a, b2 in itertools.combinations(g, 2):
            k, q, w2 = theorem(a, b2)
            cls[k] += 1
            if k == "i":
                maxbound = max(maxbound, F[w2]["F"][q])
            else:
                has = True
        unsep_groups += has
    P(f"\nR3: {len(groups)} groups of survivors with identical (width, height) at 1e11, {sum(len(g) for g in groups)} rules, {sum(cls.values())} pairs")
    P(f"  pairs by theorem class: (i) diverge exactly at F_q: {cls['i']}, (ii) identical forever: {cls['ii']}, (iii) agree at least until the wrapped read: {cls['iii']}")
    P(f"  largest divergence time over the (i) pairs: {maxbound} steps; groups holding a pair the lemma does not separate: {unsep_groups} (registered: at most 3)")
    # ---- R4 ----
    p4 = E / "r4_first_reads.csv"
    if p4.exists():
        D = load_first(p4)
        rows = {r["rule"]: r for r in late_onsets()}
        P("\nR4: late-highway pairs with equal onset (within 1e-4): theorem class and the lemma's divergence time against the onset")
        P(f"  {'rule A':<12} {'rule B':<12} {'onset':>14} class {'q':>3} {'F_q or W (longer rule)':>24}  verdict")
        bad = n_pairs = 0
        for a, b2 in itertools.combinations(rows.values(), 2):
            if abs(a["onset"] - b2["onset"]) / max(a["onset"], b2["onset"]) >= 1e-4:
                continue
            k, q, w2 = theorem(a["rule"], b2["rule"])
            d = D.get(w2)
            if d is None:
                continue
            n_pairs += 1
            bound = d["F"][q] if k == "i" else d["W"]
            if k == "ii":
                v = "identical forever"
            elif bound is None:
                v = f"bound beyond the cap ({d['steps']:.2e} steps run) - consistent"
            elif bound > a["onset"]:
                v = "bound after onset - consistent"
            else:
                v = "diverged long before the onset (equal onset is not a shared trajectory)" if k == "i" else "wrapped-read bound is before the onset (inconclusive)"
                bad += 1
            P(f"  {a['rule']:<12} {b2['rule']:<12} {a['onset']:>14,} {k:>5} {q if q is not None else '-':>3} {bound if bound is not None else '>cap':>24}  {v}")
        P(f"  pairs whose lemma bound lies before the onset: {bad} of {n_pairs}")
        p3 = E / "r4_iii_pair_diff.csv"
        if p3.exists():
            P("\n  class (iii) pairs: the lemma gives only a lower bound, so the first position difference was measured (lockstep, 32768 board):")
            for r in csv.DictReader(open(p3)):
                P(f"    {r['rule_a']:<10} {r['rule_b']:<12} {r['result']:<7} after {int(r['steps']):>5} steps")
    (E / "analysis.txt").write_text("\n".join(out) + "\n")


{"specs": main_specs, "report": main_report}[sys.argv[1]]()
