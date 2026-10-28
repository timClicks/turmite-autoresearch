# turmite-autoresearch blog

A small Jekyll site for researcher-written Markdown entries. The blog is
independent of the simulator in `web/` and does not publish the repository's
notes, raw data, or scratch files automatically. Build dependencies are pinned
in `Gemfile.lock` and `uv.lock`.

## Write an entry

1. Copy `templates/post.md` to `_posts/YYYY-MM-DD-short-title.md`.
2. Set the title, description, date **with a timezone offset**, author, status,
   and tags. Suggested statuses: `Hypothesis`, `Experiment`, `Null result`,
   `Instrument`, and `Project note` (free text).
3. For research results, set `experiment` to its repository-relative folder
   and `commit` to the full Git revision containing the evidence. Link data,
   scripts, commands, seeds, fit windows, calibration, and uncertainty in the
   body. Blog entries summarise the scientific record; they do not replace it.
4. Preview, review the generated page, and commit the source in a PR.

Use `_drafts/short-title.md` while writing (create the directory as needed).
Drafts and future-dated posts are excluded from production. To publish a draft,
move it into `_posts/` with a dated filename and update its date. Drafts committed
to a public repository **are public source**, even though absent from the site.

Store small figures in `assets/posts/<slug>/`. In Markdown, use a base-path-aware
image URL:

```liquid
![Descriptive alt text]({{ '/assets/posts/my-entry/figure.png' | relative_url }})
```

Use fenced code blocks with a language, Markdown tables, and normal headings.
For inline equations use Unicode or HTML (`t<sup>1/3</sup>`); this bootstrap
does not load a remote maths renderer. For cross-post links use Jekyll's
`post_url` tag on its own. In Jekyll 4 it already includes `baseurl`, so do
not pass it through `relative_url` (that doubles the base path and fails
`scripts/check.rb`):

```liquid
{% capture entry_url %}{% post_url 2026-10-19-opening-the-research-log %}{% endcapture %}
[Opening entry]({{ entry_url }})
```

Add corrections under a new dated heading; preserve the original prediction.
Avoid numerical claims without a reproducible source.

## Local preview (WSL)

Requires Ruby 3.3 and Bundler. Run in WSL from `/mnt/f/Code/turmite/blog`:

```bash
export UV_PROJECT_ENVIRONMENT=$HOME/.venvs/turmite UV_LINK_MODE=copy
export BUNDLE_PATH=$HOME/.local/share/turmite-blog-gems
bundle install
cd ..
uv run --frozen --only-group blog blog/scripts/experiments.py
cd blog
bundle exec jekyll serve --host 0.0.0.0 --baseurl ''
# Include work in progress only when previewing:
bundle exec jekyll serve --host 0.0.0.0 --baseurl '' --drafts --future
```

Open <http://localhost:4000>. The Python preparation step publishes the
experiment records; Jekyll builds the complete site. Re-run preparation after
changing an experiment, then restart Jekyll or let its watcher rebuild.
To build and check a project site locally:

```bash
# From the repository root, using the WSL environment exports above:
uv run --frozen --only-group blog blog/scripts/experiments.py --baseurl /turmite-autoresearch
cd blog
JEKYLL_ENV=production bundle exec jekyll build --strict_front_matter --baseurl /turmite-autoresearch
bundle exec ruby scripts/check.rb _site /turmite-autoresearch
```

Output is in ignored `_site/`. The checker verifies required pages, local
links and assets, project-site prefixes, and exclusion of authoring files.
Canonical URLs and feed URLs use `url` and `baseurl`; for a production-like
local build, set `url` in a separate config override. `repository_url` enables
source and provenance links and defaults to `https://github.com/timClicks/turmite-autoresearch`.
GitHub Actions supplies all three automatically, including the `/turmite-autoresearch`
base path for this repository’s project site.

## Interactive statistics in posts

Pair statistical claims with an embedded, bespoke explorer when changing a
window or parameter helps readers judge them. Keep the explanation and a static
fallback in the post. Sliders should select recorded parameters or explicitly
labelled model assumptions; do not imply a fresh simulation or interpolate
unmeasured noise levels. Show sample counts, between-seed spread, exclusions,
and drift alongside the estimate.

