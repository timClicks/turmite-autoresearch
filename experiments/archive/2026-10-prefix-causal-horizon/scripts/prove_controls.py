# /// script
# requires-python = ">=3.12"
# dependencies = ["z3-solver==4.13.4.0"]
# ///
"""Negative controls for prove_prefix.py: weaken one premise of a lemma and z3 must find a counterexample; restore it and z3
must prove the step. Each control and its twin use the same concrete lengths and the same quantifier-free state (an otherwise
blank grid with one coloured cell under the ant), so the only difference is the premise under test.

Run: uv run experiments/archive/2026-10-prefix-causal-horizon/scripts/prove_controls.py
"""
import sys
from z3 import And, Array, Int, K, Or, Select, sat, unsat
from prove_prefix import DX, DY, Z, check, get, nxt, put, same_pos


def zero_grid():
    return K(Z, K(Z, 0))


def valid_letters(D, k):
    return And(*[Or(Select(D, i) == 1, Select(D, i) == 3) for i in range(k)])


class S:
    """Ant at (x, y) heading h, blank grid except the cell under it holding colour c."""
    def __init__(self, tag, c):
        self.x, self.y, self.h, self.c = Int(f"x{tag}"), Int(f"y{tag}"), Int(f"h{tag}"), c
        self.g = put(zero_grid(), self.x, self.y, c)


def one_step(s, n, D):
    h = (s.h + Select(D, s.c)) % 4
    return s.x + DX(h), s.y + DY(h), h, put(s.g, s.x, s.y, nxt(s.c, n))


def run():
    D, E = Array("D", Z, Z), Array("E", Z, Z)
    ok = []
    x, y, h = Int("x"), Int("y"), Int("h")
    st = [0 <= h, h < 4]

    def pair(cA, cB, nA, nB):
        a, b = S("a", cA), S("b", cB)
        a.x, a.y, a.h = x, y, h
        b.x, b.y, b.h = x, y, h
        a.g, b.g = put(zero_grid(), x, y, cA), put(zero_grid(), x, y, cB)
        return a, b, one_step(a, nA, D), one_step(b, nB, E)

    # NC1 / twin: lemma A, n=3, n'=4, p=2. Colour read c: guard c < p (proved) vs c <= p (control).
    for c, expect, label in ((1, unsat, "twin: colour read 1 < p=2"), (2, sat, "NC1 : colour read 2 == p, guard widened")):
        a, b, sa, sb = pair(c, c, 3, 4)
        letters = And(valid_letters(D, 3), valid_letters(E, 4), Select(D, 0) == Select(E, 0), Select(D, 1) == Select(E, 1))
        eq = And(same_pos(sa, sb), sa[2] == sb[2], sa[3] == sb[3])
        ok.append(check(f"A  n=3 n'=4 p=2, {label}: Inv after one step", [letters] + st, eq, expect))

    # NC2 / twin: lemma L step, n=3, n'=5, w' reads colour 1 (= 1 mod 3). Turn agreement premise present vs dropped.
    for agree, expect, label in ((True, unsat, "twin: D[1] == E[1]"), (False, sat, "NC2 : turn agreement dropped")):
        a, b, sa, sb = pair(1, 1, 3, 5)
        prem = [valid_letters(D, 3), valid_letters(E, 5)] + st + ([Select(D, 1) == Select(E, 1)] if agree else [])
        ok.append(check(f"L  n=3 n'=5, {label}: positions equal after the step", prem, And(same_pos(sa, sb), sa[2] == sb[2]), expect))

    # NC3 / twin: grid relation g_w = g_w' mod n across a wrap step (w' reads n'-1). n | n' keeps it, n not dividing n' breaks it.
    for (n, m, cw, cp), expect, label in ((((3, 6, 2, 5)), unsat, "twin: n=3 divides n'=6"), (((3, 5, 1, 4)), sat, "NC3 : n=3 does not divide n'=5, no wrap flag")):
        a, b, sa, sb = pair(cw, cp, n, m)
        letters = And(valid_letters(D, n), valid_letters(E, m), Select(D, cw) == Select(E, cp))
        rel = (get(sb[3], x, y) % n) == get(sa[3], x, y)  # the written cell is the only one that changed
        ok.append(check(f"L  wrap step, {label}: relation g_w = g_w' mod n kept", [letters] + st, rel, expect))

    # NC4 / twin: lemma R (w' = w repeated) vs a periodic extension of the wrong length, positions and relation after the wrap.
    for (n, m), expect, label in (((2, 4), unsat, "twin: w' = w w"), ((3, 5), sat, "NC4 : w' = w + 2 letters of w")):
        c2 = m - 1
        a, b, sa, sb = pair(c2 % n, c2, n, m)
        per = And(*[Select(E, i) == Select(D, i % n) for i in range(m)])
        rel = And(same_pos(sa, sb), (get(sb[3], x, y) % n) == get(sa[3], x, y))
        ok.append(check(f"R  n={n} n'={m}, {label}: trajectories equal through the wrap", [valid_letters(D, n), valid_letters(E, m), per] + st, rel, expect))

    print(f"\n{sum(ok)}/{len(ok)} controls as expected")
    return all(ok)


if __name__ == "__main__":
    sys.exit(0 if run() else 1)
