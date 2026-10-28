# /// script
# dependencies = ["polars", "numpy", "scipy"]
# ///
"""Cohort, arm and seed manifest for kappa-prefix-exposure. Uses only W3c's pre-existing per-rule
labels (stationary / nonstationary, attainable); no mutant has been simulated when this runs.

usage (repo root): uv run experiments/archive/2026-10-kappa-prefix-exposure/scripts/select_cohort.py
"""
import hashlib, json, subprocess, sys
from pathlib import Path

import polars as pl

ROOT = Path(__file__).resolve().parents[4]
EXP = Path(__file__).resolve().parents[1]
RS = ROOT / "experiments/archive/2026-10-kappa-rule-space"
sys.path.insert(0, str(ROOT / "experiments" / "_lib"))
from analyse_probe import per_rule  # noqa: E402

SALT = "kpe-2026-10-15"
PILOT_SEEDS = [2026101570001 + i for i in range(4)]
CONF_SEEDS = [2026101571001 + i for i in range(64)]
PRED_SEEDS, TGT_SEEDS = CONF_SEEDS[:32], CONF_SEEDS[32:]


def h(*parts) -> str:
    return hashlib.sha256(":".join((SALT,) + tuple(map(str, parts))).encode()).hexdigest()


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


# ---- pre-existing labels: the W3c recipe, copied from w3c_analyse.py (core band, >= 6 runs, |median g_k| < 0.05)
raw = pl.read_csv(RS / "dumps" / "w3c_probe.csv")
r = per_rule(raw).with_columns(base=pl.col("rule").str.split("@").list.first())
a22 = raw.filter(pl.col("k") == 22).select("rule", lnA22=pl.col("area").log())
r = r.join(a22, on="rule", how="left")
core = r.filter(pl.col("alpha_w").is_between(0.25, 0.42) & (pl.col("kappa") > 0))
rules = (core.group_by("base").agg(n_runs=pl.len(), lnk=pl.col("kappa").log().mean(), g_k=pl.col("g_k").median(),
                                   lnA22=pl.col("lnA22").mean(), kappa=pl.col("kappa").mean())
         .filter(pl.col("n_runs") >= 6).sort("base")
         .with_columns(n=pl.col("base").str.len_chars(), family=pl.col("base").str.slice(0, 5),
                       label=pl.when(pl.col("g_k").abs() < 0.05).then(pl.lit("stationary")).otherwise(pl.lit("nonstationary"))))
n_sampled = len(RS.joinpath("results", "w3c_rules.txt").read_text().split())