The first example is the noisy-rotor explorer in **The ant below every walker**.
It refits saved probe windows entirely in the browser, with no server, remote
plotting library, or simulation. Noise selects one of nine measured levels;
two window sliders change the first and last included window ends. The graph
uses equally spaced, labelled noise categories and does not connect them.
The table and live text provide the same results without relying on colour
or the SVG. Sliders support keyboard input; no animation is required.

To reuse that instrument in another post, add `interactive_stats: true` to its
front matter and put this on its own line, with blank lines around it:

```liquid
{% include stats-explorer.html data="noisy_rotor" %}
```

`_includes/stats-explorer.html` defines this instrument's controls, fallback,
method and provenance. `assets/stats.js` supplies the browser fits and a small
SVG plot. New scientific instruments should get their own include and a
specific data schema rather than inheriting noisy-rotor assumptions.
The layout loads the shared script only on opted-in pages; multiple instances
have independent controls. Styling follows the blog's light/dark themes.

The compact `_data/noisy_rotor.json` is generated from committed CSVs with
`uv run --frozen blog/scripts/export_stats.py` (WSL, normal environment exports).
It records source revision, input SHA-256 hashes, column meanings, seeds,
run escape flags and the generating command. The exporter refuses uncommitted
input changes. Regenerate and commit the payload when adopting new evidence;
do not hand-edit it. Jekyll embeds it directly, so Pages subpaths need no fetch
configuration. Nothing executes notebook cells or rewrites research results.

Run `node blog/scripts/test_stats.js` using the existing pinned jsdom dependency
(`npm ci --prefix web`). Tests check analytical controls, every row of the
published numpy analysis at its reported precision, source hashes, missing
windows, slider bounds, reset and independent instances. This preserves the
existing estimator; any future estimator change requires scientific calibration
under the repository's normal experiment conventions.

## Homepage

The **Preliminary results** section gives each of the manuscript's nine key-result
bullets a card in a responsive masonry layout. Existing figures link to full-size
copies; native details preserve caveats without JavaScript. Two sliders illustrate
the stated cube-root scaling and the fitted opening-run law, and a toggle compares
saved occupation values with their growth-adjusted references. Card 09 adds a time
slider over RLRLLL's saved snapshots: the browser redraws the territory from the
committed arrival map (`rlrlll_arrival.png`, one byte per 16x16 block) with the
figure's exact colours, and only once it has drawn the canvas does it reveal the
slider; otherwise the static map stays. The controls do not run simulations or
estimate new scientific quantities. The ant bar is a median
over rules; walker bars are eight-seed means, with the window mismatch disclosed.

Numbers, paper bullet titles, five manuscript figure copies and one homepage-only
figure (card 09's RLRLLL portrait, from `experiments/archive/2026-10-rlrlll-portrait/results/`;
listed in `EXTRA_IMAGES`) are exported from committed sources, with hashes and a
pinned revision:

```bash
uv run --frozen --only-group blog blog/scripts/export_results.py
uv run --frozen --only-group blog blog/scripts/export_results.py --check
```

Commit the exported JSON and images whenever the manuscript inputs change; CI
checks freshness. The exporter ignores WSL mount-only executable-bit differences,
while refusing content changes in scientific inputs. After the normal Jekyll build,
`node blog/scripts/test_results.js` checks all nine paper headings, saved-source
hashes, useful no-JavaScript content, and the slider/toggle behaviour. It uses the
existing pinned `web/` jsdom dependency. Homepage-only styles and script are loaded
by `preliminary_results: true` in front matter.

Verified on 2026-10-20: production Jekyll build and link checker; nine-card DOM
and source-hash checks; existing ant controls; headless browser checks at 1280px
desktop, 390px mobile and 860px dark mode, including keyboard sliders, the
reference toggle, image loads, overflow and JavaScript-disabled details. Review
captures live in ignored `tmp/homepage-review/`.

