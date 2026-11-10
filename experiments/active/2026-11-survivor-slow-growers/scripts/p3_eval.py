"""P3 evaluation: side(2e11)/side(1e11) for the 8 sampled slow survivors (stdlib only).
Reads results/p3/<rule>.csv (2e11 re-runs) and results/classes.csv (census 1e11 sides).
Writes results/p3_analysis.txt. Registered threshold: ratio <= 1.05, no escape, no highway."""
import csv, math, pathlib
E = pathlib.Path(__file__).resolve().parents[1]
R = E / "results"
cls = {r["rule"]: r for r in csv.DictReader(open(R / "classes.csv"))}
out, fails = [], 0
out.append("== P3: side(2e11)/side(1e11), registered: all <= 1.05, no escape, no highway (cube root predicts 2^(1/3) = 1.26)")
for rule in (R / "p3_sample.txt").read_text().split():
    row = next(csv.DictReader(open(R / "p3" / f"{rule}.csv")))
    s2 = max(int(row["width"]), int(row["height"]))
    s1 = int(cls[rule]["side_1e11"])
    ratio = s2 / s1
    hw = bool(row["period"]) or row["stop"] != "budget"
    ok = ratio <= 1.05 and not hw
    fails += not ok
    g = math.log10(ratio) / math.log10(2)
    out.append(f"{rule}: stop={row['stop']} steps={row['steps']} side 1e11 {s1} -> 2e11 {s2}, ratio {ratio:.4f}, "
               f"local exponent {g:.3f}, g11 {cls[rule]['g11']}, highway/escape {hw} -> {'ok' if ok else 'FAIL'}")
out.append(f"P3 -> {'HOLD' if fails == 0 else 'FAIL'} ({fails} of 8 outside the registered bound)")
(R / "p3_analysis.txt").write_text("\n".join(out) + "\n")
print("\n".join(out))
