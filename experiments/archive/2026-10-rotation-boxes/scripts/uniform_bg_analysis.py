"""Score the registered predictions U1-U4 of part 3 (README) from results/uniform_bg_shapes_{1e8,1e9}.csv.
Run: uv run --frozen experiments/archive/2026-10-rotation-boxes/scripts/uniform_bg_analysis.py"""
import csv, itertools, pathlib

R = pathlib.Path(__file__).resolve().parents[1] / "results"
cls = [l.split() for l in (R / "uniform_bg_classes.txt").read_text().splitlines()]


def load(T):
    d = {}
    for r in csv.DictReader(open(R / f"uniform_bg_shapes_{T}.csv")):
        d.setdefault(r["rule"], {})[int(r["k"])] = r["shape"]
    return d


S = {"1e8": load(100000000)}
if (R / "uniform_bg_shapes_1000000000.csv").exists():
    S["1e9"] = load(1000000000)
out = []
P = lambda *a: (print(*a), out.append(" ".join(map(str, a))))


def coincident(shapes):
    return {(a, b) for a, b in itertools.combinations(sorted(shapes), 2) if shapes[a] == shapes[b] and shapes[a] != "left_board"}


def rotated(w, k):
    return w[k:] + w[:k]


def trivial(w, a, b):
    """Coincidence guaranteed by symmetry: the two backgrounds give the same rotated rule, or mirror images of each other
    (footprints are mirror-invariant, control C2). NOT part of the registered scoring: added after seeing the control classes."""
    ra, rb = rotated(w, a), rotated(w, b)
    return ra == rb or rb == ra.translate(str.maketrans("LR", "RL"))


for h, D in S.items():
    P(f"\n== {h} steps: footprints of each class representative on all n uniform backgrounds")
    summ = {"A": [0, 0, 0, 0, 0], "B": [0, 0, 0, 0, 0]}  # classes with a pair, all-identical classes, pairs, classes with a non-trivial pair, non-trivial pairs
    for pop, rule in cls:
        sh = D[rule]
        c = coincident(sh)
        nt = {p for p in c if not trivial(rule, *p)}
        left = sum(v == "left_board" for v in sh.values())
        n = len(sh)
        distinct = len(set(sh.values()))
        summ[pop][0] += bool(c)
        summ[pop][1] += distinct == 1
        summ[pop][2] += len(c)
        summ[pop][3] += bool(nt)
        summ[pop][4] += len(nt)
        P(f"  {pop} {rule:<12} n={n:<2} left board {left:<2} distinct {distinct:<2} coincident pairs {len(c):<2} of which non-trivial {len(nt):<2} {sorted(nt) if nt else ''}")
    for pop in "AB":
        P(f"  population {pop}: {summ[pop][0]} of {sum(1 for p, _ in cls if p == pop)} classes have a coincident pair; "
          f"{summ[pop][1]} have all backgrounds identical; {summ[pop][2]} coincident pairs in total "
          f"[post hoc: excluding pairs forced by mirror/rotation symmetry, {summ[pop][3]} classes and {summ[pop][4]} pairs remain]")
if "1e9" in S:
    P("\n== U4 (non-trivial pairs only; symmetric pairs coincide forever by construction): coincident pairs at 1e8 that still coincide at 1e9")
    tot = kept = 0
    for pop, rule in cls:
        for a, b in coincident(S["1e8"][rule]):
            if trivial(rule, a, b):
                continue  # post hoc: symmetric pairs coincide at every horizon by construction
            tot += 1
            kept += S["1e9"][rule][a] == S["1e9"][rule][b]
    P(f"  {tot} coincident pairs at 1e8; {kept} still coincide at 1e9 ({tot - kept} do not: {100*(tot-kept)/max(tot,1):.0f}%)")
(R / "uniform_bg_analysis.txt").write_text("\n".join(out) + "\n")
