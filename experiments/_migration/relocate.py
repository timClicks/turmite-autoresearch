"""Move experiment folders and rewrite every reference to them, from a TSV of old -> new paths.

usage (from the repository root):
    uv run --frozen experiments/_migration/relocate.py MAP.tsv [--dry-run]
    uv run --frozen experiments/_migration/relocate.py MAP.tsv --local-only

MAP.tsv has a header and the columns old_path, new_path, bucket, reason, with paths such as
`experiments/2026-10-13-census-sweeps` -> `experiments/archive/2026-10-census-sweeps`. To move an
experiment between buckets later, write a one-row map (`experiments/active/X` -> `experiments/archive/X`)
and run this script on it; the rows of earlier maps stay as the record of where things used to be.

The default mode `git mv`s every tracked folder and rewrites tracked text files in the same pass:
  * `experiments/OLD...` -> `experiments/BUCKET/NEW...` (repository paths in prose, code, CI, the paper);
  * `/experiments/OLD/` site URLs under `blog/` -> `/experiments/NEW/` (blog pages are keyed by slug, not bucket);
  * a bare `OLD` slug -> `NEW` (reader guides, atlas, figure lists, prose);
  * relative paths (`../x`, `../../notes/y.md`, `$(dirname "$0")/../../..`) inside a moved folder that leave it are
    recomputed for the new depth, and `Path(__file__).parents[k]` / `.parent` chains that reach `experiments/` or
    above gain one level per extra directory;
  * `X.parent / "OLD"` and `"experiments" / "OLD"` in Python become bucket-aware.
It does not touch, by design: links pinned to a commit (`blob/<sha>/experiments/OLD/...`, which must keep the path
that existed at that commit), generated data (anything under `results/` except Markdown reports, and `.log`, `.csv`,
`.sha256`, `.patch` files anywhere), notebook outputs (only cell sources are rewritten), and `experiments/_migration/`.

Review the staged diff before committing. Two cases needed hand fixes on 2026-10-28: paths that point into another
worktree or branch, which still has the old layout, and a name such as `EXP` reused inside generated notebook code
for a different folder (`Path.cwd()`), whose `.parent` was bumped. A script whose string literals are themselves
relative paths it once rewrote (a one-off fix-up) is also rewritten; restore it, since it records what was run.

`--local-only` is for other checkouts after pulling the move: git has moved the tracked files, but gitignored
`dumps*/`, `knock*/`, `scratch/` and `synth/` stay in the old folders. It moves whatever is left in each old folder
into the new one and refuses to overwrite anything.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[2]
SKIP_SUFFIXES = {".log", ".csv", ".sha256", ".patch", ".pdf", ".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg",
                 ".zip", ".gz", ".lz4", ".bin", ".parquet", ".npz", ".npy", ".ico", ".woff", ".woff2"}
BUCKETS = ("active", "archive", "proposed")


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True)


def load_map(path: Path) -> list[tuple[str, str]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].split("\t")[:2] != ["old_path", "new_path"]:
        raise SystemExit(f"{path}: expected a header starting old_path<TAB>new_path")
    pairs = [tuple(line.split("\t")[:2]) for line in lines[1:] if line.strip()]
    olds, news = [o for o, _ in pairs], [n for _, n in pairs]
    if len(set(olds)) != len(olds) or len(set(news)) != len(news):
        raise SystemExit("duplicate old or new paths in the map")
    for o, n in pairs:
        for p in (o, n):
            if not re.fullmatch(r"experiments/(?:(?:%s)/)?[^/_][^/]*" % "|".join(BUCKETS), p):
                raise SystemExit(f"not an experiment folder path: {p}")
    return pairs


def is_data(rel: str) -> bool:
    p = PurePosixPath(rel)
    if p.suffix.lower() in SKIP_SUFFIXES or rel.startswith("experiments/_migration/"):
        return True
    return "results" in p.parts[:-1] and p.suffix.lower() != ".md"


class Rewriter:
    def __init__(self, pairs: list[tuple[str, str]]):
        self.pairs = pairs
        self.by_old = dict(pairs)
        self.slug = {PurePosixPath(o).name: PurePosixPath(n).name for o, n in pairs}
        self.full = {PurePosixPath(o).name: n for o, n in pairs}
        alt = "|".join(re.escape(s) for s in sorted(self.slug, key=len, reverse=True))
        bucket = "(?:%s)/" % "|".join(BUCKETS)
        # One pass, so a replacement is never rewritten again. The slug must not continue as a longer name.
        self.token = re.compile(
            r"(?P<pin>(?:blob|tree|raw)/[0-9a-f]{7,40}/)?(?P<exp>experiments/(?:%s)?)?(?P<slug>%s)(?![\w-])" % (bucket, alt))
        self.pyjoin = re.compile(
            r'(?P<pre>(?P<var>\b\w+)(?:\.parent|\.parents\[0\])\s*/\s*|"experiments"\s*/\s*|"experiments",\s*)'
            r'"(?P<slug>%s)(?=["/])' % alt)
        # A relative path has at least one slash (`../x`, `../..`); a bare `..` is too often an ellipsis or a range.
        self.rel = re.compile(r"""(?<![\w.~-])\.\.(?:/\.\.)*/[^\s)\]>`'"*,;:|{}]*""")

    def moved(self, rel: str) -> tuple[str, str] | None:
        for o, n in self.pairs:
            if rel.startswith(o + "/"):
                return o, n
        return None

    def new_path(self, rel: str) -> str:
        hit = self.moved(rel)
        return hit[1] + rel[len(hit[0]):] if hit else rel

    def text(self, s: str, rel: str) -> str:
        hit = self.moved(rel)
        s = self.relative(s, rel, hit)
        levels = {}
        if hit and rel.endswith(".py"):
            s, levels = self.python_roots(s, rel)
        s = self.pyjoin.sub(self._pyjoin(rel, levels), s)
        return self.token.sub(self._token(rel), s)

    def _pyjoin(self, rel: str, levels: dict[str, int]):
        new_parts = PurePosixPath(self.new_path(rel)).parts

        def fn(m: re.Match) -> str:
            path = self.full[m["slug"]]  # experiments/BUCKET/NEW
            if m["pre"].startswith('"experiments",'):
                return '"experiments", "' + '", "'.join(PurePosixPath(path).parts[1:])
            if m["pre"].startswith('"experiments"'):
                return f'"{path}'
            name = m["var"]
            if name not in levels:
                return m[0]  # X.parent / "OLD" where X is not a known folder of this file: leave for review
            # X.parent was experiments/. Address the sibling from the repository root instead, as a path that a
            # later bucket move can rewrite.
            return f'{name}.parents[{len(new_parts) - levels[name] - 1}] / "{path}'
        return fn

    def _token(self, rel: str):
        in_blog = rel.startswith("blog/")

        def fn(m: re.Match) -> str:
            if m["pin"]:
                return m[0]
            new_slug = self.slug[m["slug"]]
            if not m["exp"]:
                prev = m.string[m.start() - 1:m.start()]
                if PurePosixPath(rel).parent.as_posix() == "experiments" and re.fullmatch(r"[(\s`'\"<]?", prev):
                    return self.full[m["slug"]][len("experiments/"):]  # a link relative to experiments/
                return new_slug
            start = m.start("exp")
            before = m.string[start - 2] if start >= 2 else ""
            if in_blog and m.string[start - 1:start] == "/" and not re.match(r"[\w.~-]", before):
                return "experiments/" + new_slug  # site URL: one page per slug, independent of bucket
            return self.full[m["slug"]]
        return fn

    def relative(self, s: str, rel: str, hit: tuple[str, str] | None) -> str:
        old_dir = PurePosixPath(rel).parent.as_posix()
        new_dir = PurePosixPath(self.new_path(rel)).parent.as_posix()
        # A relative path is read from the file's folder, or, for scripts that `cd` there first, from its experiment.
        bases = [(old_dir, new_dir)]
        if hit and old_dir != hit[0]:
            bases.append(hit)

        def fn(m: re.Match) -> str:
            tok = m[0]
            for old_base, new_base in bases:
                target = os.path.normpath(os.path.join(old_base, tok))
                if target.startswith(".."):
                    continue
                if hit and (target == hit[0] or target.startswith(hit[0] + "/")):
                    return tok  # inside the same experiment, which moves as a whole
                if target in self.by_old or self.moved(target):
                    dest = self.by_old.get(target) or self.new_path(target)  # gitignored targets need not exist
                elif hit and (ROOT / target).exists():
                    dest = target  # leaves a moved experiment for a path that stays put (notes/, src/, ...)
                else:
                    continue
                new = os.path.relpath(dest, new_base)
                return new + "/" if tok.endswith("/") and not new.endswith("/") else new
            return tok
        return self.rel.sub(fn, s)

    def python_roots(self, s: str, rel: str) -> tuple[str, dict[str, int]]:
        """Bump `Path(__file__)` ancestors, and ancestors of names bound to them, that reach experiments/ or above.

        A level counts `.parent` steps from the file (`.parents[k]` is level k + 1). Returns the new text and the
        levels of the names bound in simple assignments, for _pyjoin."""
        old_parts = PurePosixPath(rel).parts
        extra = len(PurePosixPath(self.new_path(rel)).parts) - len(old_parts)
        reach = len(old_parts) - 1 - old_parts.index("experiments")  # level of experiments/ from the old file
        anchor = r"(?:pathlib\.)?Path\((?:__file__|sys\.argv\[0\])\)(?:\.resolve\(\))?"
        step = r"(?:\.parents\[(?P<k>\d+)\]|(?P<chain>(?:\.parent)+)(?![\w\[]))"

        def level(m: re.Match) -> int:
            return int(m["k"]) + 1 if m["k"] is not None else m["chain"].count(".parent")

        def bump(m: re.Match, base: int) -> str:
            text = m[0]
            if base >= reach or base + level(m) < reach:
                return text  # the base itself was bumped, or the target stays inside the experiment
            if m["k"] is not None:
                return text[: text.rindex("[") + 1] + f"{int(m['k']) + extra}]"
            return text + ".parent" * extra

        levels: dict[str, int] = {}
        for m in re.finditer(r"(?:^|;)\s*(?P<name>\w+)\s*=\s*" + anchor + r"(?:" + step + r")?(?=\s*(?:;|#|$))", s, re.M):
            levels[m["name"]] = level(m) if (m["k"] is not None or m["chain"]) else 0
        for m in re.finditer(r"(?:^|;)\s*(?P<name>\w+)\s*=\s*(?P<base>\w+)" + step + r"(?=\s*(?:;|#|$))", s, re.M):
            if m["base"] in levels:
                levels.setdefault(m["name"], levels[m["base"]] + level(m))
        s = re.sub(anchor + step, lambda m: bump(m, 0), s)
        for name, base in levels.items():
            # `X.parent / "OLD"` is a sibling experiment; _pyjoin rewrites it, so do not bump it here.
            s = re.sub(rf"\b{name}" + step + r'(?!\s*/\s*"(?:%s)["/])' % "|".join(map(re.escape, self.slug)),
                       lambda m, b=base: bump(m, b), s)
        new_levels = {n: (lv + extra if lv >= reach else lv) for n, lv in levels.items()}
        return s, new_levels

    def notebook(self, raw: str, rel: str) -> str:
        nb = json.loads(raw)
        for cell in nb.get("cells", []):
            src = cell.get("source", "")
            joined = "".join(src) if isinstance(src, list) else src
            new = self.text(joined, rel)
            if new != joined:
                cell["source"] = new.splitlines(keepends=True) if isinstance(src, list) else new
        out = json.dumps(nb, indent=1, ensure_ascii=False) + "\n"
        return out


