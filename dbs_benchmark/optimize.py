"""Six methods share a finite feasible domain and a budgeted scalar oracle.

QAOA uses a seeded noiseless statevector sampler, p=1, correct binary cost
phases, and finite shots for COBYLA and final proposals. No hardware is used.
"""
from dataclasses import dataclass
from numbers import Integral
import warnings
import numpy as np
from numba import njit
from scipy.optimize import minimize
from scipy.stats import norm
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import ConstantKernel, Matern
from sklearn.exceptions import ConvergenceWarning
from audit.bounded_core import BudgetedOracle

METHODS = ['Random', 'GA', 'BO', 'CMA-ES', 'Surrogate (exhaustive)', 'QAOA (p=1)']

@dataclass
class FiniteDomain:
    feasible: np.ndarray
    n_bits: int

    @property
    def size(self):
        return int(self.feasible.sum())

    def validate(self, mask):
        if isinstance(mask, bool) or not isinstance(mask, Integral):
            raise TypeError('integer setting required')
        if not 0 <= mask < len(self.feasible) or not self.feasible[mask]:
            raise ValueError('outside declared feasible domain')
        return int(mask)

def shared_initial(domain, seed, n=5, zero_control=True):
    ids = np.flatnonzero(domain.feasible)
    rng = np.random.default_rng(np.random.SeedSequence([seed, 101]))
    initial = [0] if zero_control and domain.feasible[0] else []
    remaining = ids[~np.isin(ids,initial)]
    return initial + rng.choice(remaining,n-len(initial),replace=False).astype(int).tolist()

def bit_matrix(ids,n):
    return ((np.asarray(ids)[:,None] >> np.arange(n)) & 1).astype(float)

def fit_surrogate(records,n,ridge):
    bits = bit_matrix([i for i,_ in records],n)
    phi = np.column_stack([np.ones(len(bits))]+[bits[:,i] for i in range(n)]+
                          [bits[:,i]*bits[:,j] for i in range(n) for j in range(i+1,n)])
    y = np.array([y for _,y in records])
    # Dual ridge is algebraically identical, faster when observations < features.
    return phi.T @ np.linalg.solve(phi@phi.T+ridge*np.eye(len(y)),y)

@njit(cache=True)
def predict_all(coef,n):
    out = np.empty(1<<n)
    for m in range(len(out)):
        v, col = coef[0], 1+n
        for i in range(n):
            v += coef[1+i]*((m>>i)&1)
        for i in range(n):
            for j in range(i+1,n):
                v += coef[col]*((m>>i)&1)*((m>>j)&1)
                col += 1
        out[m] = v
    return out

@njit(cache=True)
def qaoa_state(energies,gamma,beta):
    # H^n |0>; exp(-i gamma f(x)); exp(-i beta sum X).
    state = np.exp(-1j*gamma*energies)/np.sqrt(len(energies))
    c,s = np.cos(beta), -1j*np.sin(beta)
    stride = 1
    while stride < len(state):
        for block in range(0,len(state),2*stride):
            for k in range(stride):
                lo,hi = block+k,block+k+stride
                a,b = state[lo],state[hi]
                state[lo],state[hi] = c*a+s*b, s*a+c*b
        stride *= 2
    return state

def qaoa_propose(pred,available,rng,oracle,cfg):
    def samples(params,shots):
        state = qaoa_state(pred,float(params[0]),float(params[1]))
        probs = np.abs(state)**2; probs /= probs.sum()
        oracle.count('circuit_executions'); oracle.count('shots',shots)
        return rng.choice(len(pred),shots,p=probs)
    def expected(params):
        ids = samples(params,cfg['qaoa_shots'])
        return float(pred[ids].mean())
    x0 = rng.uniform(0.,np.pi,2)
    result = minimize(expected,x0,method='COBYLA',options={'maxiter':cfg['qaoa_maxiter']})
    picked = np.unique(samples(result.x,4*cfg['qaoa_shots']))
    picked = picked[available[picked]]
    # Novelty and hard feasibility are handled at proposal selection, not by
    # an exclusion penalty missing from the cost circuit. All shots are logged.
    if len(picked):
        return int(picked[np.argmin(pred[picked])]), dict(nfev=int(result.nfev),
            success=bool(result.success),fallback=False)
    return int(rng.choice(np.flatnonzero(available))), dict(nfev=int(result.nfev),
            success=bool(result.success),fallback=True)

