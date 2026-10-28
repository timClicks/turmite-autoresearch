"""Law-group census for all rules of length 2..8 (predictions P1, P3, P4, P6, P7).

  uv run --no-project experiments/archive/2026-10-invariant-mining-snf/scripts/census.py [--nmax 8]

Writes results/fingerprints.csv, results/universal.csv, results/by_counts.csv, results/p4.csv and
results/census_provenance.json.  Exact algebra: no randomness, no seeds, no step counts.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import itertools
import json
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "experiments" / "_lib"))
import lawmod as lm  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "results"


def all_rules(n: int):
    for bits in itertools.product("RL", repeat=n):
        yield "".join(bits)


def sub_order(M, cols, k, m):
    """Order of {u mod m : M u = 0, u zero outside `cols`} (kernel of the column-restricted matrix)."""
    keep = [[row[c] for c in cols] for row in M]
    return lm.snf(keep, len(cols)).order(m)


def faithful_heading(M, cols, m):
    """Post hoc refinement of P4: a law with a = b = e = 0 whose Phi(1) is odd (pins h mod 4, not just parity).
    cols[0] must be the Phi(1) column; some generator has an odd entry there iff the group has such a law."""
    keep = [[row[c] for c in cols] for row in M]
    return int(any(g[0] % 2 for g in lm.snf(keep, len(cols)).generators(m)))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def provenance(cmd: list[str], extra: dict) -> dict:
    git = lambda *a: subprocess.run(["git", *a], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    return {
        "command": " ".join(cmd),
        "git_head": git("rev-parse", "HEAD"),
        "git_dirty_paths": [l for l in git("status", "--short").splitlines() if "invariant-mining-snf" in l or "lawmod" in l],
        "python": sys.version.split()[0],
        "lawmod_sha256": sha(ROOT / "experiments" / "_lib" / "lawmod.py"),
        "script_sha256": sha(Path(__file__)),
        **extra,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--nmax", type=int, default=8)
    args = ap.parse_args()
    OUT.mkdir(exist_ok=True)

    fp_rows = []  # per rule x family
    uni = {}  # (family, n) -> Snf
    p4_rows = []
    for fname in lm.FAMILIES:
        fam = lm.Family(fname)
        for n in range(2, args.nmax + 1):
            k = lm.Layout(fam, n).size()
            uni[(fname, n)] = lm.snf(lm.universal_rows(fam, n), k)
            for rule in all_rules(n):
                M = lm.rule_rows(fam, rule)
                sn = lm.snf(M, k)
                free, facs = sn.fingerprint()
                fp_rows.append({
                    "rule": rule, "n": n, "nR": rule.count("R"), "family": fname, "free": free,
                    "factors": " ".join(map(str, facs)),
                    **{f"order_m{m}": sn.order(m) for m in (2, 3, 4, 8)},
                    "order_mn": sn.order(n), "order_m2n": sn.order(2 * n), "order_m4n": sn.order(4 * n),
                })
                if fname == "F1":
                    cols_phi_w = list(range(3, k))
                    cols_w = list(range(3 + len(fam.phi_keys()), k))
                    # law with a = b = e = 0 and Phi not identically zero, mod 4
                    has_pure = sub_order(M, cols_phi_w, k, 4) > sub_order(M, cols_w, k, 4)
                    D = (rule.count("R") - rule.count("L")) % 4
                    p4_rows.append({"rule": rule, "n": n, "D_mod4": D, "pure_tape_heading_law": int(has_pure),
                                    "predicted": int(D == 0),
                                    "posthoc_faithful_law": faithful_heading(M, cols_phi_w, 4)})
        print("done family", fname, file=sys.stderr)

    with open(OUT / "fingerprints.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(fp_rows[0]))
        w.writeheader()
        w.writerows(fp_rows)
    with open(OUT / "p4.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(p4_rows[0]))
        w.writeheader()
        w.writerows(p4_rows)

    # P1: fingerprint is a function of (family, n, nR)
    by_counts = defaultdict(set)
    for r in fp_rows:
        by_counts[(r["family"], r["n"], r["nR"])].add((r["free"], r["factors"]))
    exceptions = {k: sorted(v) for k, v in by_counts.items() if len(v) > 1}
    with open(OUT / "by_counts.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["family", "n", "nR", "n_distinct_fingerprints", "free", "factors"])
        for (fam, n, nr), v in sorted(by_counts.items()):
            for free, facs in sorted(v):
                w.writerow([fam, n, nr, len(v), free, facs])

    # Universal groups
    with open(OUT / "universal.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["family", "n", "free", "factors", "m", "order"])
        for (fam, n), sn in sorted(uni.items()):
            free, facs = sn.fingerprint()
            for m in sorted({2, 3, 4, 5, 6, 7, 8, n, 2 * n, 4 * n}):
                w.writerow([fam, n, free, " ".join(map(str, facs)), m, sn.order(m)])

    # Summaries for the README
    p1 = {"rules_checked_per_family": sum(1 for r in fp_rows if r["family"] == "F1"),
          "exceptions": {f"{k[0]} n={k[1]} nR={k[2]}": v for k, v in exceptions.items()}}
    p4_bad = [r for r in p4_rows if r["pure_tape_heading_law"] != r["predicted"]]
    p4_bad_posthoc = [r for r in p4_rows if r["posthoc_faithful_law"] != r["predicted"]]
    prov = provenance(sys.argv, {"nmax": args.nmax, "P1": p1, "P4_mismatches": len(p4_bad), "P4_mismatch_D_values": sorted({r["D_mod4"] for r in p4_bad}),
                                 "P4_posthoc_mismatches": [r["rule"] for r in p4_bad_posthoc],
                                 "P4_rules": len(p4_rows)})
    (OUT / "census_provenance.json").write_text(json.dumps(prov, indent=1))
    print(json.dumps({"P1_exceptions": len(exceptions), "P4_mismatches": len(p4_bad), "P4_posthoc_mismatches": len(p4_bad_posthoc)}))


if __name__ == "__main__":
    main()
