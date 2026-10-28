"""Prediction P2: the SNF solver (family A0) versus src/bin/invariants.rs (the parallel enumerative miner).

  uv run --no-project experiments/archive/2026-10-invariant-mining-snf/scripts/cross_check_peer.py --exe PATH/TO/invariants[.exe]

For every rule of length 2..8 and m in {2, 4}: (number of lines `invariants RULE` prints for m) + 1 must equal
the size of the A0 solution set from the Smith normal form.  The peer code was uncommitted when this ran,
so the sha256 of src/invariants.rs and src/bin/invariants.rs is recorded with the result.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "experiments" / "_lib"))
import lawmod as lm  # noqa: E402

EXP = Path(__file__).resolve().parents[1]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--exe", required=True)
    ap.add_argument("--nmax", type=int, default=8)
    args = ap.parse_args()
    rules = ["".join(b) for n in range(2, args.nmax + 1) for b in itertools.product("RL", repeat=n)]
    out = subprocess.run([args.exe, *rules], capture_output=True, text=True, check=True).stdout.splitlines()[1:]
    peer = Counter()
    for l in out:
        rule, m, *_ = l.split(",")
        peer[(rule, int(m))] += 1
    fam = lm.Family("A0")
    bad = []
    for rule in rules:
        n = len(rule)
        sn = lm.snf(lm.rule_rows(fam, rule), lm.Layout(fam, n).size())
        for m in (2, 4):
            if peer[(rule, m)] + 1 != sn.order(m):
                bad.append({"rule": rule, "m": m, "peer_nonzero_laws": peer[(rule, m)], "snf_order": sn.order(m)})
    sha = lambda p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest()
    res = {
        "command": " ".join(sys.argv), "rules": len(rules), "comparisons": 2 * len(rules), "mismatches": len(bad),
        "examples": bad[:10],
        "peer_src_sha256": {p: sha(p) for p in ("src/invariants.rs", "src/bin/invariants.rs")},
        "peer_files_committed": subprocess.run(["git", "ls-files", "src/invariants.rs"], cwd=ROOT, capture_output=True, text=True).stdout.strip() != "",
        "git_head": subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip(),
    }
    (EXP / "results" / "crosscheck_peer.json").write_text(json.dumps(res, indent=1))
    print(json.dumps({k: res[k] for k in ("rules", "comparisons", "mismatches", "peer_files_committed")}))


if __name__ == "__main__":
    main()
