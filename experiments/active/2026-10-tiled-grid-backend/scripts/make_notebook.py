"""Build and execute notebook.ipynb (reads only committed results/). Run from the repository root:
UV_PROJECT_ENVIRONMENT=<dir outside the checkout if needed> uv run --frozen experiments/active/2026-10-tiled-grid-backend/scripts/make_notebook.py
"""
from pathlib import Path

import nbformat
from nbclient import NotebookClient

root = Path(__file__).resolve().parents[1]
nb = nbformat.v4.new_notebook()
md, code = nbformat.v4.new_markdown_cell, nbformat.v4.new_code_cell
nb.cells = [
    md(
        "# Tiled CPU grid backend for the lean ant: what it saves and what it costs\n\n"
        "**Question.** `sweep_lean`'s dense grid writes `(size+2)^2` bytes per worker per rule. Does a tiled grid "
        "(sparse 64x64 tiles; bounded cache; packed or LZ4-compressed inactive tiles) shrink the process at an acceptable "
        "throughput cost, with *identical* output?\n\n"
        "**Assumptions.** Same bounded board and escape semantics as dense; workloads are five census rules used as workloads, "
        "not as subjects (no scientific claim about them); one machine (WSL2, Xeon W-2125), single thread, shared with another "
        "contributor; dense throughput is noisy to ~20%.\n\n"
        "Predictions and adoption criteria were registered in `README.md` before timing; this notebook only reads the committed "
        "`results/` and agrees with the README's Results section."
    ),
    code(
        "from pathlib import Path\n"
        "import json, polars as pl\n"
        "res = Path('..') / 'results' if Path('../results').exists() else Path('results')\n"
        "prov = (res / 'runs_provenance.txt').read_text().splitlines()\n"
        "print('\\n'.join(l for l in prov if l.startswith(('date','uname','cpu','rustc','bench commit','loadavg')) or 'sweep_lean' in l))\n"
        "print((res / 'runs_d_provenance.txt').read_text().splitlines()[0:9][-3:])"
    ),
    md("## Exactness gate\nEvery benchmark run's CSV was compared byte-for-byte with the dense run of the same repetition."),
    code(
        "ident = pl.concat([pl.read_csv(res / d / 'identity.tsv', separator='\\t', has_header=False, new_columns=['wl','cfg','rep','same']) for d in ('runs','runs_d')])\n"
        "print(ident.height, 'runs;', ident.filter(pl.col('same') != 1).height, 'differ from dense')"
    ),
    md("## Memory and throughput (medians over repetitions)\nRatios against dense are within noise unless they differ from 1 by more than ~1.2x."),
    code(
        "a = pl.read_csv(res / 'summary.csv')\n"
        "cols = ['wl','cfg','reps','sps_med','tput_vs_dense','rss_med','rss_vs_dense','rss_vs_B6','transitions_per_step','misses','evictions','end_tiles']\n"
        "with pl.Config(tbl_rows=60, tbl_cols=20, tbl_width_chars=200):\n"
        "    print(a.select(cols).with_columns(pl.col(pl.Float64).round(3)))"
    ),
    md("## Stage D (LZ4 on packed tiles), separate batch with its own dense/B6/C1024 references"),
    code(
        "d = pl.read_csv(res / 'summary_runs_d.csv')\n"
        "with pl.Config(tbl_rows=60, tbl_cols=20, tbl_width_chars=200):\n"
        "    print(d.select(cols).with_columns(pl.col(pl.Float64).round(3)))"
    ),
    md("## Would block compression pay? (criterion A5, per-tile deflate/xz on real canonical payloads)"),
    code(
        "ce = json.loads((res / 'compress_estimate.json').read_text())\n"
        "for r in ce: print(r['rule'], 'tiles', r['tiles'], 'packed', r['packed_total_bytes'], 'deflate9 x', r['deflate9']['ratio_vs_packed'], 'xz6 x', r['xz6']['ratio_vs_packed'])\n"
        "print(open(res / 'codec_bench.tsv').read())"
    ),
    md(
        "## What this does and does not show\n"
        "* Exact: all benchmark runs are byte-identical to dense; the oracle tests compare whole states.\n"
        "* Sparse tiles: ~0.1x dense RSS on compact/thin workloads, 0.003x on a 65536 board; 12% on a pattern that fills the board.\n"
        "* Packing alone saves 33% on the large structured footprint with a big cache and thrashes with a small one.\n"
        "* LZ4 gives 0.19x dense on the structured W3 only (one rule); chaotic W1 compresses ~2x and is small anyway.\n"
        "* Not shown: multi-thread behaviour, other CPUs, chaotic rules at 1e10 steps, tile-offset effects, probe memory.\n\n"
        "**Caveats.** Dense is noisy to ~20% in this shared environment; 'tiled is faster than dense' is weak evidence and an "
        "untested cache-layout hypothesis. **Next steps:** tiled probe; tile-offset ablation for compact starts."
    ),
]
NB = root / "notebook.ipynb"
NotebookClient(nb, timeout=600, kernel_name="python3", resources={"metadata": {"path": str(root / "scripts")}}).execute()
nbformat.write(nb, NB)
print("wrote", NB)
