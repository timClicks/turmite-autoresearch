# /// script
# dependencies = ["polars", "numpy"]
# ///
"""POST HOC: identify the kept hex rules with extreme 1/c and print their k=20..26 windows. usage: uv run .../outlier.py"""
import contextlib, io, runpy
from pathlib import Path
import numpy as np
import polars as pl
with contextlib.redirect_stdout(io.StringIO()):
    ns = runpy.run_path(str(Path(__file__).with_name("analyse.py")))
kept, ants, R = ns["kept"], ns["ants"], ns["R"]
k = kept.with_columns(invc=1 / pl.col("c")).sort("invc", descending=True).head(4)
print(k.select("lattice", "spec", "lead", "invc", "a", "beta", "alpha_w", "g_k", "kratio"))
spec = k["spec"][0]
w = ants.filter((pl.col("spec") == spec) & (pl.col("k") >= 20)).with_columns(c=pl.col("new_cells") / pl.col("boundary_steps"), kappa_B=pl.col("boundary_steps") / 2.0 ** pl.col("k"))
print(w.select("k", "area", "perimeter", "new_cells", "boundary_steps", "c", "width", "height"))
