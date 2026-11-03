"""Dependency-free sparse walkers for short runs and independent oracle checks.

Coordinates and SplitMix64 match the Rust walkers. Zero-valued entries are kept:
dictionary membership is permanent departure memory, not a colour test.
This is not the tiled census runner or the complete registered Q33 instrument.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import math

MASK64 = (1 << 64) - 1
DIRS = ((0, -1), (1, 0), (0, 1), (-1, 0))
TURNS = {"S": 0, "R": 1, "U": 2, "L": 3}
VERSION = "turmite-python-sparse-v1"


def splitmix_next(state: int) -> tuple[int, int]:
    state = (state + 0x9E3779B97F4A7C15) & MASK64
    z = state
    z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & MASK64
    z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & MASK64
    return state, z ^ (z >> 31)


def persistent_turn(draw: int) -> int:
    """Exactly P(S)=127/128, P(R)=P(L)=1/256, using high-32 bits."""
    u = draw >> 32
    return (3 if u & 128 else 1) if u & 127 == 0 else 0


@dataclass(frozen=True)
class Config:
    rule: str = "RLL"
    policy: str = "ant"
    seed: int = 0
    cap: int | None = None
    fresh_set: str = "RLU"

    def __post_init__(self) -> None:
        if not self.rule or set(self.rule) - set("RL"):
            raise ValueError("rule must be a nonempty R/L string")
        if self.policy not in {"ant", "fresh-set", "persistent-fresh"}:
            raise ValueError("unknown policy")
        if type(self.seed) is not int or not 0 <= self.seed <= MASK64:
            raise ValueError("seed must be an unsigned 64-bit integer")
        if self.cap is not None and (type(self.cap) is not int or self.cap < 1):
            raise ValueError("cap must be positive or None (uncapped)")
        if self.cap is not None and self.policy != "persistent-fresh":
            raise ValueError("a cap is defined only for persistent-fresh")
        if not self.fresh_set or set(self.fresh_set) - set("RLU"):
            raise ValueError("fresh_set must contain only R, L, U")


class CellLimit(RuntimeError):
    """Stopped before a birth; the state can be resumed with a larger budget."""


class SparseWalker:
    def __init__(self, config: Config):
        self.config = config
        self.cells: dict[tuple[int, int], int] = {}
        self.boundary: set[tuple[int, int]] = set()
        self.x = self.y = self.heading = self.steps = 0
        self.state = config.seed
        self.run_length = 0
        self.origin_run = True
        self.fresh_hist: dict[int, int] = {}
        self.origin_run_length: int | None = None
        self.cap_turns = self.cap_turns_nonorigin = 0
        self.boundary_reads = self.perimeter = 0
        self.kappa_sum = 0.0
        self.kappa_defined_steps = 0
        self.bounds: tuple[int, int, int, int] | None = None

    def step(self, max_cells: int | None = None) -> bool:
        p = (self.x, self.y)
        fresh = p not in self.cells
        if fresh and max_cells is not None and len(self.cells) >= max_cells:
            raise CellLimit("departed-cell budget reached before next birth")
        self.state, draw = splitmix_next(self.state)  # consumed on EVERY step
        if self.boundary:
            on_boundary = p in self.boundary
            self.boundary_reads += on_boundary
            self.kappa_sum += on_boundary * len(self.cells) / len(self.boundary)
            self.kappa_defined_steps += 1
        c = self.cells.get(p, 0)
        if fresh:
            self.run_length += 1
        else:
            if self.run_length:
                if self.origin_run:
                    self.origin_run_length = self.run_length
                else:
                    r = self.run_length
                    self.fresh_hist[r] = self.fresh_hist.get(r, 0) + 1
                self.origin_run = False
            self.run_length = 0
        turn = TURNS[self.config.rule[c]]
        if fresh and self.config.policy == "fresh-set":
            k = ((draw >> 32) * len(self.config.fresh_set)) >> 32
            turn = TURNS[self.config.fresh_set[k]]
        elif fresh and self.config.policy == "persistent-fresh":
            if self.config.cap is not None and self.run_length >= self.config.cap:
                turn = 2
                self.cap_turns += 1
                self.cap_turns_nonorigin += not self.origin_run
            else:
                turn = persistent_turn(draw)
        self.heading = (self.heading + turn) & 3
        self.cells[p] = (c + 1) % len(self.config.rule)
        if fresh:
            neighbours = [(self.x + dx, self.y + dy) for dx, dy in DIRS]
            degree = sum(q in self.cells for q in neighbours)
            self.perimeter += 4 - 2 * degree
            if degree < 4:
                self.boundary.add(p)
            for q in neighbours:
                if q in self.boundary and all(
                    (q[0] + dx, q[1] + dy) in self.cells for dx, dy in DIRS
                ):
                    self.boundary.remove(q)
            if self.bounds is None:
                self.bounds = (self.x, self.x, self.y, self.y)
            else:
                x0, x1, y0, y1 = self.bounds
                self.bounds = min(x0, self.x), max(x1, self.x), min(y0, self.y), max(y1, self.y)
        dx, dy = DIRS[self.heading]
        self.x += dx
        self.y += dy
        self.steps += 1
        return fresh

    def snapshot(self, *, hull: bool = False) -> dict:
        sx = sy = 0
        if self.bounds is not None:
            x0, x1, y0, y1 = self.bounds
            sx, sy = x1 - x0 + 1, y1 - y0 + 1
        return {
            "steps": self.steps, "x": self.x, "y": self.y, "heading": self.heading,
            "area": len(self.cells), "span_x": sx, "span_y": sy,
            "width": math.sqrt(sx * sy), "perimeter": self.perimeter,
            "boundary_cells": len(self.boundary), "boundary_reads": self.boundary_reads,
            "kappa_sum": self.kappa_sum, "kappa_defined_steps": self.kappa_defined_steps,
            "cap_turns": self.cap_turns, "cap_turns_nonorigin": self.cap_turns_nonorigin,
            "hull_area_centres": hull_area(self.cells) if hull else None,
        }

    def fresh_summary(self) -> dict:
        return {
            "completed_nonorigin": [
                {"length": r, "count": n, "duration_weight": r * n}
                for r, n in sorted(self.fresh_hist.items())
            ],
            "origin_completed_length": self.origin_run_length,
            "unfinished": {
                "length": self.run_length, "origin": self.origin_run,
                "right_censored": bool(self.run_length),
            },
        }

    def checkpoint(self) -> dict:
        return {
            "format": VERSION, "config": asdict(self.config),
            "cells": [[x, y, c] for (x, y), c in sorted(self.cells.items())],
            "position": [self.x, self.y], "heading": self.heading,
            "steps": self.steps, "rng_state": self.state,
            "run_length": self.run_length, "origin_run": self.origin_run,
            "fresh_hist": [[r, n] for r, n in sorted(self.fresh_hist.items())],
            "origin_run_length": self.origin_run_length,
            "cap_turns": self.cap_turns, "cap_turns_nonorigin": self.cap_turns_nonorigin,
            "boundary_reads": self.boundary_reads, "kappa_sum": self.kappa_sum,
            "kappa_defined_steps": self.kappa_defined_steps,
        }

    @classmethod
    def from_checkpoint(cls, data: dict) -> SparseWalker:
        if data.get("format") != VERSION:
            raise ValueError("unsupported checkpoint format")
        walker = cls(Config(**data["config"]))
        triples = data["cells"]
        if any(len(t) != 3 or any(type(v) is not int for v in t)
               or not 0 <= t[2] < len(walker.config.rule) for t in triples):
            raise ValueError("invalid cell record")
        walker.cells = {(x, y): c for x, y, c in triples}
        if len(walker.cells) != len(triples):
            raise ValueError("duplicate checkpoint coordinates")
        walker.x, walker.y = data["position"]
        walker.heading = data["heading"]
        walker.steps = data["steps"]
        walker.state = data["rng_state"]
        if (any(type(v) is not int for v in (walker.x, walker.y, walker.heading, walker.steps, walker.state))
                or not 0 <= walker.heading < 4 or walker.steps < len(walker.cells)
                or not 0 <= walker.state <= MASK64):
            raise ValueError("invalid checkpoint clock/position/RNG")
        for name in ("run_length", "origin_run", "origin_run_length", "cap_turns",
                     "cap_turns_nonorigin", "boundary_reads", "kappa_sum", "kappa_defined_steps"):
            setattr(walker, name, data[name])
        walker.fresh_hist = dict(data["fresh_hist"])
        counters = (walker.run_length, walker.cap_turns, walker.cap_turns_nonorigin,
                    walker.boundary_reads, walker.kappa_defined_steps)
        if (any(type(v) is not int or v < 0 or v > walker.steps for v in counters)
                or type(walker.origin_run) is not bool
                or not isinstance(walker.kappa_sum, (int, float))
                or not math.isfinite(walker.kappa_sum) or walker.kappa_sum < 0
                or walker.cap_turns_nonorigin > walker.cap_turns
                or len(walker.fresh_hist) != len(data["fresh_hist"])
                or any(type(r) is not int or type(n) is not int or r < 1 or n < 1
                       for r, n in walker.fresh_hist.items())):
            raise ValueError("invalid checkpoint counters")
        origin = walker.origin_run_length
        if origin is not None and (type(origin) is not int or origin < 1):
            raise ValueError("invalid origin run")
        if (sum(r * n for r, n in walker.fresh_hist.items()) + (origin or 0)
                + walker.run_length != len(walker.cells)):
            raise ValueError("fresh-run accounting does not match area")
        if walker.state != (walker.config.seed + walker.steps * 0x9E3779B97F4A7C15) & MASK64:
            raise ValueError("checkpoint RNG clock mismatch")
        # Rebuild derived geometry rather than trusting redundant cached values.
        for x, y in walker.cells:
            missing = sum((x + dx, y + dy) not in walker.cells for dx, dy in DIRS)
            walker.perimeter += missing
            if missing:
                walker.boundary.add((x, y))
        if walker.cells:
            xs, ys = zip(*walker.cells)
            walker.bounds = min(xs), max(xs), min(ys), max(ys)
        return walker


def hull_area(points) -> float:
    """Convex hull of cell CENTRES; lines and singleton sets have zero area."""
    pts = sorted(points)
    if len(pts) < 3:
        return 0.0

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    lower, upper = [], []
    for p in pts:
        while len(lower) > 1 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    for p in reversed(pts):
        while len(upper) > 1 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    h = lower[:-1] + upper[:-1]
    return abs(sum(a[0] * b[1] - a[1] * b[0] for a, b in zip(h, h[1:] + h[:1]))) / 2


def sample_steps(target: int, start: int = 0, *, suboctaves: bool = False) -> list[int]:
    """Absolute log schedule plus endpoints; usable for resumed segments."""
    result = {start, target}
    for k in range(max(1, target).bit_length()):
        for j in range(8 if suboctaves else 1):
            t = int(2 ** (k + j / 8)) if j else 1 << k
            if start <= t <= target:
                result.add(t)
    return sorted(result)


def log_slope(points: list[tuple[float, float]]) -> float | None:
    if len(points) < 2 or any(t <= 0 or a <= 0 for t, a in points):
        return None
    xs, ys = zip(*[(math.log(t), math.log(a)) for t, a in points])
    mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
    den = sum((x - mx) ** 2 for x in xs)
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / den if den else None


def octave_fits(samples: list[dict], *, suboctaves: bool = False) -> list[dict]:
    """Only complete absolute octaves. Endpoint-only fits are labelled as such."""
    by_step = {s["steps"]: s for s in samples}
    fits = []
    for start in sorted(t for t in by_step if t > 0 and t & (t - 1) == 0):
        end = 2 * start
        if end not in by_step:
            continue
        times = sample_steps(end, start, suboctaves=suboctaves)
        if any(t not in by_step for t in times):
            continue
        rows = [by_step[t] for t in times]
        a, b = rows[0], rows[-1]
        births = b["area"] - a["area"]
        boundary = b["boundary_reads"] - a["boundary_reads"]
        defined = b["kappa_defined_steps"] - a["kappa_defined_steps"]
        fits.append({
            "start": start, "end": end, "samples": len(rows),
            "estimator": "ols_suboctave" if suboctaves else "endpoint_log_ratio",
            "alpha_A": log_slope([(r["steps"], r["area"]) for r in rows]),
            "alpha_W": log_slope([(r["steps"], r["width"]) for r in rows]),
            "width_geomean": math.sqrt(a["width"] * b["width"]),
            "births": births, "boundary_reads": boundary,
            "boundary_fraction": boundary / (end - start),
            "boundary_cost_per_birth": boundary / births if births else None,
            "births_per_boundary_read": births / boundary if boundary else None,
            "kappa": (b["kappa_sum"] - a["kappa_sum"]) / defined if defined else None,
        })
    return fits
