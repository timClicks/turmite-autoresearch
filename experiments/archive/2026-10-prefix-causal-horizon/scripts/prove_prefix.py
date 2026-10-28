# /// script
# requires-python = ">=3.12"
# dependencies = ["z3-solver==4.13.4.0"]
# ///
"""Machine-check the inductive steps of the prefix lemmas (README of this experiment) with z3.

The grid is an SMT array Z -> (Z -> colour), so the obligations hold for an unbounded board. A rule is a length n and an
array of turn deltas D (1 = R, 3 = L), with n and the letters symbolic wherever possible. Each lemma is the usual
simulation-relation proof: base case (equal blank boards) is trivial; the *step* obligation is "Inv and guard imply Inv after one
step in both runs", checked by asking z3 for a counterexample (unsat = proved). The outer induction on the number of steps and the
definition of F_p as the first step that violates the guard are the pen-and-paper part (README).

Negative controls live in prove_controls.py (quantifier-free, so z3 can return a model).

Run: uv run experiments/archive/2026-10-prefix-causal-horizon/scripts/prove_prefix.py
"""
import sys
from z3 import (And, Array, ArraySort, ForAll, If, Implies, Int, IntSort, Not, Or, Select, Solver, Store, sat, unsat, unknown)

Z = IntSort()
GridSort = ArraySort(Z, ArraySort(Z, Z))
DX = lambda h: If(h == 0, 0, If(h == 1, 1, If(h == 2, 0, -1)))  # src/lib.rs: DIRS = [(0,-1),(1,0),(0,1),(-1,0)]
DY = lambda h: If(h == 0, -1, If(h == 1, 0, If(h == 2, 1, 0)))

get = lambda g, x, y: Select(Select(g, x), y)
put = lambda g, x, y, v: Store(g, x, Store(Select(g, x), y, v))
nxt = lambda c, n: If(c + 1 == n, 0, c + 1)  # (c + 1) mod n for 0 <= c < n


class State:
    def __init__(self, tag):
        self.x, self.y, self.h = Int(f"x{tag}"), Int(f"y{tag}"), Int(f"h{tag}")
        self.g = Array(f"g{tag}", Z, ArraySort(Z, Z))

    def colour(self):
        return get(self.g, self.x, self.y)


def step(s, n, D, newg=None):
    """One ant step as a tuple (x, y, h, g); `newg` overrides the written colour (used by the wrap-flag lemma)."""
    c = s.colour()
    h = (s.h + Select(D, c)) % 4
    return (s.x + DX(h), s.y + DY(h), h, put(s.g, s.x, s.y, nxt(c, n) if newg is None else newg))


def rule_ok(n, D):
    c = Int("c_ok")
    return And(n >= 1, ForAll([c], Implies(And(0 <= c, c < n), Or(Select(D, c) == 1, Select(D, c) == 3))))


def colours_in_range(s, n):
    a, b = Int("a_r"), Int("b_r")
    return ForAll([a, b], And(0 <= get(s.g, a, b), get(s.g, a, b) < n))


def check(name, premises, goal, expect):
    sol = Solver()
    sol.set("timeout", 120_000)
    sol.add(*premises, Not(goal))
    r = sol.check()
    verdict = {"unsat": "unsat (proved)", "sat": "sat (counterexample)", "unknown": "unknown"}[str(r)]
    ok = str(r) == str(expect)
    print(f"{'ok  ' if ok else 'FAIL'} {name:<62} {verdict}", flush=True)
    return ok


def same_pos(a, b):
    return And(a[0] == b[0], a[1] == b[1])


