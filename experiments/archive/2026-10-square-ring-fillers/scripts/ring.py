"""Shared helpers for the square-ring-fillers analyses (stdlib only)."""


def T(rule, v):
    return rule[v % len(rule)]


def pi_k(rule, kmax=64):
    """Smallest k >= 1 with Pi(k): T(v) = R for v in [0, 2k+2] except T(k) = L (README). None if no k <= kmax."""
    for k in range(1, kmax + 1):
        if T(rule, k) == "L" and all(T(rule, v) == "R" for v in range(2 * k + 3) if v != k):
            return k
    return None


def parse_reads(s):
    out = {}
    for part in filter(None, s.split(";")):
        v, c = part.split(":")
        out[64 if v == "64+" else int(v)] = int(c)
    return out
