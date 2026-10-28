"""Prepare only a deterministic prospective design; never run or score ants."""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
from pathlib import Path
import random

ROOT = Path(__file__).resolve().parents[4]
EXP = Path(__file__).resolve().parents[1]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def necklace(rule: str) -> str:
    mirror = rule.translate(str.maketrans("RL", "LR"))
    return min(r[i:] + r[:i] for r in (rule, mirror) for i in range(len(r)))


def primitive(rule: str) -> bool:
    return all(rule != rule[:k] * (len(rule) // k)
               for k in range(1, len(rule)) if len(rule) % k == 0)


def swapped(rule: str, indices: list[int], rng: random.Random):
    choices = [(i, j) for i in indices for j in indices
               if i < j and rule[i] != rule[j]]
    if not choices:
        return None
    i, j = rng.choice(choices)
    letters = list(rule)
    letters[i], letters[j] = letters[j], letters[i]
    return "".join(letters), f"{i},{j}"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="verify saved design without writing")
    args = parser.parse_args()
    config_path = EXP / "design.json"
    config = json.loads(config_path.read_text())
    inputs = [config_path, Path(__file__).resolve()]
    seen = set()
    for name in config["exclusion_lists"]:
        path = ROOT / name
        inputs.append(path)
        for line in path.read_text().splitlines():
            rule = line.strip()
            if not rule or set(rule) - set("RL"):
                raise ValueError(f"unexpected rule in {name}: {line!r}")
            seen.add(necklace(rule))

    rng = random.Random(config["sampling_seed"])
    rows = []
    for split, count in config["families_per_lead"].items():
        for lead in config["leads"]:
            for family in range(count):
                for attempt in range(100000):
                    n = config["rule_length"]
                    rule = "R" * lead + "L" + "".join(rng.choice("RL") for _ in range(n - lead - 1))
                    early = swapped(rule, config["early_indices"], rng)
                    late = swapped(rule, config["late_indices"], rng)
                    if early is None or late is None:
                        continue
                    arms = [("base", rule, ""), ("early_swap", *early), ("late_swap", *late)]
                    keys = [necklace(r) for _, r, _ in arms]
                    if len(set(keys)) != 3 or any(k in seen for k in keys):
                        continue
                    if not all(primitive(r) for _, r, _ in arms):
                        continue
                    if any(len(r) - len(r.lstrip("R")) != lead for _, r, _ in arms):
                        continue
                    seen.update(keys)
                    seeds = config["pilot_seeds" if split == "pilot" else "main_seeds"]
                    for arm, r, positions in arms:
                        assert len(r) == n and r.count("R") == rule.count("R")
                        assert len(r) - len(r.lstrip("R")) == lead
                        rows.append([f"{split}-m{lead}-{family:02}", split, lead, arm,
                                     r, positions, ";".join(map(str, seeds))])
                    break
                else:
                    raise RuntimeError(f"could not fill {split}, lead {lead}, family {family}")

    output = io.StringIO(newline="")
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow(["family", "split", "lead", "arm", "rule", "swap_indices", "interior_seeds"])
    writer.writerows(rows)
    payload = output.getvalue().encode()
    provenance = {
        "status": "design_only_no_measurements",
        "base_revision": config["base_revision"],
        "command": "uv run --frozen experiments/active/2026-10-c-law-renewal/scripts/prepare.py",
        "environment": "WSL; UV_PROJECT_ENVIRONMENT=$HOME/.venvs/turmite UV_LINK_MODE=copy; Python >=3.12",
        "sampling_seed": config["sampling_seed"],
        "inputs_sha256": {p.relative_to(ROOT).as_posix(): digest(p) for p in inputs},
        "families": len(rows) // 3,
        "rules": len(rows),
        "manifest_sha256": hashlib.sha256(payload).hexdigest(),
    }
    files = {"families.csv": payload,
             "provenance.json": (json.dumps(provenance, indent=2) + "\n").encode()}
    destination = EXP / "results" / "design"
    # Preflight every file before writing any, so partial conflicts cannot mutate the design.
    for name, data in files.items():
        path = destination / name
        if path.exists() and path.read_bytes() != data:
            raise RuntimeError(f"refusing different existing design: {path}; register a new version")
        if args.check and not path.exists():
            raise RuntimeError(f"missing saved design: {path}")
    if not args.check:
        destination.mkdir(parents=True, exist_ok=True)
        for name, data in files.items():
            path = destination / name
            if not path.exists():
                path.write_bytes(data)
    print(f"{'Verified' if args.check else 'Prepared'} {len(rows) // 3} families; design only, no measurements.")


if __name__ == "__main__":
    main()
