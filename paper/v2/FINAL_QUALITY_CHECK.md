> These checks describe manuscript preparation at the frozen commit. The later GitHub publication changes only the root README and adds publication documents; it does not alter scientific code or results.

# Final Quality Check — October 4, 2026

The checks below concern manuscript preparation and saved evidence. No experimental validation was rerun for this revision.

| Requirement | Outcome |
|---|---|
| Version 1 preserved unchanged | PASS. Original and preserved copy have SHA-256 `98092c4f55849357942911bca47b4005f7f22fd5eaadf144bfdd6a3a2739c328`. |
| Research code/results unchanged | PASS. All 86 tracked files unchanged; research Git status clean at the exact requested commit. |
| Version 2 clearly versioned | PASS. Separate new manuscript, October 4, 2026; October 2026 Validated Revision. |
| Stage 1/2 numbers source-faithful | QUALIFIED PASS. Stage 1 sweep matches V1 Table 1; its sweep-specific n/raw records are unavailable. Stage 2 uses frozen notebook output, agreeing with V1 prose and replacing its conflicting table image. No claim of a new Stage 1/2 methodological validation. |
| Stage 3 values match report/data | PASS. Complete 28-row summary and all eight paired-comparison rows checked against saved data; model/domain/resources reconciled with report. |
| No positive 75–80% advantage survives | PASS. Percentages appear only in explicit withdrawal/history context. |
| No clinical necessity of six contacts | PASS. Fixed-cardinality benchmark choice; direct-model cardinality results in main text. |
| QUBO-to-Ising validation accurate | PASS. Three exhaustive 65,536-state checks; numerical error correctly aggregated; hard constraints are not falsely claimed to be in the phase Hamiltonian. |
| QAOA fallback reported as 0% | PASS. 1,830/1,830 adaptive proposals from samples. |
| Full-domain surrogate explained | PASS. Cheap predictions over unseen admissible masks followed by one true-objective query. |
| Paired statistical language correct | PASS. Non-separation, no equivalence/noninferiority assertion; separate principal/secondary Holm families. |
| Beta-model failure visible | PASS. Dedicated main-text subsection, Figure 4 and Table 5. |
| Practical impact without clinical overclaim | PASS. Research-method decision framework; no treatment recommendation. |
| Multi-instance future work | PASS. Pre-specified 10–30+ independent synthetic instances; no favorable-instance tuning. |
| Computational cost separate from query efficiency | PASS. Circuits/shots, classical support, offline oracle and excluded costs disclosed. |
| Clinical fidelity separate from optimization performance | PASS. Fitted model, direct simulator, and patient outcome distinguished. |
| Abstract and conclusion agree | PASS. Competitive corrected Stage 3; no supported superiority; strong classical methods remain practical current-scale choices. |
| Figures/tables trace to saved artifacts | PASS. Seven figures, fourteen tables; historical Stage 1/2 provenance distinguished from validated Stage 3. |
| Manuscript stands alone | PASS. Model equations, definitions, methods, complete results, synthetic metadata, references, limits and interpretation supplied. |
| Evolution note explains revision | PASS. Original result, audit issues, corrections, changed conclusion and research principle stated. |
| Citations and cross-references | PASS. Eight bibliography keys used and resolved; no “??” in final PDF; bibliographic corrections documented. |
| PDF compilation/layout | PASS. Final Tectonic compilation succeeded. Rendered-page inspection and text-boundary check completed; no overfull boxes or missing references in final pass. |

Remaining scientific limitations are deliberately retained in the manuscript and claim audit. In particular, preserving historical Stage 1/2 results does not establish that their legacy quantum code has been corrected or that their internal objective-access accounting has been retrospectively validated. This qualification is necessary for a defensible paper under the no-code-change/no-rerun constraint.
