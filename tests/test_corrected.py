import json
import unittest
from pathlib import Path
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector
from audit.bounded_core import BudgetedOracle, BudgetExceeded, append_cost_phase
from dbs_benchmark.model import signal,beta_power,build_stage
from dbs_benchmark.reference import simulate_stn_gpe,MAIN_PATIENT,DBSParams,SIM
from dbs_benchmark.optimize import (FiniteDomain,METHODS,shared_initial,run,
                                    qaoa_state,predict_all,fit_surrogate,bit_matrix)

class Corrected(unittest.TestCase):
    def test_reference_recurrence(self):
        for f,a,pw in [(0.,0.,0.),(130.,.25,.00024),(60.,1.5,.00005),(180.,2.1,.00024)]:
            _,old=simulate_stn_gpe(MAIN_PATIENT,DBSParams(f,a,pw),SIM)
            new=signal(f,a,pw)
            np.testing.assert_allclose(new,old,rtol=0,atol=2e-12)
            self.assertAlmostEqual(float(beta_power(new)),float(beta_power(old)),places=12)

    def test_trapezoid_compatibility(self):
        x=np.array([13.,15.,23.,30.]); y=np.array([.3,.9,.2,.4])
        manual=sum((x[i+1]-x[i])*(y[i]+y[i+1])/2 for i in range(3))
        self.assertEqual(float(np.trapezoid(y,x)),manual)

    def test_real_qiskit_phase_and_endianness(self):
        n=3; linear=np.array([.7,-1.2,.3]); pairs=np.array([[0.,.4,-.6],[0.,0.,.9],[0.,0.,0.]])
        coef=np.r_[.13,linear,pairs[np.triu_indices(n,1)]]
        energy=predict_all(coef,n)
        for gamma,beta in [(.31,.67),(1.2,2.1)]:
            qc=QuantumCircuit(n);qc.h(range(n));append_cost_phase(qc,gamma,.13,linear,pairs)
            qc.rx(2*beta,range(n))
            expected=np.asarray(Statevector.from_instruction(qc))
            np.testing.assert_allclose(qaoa_state(energy,gamma,beta),expected,rtol=0,atol=3e-14)

    def test_ridge_and_exhaustive_prediction(self):
        rows=[(0,.2),(3,-.4),(7,.8),(12,1.7),(15,-.6)]
        coef=fit_surrogate(rows,4,.001)
        bits=bit_matrix(np.arange(16),4)
        phi=np.column_stack([np.ones(16)]+[bits[:,i] for i in range(4)]+
                            [bits[:,i]*bits[:,j] for i in range(4) for j in range(i+1,4)])
        np.testing.assert_allclose(predict_all(coef,4),phi@coef,atol=1e-12)
        design=phi[[m for m,_ in rows]]
        primal=np.linalg.solve(design.T@design+.001*np.eye(11),design.T@np.array([y for _,y in rows]))
        np.testing.assert_allclose(coef,primal,atol=1e-11)

    def test_all_methods_share_domain_budget_and_seed(self):
        cfg=json.loads(Path('configs/smoke.json').read_text());cfg.update(stage=3,dims=None)
        coords=bit_matrix(np.arange(16),4)
        for allow in (True,False):
            feasible=np.ones(16,dtype=bool);feasible[0]=allow;feasible[7]=False
            domain=FiniteDomain(feasible,4);init=shared_initial(domain,2,5,True)
            for method in METHODS:
                traces=[]
                for repeat in range(2):
                    calls=[]
                    def objective(m): calls.append(m); return float((m-3)**2)
                    oracle=BudgetedOracle(objective,10,domain,evaluation_kind='test')
                    info=run(method,oracle,coords,init,2,cfg)
                    self.assertEqual(len(calls),10,(method,allow,info))
                    self.assertEqual(len(set(calls)),10)
                    self.assertEqual(calls[:5],init)
                    self.assertTrue(all(feasible[m] for m in calls))
                    if allow:self.assertIn(0,calls)
                    traces.append(oracle.records)
                    self.assertEqual(oracle.report()['denied'],0)
                self.assertEqual(traces[0],traces[1],method)

    def test_fresh_fit_and_both_stage3_optima(self):
        cost,feasible,_,meta=build_stage(3)
        np.testing.assert_allclose(meta['fit_coefficients'],[.9437580303537099,-.11458817038088728,.02229011277045427],atol=1e-12)
        self.assertGreater(meta['minimum_linear'],0);self.assertGreater(meta['minimum_pair'],0)
        self.assertEqual(int(cost.argmin()),0)
        self.assertEqual(int(cost[1:].argmin())+1,4096)
        self.assertAlmostEqual(cost[4096],.1736142930258106,places=12)

if __name__=='__main__':unittest.main()
