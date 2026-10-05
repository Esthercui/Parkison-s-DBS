# Benchmarking Quantum-Assisted Optimization for Parkinson’s Deep Brain Stimulation

## Version 2 — October 2026 Validated Revision

**A Ground-Truth Validation Study** · Revision completed October 4, 2026

[**Read Version 2 (PDF)**](paper/v2/CURRENT_v2_DBS_Manuscript.pdf) · [Manuscript source and review package](paper/v2/) · [Validation report](STAGE3_VALIDATION_REPORT.md) · [Research evolution note](paper/v2/RESEARCH_EVOLUTION_AND_VALIDATION_NOTE.md)

Version 2 is a substantial revision of the March 2026 study. It supersedes the original Stage 3 conclusions following methodological re-audit. The [March 2026 Version 1 PDF](paper/v2/version1-preserved/PRESERVED_v1_DBS_March2026.pdf) is preserved unchanged as a historical record.

## Scientific conclusion

Classical optimization, especially CMA-ES, performed strongest in the historical smooth DBS-tuning benchmark. The constrained extension narrowed the performance gap. In the corrected combinatorial Stage 3 benchmark, a simulated p=1 QAOA-assisted surrogate proposal method was competitive in objective-query efficiency, but was **not statistically separated from strong full-domain classical surrogate search** at any tested budget. Nonsignificance does not establish statistical equivalence.

The original apparent 75–80% Stage 3 advantage did not survive validation. This study establishes neither quantum advantage nor computational speedup, clinical validation, or treatment recommendations. At this scale, strong classical methods remain the practical choice.

## Three-stage benchmark

| Stage | Problem | Interpretation |
| --- | --- | --- |
| 1 | Smooth frequency × amplitude × pulse-width tuning, with a full ground-truth grid | Historical results favor CMA-ES. |
| 2 | Clinically motivated constrained extension | Historical results show a narrower QAOA/classical gap. |
| 3 | Fixed-cardinality, fitted-efficacy-screened selection among 16 binary contact variables | Corrected QAOA-assisted proposals are competitive with classical surrogate proposals, without supported superiority. |

Stages 1 and 2 are retained historical evidence, with provenance and implementation limitations disclosed in the manuscript. The Stage 3 re-audit does not retroactively validate their legacy QAOA implementation or budget accounting. Cross-stage rankings do not establish a controlled causal transition to quantum benefit.

## Authoritative Stage 3 evidence