The homepage includes three live, deterministic blank-grid ant trails. They pause
offscreen and in hidden tabs, start as still previews with reduced motion enabled,
and stop at 100,000 steps. Play and Start over replay the same rules from blank
grids. The RLRLLL preview does not reach its billion-step column-sweeper transition.
Check dynamics against the sparse oracle and existing web simulator, plus the
animation controls, with `node blog/scripts/test_ants.js` from the repository root
(uses the pinned `web/` jsdom dependency; install with `npm ci --prefix web`).

Maintain the results highlights and current investigations in `index.html` when
the scientific record changes. Evidence links pin the revision containing the
reported results; experiment-page links lead to the evolving record.

## GitHub Pages setup

1. Push this repository to GitHub. In **Settings → Pages → Build and
   deployment → Source**, select **GitHub Actions**.
2. Ensure the default branch is `main` (or adjust the workflow's
   push branches). The first push containing the blog runs the workflow;
   alternatively run **Research blog** manually on the default branch.
3. The workflow builds and checks PRs, and deploys only from the repository's
   default branch. It uses the `github-pages` environment. If environment
   approvals or branch rules are enabled, satisfy them in GitHub.

The workflow uses the pinned Ruby bundle for both local and CI builds. It
gets the site's origin and base path from `actions/configure-pages`, so both
`https://OWNER.github.io/REPO/` and user/organisation sites work. Custom domains
are configured in Pages settings; add `blog/CNAME` if the domain setup requires
it. Feed links and canonical URLs follow the Pages configuration.

Blog, experiment, Python dependency, and workflow changes trigger automatic
builds. This does not run simulations, publish all experiment files, or require a deployment
secret. The workflow needs Pages enabled and the normal `GITHUB_TOKEN`
permissions for Pages deployment.

## Research atlas

`/atlas/` indexes the research by scientific question: current state, best
evidence, counterevidence, open questions and a chronology per topic. It is a
**materialised view, not a place to record work**. `blog/atlas.json` only
curates which experiment bears on which question, in what role, and what
changed; findings and caveats are copied from `experiment-guides.tsv` and claims
from the evidence ledger (`experiments/archive/2026-10-evidence-ledger/results/claims.json`).
Curated prose may not carry measurements (a lint rejects decimals, percentages
and exponent notation; it is a guardrail, not proof). Every tracked experiment must be
filed under a topic or listed under `unfiled` with a reason, so a new experiment
fails the build until it is placed. Each topic shows experiments newer than its
`reviewed` date. States come from a fixed vocabulary defined in the file.

```bash
python3 blog/scripts/atlas.py --check    # validate only
python3 blog/scripts/atlas.py            # write ignored blog/atlas/ and blog/_data/atlas.json
python3 blog/scripts/test_atlas.py
```

Run it after `experiments.py` and before Jekyll (CI does). To change what a
page says, change the underlying record (guide, ledger or experiment), then
rebuild. When a result changes a topic's state, edit `state`, `state_summary`
and `reviewed` in `atlas.json` in the same commit.

## Experiment pages and notebook renders

The preparation script discovers tracked `experiments/<bucket>/<slug>/README.md`
files (buckets `active`, `archive`, `proposed`), excluding internal `_` folders.
Every experiment gets an entry in `/experiments/` and a page at
`/experiments/<slug>/`. The URL omits the bucket, so moving an experiment from
`active/` to `archive/` does not break links to its page; slugs must therefore
be unique across buckets (the script checks). The searchable
index remains usable without JavaScript; JavaScript adds filtering.

Each page opens with an editorial reader guide: an approachable title, the
question, the idea under test, what was learned, and what remains open. These
introductions live in `experiment-guides.tsv`, one row per tracked experiment.
They summarize the cited evidence; they are **not new preregistrations**. Say
explicitly when a folder is a descriptive archive, a pilot, or an unrun plan.
The publisher checks complete guide coverage so a new experiment cannot silently
fall back to an internal README as its introduction. Write plain sentences,
define specialized terms, and check the latest results and corrections before
updating a guide. The evidence column is a repository-relative tracked file.

