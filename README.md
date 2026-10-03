# DBS contact-selection benchmark — research audit

This repository contains exploratory simulation notebooks and historical saved
outputs. It is not a validated treatment-selection system.

Start with the [Stage 3 discrepancy report](docs/discrepancy_report_v1.md) and
[minimal corrective experiment plan](docs/corrective_plan_v1.md). Historical
performance tables should not support QAOA superiority claims while their
feasibility, Hamiltonian mapping and accounting issues remain unresolved.

The original notebooks remain byte-for-byte intact:

- `stage1.ipynb`: parameter-tuning exploration.
- `stage2.ipynb`: modeled constraint exploration; no clinical validation implied.
- `stage3.ipynb`: combinatorial objective, saved benchmark and figures.

[Historical provenance](historical/README.md) identifies the preserved snapshot.
The saved Stage 3 label **“Surrogate (Exact)” means a random pool of 5,000
draws**, not exhaustive minimization. The saved table is not a corrected table.
New `audit.bounded_core.run_surrogate_exhaustive` fits the same quadratic feature
family and fully enumerates feasible, unevaluated masks at each proposal. It
solves the fitted surrogate; it does not certify the true simulator objective.

## Inexpensive reviewer checks

Using an environment with NumPy, SciPy and scikit-learn:

```bash
python -m audit.reviewer_example
python -m unittest discover -s tests -v
```

This review used the existing `studio-python` environment; exact versions are
recorded in `requirements-audit.txt`. No packages were upgraded or installed.
The example reconstructs Q from the notebook's **saved fit coefficients** and
enumerates 65,536 cheap quadratic values. It does not refit the simulator, run
the 720-job sweep, use a Qiskit simulator, or generate a revised performance
table. CMA and QAOA call-path checks use explicitly labeled test doubles.

Expected findings: allowed-empty optimum mask 0, cost 0; nonempty optimum mask
4096 (contact 12, zero based), cost about 0.1736142930; threshold decoder maps
zeros to mask 1; the historical CMA batch probe reads 18 unique masks while
reporting 10. Eight audit tests pass in the recorded review environment.

The stimulation domain must be chosen from the scientific question before a
comparison. `Domain(n_bits=16, allow_empty=...)` has no implicit choice.
`BudgetedOracle` records scalar objective access, duplicate cache hits and denied
post-budget reads. Historical optimizer steps, surrogate calculations and shots
that have not been instrumented are reported as `null`, not zero. Revised
end-to-end optimizer integration and performance runs still require review.

Contribution descriptions and any external release need Esther's confirmation.
