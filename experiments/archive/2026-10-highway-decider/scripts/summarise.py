"""Summarise results/decide_all.csv (registered quantities D1, D3-C4, D4, D5).  usage: python3 summarise.py [decide_all.csv]"""
import collections
import csv
import sys

rows = list(csv.DictReader(open(sys.argv[1] if len(sys.argv) > 1 else "decide_all.csv")))
rules = collections.OrderedDict()
for r in rows:
    rules.setdefault(r["rule"], []).append(r)
print("rules", len(rules), "rows", len(rows))
pre_cert = [r for r in rows if r["K"] == "pre" and r["ok"] == "True"]
print("C4 pre-onset certificates:", len(pre_cert), [(r["rule"], r["t"]) for r in pre_cert[:5]])
oracle_bad = [r for r in rows if r["oracle"] == "False"]
print("D4 oracle False rows:", len(oracle_bad), "of", len(rows), "; error rows:", sum(r["ok"] == "error" for r in rows))
first = collections.Counter()
uncert = []
byK = collections.Counter()
areas = []
for rule, rs in rules.items():
    ks = [r for r in rs if r["K"] != "pre"]
    ok = [r for r in ks if r["ok"] == "True"]
    for r in ok:
        byK[r["K"]] += 1
    if ok:
        first[ok[0]["K"]] += 1
        areas.append(int(ok[0]["area"]))
    else:
        uncert.append((rule, [(r["K"], r["clause"]) for r in ks]))
n, nc = len(rules), len(rules) - len(uncert)
print(f"D1 certified at some K: {nc} of {n} ({nc / n:.4f})")
print("first K that passes:", dict(first))
print("passes per K:", dict(byK))
if areas:
    areas.sort()
    print("window area of the first passing K: min", areas[0], "median", areas[len(areas) // 2], "max", areas[-1])
print("D5 uncertified rules:", len(uncert))
for u in uncert[:40]:
    print("  ", u[0], u[1][:5])
cl = collections.Counter(c for _, l in uncert for _, c in l)
print("clauses among uncertified rows:", dict(cl))
