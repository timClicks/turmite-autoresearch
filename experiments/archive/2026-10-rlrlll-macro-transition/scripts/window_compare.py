# /// script
# requires-python = ">=3.12"
# dependencies = ["numpy"]
# ///
"""Task A: compare cell-level windows at the sweeper's own front with the closed family C(m, q).

usage: uv run experiments/archive/2026-10-rlrlll-macro-transition/scripts/window_compare.py WINDIR [controls|scan]
WINDIR holds ev_<x>.bin and ref.bin written by examples/rlrlll_macro_transition_window.rs. The canonical family is
results/canonical_k0.txt (phases q = 0, 1, 2 at x = -2197, -2200, -2203 with m = 434, 436, 438).

Membership test (the checker's hypothesis): every cell in columns west of x+48 inside the apron is colour 0 except the
rectangle top_q . bulk^m . bottom_q on columns [x, x+48), and the ant stands on column x, `dy` rows below the rectangle's
top row, with the canonical heading. Primary score: colour equality, unvisited = 0. Secondary: visited flag too.
"""
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[4]
E = ROOT / "experiments/archive/2026-10-rlrlll-macro-transition"
CLOCK = (934, 1058, 898)


def load_canonical():
    ph = []
    lines = [l for l in (E / "results/canonical_k0.txt").read_text().splitlines() if not l.startswith("#")]
    i = 0
    while i < len(lines):
        f = lines[i].split()
        assert f[0] == "phase"
        m, dx, dy, h = int(f[5]), int(f[7]), int(f[8]), int(f[9])
        nt = int(lines[i + 1].split()[1])
        top = lines[i + 2:i + 2 + nt]
        assert lines[i + 2 + nt] == "bulk"
        bulk = lines[i + 3 + nt]
        nb = int(lines[i + 4 + nt].split()[1])
        bot = lines[i + 5 + nt:i + 5 + nt + nb]
        i += 5 + nt + nb
        ph.append(dict(m=m, dx=dx, dy=dy, h=h, top=top, bulk=bulk, bot=bot))
    return ph


def rows_of(p, m):
    """Canonical rectangle as bytes, 255 = '.' (unvisited)."""
    rs = p["top"] + [p["bulk"]] * m + p["bot"]
    return np.array([[255 if c == "." else int(c) for c in r] for r in rs], dtype=np.uint8)


def mq(x):
    d = -2197 - x
    assert d % 3 == 0
    j = d // 3
    return 434 + 2 * j, j % 3


def load_ev(path):
    raw = path.read_bytes()
    nl = raw.index(b"\n")
    h = list(map(int, raw[:nl].split()))
    if len(h) == 5:  # ref.bin: t x0 y0 w hgt
        t, x0, y0, w, hgt = h
        return dict(t=t, x0=x0, y0=y0, a=np.frombuffer(raw[nl + 1:], np.uint8).reshape(hgt, w))
    x, t, ax, ay, hd, x0, y0, w, hgt = h
    return dict(x=x, t=t, ax=ax, ay=ay, h=hd, x0=x0, y0=y0, a=np.frombuffer(raw[nl + 1:], np.uint8).reshape(hgt, w))


def was_old(ref, X, Y):
    if ref is None:
        return None
    rx, ry = X - ref["x0"], Y - ref["y0"]
    if 0 <= rx < ref["a"].shape[1] and 0 <= ry < ref["a"].shape[0]:
        return bool(ref["a"][ry, rx] != 255)
    return None


