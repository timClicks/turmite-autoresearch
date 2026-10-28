"""Small publishing fixtures: saved outputs, paths, provenance, and repeatability."""
import contextlib
import hashlib
import io
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import nbformat

import experiments


class PublishingTest(unittest.TestCase):
    def test_saved_outputs_links_and_repeatability(self):
        with tempfile.TemporaryDirectory() as scratch:
            root = Path(scratch)
            blog = root / "blog"
            blog.mkdir()
            first = root / "experiments/active/2026-10-first"
            second = root / "experiments/archive/2026-10-second"
            first.mkdir(parents=True)
            second.mkdir(parents=True)
            (first / "README.md").write_text(
                "# First experiment\n\n[Jump](#first-experiment)\n\n[Other](../../archive/2026-10-second/README.md)\n\n"
                "[Code](script.py)\n\n![Figure](plot.svg)\n\n[Missing](gone.csv)\n")
            (first / "script.py").write_text("print('source')\n")
            (first / "plot.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg"/>')
            (second / "README.md").write_text("# No notebook yet\n")
            (blog / "experiment-guides.tsv").write_text(
                "slug\ttitle\tquestion\thypothesis\tfinding\tcaveat\tevidence\n"
                + f"{first.name}\tA readable title\tWhy explore?\tA testable idea\tThe test failed.\tFinite windows.\texperiments/active/{first.name}/README.md\n"
                + f"{second.name}\tA planned test\tWhat might happen?\tAn unrun prediction\tNot run.\tNo evidence yet.\texperiments/archive/{second.name}/README.md\n")
            (blog / "experiment-figures.json").write_text(json.dumps({
                "library": {"plot": {"path": f"experiments/active/{first.name}/plot.svg",
                                     "recipe": f"experiments/active/{first.name}/script.py",
                                     "alt": "Measured comparison", "caption": "A saved observation, not a mechanism."}},
                "experiments": {first.name: ["plot"]},
            }))
            (first / "NOTEBOOK.md").write_text("# Dated log\n\nObservation.\n")
            nested = first / "notebooks"
            nested.mkdir()
            notebook = nbformat.v4.new_notebook(cells=[
                nbformat.v4.new_markdown_cell("# Saved narrative"),
                nbformat.v4.new_code_cell("raise RuntimeError('must not execute')", outputs=[
                    nbformat.v4.new_output("stream", name="stdout", text="SAVED_OUTPUT_42\n"),
                    nbformat.v4.new_output("error", ename="ValueError", evalue="saved error", traceback=["saved traceback"]),
                ]),
            ])
            # Exercise the older notebook format without modifying its on-disk IDs.
            for cell in notebook.cells:
                cell.pop("id", None)
            notebook_path = nested / "detail.ipynb"
            notebook_path.write_text(json.dumps(notebook), encoding="utf-8-sig")
            original = notebook_path.read_bytes()
            internal = root / "experiments/_template"
            internal.mkdir()
            (internal / "README.md").write_text("# Not an experiment")
            for args in (["init", "-q"], ["add", "."],
                         ["-c", "user.name=Fixture", "-c", "user.email=fixture@example.test", "commit", "-qm", "Fixture"]):
                subprocess.run(["git", *args], cwd=root, check=True)
            (first / "untracked.ipynb").write_text("invalid untracked notebook")

            with patch.multiple(experiments, ROOT=root, BLOG=blog, OUTPUT=blog / "experiments"):
                def render():
                    with contextlib.redirect_stdout(io.StringIO()):
                        experiments.build("/project", "https://github.com/example/project")
                    return {p.relative_to(blog).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                            for p in blog.rglob("*") if p.is_file()}

                snapshot = render()
                self.assertEqual(snapshot, render())
                self.assertEqual(notebook_path.read_bytes(), original)
                catalog = json.loads((blog / "_data/experiments.json").read_text())
                self.assertEqual(len(catalog), 2)
                first_page = (blog / "experiments" / first.name / "index.html").read_text()
                second_page = (blog / "experiments" / second.name / "index.html").read_text()
                self.assertIn("SAVED_OUTPUT_42", first_page)
                self.assertIn("A readable title", first_page)
                self.assertIn('id="reader-hypothesis"', first_page)
                self.assertIn("The test failed.", first_page)
                self.assertIn("A saved observation, not a mechanism.", first_page)
                self.assertLess(first_page.index("The test failed."), first_page.index('id="research-record"'))
                self.assertIn('<details class="record-details">', first_page)
                self.assertIn('<details id="notebook-notebooks-detail-ipynb"', first_page)
                self.assertIn('href="/project/experiments/' + first.name + '/assets/', first_page)
                self.assertIn('id="first-experiment"', first_page)
                self.assertIn('href="#first-experiment"', first_page)
                self.assertIn("saved traceback", first_page)
                self.assertIn('<details class="notebook-code">', first_page)
                self.assertIn("/project/experiments/2026-10-second/", first_page)
                self.assertIn("/assets/experiments/active/2026-10-first/plot.svg", first_page)
                self.assertIn("https://github.com/example/project/blob/", first_page)
                self.assertIn("No committed Jupyter notebook", second_page)
                manifest = json.loads((blog / "experiments/manifest.json").read_text())
                self.assertEqual(manifest["missing_links"][0]["target"], "gone.csv")
                self.assertEqual(len(catalog[1]["notebooks"]), 1)
                self.assertTrue(catalog[1]["reader_guide"])
                self.assertTrue(catalog[1]["has_figures"])
                self.assertIn("blog/experiment-guides.tsv", manifest["inputs"])
                self.assertIn(f"experiments/active/{first.name}/script.py", manifest["inputs"])
                self.assertIn(f"experiments/active/{first.name}/plot.svg", manifest["inputs"])

    def test_unmarked_directory_is_preserved(self):
        with tempfile.TemporaryDirectory() as scratch:
            output = Path(scratch) / "blog/experiments"
            output.mkdir(parents=True)
            sentinel = output / "keep.txt"
            sentinel.write_text("existing file")
            with patch.multiple(experiments, ROOT=Path(scratch), BLOG=output.parent, OUTPUT=output), \
                    patch.object(experiments, "git", return_value=""):
                with self.assertRaisesRegex(RuntimeError, "unmarked"):
                    experiments.build("", "")
            self.assertEqual(sentinel.read_text(), "existing file")


if __name__ == "__main__":
    unittest.main()
