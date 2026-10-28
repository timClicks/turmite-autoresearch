from pathlib import Path
import json,hashlib
import numpy as np
import polars as pl
root=Path(__file__).resolve().parents[4]; exp=root/'experiments/archive/2026-10-single-cell-gates'; out=exp/'results'
df=pl.concat([pl.read_csv(p) for p in sorted((out/'raw').glob('*.rep.csv')) if p.stat().st_size > 110])
dep=pl.concat([pl.read_csv(p) for p in sorted((out/'raw').glob('*.dep.csv')) if p.stat().st_size > 145])
assert dep['live_ok'].min()==1
controls=df.filter(pl.col('arm').is_in(['sham','offpath']) | pl.col('spec').str.starts_with('rw:'))
assert controls.filter((pl.col('arm')!='missing') & (pl.col('ident')!=1)).height==0
rows=[]
for r in df.filter(pl.col('arm').is_in(['gate','matched'])).iter_rows(named=True):
 r['rule']=r['spec'].split('@')[0];r['seed']=r['spec'].split('@')[-1]
 r['time_abs']=abs(np.log2(r['t']/r['base_t']));r['time_signed']=np.log2(r['t']/r['base_t'])
 r['reach_abs']=abs(r['reach']-r['base_reach'])/max(1,r['base_reach']);r['reach_signed']=(r['reach']-r['base_reach'])/max(1,r['base_reach'])
 r['time_factor2']=int(r['t']/r['base_t']>=2 or r['t']/r['base_t']<=.5)
 r['reach_factor2']=int(r['reach']/max(1,r['base_reach'])>=2 or r['reach']/max(1,r['base_reach'])<=.5)
 rows.append(r)
x=pl.DataFrame(rows); ants=x.filter(pl.col('spec').str.contains('@'))
metrics=['time_abs','reach_abs','time_signed','reach_signed','time_factor2','reach_factor2']
seed=ants.group_by(['rule','seed','arm']).agg([pl.col(m).mean() for m in metrics]).sort(['rule','seed','arm'])
seed.write_csv(out/'seed_means.csv')
rule=seed.group_by(['rule','arm']).agg([pl.col(m).mean() for m in metrics]);rule.sort(['rule','arm']).write_csv(out/'rule_means.csv')
summary={'departures':dep.height,'ant_departures':dep.filter(pl.col('spec').str.contains('@')).height,'pairs':ants.filter(pl.col('arm')=='gate').height,'missing_pairs':df.filter(pl.col('arm')=='missing').height,'controls':controls.filter(pl.col('arm')!='missing').height,'censored':ants['cens'].sum(),'interventions':ants.height,'rules':3,'bootstrap_seed':2026102201,'metrics':{}}
rng=np.random.default_rng(2026102201)
rules=sorted(ants['rule'].unique().to_list())
for m in metrics:
 contrasts=[]
 for r in rules:
  z=seed.filter(pl.col('rule')==r)
  g={a['seed']:a[m] for a in z.filter(pl.col('arm')=='gate').iter_rows(named=True)}
  c={a['seed']:a[m] for a in z.filter(pl.col('arm')=='matched').iter_rows(named=True)}
  contrasts.append(np.array([g[k]-c[k] for k in sorted(g)]))
 boot=np.array([np.mean([rng.choice(contrasts[i],len(contrasts[i]),replace=True).mean() for i in rng.integers(0,len(rules),len(rules))]) for _ in range(10000)])
 summary['metrics'][m]={'gate_mean':float(seed.filter(pl.col('arm')=='gate')[m].mean()),'matched_mean':float(seed.filter(pl.col('arm')=='matched')[m].mean()),'difference':float(np.mean([c.mean() for c in contrasts])),'ci95':np.quantile(boot,[.025,.975]).tolist(),'between_seed_sd':{r:float(c.std(ddof=1)) for r,c in zip(rules,contrasts)},'per_rule_difference':dict(zip(rules,[float(c.mean()) for c in contrasts]))}
summary['by_band']=ants.group_by(['band','arm']).agg(pl.len(),pl.col('time_abs').mean(),pl.col('reach_abs').mean()).sort(['band','arm']).to_dicts()
summary['rotor']=x.filter(pl.col('spec').str.starts_with('rotor:')).group_by('arm').agg(pl.len(),pl.col('time_abs').mean(),pl.col('reach_abs').mean(),pl.col('cens').sum()).to_dicts()
(out/'analysis.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))

