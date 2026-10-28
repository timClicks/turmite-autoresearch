"""Run one stage of the return-gates experiment: pilot | controls | confirm.

Run from the repo root inside WSL (needs the release example built):
  uv run experiments/archive/2026-10-kappa-return-gates/scripts/run_stage.py pilot [--threads 6]
Seeds (frozen in README.md): pilot 2026102001-08; controls 2026102051-58 (rotor, rw);
confirmation predictor 2026102101-(2026102100+S) with S from results/seed_count.json,
confirmation target 2026102201-32. Resumable: finished specs carry a .done marker with the config hash.
"""
from pathlib import Path
import argparse, hashlib, json, subprocess, sys
import polars as pl

ROOT = Path(__file__).resolve().parents[4]
EXP = Path(__file__).resolve().parents[1]
BIN = ROOT / "target/release/examples/kappa_return_gates_sampler"
CAP, GRID = 2**29, 4096
BANDS = [(32768, 34816), (131072, 139264)]
SOURCES = ["src/return_gates.rs", "src/field_age.rs", "src/fixed_area.rs", "src/walkers.rs", "examples/kappa_return_gates_sampler.rs"]

ap = argparse.ArgumentParser()
ap.add_argument("stage", choices=["pilot", "controls", "confirm"])
ap.add_argument("--threads", type=int, default=6)
a = ap.parse_args()

rules = pl.read_csv(EXP / "results/cohort.csv")["base"].to_list()
assert len(rules) == 24
roles = {}
if a.stage == "pilot":
    specs = [(f"{r}@{s}", "pilot", r, s) for r in rules for s in range(2026102001, 2026102009)]
elif a.stage == "controls":
    specs = [(f"{k}:{s}", "control", k, s) for k in ("rotor", "rw") for s in range(2026102051, 2026102059)]
else:
    S = json.loads((EXP / "results/seed_count.json").read_text())["S_pred"]
    assert S in (8, 16, 32, 64)
    specs = [(f"{r}@{s}", "predictor", r, s) for r in rules for s in range(2026102101, 2026102101 + S)]
    specs += [(f"{r}@{s}", "target", r, s) for r in rules for s in range(2026102201, 2026102233)]
src_hashes = {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in SOURCES}
cfg_hash = hashlib.sha256(json.dumps([src_hashes, CAP, GRID, BANDS], sort_keys=True).encode()).hexdigest()[:16]
out = EXP / "dumps" / a.stage
out.mkdir(parents=True, exist_ok=True)
cmd = [str(BIN), str(out), str(CAP), str(GRID), ",".join(f"{lo}-{hi}" for lo, hi in BANDS), cfg_hash, str(a.threads)]
log = EXP / "results" / f"{a.stage}_run.log"
with log.open("a") as lf:
    r = subprocess.run(cmd, input="\n".join(s[0] for s in specs) + "\n", text=True, stderr=lf)
assert r.returncode == 0, "sampler failed; see " + str(log)
frames = []
for spec, role, rule, seed in specs:
    f = out / (spec.replace(":", "_").replace("@", "_") + ".gates.csv")
    d = pl.read_csv(f, schema_overrides={"ext_boundary": pl.Int64, "hole_boundary": pl.Int64})
    st = pl.read_csv(out / (f.name.replace("gates", "status")))
    frames.append(d.with_columns(pl.lit(role).alias("role"), pl.lit(rule).alias("rule"), pl.lit(seed).alias("seed"), pl.lit(st["stop"][0]).alias("stop"), pl.lit(st["t_final"][0]).alias("t_final")))
runs = pl.concat(frames)
runs.write_csv(EXP / "results" / f"{a.stage}_runs.csv")
manifest = dict(
    command=f"uv run experiments/archive/2026-10-kappa-return-gates/scripts/run_stage.py {a.stage} --threads {a.threads}",
    sampler_command=" ".join(cmd[:6]) + f" {a.threads}  (specs on stdin)",
    git_commit=subprocess.check_output(["git", "rev-parse", "HEAD"], text=True, cwd=ROOT).strip(),
    source_sha256=src_hashes, config_hash=cfg_hash, cap=CAP, grid=GRID, bands=BANDS,
    cohort_sha256=hashlib.sha256((EXP / "results/cohort.csv").read_bytes()).hexdigest(),
    n_specs=len(specs), seeds={role: sorted({s for _, rl, _, s in specs if rl == role}) for role in {x[1] for x in specs}},
    runs_csv_sha256=hashlib.sha256((EXP / "results" / f"{a.stage}_runs.csv").read_bytes()).hexdigest(),
)
(EXP / "results" / f"{a.stage}_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
print(runs.group_by("role", "stop").len())
