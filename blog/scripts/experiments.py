"""Publish tracked experiment documents and saved notebook outputs; never execute cells."""
from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import re
import shutil
import subprocess
from pathlib import Path
from urllib.parse import quote, unquote, urlsplit

import nbformat
from bs4 import BeautifulSoup
from nbconvert import HTMLExporter

ROOT = Path(__file__).resolve().parents[2]
BLOG = ROOT / "blog"
OUTPUT = BLOG / "experiments"
# experiments/<bucket>/<slug>/: the bucket is status, the slug is identity, so pages are keyed by slug alone.
BUCKETS = ("active", "archive", "proposed")


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def notebook_anchor(path: Path, experiment: Path) -> str:
    return "notebook-" + path.relative_to(experiment).as_posix().replace("/", "-").replace(".", "-")


def heading_slug(text: str) -> str:
    return re.sub(r"[^\w -]", "", unquote(text).lower()).replace(" ", "-")


def build(baseurl: str, repository: str) -> None:
    tracked = {ROOT / path for path in git("ls-files").splitlines()}
    readmes = sorted((p for p in tracked if p.parent.parent.parent == ROOT / "experiments"
                      and p.parent.parent.name in BUCKETS and p.name == "README.md"
                      and not p.parent.name.startswith("_")), key=lambda p: p.parent.name, reverse=True)
    experiments = {p.parent for p in readmes}
    if len({p.name for p in experiments}) != len(experiments):
        raise ValueError("Two buckets hold experiments with the same slug; slugs must be unique")
    commit = git("rev-parse", "HEAD")
    # This fixed directory contains generated website files, never research data.
    assert OUTPUT.resolve() == ROOT.resolve() / "blog" / "experiments"
    marker = OUTPUT / ".generated-by-turmite-blog"
    if OUTPUT.exists():
        if not marker.is_file():
            raise RuntimeError(f"Refusing to replace an unmarked directory: {OUTPUT}")
        shutil.rmtree(OUTPUT)
    OUTPUT.mkdir()
    marker.touch()
    exporter = HTMLExporter(template_name="basic")
    exporter.exclude_anchor_links = True
    catalog = []
    manifest = {"commit": commit, "inputs": {}, "missing_links": []}
    guide_path = BLOG / "experiment-guides.tsv"
    guides = {}
    if guide_path.is_file():
        manifest["inputs"][guide_path.relative_to(ROOT).as_posix()] = digest(guide_path)
        with guide_path.open(encoding="utf-8") as handle:
            for row in csv.DictReader(handle, delimiter="\t"):
                if row["slug"] in guides or not all(row.values()):
                    raise ValueError(f"Duplicate or incomplete reader guide: {row['slug']}")
                guides[row["slug"]] = row
        if set(guides) != {p.name for p in experiments}:
            raise ValueError("Reader guide coverage differs from tracked experiments: "
                             + str(sorted(set(guides) ^ {p.name for p in experiments})))
    figure_path = BLOG / "experiment-figures.json"
    figures = json.loads(figure_path.read_text()) if figure_path.is_file() else {"library": {}, "experiments": {}}
    if figure_path.is_file():
        manifest["inputs"][figure_path.relative_to(ROOT).as_posix()] = digest(figure_path)
        if set(figures["experiments"]) - {p.name for p in experiments}:
            raise ValueError("Figure collection refers to an unknown experiment")

    def site_url(path: str) -> str:
        return baseurl + "/experiments/" + path

    def repo_url(path: Path, fragment: str = "") -> str:
        return repository + "/blob/" + commit + "/" + quote(path.relative_to(ROOT).as_posix()) + fragment

    def rewrite(fragment: str, source: Path, experiment: Path) -> str:
        soup = BeautifulSoup(fragment, "html.parser")
        namespace = notebook_anchor(source, experiment) + "-" if source.suffix == ".ipynb" else "log-" if source.name == "NOTEBOOK.md" else ""
        heading_counts = {}
        for heading in soup.find_all(re.compile(r"^h[1-6]$")):
            slug = heading_slug(heading.get_text())
            count = heading_counts.get(slug, 0)
            heading_counts[slug] = count + 1
            heading["id"] = namespace + slug + (f"-{count}" if count else "")
        for element in soup.find_all(["a", "img", "source"]):
            attr = "href" if element.name == "a" else "src"
            url = element.get(attr)
            if not url or url.startswith("//"):
                continue
            if url.startswith("#"):
                element[attr] = "#" + namespace + heading_slug(url[1:])
                continue
            parsed = urlsplit(url)
            if parsed.scheme:
                continue
            target = (source.parent / unquote(parsed.path)).resolve()
            suffix = "#" + heading_slug(parsed.fragment) if parsed.fragment else ""
            parent_experiment = next((p for p in [target, *target.parents] if p in experiments), None)
            if target.name == "README.md" and target.parent in experiments:
                element[attr] = site_url(target.parent.name + "/") + suffix
            elif target.suffix == ".ipynb" and target in tracked and parent_experiment:
                anchor = notebook_anchor(target, parent_experiment)
                if parsed.fragment:
                    anchor += "-" + heading_slug(parsed.fragment)
                element[attr] = site_url(parent_experiment.name + "/") + "#" + anchor
            elif attr == "src" and target in tracked and target.is_file():
                # Copy only referenced, committed images, preserving their repository path.
                relative = target.relative_to(ROOT)
                dest = OUTPUT / experiment.name / "assets" / relative
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(target, dest)
                manifest["inputs"][relative.as_posix()] = digest(target)
                element[attr] = site_url(experiment.name + "/assets/" + quote(relative.as_posix()))
            elif target in tracked or (target.is_dir() and ROOT in target.parents):
                if repository:
                    link = repo_url(target, suffix)
                    if target.is_dir():
                        link = link.replace("/blob/", "/tree/", 1)
                    element[attr] = link
                else:
                    del element[attr]
                    element["title"] = "Repository source: " + target.relative_to(ROOT).as_posix()
                    element["class"] = ["source-reference"]
            else:
                # Older READMEs contain migration-era links; keep their label, not a 404.
                manifest["missing_links"].append({"source": source.relative_to(ROOT).as_posix(), "target": url})
                del element[attr]
                element["title"] = "Source reference unavailable: " + url
                element["class"] = ["source-reference"]
        for code_input in soup.select(".input"):
            details = soup.new_tag("details", attrs={"class": "notebook-code"})
            summary = soup.new_tag("summary")
            summary.string = "Code"
            code_input.wrap(details)
            details.insert(0, summary)
        return str(soup)

    def render_markdown(path: Path, experiment: Path) -> str:
        manifest["inputs"][path.relative_to(ROOT).as_posix()] = digest(path)
        notebook = nbformat.v4.new_notebook(cells=[nbformat.v4.new_markdown_cell(path.read_text(), id="document")])
        notebook.metadata.language_info = {"name": "python", "pygments_lexer": "python3"}
        body, _ = exporter.from_notebook_node(notebook, resources={"metadata": {"path": str(path.parent)}})
        return rewrite(body, path, experiment)

    for readme in readmes:
        experiment = readme.parent
        notebooks = sorted(p for p in tracked if p.suffix == ".ipynb"
                           and (p.parent == experiment or experiment / "notebooks" in p.parents))
        text = readme.read_text()
        title_match = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
        title = title_match.group(1).replace("`", "") if title_match else experiment.name
        overview = render_markdown(readme, experiment)
        excerpt = BeautifulSoup(overview, "html.parser").find("p")
        description = re.sub(r"\s+", " ", excerpt.get_text(" ", strip=True))[:250] if excerpt else "Experiment record."
        guide = guides.get(experiment.name)
        sections = []
        if guide:
            title, description = guide["title"], guide["question"]
            sections.append('<section class="prose reader-guide">'
                            '<h2 id="reader-hypothesis">The idea under test</h2><p>' + html.escape(guide["hypothesis"]) + '</p>'
                            '<h2 id="reader-findings">What we learned</h2><p>' + html.escape(guide["finding"]) + '</p>'
                            '<h3>What this leaves open</h3><p>' + html.escape(guide["caveat"]) + '</p></section>')
            evidence = ROOT / guide["evidence"]
            if evidence not in tracked or not evidence.is_file():
                raise ValueError(f"Reader guide evidence must be tracked: {evidence}")
            manifest["inputs"][guide["evidence"]] = digest(evidence)
            evidence_html = rewrite('<a href="' + html.escape(str(evidence), quote=True) + '">Read the evidence and reproduction recipe ↗</a>', readme, experiment)
            sections.append('<p class="guide-evidence">' + evidence_html + '</p>')
        else:
            sections.append('<section class="prose reader-guide"><h2>About this record</h2>'
                            '<p>This experiment has not yet received a reader introduction. The original record below '
                            'contains its methods and any saved findings.</p></section>')
        gallery = []
        for figure_id in figures["experiments"].get(experiment.name, []):
            figure = figures["library"][figure_id]
            asset, recipe = ROOT / figure["path"], ROOT / figure["recipe"]
            if asset not in tracked or recipe not in tracked or not asset.is_file() or not recipe.is_file():
                raise ValueError(f"Figure and recipe must be tracked files: {figure}")
            manifest["inputs"][figure["recipe"]] = digest(recipe)
            fragment = ('<figure><a href="' + html.escape(str(asset), quote=True) + '">'
                        '<img src="' + html.escape(str(asset), quote=True) + '" alt="' + html.escape(figure["alt"], quote=True)
                        + '" loading="lazy"></a><figcaption>' + html.escape(figure["caption"])
                        + ' <a href="' + html.escape(str(recipe), quote=True) + '">Figure source and recipe ↗</a></figcaption></figure>')
            # Both the full-size link and inline image use the copied site asset.
            rendered = rewrite(fragment, readme, experiment)
            soup = BeautifulSoup(rendered, "html.parser")
            soup.find("a")["href"] = soup.find("img")["src"]
            gallery.append(str(soup))
        if gallery:
            sections.insert(0, '<section id="visual-evidence" class="experiment-figures" aria-label="Visual evidence">'
                            '<h2>A closer look</h2>' + ''.join(gallery) + '</section>')
        sections.append('<section id="research-record" class="research-record"><h2>Inside the experiment</h2>'
                        '<p>Methods, registered predictions, exact commands and saved analysis. '
                        'These are the working research documents; expand them for the detail behind the introduction.</p>'
                        '<details class="record-details"><summary>Methods and original experiment record</summary>'
                        '<div class="prose experiment-overview">' + overview + '</div></details>')
        notebook_info = []
        for path in notebooks:
            manifest["inputs"][path.relative_to(ROOT).as_posix()] = digest(path)
            data = json.loads(path.read_text(encoding="utf-8-sig"))
            # Older notebooks lack cell IDs. Assign stable IDs in memory only;
            # nbformat otherwise introduces random IDs when repairing them.
            for index, cell in enumerate(data.get("cells", [])):
                cell.setdefault("id", f"cell-{index}")
            notebook = nbformat.reads(json.dumps(data), as_version=4)
            language = notebook.metadata.setdefault("language_info", {})
            language.setdefault("name", "python")
            if language.get("name", "python").startswith("python"):
                # Static syntax highlighting does not need an interactive kernel.
                language["pygments_lexer"] = "python3"
            code_cells = [c for c in notebook.cells if c.cell_type == "code"]
            outputs = sum(len(c.get("outputs", [])) for c in code_cells)
            errors = sum(o.output_type == "error" for c in code_cells for o in c.get("outputs", []))
            body, _ = exporter.from_notebook_node(notebook, resources={"metadata": {"path": str(path.parent)}})
            anchor = notebook_anchor(path, experiment)
            name = path.relative_to(experiment).as_posix()
            download = experiment.name + "/notebooks/" + name
            dest = OUTPUT / download
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, dest)
            message = f"{outputs} saved outputs · {len(code_cells)} code cells. Cells are not executed during publication."
            if not outputs:
                message = "No saved outputs. This render shows the saved narrative and code; cells have not been executed for publication."
            if errors:
                message += f" {errors} saved error outputs are preserved below."
            sections.append(f'<details id="{anchor}" class="notebook-section record-details"><summary>Analysis notebook: {html.escape(name)}</summary>'
                            f'<p class="render-note">{message} '
                            f'<a href="{site_url(download)}" download>Download notebook</a></p>'
                            f'<div class="notebook-render">{rewrite(body, path, experiment)}</div></details>')
            notebook_info.append({"name": name, "anchor": anchor, "outputs": outputs, "errors": errors})
        if not notebooks:
            sections.append('<section class="notebook-section"><h2>Notebook</h2><p class="render-note">'
                            'No committed Jupyter notebook is available for this experiment yet.</p></section>')
        log = experiment / "NOTEBOOK.md"
        if log in tracked:
            sections.append('<details class="lab-log"><summary>Read the dated lab log</summary>'
                            '<div class="prose">' + render_markdown(log, experiment) + '</div></details>')
        sections.append('</section>')
        metadata = {"layout": "experiment", "title": title, "description": description,
                    "reader_guide": bool(guide), "has_figures": bool(gallery),
                    "figure_preview": BeautifulSoup(gallery[0], "html.parser").find("img")["src"] if gallery else "",
                    "slug": experiment.name, "bucket": experiment.parent.name, "source_commit": commit, "notebooks": notebook_info,
                    "source_url": repo_url(readme) if repository else ""}
        destination = OUTPUT / experiment.name / "index.html"
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text("---\n" + json.dumps(metadata, ensure_ascii=False) + "\n---\n{% raw %}\n"
                               + "\n".join(sections) + "\n{% endraw %}\n")
        catalog.append({**metadata, "url": "/experiments/" + experiment.name + "/"})
    data_dir = BLOG / "_data"
    data_dir.mkdir(exist_ok=True)
    (data_dir / "experiments.json").write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n")
    (OUTPUT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2) + "\n")
    print(f"Published {len(catalog)} experiment pages, {sum(len(p['notebooks']) for p in catalog)} notebooks; "
          f"{len(manifest['missing_links'])} unavailable source references recorded in experiments/manifest.json.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseurl", default="", help="Pages project path, e.g. /turmite")
    parser.add_argument("--repository-url", default="", help="GitHub repository URL for pinned source links")
    args = parser.parse_args()
    build(args.baseurl.rstrip("/"), args.repository_url.rstrip("/"))
