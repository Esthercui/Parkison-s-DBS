"""Cheap discrepancy reproduction using saved fit coefficients; no simulation sweep."""
import ast
import argparse
import json
import numpy as np
from .bounded_core import (Domain, BudgetedOracle, LegacyOracleView,
    minimize_surrogate_exhaustive, quadratic_values, qubo_to_ising)
from .historical import load_stage3
from .probes import GateRecorder,cma_leak_probe,qaoa_path_probe

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--full',action='store_true',help='include per-request oracle logs')
    args=parser.parse_args()
    env,nb=load_stage3()
    q=env['Q'];linear=np.diag(q);pairs=np.triu(q,1)
    masks=np.arange(1<<16)
    costs=quadratic_values(masks,0.,linear,pairs)
    # Cross-check vector evaluation against original scalar objective at
    # boundaries and asymmetric patterns; all-state consistency is tested below.
    for m in (0,1,2,1<<15,12345,65535):
        np.testing.assert_allclose(costs[m],env['qubo_value'](env['mask_to_bits'](m),q),atol=1e-12)
    allow=minimize_surrogate_exhaustive(0.,linear,pairs,Domain(16,True))
    nonempty=minimize_surrogate_exhaustive(0.,linear,pairs,Domain(16,False))
    constant,h,j=qubo_to_ising(0.,linear,pairs)
    bits=((masks[:,None] >> np.arange(16))&1).astype(float);z=1-2*bits
    correct=np.full(len(masks),constant);legacy=np.zeros(len(masks))
    for i in range(16):
        correct+=h[i]*z[:,i];legacy+=linear[i]*z[:,i]
        for k in range(i+1,16):
            correct+=j[i,k]*z[:,i]*z[:,k]
            legacy+=pairs[i,k]*z[:,i]*z[:,k]
    # Execute the actual nested historical builder into a gate recorder.
    tree=ast.parse(''.join(nb['cells'][7]['source']))
    outer=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='run_surrogate_qaoa')
    builder=next(x for x in outer.body if isinstance(x,ast.FunctionDef) and x.name=='build_qaoa')
    ctx=dict(QuantumCircuit=GateRecorder,bitlen=16,p_layers=1)
    exec(compile(ast.Module(body=[builder],type_ignores=[]),'historical_cost_builder','exec'),ctx)
    gates=ctx['build_qaoa']([1.0],[0.0],linear,[(i,k,pairs[i,k]) for i in range(16) for k in range(i+1,16)]).gates
    assert all(g[1]==2*linear[g[2]] if g[0]=='z' else g[1]==2*pairs[g[2],g[3]] for g in gates)
    cma=cma_leak_probe(env)
    paths={}
    for name,budget in [('run_random',10),('run_ga',10),('run_bo',3),('run_surrogate_exact',3)]:
        oracle=BudgetedOracle(lambda m:float(costs[m]),budget,Domain(16,True),evaluation_kind='precomputed_saved_fit_QUBO_lookup')
        reported=env[name](LegacyOracleView(oracle),budget,0)
        paths[name]=dict(reported=len(reported),report=oracle.report())
    definitions=[i for i,c in enumerate(nb['cells']) if 'def run_surrogate_exact(' in ''.join(c.get('source',[]))]
    report=dict(provenance=env['audit_provenance'],
        oracle_allowed=allow,oracle_nonempty=nonempty,
        no_stimulation=dict(mask=0,cost_without_c0=float(costs[0]),fitted_beta_with_c0=env['c0']),
        minimum_linear=float(linear.min()),minimum_pair=float(pairs[np.triu_indices(16,1)].min()),
        all_nonempty_costs_positive=bool(np.all(costs[1:]>0)),
        decode_zero_mask=env['bits_to_mask'](env['decode_threshold'](np.zeros(16))),
        surrogate_definition_cells=definitions,
        corrected_mapping_max_error=float(np.max(np.abs(correct-costs))),
        historical_mapping_error_after_matching_zero_offset=float(np.max(np.abs((legacy-legacy[0])-costs))),
        historical_cost_gates=len(gates),cma_probe=cma,method_probes=paths,
        qaoa_sampler_path=qaoa_path_probe(env),qaoa_fallback_path=qaoa_path_probe(env,fallback=True),
        scope='audit only; saved fit reused explicitly; no new benchmark table or clinical inference')
    if args.full:
        print(json.dumps(report,indent=2))
    else:
        short={k:v for k,v in report.items() if k not in
               ('cma_probe','method_probes','qaoa_sampler_path','qaoa_fallback_path')}
        short['cma_probe']={k:v for k,v in cma.items() if k!='guard'}
        short['method_probe_objective_calls']={k:v['report']['objective_attempts'] for k,v in paths.items()}
        short['qaoa_paths']='normal/fallback checked with doubles, no quantum simulation'
        print(json.dumps(short,indent=2))

if __name__=='__main__': main()