# ---- families (R + 4 letters) -> development / validation by hash rank: validation tests prefix families unseen in development
fams = sorted(rules["family"].unique().to_list(), key=lambda f: h("family", f))
dev_f, val_f = set(fams[: len(fams) // 2]), set(fams[len(fams) // 2:])


def draw(side_fams, label, quota_by_n):
    """Round-robin over the side's families in hash order, within a family by rule hash, until the
    per-length quotas are filled. Deterministic; no outcome of a mutant is used."""
    pool = rules.filter(pl.col("family").is_in(sorted(side_fams)) & (pl.col("label") == label))
    by_f = {f: sorted(pool.filter(pl.col("family") == f)["base"].to_list(), key=lambda b: h("pick", b))
            for f in sorted(side_fams, key=lambda f: h("family", f))}
    order, depth = [], 0
    while any(depth < len(v) for v in by_f.values()):
        order += [v[depth] for v in by_f.values() if depth < len(v)]
        depth += 1
    left, chosen = dict(quota_by_n), []
    for b in order:
        n = len(b)
        if left.get(n, 0) > 0:
            chosen.append(b)
            left[n] -= 1
    return chosen, {n: q for n, q in left.items() if q > 0}


rows, shortfalls = [], {}
for side, sf in (("dev", dev_f), ("val", val_f)):
    st, s1 = draw(sf, "stationary", {13: 5, 14: 5})
    ns, s2 = draw(sf, "nonstationary", {13: 1, 14: 1})
    shortfalls[side] = {"stationary": s1, "nonstationary": s2}
    for i, b in enumerate(st + ns):
        rows.append(dict(side=side, idx=i, base=b))
coh = pl.DataFrame(rows).join(rules, on="base").sort("side", "idx").with_columns(pl.col(pl.Float64).round(6))  # rounded: float sums are not bit-stable across runs


def positions(i: int, n: int):
    """Positions 1 and 2 for every base (the W6 matched-area reanalysis, committed 3d00123 after this
    experiment was scaffolded, localised the early effect there); one mid letter (3..7) and two late letters
    (8..n-1), balanced over the side-local index i."""
    big_l = n - 8
    mid = 3 + (i % 5)
    late = [8 + (i % big_l), 8 + ((i + (big_l + 1) // 2) % big_l)]
    return mid, late


def flip(rule: str, j: int) -> str:
    return rule[:j] + ("R" if rule[j] == "L" else "L") + rule[j + 1:]


arms = []
for row in coh.iter_rows(named=True):
    mid, late = positions(row["idx"], row["n"])
    arms.append(dict(side=row["side"], base=row["base"], arm="base", pos=-1, rule=row["base"]))
    for name, j in (("a1", 1), ("a2", 2), ("m1", mid), ("l1", late[0]), ("l2", late[1]), ("p0", 0)):
        arms.append(dict(side=row["side"], base=row["base"], arm=name, pos=j, rule=flip(row["base"], j)))
arms = pl.DataFrame(arms)
assert arms.group_by("base").agg(pl.col("rule").n_unique()).filter(pl.col("rule") != 7).height == 0, "arms must be distinct"


def root_len(s):
    n = len(s)
    return next((p for p in range(1, n) if n % p == 0 and s[:p] * (n // p) == s), n)


arms = arms.with_columns(primitive=pl.col("rule").map_elements(lambda s: root_len(s) == len(s), return_dtype=pl.Boolean))

# ---- seed audit: no other file in the repo mentions any of these seed strings
used = [str(s) for s in PILOT_SEEDS + CONF_SEEDS]
hits = []
for p in list(ROOT.glob("experiments/**/*")) + list(ROOT.glob("src/**/*.rs")) + list(ROOT.glob("examples/*.rs")) + list(ROOT.glob("notes/*")) + list(ROOT.glob("research-outputs/**/*.typ")):
    if not p.is_file() or EXP in p.parents or any(part.startswith("dumps") or part == "__pycache__" for part in p.parts) or p.stat().st_size > 5_000_000 or p.suffix in {".pdf", ".png", ".u32"}:
        continue
    try:
        txt = p.read_text(errors="ignore")
    except OSError:
        continue
    if any(s in txt for s in used) or "20261015700" in txt or "20261015710" in txt:
        hits.append(str(p.relative_to(ROOT)))

res = EXP / "results"
coh.write_csv(res / "cohort.csv")
arms.write_csv(res / "arms.csv")


def specs(side, seeds):
    a = arms.filter(pl.col("side").is_in(side))
    return [f"{rule}@{s}" for rule in sorted(set(a["rule"].to_list())) for s in seeds]


# the same mutant can be reached from two bases; a spec is simulated once and credited to both
lists = {"specs_pilot_dev.txt": specs(["dev"], PILOT_SEEDS), "specs_confirm_dev.txt": specs(["dev"], CONF_SEEDS),
         "specs_confirm_val.txt": specs(["val"], CONF_SEEDS)}
for name, v in lists.items():
    (res / name).write_text("\n".join(v) + "\n")

git = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
man = dict(
    cmd="uv run experiments/archive/2026-10-kappa-prefix-exposure/scripts/select_cohort.py", git_head=git, working_tree="dirty (other experiments)",
    salt=SALT, w3c_rules_sampled=n_sampled, usable_rules=rules.height, usable_stationary=int((rules["label"] == "stationary").sum()),
    usable_nonstationary=int((rules["label"] == "nonstationary").sum()), dev_families=sorted(dev_f), val_families=sorted(val_f),
    shortfalls=shortfalls, pilot_seeds=PILOT_SEEDS, pred_seeds=PRED_SEEDS, tgt_seeds=TGT_SEEDS,
    seed_audit_files_mentioning_namespace=hits,
    non_primitive_arm_rules=arms.filter(~pl.col("primitive"))["rule"].to_list(),
    inputs={"dumps/w3c_probe.csv (gitignored)": sha256_file(RS / "dumps" / "w3c_probe.csv"), "results/w3c_rules.txt": sha256_file(RS / "results" / "w3c_rules.txt"),
            "analyse_probe.py": sha256_file(ROOT / "experiments" / "_lib" / "analyse_probe.py")},
    outputs={n: hashlib.sha256((res / n).read_bytes()).hexdigest() for n in ["cohort.csv", "arms.csv", *lists]},
    spec_counts={n: len(v) for n, v in lists.items()},
)
(res / "selection_manifest.json").write_text(json.dumps(man, indent=1, sort_keys=True) + "\n")
pl.Config.set_tbl_rows(40); pl.Config.set_tbl_cols(14)
print(coh.select("side", "idx", "base", "n", "family", "label", "n_runs", "lnk", "g_k"))
print(json.dumps({k: man[k] for k in ["usable_rules", "usable_stationary", "usable_nonstationary", "shortfalls", "dev_families", "val_families",
                                       "seed_audit_files_mentioning_namespace", "non_primitive_arm_rules", "spec_counts"]}, indent=1))
