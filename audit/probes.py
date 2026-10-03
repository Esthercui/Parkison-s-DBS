"""Deterministic call-path probes; doubles are not optimizer performance runs."""
from types import SimpleNamespace
from contextlib import contextmanager
import sys
from unittest.mock import patch
import numpy as np
from .bounded_core import BudgetedOracle, BudgetExceeded, Domain, LegacyOracleView

@contextmanager
def temporary_modules(replacements):
    # Restore only our test doubles. Clearing sys.modules would remove lazily
    # imported native NumPy modules and make a second import unsafe.
    missing=object()
    previous={name:sys.modules.get(name,missing) for name in replacements}
    sys.modules.update(replacements)
    try: yield
    finally:
        for name,value in previous.items():
            if value is missing: sys.modules.pop(name,None)
            else: sys.modules[name]=value

class ReadSpy:
    def __init__(self):
        self.size=1<<16
        self.reads=[]
    def __len__(self): return self.size
    def __getitem__(self,mask):
        self.reads.append(int(mask))
        return float(int(mask).bit_count())

class FakeCMA:
    def __init__(self,*args,**kwargs): self.done=False
    def stop(self): return self.done
    def ask(self):
        return [np.array([(m>>i)&1 for i in range(16)],dtype=float) for m in range(1,19)]
    def tell(self,*args): self.done=True

class GateRecorder:
    def __init__(self,n): self.n=n;self.global_phase=0.;self.gates=[]
    def h(self,*args): pass
    def rz(self,angle,i): self.gates.append(('z',float(angle),i))
    def rzz(self,angle,i,j): self.gates.append(('zz',float(angle),i,j))
    def rx(self,*args): pass
    def measure_all(self): pass

def cma_leak_probe(env):
    fake=SimpleNamespace(CMAEvolutionStrategy=FakeCMA)
    with temporary_modules({'cma':fake}):
        spy=ReadSpy()
        reported=env['run_cma_es'](spy,10,1)
        guarded=BudgetedOracle(lambda m:float(m.bit_count()),10,Domain(16,True),evaluation_kind='synthetic_call_path_probe')
        stopped=False
        try: env['run_cma_es'](LegacyOracleView(guarded),10,1)
        except BudgetExceeded: stopped=True
    return dict(probe='historical CMA function with deterministic 18-member ask/tell double; not real CMA optimization',
                unguarded_reported=len(reported),unguarded_reads=len(spy.reads),
                unguarded_unique_masks=len(set(spy.reads)),guard_stopped=stopped,guard=guarded.report())

def qaoa_path_probe(env, *, fallback=False):
    # Historical seed-0 initialization contains these masks. Sampling only one
    # of them exercises the random-pool fallback; sampling zero exercises the
    # regular unseen-candidate branch. No quantum simulator runs here.
    first=int(np.random.default_rng(0).integers(0,1<<16))
    mask=first if fallback else 0
    counts={format(mask,'016b'):16}
    class FakeSampler:
        def run(self,circuits,shots):
            pub=SimpleNamespace(data=SimpleNamespace(meas=SimpleNamespace(get_counts=lambda:counts)))
            return SimpleNamespace(result=lambda:[pub])
    def fake_minimize(fun,x0,**kwargs):
        fun(x0)
        return SimpleNamespace(x=x0)
    oracle=BudgetedOracle(lambda m:float(m.bit_count()),10,Domain(16,True),evaluation_kind='synthetic_call_path_probe')
    modules={'qiskit':SimpleNamespace(QuantumCircuit=GateRecorder),
             'qiskit_aer':SimpleNamespace(),
             'qiskit_aer.primitives':SimpleNamespace(SamplerV2=FakeSampler)}
    with temporary_modules(modules),patch('scipy.optimize.minimize',fake_minimize):
        reported=env['run_surrogate_qaoa'](LegacyOracleView(oracle),10,0,shots=16,maxiter=1,cand_pool=32)
    return dict(probe='historical QAOA with sampler/circuit/minimizer doubles; no quantum performance evidence',
                fallback=fallback,reported=len(reported),guard=oracle.report())
