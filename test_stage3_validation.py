"""Targeted tests of the four requested Stage 3 changes."""
import ast
import json
from pathlib import Path
import subprocess
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import numpy as np
import validate_stage3 as runner
from stage3_validation_core import (binary_to_ising, binary_values, ising_values,
    bits_for_masks, fit_surrogate, exhaustive_proposal)


class Stage3ValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        runner.load_notebook()

    def test_full_space_energy_equivalence(self):
        rng=np.random.default_rng(98);bits=bits_for_masks(np.arange(65536))
        a=rng.normal(size=16);b=np.triu(rng.normal(size=(16,16)),1);c=.923
        error=np.max(np.abs(binary_values(bits,c,a,b)-ising_values(bits,*binary_to_ising(c,a,b))))
        self.assertLessEqual(error,1e-10)

    def test_shared_fit_matches_original(self):
        baseline=json.loads(subprocess.check_output(["git","show",runner.BASE+":stage3.ipynb"],cwd=runner.ROOT))
        tree=ast.parse("".join(baseline["cells"][7]["source"]))
        outer=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=="run_surrogate_qaoa")
        functions=[n for n in outer.body if isinstance(n,ast.FunctionDef) and n.name in ("quad_design","fit_surrogate")]
        scope=dict(np=np,mask_to_bits=runner.mask_to_bits,bitlen=16,ridge=.001)
        exec(compile(ast.Module(body=functions,type_ignores=[]),"historical_fit","exec"),scope)
        observations=runner.initial_observations(40,17)
        for old,new in zip(scope["fit_surrogate"](observations),fit_surrogate(observations)):
            np.testing.assert_array_equal(old,new)

    def test_exhaustive_selection_and_tie_rule(self):
        initial=runner.initial_observations(40,17);seen={m for m,_ in initial}
        c,a,b=fit_surrogate(initial)
        selected,prediction,count=exhaustive_proposal(runner.ADMISSIBLE_MASKS,seen,c,a,b)
        values=[]
        for m in runner.ADMISSIBLE_MASKS:
            if int(m) in seen:continue
            bits=runner.mask_to_bits(int(m));v=c+float(a@bits)
            for i in range(16):
                for j in range(i+1,16):v+=float(b[i,j]*bits[i]*bits[j])
            values.append((v,int(m)))
        self.assertAlmostEqual(prediction,min(v for v,_ in values),places=10)
        self.assertNotIn(selected,seen);self.assertEqual(count,len(values))
        tied=exhaustive_proposal(runner.ADMISSIBLE_MASKS,seen,0.,np.zeros(16),np.zeros((16,16)))[0]
        self.assertEqual(tied,min(int(m) for m in runner.ADMISSIBLE_MASKS if int(m) not in seen))

    def test_matched_initial_observations(self):
        expected=runner.initial_observations(12,17)
        for function in (runner.run_surrogate_exact,runner.run_surrogate_exhaustive,runner.run_surrogate_qaoa):
            observed=function(runner.oracle_cost_flat,12,17)
            self.assertEqual(observed[:len(expected)],expected)
            self.assertEqual(len(observed),12)
            self.assertTrue(all(runner.is_admissible_mask(m) for m,_ in observed))

    def test_instrumentation_does_not_change_proposals(self):
        plain=runner.run_surrogate_qaoa(runner.oracle_cost_flat,12,3)
        trace=[];raw=[];history=[]
        recorded=runner.run_surrogate_qaoa(runner.oracle_cost_flat,12,3,
                                         trace=trace,raw_samples=raw,circuit_history=history)
        self.assertEqual(plain,recorded)
        self.assertEqual(len(trace),2)
        for t,r in zip(trace,raw):
            self.assertEqual(sum(r['counts'].values()),1024)
            self.assertEqual(t['total_qaoa_shots'],t['cobyla_nfev']*256+1024)
            self.assertGreaterEqual(t['selected_surrogate_gap'],-1e-10)

    def test_forced_infeasible_samples_use_original_fallback(self):
        class EmptyOnlySampler:
            def __init__(self,*args,**kwargs):pass
            def run(self,circuits,shots):
                data=SimpleNamespace(meas=SimpleNamespace(get_counts=lambda:{'0'*16:shots}))
                return SimpleNamespace(result=lambda:[SimpleNamespace(data=data)])
        trace=[]
        with patch('qiskit_aer.primitives.SamplerV2',EmptyOnlySampler):
            observations=runner.run_surrogate_qaoa(runner.oracle_cost_flat,10,0,trace=trace)
        self.assertEqual(trace[0]['proposal_source'],'CLASSICAL_FALLBACK')
        self.assertEqual(trace[0]['fallback_pool_draws'],5000)
        self.assertEqual(trace[0]['unseen_admissible_unique'],0)
        self.assertTrue(runner.is_admissible_mask(observations[-1][0]))


if __name__=='__main__':unittest.main()
