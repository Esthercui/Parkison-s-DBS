"""Run fresh oracles and paired-seed comparisons; never read notebook outputs."""
import argparse
import hashlib
import importlib.metadata
import json
import platform
from pathlib import Path
import subprocess
import time
import numpy as np
from numba import set_num_threads
from threadpoolctl import threadpool_limits
from audit.bounded_core import BudgetedOracle
from .model import build_stage
from .optimize import FiniteDomain, METHODS, shared_initial, run

ROOT = Path(__file__).resolve().parents[1]

def code_fingerprint():
    files = sorted(list((ROOT/'dbs_benchmark').glob('*.py'))+
                   [ROOT/'audit/bounded_core.py',ROOT/'requirements-lock.txt'])
    return {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config',default='configs/benchmark.json')
    parser.add_argument('--output',default='results/current')
    parser.add_argument('--oracle-only',action='store_true')
    parser.add_argument('--reuse-oracles',action='store_true')
    args = parser.parse_args()
    cfg = json.loads(Path(args.config).read_text())
    out = Path(args.output); out.mkdir(parents=True,exist_ok=True)
    set_num_threads(cfg['simulator_threads'])
    fingerprints = code_fingerprint()
    manifest = dict(config=cfg,source_sha256=fingerprints,
        git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        git_dirty=bool(subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True)),
        python=platform.python_version(), platform=platform.platform(),
        packages={p:importlib.metadata.version(p) for p in
                  ('numpy','scipy','scikit-learn','cma','numba','qiskit','matplotlib')},
        timestamp_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),
        interpretation='Seeds repeat one model instance; no clinical or hardware validation.')
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    with threadpool_limits(limits=1):
        for stage in cfg['stages']:
            name=f'stage{stage}'
            saved=out/(name+'_oracle.npz'); metap=out/(name+'_oracle.json')
            model_hash={k:v for k,v in fingerprints.items() if k.endswith(('model.py','reference.py','contacts.py'))}
            signature=dict(grid=cfg['grid'],stage=stage,allow_empty=cfg['allow_empty'],source=model_hash)
            if args.reuse_oracles and saved.exists() and metap.exists():
                meta=json.loads(metap.read_text())
                if meta['signature']!=signature: raise ValueError('oracle source/config mismatch')
                if hashlib.sha256(saved.read_bytes()).hexdigest()!=meta['npz_sha256']:
                    raise ValueError('oracle artifact hash mismatch')
                with np.load(saved) as d: cost,feasible,coords=d['cost'],d['feasible'],d['coords']
                print(name,'reusing verified oracle',flush=True)
            else:
                cost,feasible,coords,meta=build_stage(stage,tuple(cfg['grid']),cfg['allow_empty'])
                np.savez_compressed(saved,cost=cost,feasible=feasible,coords=coords)
                meta.update(signature=signature,npz_sha256=hashlib.sha256(saved.read_bytes()).hexdigest())
                metap.write_text(json.dumps(meta,indent=2)+'\n')
                print(name,'fresh oracle',meta['domain_size'],'optimum',meta['ground_truth_cost'],
                      'seconds',round(meta['build_seconds'],2),flush=True)
            if args.oracle_only: continue
            domain=FiniteDomain(feasible,meta['n_bits'])
            methods=METHODS+(['Sparse-first'] if stage==3 else [])
            jobcfg={**cfg,'stage':stage,'dims':meta['grid']}
            with (out/(name+'_runs.jsonl')).open('w') as log:
                for seed in cfg['seeds']:
                    initial=shared_initial(domain,seed,cfg['initial_size'],cfg['zero_control'])
                    for method in methods:
                        oracle=BudgetedOracle(lambda i:cost[i],max(cfg['budgets']),domain,
                                              evaluation_kind=meta['objective_kind'])
                        details=run(method,oracle,coords,initial,seed,jobcfg)
                        if oracle.attempted!=max(cfg['budgets']): raise RuntimeError('incomplete budget')
                        report=oracle.report()
                        if report['denied'] or any(e['status'] in ('objective_error','invalid_or_infeasible')
                                                  for e in report['events']):
                            raise RuntimeError('invalid comparison')
                        row=dict(stage=stage,method=method,seed=seed,initial=initial,
                                 records=oracle.records,accounting=report,internal=details,
                                 regrets={str(b):min(y for _,y in oracle.records[:b])-meta['ground_truth_cost']
                                          for b in cfg['budgets']})
                        log.write(json.dumps(row)+'\n');log.flush()
                        print(name,seed,method,'regret',round(row['regrets'][str(max(cfg['budgets']))],8),
                              'seconds',round(report['wall_seconds'],2),flush=True)
    print('Finished:',out,flush=True)

if __name__=='__main__': main()
