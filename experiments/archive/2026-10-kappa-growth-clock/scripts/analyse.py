"""Frozen growth-clock audit. Outputs include calibration and provenance."""
from pathlib import Path
import hashlib
import json
import csv
import numpy as np
import polars as pl

ROOT = Path(__file__).resolve().parents[4]
EXP = Path(__file__).resolve().parents[1]
OUT = EXP / 'results'
SEED = 2026101608
NB = 2000


def design(a, test=None):
    """Fit hinges on training observations only."""
    if test is None:
        test = a
    knots = np.quantile(a, [.25,.5,.75])
    def build(v):
        return np.column_stack([np.ones(len(v)), v] + [np.maximum(v-k,0) for k in knots])
    return build(a), build(test)


def coefficient(x, y, lead):
    return float(np.linalg.lstsq(np.c_[x, lead], y, rcond=None)[0][-1])


def crossval(a, y, lead, family):
    loss0, loss1, den = np.zeros(len(y)), np.zeros(len(y)), np.zeros(len(y))
    for f in np.unique(family):
        tr, te = family != f, family == f
        x, z = design(a[tr], a[te])
        p0 = z @ np.linalg.lstsq(x, y[tr], rcond=None)[0]
        p1 = np.c_[z,lead[te]] @ np.linalg.lstsq(np.c_[x,lead[tr]], y[tr], rcond=None)[0]
        loss0[te], loss1[te], den[te] = (y[te]-p0)**2, (y[te]-p1)**2, (y[te]-y[tr].mean())**2
    return loss0, loss1, den


def calibration():
    rng = np.random.default_rng(SEED+100)
    a = rng.uniform(0, 3, 256)
    lead = rng.integers(1, 5, 256).astype(float)
    x, _ = design(a)
    beta = np.arange(x.shape[1])*.07
    y0 = x @ beta
    b0 = coefficient(x, y0, lead)
    b1 = coefficient(x, y0+.2*lead, lead)
    # Zero-noise regression and accounting should be exact to roundoff.
    assert abs(b0) < 1e-10 and abs(b1-.2) < 1e-10
    log_pa = -.3*a+.01*lead
    log_b = y0+.2*lead+log_pa
    err = abs(coefficient(x,log_b,lead)-coefficient(x,log_pa,lead)-b1)
    assert err < 1e-10
    # Correlated lead/area, family-correlated noise: measure finite-sample bias.
    fam = np.repeat(np.arange(16),4)
    ld = np.tile(np.arange(1,5),16).astype(float)
    area = rng.normal(size=16)[fam] - .25*ld + rng.normal(0,.3,64)
    sx,_ = design(area)
    base = sx @ np.array([.1,.3,-.2,.1,.05])
    estimates=[]
    for _ in range(200):
        noise=rng.normal(0,.04,16)[fam]+rng.normal(0,.04,64)
        estimates.append([coefficient(sx,base+noise,ld),coefficient(sx,base+.15*ld+noise,ld)])
    avg=np.mean(estimates,axis=0)
    assert abs(avg[0])<.01 and abs(avg[1]-.15)<.01
    losses=crossval(area,base,ld,fam)
    null_gain=float((losses[0]-losses[1]).sum()/losses[2].sum())
    assert abs(null_gain)<.02
    return dict(null_slope=b0, planted_slope=b1, accounting_error=err,
                noisy_repetitions=200,noisy_null_mean=float(avg[0]),noisy_planted_mean=float(avg[1]),
                known_null_cv_gain=null_gain,
                scope='Exact spline coefficient and identity calibration; no exponent estimator used.')