def plan(pairs):
    rw = Rewriter(pairs)
    tracked = [f for f in git("ls-files", "-z").split("\0") if f]
    for o, n in pairs:
        if not any(f.startswith(o + "/") for f in tracked):
            raise SystemExit(f"nothing tracked under {o}")
        if (ROOT / n).exists():
            raise SystemExit(f"target exists: {n}")
    edits = {}
    for rel in tracked:
        if is_data(rel):
            continue
        path = ROOT / rel
        if path.is_symlink() or not path.is_file():
            continue
        try:
            raw = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if rel.endswith(".ipynb"):
            try:
                exact = json.dumps(json.loads(raw), indent=1, ensure_ascii=False) + "\n" == raw
            except json.JSONDecodeError:  # e.g. a byte-order mark
                exact = False
            if not exact:
                print(f"warning: {rel} does not round-trip through json; rewriting it as text")
                new = rw.text(raw, rel)
            else:
                new = rw.notebook(raw, rel)
        else:
            new = rw.text(raw, rel)
        if new != raw:
            edits[rel] = new
    return rw, edits


def relocate(pairs, dry_run: bool) -> None:
    rw, edits = plan(pairs)
    print(f"{len(pairs)} folders to move, {len(edits)} files to rewrite")
    if dry_run:
        for rel in sorted(edits):
            print("rewrite", rel, "->", rw.new_path(rel))
        return
    for o, n in pairs:
        (ROOT / n).parent.mkdir(parents=True, exist_ok=True)
        subprocess.check_call(["git", "mv", o, n], cwd=ROOT)
    for rel, text in edits.items():
        (ROOT / rw.new_path(rel)).write_text(text, encoding="utf-8", newline="")
    subprocess.check_call(["git", "add", "-A", "--", *sorted({PurePosixPath(rw.new_path(r)).as_posix() for r in edits})],
                          cwd=ROOT)
    move_leftovers(pairs)


def move_leftovers(pairs) -> None:
    for o, n in pairs:
        src, dst = ROOT / o, ROOT / n
        if not src.exists():
            continue
        if not dst.exists():
            raise SystemExit(f"{n} does not exist; pull the commit that moved {o} first")
        for item in sorted(src.rglob("*"), key=lambda p: len(p.parts), reverse=True):
            if item.is_dir():
                continue
            target = dst / item.relative_to(src)
            if target.exists():
                raise SystemExit(f"refusing to overwrite {target.relative_to(ROOT)}")
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(item, target)
            print("moved", item.relative_to(ROOT), "->", target.relative_to(ROOT))
        for d in sorted((p for p in src.rglob("*") if p.is_dir()), key=lambda p: len(p.parts), reverse=True):
            d.rmdir()
        src.rmdir()


def main() -> None:
    args = sys.argv[1:]
    if not args or args[0].startswith("-"):
        raise SystemExit(__doc__)
    pairs = load_map(Path(args[0]))
    if "--local-only" in args:
        move_leftovers(pairs)
    else:
        relocate(pairs, "--dry-run" in args)


if __name__ == "__main__":
    main()
