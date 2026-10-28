"""Materialise the research atlas: topic pages assembled from existing records.

blog/atlas.json only curates (which experiment bears on which question, in what
role, what changed). Findings, caveats and claim text are copied from the
reader guides and the evidence ledger, so nothing is recorded here that is not
recorded, with provenance, elsewhere. Validation fails the build when the view
and the record disagree.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BLOG = ROOT / "blog"
SOURCE = BLOG / "atlas.json"
GUIDES = BLOG / "experiment-guides.tsv"
CLAIMS = ROOT / "experiments/archive/2026-10-evidence-ledger/results/claims.json"
OUTPUT = BLOG / "atlas"
DATA = BLOG / "_data" / "atlas.json"
MARKER = ".generated-by-turmite-blog"

# Guardrail, not proof: curated prose may not carry measurements. Decimals,
# percentages and exponent notation must come from a linked record instead.
MEASUREMENT = re.compile(r"\d\s*%|\b\d+\.\d+\b|\b\d+(?:\.\d+)?e[+-]?\d+\b|10\^|\bp\s*[<=]|±")
ROLE_TEXT_FIELDS = ("question", "state_summary")


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def slug_date(slug: str) -> str:
    m = re.match(r"(\d{4}-\d{2})(?:-(\d{2}))?-", slug)
    if not m:
        raise ValueError(f"Experiment folder without a date prefix: {slug}")
    return f"{m.group(1)}-{m.group(2) or '00'}"


def post_meta(name: str) -> dict:
    text = (BLOG / "_posts" / name).read_text(encoding="utf-8")
    m = re.search(r"^title:\s*(.+)$", text, re.M)
    title = m.group(1).strip().strip('"').strip("'") if m else name
    y, mo, d, rest = re.match(r"(\d{4})-(\d{2})-(\d{2})-(.+)\.md$", name).groups()
    return {"date": f"{y}-{mo}-{d}", "title": title, "url": f"/{y}/{mo}/{d}/{rest}/"}


def load_inputs(source: Path = SOURCE) -> dict:
    tracked = set(git("ls-files").splitlines())
    experiments = {Path(p).parent.name for p in tracked
                   if re.fullmatch(r"experiments/[^_/][^/]*/README\.md", p)}
    guides = {}
    with GUIDES.open(encoding="utf-8") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            guides[row["slug"]] = row
    claims = {c["id"]: c for c in json.loads(CLAIMS.read_text())["claims"]}
    claim_doc = json.loads(CLAIMS.read_text())
    return {"atlas": json.loads(source.read_text()), "tracked": tracked, "experiments": experiments,
            "guides": guides, "claims": claims, "claim_sources": claim_doc["sources"]}


def validate(inp: dict) -> list[str]:
    atlas, errors = inp["atlas"], []
    states, topics = atlas["states"], atlas["topics"]
    seen_slugs = set()
    filed: set[str] = set()
    for t in topics:
        where = f"topic {t.get('slug')}"
        if t["slug"] in seen_slugs:
            errors.append(f"{where}: duplicate slug")
        seen_slugs.add(t["slug"])
        if t["state"] not in states:
            errors.append(f"{where}: unknown state {t['state']!r}")
        if not t["evidence"]:
            errors.append(f"{where}: no evidence listed")
        for field in ROLE_TEXT_FIELDS:
            if MEASUREMENT.search(t[field]):
                errors.append(f"{where}: {field} carries a measurement; link the record instead")
        for cid in t["claims"]:
            if cid not in inp["claims"]:
                errors.append(f"{where}: unknown claim {cid}")
        refs = [("evidence", i) for i in t["evidence"]] + [("counter", i) for i in t["counter"]]
        for role, item in refs:
            ref = item["ref"]
            if ref.startswith("file:"):
                if ref[5:] not in inp["tracked"]:
                    errors.append(f"{where}: {role} file not tracked: {ref[5:]}")
                if not item.get("why"):
                    errors.append(f"{where}: file reference {ref} needs a why")
            elif ref not in inp["experiments"]:
                errors.append(f"{where}: {role} refers to unknown experiment {ref}")
            else:
                filed.add(ref)
            if MEASUREMENT.search(item.get("why", "")):
                errors.append(f"{where}: why for {ref} carries a measurement")
        for ref in t["also"]:
            if ref not in inp["experiments"]:
                errors.append(f"{where}: also refers to unknown experiment {ref}")
            filed.add(ref)
        for name in t["posts"]:
            if not (BLOG / "_posts" / name).is_file():
                errors.append(f"{where}: unknown post {name}")
        for o in t["open"]:
            if o.get("source") and o["source"] not in inp["tracked"]:
                errors.append(f"{where}: open-question source not tracked: {o['source']}")
            if MEASUREMENT.search(o["text"]):
                errors.append(f"{where}: open question carries a measurement")
        members = {i["ref"] for _, i in refs} | set(t["also"])
        for turn in t["turns"]:
            if turn["ref"] not in members:
                errors.append(f"{where}: turning point {turn['ref']} is not filed under the topic")
            if MEASUREMENT.search(turn["change"]) or len(turn["change"]) > 140:
                errors.append(f"{where}: turning point text for {turn['ref']} is too long or carries a measurement")
    for ref, reason in atlas["unfiled"].items():
        if ref not in inp["experiments"]:
            errors.append(f"unfiled refers to unknown experiment {ref}")
        if not reason.strip():
            errors.append(f"unfiled {ref} needs a reason")
    missing = inp["experiments"] - filed - set(atlas["unfiled"])
    if missing:
        errors.append("Experiments neither filed nor listed under unfiled: " + ", ".join(sorted(missing)))
    if set(inp["guides"]) != inp["experiments"]:
        errors.append("Reader guides and tracked experiments differ")
    return errors


def materialise(inp: dict, revision: str) -> dict:
    atlas, guides = inp["atlas"], inp["guides"]

    def exp_entry(slug: str) -> dict:
        g = guides[slug]
        return {"kind": "experiment", "slug": slug, "date": slug_date(slug), "title": g["title"],
                "url": f"/experiments/{slug}/", "finding": g["finding"], "caveat": g["caveat"],
                "evidence_path": g["evidence"]}

    out = []
    for t in atlas["topics"]:
        def items(lst):
            res = []
            for i in lst:
                if i["ref"].startswith("file:"):
                    res.append({"kind": "file", "path": i["ref"][5:], "why": i["why"],
                                "title": i["ref"][5:].rsplit("/", 1)[-1]})
                else:
                    e = exp_entry(i["ref"])
                    e["why"] = i.get("why", "")
                    res.append(e)
            return res

        evidence, counter = items(t["evidence"]), items(t["counter"])
        turns = {x["ref"]: x["change"] for x in t["turns"]}
        roles = {i["ref"]: "evidence" for i in t["evidence"]}
        roles.update({i["ref"]: "counter" for i in t["counter"]})
        members = list(dict.fromkeys([i["ref"] for i in t["evidence"] + t["counter"]
                                      if not i["ref"].startswith("file:")] + t["also"]))
        chron = []
        for slug in members:
            e = exp_entry(slug)
            chron.append({"kind": "experiment", "date": e["date"], "title": e["title"], "url": e["url"],
                          "role": roles.get(slug, "context"), "turn": turns.get(slug, "")})
        for name in t["posts"]:
            p = post_meta(name)
            chron.append({"kind": "post", "date": p["date"], "title": p["title"], "url": p["url"],
                          "role": "post", "turn": ""})
        chron.sort(key=lambda c: (c["date"], c["title"]))
        newest = max(slug_date(s) for s in members)
        since = [c for c in chron if c["kind"] == "experiment" and c["date"] > t["reviewed"]]
        claims = []
        for cid in t["claims"]:
            c = inp["claims"][cid]
            claims.append({**{k: c[k] for k in ("id", "kind", "verdict", "observation", "failed_explanation",
                                                 "question", "next_decision", "scope", "limitations")},
                           "sources": [inp["claim_sources"][s] for s in c["sources"]]})
        out.append({
            "slug": t["slug"], "question": t["question"], "state": t["state"],
            "state_label": atlas["states"][t["state"]]["label"],
            "state_meaning": atlas["states"][t["state"]]["meaning"],
            "state_summary": t["state_summary"], "reviewed": t["reviewed"],
            "newest_evidence": newest, "experiment_count": len(members),
            "newer_than_review": since, "claims": claims, "evidence": evidence, "counter": counter,
            "open": t["open"], "chronology": chron, "turns": [c for c in chron if c["turn"]],
            "claim_questions": [c["question"] for c in claims if c["verdict"] != "supported"],
        })
    return {"revision": revision, "inputs": {
                p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in (SOURCE, GUIDES, CLAIMS)},
            "states": atlas["states"], "topics": out}


def write(view: dict) -> None:
    assert OUTPUT.resolve() == ROOT.resolve() / "blog" / "atlas"
    if OUTPUT.exists():
        if not (OUTPUT / MARKER).is_file():
            raise RuntimeError(f"Refusing to replace an unmarked directory: {OUTPUT}")
        shutil.rmtree(OUTPUT)
    OUTPUT.mkdir()
    (OUTPUT / MARKER).touch()
    DATA.write_text(json.dumps(view, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    for t in view["topics"]:
        folder = OUTPUT / t["slug"]
        folder.mkdir()
        question = t["question"].replace('"', '\\"')
        (folder / "index.md").write_text(
            f'---\nlayout: atlas-topic\ntitle: "{question}"\ndescription: "{t["state_label"]}. '
            f'{t["state_summary"].replace(chr(34), chr(39))}"\npermalink: /atlas/{t["slug"]}/\n'
            f'topic: {t["slug"]}\n---\n', encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="validate only; write nothing")
    args = parser.parse_args()
    inp = load_inputs()
    errors = validate(inp)
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    if not args.check:
        write(materialise(inp, git("rev-parse", "HEAD")))
        print(f"Atlas: {len(inp['atlas']['topics'])} topics, {len(inp['experiments'])} experiments covered.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
