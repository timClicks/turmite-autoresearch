"""Read the editorial catalogue; no dependencies beyond Python 3.12 stdlib."""

import argparse
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
EXPERIMENT = Path(__file__).resolve().parents[1]
CATALOGUE = EXPERIMENT / "results/claims.json"
REPO_URL = "https://github.com/timClicks/turmite-autoresearch"
TOPICS = {"boundary-occupation", "return-dynamics", "regime-changes"}
KINDS = {"identity", "calibration", "prediction", "instrument", "intervention", "observation"}
VERDICTS = {"accounting-only", "supported", "failed", "mixed", "uninformative", "unresolved"}
TEXT_FIELDS = ("observation", "failed_explanation", "question", "next_decision", "scope", "limitations")


def validate(data):
    if data.get("schema_version") != 1:
        raise ValueError("unsupported schema_version")
    revision = data["source_revision"]
    if not re.fullmatch(r"[0-9a-f]{40}", revision):
        raise ValueError("source_revision must be a full Git hash")
    ids = set()
    for claim in data["claims"]:
        cid = claim["id"]
        if not re.fullmatch(r"(?:BO|RD|RG)-[0-9]{2}", cid) or cid in ids:
            raise ValueError(f"invalid or duplicate claim ID: {cid}")
        ids.add(cid)
        for field, allowed in (("topic", TOPICS), ("kind", KINDS), ("verdict", VERDICTS)):
            if claim[field] not in allowed:
                raise ValueError(f"{cid}: invalid {field}")
        for field in TEXT_FIELDS:
            if not isinstance(claim[field], str) or not claim[field].strip():
                raise ValueError(f"{cid}: missing {field}")
        if not claim["sources"] or any(s not in data["sources"] for s in claim["sources"]):
            raise ValueError(f"{cid}: unknown or missing source")
    for key, path in data["sources"].items():
        if not isinstance(path, str) or "\\" in path or path.startswith("/") or ".." in path.split("/"):
            raise ValueError(f"invalid source path: {key}")
        subprocess.run(["git", "cat-file", "-e", f"{revision}:{path}"], cwd=ROOT, check=True, capture_output=True)


def source_url(data, key):
    return f"{REPO_URL}/blob/{data['source_revision']}/{data['sources'][key]}"


def query(data, topic=None, verdict=None, text=None):
    return [c for c in data["claims"]
            if (topic is None or c["topic"] == topic)
            and (verdict is None or c["verdict"] == verdict)
            and (text is None or text.casefold() in json.dumps(c, ensure_ascii=False).casefold())]


def render(data):
    def cell(value):
        return value.replace("|", "\\|").replace("\n", " ")

    lines = ["# Claim ledger: boundary access and regime changes", "",
             "Generated from human-authored `claims.json` by `scripts/ledger.py render`.",
             f"Reviewed {data['reviewed_at']}; all evidence pinned at `{data['source_revision']}`.",
             "No new measurements. Verdicts apply to the stated test and scope, not entire mechanisms.", "",
             "## Compact decision view", "",
             "| ID / verdict | Supported observation or test outcome | Failed explanation / inference | Unresolved question | Next decision |",
             "|---|---|---|---|---|"]
    for c in data["claims"]:
        lines.append("| " + " | ".join(cell(v) for v in (
            f"[{c['id']}](#{c['id'].lower()}) / {c['verdict']}", c["observation"],
            c["failed_explanation"], c["question"], c["next_decision"])) + " |")
    lines += ["", "## Scope and evidence", "",
              "Always retrieve these limits with the compact row. Source READMEs/notes include",
              "recipes, manifests and corrections; linked data are retained measurements, not reruns."]
    for c in data["claims"]:
        lines += ["", f"### {c['id']}", "", f"**{c['topic']} · {c['kind']} · {c['verdict']}**", "",
                  f"Scope: {c['scope']}", "", f"Limits: {c['limitations']}", "",
                  "Evidence: " + "; ".join(f"[{s}]({source_url(data, s)})" for s in c["sources"]) + "."]
    return "\n".join(lines) + "\n"


def atom(value):
    # Quoted ISO-style atoms; double embedded apostrophes, escape backslashes.
    return "'" + value.replace("\\", "\\\\").replace("'", "''").replace("\n", " ") + "'"


def facts(data):
    yield "% Catalogue assertions, not scientific truth or automatic pruning permission."
    yield f"snapshot({atom(data['source_revision'])}, {atom(data['reviewed_at'])})."
    for key, path in data["sources"].items():
        yield f"source({atom(key)}, {atom(data['source_revision'])}, {atom(path)})."
    for c in data["claims"]:
        yield "claim(" + ", ".join(atom(c[k]) for k in ("id", "topic", "kind", "verdict")) + ")."
        for field in TEXT_FIELDS:
            yield f"{field}({atom(c['id'])}, {atom(c[field])})."
        for key in c["sources"]:
            yield f"evidence({atom(c['id'])}, {atom(key)})."


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("validate", "render", "query", "facts"))
    parser.add_argument("--topic", choices=sorted(TOPICS))
    parser.add_argument("--verdict", choices=sorted(VERDICTS))
    parser.add_argument("--text")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()
    data = json.loads(CATALOGUE.read_text(encoding="utf-8"))
    validate(data)
    if args.command == "validate":
        print(f"Validated {len(data['claims'])} claims and {len(data['sources'])} pinned source paths.")
    elif args.command == "render":
        target = EXPERIMENT / "results/ledger.md"
        target.write_text(render(data), encoding="utf-8", newline="\n")
        print(target.relative_to(ROOT).as_posix())
    elif args.command == "facts":
        print("\n".join(facts(data)))
    else:
        matches = query(data, args.topic, args.verdict, args.text)
        if args.as_json:
            print(json.dumps({**data, "claims": matches}, indent=2, ensure_ascii=False))
        else:
            for c in matches:
                print(f"{c['id']} [{c['kind']}; {c['verdict']}]")
                for field in TEXT_FIELDS:
                    print(f"  {field}: {c[field]}")
                for source in c["sources"]:
                    print(f"  source: {source_url(data, source)}")


if __name__ == "__main__":
    main()
