"""Post hoc sparse replay of the largest k=1 shortening, independent of Rust.

This is a verification example selected from the pilot, not another hypothesis test.
"""
import csv
import json
from collections import defaultdict, deque
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
MASK = (1 << 64) - 1
DIRS = [(0, -1), (1, 0), (0, 1), (-1, 0)]


def mix(value):
    value = ((value ^ (value >> 30)) * 0xBF58476D1CE4E5B9) & MASK
    value = ((value ^ (value >> 27)) * 0x94D049BB133111EB) & MASK
    return value ^ (value >> 31)


def next_random(state):
    state = (state + 0x9E3779B97F4A7C15) & MASK
    return state, mix(state)


def initial(rule, seed, pos):
    x, y = pos
    if abs(x) > 2 or abs(y) > 2:
        return 0
    key = ((x & 0xFFFFFFFF) << 32) | (y & 0xFFFFFFFF)
    return mix(mix(seed ^ 0x5851F42D4C957F2D) ^ key) % len(rule)


def step(rule, cells, pos, heading):
    colour = cells.get(pos, 0)
    heading = (heading + (1 if rule[colour] == "R" else -1)) % 4
    cells[pos] = (colour + 1) % len(rule)
    dx, dy = DIRS[heading]
    return (pos[0] + dx, pos[1] + dy), heading


def main():
    candidates = []
    for path in sorted((HERE / "results").glob("*.csv")):
        if path.name.endswith(".audit.csv"):
            continue
        candidates.extend(r for r in csv.DictReader(path.open()) if r["k"] == "1")
    row = max(candidates, key=lambda r: int(r["base_t"]) / int(r["arm_t"]))
    rule, seed, t0 = row["rule"], int(row["seed"]), int(row["t0"])
    cells, visited = {}, set()
    pos, heading = (0, 0), 0
    for time in range(t0 + 1):
        if pos not in visited:
            visited.add(pos)
            cells[pos] = initial(rule, seed, pos)
        if time < t0:
            pos, heading = step(rule, cells, pos, heading)
    neighbours = lambda p: [(p[0]+dx, p[1]+dy) for dx, dy in DIRS]
    boundary = {p for p in visited if any(q not in visited for q in neighbours(p))}
    interior = visited - boundary
    assert pos in interior
    depth = {p: 0 for p in boundary}
    queue = deque(sorted(boundary))
    while queue:
        p = queue.popleft()
        for q in neighbours(p):
            if q in visited and q not in depth:
                depth[q] = depth[p] + 1
                queue.append(q)

    state = 0xCBF29CE484222325
    for byte in rule.encode():
        state = ((state ^ byte) * 0x100000001B3) & MASK
    for part in [seed, int(row["band"]), int(row["departure"]), 1, int(row["replica"])]:
        _, state = next_random(state ^ part)
    groups = defaultdict(list)
    for p in sorted(interior, key=lambda p: (p[1], p[0])):
        groups[depth[p] // 8, 1 if rule[cells[p]] == "R" else 3].append(p)
    altered = cells.copy()
    for key in sorted(groups):
        points = groups[key]
        for j in range(len(points)-1, 0, -1):
            size = j + 1
            threshold = ((-size) & MASK) % size
            while True:
                state, value = next_random(state)
                if value >= threshold:
                    break
            a, b = points[j], points[value % size]
            altered[a], altered[b] = altered[b], altered[a]
    assert all(rule[cells[p]] == rule[altered[p]] for p in visited)
    assert all(cells[p] == altered[p] for p in boundary)
    assert sum(cells[p] != altered[p] for p in interior) == int(row["changed"])

    def episode(field):
        p, h, path, reads = pos, heading, [], []
        for duration in range(1, 2**18 + 1):
            reads.append(p)
            p, h = step(rule, field, p, h)
            path.append((p, h))
            if p in boundary:
                return duration, path, reads
        raise AssertionError("witness was censored")

    base_t, base_path, reads = episode(cells.copy())
    arm_t, arm_path, _ = episode(altered.copy())
    assert (base_t, arm_t) == (int(row["base_t"]), int(row["arm_t"]))
    split = next(i for i, (a, b) in enumerate(zip(base_path, arm_path)) if a != b)
    source = reads[split]
    visits = reads[:split+1].count(source)
    assert (split+1, visits) == (int(row["split_step"]), int(row["split_visit"]))
    n = len(rule)
    result = dict(selection="Post hoc maximum base_t / arm_t among all k=1 rows; not representative",
        row=row, independent_sparse_replay="passed", next_turn_equal_on_every_visited_cell=True,
        departure_position=pos, departure_heading=heading, split_source=source,
        split_source_initial_colours=[cells[source], altered[source]],
        split_source_future_turns=["".join(rule[(c+i)%n] for i in range(n)) for c in [cells[source], altered[source]]],
        baseline_first_steps=base_path[:12], arm_path=arm_path)
    (HERE / "results/witness.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
