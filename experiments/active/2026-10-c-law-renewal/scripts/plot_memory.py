"""Render the committed excluded-pilot sufficiency tests; no fitting."""
from pathlib import Path
import argparse
import hashlib
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[4]
EXP = Path(__file__).resolve().parents[1]
source = EXP / "results/memory_report.json"
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--replace",action="store_true",help="replace only this experiment's inspected generated figure")
args = parser.parse_args()
report = json.loads(source.read_text())
fig, axes = plt.subplots(1,2,figsize=(10.8,4),layout="constrained")
colors = ["#007f86","#bd7919","#7853a4","#b4483e"]
tops = [0.0,0.0]
for x,radius in enumerate([0,1,2,4,8]):
    rows = [r for r in report["comparisons"] if r["mode"]==f"uniform:{radius}" and r["eligible"]]
    for panel,key in enumerate(["abs_log_error","max_budget_error"]):
        values = []
        for j,row in enumerate(rows):
            value = row[key]
            if value is None:
                axes[panel].text(x,0.98,"infinite",transform=axes[panel].get_xaxis_transform(),ha="center",va="top",fontsize=8)
                continue
            values.append(value)
            tops[panel] = max(tops[panel],value)
            axes[panel].scatter(x+(j-3.5)*0.035,value,s=32,color=colors[row["lead"]-1],alpha=.8)
        if values:
            axes[panel].plot([x-.17,x+.17],[np.median(values)]*2,color="#222",lw=2.5)
        axes[panel].text(x,-0.17,f"n={len(rows)}",transform=axes[panel].get_xaxis_transform(),ha="center",fontsize=8)
for panel,ax in enumerate(axes):
    ax.set_xticks(range(5),["0","1","2","4","8"])
    ax.set_xlabel("Retained colour radius (Chebyshev cells)",labelpad=20)
    ax.set_yscale("symlog",linthresh=.01)
    ax.set_ylim(0,tops[panel]*1.25)
    ax.grid(axis="y",alpha=.2)
    ax.spines[["top","right"]].set_visible(False)
axes[0].set_title("Total birth efficiency can look close")
axes[0].set_ylabel("Absolute ln(c model / c full)")
axes[0].axhline(.1,color="#555",ls="--",lw=1,label="M1 median limit")
axes[0].axhline(.25,color="#888",ls=":",lw=1,label="M1 maximum limit")
axes[0].legend(fontsize=8)
axes[1].set_title("The return budget remains wrong")
axes[1].set_ylabel("Largest category error (reads per birth)")
axes[1].axhline(.2,color="#555",ls="--",lw=1,label="M2 median limit")
axes[1].legend(fontsize=8)
for lead,color in enumerate(colors,1):
    axes[1].scatter([],[],color=color,label=f"lead {lead}")
handles,labels=axes[1].get_legend_handles_labels()
fig.legend(handles[-4:],labels[-4:],loc="outside lower center",ncol=4,frameon=False,fontsize=9)
fig.suptitle("Excluded pilot: 4 rules × 2 seeds | Points: paired runs | Black bars: medians",fontsize=11)
out = EXP / "results/memory_pilot.png"
if out.exists() and not args.replace: raise RuntimeError("refusing to overwrite existing figure; inspect then use --replace")
fig.savefig(out,dpi=180,metadata={"Software":"matplotlib; scripts/plot_memory.py","Description":f"Input SHA256 {hashlib.sha256(source.read_bytes()).hexdigest()}; excluded pilot only"})
plt.close(fig)
print(out.relative_to(ROOT))
