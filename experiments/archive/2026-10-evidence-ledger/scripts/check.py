"""Focused integrity checks and clean-namespace execution of the stdlib notebook."""

import copy
import contextlib
import io
import json

import ledger


data = json.loads(ledger.CATALOGUE.read_text(encoding="utf-8"))
ledger.validate(data)
assert len(ledger.query(data, topic="return-dynamics")) == 5
assert {c["id"] for c in ledger.query(data, topic="return-dynamics", verdict="uninformative")} == {"RD-03", "RD-05"}
assert "RD-05" in {c["id"] for c in ledger.query(data, text="ELIGIBILITY")}
assert not ledger.query(data, text="no_such_claim_19e92")
for mutate in (
    lambda d: d["claims"].append(copy.deepcopy(d["claims"][0])),
    lambda d: d["claims"][0].update(sources=["missing"]),
    lambda d: d["claims"][0].update(limitations=""),
):
    bad = copy.deepcopy(data)
    mutate(bad)
    try:
        ledger.validate(bad)
    except ValueError:
        pass
    else:
        raise AssertionError("invalid catalogue accepted")
rendered = ledger.render(data)
assert rendered == (ledger.EXPERIMENT / "results/ledger.md").read_text(encoding="utf-8")
facts = list(ledger.facts(data))
assert sum(line.startswith("claim(") for line in facts) == len(data["claims"])
assert sum(line.startswith("limitations(") for line in facts) == len(data["claims"])
assert ledger.atom("isn't") == "'isn''t'"

# Notebook cells are ordinary stdlib code: a fresh namespace avoids hidden state.
# This is not a Jupyter/kernel integration test.
notebook_path = ledger.EXPERIMENT / "notebook.ipynb"
notebook = json.loads(notebook_path.read_text(encoding="utf-8"))
namespace = {"__name__": "__main__"}
execution_count = 0
for index, cell in enumerate(notebook["cells"]):
    cell["id"] = f"evidence-{index}"
    if cell["cell_type"] != "code":
        continue
    execution_count += 1
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        exec(compile("".join(cell["source"]), f"notebook-cell-{index}", "exec"), namespace)
    cell["execution_count"] = execution_count
    cell["outputs"] = [{"name": "stdout", "output_type": "stream", "text": output.getvalue().splitlines(True)}]
notebook_path.write_text(json.dumps(notebook, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
print("PASS: filters, malformed-record rejection, generated-view equality, fact coverage, notebook cells.")
