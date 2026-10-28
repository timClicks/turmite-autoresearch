"""Task C1: an independent implementation of the generalised Langton ant and of the sweeper family's text format.

No import from the turmite crate or from the first checker. Uses only the rule definition (AGENTS.md: colour c turns by
rule[c], advances to (c + 1) % n, steps forward) and results/canonical_k0.txt read as text.

Coordinates: x grows east, y grows SOUTH (row index of the canonical file, top row = smallest y). A heading table maps
heading -> (dx, dy). The two chiralities are `CW` (increasing heading turns N -> E -> S -> W on the page, y down) and `CCW`;
both have heading 3 = west, which is what canonical_k0.txt fixes.
"""
from pathlib import Path

CW = ((0, -1), (1, 0), (0, 1), (-1, 0))    # 0 = N, 1 = E, 2 = S, 3 = W
CCW = ((0, 1), (1, 0), (0, -1), (-1, 0))   # 0 = S, 1 = E, 2 = N, 3 = W
STRIP = 48                                  # columns of the family window: x = 0 .. 47, the front is column 0

ROOT = Path(__file__).resolve().parents[4]
E = ROOT / "experiments/archive/2026-10-rlrlll-macro-transition"


class Ant:
    """Sparse-grid ant; colour 0 is absent from the dict. `table`/`rsign` select the heading convention."""

    def __init__(self, rule, cells=None, pos=(0, 0), h=0, table=CW, rsign=1):
        self.rule, self.n, self.table, self.rsign = rule, len(rule), table, rsign
        self.cells = dict(cells or {})
        self.pos, self.h, self.steps = pos, h, 0

    def step(self):
        """One move; returns (x, y, colour read, heading after the turn) for the cell that was read."""
        x, y = self.pos
        c = self.cells.get((x, y), 0)
        self.h = (self.h + (self.rsign if self.rule[c] == "R" else -self.rsign)) % 4
        c2 = (c + 1) % self.n
        if c2:
            self.cells[(x, y)] = c2
        else:
            self.cells.pop((x, y), None)
        dx, dy = self.table[self.h]
        self.pos = (x + dx, y + dy)
        self.steps += 1
        return x, y, c, self.h


def parse_canonical(path=None):
    """Read the proposal as text: three phases {m, dx, dy, h, top, bulk, bottom}; rows are 48-character strings, '.' = 0."""
    path = Path(path) if path else E / "results/canonical_k0.txt"
    lines = [l for l in path.read_text().splitlines() if not l.startswith("#")]
    phases, i = [], 0
    while i < len(lines):
        f = lines[i].split()
        assert f[0] == "phase" and f[-2] == "width" and int(f[-1]) == STRIP, lines[i]
        # "phase q k K m M ant DX DY H width 48"
        m, dx, dy, h = int(f[5]), int(f[7]), int(f[8]), int(f[9])
        nt = int(lines[i + 1].split()[1])
        top = lines[i + 2:i + 2 + nt]
        assert lines[i + 2 + nt] == "bulk"
        bulk = lines[i + 3 + nt]
        nb = int(lines[i + 4 + nt].split()[1])
        bottom = lines[i + 5 + nt:i + 5 + nt + nb]
        i += 5 + nt + nb
        for r in top + [bulk] + bottom:
            assert len(r) == STRIP, len(r)
        phases.append(dict(m=m, dx=dx, dy=dy, h=h, top=top, bulk=bulk, bottom=bottom))
    assert len(phases) == 3
    return phases


def rows_of(p, m):
    """The rectangle top . bulk^m . bottom as a list of 48-char strings."""
    return list(p["top"]) + [p["bulk"]] * m + list(p["bottom"])


def cells_of(rows, y0=0):
    """Nonzero cells of a list of row strings placed with the first row at y = y0, column 0 = front."""
    # '.' is unvisited and '0' is visited-but-colour-0 in the canonical file; the dynamics see colour only.
    return {(x, y0 + j): int(ch) for j, r in enumerate(rows) for x, ch in enumerate(r) if ch not in ".0"}


def start_state(p, m):
    """(cells, pos, heading) of C(m, q) with the rectangle's top row at y = 0 and the front at x = 0."""
    return cells_of(rows_of(p, m)), (p["dx"], p["dy"]), p["h"]


def window_after_cycle(ant, shift=3):
    """Cells with x in [-shift, STRIP - shift), shifted east by `shift` so the new front is column 0. Cells east of that
    are 'arbitrary' in the family and are dropped."""
    return {(x + shift, y): c for (x, y), c in ant.cells.items() if -shift <= x < STRIP - shift}


def run_cycle(rule, p, m, table=CW, rsign=1, record=False, limit=2_000_000):
    """Run C(m, q) until the minimum x first reaches -3 (the front has moved 3 columns). Returns a dict with the step count,
    the re-anchored window and the ant. Fails (returns reason) if the ant ever stands east of column STRIP - 1.
    If `record`, also returns the list of positions the ant stood on (before each step) and the colours read."""
    cells, pos, h = start_state(p, m)
    ant = Ant(rule, cells, pos, h, table, rsign)
    trail = []
    xmin = pos[0]
    while xmin > -3:
        if record:
            trail.append(ant.pos)
        x, y, c, hh = ant.step()
        nx = ant.pos[0]
        if nx >= STRIP:
            return dict(ok=False, why=f"left the strip at column {nx}", steps=ant.steps, trail=trail)
        xmin = min(xmin, nx)
        if ant.steps > limit:
            return dict(ok=False, why="no front advance", steps=ant.steps, trail=trail)
    if record:
        trail.append(ant.pos)
    return dict(ok=True, steps=ant.steps, window=window_after_cycle(ant), ant=ant, trail=trail)


def expected_next(phases, q, m, ant_y):
    """C(m + 2, q + 1) as a dict of cells, placed so that the ant's row sits `dy` below the top row."""
    nq = phases[(q + 1) % 3]
    return cells_of(rows_of(nq, m + 2), y0=ant_y - nq["dy"])


def closes(rule, phases, q, m, table=CW, rsign=1):
    """True iff one cycle from C(m, q) is exactly C(m + 2, q + 1) (window, ant column and heading)."""
    r = run_cycle(rule, phases[q], m, table, rsign)
    if not r["ok"]:
        return False
    nq = phases[(q + 1) % 3]
    a = r["ant"]
    ant_x = a.pos[0] + 3
    return r["window"] == expected_next(phases, q, m, a.pos[1]) and ant_x == nq["dx"] and a.h == nq["h"]