def compare(ev, ph, m, ref=None, width=48):
    """Compare event `ev` with C(m, ph). `width` < 48 scores only the first `width` window columns."""
    rect = rows_of(ph, m)[:, :width]
    n = rect.shape[0]
    a = ev["a"]
    top_idx = (ev["ay"] - ph["dy"]) - ev["y0"]  # dump row of the rectangle's first row
    c0 = ev["ax"] - ph["dx"] - ev["x0"]  # dump column of the front
    out = dict(ant_ok=(ev["h"] == ph["h"]))
    if not (0 <= top_idx and top_idx + n <= a.shape[0]):
        out.update(ok=False, ok_flag=False, n_in=-1, n_out=-1, first=None, kinds={})
        return out
    exp = np.full(a.shape, 255, np.uint8)
    exp[top_idx:top_idx + n, c0:c0 + width] = rect
    cols = slice(0, c0 + width)  # everything west of the window's east edge
    dif = (np.where(a == 255, 0, a) != np.where(exp == 255, 0, exp))[:, cols]
    dif_flag = ((a == 255) != (exp == 255))[:, cols]
    inside = np.zeros(a.shape, bool)
    inside[top_idx:top_idx + n, c0:c0 + width] = True
    inside = inside[:, cols]
    ys, xs = np.nonzero(dif)  # row-major
    n_in = int(dif[inside].sum())
    first = None
    if len(ys):
        y, xx = int(ys[0]), int(xs[0])
        X, Y = ev["x0"] + xx, ev["y0"] + y
        first = dict(canon_row=y - top_idx, canon_col=xx - c0, abs_x=X, abs_y=Y, expect=int(exp[y, xx]), actual=int(a[y, xx]),
                     old=was_old(ref, X, Y), in_rect=bool(inside[y, xx]))
    kinds = {"old": 0, "col>=-1546": 0, "other": 0, "unknown_old": 0}
    for y, xx in zip(ys, xs):
        X, Y = ev["x0"] + int(xx), ev["y0"] + int(y)
        o = was_old(ref, X, Y)
        if o:
            kinds["old"] += 1
        elif X >= -1546:
            kinds["col>=-1546"] += 1
        elif o is None:
            kinds["unknown_old"] += 1
        else:
            kinds["other"] += 1
    out.update(ok=bool(not dif.any() and out["ant_ok"]), ok_flag=bool(not dif.any() and not dif_flag.any() and out["ant_ok"]),
               n_in=n_in, n_out=int(dif.sum()) - n_in, first=first, kinds=kinds)
    return out


def fmt_first(f):
    if f is None:
        return "-"
    return (f"canon(row {f['canon_row']}, col {f['canon_col']}) abs({f['abs_x']},{f['abs_y']}) exp {f['expect']} got {f['actual']} "
            f"{'in' if f['in_rect'] else 'out'}-rect old={f['old']}")


