import cmath
import itertools
import unittest
import numpy as np
from audit.bounded_core import (Domain,BudgetedOracle,BudgetExceeded,InfeasibleMask,
    LegacyOracleView,decode_threshold,minimize_surrogate_exhaustive,quadratic_values,
    qubo_to_ising,append_cost_phase,run_surrogate_exhaustive)
from audit.historical import load_stage3
from audit.probes import GateRecorder,cma_leak_probe,qaoa_path_probe

class AuditTests(unittest.TestCase):
    def test_cache_initialization_failure_and_post_budget(self):
        calls=[]
        def cost(m): calls.append(m);return float(m)
        o=BudgetedOracle(cost,2,Domain(3,True),evaluation_kind='test')
        self.assertEqual(o.evaluate(0,phase='initialization'),0)
        self.assertEqual(o.evaluate(0),0)
        self.assertEqual(o.evaluate(1),1)
        self.assertEqual(o.evaluate(1),1)
        with self.assertRaises(BudgetExceeded): o.evaluate(2)
        self.assertEqual(calls,[0,1]);self.assertEqual(o.attempted,2)
        self.assertEqual(o.report()['cache_hits'],2)
        self.assertTrue(o.events[-2]['post_budget'])
        self.assertEqual(o.events[-1]['status'],'budget_denied')
        failing=BudgetedOracle(lambda m:float('nan'),1,Domain(1,True),evaluation_kind='test')
        with self.assertRaises(ValueError): failing.evaluate(0)
        with self.assertRaises(BudgetExceeded): failing.evaluate(0)
        self.assertEqual((failing.attempted,failing.completed),(1,0))

    def test_domain_and_array_access_cannot_bypass_budget(self):
        o=BudgetedOracle(lambda m:float(m),1,Domain(2,False),evaluation_kind='test')
        for m in (-1,4,0,1.5,True):
            with self.assertRaises((ValueError,TypeError)):o.evaluate(m)
        self.assertEqual(o.attempted,0)
        view=LegacyOracleView(o)
        with self.assertRaises(TypeError):np.asarray(view)
        with self.assertRaises(TypeError):list(view)
        with self.assertRaises(TypeError):view[:]
        self.assertEqual(view[1],1)
        with self.assertRaises(BudgetExceeded):view[2]

    def test_both_domains_are_explicit_and_consistent(self):
        for allow in (True,False):
            d=Domain(3,allow)
            bits=decode_threshold([0,0,0],d)
            self.assertEqual(int(bits.sum()),0 if allow else 1)
            result=minimize_surrogate_exhaustive(0,[1,2,3],np.zeros((3,3)),d)
            self.assertEqual(result['mask'],0 if allow else 1)
            self.assertEqual(result['masks_evaluated'],8 if allow else 7)
            self.assertEqual(d.validate(result['mask']),result['mask'])

    def test_exhaustive_surrogate_16_bits_known_optimum(self):
        linear=np.array([-1 if i%2==0 else 2 for i in range(16)])
        d=Domain(16,True)
        o=BudgetedOracle(lambda m:0,0,d,evaluation_kind='test')
        result=minimize_surrogate_exhaustive(0.75,linear,np.zeros((16,16)),d,accounting=o)
        self.assertEqual(result['mask'],sum(1<<i for i in range(0,16,2)))
        self.assertEqual(result['value'],-7.25)
        self.assertEqual(o.resources['surrogate_predictions'],65536)
        self.assertEqual(o.attempted,0)
        limited=minimize_surrogate_exhaustive(0,[1],np.zeros((1,1)),Domain(1,True),excluded=(0,))
        self.assertEqual(limited['mask'],1)

    def test_qubo_basis_energies_offsets_and_bit_order(self):
        linear=np.array([-1.2,0.8,2.3]);pairs=np.array([[0,.4,-.7],[0,0,1.1],[0,0,0]])
        constant,h,j=qubo_to_ising(.7,linear,pairs)
        gamma=.37;qc=GateRecorder(3)
        append_cost_phase(qc,gamma,.7,linear,pairs)
        for bits in itertools.product((0,1),repeat=3):
            mask=sum(x<<i for i,x in enumerate(bits));z=1-2*np.array(bits)
            energy=.7+sum(linear[i]*bits[i] for i in range(3))+sum(pairs[i,k]*bits[i]*bits[k] for i in range(3) for k in range(i+1,3))
            ising=constant+sum(h*z)+sum(j[i,k]*z[i]*z[k] for i in range(3) for k in range(i+1,3))
            phase=qc.global_phase
            for g in qc.gates:
                phase-=g[1]/2*z[g[2]]*(z[g[3]] if g[0]=='zz' else 1)
            self.assertAlmostEqual(energy,ising,places=12)
            self.assertAlmostEqual(abs(cmath.exp(1j*phase)-cmath.exp(-1j*gamma*energy)),0,places=12)
            self.assertAlmostEqual(quadratic_values([mask],.7,linear,pairs)[0],energy,places=12)

    def test_fitted_exhaustive_baseline_charges_initial_data_and_proposals(self):
        for allow in (True,False):
            o=BudgetedOracle(lambda m:float(m.bit_count()),4,Domain(3,allow),evaluation_kind='test')
            rows=run_surrogate_exhaustive(o,[1,1,2])
            self.assertEqual(len(rows),4)
            self.assertEqual(o.attempted,4)
            self.assertEqual(o.report()['cache_hits'],1)
            self.assertEqual(o.report()['resources']['surrogate_fits'],2)
            self.assertEqual(o.report()['resources']['surrogate_predictions'],11 if allow else 9)
            self.assertEqual(o.report()['resources']['shots'],0)
            if not allow:self.assertTrue(all(m!=0 for m,_ in rows))

    def test_historical_cma_batch_leak_is_blocked(self):
        env,_=load_stage3();p=cma_leak_probe(env)
        self.assertEqual(p['unguarded_reported'],10)
        self.assertEqual(p['unguarded_unique_masks'],18)
        self.assertTrue(p['guard_stopped'])
        self.assertEqual(p['guard']['objective_attempts'],10)
        self.assertEqual(p['guard']['denied'],1)

    def test_historical_qaoa_regular_and_fallback_accesses_are_guarded(self):
        env,_=load_stage3()
        for fallback in (False,True):
            p=qaoa_path_probe(env,fallback=fallback)
            self.assertEqual(p['reported'],10)
            self.assertEqual(p['guard']['objective_attempts'],10)
            self.assertEqual(p['guard']['denied'],0)

if __name__=='__main__':unittest.main()
