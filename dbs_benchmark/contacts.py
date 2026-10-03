"""Unchanged contact geometry and QUBO formula; freshly fitted coefficients required."""
import numpy as np
N_CONTACTS = 16
F_HZ = 130.0
PW_US = 240.0
PW_S = PW_US * 1e-06
A_UNIT = 0.25
A_MAX = 1.5
PW_MAX_US = 240.0
PW_MAX_S = PW_MAX_US * 1e-06
LAMBDA_COUNT = 0.18
LAMBDA_ENERGY = 0.2
LAMBDA_RISK = 0.22
LAMBDA_OVERLAP = 0.3
LAMBDA_QD = 0.4
QD_SOFT_TARGET = 0.55
INFEAS_COST = 1000000.0
QAOA_P = 1
QAOA_SHOTS = 256
QAOA_MAXITER = 30
CONTACT_NAMES = [f'C{i}' for i in range(N_CONTACTS)]
CONTACT_MODE = np.array(['ring'] * 8 + ['directional'] * 8)
AREA_FACTOR = np.array([1.0, 1.0, 0.95, 0.95, 0.9, 0.9, 0.85, 0.85, 0.7, 0.68, 0.66, 0.64, 0.62, 0.6, 0.58, 0.56])
IMP_FACTOR = np.array([1.0, 1.02, 1.04, 1.06, 1.08, 1.1, 1.12, 1.14, 1.2, 1.24, 1.28, 1.32, 1.36, 1.4, 1.44, 1.48])
FOCUS = np.array([0.88, 0.92, 0.96, 1.0, 1.03, 1.01, 0.97, 0.93, 0.95, 1.02, 1.12, 1.22, 1.28, 1.18, 1.05, 0.96])
RISK = np.array([0.22, 0.2, 0.17, 0.14, 0.12, 0.13, 0.16, 0.19, 0.14, 0.11, 0.08, 0.06, 0.05, 0.07, 0.1, 0.13])
OVERLAP = np.zeros((N_CONTACTS, N_CONTACTS), dtype=float)

def circular_dist(i, j, n):
    d = abs(i - j)
    return min(d, n - d)
for i in range(N_CONTACTS):
    for j in range(i + 1, N_CONTACTS):
        d = circular_dist(i, j, N_CONTACTS)
        base = 0.0
        if d == 1:
            base = 1.0
        elif d == 2:
            base = 0.45
        elif d == 3:
            base = 0.15
        if CONTACT_MODE[i] == 'ring' and CONTACT_MODE[j] == 'ring':
            mult = 1.25
        elif CONTACT_MODE[i] == 'directional' and CONTACT_MODE[j] == 'directional':
            mult = 0.7
        else:
            mult = 1.0
        OVERLAP[i, j] = base * mult
        OVERLAP[j, i] = OVERLAP[i, j]
def mask_to_bits(mask: int, n: int=N_CONTACTS) -> np.ndarray:
    return np.array([mask >> i & 1 for i in range(n)], dtype=float)

def bits_to_mask(bits: np.ndarray) -> int:
    return int(sum((int(bits[i]) << i for i in range(N_CONTACTS))))
QD_PROXY = A_UNIT / A_MAX * (PW_S / PW_MAX_S) / AREA_FACTOR
QD_SOFT_PEN = np.maximum(0.0, QD_PROXY - QD_SOFT_TARGET) ** 2

def build_Q(c1, c2):
    n = N_CONTACTS
    Q = np.zeros((n, n), dtype=float)
    for i in range(n):
        Q[i, i] += LAMBDA_COUNT
    for i in range(n):
        Q[i, i] += float(LAMBDA_ENERGY * A_UNIT ** 2 * IMP_FACTOR[i])
    for i in range(n):
        Q[i, i] += float(LAMBDA_RISK * RISK[i])
    for i in range(n):
        Q[i, i] += float(LAMBDA_QD * QD_SOFT_PEN[i])
    for i in range(n):
        for j in range(i + 1, n):
            Q[i, j] += float(LAMBDA_OVERLAP * OVERLAP[i, j])
    for i in range(n):
        Q[i, i] += float(c1 * A_UNIT * FOCUS[i])
    for i in range(n):
        Q[i, i] += float(c2 * A_UNIT ** 2 * FOCUS[i] ** 2)
    for i in range(n):
        for j in range(i + 1, n):
            Q[i, j] += float(2 * c2 * A_UNIT ** 2 * FOCUS[i] * FOCUS[j])
    return Q
