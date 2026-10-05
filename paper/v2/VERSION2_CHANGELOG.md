# Version 2 Changelog

**Completed October 4, 2026. Status: October 2026 Validated Revision.**

New title: **Benchmarking Quantum-Assisted Optimization for Parkinson’s Deep Brain Stimulation: A Ground-Truth Validation Study**.

## Preservation and scope

- The supplied March 2026 PDF is untouched. A byte-identical copy is `version1-preserved/PRESERVED_v1_DBS_March2026.pdf`.
- SHA-256: `98092c4f55849357942911bca47b4005f7f22fd5eaadf144bfdd6a3a2739c328`.
- Research source remains at `a94acf521bc596583b873283a509b43418b0fb76`. All 86 tracked research files are hash-checked before and after preparation. Nothing in the research repository is edited.
- No algorithms, model simulations, statistical resampling, or exploratory experiments are run. Tables are formatted from saved results; images are copied/extracted from saved figures. No new scientific data are generated.
- Manuscript sources, figures, and audits are in a new sibling delivery folder, not the experimental repository. The original title page had no author byline; no author or affiliation is invented in Version 2.

## Material revision

- Abstract rewritten to report the validated benchmark, non-separation, attribution, model failure, and practical guardrails.
- Introduction and research questions center on limited-query comparison against strong classical methods; unsupported priority claims removed.
- STN–GPe background and original architecture retained; equations, fixed parameters, and synthetic metadata make the manuscript self-contained.
- Stage 1 numerical table retained from V1. Stage 2 numbers resolved using frozen notebook cell 16, consistent with V1 prose; inconsistent table-image entries are not propagated.
- All Stage 3 methods/results replaced. Added fixed-cardinality domain, exact optimum, complete seven-method results, paired CIs/tests, correct mapping, constraint-handling distinction, resource accounting, and attribution.
- Dedicated main-text efficacy validation and cardinality sensitivity added.
- Discussion rewritten around objective-query efficiency, computational cost, and biological/clinical fidelity.
- Limitations distinguish corrected Stage 3 methodology from legacy Stage 1/2 provenance and implementation limits.
- Future work prioritizes pre-specified multi-instance generalization and labels scaling/deeper-circuit/hardware ideas as untested hypotheses.
- Contributions and conclusion rewritten around the reproducible benchmark and validation framework.
- Literature repaired: Picillo et al. (2016) replaces the misattributed Chatha entry; the underlying Fleming et al. (2023) study replaces the inaccurate Foutz bibliography entry; QOMIC receives its missing full reference. Eight citations audited.
- Four main figures and three appendix figures; six main tables plus eight supplementary tables. All Stage 3 artwork is copied byte-for-byte; its legacy “Exhaustive” label is translated explicitly in captions.

## Source conflicts and bounded decisions

1. **Stage 2 table image vs source:** V1 p.15 prints CMA-ES means 0.0852/0.0762/0.0659/0.0601 and QAOA means 0.0974/0.0836/0.0723/0.0655. Frozen cell 16 and V1 prose instead agree on CMA-ES 0.0839/0.0749/0.0658/0.0602 and QAOA 0.0974/0.0860/0.0751/0.0659. V1 table also prints Pool B=10 0.0979 (source 0.0979), Random B=10 SD 0.0242, and an apparent Pool B=40 SD typo 0.2223 (source 0.0223). Source-consistent SDs are used throughout. No values are averaged across conflicts.
2. **Stage 1 sweep traceability:** V1 Table 1 is the source of the four-budget table. The notebook’s separate 10-seed B=40 summaries are different records and do not replace it. The sweep-specific n and raw rows remain unverified.
3. **Mapping “including constraints”:** the authoritative report explicitly states no quadratic cardinality penalty is present in the phase QUBO. Version 2 transforms every present surrogate term and accurately describes hard filtering and the classical 1,000 rejection barrier. It does not invent a constrained Hamiltonian.
4. **Historical implementation scope:** source inspection shows Stage 1/2 legacy direct phase coefficients, pair sparsification, and potential final-population cost reads beyond logged unique queries in CMA-ES. These are disclosed; they were not repaired or rerun. Stage 3’s corrected mapping and audited budgets are not generalized retrospectively.
5. **Novelty:** no “first” or priority assertion is retained because the bounded references audit is not an exhaustive novelty search.

## Claims withdrawn or qualified

The full claim-by-claim disposition is in `VERSION2_CLAIM_AUDIT.md` and `VERSION2_OLD_VS_NEW.md`. Withdrawn: the positive 75–80% advantage; QAOA best at every Stage 3 budget; an identified transition to quantum superiority; universal superiority; clinical necessity of six contacts; “exact” description of a candidate pool; clinical treatment/programming benefit inferred from synthetic regret; and an unsupported first-of-kind claim. Qualified: realistic budgets, anatomical/geometry language, clinical threshold language, beta as a clinical outcome, full-domain enumeration, source validation scope, and cross-stage causal interpretation. No computational-speedup, patient-readiness, or equivalence claim is introduced.
