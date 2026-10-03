"""Derive tables and publication figures exclusively from validated run records."""
import csv
import hashlib
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
COLORS={'Random':'#8b8d91','GA':'#a86e20','BO':'#406681','CMA-ES':'#202c40',
        'Surrogate (exhaustive)':'#497a55','QAOA (p=1)':'#af4568','Sparse-first':'#706854'}

def csv_write(path,rows):
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def validate(directory):
    manifest=json.loads((directory/'manifest.json').read_text())
    cfg=manifest['config']
    for p,digest in manifest['source_sha256'].items():
        assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==digest, p
    allrows=[]
    for stage in cfg['stages']:
        meta=json.loads((directory/f'stage{stage}_oracle.json').read_text())
        npz=directory/f'stage{stage}_oracle.npz'
        assert hashlib.sha256(npz.read_bytes()).hexdigest()==meta['npz_sha256']
        data=np.load(npz);cost=data['cost'];feasible=data['feasible']
        assert float(cost[feasible].min())==meta['ground_truth_cost']
        rows=[json.loads(x) for x in (directory/f'stage{stage}_runs.jsonl').read_text().splitlines()]
        expected=7 if stage==3 else 6
        assert len(rows)==len(cfg['seeds'])*expected
        keys=[(r['method'],r['seed']) for r in rows];assert len(set(keys))==len(keys)
        for seed in cfg['seeds']:
            batch=[r for r in rows if r['seed']==seed]
            assert len(batch)==expected
            assert all(r['initial']==batch[0]['initial'] for r in batch)
        for r in rows:
            rec=r['records'];ids=[m for m,_ in rec];a=r['accounting']
            assert len(rec)==len(set(ids))==max(cfg['budgets'])==a['objective_attempts']
            assert ids[:cfg['initial_size']]==r['initial']
            assert feasible[ids].all() and a['denied']==0
            assert a['objective_completed']==max(cfg['budgets'])
            for m,v in rec: assert v==cost[m]
            for b in cfg['budgets']:
                assert abs(min(v for _,v in rec[:b])-meta['ground_truth_cost']-r['regrets'][str(b)])<1e-14
            if r['method']=='QAOA (p=1)':
                solves=r['internal']['qaoa_solves']
                assert len(solves)==max(cfg['budgets'])-cfg['initial_size']
                assert a['resources']['shots']==sum((s['nfev']+4)*cfg['qaoa_shots'] for s in solves)
                assert a['resources']['circuit_executions']==sum(s['nfev']+1 for s in solves)
        allrows.extend(rows)
    return manifest,allrows

