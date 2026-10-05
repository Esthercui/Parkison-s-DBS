# Research Evolution and Validation Note

**Version 2 | October 2026 Validated Revision | October 4, 2026**

The March 2026 study, *Quantum-assisted Optimization of Parkinson’s Deep Brain Stimulation (DBS) Parameters*, established a three-stage simulation benchmark: smooth stimulation tuning, a constrained extension, and discrete contact selection. Its original Stage 3 results appeared to show a strong QAOA advantage, including approximately 75–80% lower regret than the reported classical surrogate comparator. That manuscript remains preserved, byte-for-byte, as Version 1.

The subsequent audit deliberately stress-tested the result. It identified pathological zero-contact/domain behavior, incorrect use of binary-QUBO coefficients as Ising rotation coefficients, an inadequately strong classical surrogate pool comparator, missing proposal-attribution instrumentation, and an unsupported physiological interpretation of fitted-efficacy screening. These issues affected what the comparison measured and what could be concluded from it.

The final validated benchmark fixes the primary domain at exactly six of 16 synthetic contacts, screened by the inherited fitted BetaRatio threshold of 0.8228585. Six is a controlled cardinality choice, not a clinical requirement. The binary-to-Ising mapping is corrected and checked over all 65,536 states, with maximum energy discrepancy 2.84217 × 10⁻¹⁴. All terms in the learned quadratic surrogate are transformed; hard cardinality/efficacy constraints remain classical filtering rules, not phase-Hamiltonian penalties.

A full-domain classical surrogate comparator now scores every unseen admissible mask using cheap predictions before spending one objective query. The surrogate methods share initial observations, and comparisons use paired statistics with four-budget Holm correction. QAOA instrumentation attributes all 1,830 adaptive proposals to QAOA samples, with zero fallback. Direct STN–GPe validation and cardinality sensitivity expose substantial mismatch between the fixed quadratic efficacy approximation and the underlying simulator: the fit rejects all four- and five-contact masks, while direct simulation accepts 1,817 of 1,820 and all 4,368, respectively.

The original 75–80% advantage disappears under these controls. Corrected simulated p=1 QAOA is competitive in objective-query efficiency, but is not statistically separated from full-domain classical surrogate search at any tested budget; all principal Holm-adjusted p values are 1.000. Nonsignificance does not establish equivalence. The experiment also does not establish a runtime or hardware speedup, clinical efficacy, or an isolated causal contribution of quantum evolution.

Version 2 is a substantial revision of the same research program. Its contribution is the ground-truth benchmark, corrected pipeline, strong comparator, and a validation framework that distinguishes query efficiency, computation, and biological fidelity. Historical Stage 1/2 results remain, with explicit source and legacy-implementation qualifications; the corrected Stage 3 validation is not retroactively assigned to them. No experimental code was changed or optimizer run performed for this manuscript revision.

**Authoritative evidence:** commit `a94acf521bc596583b873283a509b43418b0fb76`, `STAGE3_VALIDATION_REPORT.md`, and `results/stage3_validated/`. The separate claim audit maps final statements to those artifacts.

Validation became the guardrail: the goal was not to preserve the exciting result, but to determine what survived attempts to disprove it.