Scientific code and results are frozen at [`a94acf521bc596583b873283a509b43418b0fb76`](https://github.com/Esthercui/Parkison-s-DBS/commit/a94acf521bc596583b873283a509b43418b0fb76). Use [STAGE3_VALIDATION_REPORT.md](STAGE3_VALIDATION_REPORT.md) and [results/stage3_validated/](results/stage3_validated/) for current Stage 3 conclusions.

- **Domain:** 65,536 binary masks; 8,008 with exactly six active contacts; 6,881 admissible under fitted BetaRatio ≤ 0.8228585. Six contacts is a benchmark design choice, not a clinical requirement. Contact indices are synthetic metadata indices, not anatomical electrode locations.
- **Ground truth:** mask 38180, active zero-based indices `[2, 5, 8, 10, 12, 15]`, fitted objective minimum 1.5690394714699.
- **Comparison:** Random, Genetic Algorithm, Bayesian Optimization, CMA-ES, Surrogate (Pool), Surrogate (Full-Domain), and simulated p=1 QAOA-assisted surrogate proposals; budgets 10, 20, 30, 40 and 30 seeds per method/budget on one synthetic instance.
- **Paired inference:** QAOA minus Full-Domain mean regret differences are −0.002339, +0.011083, +0.004004, and −0.001316 in budget order. All paired 95% intervals include zero; all Holm-adjusted p-values are 1.000. Descriptive ranks vary across budgets.
- **Implementation verification:** exhaustive QUBO/Ising energy checks cover all 65,536 states; maximum discrepancy 2.84217e−14 and mean discrepancy 1.58893e−15. This validates the mapping, not quantum performance.
- **Attribution:** all 1,830 adaptive QAOA proposals came from QAOA samples; fallback rate 0%. Internal resources were 54,829 sampling circuits and 15,441,664 shots, alongside 3,000 budgeted QAOA objective queries including initialization.

### What the methods actually evaluate

The STN–GPe neurodynamic model is classical. QAOA acts only on a learned quadratic surrogate through classical fitting, QUBO construction, corrected Ising mapping, classical angle optimization, simulated p=1 sampling, admissibility filtering, and evaluation of the selected proposal. Hard admissibility rules are enforced by classical filtering; the sampled expectation barrier is not a hard-constraint phase Hamiltonian.

Surrogate (Full-Domain), labeled “Surrogate (Exhaustive)” in saved artifacts, scores cheap learned predictions over all currently admissible, unevaluated masks and spends one budgeted objective query on its selected candidate. It does **not** test every DBS setting against an expensive simulator or patient. Stage 3 budgeted “true-objective” queries access the fitted benchmark oracle; they are not fresh direct STN–GPe simulations or clinical trials.

### Biological-model fidelity

The quadratic efficacy approximation enables the QUBO-compatible benchmark but is imperfect. Against the direct simulator, global R² is 0.761188; within the reachable six-contact amplitude interval, R² is −986.838188 because direct response is nearly flat and the fit fails to track its small variation. Cardinality sensitivity shows that the direct model passes the inherited threshold for nearly all four-contact masks and all five-contact masks, despite the fit rejecting all of them. These findings do not support interpreting six contacts as physiologically necessary.

Objective-query efficiency, computational cost, and biological fidelity are separate dimensions. An optimizer cannot compensate for a poorly validated objective.

## Repository guide and reproducibility

| Location | Role |
| --- | --- |
| [paper/v2/](paper/v2/) | Current manuscript, PDF-ready source, preserved V1, audits, manifests, and selected evidence |
| [STAGE3_VALIDATION_REPORT.md](STAGE3_VALIDATION_REPORT.md) | Validated Stage 3 methods, results, limitations, and reproduction instructions |
| [results/stage3_validated/](results/stage3_validated/) | Authoritative saved Stage 3 data, statistics, instrumentation, and figures |
| [validate_stage3.py](validate_stage3.py) | Frozen validated Stage 3 runner; see the report before reproducing |
| [requirements-stage3.txt](requirements-stage3.txt) | Frozen Stage 3 environment requirements |
| [STAGE3_RESULTS.md](STAGE3_RESULTS.md), [results/stage3_controlled/](results/stage3_controlled/), [run_stage3.py](run_stage3.py) | Retained earlier controlled baseline; historical, superseded for current Stage 3 conclusions |
| [docs/REPOSITORY_PROVENANCE.md](docs/REPOSITORY_PROVENANCE.md) | Branch snapshot preservation and integration provenance |

The publication update changes documentation and adds manuscript files only. It does not alter the frozen scientific code/results or run new experiments. Consult the validation report for reproduction into a new output directory; preserve delivered evidence.

## Limitations and next questions

This is a simulation-based, preclinical benchmark with a simplified STN–GPe model, beta power as a proxy, an imperfect efficacy fit, one synthetic contact instance, 30 Stage 3 seeds, and a narrow simulated p=1 QAOA configuration. Equal objective-query budgets do not imply equal computational cost.

A priority for future work is **multi-instance robustness and generalization**: freeze the validated algorithms and compare them on 10–30+ independently generated contact landscapes with distributions specified before optimizer comparison. Richer current steering, patient variability, side-effect constraints, real DBS/LFP data, closed-loop policies, larger spaces, deeper circuits, and quantum hardware are future research directions. Potential usefulness in larger domains remains a hypothesis.
