"""Deterministic reference dynamics, accelerated without fastmath.

Only the historical noise-free instance is supported. No patient data are used.
"""
import time
import numpy as np
from numba import njit, prange
from scipy.signal import welch
from .reference import MAIN_PATIENT, SIM
from .contacts import build_Q

P = np.array([MAIN_PATIENT.tau_stn, MAIN_PATIENT.tau_gpe,
              MAIN_PATIENT.delay_stn_to_gpe, MAIN_PATIENT.delay_gpe_to_stn,
              MAIN_PATIENT.w_stn_to_gpe, MAIN_PATIENT.w_gpe_to_stn,
              MAIN_PATIENT.I_cort, MAIN_PATIENT.I_gpe_bias,
              MAIN_PATIENT.gain_stn, MAIN_PATIENT.gain_gpe])

@njit(cache=True)
def signal(f, A, pw, p=P, dt=SIM.dt, duration=SIM.T, discard=SIM.discard):
    n = int(duration / dt)
    stn, gpe = np.zeros(n), np.zeros(n)
    stn[0] = gpe[0] = 0.1
    d_sg, d_gs = max(1, int(p[2]/dt)), max(1, int(p[3]/dt))
    if A == 0 or f == 0 or pw == 0:
        f = 0.0
    period = 1/f if f > 0 else 0.0
    next_pulse, pulse_end = 0.0, -1.0
    for k in range(n-1):
        tt, Idbs = k*dt, 0.0
        if f > 0:
            if tt >= next_pulse:
                pulse_end = next_pulse + pw
                next_pulse += period
            if tt < pulse_end:
                Idbs = A
        sd = stn[k-d_sg] if k >= d_sg else stn[0]
        gd = gpe[k-d_gs] if k >= d_gs else gpe[0]
        fs = np.tanh(p[8]*(p[6]-p[5]*gd+Idbs))
        fg = np.tanh(p[9]*(p[4]*sd+p[7]))
        stn[k+1] = stn[k]+dt*((-stn[k]+fs)/p[0])
        gpe[k+1] = gpe[k]+dt*((-gpe[k]+fg)/p[1])
    return (stn-gpe)[int(discard/dt):]

@njit(parallel=True, cache=True)
def signal_batch(settings):
    out = np.empty((len(settings), int(SIM_T / SIM_DT)-int(SIM_DISCARD / SIM_DT)))
    for i in prange(len(settings)):
        out[i] = signal(settings[i,0], settings[i,1], settings[i,2])
    return out

SIM_T, SIM_DT, SIM_DISCARD = SIM.T, SIM.dt, SIM.discard
# Match the historical sample-time subtraction, including its rounding.
FS = 1.0 / ((int(SIM.discard/SIM.dt)+1)*SIM.dt-int(SIM.discard/SIM.dt)*SIM.dt)

def beta_power(y):
    f, psd = welch(y, fs=FS, nperseg=min(y.shape[-1], 8192), axis=-1)
    take = (f >= 13) & (f <= 30)
    return np.trapezoid(psd[...,take], f[take], axis=-1)

def simulate_settings(settings, chunk=128):
    out = np.empty(len(settings))
    for lo in range(0, len(settings), chunk):
        out[lo:lo+chunk] = beta_power(signal_batch(settings[lo:lo+chunk]))
    return out

def knee(beta, energy, feasible):
    ids = np.flatnonzero(feasible)
    # Explicit stable tie rule: lower beta, then lower energy, then mask.
    order = ids[np.lexsort((ids, energy[ids], beta[ids]))]
    front, best = [], np.inf
    for i in order:
        if energy[i] < best:
            front.append(i); best = energy[i]
    b,e = beta[front],energy[front]
    dist = ((b-b.min())/(np.ptp(b)+1e-12))**2 + ((e-e.min())/(np.ptp(e)+1e-12))**2
    return int(front[int(np.argmin(dist))])

def build_stage(stage, grid=(64,64,16), allow_empty=True):
    start = time.perf_counter()
    baseline = float(beta_power(signal(0.,0.,0.)))
    meta = dict(stage=stage, baseline_beta=baseline, simulator_seed=0,
                simulator_noise_std=0.0, fs=FS)
    if stage == 3:
        amp = np.linspace(0.,4.,41)
        settings = np.column_stack((np.full(41,130.),amp,np.full(41,240e-6)))
        ratios = simulate_settings(settings)/(baseline+1e-12)
        design = np.column_stack((np.ones(41),amp,amp**2))
        coef = np.linalg.lstsq(design,ratios,rcond=None)[0]
        q = build_Q(coef[1],coef[2])
        ids = np.arange(1<<16)
        coords = ((ids[:,None] >> np.arange(16))&1).astype(float)
        cost = np.einsum('bi,ij,bj->b',coords,q,coords,optimize=True)
        feasible = np.ones(len(ids),dtype=bool); feasible[0] = allow_empty
        residual = ratios-design@coef
        meta.update(grid=None, n_bits=16, simulator_evaluations=42,
                    fit_coefficients=coef.tolist(), fit_amplitudes=amp.tolist(),
                    fit_ratios=ratios.tolist(), fit_rmse=float(np.sqrt(np.mean(residual**2))),
                    fit_max_abs_error=float(np.max(np.abs(residual))),
                    minimum_linear=float(np.diag(q).min()),
                    minimum_pair=float(q[np.triu_indices(16,1)].min()),
                    allow_empty=allow_empty, objective_kind='fitted_qubo_lookup',
                    intercept_dropped=float(coef[0]), Q=q.tolist())
    else:
        dims = tuple(grid)+( (2,) if stage==2 else () )
        indices = np.array(np.unravel_index(np.arange(np.prod(dims)),dims)).T
        coords = indices/(np.array(dims)-1)
        f = np.linspace(60,180,grid[0])[indices[:,0]]
        a = np.linspace(0,1.5,grid[1])[indices[:,1]]
        pw = np.linspace(50,240,grid[2])[indices[:,2]]*1e-6
        mode = indices[:,3] if stage==2 else np.zeros(len(f),dtype=int)
        qd = (a/1.5)*(pw/240e-6)/np.array([1.,.25])[mode]
        feasible = qd<=.60 if stage==2 else np.ones(len(f),dtype=bool)
        energy = (a/1.5)**2*(f/180)*(pw/240e-6)*np.array([1.,2.])[mode]
        ae = a*np.array([1.,1.4])[mode]
        beta = np.full(len(f),np.inf)
        settings = np.column_stack((f[feasible],ae[feasible],pw[feasible]))
        beta[feasible] = simulate_settings(settings)/(baseline+1e-12)
        ki = knee(beta,energy,feasible)
        cost = beta+5*np.maximum(0.,energy-energy[ki])
        meta.update(grid=list(dims), n_bits=int(np.log2(len(f))),
                    simulator_evaluations=1+int(feasible.sum()),
                    knee_mask=ki, knee_energy=float(energy[ki]),
                    objective_kind='cached_simulator_objective', penalty=5.,
                    qd_limit=.60 if stage==2 else None)
    best = int(np.flatnonzero(feasible)[np.argmin(cost[feasible])])
    meta.update(domain_size=int(feasible.sum()), ground_truth_mask=best,
                ground_truth_cost=float(cost[best]), build_seconds=time.perf_counter()-start)
    return cost,feasible,coords,meta
