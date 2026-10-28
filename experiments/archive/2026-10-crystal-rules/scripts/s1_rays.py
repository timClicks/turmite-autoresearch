# /// script
# dependencies = ["polars", "numpy"]
# ///
"""S1 ray anatomy summary (README 'S1 ray anatomy: operationalisation', registered before any crystal-rule ray CSV existed).
Reads dumps/rays_<RULE>.csv (gitignored; produced by examples/crystal_rules_rays.rs), writes results/s1_rays.txt.
usage (repo root): uv run experiments/archive/2026-10-crystal-rules/scripts/s1_rays.py"""
import subprocess
from pathlib import Path
import numpy as np, polars as pl

E = Path(__file__).resolve().parents[1]
RULES = ["RLLLLRRL", "LRRRRRLLR", "RLLLLLLLRRLRR", "RLRRRL"]
MINLEN = 64
out = ["# s1 rays; commit " + subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip(), f"# rays with length >= {MINLEN} cells; 2^28 steps, board 16384, blank start"]
verdict = {}
for r in RULES:
    d = pl.read_csv(E / "dumps" / f"rays_{r}.csv", schema_overrides={"motif": pl.String}).filter(pl.col("length_cells") >= MINLEN)
    out.append(f"\n## {r}: rays >= {MINLEN} cells: {d.height}")
    if d.height == 0:
        out.append("  no rays"); verdict[r] = None; continue
    L = d["length_cells"].to_numpy().astype(float); tot = L.sum()
    out.append(f"  total ray length {int(tot)} cells; median {np.median(L):.0f}, max {int(L.max())}; steps/cell median {d['steps_per_cell'].median():.2f} (range {d['steps_per_cell'].min():.2f}-{d['steps_per_cell'].max():.2f})")
    bins = np.floor(np.log2(L)).astype(int)
    out.append("  length log2-bins (count): " + ", ".join(f"2^{b}:{int((bins == b).sum())}" for b in sorted(set(bins))))
    ap = d.filter(pl.col("period") == 0)
    out.append(f"  aperiodic rays: {ap.height} ({ap['length_cells'].sum() / tot:.3f} of length)")
    per = d.filter(pl.col("period") > 0).group_by("motif", "period").agg(pl.col("length_cells").sum().alias("len"), pl.len().alias("n")).sort("len", descending=True)
    sh = per["len"].to_numpy() / tot
    for row, s in list(zip(per.iter_rows(named=True), sh))[:6]:
        out.append(f"  motif p={row['period']:3d} share {s:.3f} rays {row['n']:5d}  {row['motif'][:48]}")
    n1 = int((sh >= 0.01).sum())
    top, top_p = (sh[0], int(per["period"][0])) if per.height else (0.0, 0)
    out.append(f"  distinct motifs with >=1% of length: {n1}; dominant share {top:.3f}, dominant p {top_p}")
    rev = float((d["rev_frac"].to_numpy() * L).sum() / tot); same = float((d["same_frac"].to_numpy() * L).sum() / tot)
    out.append(f"  length-weighted reverse-overlap {rev:.3f}, same-heading overlap {same:.3f}")
    hd = d.group_by("hx", "hy").agg(pl.col("length_cells").sum().alias("len")).sort("len", descending=True)
    out.append("  heading share of length: " + ", ".join(f"({a:+d},{b:+d}) {l / tot:.2f}" for a, b, l in hd.iter_rows()))
    tc = d.group_by("term_colour").agg(pl.len().alias("n")).sort("n", descending=True)
    out.append("  terminating colour counts: " + ", ".join(f"{c}:{n}" for c, n in tc.iter_rows()))
    verdict[r] = dict(top=top, p=top_p, n1=n1, rev=rev)
# EXPLORATORY (not registered; added after seeing the colour-level motifs): collapse colours to the turn letter the rule assigns them.
out.append("\n== EXPLORATORY: motifs after mapping colour -> turn letter (R/L); not a registered test ==")
for r in RULES:
    d = pl.read_csv(E / "dumps" / f"rays_{r}.csv", schema_overrides={"motif": pl.String}).filter((pl.col("length_cells") >= MINLEN) & (pl.col("period") > 0))
    if d.height == 0:
        continue
    tot = d["length_cells"].sum(); acc = {}
    for m, ln in zip(d["motif"], d["length_cells"]):
        w = "".join(r[ord(ch) - 48] for ch in m)
        acc[w] = acc.get(w, 0) + ln
    canon = {}
    for w, ln in acc.items():
        c = min(w[i:] + w[:i] for i in range(len(w)))
        canon[c] = canon.get(c, 0) + ln
    s = sorted(canon.items(), key=lambda kv: -kv[1])
    out.append(f"{r}: distinct turn-letter motifs {len(s)}; " + ", ".join(f"{w[:12]}:{ln / tot:.3f}" for w, ln in s[:5]))
out.append("\n== registered verdicts (P2 H-ray, P4 H-reverse); control RLRRRL reported, not judged ==")
for r in RULES[:3]:
    v = verdict[r]
    if v is None:
        out.append(f"{r}: no rays >= {MINLEN} cells; P2/P4 not evaluable"); continue
    p2 = v["top"] >= 0.8 and 4 <= v["p"] <= 40
    p2f = v["n1"] > 5 or v["p"] > 100
    out.append(f"{r}: P2 {'HELD' if p2 else ('FALSIFIED' if p2f else 'NOT HELD (not falsified)')} (dominant share {v['top']:.3f}, p={v['p']}, motifs>=1% {v['n1']}); "
               f"P4 {'HELD (<=0.20)' if v['rev'] <= 0.2 else ('H-reverse supported (>0.50)' if v['rev'] > 0.5 else 'in between')} (rev {v['rev']:.3f})")
(E / "results" / "s1_rays.txt").write_text("\n".join(out) + "\n"); print("\n".join(out))