def main():
    tables=[];comparisons=[];resources=[];plotdata={}
    for name in ('current','nonempty'):
        folder=ROOT/'results'/name;manifest,rows=validate(folder);cfg=manifest['config']
        n=len(cfg['seeds']);rng=np.random.default_rng(20261003)
        resamples=rng.integers(0,n,size=(10000,n))
        for stage in cfg['stages']:
            methods=list(dict.fromkeys(r['method'] for r in rows if r['stage']==stage))
            for method in methods:
                batch=sorted([r for r in rows if r['stage']==stage and r['method']==method],key=lambda r:r['seed'])
                for b in cfg['budgets']:
                    vals=np.array([r['regrets'][str(b)] for r in batch])
                    lo,hi=np.quantile(vals[resamples].mean(axis=1),[.025,.975])
                    tables.append(dict(experiment=name,stage=stage,method=method,budget=b,n_seeds=n,
                        mean_regret=float(vals.mean()),sd_regret=float(vals.std(ddof=1)),
                        median_regret=float(np.median(vals)),mean_ci95_lo=float(lo),mean_ci95_hi=float(hi),
                        optimum_hits=int((vals<=1e-9).sum())))
                    plotdata[(name,stage,method,b)]=vals
                for r in batch:
                    a=r['accounting'];z=a['resources']
                    resources.append(dict(experiment=name,stage=stage,method=method,seed=r['seed'],
                        charged_objective_queries=a['objective_attempts'],actual_simulator_calls_in_search=0,
                        cache_hits=a['cache_hits'],surrogate_fits=z['surrogate_fits'],
                        surrogate_predictions=z['surrogate_predictions'],
                        statevector_circuits=z['circuit_executions'],simulated_shots=z['shots'],
                        optimizer_steps=z['optimizer_steps'],search_wall_seconds=a['wall_seconds'],
                        rejected_proposals=r['internal']['rejected_proposals'],
                        fallback_proposals=r['internal']['fallback_proposals'],
                        qaoa_cobyla_converged=sum(s['success'] for s in r['internal']['qaoa_solves']),
                        qaoa_cobyla_solves=len(r['internal']['qaoa_solves'])))
            for b in cfg['budgets']:
                q=plotdata[(name,stage,'QAOA (p=1)',b)]
                for other in methods:
                    if other=='QAOA (p=1)':continue
                    delta=q-plotdata[(name,stage,other,b)]
                    lo,hi=np.quantile(delta[resamples].mean(axis=1),[.025,.975])
                    comparisons.append(dict(experiment=name,stage=stage,budget=b,comparator=other,
                        qaoa_minus_comparator_mean=float(delta.mean()),paired_ci95_lo=float(lo),
                        paired_ci95_hi=float(hi),qaoa_wins=int((delta < -1e-9).sum()),
                        ties=int((np.abs(delta)<=1e-9).sum()),qaoa_losses=int((delta>1e-9).sum())))
    for filename,rows in [('summary.csv',tables),('paired_comparisons.csv',comparisons),('resources.csv',resources)]:
        csv_write(ROOT/'results'/filename,rows)
    note='10 paired optimizer seeds, one fixed simulator instance. Mean +/- sample SD. Lower regret is better.'
    lines=['# Corrected results','',note,'','Full original grids; budgets are prefixes of each 40-query run.',
           '95% percentile bootstrap intervals (10,000 resamples, seed 20261003) are descriptive; no multiplicity-adjusted significance claims.',
           'See `summary.csv` for all budgets and confidence intervals; `paired_comparisons.csv` preserves pairing.','',
           '| Experiment | Stage | Method | B=10 mean +/- SD | B=40 mean +/- SD | B=40 optimum hits |',
           '|---|---|---|---:|---:|---:|']
    for row in tables:
        if row['budget']!=40:continue
        first=next(r for r in tables if all(r[k]==row[k] for k in ('experiment','stage','method')) and r['budget']==10)
        lines.append(f"| {row['experiment']} | {row['stage']} | {row['method']} | {first['mean_regret']:.6f} +/- {first['sd_regret']:.6f} | {row['mean_regret']:.6f} +/- {row['sd_regret']:.6f} | {row['optimum_hits']}/10 |")
    (ROOT/'results/RESULTS.md').write_text('\n'.join(lines)+'\n')
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,
        'axes.spines.right':False,'svg.fonttype':'none','svg.hashsalt':'dbs-corrected-v1','savefig.facecolor':'white'})
    assets=ROOT/'assets';assets.mkdir(exist_ok=True)
    fig,axs=plt.subplots(1,3,figsize=(14,6),gridspec_kw={'width_ratios':[1,1,1]})
    for ax,stage in zip(axs,(1,2,3)):
        selected=[r for r in tables if r['experiment']=='current' and r['stage']==stage and r['budget']==40 and r['method']!='Sparse-first']
        for i,row in enumerate(selected):
            vals=plotdata[('current',stage,row['method'],40)]
            ax.scatter(vals,np.full(len(vals),i)+np.linspace(-.15,.15,len(vals)),s=16,alpha=.6,color=COLORS[row['method']])
            ax.errorbar(row['mean_regret'],i,xerr=[[row['mean_regret']-row['mean_ci95_lo']],
                        [row['mean_ci95_hi']-row['mean_regret']]],color=COLORS[row['method']],fmt='D',ms=5,capsize=3)
        ax.set_yticks(range(len(selected)),[r['method'].replace(' (exhaustive)','\n(exhaustive)') for r in selected])
        ax.invert_yaxis();ax.grid(axis='x',color='#e5e5e5');ax.set_axisbelow(True)
        ax.set_xlabel('Regret at 40 charged objective queries')
        ax.set_title(f'Stage {stage}'+('\nAll methods tie at zero' if stage==3 else '\nFull finite grid'),loc='left',fontsize=12)
        if stage==3:ax.set_xlim(-.004,.08);ax.set_xticks([0,.04,.08])
        else:ax.set_xlim(left=-.005)
    fig.suptitle('Corrected DBS benchmark: fresh results, no Stage 3 superiority',x=.025,ha='left',fontsize=17)
    fig.text(.025,.075,'Dots: individual seeds. Diamonds: means. Whiskers: descriptive 95% bootstrap CIs; n=10 seeds on one model.',fontsize=10)
    fig.text(.025,.04,'Compare methods within each stage. Stage 3 includes the no-stimulation control; its objective is a fitted QUBO, not a new neural simulation.',fontsize=9)
    for ax in axs: ax.set_xlim(-.005,.18); ax.set_xticks([0,.05,.10,.15])
    fig.tight_layout(rect=[0,.12,1,.91],w_pad=2)
    fig.savefig(assets/'corrected_results.svg', metadata={'Date': None});fig.savefig(assets/'corrected_results.png',dpi=180);plt.close(fig)
    fig,axs=plt.subplots(1,2,figsize=(12,4.8))
    d=np.load(ROOT/'results/current/stage3_oracle.npz');cost=d['cost']
    counts=np.array([i.bit_count() for i in range(len(cost))])
    mins=[cost[counts==i].min() for i in range(17)];maxs=[cost[counts==i].max() for i in range(17)]
    axs[0].fill_between(range(17),mins,maxs,color='#d7e3ea',label='Minimum–maximum over all masks')
    axs[0].plot(range(17),mins,'o-',color='#406681',label='Minimum cost')
    axs[0].set(xlabel='Active contacts',ylabel='Stage 3 objective (intercept omitted)',title='The objective favors no stimulation')
    axs[0].legend(frameon=False,fontsize=8);axs[0].set_xticks(range(0,17,2));axs[0].set_ylim(bottom=0)
    methods=['BO','Surrogate (exhaustive)','QAOA (p=1)','Sparse-first']
    for i,method in enumerate(methods):
        selected=[r for r in tables if r['experiment']=='nonempty' and r['method']==method]
        axs[1].plot([r['budget'] for r in selected],[r['mean_regret'] for r in selected],
                    marker=['o','s','^','D'][i],linestyle=['-','--',':','-.'][i],
                    color=COLORS[method],label=method)
        axs[1].fill_between([r['budget'] for r in selected],
            [r['mean_ci95_lo'] for r in selected],[r['mean_ci95_hi'] for r in selected],
            color=COLORS[method],alpha=.12)
    axs[1].set(xlabel='Charged objective queries',ylabel='Mean regret',title='Nonempty-domain sensitivity')
    axs[1].legend(frameon=False,fontsize=8);axs[1].set_xticks([10,20,30,40]);axs[1].set_ylim(bottom=-.001)
    fig.text(.05,.035,'Fresh fit; all masks enumerated. Sensitivity: four selected methods, 10 seeds; bands are descriptive 95% CIs. All methods in results/summary.csv.',fontsize=8)
    fig.tight_layout(rect=[0,.08,1,1]);fig.savefig(assets/'stage3_diagnostic.svg', metadata={'Date': None});fig.savefig(assets/'stage3_diagnostic.png',dpi=180);plt.close(fig)
    hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted((ROOT/'results').rglob('*')) if p.is_file() and 'smoke' not in p.parts and p.name!='validation.json'}
    (ROOT/'results/validation.json').write_text(json.dumps(dict(status='PASS',
        verified_runs=len(resources),source='fresh recorded objective accesses',sha256=hashes),indent=2)+'\n')
    print('Validated',len(resources),'runs; wrote 3 CSVs, RESULTS.md and 2 figures.')

if __name__=='__main__': main()