def main():
    results = []
    n, m, p = Int("n"), Int("n_prime"), Int("p")
    D, E = Array("D", Z, Z), Array("E", Z, Z)  # turn deltas of w and w'
    s, t = State("1"), State("2")
    i = Int("i")
    agree_below_p = ForAll([i], Implies(And(0 <= i, i < p), Select(D, i) == Select(E, i)))
    inv_eq = And(s.x == t.x, s.y == t.y, s.h == t.h, s.g == t.g, 0 <= s.h, s.h < 4)

    # ---- Lemma 0: colours stay in [0, n) ----
    a0, b0 = Int("a0"), Int("b0")
    g_after = step(s, n, D)[3]
    results.append(check("L0  step keeps every colour in [0, n)  (n symbolic)",
                         [rule_ok(n, D), colours_in_range(s, n)],
                         ForAll([a0, b0], And(0 <= get(g_after, a0, b0), get(g_after, a0, b0) < n)), unsat))

    # ---- Lemma A: step preserves equality while the colour read is < p; divergence when it is p ----
    base = [rule_ok(n, D), rule_ok(m, E), 1 <= p, p < n, p < m, agree_below_p, inv_eq, colours_in_range(s, n), colours_in_range(t, m)]
    c = s.colour()
    stepA, stepB = step(s, n, D), step(t, m, E)
    eq_after = And(stepA[0] == stepB[0], stepA[1] == stepB[1], stepA[2] == stepB[2], stepA[3] == stepB[3])
    results.append(check("A   Inv & read colour < p  =>  Inv after one step  (n, n', p symbolic)", base + [c < p], eq_after, unsat))
    results.append(check("A   read colour == p & D[p] != E[p]  =>  positions differ", base + [c == p, Select(D, p) != Select(E, p)],
                         Not(same_pos(stepA, stepB)), unsat))

    # ---- Lemma B (prefix case, n < n'): at w' 's first read of colour n, w reads its wrapped cell (colour 0), w' reads n ----
    # Equal-state premise only on the ant (position, heading); the grid relation up to that step is Lemma L's.
    cB = And(s.colour() == 0, t.colour() == n)
    results.append(check("B   w reads 0, w' reads n  =>  (D[0] != E[n]) iff positions differ",
                         [rule_ok(n, D), rule_ok(m, E), n >= 1, n < m, s.x == t.x, s.y == t.y, s.h == t.h, 0 <= s.h, s.h < 4, cB],
                         (Select(D, 0) != Select(E, n)) == Not(same_pos(step(s, n, D), step(t, m, E))), unsat))

    # ---- Lemma L: lift.  w' colours c' correspond to w colours c' mod n, until w' wraps. Concrete lengths 1..12, letters symbolic. ----
    ok_all = True
    for nn in range(1, 13):
        for mm in range(nn + 1, 13):
            n_, m_ = nn, mm
            sl, tl = State("l1"), State("l2")
            wr = Array("wrap", Z, ArraySort(Z, Z))
            a, b = Int("a"), Int("b")
            inv = And(sl.x == tl.x, sl.y == tl.y, sl.h == tl.h, 0 <= sl.h, sl.h < 4,
                      ForAll([a, b], Implies(get(wr, a, b) == 0, get(sl.g, a, b) == get(tl.g, a, b) % n_)),
                      ForAll([a, b], And(0 <= get(tl.g, a, b), get(tl.g, a, b) < m_)),
                      ForAll([a, b], And(0 <= get(sl.g, a, b), get(sl.g, a, b) < n_)))
            ct = tl.colour()
            turn_agree = Select(D, ct % n_) == Select(E, ct)
            valid = [rule_ok(n_, D), rule_ok(m_, E), inv, get(wr, tl.x, tl.y) == 0, turn_agree]
            sw, tw = step(sl, n_, D), step(tl, m_, E)
            is_wrap = (ct == m_ - 1)
            wr2 = put(wr, tl.x, tl.y, If(is_wrap, 1, get(wr, tl.x, tl.y)))
            a2, b2 = Int("a2"), Int("b2")
            inv_after = And(same_pos(sw, tw), sw[2] == tw[2],
                            ForAll([a2, b2], Implies(get(wr2, a2, b2) == 0, get(sw[3], a2, b2) == get(tw[3], a2, b2) % n_)))
            ok_all &= check(f"L   lift step, n={n_:>2} n'={m_:>2}  (letters symbolic)", valid, inv_after, unsat)
    results.append(ok_all)

    # ---- Lemma R: n | n' and w' = w repeated: relation g_w == g_w' mod n holds through the wrap, no flag needed ----
    for n_, m_ in ((1, 3), (2, 4), (3, 6), (4, 12), (5, 10)):
        sl, tl = State("r1"), State("r2")
        invr = And(sl.x == tl.x, sl.y == tl.y, sl.h == tl.h, 0 <= sl.h, sl.h < 4,
                   ForAll([a, b], get(sl.g, a, b) == get(tl.g, a, b) % n_),
                   ForAll([a, b], And(0 <= get(tl.g, a, b), get(tl.g, a, b) < m_)), ForAll([a, b], And(0 <= get(sl.g, a, b), get(sl.g, a, b) < n_)))
        per = ForAll([i], Implies(And(0 <= i, i < m_), Select(E, i) == Select(D, i % n_)))
        sw, tw = step(sl, n_, D), step(tl, m_, E)
        goal = And(same_pos(sw, tw), sw[2] == tw[2], ForAll([Int("a4"), Int("b4")], get(sw[3], Int("a4"), Int("b4")) == get(tw[3], Int("a4"), Int("b4")) % n_))
        results.append(check(f"R   w' = w^{m_ // n_} (n={n_}, n'={m_}) step keeps trajectories equal incl. wrap", [rule_ok(n_, D), rule_ok(m_, E), invr, per], goal, unsat))
    print(f"\n{sum(results)}/{len(results)} checks as expected")
    sys.exit(0 if all(results) else 1)



if __name__ == "__main__":
    main()