`experiment-figures.json` selects existing, tracked figures for the introductions
and index thumbnails. Its library gives each image an alt description, a caption
explaining what to look for and what it cannot show, and a tracked source/recipe.
The experiment map selects library entries. Shared figures must be labelled as
context or comparisons rather than implying they are new results of that page.
Only selected images are copied; full-size versions are linked. This step does
not regenerate plots or execute notebooks. Add new measured plots through the
experiment's normal reproducible workflow, then select them here. Both editorial
files and figure recipes join the publication manifest's input hashes.

Below the introduction and figures, an expandable research record includes its README, every tracked `notebook.ipynb` at its root
and every `.ipynb` in its `notebooks/` directory, plus an expandable
`NOTEBOOK.md` lab log when present. Notebook narrative, code, saved figures,
tables, text, and error outputs are rendered with nbconvert. Code inputs are
collapsed individually; outputs stay visible within the expanded notebook. Deep
links open containing sections automatically. Original notebooks can be
downloaded. Missing notebooks and notebooks without saved outputs are labelled.
**No cells are executed**, and original scientific files are never rewritten.

The `blog` dependency group in `pyproject.toml` and `uv.lock` pins nbconvert,
nbformat, and Beautiful Soup independently of the analysis dependencies.
Preparation writes only generated `blog/experiments/` and
`blog/_data/experiments.json`, both ignored by Git. The generated directory
has an ownership marker; the script refuses to replace an unmarked directory.
CI regenerates these files before Jekyll runs. Run preparation before a local
build too, with the **same baseurl** as Jekyll.

Relative experiment and notebook links point to the corresponding site page.
Other repository references point to GitHub at the source revision when
`--repository-url https://github.com/OWNER/REPO` is provided (CI sets this).
Without it, repository-only references retain their labels and show their
source path on hover. Referenced, tracked images are copied; bulk dumps and
untracked files are never copied. Unavailable legacy references are left as
labelled text and listed in `/experiments/manifest.json`. This manifest also
records the source revision and SHA-256 of every rendered input and copied
asset. A render reflects the saved document; it does not verify its claims or
refresh stale notebook results.

Publishing checks (from the repository root under WSL):

```bash
uv run --frozen --only-group blog blog/scripts/test_experiments.py
node blog/scripts/test_experiment.js
```

The fixtures check repeatable output, preserved saved and error outputs,
nested notebooks, source and image links, heading anchors, missing notebooks,
exclusion of untracked/internal files, reader-guide ordering, figure captions
and hashes, and protection of unmarked directories. The JavaScript check uses
the existing `web/` jsdom dependency to verify that deep links reveal collapsed
records and notebook headings.

References: [Jekyll authoring](https://jekyllrb.com/docs/posts/) and
[GitHub's custom Pages workflows](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages).

## Homepage ant gallery

`assets/ants.js` drives the nine blank-grid trails on `index.html`. The pool
contains nine named starting examples plus a deterministic sample of mixed,
primitive rules of lengths 5–12 (384 total, xorshift32 seed `0x20a17`).
The sample is for visual variety, not a census or a measured classification.
Rules are taken in pool order, skipping any already on screen.

A trail pauses for 1.8 seconds before replacement when its extent reaches
256 by 200 cells in either dimension, its visited map reaches 30,000 cells,
or its recent read colours and absolute headings repeat with displacement.
The visual highway heuristic requires at least six cycles over at least
4,096 steps, checking even periods through 1,024 every 256 steps. It can miss
long periods or mistake a long transient for a highway; it does not produce
research results. There is no step limit. Pause and New rules apply to all
nine cards; reduced motion starts paused, and hidden/offscreen pages suspend.

Check with `node blog/scripts/test_ants.js` from the repository root (after
`npm ci --prefix web`). It compares stepping with the independent oracle and
web simulator, exercises replacement and controls, and checks the classic RL
highway against LLRR builder passes. Desktop uses three columns; narrow
screens stack the cards for readable trails.

## Home-page widgets

`assets/ant-explainer.js` ("How an ant works") and `assets/walker-compare.js`
("Four walkers, one start") are dependency-free and hidden until they load.
`node blog/scripts/test_widgets.js` checks them against `web/sim.js` and sparse
oracles, then drives their controls in jsdom; CI runs it with `test_ants.js`.
