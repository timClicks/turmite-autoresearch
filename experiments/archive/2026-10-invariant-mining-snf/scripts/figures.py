"""Two SVG figures for the blog post, from committed results (standard library only).

  uv run --no-project experiments/archive/2026-10-invariant-mining-snf/scripts/figures.py

fig1_law_class_vs_outcome.svg: the 108 census rules of length 8 (canonical, primitive), one column each,
  grouped into rows by number of R.  Top panel colours each rule by its F1 law-group fingerprint (read from
  results/fingerprints.csv); bottom panel by census outcome (experiments/archive/2026-10-census-sweeps/results/census.csv).
fig2_universal_orders.svg: log-scale universal group order at modulus m = n for F1, F2, F3 against n.
"""
from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

EXP = Path(__file__).resolve().parents[1]
ROOT = EXP.parents[2]
OUT = ROOT / "blog" / "assets" / "posts" / "invariants-order"
OUT.mkdir(parents=True, exist_ok=True)

INK, MUTED, BG = "#1f2328", "#59636e", "#ffffff"
LAW = ["#1f77b4", "#e69f00", "#7f7f7f"]  # fingerprint classes
OUTCOME = {"blob": "#b8bec6", "log": "#009e73", "builder": "#cc3311"}
FONT = "font-family='system-ui,Segoe UI,Helvetica,Arial,sans-serif'"


def fig1() -> None:
    n = 8
    fp = {r["rule"]: (r["free"], r["factors"]) for r in csv.DictReader(open(EXP / "results" / "fingerprints.csv")) if r["family"] == "F1"}
    census = {r["rule"]: r["cls"] for r in csv.DictReader(open(ROOT / "experiments/archive/2026-10-census-sweeps/results/census.csv")) if r["n"] == str(n)}
    classes = sorted({fp[r] for r in census})
    rows = defaultdict(list)
    for rule in sorted(census):
        rows[rule.count("R")].append(rule)
    order = sorted(rows)
    cw, ch, left, top = 11, 22, 70, 60
    width_cols = max(len(v) for v in rows.values())
    W, H = max(left + width_cols * cw + 30, 760), 2 * (len(order) * ch + 70) + 70
    o = [f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {W} {H}' width='{W}' height='{H}' {FONT} role='img'>",
         f"<title>Law fingerprint is constant along each row; census outcome is not</title>",
         f"<rect width='{W}' height='{H}' fill='{BG}'/>"]
    y0 = top
    for title, color_of, legend in (
        ("Law-group fingerprint (additive local laws, family F1)", lambda r: LAW[classes.index(fp[r])],
         [(LAW[i], lab) for i, lab in enumerate(['net turn 0 mod 4', 'net turn 2 mod 4'])]),
        ("Census outcome", lambda r: OUTCOME[census[r]], [(c, k) for k, c in OUTCOME.items()]),
    ):
        o.append(f"<text x='{left}' y='{y0 - 30}' font-size='14' font-weight='600' fill='{INK}'>{title}</text>")
        lx = left
        for c, lab in legend:
            o.append(f"<rect x='{lx}' y='{y0 - 22}' width='10' height='10' fill='{c}'/><text x='{lx + 14}' y='{y0 - 13}' font-size='11' fill='{MUTED}'>{lab}</text>")
            lx += 24 + 7 * len(lab)
        for i, k in enumerate(order):
            y = y0 + i * ch
            o.append(f"<text x='{left - 8}' y='{y + 15}' font-size='11' text-anchor='end' fill='{MUTED}'>{k} R</text>")
            for j, rule in enumerate(rows[k]):
                o.append(f"<rect x='{left + j * cw}' y='{y}' width='{cw - 1}' height='{ch - 3}' fill='{color_of(rule)}'><title>{rule}</title></rect>")
        y0 += len(order) * ch + 70
    o.append(f"<text x='{left}' y='{H - 26}' font-size='11' fill='{MUTED}'>108 canonical primitive census rules of length 8, one column per rule, one row per number of R.</text>")
    o.append(f"<text x='{left}' y='{H - 10}' font-size='11' fill='{MUTED}'>Sources: results/fingerprints.csv and the census sweep's census.csv.</text>")
    o.append("</svg>")
    (OUT / "fig1_law_class_vs_outcome.svg").write_text("\n".join(o), encoding="utf-8")
    print("fig1: law classes", len(classes), "rows", len(order))


def fig2() -> None:
    u = {(r["family"], int(r["n"]), int(r["m"])): int(r["order"]) for r in csv.DictReader(open(EXP / "results" / "universal.csv"))}
    import math
    W, H, L, T, R, B = 520, 340, 60, 30, 110, 50
    ns = list(range(2, 9))
    ymax = max(u[(f, n, n)] for f in ("F1", "F2", "F3") for n in ns)
    ly = lambda v: T + (H - T - B) * (1 - math.log(v) / math.log(ymax * 1.1))
    lx = lambda n: L + (W - L - R) * (n - 2) / 6
    cols = {"F1": "#1f77b4", "F2": "#e69f00", "F3": "#cc3311"}
    o = [f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {W} {H}' width='{W}' height='{H}' {FONT} role='img'>",
         "<title>Universal law group order at modulus n for families F1, F2, F3</title>",
         f"<rect width='{W}' height='{H}' fill='{BG}'/>",
         f"<text x='{L}' y='18' font-size='14' font-weight='600' fill='{INK}'>Laws true of every rule: group order at modulus n</text>"]
    for v in (4, 16, 64, 256, 1024, 4096, 16384):
        o.append(f"<line x1='{L}' x2='{W - R}' y1='{ly(v)}' y2='{ly(v)}' stroke='#e5e7eb'/><text x='{L - 6}' y='{ly(v) + 4}' font-size='10' text-anchor='end' fill='{MUTED}'>{v}</text>")
    for n in ns:
        o.append(f"<text x='{lx(n)}' y='{H - B + 16}' font-size='11' text-anchor='middle' fill='{MUTED}'>{n}</text>")
    o.append(f"<text x='{(L + W - R) / 2}' y='{H - 12}' font-size='11' text-anchor='middle' fill='{MUTED}'>number of colours n (solid: even n, dashed: odd n, where orders are n, n², n⁴)</text>")
    for f, c in cols.items():
        for sub, dash in ((ns[0::2], ""), (ns[1::2], " stroke-dasharray='5 4'")):
            pts = " ".join(f"{lx(n)},{ly(u[(f, n, n)])}" for n in sub)
            o.append(f"<polyline points='{pts}' fill='none' stroke='{c}' stroke-width='2'{dash}/>")
        for n in ns:
            o.append(f"<circle cx='{lx(n)}' cy='{ly(u[(f, n, n)])}' r='3.5' fill='{c}'><title>{f}, n={n}: {u[(f, n, n)]}</title></circle>")
        o.append(f"<text x='{W - R + 8}' y='{ly(u[(f, 8, 8)]) + 4}' font-size='12' fill='{c}'>{f}</text>")
    o.append("</svg>")
    (OUT / "fig2_universal_orders.svg").write_text("\n".join(o), encoding="utf-8")


if __name__ == "__main__":
    fig1()
    fig2()
