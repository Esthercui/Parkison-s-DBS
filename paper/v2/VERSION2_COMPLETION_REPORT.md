> Publication note: this report records the original manuscript delivery. GitHub integration subsequently updates the root README and adds `paper/v2/`; scientific code and results remain frozen. Local delivery paths have been omitted from this public copy.

# Version 2 Completion Report

Completed October 4, 2026. Status: **October 2026 Validated Revision**.

1. **Final title:** *Benchmarking Quantum-Assisted Optimization for Parkinson’s Deep Brain Stimulation: A Ground-Truth Validation Study*.
2. **Manuscript:** `CURRENT_v2_DBS_Manuscript.pdf`; canonical PDF-ready source `CURRENT_v2_DBS_Manuscript.tex` with `tables/` and `figures/`.
3. **Length:** 22 PDF pages, including title, references and appendices. Main prose: 4,859 words including the 226-word abstract; excludes equations, tables, captions, headings, references and appendices. Word count uses Pandoc’s LaTeX-to-plain parsing and whitespace-delimited words; counts from other tools may differ.
4. **Materially rewritten:** title/version note, Abstract, Introduction/related work, Research Questions, all Stage 3 methods/results, Discussion, Limitations, Future Work, Contributions/Conclusion, and references. STN–GPe architecture and Stage 1/2 historical methods/results are retained with source clarifications. Stage 2 values follow frozen notebook output agreeing with V1 prose, rather than its conflicting table image.
5. **Figures:** main Figure 1 Stage 1 Pareto; Figure 2 saved Stage 2 optimizer performance; Figure 3 validated Stage 3 regret versus budget; Figure 4 beta-fit validation. Appendix S1 cardinality sensitivity, S2 paired QAOA/Full-Domain differences, S3 QAOA feasibility/fallback. Seven figures total; no new experiments or research plots generated. Exact sources/captions in `FIGURE_MANIFEST.md`.
6. **Tables:** main Tables 1–2 historical Stage 1/2 performance, Table 3 complete Stage 3 mean±SD matrix, Table 4 principal paired statistics, Table 5 beta-model validation, Table 6 cardinality sensitivity. Supplementary S1–S4 full Stage 3 descriptive statistics by budget, S5 secondary Pool paired comparison, S6 simulator parameters, S7 synthetic metadata, S8 optimum components. Fourteen tables total; full source/caption mapping in `TABLE_MANIFEST.md`.

## Final scientific conclusion

The reported historical results favor classical CMA-ES for smooth DBS tuning and show a narrowing QAOA gap with added constraints. In the corrected fixed-cardinality Stage 3 benchmark, simulated p=1 QAOA-assisted proposals remain competitive in objective-query efficiency but are not statistically separated from full-domain classical surrogate search at any tested budget; all principal Holm-adjusted p values are 1.000. All 1,830 adaptive proposals come from QAOA samples, yet neither this attribution nor numerically correct QUBO-to-Ising mapping establishes quantum superiority or speedup. Direct STN–GPe validation exposes substantial local efficacy-model distortion and rejects a physiological necessity interpretation of six contacts. The contribution is the ground-truth benchmark and validation framework, with cross-stage conclusions qualified by the preserved historical implementations.

## Final real-world impact statement

At this benchmark’s scale, a QUBO encoding alone does not justify adopting a quantum optimizer: strong classical optimization and full-domain surrogate prediction remain practical choices. The useful output is a decision framework for evaluating candidate optimization systems before clinical translation—validate the feasible domain, response objective, circuit mapping, classical comparators, query accounting, and proposal attribution. Scarce patient/programming evaluations make sample efficiency important, but low regret on a distorted response model does not establish therapeutic benefit. An optimizer cannot compensate for a poorly validated objective; future medical optimization work needs objective fidelity alongside efficient search.

## Claims removed or corrected from Version 1

- Positive 75–80% Stage 3 regret-advantage claim; those percentages survive only as an explicitly withdrawn historical result.
- QAOA strongest/best-performing or lowest regret at every Stage 3 budget.
- Identification of a turning point where quantum optimization becomes better.
- Unsupported first-of-kind/first rigorous benchmark priority claim.
- “Surrogate (Exact)” applied to candidate-pool search; names now match each stage’s implementation.
- Clinical realism or clinical programming savings inferred directly from synthetic regret and chosen query budgets.
- Anatomical geometry/contact-position implications unsupported by synthetic metadata.
- Any implication that the fitted efficacy threshold or six-contact choice is clinically validated/necessary.
- Any implication that QAOA performs neural simulation, that full-domain surrogate search spends all-domain true queries, or that equal B means equal computation.
- Inaccurate or incomplete bibliographic identities, including Chatha and Foutz entries; QOMIC’s missing reference supplied.
- Unqualified progression from Stage 1 to Stage 3 as evidence of a causal quantum structural advantage.

No new equivalence, treatment recommendation, hardware speedup, or patient-readiness claim is introduced. `VERSION2_OLD_VS_NEW.md` provides the full evidence-linked comparison.

## Remaining reviewer vulnerabilities

The largest vulnerability is the historical Stage 1/2 evidence boundary: Stage 1’s sweep-specific seed count/raw records are unavailable, Stage 2’s original table conflicts with its prose, and their preserved quantum/budget-accounting routines are not retroactively covered by the corrected Stage 3 audit. Stage 3 itself is one synthetic instance with an imperfect efficacy approximation, an underdetermined surrogate, query-free screening and prediction, correlated sampler randomness, a shallow simulated ansatz, and no causal ablation isolating quantum evolution. “Competitive” is descriptive; no equivalence margin or measured runtime advantage is established. All these qualifications appear in the manuscript or claim audit. Author/affiliation/funding/conflict facts were not invented.

## Package and preservation

Local folder: `paper/v2/`.

The folder contains the manuscript PDF/TeX, figure/table assets, one-page validation-note PDF and Markdown, `VERSION2_CLAIM_AUDIT.md`, `VERSION2_CHANGELOG.md`, `VERSION2_OLD_VS_NEW.md`, `REFERENCES_AUDIT.md`, both manifests, `FINAL_QUALITY_CHECK.md`, this completion report, selected evidence, and the preserved V1 PDF. The complete package archive is `the separately delivered manuscript package ZIP`.

The original V1 SHA-256 is unchanged: `98092c4f55849357942911bca47b4005f7f22fd5eaadf144bfdd6a3a2739c328`. All 86 tracked research files remain unchanged at `a94acf521bc596583b873283a509b43418b0fb76`; the experimental repository is clean. No algorithm, simulation, exploratory experiment, or statistical resampling was run.