def controls(evs, ph, ref):
    cyc = [l.split(",") for l in (E / "results/cycles.csv").read_text().splitlines()[1:4]]
    ok_all = True
    for q, x in enumerate((-2197, -2200, -2203)):
        e = evs[x]
        m, qq = mq(x)
        assert (m, qq) == (ph[q]["m"], q), (m, qq)
        t_ok = e["t"] == int(cyc[q][1])
        r = compare(e, ph[q], m, ref)
        print(f"C1 x={x} t={e['t']} (cycles.csv {cyc[q][1]}: {'equal' if t_ok else 'DIFFERENT'}) primary={r['ok']} flag={r['ok_flag']} "
              f"ant_heading_ok={r['ant_ok']} n_in={r['n_in']} n_out={r['n_out']}")
        ok_all &= t_ok and r["ok"] and r["ok_flag"]
        for q2 in range(3):  # C2: wrong q, m +- 2 must fail
            for dm in (-2, 0, 2):
                if (q2, dm) == (q, 0):
                    continue
                r2 = compare(e, ph[q2], m + dm, ref)
                print(f"   C2 against q={q2} m={m + dm}: primary={r2['ok']} n_in={r2['n_in']} n_out={r2['n_out']}")
                ok_all &= not r2["ok"]
        ntop, nbot = len(ph[q]["top"]), len(ph[q]["bot"])
        top_idx = (e["ay"] - ph[q]["dy"]) - e["y0"]
        c0 = e["ax"] - ph[q]["dx"] - e["x0"]
        for name, row, col in (("top", ntop // 2, 30), ("bulk", ntop + m // 2, 23), ("bottom", ntop + m + nbot // 2, 5)):
            a2 = e["a"].copy()  # C3: one-cell perturbation must fail at exactly that cell
            v = a2[top_idx + row, c0 + col]
            a2[top_idx + row, c0 + col] = 0 if v == 255 else (v + 1) % 6
            r3 = compare(dict(e, a=a2), ph[q], m, ref)
            f = r3["first"]
            hit = (not r3["ok"]) and f is not None and (f["canon_row"], f["canon_col"]) == (row, col) and r3["n_in"] == 1 and r3["n_out"] == 0
            print(f"   C3 perturb {name} cell (row {row}, col {col}): primary={r3['ok']} first={fmt_first(f)} -> {'exactly that cell' if hit else 'WRONG'}")
            ok_all &= hit
        a2 = e["a"].copy()  # C3b: stray cell outside the rectangle, west of the front, must fail the blank-outside clause
        a2[top_idx - 3, 5] = 1
        r4 = compare(dict(e, a=a2), ph[q], m, ref)
        print(f"   C3b stray cell 3 rows above the rectangle, apron column 5: primary={r4['ok']} n_in={r4['n_in']} n_out={r4['n_out']}")
        ok_all &= (not r4["ok"]) and r4["n_out"] == 1
    print("CONTROLS", "ALL PASS" if ok_all else "FAILED")


def scan(evs, ph, ref):
    xs = sorted((x for x in evs if x > -2197), reverse=True)
    print(f"{len(xs)} scan events; x from {max(xs)} to {min(xs)}")
    allx = sorted(evs, reverse=True)
    clock = {}
    for x in allx:
        if x - 3 in evs:
            m, q = mq(x)
            clock[x] = (evs[x - 3]["t"] - evs[x]["t"], 12 * m + CLOCK[q])
    print("x      t            m    q  dt        primary flag  21col  n_in n_out  first differing cell | kinds(all diffs)")
    res = {}
    for x in xs:
        e = evs[x]
        m, q = mq(x)
        if m < 2:
            r = dict(ok=False, ok_flag=False, n_in=-1, n_out=-1, first=None, kinds={}, undefined=True)
            r21 = dict(ok=False)
        else:
            r, r21 = compare(e, ph[q], m, ref), compare(e, ph[q], m, ref, width=21)
        res[x] = (r, r21)
        c = clock.get(x)
        cs = "n/a" if c is None else ("ok" if c[0] == c[1] else f"FAIL({c[0]}!={c[1]})")
        print(f"{x:5d} {e['t']:12d} {m:4d} {q}  {cs:10s} {str(r['ok']):5s} {str(r['ok_flag']):5s} {str(r21['ok']):5s} {r['n_in']:5d} {r['n_out']:5d}  "
              f"{'m<2: family undefined' if r.get('undefined') else fmt_first(r['first'])} | {r.get('kinds')}")
    pairs = [x for x in clock if x <= -1552]
    print(f"\nA1 clock law on {len(pairs)} pairs with x <= -1552: all hold = {all(clock[x][0] == clock[x][1] for x in pairs)}")
    print("   clock failures, east to west (first 10):", sorted((x for x in clock if clock[x][0] != clock[x][1]), reverse=True)[:10])
    ge = [x for x in xs if x <= -1594]
    bad = [x for x in ge if not res[x][0]["ok"]]
    print(f"A2 targets x <= -1594: {len(ge)}, failing primary: {bad}")
    mid = [x for x in xs if -1591 <= x <= -1552]
    other = {x: (res[x][0]["kinds"].get("other", 0), res[x][0]["kinds"].get("unknown_old", 0)) for x in mid if res[x][0]["kinds"].get("other", 0) + res[x][0]["kinds"].get("unknown_old", 0)}
    print(f"A3 targets -1591..-1552: {len(mid)}, passing primary: {[x for x in mid if res[x][0]['ok']]}; "
          f"diff cells outside the two named sources (other, unknown_old) per target: {other}")
    fam = [x for x in xs if x <= -1549]
    f21 = [x for x in fam if not res[x][1]["ok"]]
    print("A4 (exploratory) 21-column window: eastmost failing target:", max(f21) if f21 else None,
          "; passing 21-col targets:", len([x for x in fam if res[x][1]["ok"]]), "of", len(fam))
    pas = [x for x in fam if res[x][0]["ok"]]
    print("primary 48-col: eastmost passing target", max(pas) if pas else None, "; passing", len(pas), "of", len(fam))
    print("secondary (visited flag too): passing", len([x for x in fam if res[x][0]["ok_flag"]]), "of", len(fam))


def main():
    win = Path(sys.argv[1])
    mode = sys.argv[2] if len(sys.argv) > 2 else "scan"
    ph = load_canonical()
    ref = load_ev(win / "ref.bin")
    evs = {}
    for p in win.glob("ev_*.bin"):
        e = load_ev(p)
        evs[e["x"]] = e
    (controls if mode == "controls" else scan)(evs, ph, ref)


main()
