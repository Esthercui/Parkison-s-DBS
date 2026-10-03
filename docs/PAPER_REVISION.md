# Historical manuscript requires substantive revision

Source: `paper/HISTORICAL_2026-03_DBS_Manuscript.pdf`, 22 pages, March 2026.
Retrieved from the Sources tab of ChatGPT project “Esther’s Project v2.0” on
October 3, 2026. SHA-256:
`98092c4f55849357942911bca47b4005f7f22fd5eaadf144bfdd6a3a2739c328`.
The original PDF is preserved unchanged; no corrected manuscript is claimed.

| Location | Required revision |
|---|---|
| Abstract, p.2 | Remove the progression to QAOA superiority and unverified “first rigorous” novelty claim; replace with the corrected bounded result |
| Introduction/research motivation, pp.3–7 | Separate motivation from evidence; do not assert a proven structure-dependent quantum advantage |
| Benchmark/methods, pp.7–12 | Declare common domains, initial design, seeds and actual algorithm variants; distinguish finite-grid optima from continuous or clinical optima |
| Stage 3 definition, p.10 | Explicitly state zero admissibility and fitted-objective degeneracy; record fit residuals, intercept and inactive charge-density penalties |
| Methods, p.11 | Correct the binary-to-Ising mapping and “exact” baseline; Stage 2 and Stage 3 historical comparators were candidate-pool searches |
| Budget description, pp.11–12 | Replace implied patient/simulator-trial equivalence with charged objective queries; report oracle/Pareto setup and QAOA internal resources separately |
| Results, pp.13–17 | Replace all affected tables/figures with fresh corrected data; do not mix old 30-seed summaries with current 10-seed comparisons |
| Stage 3 claims, pp.16–17 | Withdraw superiority and 75–80% improvements over the incorrectly labeled baseline |
| Discussion/impact/conclusion, pp.17–20 | Rewrite the central conclusion; the corrected comparison does not establish the proposed quantum turning point |
| Limitations, p.19 | Add one-instance scope, statevector-versus-hardware distinction, trivial optimum, grid/time-step effects, fit error, shared control and setup/resource caveats |
| p.18 arithmetic | Correct the printed 2^16 = 65,526 typo to 65,536 |
| Contributions | Add a verified collaborative contribution statement; present later Codex-assisted validation separately |

Use `results/summary.csv` and `results/paired_comparisons.csv` as the numeric
sources. The corrected run is a declared new comparison of the same model and
objective, not a claim to recover the original notebook execution environment.
Ten optimizer seeds cannot support patient or model-population generalization.
The historical PDF may be linked only with its revision warning and the corrected
results beside it. A scientific rewrite and collaborator/advisor review remain open.
