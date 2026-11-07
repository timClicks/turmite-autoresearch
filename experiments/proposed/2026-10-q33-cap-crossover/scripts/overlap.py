# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Regenerate inputs/overlap.tsv: pinned Q33 rules that also appear in prior study cohorts.

Inclusion criterion (explicit): a Q33 pilot/confirm rule is listed for a study iff that
exact rule string is a membership entry in the study's committed cohort file, under the
extractor named below. Word-substring matches inside prose or other rules do NOT count.
The blob census frame is omitted (every Q33 rule is in it by construction).

Known highway onsets (optional column) come only from committed onset tables named in
ONSET_SOURCES; missing onset is left blank. onset_lt_2_31 is "yes" when a known onset
is strictly below 2^31 (the Q33 main horizon), else "no" when onset is known, else blank.

Usage:
  uv run --offline --script .../scripts/overlap.py          # write if absent / match
  uv run --offline --script .../scripts/overlap.py --check  # compare only
"""
from __future__ import annotations

import argparse
import ast
import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
EXP = Path(__file__).resolve().parents[1]
HORIZON = 1 << 31

# study_id, relative source path, extractor name, short note
COHORTS: list[tuple[str, str, str, str]] = [
    ("wall-vs-memory-stage3b",
     "experiments/active/2026-10-wall-vs-memory/results/stage3b_specs.txt",
     "ft_specs", "wall-vs-memory Stages 3b (bounded fresh policies)"),
    ("wall-vs-memory-stage3c",
     "experiments/active/2026-10-wall-vs-memory/results/stage3c_specs.txt",
     "ft_specs", "wall-vs-memory Stages 3c"),
    ("crawler-cost-chaotic-edge",
     "experiments/archive/2026-10-crawler-cost-chaotic-edge/results/lists/cohorts.csv",
     "csv_rule", "crawler-cost-chaotic-edge mutant/parent cohorts"),
    ("kappa-exposure-classes",
     "experiments/archive/2026-10-kappa-exposure-classes/results/specs.txt",
     "lines_base", "kappa-exposure-classes 64-rule cohort"),
    ("kappa-rule-space-pool",
     "experiments/archive/2026-10-kappa-rule-space/results/rules_pool.csv",
     "csv_base", "kappa-rule-space rules_pool"),
    ("kappa-return-gates",
     "experiments/archive/2026-10-kappa-return-gates/results/cohort.csv",
     "csv_base", "kappa-return-gates cohort"),
    ("highways-unresolved-1e10",
     "experiments/archive/2026-10-highways-unresolved-rules-1e10-1e11/results/h1e10_stats.txt",
     "h1e10_highways", "highway onsets in (1e9, 1e10]"),
    ("late-highway-board-check",
     "experiments/archive/2026-10-late-highway-board-check/results/recheck",
     "recheck_dir", "late-highway board-check recheck CSVs"),
    ("b5-late-highways",
     "experiments/archive/2026-10-b5-late-highways/results/b5_stats_chunks20-60.txt",
     "b5_onsets", "B5 late highways (1e10, 1e11]"),
    ("square-ring-fillers-p6",
     "experiments/archive/2026-10-square-ring-fillers/results/p6_specs.txt",
     "lines", "square-ring-fillers P6 spec list"),
    ("highway-preconditions",
     "experiments/archive/2026-10-highway-preconditions/results/highway_specs.txt",
     "first_token", "highway-preconditions highway_specs"),
    ("highway-preconditions-control",
     "experiments/archive/2026-10-highway-preconditions/results/control_specs.txt",
     "first_token", "highway-preconditions control_specs"),
    ("c-law-mechanism-sample",
     "experiments/archive/2026-10-c-law-mechanism/results/lists/sample.txt",
     "lines", "c-law-mechanism sample list"),
    ("c-law-mechanism-band",
     "experiments/archive/2026-10-c-law-mechanism/results/lists/band.txt",
     "lines", "c-law-mechanism band list"),
]

ONSET_SOURCES: list[tuple[str, str]] = [
    ("experiments/archive/2026-10-highways-unresolved-rules-1e10-1e11/results/h1e10_stats.txt", "h1e10"),
    ("experiments/archive/2026-10-b5-late-highways/results/b5_stats_chunks20-60.txt", "b5"),
    ("experiments/archive/2026-10-late-highway-board-check/results/recheck", "recheck"),
    ("experiments/archive/2026-10-census-sweeps/results/confirmed_1B.csv", "confirmed_csv"),
    ("experiments/archive/2026-10-highway-preconditions/results/highway_specs.txt", "highway_specs"),
]


def _is_rule(s: str) -> bool:
    return bool(s) and set(s) <= set("LR") and len(s) >= 2


def _load_q33() -> dict[str, str]:
    out: dict[str, str] = {}
    for role, name in (("pilot", "specs_pilot.tsv"), ("confirm", "specs_confirm.tsv")):
        for line in (EXP / "inputs" / name).read_text().splitlines():
            if line.startswith("#") or not line.strip():
                continue
            rule = line.split("\t")[0]
            assert _is_rule(rule), rule
            out[rule] = role
    return out


def extract(path: Path, kind: str) -> set[str]:
    if kind == "lines":
        return {ln.strip() for ln in path.read_text().splitlines() if _is_rule(ln.strip())}
    if kind == "ft_specs":
        # lines like ft:RULE:R or fs:RULE:RLU:7 — take the rule field
        rules = set()
        for ln in path.read_text().splitlines():
            ln = ln.strip()
            if not ln or ln.startswith("#"):
                continue
            parts = ln.split(":")
            if len(parts) >= 2 and _is_rule(parts[1]):
                rules.add(parts[1])
        return rules
    if kind == "lines_base":
        rules = set()
        for ln in path.read_text().splitlines():
            base = ln.strip().split("@", 1)[0]
            if _is_rule(base):
                rules.add(base)
        return rules
    if kind == "first_token":
        rules = set()
        for ln in path.read_text().splitlines():
            ln = ln.strip()
            if not ln or ln.startswith("#"):
                continue
            tok = ln.split()[0]
            if _is_rule(tok):
                rules.add(tok)
        return rules
    if kind == "csv_rule":
        rules = set()
        with path.open(newline="") as fh:
            for row in csv.DictReader(fh):
                v = (row.get("rule") or "").strip().strip('"')
                if _is_rule(v):
                    rules.add(v)
        return rules
    if kind == "csv_base":
        rules = set()
        with path.open(newline="") as fh:
            reader = csv.DictReader(fh)
            key = "base" if "base" in (reader.fieldnames or []) else "rule"
            for row in reader:
                v = (row.get(key) or "").strip().strip('"').split("@", 1)[0]
                if _is_rule(v):
                    rules.add(v)
        return rules
    if kind == "h1e10_highways":
        text = path.read_text()
        m = re.search(r"highways found: (\[.*\])", text)
        if not m:
            raise ValueError(f"no highways found list in {path}")
        return {row[0] for row in ast.literal_eval(m.group(1)) if _is_rule(row[0])}
    if kind == "b5_onsets":
        rules = set()
        for ln in path.read_text().splitlines():
            m = re.match(r"\s+([LR]+)\s+onset\s+", ln)
            if m:
                rules.add(m.group(1))
        return rules
    if kind == "recheck_dir":
        rules = set()
        for csv_path in sorted(path.glob("*.csv")):
            with csv_path.open(newline="") as fh:
                for row in csv.DictReader(fh):
                    v = (row.get("rule") or "").strip()
                    if _is_rule(v):
                        rules.add(v)
        return rules
    raise ValueError(kind)


def load_onsets() -> dict[str, int]:
    """Earliest committed onset per rule (integer steps)."""
    onsets: dict[str, int] = {}

    def put(rule: str, onset: int) -> None:
        if not _is_rule(rule):
            return
        prev = onsets.get(rule)
        if prev is None or onset < prev:
            onsets[rule] = onset

    for rel, kind in ONSET_SOURCES:
        path = ROOT / rel
        if kind == "h1e10":
            text = path.read_text()
            m = re.search(r"highways found: (\[.*\])", text)
            for row in ast.literal_eval(m.group(1)):
                put(row[0], int(row[-1]))
        elif kind == "b5":
            for ln in path.read_text().splitlines():
                m = re.match(r"\s+([LR]+)\s+onset\s+([0-9.eE+]+)\s+", ln)
                if m:
                    put(m.group(1), int(float(m.group(2))))
        elif kind == "recheck":
            for csv_path in sorted(path.glob("*.csv")):
                with csv_path.open(newline="") as fh:
                    for row in csv.DictReader(fh):
                        if row.get("onset"):
                            put(row["rule"].strip(), int(float(row["onset"])))
        elif kind == "confirmed_csv":
            with path.open(newline="") as fh:
                for row in csv.DictReader(fh):
                    if (row.get("confirmed") or "").strip().lower() != "true":
                        continue
                    if not row.get("onset"):
                        continue
                    put(row["rule"].strip(), int(float(row["onset"])))
        elif kind == "highway_specs":
            for ln in path.read_text().splitlines():
                ln = ln.strip()
                if not ln or ln.startswith("#"):
                    continue
                parts = ln.split()
                if len(parts) >= 5 and _is_rule(parts[0]):
                    put(parts[0], int(float(parts[4])))
    return onsets


HEADER = (
    "# rule\trole\tstudy_id\tsource_path\tknown_onset\tonset_lt_2_31\tnote\n"
    "# Overlap of pinned Q33 pilot/confirm rules with previously *studied* experiment cohorts.\n"
    "# Exact membership only (see scripts/overlap.py COHORTS extractors); no prose substring matches.\n"
    "# The sampling frame itself (probe_summary.csv blob class) is not listed: every rule is in it by construction.\n"
    "# Inclusion is retained (README sampling rule); this record is for interpretation, not exclusion.\n"
    "# known_onset / onset_lt_2_31 come from ONSET_SOURCES in overlap.py (blank if unknown).\n"
)


def build_text() -> str:
    q33 = _load_q33()
    onsets = load_onsets()
    rows: list[tuple[str, str, str, str, str, str, str]] = []
    for study_id, rel, kind, note in COHORTS:
        path = ROOT / rel
        members = extract(path, kind)
        for rule in sorted(q33):
            if rule not in members:
                continue
            onset = onsets.get(rule)
            onset_s = "" if onset is None else str(onset)
            flag = "" if onset is None else ("yes" if onset < HORIZON else "no")
            rows.append((rule, q33[rule], study_id, rel, onset_s, flag, note))
    # Stable order: role (pilot first), rule, study_id
    role_rank = {"pilot": 0, "confirm": 1}
    rows.sort(key=lambda r: (role_rank[r[1]], r[0], r[2]))
    body = "".join("\t".join(r) + "\n" for r in rows)
    return HEADER + body


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true", help="compare with committed file; write nothing")
    ap.add_argument("--summary", action="store_true", help="print overlap counts to stdout")
    args = ap.parse_args()
    text = build_text()
    target = EXP / "inputs" / "overlap.tsv"
    data_rows = [ln for ln in text.splitlines() if ln and not ln.startswith("#")]
    pilots = {r.split("\t")[0] for r in data_rows if r.split("\t")[1] == "pilot"}
    confirms = {r.split("\t")[0] for r in data_rows if r.split("\t")[1] == "confirm"}
    in_horizon = {r.split("\t")[0] for r in data_rows if r.split("\t")[5] == "yes"}
    if args.summary or args.check:
        print(f"rows={len(data_rows)} pilot_distinct={len(pilots)}/8 "
              f"confirm_distinct={len(confirms)}/200 distinct={len(pilots|confirms)} "
              f"onset_lt_2_31_distinct={len(in_horizon)}")
    if args.check or target.exists():
        same = target.exists() and target.read_text() == text
        print(f"overlap.tsv: {'OK' if same else 'DIFFERS'}")
        if args.check:
            return 0 if same else 1
        if not same:
            target.write_text(text)
            print("overlap.tsv: rewritten")
        return 0
    target.parent.mkdir(exist_ok=True)
    target.write_text(text)
    print("overlap.tsv: written")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
