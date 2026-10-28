# /// script
# requires-python = ">=3.12"
# dependencies = ["z3-solver==4.13.4.0"]
# ///
"""Independent checker for the exposure classifier of examples/kappa_exposure_classes.rs.

Written from the documentation-level spec registered in this experiment's README (not from the Rust):
the class of a visited cell is its number of unvisited 4-neighbours; a probe boundary cell is a visited
cell with at least one unvisited 4-neighbour. Reads only the harness dumps in results/ and the committed
classes.csv of 2026-10-kappa-exposure-classes; imports nothing from the repository.

Each property is checked by asking z3 for a counterexample (unsat = proved) or, for witnesses and
negative controls, for a model (sat expected). Replay checks (P4b, P7) are plain Python.

Run (repo root): uv run --script experiments/archive/2026-10-exposure-classifier-check/scripts/check_classifier.py
"""
import csv
import hashlib
import math
import sys
from pathlib import Path

import z3
from z3 import And, BitVec, BitVecVal, Bool, Concat, Extract, If, Implies, Int, IntVal, Not, Or, Solver, Sum, sat, unsat

ROOT = Path(__file__).resolve().parents[4]
EXP = ROOT / "experiments/archive/2026-10-exposure-classifier-check"
OLD = ROOT / "experiments/archive/2026-10-kappa-exposure-classes/results/classes.csv"
UNV = 255
NBR = [(0, -1), (1, 0), (0, 1), (-1, 0)]  # N E S W, src/lib.rs DIRS convention (y grows south)
CELLS = [(w % 3 - 1, w // 3 - 1) for w in range(9)]  # window cell w at (x, y), centre w = 4
results = []


def check(name, premises, goal, expect):
    """expect unsat: goal is proved under premises. expect sat: a model of premises & not goal must exist."""
    s = Solver()
    s.set("timeout", 120_000)
    s.add(*premises, Not(goal))
    r = s.check()
    ok = str(r) == str(expect)
    verdict = {"unsat": "unsat (proved)", "sat": "sat (counterexample/witness)"}.get(str(r), "unknown")
    print(f"{'ok  ' if ok else 'FAIL'} {name:<72} {verdict}", flush=True)
    results.append((name, ok))
    return s.model() if str(r) == "sat" else None


def note(name, ok, detail=""):
    print(f"{'ok  ' if ok else 'FAIL'} {name:<72} {detail}", flush=True)
    results.append((name, ok))


# ---------- spec over a 3x3 window (outside cells are unvisited) ----------
mask = BitVec("mask", 9)


def bit(m, w):
    return Extract(w, w, m) == BitVecVal(1, 1)


def vis(m, x, y):
    return bit(m, CELLS.index((x, y))) if (x, y) in CELLS else z3.BoolVal(False)


def unvisited_nbrs(m, x, y):
    return [Not(vis(m, x + dx, y + dy)) for dx, dy in NBR]


def spec_class(m, x, y, nbrs=NBR):
    cnt = Sum([If(Not(vis(m, x + dx, y + dy)), 1, 0) for dx, dy in nbrs])
    return If(vis(m, x, y), cnt, IntVal(UNV))


def spec_boundary(m, x, y):  # probe doc: visited and at least one unvisited 4-neighbour (a disjunction, not a count)
    return And(vis(m, x, y), Or(unvisited_nbrs(m, x, y)))


def class_indicator(m, x, y, u):
    """Second, combinatorial encoding: visited and some u-subset of the neighbours is exactly the unvisited set."""
    from itertools import combinations
    un = unvisited_nbrs(m, x, y)
    alts = [And([un[i] if i in S else Not(un[i]) for i in range(4)]) for S in combinations(range(4), u)]
    return And(vis(m, x, y), Or(alts))


def table_expr(rows, col):
    e = IntVal(int(rows[-1][col]))
    for r in reversed(rows[:-1]):
        e = If(mask == int(r["mask"]), int(r[col]), e)
    return e


def d4_maps():
    return [lambda x, y: (x, y), lambda x, y: (-y, x), lambda x, y: (-x, -y), lambda x, y: (y, -x),
            lambda x, y: (-x, y), lambda x, y: (x, -y), lambda x, y: (y, x), lambda x, y: (-y, -x)]


def permute(m, g):
    """Pattern g.m: cell g(c) is visited iff c is visited in m."""
    inv = {g(*c): c for c in CELLS}
    bits = [Extract(CELLS.index(inv[CELLS[w]]), CELLS.index(inv[CELLS[w]]), m) for w in range(9)]
    return Concat(*reversed(bits))


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    print(f"checker {Path(__file__).name} sha256 {sha(Path(__file__))}")
    print(f"z3 {z3.get_version_string()}  python {sys.version.split()[0]}")
    for p in ["results/table.csv", "results/walks.csv", "results/paths.csv", "results/dump.log"]:
        print(f"input {p} sha256 {sha(EXP / p)}")
    print(f"input {OLD.relative_to(ROOT)} sha256 {sha(OLD)}\n")

    rows = list(csv.DictReader((EXP / "results/table.csv").open()))
    assert len(rows) == 512 and [int(r["mask"]) for r in rows] == list(range(512))

    # ---------- P1 totality / partition (spec, symbolic over all 512 patterns, every window cell) ----------
    for w, (x, y) in enumerate(CELLS):
        c = spec_class(mask, x, y)
        ind = [class_indicator(mask, x, y, u) for u in range(5)]
        excl = And([Not(And(ind[a], ind[b])) for a in range(5) for b in range(a + 1, 5)])
        check(f"P1  cell {w}: boundary <=> exactly one of C1..C4 (two encodings)", [],
              And(excl, spec_boundary(mask, x, y) == Or(ind[1:]),
                  And(vis(mask, x, y), Not(spec_boundary(mask, x, y))) == ind[0],
                  Not(vis(mask, x, y)) == Not(Or(ind)),
                  And([ind[u] == And(vis(mask, x, y), c == u) for u in range(5)]),
                  Not(vis(mask, x, y)) == (c == UNV)), unsat)

    # ---------- P2 agreement: dumped Rust table == spec, all patterns, all orders ----------
    for w, (x, y) in enumerate(CELLS):
        check(f"P2  cell {w}: Rust stored class == spec (forall 9-bit patterns)", [],
              table_expr(rows, f"u{w}") == spec_class(mask, x, y), unsat)
    for u in range(5):
        spec_pc = Sum([If(spec_class(mask, x, y) == u, 1, 0) for x, y in CELLS])
        check(f"P2  incremental pc[{u}] == spec count of class-{u} cells", [], table_expr(rows, f"pc{u}") == spec_pc, unsat)
    orders_ok = all(int(r["n_orders"]) == math.factorial(int(r["n_visited"])) and int(r["n_visited"]) == bin(int(r["mask"])).count("1") for r in rows)
    note("P2  every visit order enumerated (n_orders == n_visited!), 986410 total",
         orders_ok and sum(int(r["n_orders"]) for r in rows) == 986410, f"{sum(int(r['n_orders']) for r in rows)} orders")
    note("P2  all orders give one outcome; pc == scan() for every order",
         all(r["n_distinct"] == "1" and r["scan_ok"] == "true" for r in rows))

    # ---------- P3 D4 equivariance (spec and table) ----------
    for gi, g in enumerate(d4_maps()):
        gm = permute(mask, g)
        check(f"P3  g{gi}: spec class(g.m, g.c) == class(m, c), all 9 cells", [],
              And([spec_class(gm, *g(x, y)) == spec_class(mask, x, y) for x, y in CELLS]), unsat)
        tab_g = And([z3.substitute(table_expr(rows, f"u{CELLS.index(g(x, y))}"), (mask, gm)) == table_expr(rows, f"u{w}")
                     for w, (x, y) in enumerate(CELLS)])
        check(f"P3  g{gi}: Rust table equivariant", [], tab_g, unsat)

    # ---------- P4a symbolic count identities ----------
    P = Sum([If(spec_boundary(mask, x, y), 1, 0) for x, y in CELLS])
    sum_p = Sum([If(spec_class(mask, x, y) == u, 1, 0) for x, y in CELLS for u in range(1, 5)])
    check("P4a sum_{u=1..4} p_u == P (window)", [], sum_p == P, unsat)
    for w, (x, y) in enumerate(CELLS):
        fresh = Sum([If(n, 1, 0) for n in unvisited_nbrs(mask, x, y)])
        lhs = Sum([If(class_indicator(mask, x, y, u), u, 0) for u in range(1, 5)])
        check(f"P4a cell {w}: boundary => sum_u u[C_u] == #unvisited nbrs (fresh_nbrs)", [],
              Implies(spec_boundary(mask, x, y), lhs == fresh), unsat)

    # ---------- P4b independent replay of the scripted walks ----------
    walks = list(csv.DictReader((EXP / "results/walks.csv").open()))
    paths = {r["walk"]: (int(r["max_log2"]), r["path"]) for r in csv.DictReader((EXP / "results/paths.csv").open())}
    replayed = {w: replay(*paths[w]) for w in paths}
    mism = compare(walks, replayed)
    note(f"P4b replay == instrument == probe on {len(paths)} walks, {len(walks)} windows", not mism, f"{len(mism)} mismatches")

    # ---------- P5 code model of Region::visit: inductive invariant on the radius-2 diamond ----------
    p5(results)

    # ---------- P6 labels are counts, not shapes ----------
    diag = BitVecVal(sum(1 << CELLS.index(c) for c in [(-1, -1), (1, -1), (-1, 1), (1, 1)]), 9)
    check("P6  centre class independent of the 4 diagonals (spec)", [], spec_class(mask, 0, 0) == spec_class(mask & ~diag, 0, 0), unsat)
    check("P6  centre class independent of the 4 diagonals (Rust table)", [],
          table_expr(rows, "u4") == z3.substitute(table_expr(rows, "u4"), (mask, mask & ~diag)), unsat)
    m1 = check("P6  witness: u=2 with opposite unvisited nbrs (strip, not corner)", [],
               Not(And(spec_class(mask, 0, 0) == 2, Not(vis(mask, 0, -1)), Not(vis(mask, 0, 1)))), sat)
    m2 = check("P6  witness: u=1 (E open) but both west diagonals unvisited (T-junction, not flat)", [],
               Not(And(spec_class(mask, 0, 0) == 1, Not(vis(mask, 1, 0)), Not(vis(mask, -1, -1)), Not(vis(mask, -1, 1)))), sat)
    for nm, m in (("strip", m1), ("T-junction", m2)):
        if m is not None:
            print(f"      {nm} witness mask = {m.eval(mask).as_long():09b} (bit w = cell w, w = 3*(y+1)+(x+1))")
    # share of 4-neighbourhood patterns: of the 6 u=2 patterns, 2 are opposite pairs
    print("      u=2 4-neighbourhood patterns: 4 adjacent pairs (corners), 2 opposite pairs (strips)")

    # ---------- P7 u = 4 absent after the first step ----------
    w4 = [r for r in walks if r["p4"] != "0" or r["b4"] != "0" or r["f4"] != "0"]
    note("P7  scripted walks: p4 = b4 = f4 = 0 in every emitted window", not w4, f"{len(w4)} nonzero")
    old = list(csv.DictReader(OLD.open()))
    o4 = [r for r in old if r["p4"] != "0" or r["b4"] != "0" or r["f4"] != "0"]
    note(f"P7  2026-10-20 classes.csv: p4 = b4 = f4 = 0 in all {len(old)} rows", not o4, f"{len(o4)} nonzero; k range {min(int(r['k']) for r in old)}..{max(int(r['k']) for r in old)}")

    # ---------- negative controls: each must be rejected ----------
    print("\nnegative controls (each must be rejected; 'ok' means rejected as expected)")
    clipped = [dict(r) for r in rows]
    for r in clipped:
        if int(r["u4"]) != UNV:
            r["u4"] = str(min(int(r["u4"]), 2))
    check("N1  table with class clipped at 2 == spec?", [], table_expr(clipped, "u4") == spec_class(mask, 0, 0), sat)
    flip = [dict(r) for r in rows]
    flip[511]["u4"] = "1"
    check("N2  table with one flipped entry (mask 511 centre 0->1) == spec?", [], table_expr(flip, "u4") == spec_class(mask, 0, 0), sat)
    bad = [dict(r) for r in walks]
    bad[len(bad) // 2]["b2"] = str(int(bad[len(bad) // 2]["b2"]) + 1)
    n3 = compare(bad, replayed)
    note("N3  walk row with b2 + 1 rejected by replay", len(n3) == 1, f"{len(n3)} mismatch")
    asym = lambda m, x, y: spec_class(m, x, y, NBR[:3])
    g = d4_maps()[1]
    check("N4  asymmetric spec (N, E, S only) D4-equivariant?", [],
          And([asym(permute(mask, g), *g(x, y)) == asym(mask, x, y) for x, y in CELLS]), sat)
    moore = NBR + [(-1, -1), (1, -1), (-1, 1), (1, 1)]
    check("N5  Moore-count spec (8 nbrs) == Rust table?", [], table_expr(rows, "u4") == spec_class(mask, 0, 0, moore), sat)
    p5(results, mutant=True)

    n_ok = sum(ok for _, ok in results)
    print(f"\n{n_ok}/{len(results)} checks as expected")
    sys.exit(0 if n_ok == len(results) else 1)


def replay(max_log2, path):
    """Own ant-free replay: recompute every class from the visited set at each step (no incremental counters)."""
    V = {(0, 0)}
    pos, newborn, t, out = (0, 0), None, 0, []
    unv = lambda c: sum((c[0] + dx, c[1] + dy) not in V for dx, dy in NBR)
    for k in range(max_log2):
        w = dict(new_cells=0, b=[0] * 5, f=[0] * 5, bs=0, fresh=0)
        while t < (1 << (k + 1)):
            u = unv(pos)
            if u > 0:
                w["b"][u] += 1
                w["bs"] += 1
                w["fresh"] += u
                if pos == newborn:
                    w["f"][u] += 1
            dx, dy = NBR[int(path[t])]
            pos, t, newborn = (pos[0] + dx, pos[1] + dy), t + 1, None
            if pos not in V:
                V.add(pos)
                w["new_cells"] += 1
                newborn = pos
        if k >= 8:
            p = [0] * 5
            for c in V:
                p[unv(c)] += 1
            P = sum(1 for c in V if any((c[0] + dx, c[1] + dy) not in V for dx, dy in NBR))
            out.append(dict(k=k + 1, area=len(V), p=p, P=P, **w))
    return out


def compare(walks, replayed):
    bad = []
    by = {}
    for r in walks:
        by.setdefault(r["walk"], []).append(r)
    for name, ws in by.items():
        rep = replayed[name]
        if len(rep) != len(ws):
            bad.append((name, "window count"))
            continue
        for r, e in zip(ws, rep):
            got = [int(r[c]) for c in ["k", "area", "p0", "p1", "p2", "p3", "p4", "new_cells", "b1", "b2", "b3", "b4", "f1", "f2", "f3", "f4"]]
            exp = [e["k"], e["area"], *e["p"], e["new_cells"], *e["b"][1:], *e["f"][1:]]
            probe = [int(r[c]) for c in ["probe_area", "probe_perimeter", "probe_new_cells", "probe_boundary_steps", "probe_fresh_nbrs"]]
            if got != exp or probe != [e["area"], e["P"], e["new_cells"], e["bs"], e["fresh"]] or r["escaped"] != "false":
                bad.append((name, r["k"]))
    return bad


def p5(results, mutant=False):
    """Transcription of Region::visit (examples/kappa_exposure_classes.rs) for visiting cell i = (0, 0).

    State: visited flags on the radius-2 diamond, stored counters unv on the five cells that visit() can touch,
    class bins pc (an array). Pre: invariant on those five cells, i unvisited. Post: invariant again, pc moved by
    exactly the change in class membership, and no counter is decremented from 0 or indexed outside 0..4.
    Cells outside the five keep flags and counters (visit() writes only i and i + d), and their neighbour sets
    do not contain i, so their part of the invariant is untouched (frame argument, not mechanised).
    """
    D = [(x, y) for x in range(-2, 3) for y in range(-2, 3) if abs(x) + abs(y) <= 2]
    inner = [(0, 0)] + NBR
    v = {c: Bool(f"v{c}") for c in D}
    unv = {c: Int(f"unv{c}") for c in inner}
    pc = z3.Array("pc", z3.IntSort(), z3.IntSort())
    cnt = lambda vv, c: Sum([If(vv.get((c[0] + dx, c[1] + dy), z3.BoolVal(False)), 0, 1) for dx, dy in NBR])
    # neighbours of inner cells all lie in D, so vv.get(..., False) is never used for them
    assert all((c[0] + dx, c[1] + dy) in D for c in inner for dx, dy in NBR)
    inv = lambda vv, uu: And([If(vv[c], uu[c] == cnt(vv, c), uu[c] == UNV) for c in inner])
    pre = [inv(v, unv), Not(v[(0, 0)])]
    # --- code, statement by statement ---
    u = IntVal(0)
    uu = dict(unv)
    p = pc
    safe = []
    for i, (dx, dy) in enumerate(NBR):
        j = (dx, dy)
        if mutant and i == 1:  # mutant: forget to decrement the E neighbour
            u = If(uu[j] == UNV, u + 1, u)
            continue
        is_unv = uu[j] == UNV
        safe.append(Implies(Not(is_unv), And(uu[j] >= 1, uu[j] <= 4)))
        p = If(is_unv, p, z3.Store(z3.Store(p, uu[j], z3.Select(p, uu[j]) - 1), uu[j] - 1, z3.Select(z3.Store(p, uu[j], z3.Select(p, uu[j]) - 1), uu[j] - 1) + 1))
        u = If(is_unv, u + 1, u)
        uu[j] = If(is_unv, uu[j], uu[j] - 1)
    uu[(0, 0)] = u
    p = z3.Store(p, u, z3.Select(p, u) + 1)
    v2 = dict(v)
    v2[(0, 0)] = z3.BoolVal(True)
    delta_ok = And([z3.Select(p, b) - z3.Select(pc, b) ==
                    Sum([If(And(v2[c], uu[c] == b), 1, 0) for c in inner]) - Sum([If(And(v[c], unv[c] == b), 1, 0) for c in inner])
                    for b in range(5)])
    goal = And(inv(v2, uu), delta_ok, And(safe), u >= 0, u <= 4)
    if mutant:
        check("N6  mutant visit() (E neighbour not decremented) preserves invariant?", pre, goal, sat)
    else:
        check("P5  visit(i): invariant & pc bookkeeping preserved, no u8 underflow", pre, goal, unsat)


if __name__ == "__main__":
    main()
