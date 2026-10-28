# /// script
# dependencies = ["polars", "numpy", "scipy"]
# ///
"""Compare faster ingestion against the already-produced primary summaries."""
import numpy as np
import polars as pl
from analyse import EXP, summarise

fresh, checks = summarise("prod16")
old = pl.read_csv(EXP / "results/rule_summary.prod16.csv")
assert fresh.columns == old.columns and fresh.shape == old.shape
for col in fresh.columns:
    if fresh[col].dtype.is_numeric():
        np.testing.assert_allclose(fresh[col].to_numpy(), old[col].to_numpy(), rtol=1e-12, atol=1e-12)
    else:
        np.testing.assert_array_equal(fresh[col].to_numpy(), old[col].to_numpy())
print("All primary summary rows agree with the original loader to 1e-12;", checks)
