"""Reproduce registered G1 archival comparison; no stochastic operations."""
from pathlib import Path
import csv, hashlib, json, statistics, subprocess
ROOT = Path(__file__).resolve().parents[4]
EXP = Path(__file__).resolve().parents[1]
BASE = ROOT / 'experiments/archive/2026-10-highways-unresolved-rules-1e10-1e11/results'
inputs = []
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):
    inputs.append(p)
    with p.open() as f: return list(csv.DictReader(f))
def signature(eta, x, y): return eta < 8 and max(x,y)/min(x,y) >= 20
assert signature(4,40,10000)
assert not signature(4,100,100)
assert not signature(1000,40,10000)
rows = read(EXP/'results/g1_ribbon.csv')
fine=[]; prev=0
for r in rows:
    t=int(r['t_end']); dt=t-prev; prev=t
    if dt != 1000000: continue
    x=int(r['new_x1'])-int(r['new_x0'])+1
    y=int(r['new_y1'])-int(r['new_y0'])+1
    eta=float(r['steps_per_new'])
    fine.append(dict(t=t,eta=eta,thin=min(x,y),aspect=max(x,y)/min(x,y),S=signature(eta,x,y)))
onset=min(r['t'] for r in fine if r['eta']<10)
breakout=[r for r in fine if r['eta']<10]
before=[r for r in fine if r['t']<onset]
def frac(rs,key): return sum(r[key] for r in rs)/len(rs) if rs else None
summary={'registration':'2026-10-15 21:22 NZDT','base_commit':'da88e61b690507526ba4e2a2c017d9c7941beb91','command':'uv run experiments/archive/2026-10-g1-ribbon-breakout/scripts/compare_survivors.py','seed':None,'start':'blank board, north','calibration':'three synthetic geometry/efficiency controls passed','trace':{'complete_fine_windows':len(fine),'breakout_windows':len(breakout),'pre_windows':len(before),'first_breakout_window_end':onset,'S_breakout_fraction':frac(breakout,'S'),'S_before_fraction':frac(before,'S'),'median_eta':statistics.median(r['eta'] for r in breakout),'median_thin':statistics.median(r['thin'] for r in breakout),'thin_le12_fraction':sum(r['thin']<=12 for r in breakout)/len(breakout)},'census':{}}
allrows=[]; previous={}
for decade in ('h1e10','h1e11'):
    cohort=[]
    for p in sorted((BASE/decade).glob('chunk_*.csv')):
        marker=p.with_suffix('.done')
        if marker.exists():
            inputs.append(marker); cohort.extend(read(p))
    assert len({r['rule'] for r in cohort})==len(cohort)
    groups={}
    for r in cohort:
        group='highway' if r['period'] else ('no_highway_escape' if r['stop']=='escaped' else 'budget')
        w,h=int(r['width']),int(r['height']); aspect=max(w,h)/min(w,h)
        old=previous.get(r['rule'])
        out=dict(decade=decade,rule=r['rule'],group=group,steps=int(r['steps']),width=w,height=h,aspect=aspect,elongated=aspect>=2,extent_expansion=max(w,h)/max(int(old['width']),int(old['height'])) if old else '')
        allrows.append(out); groups.setdefault(group,[]).append(out)
    summary['census'][decade]={'N':len(cohort),'groups':{g:{'N':len(rs),'elongated_fraction':frac(rs,'elongated'),'median_aspect':statistics.median(r['aspect'] for r in rs)} for g,rs in groups.items()}}
    previous={r['rule']:r for r in cohort}
summary['trace']['S_prediction_pass']=frac(breakout,'S')>=.9 and frac(before,'S')<=.05
summary['transfer_prediction_pass']={d:s['groups']['no_highway_escape']['elongated_fraction']>=.75 for d,s in summary['census'].items()}
inputs.extend([ROOT/'examples/ribbon_trace.rs',ROOT/'examples/escape_trace.rs',ROOT/'src/bin/sweep_lean.rs',ROOT/'experiments/archive/2026-10-c2-arrow-bias/results/escape_trace.txt'])
summary['input_sha256']={str(p.relative_to(ROOT)):sha(p) for p in sorted(set(inputs))}
summary['script_sha256']=sha(Path(__file__))
with (EXP/'results/survivor_geometry.csv').open('w',newline='') as f:
    writer=csv.DictWriter(f,fieldnames=list(allrows[0])); writer.writeheader(); writer.writerows(allrows)
(EXP/'results/survivor_comparison.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n')
print(json.dumps({k:v for k,v in summary.items() if k not in ('input_sha256','script_sha256')},indent=2))
