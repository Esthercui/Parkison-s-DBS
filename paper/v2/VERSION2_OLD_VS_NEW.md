# Version 1 vs Version 2: Scientific Comparison

| Topic | Old central statement or implication | Version 2 conclusion | Why it changed / responsible evidence |
|---|---|---|---|
| Central story | Classical dominance → competitiveness → QAOA best-performing | Classical dominance in reported smooth results → narrowing historical gap → competitive corrected Stage 3 performance | Corrected-domain Stage 3 comparison with seven methods; `optimizer_summary.csv`, `paired_statistics.csv` |
| Effect size | Approximately 75% at B=20 and 80% at B=30 less regret than surrogate comparator | Those positive advantage claims do not survive; QAOA−Full-Domain means are −0.002339, +0.011083, +0.004004, −0.001316 | Changed admissibility, corrected mapping, stronger comparator, paired uncertainty; no factorial attribution of individual corrections |
| Rank | QAOA lowest mean at every budget | Random lowest at B=10; Full-Domain at B=20; Pool at B=30/40; QAOA ranks 3/2/3/2 | Complete seven-method validated summary |
| Statistical conclusion | Descriptive differences framed as strong evidence | No statistical separation from Full-Domain at any budget; all Holm p=1.000; not equivalence | Matched initialization; paired bootstrap and sign randomization |
| Comparator | “Surrogate (Exact)” treated as an exact solver | Stage 3 historical comparator is Pool; new Full-Domain scans cheap predictions and queries one selected mask | `stage3.ipynb` cell 7; shared surrogate and full-domain proposal code |
| Domain | Full binary contact search presented as clinically meaningful | Exactly-six, fitted-efficacy-screened domain: 8,008 cardinality masks, 6,881 admissible | `ground_truth.json`; domain removes pathological zero-contact behavior |
| Six contacts | Subsequent fitted-threshold interpretation could suggest necessity | Fixed benchmark choice only | `cardinality_sensitivity.csv`: direct passes 1,817 four-contact and all 4,368 five-contact masks |
| Efficacy | Quadratic curve treated as adequate biological grounding | Imperfect benchmark approximation with severe local mismatch | `beta_fit_metrics.json`, `threshold_validation.json`; local R² −986.838188, crossing shift 0.559478 |
| Implementation | Binary coefficients used directly for Ising rotations | Correct full binary-surrogate transformation, precision-validated; constraints filtered separately | `mapping_validation_summary.json`; 65,536 states per test, maximum discrepancy 2.84217e−14 |
| Attribution | QAOA label without measured fallback contribution | 1,830/1,830 adaptive proposals sampled by QAOA; fallback 0%; no quantum-only causal ablation | `qaoa_trace.csv`, `qaoa_fallback_summary.csv` |
| Efficiency | Limited trials could imply practical clinical gain | Query efficiency, computation, and clinical fidelity assessed separately | 54,829 sampling circuits, 15,441,664 shots; fitted-cost oracle; no patient trial or runtime comparison |
| Cross-stage trend | A structural turning point where quantum becomes better | Descriptive progression with historical implementation differences; no controlled causal transition | Stage 1/2 preserved source; corrected Stage 3 only |
| Novelty | First rigorous ground-truth quantum-assisted DBS benchmark | Reproducible benchmark and validation framework; no priority claim | Bounded reference verification does not establish exhaustive novelty |
| Future impact | Similar gains might reduce clinical programming burden | Multi-instance generalization and richer validated models are prerequisites; scaling remains a hypothesis | Single synthetic instance; biological mismatch; present domain cheaply enumerable |

The March PDF is preserved exactly. “Removed” means not retained as a positive scientific claim in Version 2; historical percentages remain only where their invalidation is explicitly explained.
