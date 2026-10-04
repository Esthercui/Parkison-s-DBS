"""Commands for the bounded Stage 3 methodology validation; no manuscript edits."""
import argparse
import ast
import csv
import gzip
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import time

for key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[key] = "1"
os.environ["MPLBACKEND"] = "Agg"

import numpy as np
from joblib import Parallel, delayed
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector
from qiskit.circuit.library import RZGate, RZZGate
from stage3_validation_core import (bits_for_masks, binary_values, binary_to_ising,
    ising_values, binary_cost_layer, fit_surrogate, exhaustive_proposal)

ROOT = Path(__file__).resolve().parent
BASE = "b43e30bdccba85767f3a8835ab30e313a60b9977"
METHODS = ["Random", "GA", "BO", "CMA-ES", "Surrogate (Pool)",
           "Surrogate (Exhaustive)", "QAOA (p=1)"]
SURROGATES = METHODS[4:]


def write_json(path, data):
    path.write_text(json.dumps(data, indent=2, allow_nan=False) + "\n")


def write_csv(path, rows):
    rows = list(rows)
    if not rows:
        raise ValueError(f"No rows for {path}")
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def source_hashes():
    return {p: hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
            for p in ("stage3.ipynb", "stage3_validation_core.py", "requirements-stage3.txt")}


def verify_scope(out):
    old = json.loads(subprocess.check_output(["git", "show", f"{BASE}:stage3.ipynb"], cwd=ROOT))
    current = json.loads((ROOT/"stage3.ipynb").read_text())
    for index in range(7):
        assert old["cells"][index]["source"] == current["cells"][index]["source"], index
    def fn(cell, name):
        return next(n for n in ast.parse("".join(cell["source"])).body
                    if isinstance(n, ast.FunctionDef) and n.name == name)
    assert ast.dump(fn(old["cells"][7], "run_surrogate_exact")) == ast.dump(fn(current["cells"][7], "run_surrogate_exact"))
    files = subprocess.check_output(["git", "ls-tree", "-r", "--name-only", BASE], cwd=ROOT, text=True).splitlines()
    preserved = [p for p in files if p.startswith("results/stage3_controlled/") or
                 p in ("stage1.ipynb", "stage2.ipynb", "run_stage3.py", "STAGE3_RESULTS.md", "README.md", "requirements-stage3.txt")]
    for p in preserved:
        assert (ROOT/p).read_bytes() == subprocess.check_output(["git", "show", f"{BASE}:{p}"], cwd=ROOT), p
    result = dict(status="PASS", baseline=BASE, preserved_files=preserved,
        notebook_cells_0_through_6_unchanged=True, surrogate_pool_ast_unchanged=True,
        manuscript_modified=False)
    write_json(out/"frozen_scope_validation.json", result)
    return result


def load_notebook():
    notebook = json.loads((ROOT/"stage3.ipynb").read_text())
    for index in range(8):
        exec(compile("".join(notebook["cells"][index]["source"]), f"stage3.ipynb:cell{index}", "exec"), globals())
    return notebook


