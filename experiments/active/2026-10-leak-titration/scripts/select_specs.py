"""Write the leak-titration run specs (no random draw: rules and seeds are the committed Stage 1 ones).

usage (repo root): uv run --frozen python experiments/active/2026-10-leak-titration/scripts/select_specs.py
Writes results/specs.txt (one probe spec per line) and results/spec_roles.csv (spec -> arm, EF, role).

Leak = probability EF that the turn on a never-departed cell is replaced by R or L with probability 1/2 each
(the wall-vs-memory `HybridWalker`, EV = 0). The fresh turn is therefore R with probability 1 - EF/2 and L with
EF/2 on the base-R arm. The base-L arm is its mirror image on fresh ground only: L with 1 - EF/2, R with EF/2.
It is run through `FreshSetWalker` (`fs:`), which draws the fresh turn uniformly from a letter set, so a 20-letter
set with k = 10 EF letters of the minority turn gives minority probability k/20 = EF/2 exactly
(index = floor(high32 * 20 / 2^32), 20 equal slots). Order of letters in the set is irrelevant.

Roles: `new` (scored), `gate_hy` (hybrid rows that must equal the committed Stage 1 rows), `gate_ft` (EF = 0 forced L,
must equal the committed Stage 3 rows), `gate_law` (base-R arm through the `fs:` encoding, compared to `hy:` in law).
"""
from pathlib import Path

EXP = Path(__file__).resolve().parents[1]
WVM = EXP.parent / "2026-10-wall-vs-memory" / "results"
RULES = sorted((WVM / "rules.txt").read_text().split())
SEEDS = range(2026102601, 2026102609)
GRID = [round(0.1 * i, 1) for i in range(1, 11)]  # 0.1 .. 1.0


def fmt(ef: float) -> str:
    """EF as the committed Stage 1 labels write it: '1' for 1.0, '0.1' for 0.1 (rows must match byte for byte)."""
    return "1" if ef == 1.0 else str(ef)


def minority_set(base: str, ef: float) -> str:
    k = round(10 * ef)
    other = "L" if base == "R" else "R"
    return base * (20 - k) + other * k


rows: list[tuple[str, str, str, str]] = []  # spec, arm, ef, role
# arm R: hybrid walker. EF = 0 is the deterministic ant (one run, seed irrelevant), as committed in Stage 1.
for r in RULES:
    rows.append((f"hy:{r}:0:0:0", "R", "0", "gate_hy"))
for ef in GRID:
    for r in RULES:
        for s in SEEDS:
            role = "gate_hy" if ef in (0.1, 1.0) else "new"
            rows.append((f"hy:{r}:0:{fmt(ef)}:{s}", "R", fmt(ef), role))
# arm L: forced L at EF = 0 (Stage 3 rows), then the 20-slot encoding of base L with minority R.
for r in RULES:
    rows.append((f"ft:{r}:L", "L", "0", "gate_ft"))
for ef in GRID:
    for r in RULES:
        for s in SEEDS:
            rows.append((f"fs:{r}:{minority_set('L', ef)}:{s}", "L", fmt(ef), "new"))
# law-equivalence gate: base R through the same fs: encoding as arm L, at EF = 0.5 and 0.8.
for ef in (0.5, 0.8):
    for r in RULES:
        for s in SEEDS:
            rows.append((f"fs:{r}:{minority_set('R', ef)}:{s}", "Rfs", fmt(ef), "gate_law"))

specs = [r[0] for r in rows]
assert len(specs) == len(set(specs)), "duplicate specs"
(EXP / "results/specs.txt").write_text("\n".join(specs) + "\n")
(EXP / "results/spec_roles.csv").write_text("spec,arm,ef,role\n" + "\n".join(",".join(r) for r in rows) + "\n")
by_role: dict[str, int] = {}
for r in rows:
    by_role[r[3]] = by_role.get(r[3], 0) + 1
print(len(specs), "specs", by_role)