def analyse_window(df, k):
    valid = df.filter((pl.col('k')==k) & (pl.col('boundary_steps')>0)).join(
        df.filter(pl.col('k')==18).select('rule',early=pl.col('area').log()), on='rule')
    valid = valid.with_columns(
        base=pl.col('rule').str.split('@').list.first(),
        lnb=(pl.col('boundary_steps')/(2**k)).log(),
        lnpa=(pl.col('perimeter')/pl.col('area')).log(),
        late=pl.col('area').log()).with_columns(lnk=pl.col('lnb')-pl.col('lnpa'))
    cohort = pl.read_csv(OUT/'cohort.csv')
    stats = valid.group_by('base').agg(
        pl.len().alias('n'), *[pl.col(c).mean() for c in ['early','late','lnb','lnpa','lnk']],
        pl.col('lnk').std().alias('lnk_seed_sd'))
    means = cohort.rename({'rule':'base'}).join(stats,on='base',how='left').with_columns(
        pl.col('n').fill_null(0)).sort('family','lead')
    means.write_csv(OUT/f'rule_means_k{k}.csv')
    good = means.filter(pl.col('n')>=3)
    complete = good.group_by('family').len().filter(pl.col('len')==4)['family'].to_list()
    fit = good.filter(pl.col('family').is_in(complete)).sort('family','lead')
    retention = {str(j):int(good.filter(pl.col('lead')==j).height) for j in range(1,5)}
    result = dict(k=k, qualifying_by_lead=retention, complete_families=len(complete),
                  valid_seed_counts=means.group_by('lead').agg(pl.col('n').sum()).sort('lead').to_dicts(),
                  gate_passed=len(complete)>=12)
    if len(complete)<12:
        result['verdict']='UNINFORMATIVE: complete-family support gate failed'
        return result
    family=fit['family'].to_numpy()
    lead=fit['lead'].to_numpy().astype(float)
    early, late, y, lnb, lnpa = [fit[c].to_numpy() for c in ['early','late','lnk','lnb','lnpa']]
    xe,_ = design(early); xl,_=design(late)
    be, bl = coefficient(xe,y,lead), coefficient(xl,y,lead)
    rng=np.random.default_rng(SEED+k)
    families=np.unique(family)
    # Resample whole families; recompute knots on each resampled training set.
    boot=[]; gains=[]
    l0,l1,den=crossval(late,y,lead,family)
    for _ in range(NB):
        draw=rng.choice(families,len(families),replace=True)
        ix=np.concatenate([np.flatnonzero(family==f) for f in draw])
        xb,_=design(late[ix]); eb,_=design(early[ix])
        boot.append([coefficient(eb,y[ix],lead[ix]),coefficient(xb,y[ix],lead[ix])])
        gains.append(float((l0[ix]-l1[ix]).sum()/den[ix].sum()))
    boot=np.array(boot)
    ci=np.quantile(boot,[.025,.975],axis=0).T
    gain=float((l0-l1).sum()/den.sum()); gci=np.quantile(gains,[.025,.975])
    b_b,b_pa=coefficient(xl,lnb,lead),coefficient(xl,lnpa,lead)
    assert abs(bl-(b_b-b_pa))<1e-9
    # Both linear size controls; explicitly descriptive post-treatment sensitivity.
    both=coefficient(np.c_[np.ones(len(y)),early,late],y,lead)
    result.update(n_rules=len(y),early_slope=be,current_slope=bl,
        early_ci=ci[0].tolist(),current_ci=ci[1].tolist(),
        current_over_early=bl/be if be else None,
        P1='HELD' if be>0 and bl>=.5*be and ci[1,0]>0 else 'FAILED',
        gain=gain,gain_ci=gci.tolist(),
        baseline_R2=float(1-l0.sum()/den.sum()),with_lead_R2=float(1-l1.sum()/den.sum()),
        P2='HELD' if gain>=.05 and gci[0]>0 else 'FAILED',
        boundary_log_slope=b_b,edge_fraction_log_slope=b_pa,
        both_area_linear_slope=both,
        between_seed_sd_median=float(fit['lnk_seed_sd'].median()))
    return result


def main():
    cal=calibration()  # Must precede ant analysis.
    df=pl.read_csv(EXP/'dumps/probe.csv')
    assert df['rule'].n_unique()==256
    assert set(df['rule'])==set((OUT/'specs.txt').read_text().split())
    lookup={(r['rule'],r['k']):r for r in df.to_dicts()}
    statuses=[]
    for spec in (OUT/'specs.txt').read_text().split():
        rows=[r for (s,k),r in lookup.items() if s==spec]
        for k in [21,22,23]:
            target=lookup.get((spec,k))
            reason=('missing_early_window' if (spec,18) not in lookup else
                    'missing_target_window' if target is None else
                    'zero_boundary_steps' if target['boundary_steps']==0 else 'valid')
            statuses.append(dict(spec=spec,k=k,escaped=rows[0]['escaped'],
                last_k=max(r['k'] for r in rows),status=reason))
    with (OUT/'seed_status.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(statuses[0]),lineterminator='\n')
        writer.writeheader();writer.writerows(statuses)
    published=df.filter(pl.col('k').is_between(18,23))
    published.write_csv(OUT/'windows.csv')
    windows=[analyse_window(published,k) for k in [21,22,23]]
    inputs=[EXP/'dumps/probe.csv',OUT/'cohort.csv',OUT/'specs.txt',Path(__file__),
            OUT/'registration.md',ROOT/'pyproject.toml',ROOT/'uv.lock',OUT/'run-sources.sha256']
    report=dict(seed=SEED,bootstrap=NB,git=(OUT/'run-commit.txt').read_text().strip(),
        provenance_note='Simulation base commit; dirty source hashes freeze run; analysis SHA256 pins estimator.',
        command='uv run experiments/archive/2026-10-kappa-growth-clock/scripts/analyse.py',
        hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},
        calibration=cal,runs=256,escaped=df.filter(pl.col('escaped'))['rule'].n_unique(),windows=windows,
        status_counts={f'k{k}':{s:sum(r['k']==k and r['status']==s for r in statuses)
            for s in sorted({r['status'] for r in statuses})} for k in [21,22,23]})
    (OUT/'analysis.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    lines=[f"Fresh growth-clock audit; seed {SEED}; {NB} family bootstraps",f"Runs: 256; escaped: {report['escaped']}",f'Calibration: {cal}']
    for r in windows:
        lines.append(json.dumps(r,sort_keys=True))
    (OUT/'analysis.txt').write_text('\n'.join(lines)+'\n')
    print('\n'.join(lines))


if __name__=='__main__':
    main()