def initial_observations(budget, seed):
    rng = np.random.default_rng(seed)
    n_init = min(max(10, budget//4), budget-1)
    initial = []
    seen = set()
    while len(initial) < n_init:
        mask = random_admissible_mask(rng)
        if mask not in seen:
            initial.append((mask, float(oracle_cost_flat[mask])))
            seen.add(mask)
    return initial


def save_domain(out):
    bits = bits_for_masks(np.arange(N_MASKS))
    amplitudes = A_UNIT*(bits @ FOCUS)
    components = dict(efficacy_without_c0=float(beta_ratio_flat[best_mask]-c0),
        count=float(LAMBDA_COUNT*best_bits.sum()),
        energy=float(LAMBDA_ENERGY*A_UNIT**2*(IMP_FACTOR @ best_bits)),
        risk=float(LAMBDA_RISK*(RISK @ best_bits)),
        overlap=float(LAMBDA_OVERLAP*sum(OVERLAP[i,j]*best_bits[i]*best_bits[j]
            for i in range(16) for j in range(i+1,16))),
        charge_density=float(LAMBDA_QD*(QD_SOFT_PEN @ best_bits)))
    assert abs(sum(components.values())-best_cost) <= 1e-12
    result = dict(total_masks=N_MASKS, exactly_six_masks=int(np.sum(active_count_flat==6)),
        admissible_masks=int(admissible_flat.sum()), percentage_full_space=float(100*admissible_flat.mean()),
        optimal_mask=best_mask, active_contacts_zero_based=np.flatnonzero(best_bits).tolist(),
        binary_msb_first=format(best_mask,"016b"), effective_amplitude=float(amplitudes[best_mask]),
        fitted_beta_ratio=float(beta_ratio_flat[best_mask]), cost=best_cost,
        objective_components=components, omitted_constant=float(c0),
        coefficients=[float(c0),float(c1),float(c2)], threshold=BETA_RATIO_LIMIT,
        optimum_count=int(np.sum(oracle_cost_flat==best_cost)),
        description="Primary fixed-cardinality, efficacy-screened benchmark; not a clinical necessity")
    write_json(out/"ground_truth.json", result)
    write_csv(out/"feasible_domain_k6.csv", (dict(mask=int(m),
        active_contacts=" ".join(map(str,np.flatnonzero(bits[m]))), effective_amplitude=float(amplitudes[m]),
        fitted_beta_ratio=float(beta_ratio_flat[m]), true_objective=float(oracle_cost_flat[m])) for m in ADMISSIBLE_MASKS))
    np.savez_compressed(out/"oracle.npz", cost=oracle_cost_flat, feasible=admissible_flat,
        beta=beta_ratio_flat, active_count=active_count_flat, amplitude=amplitudes, Q=Q,
        fit_amplitudes=Aeff_samples, fit_observed=ratios, coefficients=np.array([c0,c1,c2]))
    return result


def mapping_validation(out, notebook):
    bits = bits_for_masks(np.arange(65536))
    configurations = {
        "true_objective": (0., np.diag(Q).copy(), np.triu(Q,1)),
        "initial_surrogate": fit_surrogate(initial_observations(40,0)),
    }
    rng=np.random.default_rng(91273)
    configurations["asymmetric_fixture"]=(0.37,rng.normal(size=16),np.triu(rng.normal(size=(16,16)),1))
    energies={}; summaries={}
    for name, parameters in configurations.items():
        binary=binary_values(bits,*parameters)
        transformed=ising_values(bits,*binary_to_ising(*parameters))
        error=np.abs(binary-transformed)
        assert float(error.max()) <= 1e-10, (name,error.max())
        energies[name]=(binary,transformed,error)
        summaries[name]=dict(max_abs_error=float(error.max()),mean_abs_error=float(error.mean()),passed=int(np.sum(error<=1e-10)))
    # Confirm installed gate signs/factors, rather than relying on convention memory.
    angle=.731
    assert np.max(np.abs(np.asarray(RZGate(angle))-np.diag(np.exp(-.5j*angle*np.array([1,-1])))))<1e-14
    assert np.max(np.abs(np.asarray(RZZGate(angle))-np.diag(np.exp(-.5j*angle*np.array([1,-1,-1,1])))))<1e-14
    # Test the actual notebook QAOA builder, including the original X mixer.
    tree=ast.parse("".join(notebook["cells"][7]["source"]))
    outer=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=="run_surrogate_qaoa")
    builder=next(n for n in outer.body if isinstance(n,ast.FunctionDef) and n.name=="build_qaoa")
    scope=dict(np=np,QuantumCircuit=QuantumCircuit,binary_cost_layer=binary_cost_layer,bitlen=16,p_layers=1)
    exec(compile(ast.Module(body=[builder],type_ignores=[]),"actual_notebook_builder","exec"),scope)
    c,a,b=configurations["asymmetric_fixture"];gamma=.417;beta=.283
    pairs=[(i,j,float(b[i,j])) for i in range(16) for j in range(i+1,16)]
    circuit=scope["build_qaoa"]([gamma],[beta],a,pairs).remove_final_measurements(inplace=False)
    actual=Statevector.from_instruction(circuit).data
    offset,_,_=binary_to_ising(c,a,b)
    expected=np.exp(-1j*gamma*(energies["asymmetric_fixture"][0]-offset))/256
    ids=np.arange(65536)
    for qubit in range(16):
        expected=np.cos(beta)*expected-1j*np.sin(beta)*expected[ids^(1<<qubit)]
    state_error=float(np.max(np.abs(actual-expected)))
    assert state_error<1e-10,state_error
    rows=[]
    for mask in range(65536):
        row=dict(mask=mask)
        for name,(binary,transformed,error) in energies.items():
            row.update({name+"_binary":float(binary[mask]),name+"_ising_with_offset":float(transformed[mask]),name+"_abs_error":float(error[mask])})
        rows.append(row)
    write_csv(out/"qubo_ising_validation.csv",rows)
    summary=dict(status="PASS",configurations=65536,tests=summaries,
        max_abs_error=max(v["max_abs_error"] for v in summaries.values()),
        mean_abs_error=float(np.mean([v["mean_abs_error"] for v in summaries.values()])),
        actual_16_qubit_statevector_max_error=state_error,installed_gate_conventions="verified by matrices",
        source_sha256=source_hashes())
    write_json(out/"mapping_validation_summary.json",summary)
    write_json(out/"cardinality_penalty_rule.json",dict(quadratic_cardinality_penalty_used=False,
        lambda_value=None,reason="Pinned baseline has no cardinality penalty in the phase QUBO; none added.",
        unchanged_internal_rejection_barrier=1000,
        barrier_scope="Classical COBYLA sampled objective, for infeasible/seen masks; not encoded in cost Hamiltonian.",
        hard_rule="Exactly k=6 and fitted BetaRatio<=0.8228585 for every true evaluation",
        adequacy_check="For every fitted surrogate, assert abs(c)+sum(abs(a))+sum(abs(b)) < 1000. Never tune barrier.",
        penalized_qubo_enumeration="Not applicable: no penalized phase QUBO is used."))
    print(json.dumps(summary,indent=2),flush=True)


def require_mapping(out):
    record=json.loads((out/"mapping_validation_summary.json").read_text())
    assert record["status"]=="PASS" and record["max_abs_error"]<=1e-10
    assert record["source_sha256"]==source_hashes(),"Mapping validation is stale"


def direct_ratio(amplitude):
    _,y=simulate_stn_gpe(MAIN_PATIENT,DBSParams(F_HZ,float(amplitude),PW_S),SIM)
    return float(beta_band_power(y,FS,BETA_BAND)/(BASELINE_BETA+1e-12))


def model_validation(out,workers):
    bits=bits_for_masks(np.arange(65536))
    # Metadata FOCUS values have exactly two decimal places. Cache equivalent sums.
    units=np.rint(FOCUS*100).astype(int)
    assert np.max(np.abs(units/100-FOCUS))<1e-14
    amplitude=(bits@units)/400
    counts=bits.sum(axis=1).astype(int)
    primary=amplitude[counts==6]
    uniform=np.round(np.linspace(0,4,401),12)
    local=np.round(np.arange(int(round(primary.min()*400)),int(round(primary.max()*400))+1)/400,12)
    requested=sorted(set(np.round(amplitude,12))|set(uniform)|set(local)|set(np.round(Aeff_samples,12)))
    cache={round(float(a),12):float(v) for a,v in zip(Aeff_samples,ratios)}
    missing=[a for a in requested if a not in cache]
    values=Parallel(n_jobs=workers,backend="loky",verbose=10)(delayed(direct_ratio)(a) for a in missing)
    cache.update(zip(missing,values))
    def fitted(a):return float(c0+c1*a+c2*a*a)
    def metrics(grid):
        direct=np.array([cache[round(float(a),12)] for a in grid]);fit=np.array([fitted(a) for a in grid]);error=fit-direct
        return dict(n=len(grid),amplitude_min=float(min(grid)),amplitude_max=float(max(grid)),
            r_squared=float(1-np.sum(error**2)/np.sum((direct-direct.mean())**2)),
            rmse=float(np.sqrt(np.mean(error**2))),mae=float(np.mean(np.abs(error))),max_abs_error=float(np.max(np.abs(error))))
    write_csv(out/"beta_fit_validation.csv",(dict(effective_amplitude=float(a),direct_beta_ratio=cache[a],
        fitted_beta_ratio=fitted(a),residual=fitted(a)-cache[a],
        original_fit_point=bool(np.min(np.abs(Aeff_samples-a))<1e-11),
        global_uniform_grid=bool(a in set(uniform)),primary_local_grid=bool(a in set(local)),
        within_original_fit_range=bool(0<=a<=4)) for a in requested))
    # Bracket all direct crossings on the dense validation grid, then refine without refitting.
    from scipy.optimize import brentq
    crossings=[];refinement={}
    def threshold_function(a):
        key=float(a)
        if key not in refinement:refinement[key]=direct_ratio(key)
        return refinement[key]-BETA_RATIO_LIMIT
    for left,right in zip(uniform[:-1],uniform[1:]):
        yl=cache[left]-BETA_RATIO_LIMIT;yr=cache[right]-BETA_RATIO_LIMIT
        if yl*yr<0:
            root=brentq(threshold_function,float(left),float(right),xtol=1e-10)
            crossings.append(dict(bracket_left=float(left),bracket_right=float(right),amplitude=float(root),
                direction="downward" if yl>0 else "upward",direct_beta_ratio=refinement[root]))
    roots=sorted(float(v.real) for v in np.roots([c2,c1,c0-BETA_RATIO_LIMIT]) if abs(v.imag)<1e-12 and 0<=v.real<=4)
    threshold=dict(threshold=BETA_RATIO_LIMIT,fitted_crossings=roots,direct_crossings=crossings,
        fitted_to_nearest_direct=[dict(fitted_amplitude=a,nearest_direct_amplitude=min((v['amplitude'] for v in crossings),key=lambda x:abs(x-a)),
             difference_fitted_minus_direct=a-min((v['amplitude'] for v in crossings),key=lambda x:abs(x-a))) for a in roots] if crossings else [],
        interpretation="Benchmark efficacy threshold, not a clinical treatment threshold",
        dense_bracketing_step=.01,root_tolerance=1e-10)
    write_json(out/"threshold_validation.json",threshold)
    write_csv(out/"threshold_refinement.csv",(dict(amplitude=a,direct_beta_ratio=v) for a,v in sorted(refinement.items())))
    fit_all=c0+c1*amplitude+c2*amplitude**2
    direct_all=np.array([cache[round(float(a),12)] for a in amplitude])
    ff=fit_all<=BETA_RATIO_LIMIT;df=direct_all<=BETA_RATIO_LIMIT
    write_csv(out/"fit_vs_direct_feasibility.csv",(dict(mask=int(m),cardinality=int(counts[m]),
        effective_amplitude=float(amplitude[m]),fitted_beta_ratio=float(fit_all[m]),direct_beta_ratio=float(direct_all[m]),
        fit_pass=bool(ff[m]),direct_pass=bool(df[m])) for m in range(65536)))
    def confusion(label,selected):
        return dict(scope=label,masks=int(selected.sum()),fit_feasible_direct_feasible=int((selected&ff&df).sum()),
            fit_feasible_direct_infeasible=int((selected&ff&~df).sum()),
            fit_infeasible_direct_feasible=int((selected&~ff&df).sum()),
            fit_infeasible_direct_infeasible=int((selected&~ff&~df).sum()))
    confusion_rows=[confusion("all_cardinalities",np.ones(65536,dtype=bool)),confusion("k4_to_k7",np.isin(counts,[4,5,6,7]))]
    confusion_rows += [confusion(f"k={k}",counts==k) for k in range(17)]
    write_csv(out/"feasibility_confusion.csv",confusion_rows)
    cardinality=[]
    full_cost=binary_values(bits,0.,np.diag(Q),np.triu(Q,1))
    for k in [4,5,6,7]:
        ids=np.flatnonzero(counts==k);m=int(ids[np.argmin(fit_all[ids])])
        admissible=ids[ff[ids]]
        cost_mask=int(admissible[np.argmin(full_cost[admissible])]) if len(admissible) else None
        cardinality.append(dict(k=k,total_masks=len(ids),amplitude_min=float(amplitude[ids].min()),amplitude_max=float(amplitude[ids].max()),
            minimum_fitted_beta=float(fit_all[m]),fitted_admissible_masks=int(ff[ids].sum()),direct_pass_masks=int(df[ids].sum()),
            best_fitted_beta_mask=m,best_fitted_beta_contacts=" ".join(map(str,np.flatnonzero(bits[m]))),
            best_fitted_beta_amplitude=float(amplitude[m]),best_fitted_beta_direct_ratio=float(direct_all[m]),
            best_fitted_admissible_objective_mask=cost_mask,
            best_fitted_admissible_objective_cost=float(full_cost[cost_mask]) if cost_mask is not None else None,
            objective_optimum_direct_ratio=float(direct_all[cost_mask]) if cost_mask is not None else None))
    write_csv(out/"cardinality_sensitivity.csv",cardinality)
    result=dict(global_uniform_0_to_4=metrics(uniform),primary_k6_interval=metrics(local),
        fresh_fit_points=41,new_cached_amplitude_simulations=len(missing),threshold_refinement_simulations=len(refinement),
        unique_mask_amplitudes=len(np.unique(amplitude)),all_masks_classified=65536,
        primary_ground_truth_direct_ratio=float(direct_all[best_mask]),
        cache_key="Exact 0.0025 amplitude lattice from two-decimal FOCUS metadata; uniform-grid keys rounded to 12 decimals")
    write_json(out/"beta_fit_metrics.json",result)
    print(json.dumps(result,indent=2),flush=True)


def run_job(method,budget,seed):
    trace=[];raw=[];history=[]
    methods=dict(zip(METHODS,[run_random,run_ga,run_bo,run_cma_es,run_surrogate_exact,run_surrogate_exhaustive,run_surrogate_qaoa]))
    kwargs=dict(trace=trace,raw_samples=raw,circuit_history=history) if method==METHODS[-1] else {}
    start=time.perf_counter()
    observations=methods[method](oracle_cost_flat,budget,seed,**kwargs)
    assert len(observations)==budget==len({m for m,_ in observations})
    assert all(is_admissible_mask(m) and c==oracle_cost_flat[m] for m,c in observations)
    initial=initial_observations(budget,seed) if method in SURROGATES else []
    if initial:assert observations[:len(initial)]==initial
    best=min(c for _,c in observations)
    result=dict(method=method,budget=budget,seed=seed,best_cost=float(best),regret=float(best-best_cost),
        objective_evaluations=len(observations),feasible=True,initial_masks=[m for m,_ in initial],
        observations=observations,wall_seconds=time.perf_counter()-start)
    return result,trace,raw,history


def benchmark(out,workers,pilot=False):
    require_mapping(out)
    budgets=[10] if pilot else BUDGETS;seeds=range(2) if pilot else range(30)
    jobs=[(m,b,s) for b in budgets for m in METHODS for s in seeds]
    prefix="pilot_" if pilot else ""
    configuration=dict(baseline=BASE,execution_commit=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip(),
        source_sha256=source_hashes(),runner_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        methods=METHODS,budgets=budgets,seeds=list(seeds),workers=workers,primary_cardinality=6,
        fitted_beta_limit=BETA_RATIO_LIMIT,p=1,training_shots=256,final_shots=1024,cobyla_maxiter=30,
        mixer="Independent Rx(2*beta) on each qubit",ridge=.001,surrogate_pool=5000,fallback_pool=5000,
        initial_rule="min(max(10,B//4), B-1); same original rejection-sampling stream per seed",
        exhaustive_tie_break="Lowest mask integer among exactly equal floating predictions",
        statistical_plan=dict(bootstrap_resamples=10000,paired_permutation_resamples=100000,seed=20261003,
            tie_tolerance=1e-12,principal_holm_family="QAOA vs Exhaustive, four budgets",sd_ddof=0),
        optional_robustness="Not part of required primary run; no post-result algorithm tuning",
        frozen_qaoa_selection="COBYLA on sampled surrogate expectation with existing 1000 infeasible/seen barrier; final sampled minimum predicted cost, then historical fallback",
        pilot=pilot,python=platform.python_version(),platform=platform.platform())
    write_json(out/(prefix+"run_configuration.json"),configuration)
    env=subprocess.check_output([os.sys.executable,"-m","pip","freeze"],text=True)
    (out/"environment.txt").write_text(f"Python {platform.python_version()}\n{platform.platform()}\n\n"+env)
    traces=[];runs=[]
    with (out/(prefix+"raw_runs.jsonl")).open("w") as runfile, gzip.open(out/(prefix+"qaoa_final_samples.jsonl.gz"),"wt") as samples, gzip.open(out/(prefix+"qaoa_optimizer_history.jsonl.gz"),"wt") as hist:
        for result,trace,raw,history in Parallel(n_jobs=workers,backend="loky",return_as="generator_unordered",verbose=10)(delayed(run_job)(m,b,s) for m,b,s in jobs):
            runfile.write(json.dumps(result,allow_nan=False)+"\n");runfile.flush();runs.append(result);traces.extend(trace)
            for row in raw:samples.write(json.dumps(row)+"\n")
            for row in history:hist.write(json.dumps(row)+"\n")
    runs.sort(key=lambda r:(r["budget"],METHODS.index(r["method"]),r["seed"]))
    traces.sort(key=lambda r:(r["budget"],r["seed"],r["adaptive_step"]))
    write_csv(out/(prefix+"optimizer_runs.csv"),({k:v for k,v in r.items() if k not in ("observations","initial_masks")} for r in runs))
    write_csv(out/(prefix+"qaoa_trace.csv"),traces)
    write_csv(out/(prefix+"initial_samples_by_seed.csv"),(dict(budget=b,seed=s,initial_order=i+1,mask=m,true_objective=c)
        for b in budgets for s in seeds for i,(m,c) in enumerate(initial_observations(b,s))))
    assert len(runs)==len(jobs)
    print(f"Completed {len(runs)} runs; {len(traces)} QAOA adaptive steps",flush=True)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action",choices=["mapping","model","benchmark","statistics","figures","check","all"])
    parser.add_argument("--output",type=Path,default=ROOT/"results/stage3_validated")
    parser.add_argument("--jobs",type=int,default=25)
    parser.add_argument("--pilot",action="store_true")
    args=parser.parse_args();out=args.output.resolve();out.mkdir(parents=True,exist_ok=True)
    if out==ROOT/"results/stage3_controlled":raise ValueError("Controlled results are protected")
    verify_scope(out)
    if args.action in ("mapping","model","benchmark","all"):
        notebook=load_notebook();save_domain(out)
    if args.action in ("mapping","all"):mapping_validation(out,notebook)
    if args.action in ("model","all"):model_validation(out,args.jobs)
    if args.action in ("benchmark","all"):benchmark(out,args.jobs,args.pilot)
    if args.action in ("statistics","figures","check","all"):
        import stage3_validation_analysis as analysis
        if args.action in ("statistics","all"):analysis.statistics(out)
        if args.action in ("figures","all"):analysis.figures(out)
        if args.action in ("check","all"):analysis.check(out)


if __name__=="__main__":main()
