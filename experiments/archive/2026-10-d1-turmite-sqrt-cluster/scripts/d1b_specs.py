# /// script
# dependencies = ["numpy"]
# ///
import numpy as np
rng = np.random.default_rng(20261013)
ids = rng.integers(0, 24 ** 6, 20000)
open("experiments/archive/2026-10-d1-turmite-sqrt-cluster/results/d1b_specs.txt", "w").write("\n".join(f"tm:2:3:{i}" for i in ids) + "\n")
