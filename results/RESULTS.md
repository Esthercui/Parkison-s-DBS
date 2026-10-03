# Corrected results

10 paired optimizer seeds, one fixed simulator instance. Mean +/- sample SD. Lower regret is better.

Full original grids; budgets are prefixes of each 40-query run.
95% percentile bootstrap intervals (10,000 resamples, seed 20261003) are descriptive; no multiplicity-adjusted significance claims.
See `summary.csv` for all budgets and confidence intervals; `paired_comparisons.csv` preserves pairing.

| Experiment | Stage | Method | B=10 mean +/- SD | B=40 mean +/- SD | B=40 optimum hits |
|---|---|---|---:|---:|---:|
| current | 1 | Random | 0.112988 +/- 0.031021 | 0.081931 +/- 0.025513 | 0/10 |
| current | 1 | GA | 0.112835 +/- 0.040311 | 0.062446 +/- 0.034186 | 0/10 |
| current | 1 | BO | 0.123887 +/- 0.050012 | 0.060335 +/- 0.045391 | 0/10 |
| current | 1 | CMA-ES | 0.115262 +/- 0.039093 | 0.058542 +/- 0.033961 | 0/10 |
| current | 1 | Surrogate (exhaustive) | 0.140364 +/- 0.040237 | 0.102693 +/- 0.043016 | 0/10 |
| current | 1 | QAOA (p=1) | 0.132871 +/- 0.039176 | 0.100912 +/- 0.028124 | 0/10 |
| current | 2 | Random | 0.092997 +/- 0.025840 | 0.062562 +/- 0.017241 | 0/10 |
| current | 2 | GA | 0.102355 +/- 0.037208 | 0.068962 +/- 0.028586 | 0/10 |
| current | 2 | BO | 0.097833 +/- 0.034696 | 0.062060 +/- 0.028438 | 0/10 |
| current | 2 | CMA-ES | 0.107054 +/- 0.027420 | 0.076401 +/- 0.026903 | 0/10 |
| current | 2 | Surrogate (exhaustive) | 0.088851 +/- 0.023405 | 0.060433 +/- 0.029445 | 0/10 |
| current | 2 | QAOA (p=1) | 0.091680 +/- 0.023518 | 0.073358 +/- 0.020653 | 0/10 |
| current | 3 | Random | 0.000000 +/- 0.000000 | 0.000000 +/- 0.000000 | 10/10 |
| current | 3 | GA | 0.000000 +/- 0.000000 | 0.000000 +/- 0.000000 | 10/10 |
| current | 3 | BO | 0.000000 +/- 0.000000 | 0.000000 +/- 0.000000 | 10/10 |
| current | 3 | CMA-ES | 0.000000 +/- 0.000000 | 0.000000 +/- 0.000000 | 10/10 |
| current | 3 | Surrogate (exhaustive) | 0.000000 +/- 0.000000 | 0.000000 +/- 0.000000 | 10/10 |
| current | 3 | QAOA (p=1) | 0.000000 +/- 0.000000 | 0.000000 +/- 0.000000 | 10/10 |
| current | 3 | Sparse-first | 0.000000 +/- 0.000000 | 0.000000 +/- 0.000000 | 10/10 |
| nonempty | 3 | Random | 1.341591 +/- 0.395818 | 1.031242 +/- 0.200079 | 0/10 |
| nonempty | 3 | GA | 1.140385 +/- 0.450199 | 0.444653 +/- 0.171671 | 0/10 |
| nonempty | 3 | BO | 0.202837 +/- 0.270458 | 0.000000 +/- 0.000000 | 10/10 |
| nonempty | 3 | CMA-ES | 1.053735 +/- 0.401642 | 0.274100 +/- 0.237960 | 0/10 |
| nonempty | 3 | Surrogate (exhaustive) | 0.010512 +/- 0.013644 | 0.000000 +/- 0.000000 | 10/10 |
| nonempty | 3 | QAOA (p=1) | 0.014153 +/- 0.014023 | 0.000000 +/- 0.000000 | 10/10 |
| nonempty | 3 | Sparse-first | 0.006503 +/- 0.007039 | 0.000000 +/- 0.000000 | 10/10 |
