# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Pin the Q33 sampling frame and the excluded-pilot / confirmation rule lists.

Implements the README rule exactly: frame = rows of the probe-growth census summary
with cls == "blob"; rank by SHA-256 of UTF-8 "Q33-20261029-cohort:" + rule (ties by
rule); first 8 = excluded pilot, next 200 = confirmation. Also writes each rule's main
seed (first 8 bytes, big-endian, of SHA-256("Q33-20261029-main:" + rule)).
Reads committed data only; writes into inputs/. Refuses to overwrite differing files
unless --check is used to compare.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
EXP = Path(__file__).resolve().parents[1]
FRAME = ROOT / "experiments/archive/2026-10-probe-growth-census/results/probe_summary.csv"


def sha(s: str) -> bytes:
    return hashlib.sha256(s.encode("utf-8")).digest()


def build() -> dict[str, str]:
    raw = FRAME.read_bytes()
    rows = list(csv.DictReader(raw.decode("utf-8").splitlines()))
    blob = [r["rule"] for r in rows if r["cls"] == "blob"]
    assert len(blob) == 2630, len(blob)
    assert len(set(blob)) == 2630, "duplicate rules in frame"
    ranked = sorted(blob, key=lambda r: (sha("Q33-20261029-cohort:" + r).hex(), r))
    pilot, confirm = ranked[:8], ranked[8:208]
    def seed(r: str) -> int:
        return int.from_bytes(sha("Q33-20261029-main:" + r)[:8], "big")
    def listing(rs):
        return "".join(f"{r}\t{seed(r)}\n" for r in rs)
    frame_line = (f"{hashlib.sha256(raw).hexdigest()}  "
                  f"{FRAME.relative_to(ROOT)}\nrows={len(rows)} blob_rows={len(blob)} blob_unique={len(set(blob))}\n")
    return {
        "frame.sha256": frame_line,
        "specs_pilot.tsv": "# rule\tmain_seed (excluded pilot; ranks 1-8)\n" + listing(pilot),
        "specs_confirm.tsv": "# rule\tmain_seed (confirmation; ranks 9-208)\n" + listing(confirm),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true", help="compare with committed files; write nothing")
    args = ap.parse_args()
    bad = 0
    for name, text in build().items():
        p = EXP / "inputs" / name
        if args.check or p.exists():
            same = p.exists() and p.read_text() == text
            print(f"{name}: {'OK' if same else 'DIFFERS'}")
            bad += not same
        else:
            p.parent.mkdir(exist_ok=True)
            p.write_text(text)
            print(f"{name}: written")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
