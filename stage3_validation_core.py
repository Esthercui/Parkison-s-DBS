"""Only the Stage 3 surrogate, Ising conversion, and proposal diagnostics."""
import numpy as np
from qiskit import QuantumCircuit


def bits_for_masks(masks, n=16):
    return ((np.asarray(masks, dtype=np.int64)[:, None] >> np.arange(n)) & 1).astype(float)


def quad_design(bits):
    m, n = bits.shape
    phi = np.zeros((m, 1 + n + n*(n-1)//2), dtype=float)
    phi[:, 0] = 1.0
    phi[:, 1:1+n] = bits
    col = 1+n
    for i in range(n):
        for j in range(i+1, n):
            phi[:, col] = bits[:, i]*bits[:, j]
            col += 1
    return phi


def fit_surrogate(evaluations, n=16, ridge=1e-3):
    # Same design order, primal ridge solve, and intercept regularization as baseline.
    bits = bits_for_masks([m for m, _ in evaluations], n)
    y = np.array([v for _, v in evaluations], dtype=float)
    phi = quad_design(bits)
    theta = np.linalg.solve(phi.T @ phi + ridge*np.eye(phi.shape[1]), phi.T @ y)
    pair = np.zeros((n, n), dtype=float)
    col = 1+n
    for i in range(n):
        for j in range(i+1, n):
            pair[i, j] = theta[col]
            col += 1
    return float(theta[0]), theta[1:1+n].copy(), pair


def binary_values(bits, constant, linear, pair):
    values = constant + bits @ linear
    for i in range(len(linear)):
        for j in range(i+1, len(linear)):
            values += pair[i, j]*bits[:, i]*bits[:, j]
    return values


def binary_to_ising(constant, linear, pair):
    """Upper-triangular binary pair coefficients; x_i=(1-Z_i)/2."""
    linear = np.asarray(linear, dtype=float)
    pair = np.asarray(pair, dtype=float)
    if pair.shape != (len(linear), len(linear)) or np.any(np.tril(pair) != 0):
        raise ValueError("Pair coefficients must be strictly upper triangular")
    offset = float(constant + linear.sum()/2 + pair.sum()/4)
    h = -linear/2 - (pair.sum(axis=0) + pair.sum(axis=1))/4
    return offset, h, pair/4


def ising_values(bits, offset, h, coupling):
    z = 1-2*bits
    values = offset + z @ h
    for i in range(len(h)):
        for j in range(i+1, len(h)):
            values += coupling[i, j]*z[:, i]*z[:, j]
    return values


def binary_cost_layer(gamma, linear, pairs):
    n = len(linear)
    pair = np.zeros((n, n))
    for i, j, value in pairs:
        pair[i, j] = value
    _, h, coupling = binary_to_ising(0.0, linear, pair)
    circuit = QuantumCircuit(n)
    for i, value in enumerate(h):
        if value != 0:
            circuit.rz(2*gamma*float(value), i)
    # Preserve the original pair order. All cost-layer Z/ZZ gates commute.
    for i, j, _ in pairs:
        if coupling[i, j] != 0:
            circuit.rzz(2*gamma*float(coupling[i, j]), i, j)
    return circuit


def exhaustive_proposal(admissible_masks, evaluated, constant, linear, pair):
    available = np.array([m for m in admissible_masks if int(m) not in evaluated], dtype=int)
    if not len(available):
        raise ValueError("No unseen admissible candidate")
    available.sort()
    predictions = binary_values(bits_for_masks(available, len(linear)), constant, linear, pair)
    index = int(np.argmin(predictions))
    # Sorted masks make exact floating-point prediction ties choose the lowest mask.
    return int(available[index]), float(predictions[index]), len(available)


def sampled_diagnostics(counts, evaluated, active_count, beta_ratio, feasible, limit):
    masks = np.array(sorted(counts), dtype=int)
    weights = np.array([counts[int(m)] for m in masks], dtype=int)
    exact_k = active_count[masks] == 6
    beta_pass = beta_ratio[masks] <= limit
    admissible = feasible[masks]
    unseen = admissible & np.array([int(m) not in evaluated for m in masks])
    best = lambda valid: (int(masks[np.flatnonzero(valid)[np.argmax(weights[valid])]])
                          if valid.any() else None)
    shots = int(weights.sum())
    return dict(shots=shots, unique_sampled=int(len(masks)),
        exactly_six_shots=int(weights[exact_k].sum()), exactly_six_unique=int(exact_k.sum()),
        beta_threshold_shots=int(weights[beta_pass].sum()), beta_threshold_unique=int(beta_pass.sum()),
        admissible_shots=int(weights[admissible].sum()), unique_admissible=int(admissible.sum()),
        unseen_admissible_unique=int(unseen.sum()),
        admissible_shot_fraction=float(weights[admissible].sum()/shots),
        empirical_admissible_mass=float(weights[admissible].sum()/shots),
        highest_probability_sampled_mask=best(np.ones(len(masks), dtype=bool)),
        highest_probability_admissible_mask=best(admissible))