def run(method,oracle,coords,initial,seed,cfg):
    # RNG streams do not depend on execution order or Python hash randomization.
    method_id = METHODS.index(method) if method in METHODS else 6
    rng = np.random.default_rng(np.random.SeedSequence([seed,201,method_id]))
    for key in oracle.resources:
        oracle.count(key,0)
    for mask in initial:
        oracle.evaluate(int(mask),phase='shared_initialization')
    n = oracle.domain.n_bits
    extra = dict(rejected_proposals=0, fallback_proposals=0, internal_objective_calls=0,
                 cma_full_generations=0, qaoa_solves=[])
    es = None; batch=[]; batch_x=[]; batch_y=[]; batch_requests=0
    if method=='CMA-ES':
        import cma
        best = min(oracle.records,key=lambda x:x[1])[0]
        x0 = np.clip(coords[best],.05,.95).tolist()
        es = cma.CMAEvolutionStrategy(x0,cfg['cma_sigma'],
             {'seed':seed+10001,'popsize':cfg['cma_population'],
              'bounds':[0.,1.],'verbose':-9,'verb_log':0})
    while oracle.attempted < oracle.budget:
        available = oracle.domain.feasible.copy()
        seen = [i for i,_ in oracle.records]
        available[seen] = False
        remaining = np.flatnonzero(available)
        if method=='Random':
            pick = int(rng.choice(remaining))
        elif method=='Sparse-first':
            counts = np.array([int(x).bit_count() for x in remaining])
            pick = int(rng.choice(remaining[counts==counts.min()]))
        elif method=='GA':
            def parent():
                sample = rng.choice(len(oracle.records),min(3,len(seen)),replace=False)
                return min((oracle.records[i] for i in sample),key=lambda x:x[1])[0]
            for _ in range(cfg['proposal_retry_limit']):
                a,b = parent(),parent()
                cut = int(rng.integers(1,n)); mask = (1<<cut)-1
                pick = (a & ~mask) | (b & mask)
                flips = rng.random(n)<1/n
                for bit in np.flatnonzero(flips): pick ^= 1<<int(bit)
                if available[pick]: break
                extra['rejected_proposals'] += 1
            else:
                pick = int(rng.choice(remaining)); extra['fallback_proposals'] += 1
        elif method=='BO':
            kernel = ConstantKernel(1.,(1e-3,1e3))*Matern(nu=2.5)
            gp = GaussianProcessRegressor(kernel=kernel,alpha=1e-10,normalize_y=True,
                    random_state=seed,n_restarts_optimizer=cfg['bo_restarts'])
            y = np.array([y for _,y in oracle.records])
            with warnings.catch_warnings():
                warnings.simplefilter('ignore',ConvergenceWarning)
                gp.fit(coords[seen],y)
            oracle.count('surrogate_fits')
            best_ei, pick = -np.inf,None
            for lo in range(0,len(remaining),4096):
                ids = remaining[lo:lo+4096]
                mu,sd = gp.predict(coords[ids],return_std=True)
                sd = np.maximum(sd,1e-12)
                improvement = y.min()-mu-cfg['bo_xi']; z = improvement/sd
                ei = improvement*norm.cdf(z)+sd*norm.pdf(z)
                k = int(np.argmax(ei))
                if ei[k]>best_ei: best_ei,pick = float(ei[k]),int(ids[k])
                oracle.count('surrogate_predictions',len(ids))
        elif method=='CMA-ES':
            if not batch:
                batch = list(es.ask()); batch_x=[]; batch_y=[]
                batch_requests += 1
            x = batch.pop(0)
            if cfg['stage']==3:
                bits = np.asarray(x)>.5
                # Empty remains accessible whenever feasible; never auto-activate.
                pick = int(sum(int(v)<<i for i,v in enumerate(bits)))
            else:
                dims = cfg['dims']
                indices = np.rint(np.clip(x,0,1)*(np.array(dims)-1)).astype(int)
                pick = int(np.ravel_multi_index(tuple(indices),dims))
            if not oracle.domain.feasible[pick]:
                extra['rejected_proposals'] += 1
                value = 1e6 # known feasibility penalty, no objective read
            else:
                value = oracle.evaluate(pick,phase='cma_population')
                extra['internal_objective_calls'] += 1
            batch_x.append(x); batch_y.append(value)
            if not batch:
                es.tell(batch_x,batch_y); extra['cma_full_generations'] += 1
            if oracle.attempted>=oracle.budget: break
            if batch_requests>cfg['proposal_retry_limit']:
                extra['fallback_proposals'] += 1
                oracle.evaluate(int(rng.choice(remaining)),phase='cma_stagnation_fallback')
            continue
        else:
            coef = fit_surrogate(oracle.records,n,cfg['ridge'])
            oracle.count('surrogate_fits')
            pred = predict_all(coef,n)
            oracle.count('surrogate_predictions',len(pred))
            if method=='Surrogate (exhaustive)':
                pick = int(remaining[np.argmin(pred[remaining])])
            elif method=='QAOA (p=1)':
                pick, info = qaoa_propose(pred,available,rng,oracle,cfg)
                extra['qaoa_solves'].append(info)
                extra['fallback_proposals'] += int(info['fallback'])
                extra['internal_objective_calls'] += info['nfev']
            else: raise ValueError(method)
        oracle.count('optimizer_steps')
        oracle.evaluate(pick,phase='optimizer_proposal')
    if es is not None: oracle.count('optimizer_steps',batch_requests)
    return extra
