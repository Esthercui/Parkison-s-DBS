"""Frozen scientific reference from historical Stage 3 cell 1.
Only numerical API compatibility change: np.trapz -> np.trapezoid.
The optimized engine is checked against this original Python recurrence.
"""
from dataclasses import dataclass
from typing import Optional, Tuple
import numpy as np
from scipy.signal import welch

def beta_band_power(signal: np.ndarray, fs: float, band: Tuple[float, float]=(13.0, 30.0)) -> float:
    f, P = welch(signal, fs=fs, nperseg=min(len(signal), 8192))
    lo, hi = band
    mask = (f >= lo) & (f <= hi)
    return float(np.trapezoid(P[mask], f[mask]))

def tanh_act(x: float, gain: float) -> float:
    return float(np.tanh(gain * x))

@dataclass(frozen=True)
class STNGPePatient:
    tau_stn: float
    tau_gpe: float
    delay_stn_to_gpe: float
    delay_gpe_to_stn: float
    w_stn_to_gpe: float
    w_gpe_to_stn: float
    I_cort: float
    I_gpe_bias: float
    gain_stn: float
    gain_gpe: float
    noise_std: float = 0.0

@dataclass(frozen=True)
class DBSParams:
    f_hz: float
    A: float
    pw_s: float

@dataclass(frozen=True)
class SimParams:
    T: float = 2.0
    dt: float = 0.0001
    discard: float = 0.2
    seed: int = 0
SIM = SimParams(T=2.0, dt=0.0001, discard=0.2, seed=0)
BETA_BAND = (13.0, 30.0)
MAIN_PATIENT = STNGPePatient(tau_stn=0.009480108684355502, tau_gpe=0.01568342986890998, delay_stn_to_gpe=0.005856049933455449, delay_gpe_to_stn=0.004355096988711622, w_stn_to_gpe=0.8766085173129406, w_gpe_to_stn=0.8007248587605185, I_cort=0.21584549577209655, I_gpe_bias=0.0, gain_stn=2.418440027526686, gain_gpe=2.4195288944990088, noise_std=0.0)

def simulate_stn_gpe(patient: STNGPePatient, dbs: Optional[DBSParams], sim: SimParams):
    rng = np.random.default_rng(sim.seed)
    n = int(sim.T / sim.dt)
    t = np.arange(n) * sim.dt
    stn = np.zeros(n, dtype=float)
    gpe = np.zeros(n, dtype=float)
    stn[0], gpe[0] = (0.1, 0.1)
    d_sg = max(1, int(patient.delay_stn_to_gpe / sim.dt))
    d_gs = max(1, int(patient.delay_gpe_to_stn / sim.dt))
    if dbs is None or dbs.A == 0 or dbs.f_hz == 0 or (dbs.pw_s == 0):
        f = 0.0
        A = 0.0
        pw = 0.0
    else:
        f = float(dbs.f_hz)
        A = float(dbs.A)
        pw = float(dbs.pw_s)
    period = 1.0 / f if f > 0 else None
    next_pulse = 0.0
    pulse_end = -1.0
    for k in range(n - 1):
        tt = t[k]
        Idbs = 0.0
        if f > 0:
            if tt >= next_pulse:
                pulse_end = next_pulse + pw
                next_pulse += period
            if tt < pulse_end:
                Idbs = A
        stn_del = stn[k - d_sg] if k >= d_sg else stn[0]
        gpe_del = gpe[k - d_gs] if k >= d_gs else gpe[0]
        ns = patient.noise_std * rng.standard_normal()
        ng = patient.noise_std * rng.standard_normal()
        inp_stn = patient.I_cort - patient.w_gpe_to_stn * gpe_del + Idbs + ns
        inp_gpe = patient.w_stn_to_gpe * stn_del + patient.I_gpe_bias + ng
        Fstn = tanh_act(inp_stn, patient.gain_stn)
        Fgpe = tanh_act(inp_gpe, patient.gain_gpe)
        dstn = (-stn[k] + Fstn) / patient.tau_stn
        dgpe = (-gpe[k] + Fgpe) / patient.tau_gpe
        stn[k + 1] = stn[k] + sim.dt * dstn
        gpe[k + 1] = gpe[k] + sim.dt * dgpe
    start = int(sim.discard / sim.dt)
    y = (stn - gpe)[start:]
    tt = t[start:]
    return (tt, y)
